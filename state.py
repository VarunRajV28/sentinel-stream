"""
Global in-memory state shared across all scanner tasks and REST endpoints.

All variables are module-level singletons — importers mutate them directly.
No locks are needed because:
  • asyncio is single-threaded; the scanners run as coroutines and never
    preempt each other in the middle of a Python statement.
  • Counter and defaultdict operations are atomic at the CPython level.
"""
import collections
from typing import Dict

# Maps "HH:MM AM/PM" → cumulative dollar amount transferred in that minute
minute_revenue: Dict[str, float] = collections.defaultdict(float)

# Total money moved per user_id (Whales leaderboard)
user_totals: collections.Counter = collections.Counter()

# Raw event hits per device ID (m:dev)
device_counts: collections.Counter = collections.Counter()

# Global authentication funnel counters
auth_funnel: Dict[str, int] = {"success": 0, "failed": 0}

# ── Alert deduplication (session-scoped) ─────────────────────────────────────
# Once an entity is added here it will NOT trigger another WebSocket broadcast
# for the same pattern until the process restarts.
alerted_velocity: set = set()   # user_ids already flagged for Velocity Fraud
alerted_toxic: set    = set()   # dev_ids  already flagged as Toxic Node
