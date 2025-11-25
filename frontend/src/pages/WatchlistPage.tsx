import React, { useEffect, useState, useMemo } from 'react';
import { watchlistService } from '../api/watchlistService';
import { WatchlistItem, WatchlistCreateRequest } from '../types';
import { toast } from 'react-hot-toast';
import { Eye, Bell, Target, TrendingUp, TrendingDown, Wifi, WifiOff } from 'lucide-react';
import { useWebSocket } from '../hooks/useWebSocket';
import { formatPrice, formatPriceChange, getCurrencySymbol } from '../utils/currency';

const WatchlistPage: React.FC = () => {
    const [items, setItems] = useState<WatchlistItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [showAdd, setShowAdd] = useState(false);

    // Extract symbols and markets for WebSocket subscription
    const symbols = useMemo(() => items.map(item => item.stock.symbol), [items]);
    const markets = useMemo(() => {
        const uniqueMarkets = [...new Set(items.map(item => item.stock.market))];
        return uniqueMarkets.length > 0 ? uniqueMarkets[0] : 'india_nse';
    }, [items]);

    // Connect to WebSocket for real-time price updates
    const { isConnected, priceUpdates } = useWebSocket(symbols, markets);

    const load = async () => {
        try {
            setLoading(true);
            const data = await watchlistService.getWatchlist();
            setItems(data.items);
        } catch (e: any) {
            toast.error(e.response?.data?.detail || 'Failed to load watchlist');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        load();
    }, []);

    const handleRemove = async (id: number, symbol: string) => {
        if (!window.confirm(`Remove ${symbol} from watchlist?`)) return;
        try {
            await watchlistService.remove(id);
            toast.success(`${symbol} removed from watchlist`);
            load();
        } catch {
            toast.error('Failed to remove from watchlist');
        }
    };

    const handleAdd = async (payload: WatchlistCreateRequest) => {
        try {
            await watchlistService.addOrUpdate(payload);
            toast.success('Watchlist updated');
            setShowAdd(false);
            load();
        } catch (e: any) {
            toast.error(e.response?.data?.detail || 'Failed to update watchlist');
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 dark:border-blue-400"></div>
            </div>
        );
    }

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
                <div>
                    <div className="flex items-center gap-2 mb-2">
                        <Eye className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                        <h1 className="text-3xl lg:text-4xl font-bold text-gray-900 dark:text-gray-100">My Watchlist</h1>
                    </div>
                    <p className="text-gray-500 dark:text-gray-400 text-sm">
                        Monitor stocks you're interested in and get real-time alerts
                    </p>
                </div>
                <button
                    onClick={() => setShowAdd(true)}
                    className="btn-primary flex items-center gap-2"
                >
                    <span className="text-lg">+</span>
                    Add Stock
                </button>
            </div>

            {/* Real-time Connection Status */}
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2 text-sm">
                    {isConnected ? (
                        <>
                            <Wifi className="w-4 h-4 text-green-500" />
                            <span className="text-green-600 dark:text-green-400">Live prices active</span>
                        </>
                    ) : (
                        <>
                            <WifiOff className="w-4 h-4 text-gray-400" />
                            <span className="text-gray-500 dark:text-gray-400">Connecting to live prices...</span>
                        </>
                    )}
                </div>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 lg:gap-6">
                <MetricCard
                    title="Total Stocks"
                    value={items.length.toString()}
                    icon="📊"
                    gradient="from-blue-500 via-blue-600 to-blue-700"
                />
                <MetricCard
                    title="Price Alerts"
                    value={items.filter(item => item.alert_on_price_change).length.toString()}
                    icon="🔔"
                    gradient="from-purple-500 via-purple-600 to-purple-700"
                />
                <MetricCard
                    title="AI Signals"
                    value={items.filter(item => item.alert_on_ai_signal).length.toString()}
                    icon="🤖"
                    gradient="from-success-500 via-success-600 to-success-700"
                />
            </div>

            {/* Watchlist Table */}
            <div className="card overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-200 dark:border-slate-700 bg-gradient-to-r from-gray-50 to-gray-100/50 dark:from-slate-800 dark:to-slate-800/50">
                    <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
                        <span className="w-1 h-6 bg-gradient-to-b from-primary-600 to-primary-700 rounded-full"></span>
                        Stocks ({items.length})
                    </h2>
                </div>

                {items.length === 0 ? (
                    <div className="text-center py-16">
                        <div className="w-20 h-20 bg-gradient-to-br from-primary-100 to-blue-100 dark:from-primary-900/30 dark:to-blue-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
                            <Eye className="w-10 h-10 text-primary-600 dark:text-primary-400" />
                        </div>
                        <p className="text-gray-500 dark:text-gray-400 mb-2 font-medium">Your watchlist is empty</p>
                        <p className="text-sm text-gray-400 dark:text-gray-500 mb-6">Start tracking stocks by adding them to your watchlist</p>
                        <button
                            onClick={() => setShowAdd(true)}
                            className="btn-primary"
                        >
                            Add Your First Stock
                        </button>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200 dark:divide-slate-700">
                            <thead className="bg-gradient-to-r from-gray-50 to-gray-100/50 dark:from-slate-800 dark:to-slate-800/50">
                                <tr>
                                    <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                                        Stock
                                    </th>
                                    <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                                        Market
                                    </th>
                                    <th className="px-6 py-4 text-right text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                                        Current Price
                                    </th>
                                    <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                                        Price Alert
                                    </th>
                                    <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                                        Targets
                                    </th>
                                    <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                                        AI Signal
                                    </th>
                                    <th className="px-6 py-4 text-right text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                                        Actions
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="bg-white dark:bg-slate-800 divide-y divide-gray-100 dark:divide-slate-700">
                                {items.map((item) => (
                                    <WatchlistRow
                                        key={item.id}
                                        item={item}
                                        onRemove={handleRemove}
                                        livePriceUpdate={priceUpdates.get(item.stock.symbol)}
                                        isConnected={isConnected}
                                    />
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {showAdd && (
                <AddWatchlistModal
                    onClose={() => setShowAdd(false)}
                    onSubmit={handleAdd}
                />
            )}
        </div>
    );
};

// Metric Card Component
interface MetricCardProps {
    title: string;
    value: string;
    icon: string;
    gradient?: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, icon, gradient = 'from-gray-500 via-gray-600 to-gray-700' }) => (
    <div className={`metric-card group bg-gradient-to-br ${gradient} text-white`}>
        <div className="relative z-10 flex items-center justify-between">
            <div>
                <p className="text-white/90 text-sm font-medium mb-2">{title}</p>
                <p className="text-2xl lg:text-3xl font-bold text-white">{value}</p>
            </div>
            <div className="w-12 h-12 lg:w-14 lg:h-14 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                <span className="text-2xl">{icon}</span>
            </div>
        </div>
    </div>
);

// Watchlist Row Component
interface WatchlistRowProps {
    item: WatchlistItem;
    onRemove: (id: number, symbol: string) => void;
    livePriceUpdate?: {
        type: 'price_update';
        symbol: string;
        market: string;
        current_price: number;
        previous_close: number;
        change: number;
        change_percent: number;
        timestamp: string;
    };
    isConnected: boolean;
}

const WatchlistRow: React.FC<WatchlistRowProps> = ({ item, onRemove, livePriceUpdate, isConnected }) => {
    const marketDisplay = item.stock.market
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');

    // Use live price if available, otherwise use initial price
    const current_price = livePriceUpdate?.current_price ?? item.stock.current_price;

    // Get price change from live update if available
    const priceChange = livePriceUpdate?.change ?? 0;
    const priceChangePercent = livePriceUpdate?.change_percent ?? 0;

    const market = item.stock.market;

    return (
        <tr className="table-row">
            <td className="px-6 py-4 whitespace-nowrap">
                <div>
                    <div className="text-sm font-semibold text-gray-900 dark:text-gray-100">{item.stock.symbol}</div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">{item.stock.company_name}</div>
                </div>
            </td>
            <td className="px-6 py-4 whitespace-nowrap">
                <span className="badge badge-primary">{marketDisplay}</span>
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-right">
                {current_price != null ? (
                    <div className="flex flex-col items-end gap-1">
                        <div className="flex items-center gap-2">
                            <span className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                                {formatPrice(current_price, market)}
                            </span>
                            {livePriceUpdate && (
                                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" title="Live price"></div>
                            )}
                        </div>
                        {livePriceUpdate && (
                            <span className={`text-xs font-medium flex items-center gap-1 ${priceChange >= 0
                                ? 'text-success-600 dark:text-success-400'
                                : 'text-danger-600 dark:text-danger-400'
                                }`}>
                                {priceChange >= 0 ? (
                                    <TrendingUp className="w-3 h-3" />
                                ) : (
                                    <TrendingDown className="w-3 h-3" />
                                )}
                                <span>
                                    {priceChangePercent >= 0 ? '+' : ''}{priceChangePercent.toFixed(2)}% ({formatPriceChange(priceChange, market)})
                                </span>
                            </span>
                        )}
                    </div>
                ) : (
                    <div className="flex flex-col items-end gap-1">
                        {isConnected ? (
                            <>
                                <span className="text-sm text-gray-400 dark:text-gray-500 italic">Loading price...</span>
                                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" title="Waiting for price data"></div>
                            </>
                        ) : (
                            <span className="text-sm text-gray-400 dark:text-gray-500">-</span>
                        )}
                    </div>
                )}
            </td>
            <td className="px-6 py-4 whitespace-nowrap">
                {item.alert_on_price_change ? (
                    <div className="flex items-center gap-2">
                        <Bell className="w-4 h-4 text-success-600 dark:text-success-400" />
                        <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                            {item.alert_threshold_percent.toFixed(1)}%
                        </span>
                    </div>
                ) : (
                    <span className="text-sm text-gray-400 dark:text-gray-500">Off</span>
                )}
            </td>
            <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex flex-col gap-1">
                    {item.target_buy_price && (
                        <div className="flex items-center gap-1 text-xs">
                            <TrendingUp className="w-3 h-3 text-success-600 dark:text-success-400" />
                            <span className="text-success-700 dark:text-success-300 font-medium">
                                Buy ≤ {formatPrice(item.target_buy_price, market)}
                            </span>
                        </div>
                    )}
                    {item.target_sell_price && (
                        <div className="flex items-center gap-1 text-xs">
                            <Target className="w-3 h-3 text-danger-600 dark:text-danger-400" />
                            <span className="text-danger-700 dark:text-danger-300 font-medium">
                                Sell ≥ {formatPrice(item.target_sell_price, market)}
                            </span>
                        </div>
                    )}
                    {!item.target_buy_price && !item.target_sell_price && (
                        <span className="text-xs text-gray-400 dark:text-gray-500">None</span>
                    )}
                </div>
            </td>
            <td className="px-6 py-4 whitespace-nowrap">
                {item.alert_on_ai_signal ? (
                    <span className="badge badge-success">On</span>
                ) : (
                    <span className="badge badge-primary">Off</span>
                )}
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                <button
                    onClick={() => onRemove(item.id, item.stock.symbol)}
                    className="text-danger-600 dark:text-danger-400 hover:text-danger-700 dark:hover:text-danger-300 font-medium hover:underline transition-colors"
                >
                    Remove
                </button>
            </td>
        </tr>
    );
};

interface AddWatchlistModalProps {
    onClose: () => void;
    onSubmit: (payload: WatchlistCreateRequest) => void;
}

const AddWatchlistModal: React.FC<AddWatchlistModalProps> = ({
    onClose,
    onSubmit,
}) => {
    const [form, setForm] = useState<WatchlistCreateRequest>({
        symbol: '',
        market: 'india_nse',
        alert_on_price_change: true,
        alert_threshold_percent: 5,
        alert_on_ai_signal: true,
        target_buy_price: null,
        target_sell_price: null,
        notes: '',
    });
    const [loading, setLoading] = useState(false);

    const handleChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>,
    ) => {
        const { name, value, type, checked } = e.target as any;
        setForm((prev) => ({
            ...prev,
            [name]:
                type === 'checkbox'
                    ? checked
                    : ['target_buy_price', 'target_sell_price', 'alert_threshold_percent'].includes(
                        name,
                    )
                        ? value === '' ? null : parseFloat(value)
                        : value,
        }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!form.symbol) {
            toast.error('Symbol is required');
            return;
        }
        try {
            setLoading(true);
            await onSubmit({ ...form, symbol: form.symbol.toUpperCase() });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-40 dark:bg-opacity-60 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
                <div className="px-6 py-4 border-b border-gray-200 dark:border-slate-700 bg-gradient-to-r from-gray-50 to-gray-100/50 dark:from-slate-800 dark:to-slate-800/50 flex justify-between items-center sticky top-0 bg-white dark:bg-slate-800">
                    <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
                        <Eye className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                        Add to Watchlist
                    </h2>
                    <button
                        onClick={onClose}
                        className="text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 transition-colors p-1 hover:bg-gray-100 dark:hover:bg-slate-700 rounded-lg"
                    >
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>
                <form onSubmit={handleSubmit} className="px-6 py-6 space-y-5">
                    <div>
                        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                            Stock Symbol *
                        </label>
                        <input
                            name="symbol"
                            value={form.symbol}
                            onChange={handleChange}
                            placeholder="RELIANCE"
                            className="input-field"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                            Market *
                        </label>
                        <select
                            name="market"
                            value={form.market}
                            onChange={handleChange}
                            className="input-field"
                            required
                        >
                            <option value="india_nse">India NSE</option>
                            <option value="india_bse">India BSE</option>
                            <option value="us_nyse">US NYSE</option>
                            <option value="us_nasdaq">US NASDAQ</option>
                        </select>
                    </div>
                    <div className="flex items-center gap-3 p-4 bg-primary-50 dark:bg-primary-900/20 rounded-xl border border-primary-100 dark:border-primary-800">
                        <input
                            id="alert_on_price_change"
                            type="checkbox"
                            name="alert_on_price_change"
                            checked={form.alert_on_price_change ?? true}
                            onChange={handleChange}
                            className="w-5 h-5 text-primary-600 dark:text-primary-400 border-gray-300 dark:border-slate-600 rounded focus:ring-primary-500 bg-white dark:bg-slate-700"
                        />
                        <label htmlFor="alert_on_price_change" className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-2">
                            <Bell className="w-4 h-4 text-primary-600 dark:text-primary-400" />
                            Alert on price change
                        </label>
                    </div>
                    {form.alert_on_price_change && (
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                                Alert Threshold (% move)
                            </label>
                            <input
                                type="number"
                                name="alert_threshold_percent"
                                value={form.alert_threshold_percent ?? 5}
                                onChange={handleChange}
                                className="input-field"
                                step="0.5"
                                min="0.5"
                            />
                        </div>
                    )}
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="flex items-center gap-2 text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                                <TrendingUp className="w-4 h-4 text-success-600 dark:text-success-400" />
                                Target Buy Price ({getCurrencySymbol(form.market)})
                            </label>
                            <input
                                type="number"
                                name="target_buy_price"
                                value={form.target_buy_price ?? ''}
                                onChange={handleChange}
                                className="input-field"
                                step="0.1"
                                min="0"
                                placeholder="Optional"
                            />
                        </div>
                        <div>
                            <label className="flex items-center gap-2 text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                                <Target className="w-4 h-4 text-danger-600 dark:text-danger-400" />
                                Target Sell Price ({getCurrencySymbol(form.market)})
                            </label>
                            <input
                                type="number"
                                name="target_sell_price"
                                value={form.target_sell_price ?? ''}
                                onChange={handleChange}
                                className="input-field"
                                step="0.1"
                                min="0"
                                placeholder="Optional"
                            />
                        </div>
                    </div>
                    <div className="flex items-center gap-3 p-4 bg-purple-50 dark:bg-purple-900/20 rounded-xl border border-purple-100 dark:border-purple-800">
                        <input
                            id="alert_on_ai_signal"
                            type="checkbox"
                            name="alert_on_ai_signal"
                            checked={form.alert_on_ai_signal ?? true}
                            onChange={handleChange}
                            className="w-5 h-5 text-purple-600 dark:text-purple-400 border-gray-300 dark:border-slate-600 rounded focus:ring-purple-500 bg-white dark:bg-slate-700"
                        />
                        <label htmlFor="alert_on_ai_signal" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                            Alert when AI gives strong BUY/SELL signal
                        </label>
                    </div>
                    <div>
                        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Notes</label>
                        <textarea
                            name="notes"
                            value={form.notes ?? ''}
                            onChange={handleChange}
                            rows={3}
                            className="input-field"
                            placeholder="Optional notes about this stock..."
                        />
                    </div>
                    <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-slate-700">
                        <button
                            type="button"
                            onClick={onClose}
                            className="btn-secondary"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={loading}
                            className="btn-primary"
                        >
                            {loading ? 'Saving...' : 'Add to Watchlist'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default WatchlistPage;
