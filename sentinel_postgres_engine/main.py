from fastapi import FastAPI, Depends
from sentinel_postgres_engine.stress_tests import router as stress_router
from sentinel_postgres_engine.db import init_db, get_db
from sentinel_postgres_engine.models import DeviceStats

app = FastAPI(title="Sentinel Postgres Engine (Comparative)")

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.post("/api/analytics/device/{device_id}/velocity-tick")
async def velocity_tick(device_id: str, db: AsyncSession = Depends(get_db)):
    """
    Stress Test: Row-level locking and MVCC overhead.
    Uses INSERT ... ON CONFLICT to force locking on the device row.
    """
    stmt = pg_insert(DeviceStats).values(
        device_id=device_id,
        velocity_score=1
    ).on_conflict_do_update(
        index_elements=["device_id"],
        set_={"velocity_score": DeviceStats.velocity_score + 1}
    )
    
    await db.execute(stmt)
    await db.commit()
    
    return {"status": "ok", "device_id": device_id}

app.include_router(stress_router)

@app.get("/health")
async def health():
    return {"status": "ok", "backend": "postgres"}
