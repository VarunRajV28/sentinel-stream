import asyncio
import random
import uuid
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sentinel_postgres_engine.db_config import DATABASE_URL
from sentinel_postgres_engine.models import Base, RawEvent

# This script generates 1 million events to simulate a high-load environment
async def seed_data(count=1_000_000):
    engine = create_async_engine(DATABASE_URL)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print(f"Seeding {count} records into Postgres...")
    
    batch_size = 5000
    user_ids = [f"user_{i:05d}" for i in range(1000)]
    device_ids = [str(uuid.uuid4())[:8] for _ in range(200)]
    event_types = ["login_failed", "login_success", "transfer_attempt", "password_reset"]
    
    start_ts = datetime.utcnow() - timedelta(days=30)
    
    for i in range(0, count, batch_size):
        async with AsyncSessionLocal() as session:
            batch = []
            for j in range(batch_size):
                idx = i + j
                if idx >= count: break
                
                ts = start_ts + timedelta(seconds=idx * (30*24*3600 / count))
                batch.append(RawEvent(
                    user_id=random.choice(user_ids),
                    timestamp=ts,
                    event_type=random.choice(event_types),
                    amount=round(random.uniform(10, 5000), 2),
                    status=random.choice(["SUCCESS", "FAILED"]),
                    ip_address=f"192.168.1.{random.randint(1, 254)}",
                    device_id=random.choice(device_ids)
                ))
            session.add_all(batch)
            await session.commit()
            if (i + batch_size) % 50000 == 0:
                print(f"Progress: {i + batch_size}/{count} rows")

    print("Seeding complete.")

if __name__ == "__main__":
    asyncio.run(seed_data())
