import threading
import time
import uuid
from typing import List, Optional
from sentinel_postgres_engine.db_config import ALERT_TTL_S

class AlertStore:
    def __init__(self, ttl_s: int = 3600) -> None:
        self._ttl_s = ttl_s
        self._lock = threading.Lock()
        self._alerts: List[dict] = []
        self._seen: dict[str, float] = {}

    def add_alert(self, pattern, entity_type, entity_id, detail, time_bucket) -> bool:
        dedup_key = f"{pattern}:{entity_id}:{time_bucket}"
        now = time.time()
        with self._lock:
            self._evict_stale(now)
            if dedup_key in self._seen:
                return False
            self._seen[dedup_key] = now + self._ttl_s
            self._alerts.append({
                "id": uuid.uuid4().hex[:12],
                "pattern": pattern,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "detail": detail,
                "time_bucket": time_bucket,
                "timestamp": now,
            })
            return True

    def _evict_stale(self, now: float) -> None:
        expired = [k for k, exp in self._seen.items() if exp <= now]
        for k in expired:
            del self._seen[k]
        cutoff = now - self._ttl_s
        self._alerts = [a for a in self._alerts if a["timestamp"] >= cutoff]

alert_store = AlertStore()
