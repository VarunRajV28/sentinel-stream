import logging
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import text
from sentinel_postgres_engine.db import AsyncSessionLocal
from sentinel_postgres_engine.db_config import ATO_TIME_WINDOW_MS
from sentinel_postgres_engine.alert_store import alert_store

log = logging.getLogger("sentinel.postgres.ato")

# SQL to detect ATO sequence: 
# login_failed -> password_reset -> login_success (diff IP/device) -> transfer_attempt
# within ATO_TIME_WINDOW_MS
ATO_QUERY = """
WITH OrderedEvents AS (
    SELECT 
        user_id,
        event_type,
        timestamp,
        ip_address,
        device_id,
        LAG(event_type, 1) OVER (PARTITION BY user_id ORDER BY timestamp) as prev_1,
        LAG(event_type, 2) OVER (PARTITION BY user_id ORDER BY timestamp) as prev_2,
        LAG(event_type, 3) OVER (PARTITION BY user_id ORDER BY timestamp) as prev_3,
        LAG(timestamp, 3) OVER (PARTITION BY user_id ORDER BY timestamp) as start_ts,
        LAG(ip_address, 2) OVER (PARTITION BY user_id ORDER BY timestamp) as fail_ip,
        LAG(device_id, 2) OVER (PARTITION BY user_id ORDER BY timestamp) as fail_dev
    FROM raw_events
    WHERE timestamp > :cutoff
)
SELECT DISTINCT user_id
FROM OrderedEvents
WHERE 
    event_type = 'transfer_attempt' AND
    prev_1 = 'login_success' AND
    prev_2 = 'password_reset' AND
    prev_3 = 'login_failed' AND
    (timestamp - start_ts) <= :window_interval AND
    (ip_address != fail_ip OR device_id != fail_dev)
"""

async def scan_ato(session):
    """Detect ATO sequences using a single SQL query."""
    cutoff = datetime.utcnow() - timedelta(hours=1)
    window_interval = timedelta(milliseconds=ATO_TIME_WINDOW_MS)
    
    result = await session.execute(
        text(ATO_QUERY), 
        {"cutoff": cutoff, "window_interval": window_interval}
    )
    
    users = result.scalars().all()
    hour_bucket = datetime.utcnow().strftime("%Y%m%d%H")
    
    for user_id in users:
        added = alert_store.add_alert(
            pattern="Account Takeover (Postgres)",
            entity_type="user",
            entity_id=user_id,
            detail="ATO sequence detected via SQL Window Functions",
            time_bucket=hour_bucket
        )
        if added:
            log.warning("Account Takeover [Postgres] ▸ user=%s", user_id)

async def ato_loop():
    log.info("Postgres ATO detector started.")
    while True:
        async with AsyncSessionLocal() as session:
            try:
                await scan_ato(session)
            except Exception:
                log.exception("ATO detector error")
        await asyncio.sleep(15)
