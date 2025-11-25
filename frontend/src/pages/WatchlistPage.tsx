import React, { useEffect, useState } from 'react';
import { watchlistService } from '../api/watchlistService';
import { WatchlistItem, WatchlistCreateRequest } from '../types';
import { toast } from 'react-hot-toast';
import { Eye, Bell, Target, TrendingUp } from 'lucide-react';

const WatchlistPage: React.FC = () => {
    const [items, setItems] = useState<WatchlistItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [showAdd, setShowAdd] = useState(false);

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
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
                <div>
                    <div className="flex items-center gap-2 mb-2">
                        <Eye className="w-6 h-6 text-primary-600" />
                        <h1 className="text-3xl lg:text-4xl font-bold text-gray-900">My Watchlist</h1>
                    </div>
                    <p className="text-gray-500 text-sm">
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
                <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-gray-100/50">
                    <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                        <span className="w-1 h-6 bg-gradient-to-b from-primary-600 to-primary-700 rounded-full"></span>
                        Stocks ({items.length})
                    </h2>
                </div>

                {items.length === 0 ? (
                    <div className="text-center py-16">
                        <div className="w-20 h-20 bg-gradient-to-br from-primary-100 to-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                            <Eye className="w-10 h-10 text-primary-600" />
                        </div>
                        <p className="text-gray-500 mb-2 font-medium">Your watchlist is empty</p>
                        <p className="text-sm text-gray-400 mb-6">Start tracking stocks by adding them to your watchlist</p>
                        <button
                            onClick={() => setShowAdd(true)}
                            className="btn-primary"
                        >
                            Add Your First Stock
                        </button>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gradient-to-r from-gray-50 to-gray-100/50">
                                <tr>
                                    <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                                        Stock
                                    </th>
                                    <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                                        Market
                                    </th>
                                    <th className="px-6 py-4 text-right text-xs font-bold text-gray-700 uppercase tracking-wider">
                                        Current Price
                                    </th>
                                    <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                                        Price Alert
                                    </th>
                                    <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                                        Targets
                                    </th>
                                    <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                                        AI Signal
                                    </th>
                                    <th className="px-6 py-4 text-right text-xs font-bold text-gray-700 uppercase tracking-wider">
                                        Actions
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-100">
                                {items.map((item) => (
                                    <WatchlistRow
                                        key={item.id}
                                        item={item}
                                        onRemove={handleRemove}
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
}

const WatchlistRow: React.FC<WatchlistRowProps> = ({ item, onRemove }) => {
    const marketDisplay = item.stock.market
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');

    return (
        <tr className="table-row">
            <td className="px-6 py-4 whitespace-nowrap">
                <div>
                    <div className="text-sm font-semibold text-gray-900">{item.stock.symbol}</div>
                    <div className="text-xs text-gray-500">{item.stock.company_name}</div>
                </div>
            </td>
            <td className="px-6 py-4 whitespace-nowrap">
                <span className="badge badge-primary">{marketDisplay}</span>
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-right">
                {item.stock.current_price != null ? (
                    <span className="text-sm font-semibold text-gray-900">
                        ₹{item.stock.current_price.toFixed(2)}
                    </span>
                ) : (
                    <span className="text-sm text-gray-400">-</span>
                )}
            </td>
            <td className="px-6 py-4 whitespace-nowrap">
                {item.alert_on_price_change ? (
                    <div className="flex items-center gap-2">
                        <Bell className="w-4 h-4 text-success-600" />
                        <span className="text-sm font-medium text-gray-900">
                            {item.alert_threshold_percent.toFixed(1)}%
                        </span>
                    </div>
                ) : (
                    <span className="text-sm text-gray-400">Off</span>
                )}
            </td>
            <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex flex-col gap-1">
                    {item.target_buy_price && (
                        <div className="flex items-center gap-1 text-xs">
                            <TrendingUp className="w-3 h-3 text-success-600" />
                            <span className="text-success-700 font-medium">
                                Buy ≤ ₹{item.target_buy_price.toFixed(2)}
                            </span>
                        </div>
                    )}
                    {item.target_sell_price && (
                        <div className="flex items-center gap-1 text-xs">
                            <Target className="w-3 h-3 text-danger-600" />
                            <span className="text-danger-700 font-medium">
                                Sell ≥ ₹{item.target_sell_price.toFixed(2)}
                            </span>
                        </div>
                    )}
                    {!item.target_buy_price && !item.target_sell_price && (
                        <span className="text-xs text-gray-400">None</span>
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
                    className="text-danger-600 hover:text-danger-700 font-medium hover:underline transition-colors"
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
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
                <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-gray-100/50 flex justify-between items-center sticky top-0 bg-white">
                    <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                        <Eye className="w-5 h-5 text-primary-600" />
                        Add to Watchlist
                    </h2>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-gray-600 transition-colors p-1 hover:bg-gray-100 rounded-lg"
                    >
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>
                <form onSubmit={handleSubmit} className="px-6 py-6 space-y-5">
                    <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">
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
                        <label className="block text-sm font-semibold text-gray-700 mb-2">
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
                    <div className="flex items-center gap-3 p-4 bg-primary-50 rounded-xl border border-primary-100">
                        <input
                            id="alert_on_price_change"
                            type="checkbox"
                            name="alert_on_price_change"
                            checked={form.alert_on_price_change ?? true}
                            onChange={handleChange}
                            className="w-5 h-5 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                        />
                        <label htmlFor="alert_on_price_change" className="text-sm font-medium text-gray-700 flex items-center gap-2">
                            <Bell className="w-4 h-4 text-primary-600" />
                            Alert on price change
                        </label>
                    </div>
                    {form.alert_on_price_change && (
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-2">
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
                            <label className="flex items-center gap-2 text-sm font-semibold text-gray-700 mb-2">
                                <TrendingUp className="w-4 h-4 text-success-600" />
                                Target Buy Price (₹)
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
                            <label className="flex items-center gap-2 text-sm font-semibold text-gray-700 mb-2">
                                <Target className="w-4 h-4 text-danger-600" />
                                Target Sell Price (₹)
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
                    <div className="flex items-center gap-3 p-4 bg-purple-50 rounded-xl border border-purple-100">
                        <input
                            id="alert_on_ai_signal"
                            type="checkbox"
                            name="alert_on_ai_signal"
                            checked={form.alert_on_ai_signal ?? true}
                            onChange={handleChange}
                            className="w-5 h-5 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                        />
                        <label htmlFor="alert_on_ai_signal" className="text-sm font-medium text-gray-700">
                            Alert when AI gives strong BUY/SELL signal
                        </label>
                    </div>
                    <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">Notes</label>
                        <textarea
                            name="notes"
                            value={form.notes ?? ''}
                            onChange={handleChange}
                            rows={3}
                            className="input-field"
                            placeholder="Optional notes about this stock..."
                        />
                    </div>
                    <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
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
