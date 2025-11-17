/**
 * Main Dashboard - Shows portfolio summary, watchlist, and recent analyses
 */
import React, { useEffect, useState } from 'react';
import { TrendingUp, Eye, DollarSign, AlertCircle } from 'lucide-react';
import { portfolioAPI, watchlistAPI } from '../lib/api';
import { PortfolioItem, WatchlistItem } from '../types';
import toast from 'react-hot-toast';

export const Dashboard: React.FC = () => {
    const [portfolioSummary, setPortfolioSummary] = useState<any>(null);
    const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadDashboardData();
    }, []);

    const loadDashboardData = async () => {
        try {
            const [summaryRes, watchlistRes] = await Promise.all([
                portfolioAPI.getSummary(),
                watchlistAPI.getAll(),
            ]);

            setPortfolioSummary(summaryRes.data);
            setWatchlist(watchlistRes.data);
        } catch (error) {
            console.error('Failed to load dashboard:', error);
            toast.error('Failed to load dashboard data');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto p-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>

            {/* Portfolio Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <div className="bg-white rounded-lg shadow-md p-6">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-gray-600 text-sm">Total Holdings</span>
                        <DollarSign className="w-5 h-5 text-blue-600" />
                    </div>
                    <div className="text-2xl font-bold">{portfolioSummary?.total_holdings || 0}</div>
                </div>

                <div className="bg-white rounded-lg shadow-md p-6">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-gray-600 text-sm">Total Invested</span>
                        <DollarSign className="w-5 h-5 text-gray-600" />
                    </div>
                    <div className="text-2xl font-bold">
                        ₹{portfolioSummary?.total_invested?.toLocaleString() || 0}
                    </div>
                </div>

                <div className="bg-white rounded-lg shadow-md p-6">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-gray-600 text-sm">Current Value</span>
                        <TrendingUp className="w-5 h-5 text-green-600" />
                    </div>
                    <div className="text-2xl font-bold">
                        ₹{portfolioSummary?.current_value?.toLocaleString() || 0}
                    </div>
                </div>

                <div className="bg-white rounded-lg shadow-md p-6">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-gray-600 text-sm">Total P&L</span>
                        <AlertCircle className={`w-5 h-5 ${portfolioSummary?.total_profit_loss >= 0 ? 'text-green-600' : 'text-red-600'}`} />
                    </div>
                    <div className={`text-2xl font-bold ${portfolioSummary?.total_profit_loss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {portfolioSummary?.total_profit_loss >= 0 ? '+' : ''}
                        ₹{portfolioSummary?.total_profit_loss?.toLocaleString() || 0}
                    </div>
                    <div className="text-sm text-gray-600">
                        ({portfolioSummary?.total_profit_loss_percent?.toFixed(2) || 0}%)
                    </div>
                </div>
            </div>

            {/* Watchlist */}
            <div className="bg-white rounded-lg shadow-md p-6 mb-8">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-bold flex items-center gap-2">
                        <Eye className="w-5 h-5" />
                        Watchlist
                    </h2>
                    <span className="text-sm text-gray-600">{watchlist.length} stocks</span>
                </div>

                {watchlist.length === 0 ? (
                    <p className="text-gray-500 text-center py-8">
                        No stocks in watchlist. Add stocks to monitor them.
                    </p>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead>
                                <tr>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Symbol</th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Company</th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Current Price</th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Alert At</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-200">
                                {watchlist.map((item) => (
                                    <tr key={item.id} className="hover:bg-gray-50">
                                        <td className="px-4 py-3 font-medium">{item.symbol}</td>
                                        <td className="px-4 py-3 text-sm text-gray-600">{item.company_name}</td>
                                        <td className="px-4 py-3">₹{item.current_price?.toFixed(2) || 'N/A'}</td>
                                        <td className="px-4 py-3 text-sm">±{item.alert_threshold_percent}%</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {/* Best/Worst Performers */}
            {portfolioSummary?.best_performer && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                        <h3 className="text-lg font-bold text-green-800 mb-2">Best Performer</h3>
                        <div className="text-2xl font-bold text-green-600">
                            {portfolioSummary.best_performer.symbol}
                        </div>
                        <div className="text-sm text-green-700">
                            +{portfolioSummary.best_performer.profit_loss_percent?.toFixed(2)}%
                        </div>
                    </div>

                    {portfolioSummary?.worst_performer && (
                        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                            <h3 className="text-lg font-bold text-red-800 mb-2">Worst Performer</h3>
                            <div className="text-2xl font-bold text-red-600">
                                {portfolioSummary.worst_performer.symbol}
                            </div>
                            <div className="text-sm text-red-700">
                                {portfolioSummary.worst_performer.profit_loss_percent?.toFixed(2)}%
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};
