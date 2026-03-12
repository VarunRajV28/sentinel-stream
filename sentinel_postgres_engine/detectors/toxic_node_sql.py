import logging
import asyncio
from datetime import datetime
from sqlalchemy import select
from sentinel_postgres_engine.db import AsyncSessionLocal
from sentinel_postgres_engine.models import RiskMetric
from sentinel_postgres_engine.db_config import TOXIC_HITS_ALERT
from sentinel_postgres_engine.alert_store import alert_store

log = logging.getLogger("sentinel.postgres.toxic")

async def scan_toxic(session):
    """Scan risk_metrics for toxic nodes."""
    day_bucket = datetime.utcnow().strftime("%Y%m%d")
    
    stmt = select(RiskMetric).where(
        (RiskMetric.day_bucket == day_bucket) &
        (RiskMetric.interactions > TOXIC_HITS_ALERT)
    )
    
    result = await session.execute(stmt)
    toxic_nodes = result.scalars().all()
    
    for t in toxic_nodes:
        added = alert_store.add_alert(
            pattern="Toxic Node (Postgres)",
            entity_type="device",
            entity_id=t.device_id,
            detail=f"interactions={t.interactions} on {day_bucket}",
            time_bucket=day_bucket
        )
        if added:
            log.warning("Toxic Node [Postgres] ▸ dev=%s", t.device_id)

async def toxic_node_loop():
    log.info("Postgres Toxic-node detector started.")
    while True:
        async with AsyncSessionLocal() as session:
            try:
                await scan_toxic(session)
            except Exception:
                log.exception("Toxic-node detector error")
        await asyncio.sleep(10)
