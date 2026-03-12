import logging
import time
from fastapi import APIRouter, Depends
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sentinel_postgres_engine.db import get_db
from sentinel_postgres_engine.models import RawEvent

router = APIRouter(prefix="/api/analytics", tags=["stress_tests"])
log = logging.getLogger("sentinel.postgres.stress")

@router.get("/events/global/latest")
async def get_global_latest(db: AsyncSession = Depends(get_db)):
    """
    Stress Test: Fetch latest 1000 events.
    In Postgres, this requires a heavy B-Tree scan and MVCC overhead at scale.
    """
    start_time = time.perf_counter()
    stmt = select(RawEvent).order_by(desc(RawEvent.timestamp)).limit(1000)
    result = await db.execute(stmt)
    events = result.scalars().all()
    execution_time = time.perf_counter() - start_time
    
    return {
        "count": len(events),
        "execution_time_ms": round(execution_time * 1000, 2),
        "events": [
            {"id": e.id, "user_id": e.user_id, "ts": e.timestamp, "type": e.event_type}
            for e in events
        ]
    }

@router.get("/device/{device_id}/uniqueness")
async def get_device_uniqueness(device_id: str, db: AsyncSession = Depends(get_db)):
    """
    Stress Test: COUNT(DISTINCT user_id) for a specific device.
    This is notoriously slow in relational databases on large datasets.
    """
    start_time = time.perf_counter()
    stmt = select(func.count(func.distinct(RawEvent.user_id))).where(RawEvent.device_id == device_id)
    result = await db.execute(stmt)
    count = result.scalar()
    execution_time = time.perf_counter() - start_time
    
    return {
        "device_id": device_id,
        "unique_users_count": count,
        "execution_time_ms": round(execution_time * 1000, 2)
    }

@router.get("/events/deep-skip")
async def deep_skip_events(offset: int = 50000, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """
    Stress Test: Deep Pagination (OFFSET).
    Postgres must scan and discard all rows before the offset.
    """
    start_time = time.perf_counter()
    stmt = select(RawEvent).order_by(RawEvent.id).offset(offset).limit(limit)
    result = await db.execute(stmt)
    events = result.scalars().all()
    execution_time = time.perf_counter() - start_time
    
    return {
        "offset": offset,
        "count": len(events),
        "execution_time_ms": round(execution_time * 1000, 2)
    }

@router.get("/users/global-summary")
async def get_global_user_summary(db: AsyncSession = Depends(get_db)):
    """
    Stress Test: Global Group By.
    Calculate total volume and count for every user in the 1M record table.
    """
    start_time = time.perf_counter()
    stmt = select(
        RawEvent.user_id,
        func.count(RawEvent.id).label("total_events"),
        func.sum(RawEvent.amount).label("total_volume")
    ).group_by(RawEvent.user_id)
    
    result = await db.execute(stmt)
    summary = result.all()
    execution_time = time.perf_counter() - start_time
    
    return {
        "user_count": len(summary),
        "execution_time_ms": round(execution_time * 1000, 2),
        "sample": [
            {"user_id": row[0], "events": row[1], "volume": float(row[2])}
            for row in summary[:5]
        ]
    }
