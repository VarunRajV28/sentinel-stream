import asyncio
import logging
from sentinel_postgres_engine.db import init_db
from sentinel_postgres_engine.detectors.velocity_sql import velocity_loop
from sentinel_postgres_engine.detectors.toxic_node_sql import toxic_node_loop
from sentinel_postgres_engine.detectors.ato_sql import ato_loop
from sentinel_postgres_engine.ledger_processor import ledger_processor_loop

log = logging.getLogger("sentinel.postgres.pool")

async def start_engine():
    """Start all background tasks for the Postgres engine."""
    log.info("Initializing Postgres Database...")
    await init_db()
    
    log.info("Starting background tasks...")
    tasks = [
        asyncio.create_task(velocity_loop(), name="pg_velocity"),
        asyncio.create_task(toxic_node_loop(), name="pg_toxic"),
        asyncio.create_task(ato_loop(), name="pg_ato"),
        asyncio.create_task(ledger_processor_loop(), name="pg_ledger"),
    ]
    
    log.info("Postgres engine workers launched.")
    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        log.info("Postgres engine shutting down...")
        for t in tasks:
            t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start_engine())
