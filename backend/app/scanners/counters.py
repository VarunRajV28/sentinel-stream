import asyncio
import logging
import time
import happybase

from app.core.config import (
    settings,
    TABLE_RISK,
    TABLE_VELOCITY,
    TOXIC_HITS_ALERT,
    VELOCITY_SUM_ALERT,
)
from app.db.hbase_pool       import decode_counter
from app.state               import alerted_toxic, alerted_velocity, user_totals
from app.services.ws_manager import manager

log = logging.getLogger("ids.scanner.counters")


def _scan_counters_once() -> tuple[dict[str, int], list[dict], list[dict]]:
    """Run one blocking happybase scan cycle and return derived state + alerts."""
    conn = happybase.Connection(settings.HBASE_HOST, port=settings.HBASE_PORT)
    try:
        vel_table = conn.table(TABLE_VELOCITY)
        user_totals_cents: dict[str, int] = {}
        velocity_alerts: list[dict] = []

        for row_key_bytes, data in vel_table.scan(batch_size=500):
            parts = row_key_bytes.decode("utf-8").split("-")
            if len(parts) < 3:
                continue
            user_id = "-".join(parts[1:-1])
            tx_sum  = decode_counter(data[b"v:tx_sum_cents"]) if b"v:tx_sum_cents" in data else 0

            user_totals_cents[user_id] = user_totals_cents.get(user_id, 0) + tx_sum

            if tx_sum > VELOCITY_SUM_ALERT and user_id not in alerted_velocity:
                alerted_velocity.add(user_id)
                velocity_alerts.append({
                    "type":    "ALERT",
                    "pattern": "Rapid Transfers",
                    "entity":  user_id,
                    "detail":  f"Total transfer sum ₹{tx_sum / 100:,.2f} exceeds threshold.",
                    "ts":      time.strftime("%H:%M:%S"),
                    "log":     f"Rapid Transfers: user={user_id}  sum=${tx_sum / 100:.2f}",
                })

        risk_table = conn.table(TABLE_RISK)
        toxic_alerts: list[dict] = []
        for row_key_bytes, data in risk_table.scan(batch_size=500):
            parts = row_key_bytes.decode("utf-8").split("-")
            if len(parts) < 3:
                continue
            dev_id       = "-".join(parts[1:-1])
            interactions = decode_counter(data[b"c:interactions"]) if b"c:interactions" in data else 0

            if interactions > TOXIC_HITS_ALERT and dev_id not in alerted_toxic:
                alerted_toxic.add(dev_id)
                toxic_alerts.append({
                    "type":    "ALERT",
                    "pattern": "Suspicious Node",
                    "entity":  dev_id,
                    "detail":  f"Device interacted with {interactions} distinct accounts.",
                    "ts":      time.strftime("%H:%M:%S"),
                    "log":     f"Suspicious Node: dev={dev_id}  interactions={interactions}",
                })

        return user_totals_cents, velocity_alerts, toxic_alerts
    finally:
        conn.close()


async def counter_scanner_loop() -> None:
    log.info("Counter scanner started.")

    while True:
        try:
            user_totals_cents, velocity_alerts, toxic_alerts = await asyncio.to_thread(_scan_counters_once)

            user_totals.clear()
            user_totals.update({uid: cents / 100 for uid, cents in user_totals_cents.items()})

            for alert in velocity_alerts:
                log.warning(alert.pop("log"))
                await manager.broadcast(alert)

            for alert in toxic_alerts:
                log.warning(alert.pop("log"))
                await manager.broadcast(alert)

        except Exception:
            log.exception("Counter scanner error - retrying next cycle")

        await asyncio.sleep(2)
