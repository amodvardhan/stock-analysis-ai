import React, { useState, useEffect } from 'react';
import { portfolioService } from '../api/portfolioService';
import { PortfolioSummary, PortfolioHolding } from '../types';
import { toast } from 'react-hot-toast';
import AddHoldingModal from './AddHoldingModal';

export const Portfolio: React.FC = () => {
    const [summary, setSummary] = useState<PortfolioSummary | null>(null);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [showAddModal, setShowAddModal] = useState(false);

    useEffect(() => {
        loadPortfolio();
    }, []);

    const loadPortfolio = async () => {
        try {
            setLoading(true);
            const data = await portfolioService.getPortfolioSummary();
            setSummary(data);
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to load portfolio');
        } finally {
            setLoading(false);
        }
    };

    const handleRefresh = async () => {
        try {
            setRefreshing(true);
            await portfolioService.refreshPortfolio();
            await loadPortfolio();
            toast.success('Portfolio refreshed successfully');
        } catch (error: any) {
            toast.error('Failed to refresh portfolio');
        } finally {
            setRefreshing(false);
        }
    };

    const handleRemoveHolding = async (holdingId: number, symbol: string) => {
        if (!window.confirm(`Remove ${symbol} from portfolio?`)) return;

        try {
            await portfolioService.removeHolding(holdingId);
            toast.success(`${symbol} removed from portfolio`);
            loadPortfolio();
        } catch (error: any) {
            toast.error('Failed to remove holding');
        }
    };

    const handleAddSuccess = () => {
        setShowAddModal(false);
        loadPortfolio();
        toast.success('Stock added to portfolio');
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    if (!summary) {
        return (
            <div className="text-center py-12">
                <p className="text-gray-500">Failed to load portfolio</p>
            </div>
        );
    }

    const { portfolio, holdings, sector_allocation } = summary;

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
                <div>
                    <h1 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-1">My Portfolio</h1>
                    <p className="text-gray-500 text-sm">
                        Last updated: {new Date(portfolio.last_updated).toLocaleString()}
                    </p>
                </div>
                <div className="flex gap-3">
                    <button
                        onClick={handleRefresh}
                        disabled={refreshing}
                        className="btn-secondary flex items-center gap-2"
                    >
                        <span className={refreshing ? 'animate-spin' : ''}>🔄</span>
                        {refreshing ? 'Refreshing...' : 'Refresh'}
                    </button>
                    <button
                        onClick={() => setShowAddModal(true)}
                        className="btn-primary flex items-center gap-2"
                    >
                        <span className="text-lg">+</span>
                        Add Stock
                    </button>
                </div>
            </div>

            {/* Portfolio Metrics */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
                <MetricCard
                    title="Total Invested"
                    value={`₹${portfolio.total_invested.toLocaleString('en-IN', { maximumFractionDigits: 2 })}`}
                    icon="💰"
                    gradient="from-blue-500 via-blue-600 to-blue-700"
                />
                <MetricCard
                    title="Current Value"
                    value={`₹${portfolio.current_value.toLocaleString('en-IN', { maximumFractionDigits: 2 })}`}
                    icon="📊"
                    gradient="from-purple-500 via-purple-600 to-purple-700"
                />
                <MetricCard
                    title="Total Return"
                    value={`₹${portfolio.total_return.toLocaleString('en-IN', { maximumFractionDigits: 2 })}`}
                    icon={portfolio.total_return >= 0 ? '📈' : '📉'}
                    valueColor={portfolio.total_return >= 0 ? 'text-white' : 'text-white'}
                    gradient={portfolio.total_return >= 0 ? 'from-success-500 via-success-600 to-success-700' : 'from-danger-500 via-danger-600 to-danger-700'}
                />
                <MetricCard
                    title="Return %"
                    value={`${portfolio.return_percentage >= 0 ? '+' : ''}${portfolio.return_percentage.toFixed(2)}%`}
                    icon={portfolio.return_percentage >= 0 ? '✨' : '⚠️'}
                    valueColor={portfolio.return_percentage >= 0 ? 'text-white' : 'text-white'}
                    gradient={portfolio.return_percentage >= 0 ? 'from-success-500 via-success-600 to-success-700' : 'from-danger-500 via-danger-600 to-danger-700'}
                />
            </div>

            {/* Holdings Table */}
            <div className="card overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-gray-100/50">
                    <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                        <span className="w-1 h-6 bg-gradient-to-b from-primary-600 to-primary-700 rounded-full"></span>
                        Holdings ({holdings.length})
                    </h2>
                </div>

                {holdings.length === 0 ? (
                    <div className="text-center py-16">
                        <div className="w-20 h-20 bg-gradient-to-br from-primary-100 to-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                            <span className="text-4xl">📊</span>
                        </div>
                        <p className="text-gray-500 mb-2 font-medium">Your portfolio is empty</p>
                        <p className="text-sm text-gray-400 mb-6">Start building your portfolio by adding your first stock</p>
                        <button
                            onClick={() => setShowAddModal(true)}
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
                                    <th className="px-6 py-4 text-right text-xs font-bold text-gray-700 uppercase tracking-wider">
                                        Quantity
                                    </th>
                                    <th className="px-6 py-4 text-right text-xs font-bold text-gray-700 uppercase tracking-wider">
                                        Avg. Buy Price
                                    </th>
                                    <th className="px-6 py-4 text-right text-xs font-bold text-gray-700 uppercase tracking-wider">
                                        Current Price
                                    </th>
                                    <th className="px-6 py-4 text-right text-xs font-bold text-gray-700 uppercase tracking-wider">
                                        Invested
                                    </th>
                                    <th className="px-6 py-4 text-right text-xs font-bold text-gray-700 uppercase tracking-wider">
                                        Current Value
                                    </th>
                                    <th className="px-6 py-4 text-right text-xs font-bold text-gray-700 uppercase tracking-wider">
                                        P&L
                                    </th>
                                    <th className="px-6 py-4 text-right text-xs font-bold text-gray-700 uppercase tracking-wider">
                                        Actions
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-100">
                                {holdings.map((holding) => (
                                    <HoldingRow
                                        key={holding.id}
                                        holding={holding}
                                        onRemove={handleRemoveHolding}
                                    />
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {/* Sector Allocation */}
            {holdings.length > 0 && (
                <div className="card">
                    <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
                        <span className="w-1 h-6 bg-gradient-to-b from-primary-600 to-primary-700 rounded-full"></span>
                        Sector Allocation
                    </h2>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {Object.entries(sector_allocation).map(([sector, value], index) => {
                            const percentage = (value / portfolio.current_value) * 100;
                            const colors = [
                                'from-blue-500 to-blue-600',
                                'from-purple-500 to-purple-600',
                                'from-success-500 to-success-600',
                                'from-orange-500 to-orange-600',
                                'from-pink-500 to-pink-600',
                                'from-indigo-500 to-indigo-600',
                            ];
                            const colorClass = colors[index % colors.length];
                            return (
                                <div key={sector} className={`p-5 bg-gradient-to-br ${colorClass} rounded-xl text-white shadow-md hover:shadow-lg transition-all duration-200 group hover:scale-105`}>
                                    <p className="text-sm text-white/90 mb-2 font-medium">{sector}</p>
                                    <p className="text-2xl font-bold mb-1">
                                        {percentage.toFixed(1)}%
                                    </p>
                                    <p className="text-xs text-white/80">
                                        ₹{value.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                                    </p>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}

            {/* Add Holding Modal */}
            {showAddModal && (
                <AddHoldingModal
                    onClose={() => setShowAddModal(false)}
                    onSuccess={handleAddSuccess}
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
    valueColor?: string;
    gradient?: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, icon, valueColor = 'text-white', gradient = 'from-gray-500 via-gray-600 to-gray-700' }) => (
    <div className={`metric-card group bg-gradient-to-br ${gradient} text-white`}>
        <div className="relative z-10 flex items-center justify-between">
            <div>
                <p className="text-white/90 text-sm font-medium mb-2">{title}</p>
                <p className={`text-2xl lg:text-3xl font-bold ${valueColor}`}>{value}</p>
            </div>
            <div className="w-12 h-12 lg:w-14 lg:h-14 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                <span className="text-2xl">{icon}</span>
            </div>
        </div>
    </div>
);

// Holding Row Component
interface HoldingRowProps {
    holding: PortfolioHolding;
    onRemove: (id: number, symbol: string) => void;
}

const HoldingRow: React.FC<HoldingRowProps> = ({ holding, onRemove }) => {
    const { stock, quantity, average_buy_price, total_invested, current_price, current_value, unrealized_pl, unrealized_pl_percentage } = holding;

    const plColor = unrealized_pl && unrealized_pl >= 0 ? 'text-success-600' : 'text-danger-600';
    const plBgColor = unrealized_pl && unrealized_pl >= 0 ? 'bg-success-50 border-success-200' : 'bg-danger-50 border-danger-200';
    const plIcon = unrealized_pl && unrealized_pl >= 0 ? '↑' : '↓';

    return (
        <tr className="table-row">
            <td className="px-6 py-4 whitespace-nowrap">
                <div>
                    <div className="text-sm font-semibold text-gray-900">{stock.symbol}</div>
                    <div className="text-xs text-gray-500">{stock.company_name}</div>
                </div>
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-right">
                <span className="text-sm font-medium text-gray-900">{quantity}</span>
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-right">
                <span className="text-sm font-medium text-gray-900">₹{average_buy_price.toFixed(2)}</span>
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-right">
                <span className="text-sm font-medium text-gray-900">
                    {current_price ? `₹${current_price.toFixed(2)}` : '-'}
                </span>
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-right">
                <span className="text-sm font-medium text-gray-900">
                    ₹{total_invested.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                </span>
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-right">
                <span className="text-sm font-medium text-gray-900">
                    {current_value ? `₹${current_value.toLocaleString('en-IN', { maximumFractionDigits: 2 })}` : '-'}
                </span>
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-right">
                {unrealized_pl !== null ? (
                    <div className={`inline-flex flex-col items-end px-3 py-1.5 rounded-lg border ${plBgColor}`}>
                        <div className={`text-sm font-bold ${plColor} flex items-center gap-1`}>
                            <span>{plIcon}</span>
                            <span>₹{Math.abs(unrealized_pl).toLocaleString('en-IN', { maximumFractionDigits: 2 })}</span>
                        </div>
                        <div className={`text-xs font-semibold ${plColor}`}>
                            ({unrealized_pl_percentage !== null ? (unrealized_pl_percentage >= 0 ? '+' : '') + unrealized_pl_percentage.toFixed(2) : '0.00'}%)
                        </div>
                    </div>
                ) : (
                    <span className="text-sm text-gray-400">-</span>
                )}
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                <button
                    onClick={() => onRemove(holding.id, stock.symbol)}
                    className="text-danger-600 hover:text-danger-700 font-medium hover:underline transition-colors"
                >
                    Remove
                </button>
            </td>
        </tr>
    );
};


