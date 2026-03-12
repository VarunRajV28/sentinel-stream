import logging
import asyncio
from datetime import datetime
from sqlalchemy import select, update, insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sentinel_postgres_engine.db import AsyncSessionLocal
from sentinel_postgres_engine.models import RawEvent, VelocityMetric, RiskMetric

log = logging.getLogger("sentinel.postgres.ledger")

# This processor mimics the aggregate-updating behavior of scanners/ledger.py
# In a real app, this might be handled by triggers or during ingestion.
# For the comparative study, we scan raw_events for 'unprocessed' rows.

# Conceptually, we'd need a 'processed' flag or a watermark.
# I'll add a simple watermark-based approach or just process everything for now
# assuming it's a small-scale demo. For 1M rows, we need a watermark.

_watermark = 0

async def process_new_events(session):
    global _watermark
    
    # Fetch events newer than watermark
    stmt = select(RawEvent).where(RawEvent.id > _watermark).order_by(RawEvent.id).limit(1000)
    result = await session.execute(stmt)
    events = result.scalars().all()
    
    if not events:
        return
    
    for ev in events:
        # Update Velocity Metrics (Upsert)
        hour_bucket = ev.timestamp.strftime("%Y%m%d%H")
        amount_cents = int(ev.amount * 100) if ev.event_type == 'transfer_attempt' and ev.status == 'SUCCESS' else 0
        
        insert_stmt = pg_insert(VelocityMetric).values(
            user_id=ev.user_id,
            hour_bucket=hour_bucket,
            tx_count=1 if ev.event_type == 'transfer_attempt' else 0,
            tx_sum_cents=amount_cents
        ).on_conflict_do_update(
            index_elements=['user_id', 'hour_bucket'],
            set_={
                "tx_count": VelocityMetric.tx_count + (1 if ev.event_type == 'transfer_attempt' else 0),
                "tx_sum_cents": VelocityMetric.tx_sum_cents + amount_cents
            }
        )
        await session.execute(insert_stmt)
        
        # Update Risk Metrics (Upsert)
        if ev.device_id:
            day_bucket = ev.timestamp.strftime("%Y%m%d")
            risk_stmt = pg_insert(RiskMetric).values(
                device_id=ev.device_id,
                day_bucket=day_bucket,
                interactions=1
            ).on_conflict_do_update(
                index_elements=['device_id', 'day_bucket'],
                set_={"interactions": RiskMetric.interactions + 1}
            )
            await session.execute(risk_stmt)
        
        _watermark = max(_watermark, ev.id)
    
    await session.commit()
    # log.info("Processed events up to ID %d", _watermark)

async def ledger_processor_loop():
    log.info("Postgres Ledger processor started.")
    while True:
        async with AsyncSessionLocal() as session:
            try:
                await process_new_events(session)
            except Exception:
                log.exception("Ledger processor error")
        await asyncio.sleep(1)
