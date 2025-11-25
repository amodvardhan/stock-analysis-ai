import { useEffect, useState } from 'react'
import { marketService, MarketOverview } from '../api/marketService'
import { toast } from 'react-hot-toast'
import { TrendingUp, TrendingDown, BarChart3, Activity, Globe, Sparkles } from 'lucide-react'

export const MarketOverviewPage = () => {
    const [overview, setOverview] = useState<MarketOverview | null>(null)
    const [loading, setLoading] = useState(true)
    const [market, setMarket] = useState('india_nse')

    useEffect(() => {
        loadOverview()
    }, [market])

    const loadOverview = async () => {
        try {
            setLoading(true)
            const data = await marketService.getMarketOverview(market, true, true)
            setOverview(data)
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to load market overview')
        } finally {
            setLoading(false)
        }
    }

    if (loading && !overview) {
        return (
            <div className="flex justify-center items-center h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        )
    }

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <div className="flex items-center gap-2 mb-2">
                        <Globe className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                        <h1 className="text-3xl lg:text-4xl font-bold text-gray-900 dark:text-gray-100">
                            Market Overview
                        </h1>
                    </div>
                    <p className="text-gray-500 dark:text-gray-400 text-sm">
                        Comprehensive market analysis and insights
                    </p>
                </div>
                <select
                    value={market}
                    onChange={(e) => setMarket(e.target.value)}
                    className="input-field"
                >
                    <option value="india_nse">India NSE</option>
                    <option value="india_bse">India BSE</option>
                    <option value="us_nyse">US NYSE</option>
                    <option value="us_nasdaq">US NASDAQ</option>
                </select>
            </div>

            {overview && (
                <>
                    {/* Market Statistics */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="card">
                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Total Stocks</p>
                            <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                                {overview.statistics.total_stocks.toLocaleString()}
                            </p>
                        </div>
                        <div className="card">
                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Advancing</p>
                            <p className="text-2xl font-bold text-success-600 dark:text-success-400">
                                {overview.statistics.advancing}
                            </p>
                        </div>
                        <div className="card">
                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Declining</p>
                            <p className="text-2xl font-bold text-danger-600 dark:text-danger-400">
                                {overview.statistics.declining}
                            </p>
                        </div>
                        <div className="card">
                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Unchanged</p>
                            <p className="text-2xl font-bold text-gray-600 dark:text-gray-400">
                                {overview.statistics.unchanged}
                            </p>
                        </div>
                    </div>

                    {/* Market Indices */}
                    {Object.keys(overview.indices).length > 0 && (
                        <div className="card">
                            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                                <BarChart3 className="w-6 h-6" />
                                Market Indices
                            </h2>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                                {Object.entries(overview.indices).map(([index, data]) => (
                                    <div
                                        key={index}
                                        className={`p-4 rounded-lg border ${
                                            data.change_percent >= 0
                                                ? 'bg-success-50 dark:bg-success-900/20 border-success-200 dark:border-success-800'
                                                : 'bg-danger-50 dark:bg-danger-900/20 border-danger-200 dark:border-danger-800'
                                        }`}
                                    >
                                        <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                                            {index}
                                        </p>
                                        <p className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-1">
                                            {data.value.toFixed(2)}
                                        </p>
                                        <div className="flex items-center gap-1">
                                            {data.change_percent >= 0 ? (
                                                <TrendingUp className="w-4 h-4 text-success-600" />
                                            ) : (
                                                <TrendingDown className="w-4 h-4 text-danger-600" />
                                            )}
                                            <span
                                                className={`font-semibold ${
                                                    data.change_percent >= 0
                                                        ? 'text-success-600 dark:text-success-400'
                                                        : 'text-danger-600 dark:text-danger-400'
                                                }`}
                                            >
                                                {data.change_percent >= 0 ? '+' : ''}
                                                {data.change_percent.toFixed(2)}%
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Sector Performance */}
                    {Object.keys(overview.sectors).length > 0 && (
                        <div className="card">
                            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                                <Activity className="w-6 h-6" />
                                Sector Performance
                            </h2>
                            <div className="space-y-3">
                                {Object.entries(overview.sectors)
                                    .sort(([, a], [, b]) => (b.avg_change || 0) - (a.avg_change || 0))
                                    .map(([sector, data]) => (
                                        <div
                                            key={sector}
                                            className="p-4 rounded-lg border border-gray-200 dark:border-slate-700 hover:shadow-md transition-shadow"
                                        >
                                            <div className="flex items-center justify-between">
                                                <div>
                                                    <p className="font-semibold text-gray-900 dark:text-gray-100">
                                                        {sector}
                                                    </p>
                                                    <p className="text-sm text-gray-600 dark:text-gray-400">
                                                        Avg Change: {data.avg_change?.toFixed(2) || 0}%
                                                    </p>
                                                </div>
                                                <div
                                                    className={`text-2xl font-bold ${
                                                        (data.avg_change || 0) >= 0
                                                            ? 'text-success-600 dark:text-success-400'
                                                            : 'text-danger-600 dark:text-danger-400'
                                                    }`}
                                                >
                                                    {(data.avg_change || 0) >= 0 ? '+' : ''}
                                                    {(data.avg_change || 0).toFixed(2)}%
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                            </div>
                        </div>
                    )}

                    {/* AI Insights */}
                    {overview.ai_insights && (
                        <div className="card bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/30 dark:to-blue-900/30 border border-primary-100 dark:border-primary-800">
                            <div className="flex items-center gap-2 mb-4">
                                <Sparkles className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                                <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                                    AI Market Insights
                                </h3>
                            </div>
                            <p className="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-line">
                                {overview.ai_insights}
                            </p>
                            <div className="mt-4 pt-4 border-t border-primary-200 dark:border-primary-700">
                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                    Overall Sentiment:{' '}
                                    <span
                                        className={`font-semibold capitalize ${
                                            overview.overall_sentiment === 'bullish'
                                                ? 'text-success-600 dark:text-success-400'
                                                : overview.overall_sentiment === 'bearish'
                                                ? 'text-danger-600 dark:text-danger-400'
                                                : 'text-gray-600 dark:text-gray-400'
                                        }`}
                                    >
                                        {overview.overall_sentiment}
                                    </span>
                                </p>
                            </div>
                        </div>
                    )}
                </>
            )}
        </div>
    )
}

