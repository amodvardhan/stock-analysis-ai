/**
 * Currency utility functions for market-based formatting
 * 
 * Rules:
 * - US markets (us_nyse, us_nasdaq): Use USD ($)
 * - All other markets (India, etc.): Use INR (₹)
 */

/**
 * Check if a market is a US market
 */
export const isUSMarket = (market: string): boolean => {
    return market?.startsWith('us_') || false;
};

/**
 * Get currency symbol for a market
 */
export const getCurrencySymbol = (market: string): string => {
    return isUSMarket(market) ? '$' : '₹';
};

/**
 * Get currency code for a market
 */
export const getCurrencyCode = (market: string): string => {
    return isUSMarket(market) ? 'USD' : 'INR';
};

/**
 * Format a price value with appropriate currency symbol
 */
export const formatPrice = (price: number | null | undefined, market: string, decimals: number = 2): string => {
    if (price == null || isNaN(price)) return '-';
    const symbol = getCurrencySymbol(market);
    return `${symbol}${price.toFixed(decimals)}`;
};

/**
 * Format a price change with appropriate currency symbol
 */
export const formatPriceChange = (change: number | null | undefined, market: string, decimals: number = 2): string => {
    if (change == null || isNaN(change)) return '-';
    const symbol = getCurrencySymbol(market);
    const sign = change >= 0 ? '+' : '';
    return `${sign}${symbol}${Math.abs(change).toFixed(decimals)}`;
};

/**
 * Format a price with locale-aware formatting
 */
export const formatPriceLocale = (
    price: number | null | undefined,
    market: string,
    options?: { minimumFractionDigits?: number; maximumFractionDigits?: number }
): string => {
    if (price == null || isNaN(price)) return '-';
    const currency = getCurrencyCode(market);
    const locale = isUSMarket(market) ? 'en-US' : 'en-IN';

    // Ensure minimumFractionDigits is never greater than maximumFractionDigits
    const maxFractionDigits = options?.maximumFractionDigits ?? 2;
    const minFractionDigits = options?.minimumFractionDigits ?? Math.min(2, maxFractionDigits);
    const finalMinFractionDigits = Math.min(minFractionDigits, maxFractionDigits);

    return new Intl.NumberFormat(locale, {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: finalMinFractionDigits,
        maximumFractionDigits: maxFractionDigits,
    }).format(price);
};

