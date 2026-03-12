"""
IDS Backend Configuration — Constants, thresholds, and HBase connection settings.
"""
import sys

# ── HBase Connection ──────────────────────────────────────────────────────────
HBASE_HOST = "10.120.232.230"
HBASE_PORT = 9090
POOL_SIZE = 10

# ── Table Names ───────────────────────────────────────────────────────────────
TABLE_EVENT_LEDGER = "user_event_ledger"
TABLE_VELOCITY = "user_velocity_counters"
TABLE_RISK = "entity_risk_counters"

# ── Fraud Thresholds ─────────────────────────────────────────────────────────
VELOCITY_SUM_CENTS = 500_000   # $5,000.00
VELOCITY_TX_COUNT = 4
TOXIC_INTERACTIONS = 3

# ── Background Task Poll Intervals (seconds) ─────────────────────────────────
VELOCITY_INTERVAL_S = 10
TOXIC_INTERVAL_S = 10
ATO_INTERVAL_S = 15

# ── ATO Detection ────────────────────────────────────────────────────────────
ATO_SCAN_LIMIT = 5000          # Max rows per salt prefix scan
ATO_TIME_WINDOW_MS = 300_000   # 5-minute sliding window for the ATO sequence

# ── Alert Deduplication ──────────────────────────────────────────────────────
ALERT_TTL_S = 3600             # 1 hour dedup window

# ── Reverse Timestamp Base (must match ingestion script) ─────────────────────
REVERSE_TS_BASE = sys.maxsize

# ── Pre-computed Hex Salts (the 4-region pre-split uses ['4','8','c']) ────────
HEX_SALTS = [format(i, "x") for i in range(16)]  # '0' .. 'f'

# ── Alert Thresholds (Background Scanner v2) ────────────────────────────────
VELOCITY_SUM_ALERT  = 1_000_000  # cents → $10,000 total transferred
TOXIC_HITS_ALERT    = 50         # distinct-account interactions per device
BRUTE_FORCE_THRESH  = 50         # login_failed events in one 1-second window
