import { useEffect, useState } from 'react'
import { marketService, MarketMovers, MarketMover } from '../api/marketService'
import { toast } from 'react-hot-toast'
import { TrendingUp, TrendingDown, Activity, ArrowUp, ArrowDown, Sparkles } from 'lucide-react'

export const MarketMoversPage = () => {
    const [movers, setMovers] = useState<MarketMovers | null>(null)
    const [loading, setLoading] = useState(true)
    const [market, setMarket] = useState('india_nse')
    const [activeTab, setActiveTab] = useState<'gainers' | 'losers' | 'active'>('gainers')

    useEffect(() => {
        loadMovers()
    }, [market])

    const loadMovers = async () => {
        try {
            setLoading(true)
            const data = await marketService.getMarketMovers(market, 'all', 20)
            setMovers(data)
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to load market movers')
        } finally {
            setLoading(false)
        }
    }

    const getCurrentData = (): MarketMover[] => {
        if (!movers) return []
        switch (activeTab) {
            case 'gainers':
                return movers.gainers
            case 'losers':
                return movers.losers
            case 'active':
                return movers.most_active
            default:
                return []
        }
    }

    if (loading && !movers) {
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
                        <Activity className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                        <h1 className="text-3xl lg:text-4xl font-bold text-gray-900 dark:text-gray-100">
                            Market Movers
                        </h1>
                    </div>
                    <p className="text-gray-500 dark:text-gray-400 text-sm">
                        Top gainers, losers, and most active stocks
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

            {/* Tabs */}
            <div className="flex gap-3">
                <button
                    onClick={() => setActiveTab('gainers')}
                    className={`px-6 py-3 rounded-xl font-semibold transition-all flex items-center gap-2 ${
                        activeTab === 'gainers'
                            ? 'bg-gradient-to-r from-success-600 to-success-700 text-white shadow-lg'
                            : 'bg-white dark:bg-slate-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-slate-700 border border-gray-200 dark:border-slate-700'
                    }`}
                >
                    <ArrowUp className="w-4 h-4" />
                    Top Gainers ({movers?.gainers.length || 0})
                </button>
                <button
                    onClick={() => setActiveTab('losers')}
                    className={`px-6 py-3 rounded-xl font-semibold transition-all flex items-center gap-2 ${
                        activeTab === 'losers'
                            ? 'bg-gradient-to-r from-danger-600 to-danger-700 text-white shadow-lg'
                            : 'bg-white dark:bg-slate-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-slate-700 border border-gray-200 dark:border-slate-700'
                    }`}
                >
                    <ArrowDown className="w-4 h-4" />
                    Top Losers ({movers?.losers.length || 0})
                </button>
                <button
                    onClick={() => setActiveTab('active')}
                    className={`px-6 py-3 rounded-xl font-semibold transition-all flex items-center gap-2 ${
                        activeTab === 'active'
                            ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white shadow-lg'
                            : 'bg-white dark:bg-slate-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-slate-700 border border-gray-200 dark:border-slate-700'
                    }`}
                >
                    <Activity className="w-4 h-4" />
                    Most Active ({movers?.most_active.length || 0})
                </button>
            </div>

            {/* Movers Table */}
            {movers && (
                <>
                    <div className="card overflow-hidden">
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead className="bg-gray-50 dark:bg-slate-800">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                                            Rank
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                                            Symbol
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                                            Company
                                        </th>
                                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                                            Price
                                        </th>
                                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                                            Change
                                        </th>
                                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                                            Change %
                                        </th>
                                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                                            Volume
                                        </th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white dark:bg-slate-900 divide-y divide-gray-200 dark:divide-slate-700">
                                    {getCurrentData().map((stock, index) => (
                                        <tr
                                            key={stock.symbol}
                                            className="hover:bg-gray-50 dark:hover:bg-slate-800 transition-colors"
                                        >
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-100">
                                                #{index + 1}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900 dark:text-gray-100">
                                                {stock.symbol}
                                            </td>
                                            <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-400">
                                                {stock.company_name}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900 dark:text-gray-100 text-right">
                                                ₹{stock.current_price.toFixed(2)}
                                            </td>
                                            <td
                                                className={`px-6 py-4 whitespace-nowrap text-sm font-semibold text-right ${
                                                    stock.change >= 0
                                                        ? 'text-success-600 dark:text-success-400'
                                                        : 'text-danger-600 dark:text-danger-400'
                                                }`}
                                            >
                                                <div className="flex items-center justify-end gap-1">
                                                    {stock.change >= 0 ? (
                                                        <TrendingUp className="w-4 h-4" />
                                                    ) : (
                                                        <TrendingDown className="w-4 h-4" />
                                                    )}
                                                    {stock.change >= 0 ? '+' : ''}₹{Math.abs(stock.change).toFixed(2)}
                                                </div>
                                            </td>
                                            <td
                                                className={`px-6 py-4 whitespace-nowrap text-sm font-bold text-right ${
                                                    stock.change_percent >= 0
                                                        ? 'text-success-600 dark:text-success-400'
                                                        : 'text-danger-600 dark:text-danger-400'
                                                }`}
                                            >
                                                {stock.change_percent >= 0 ? '+' : ''}
                                                {stock.change_percent.toFixed(2)}%
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400 text-right">
                                                {stock.volume.toLocaleString()}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    {/* AI Insights */}
                    {movers.insights && (
                        <div className="card bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/30 dark:to-blue-900/30 border border-primary-100 dark:border-primary-800">
                            <div className="flex items-center gap-2 mb-4">
                                <Sparkles className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                                <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                                    AI Market Insights
                                </h3>
                            </div>
                            <p className="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-line">
                                {movers.insights}
                            </p>
                        </div>
                    )}
                </>
            )}
        </div>
    )
}

