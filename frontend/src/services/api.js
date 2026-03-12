/**
 * API service layer: all network calls in one place.
 * Components import named functions here; never call fetch() directly.
 */

/**
 * Fetch per-minute revenue totals.
 * @returns {Promise<Record<string, number>>} Map of "HH:MM AM/PM" -> USD amount.
 */
export async function fetchRevenue() {
  const res = await fetch("/api/metrics/revenue");
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

/**
 * Fetch a user's velocity profile from HBase.
 * @param {string} userId - e.g. "user_42"
 * @returns {Promise<object|null>} Profile object, or null if the user doesn't exist.
 */
export async function fetchUserProfile(userId) {
  const res = await fetch(`/api/user/${encodeURIComponent(userId)}/profile`);
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

/**
 * Fetch a user's 10 most recent events from the ledger.
 * @param {string} userId - e.g. "user_42"
 * @returns {Promise<object|null>} History payload, or null if the user doesn't exist.
 */
export async function fetchUserHistory(userId) {
  const res = await fetch(`/api/user/${encodeURIComponent(userId)}/history`);
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}
