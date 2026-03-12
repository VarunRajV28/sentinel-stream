/**
 * Currency formatter.
 * @param {number} value - Numeric amount in USD.
 * @param {number} [decimals=2] - Number of decimal places.
 */
export const formatCurrency = (value, decimals = 2) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
