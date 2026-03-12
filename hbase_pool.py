"""
HBase connection pool and shared helpers for row-key generation and byte decoding.
"""
import hashlib
import time
import happybase
from config import HBASE_HOST, HBASE_PORT, POOL_SIZE, REVERSE_TS_BASE

# ── Connection Pool (module-level singleton) ──────────────────────────────────
pool = happybase.ConnectionPool(
    size=POOL_SIZE,
    host=HBASE_HOST,
    port=HBASE_PORT,
)


def get_salt(identifier: str) -> str:
    """Return the 1-char hex salt for a given identifier (user_id, dev_id, etc.).

    Must match the ingestion script exactly:
        hashlib.md5(identifier.encode('utf-8')).hexdigest()[0]
    """
    return hashlib.md5(identifier.encode("utf-8")).hexdigest()[0]


def decode_counter(value: bytes) -> int:
    """Decode an HBase atomic counter stored as an 8-byte big-endian long."""
    return int.from_bytes(value, byteorder="big")


def reverse_ts_to_human(reverse_ts_str: str) -> str:
    """Convert a reverse-timestamp string back to 'HH:MM:SS AM/PM'."""
    real_ts_ms = REVERSE_TS_BASE - int(reverse_ts_str)
    return time.strftime("%I:%M:%S %p", time.localtime(real_ts_ms / 1000))


def reverse_ts_to_minute(reverse_ts_str: str) -> str:
    """Return 'HH:MM AM/PM' minute bucket (for grouping revenue)."""
    real_ts_ms = REVERSE_TS_BASE - int(reverse_ts_str)
    return time.strftime("%I:%M %p", time.localtime(real_ts_ms / 1000))
