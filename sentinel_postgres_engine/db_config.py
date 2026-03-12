import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5433")
POSTGRES_DB = os.getenv("POSTGRES_DB", "sentinel_stream")

DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Fraud Thresholds (matching HBase version)
VELOCITY_SUM_CENTS = 500_000   # $5,000.00
VELOCITY_TX_COUNT = 4
TOXIC_INTERACTIONS = 3

# Alert Thresholds
VELOCITY_SUM_ALERT = 1_000_000  # $10,000
TOXIC_HITS_ALERT = 50
BRUTE_FORCE_THRESH = 50

# Pattern Windows
ATO_TIME_WINDOW_MS = 300_000  # 5 minutes

# Alert Deduplication
ALERT_TTL_S = 3600             # 1 hour dedup window
