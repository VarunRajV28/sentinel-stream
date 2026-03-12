import logging
import asyncio
from datetime import datetime
from sqlalchemy import select, func
from sentinel_postgres_engine.db import AsyncSessionLocal
from sentinel_postgres_engine.models import VelocityMetric
from sentinel_postgres_engine.db_config import VELOCITY_SUM_ALERT
from sentinel_postgres_engine.alert_store import alert_store

log = logging.getLogger("sentinel.postgres.velocity")

async def scan_velocity(session):
    """
    Scan velocity_metrics for breaches.
    In Postgres, this is a simple filtered query.
    """
    # Current hour bucket
    hour_bucket = datetime.utcnow().strftime("%Y%m%d%H")
    
    stmt = select(VelocityMetric).where(
        (VelocityMetric.hour_bucket == hour_bucket) &
        (VelocityMetric.tx_sum_cents > VELOCITY_SUM_ALERT)
    )
    
    result = await session.execute(stmt)
    breaches = result.scalars().all()
    
    for b in breaches:
        added = alert_store.add_alert(
            pattern="Velocity Breach (Postgres)",
            entity_type="user",
            entity_id=b.user_id,
            detail=f"tx_sum=${b.tx_sum_cents / 100:.2f} in hour {hour_bucket}",
            time_bucket=hour_bucket
        )
        if added:
            log.warning("Velocity Breach [Postgres] ▸ user=%s", b.user_id)

async def velocity_loop():
    log.info("Postgres Velocity detector started.")
    while True:
        async with AsyncSessionLocal() as session:
            try:
                await scan_velocity(session)
            except Exception:
                log.exception("Velocity detector error")
        await asyncio.sleep(10)
