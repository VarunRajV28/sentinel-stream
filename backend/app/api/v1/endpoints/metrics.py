"""
Endpoint — Global Metrics (in-memory reads).

All endpoints here read from the module-level state singletons updated by the
background scanner tasks.  They never touch HBase directly, so latency is
sub-millisecond regardless of cluster load.

Endpoints
---------
GET /api/metrics/revenue  — per-minute transfer totals
GET /api/metrics/whales   — top-10 users by amount transacted
GET /api/metrics/devices  — top-10 most active device IDs
GET /api/metrics/auth     — success / failure funnel totals
"""
from fastapi import APIRouter

from app.state import auth_funnel, device_counts, minute_revenue, user_totals

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("/revenue")
def get_revenue():
    """Revenue aggregated per minute from successful transfer_attempt events."""
    return dict(minute_revenue)


@router.get("/whales")
def get_whales():
    """Top 10 users by total dollar amount transacted (Whales leaderboard)."""
    return [
        {"user_id": uid, "total_amount": round(amt, 2)}
        for uid, amt in user_totals.most_common(10)
    ]


@router.get("/devices")
def get_devices():
    """Top 10 most active device IDs by raw event count."""
    return [
        {"device_id": dev, "event_count": count}
        for dev, count in device_counts.most_common(10)
    ]


@router.get("/auth")
def get_auth():
    """Global authentication funnel: successes, failures, and failure rate."""
    total = auth_funnel["success"] + auth_funnel["failed"]
    return {
        **auth_funnel,
        "total":        total,
        "failure_rate": round(auth_funnel["failed"] / total * 100, 2) if total else 0,
    }
