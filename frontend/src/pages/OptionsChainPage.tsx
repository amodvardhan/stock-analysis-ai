import { useEffect, useState } from 'react'
import { marketService } from '../api/marketService'
import { toast } from 'react-hot-toast'
import { TrendingUp, TrendingDown, Target, Sparkles, Calendar } from 'lucide-react'

export const OptionsChainPage = () => {
    const [optionsData, setOptionsData] = useState<any>(null)
    const [loading, setLoading] = useState(true)
    const [symbol, setSymbol] = useState('RELIANCE')
    const [market, setMarket] = useState('india_nse')
    const [expirationDate, setExpirationDate] = useState<string>('')

    useEffect(() => {
        if (symbol) {
            loadOptions()
        }
    }, [symbol, market, expirationDate])

    const loadOptions = async () => {
        try {
            setLoading(true)
            const data = await marketService.getOptionsChain(symbol, market, expirationDate || undefined)
            setOptionsData(data)
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to load options chain')
        } finally {
            setLoading(false)
        }
    }

    if (loading && !optionsData) {
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
                        <Target className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                        <h1 className="text-3xl lg:text-4xl font-bold text-gray-900 dark:text-gray-100">
                            Options Chain Analysis
                        </h1>
                    </div>
                    <p className="text-gray-500 dark:text-gray-400 text-sm">
                        Comprehensive options chain data with AI insights
                    </p>
                </div>
            </div>

            {/* Filters */}
            <div className="card">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                            Stock Symbol
                        </label>
                        <input
                            type="text"
                            value={symbol}
                            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                            placeholder="e.g., RELIANCE"
                            className="input-field"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                            Market
                        </label>
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
                    <div>
                        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                            Expiration Date (Optional)
                        </label>
                        <select
                            value={expirationDate}
                            onChange={(e) => setExpirationDate(e.target.value)}
                            className="input-field"
                        >
                            <option value="">Latest</option>
                            {optionsData?.available_expirations?.map((exp: string) => (
                                <option key={exp} value={exp}>{exp}</option>
                            ))}
                        </select>
                    </div>
                </div>
            </div>

            {optionsData && !optionsData.error && (
                <>
                    {/* Current Price & Metrics */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="card">
                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Current Price</p>
                            <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                                ₹{optionsData.current_price?.toFixed(2) || 'N/A'}
                            </p>
                        </div>
                        <div className="card">
                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Put-Call Ratio</p>
                            <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                                {optionsData.metrics?.put_call_ratio || 'N/A'}
                            </p>
                        </div>
                        <div className="card">
                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Total Call OI</p>
                            <p className="text-2xl font-bold text-primary-600 dark:text-primary-400">
                                {optionsData.metrics?.total_call_oi?.toLocaleString() || 'N/A'}
                            </p>
                        </div>
                        <div className="card">
                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Total Put OI</p>
                            <p className="text-2xl font-bold text-danger-600 dark:text-danger-400">
                                {optionsData.metrics?.total_put_oi?.toLocaleString() || 'N/A'}
                            </p>
                        </div>
                    </div>

                    {/* Options Chain Table */}
                    <div className="card overflow-hidden">
                        <h2 className="text-2xl font-bold mb-6">Options Chain</h2>
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            {/* Calls */}
                            <div>
                                <h3 className="text-lg font-semibold text-success-600 dark:text-success-400 mb-4">
                                    CALLS
                                </h3>
                                <div className="overflow-x-auto">
                                    <table className="w-full text-sm">
                                        <thead className="bg-gray-50 dark:bg-slate-800">
                                            <tr>
                                                <th className="px-3 py-2 text-left">Strike</th>
                                                <th className="px-3 py-2 text-right">Last</th>
                                                <th className="px-3 py-2 text-right">OI</th>
                                                <th className="px-3 py-2 text-right">IV</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-gray-200 dark:divide-slate-700">
                                            {optionsData.calls?.slice(0, 10).map((call: any, idx: number) => (
                                                <tr key={idx} className={call.in_the_money ? 'bg-success-50 dark:bg-success-900/20' : ''}>
                                                    <td className="px-3 py-2 font-semibold">{call.strike}</td>
                                                    <td className="px-3 py-2 text-right">{call.last_price.toFixed(2)}</td>
                                                    <td className="px-3 py-2 text-right">{call.open_interest.toLocaleString()}</td>
                                                    <td className="px-3 py-2 text-right">{(call.implied_volatility * 100).toFixed(1)}%</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>

                            {/* Puts */}
                            <div>
                                <h3 className="text-lg font-semibold text-danger-600 dark:text-danger-400 mb-4">
                                    PUTS
                                </h3>
                                <div className="overflow-x-auto">
                                    <table className="w-full text-sm">
                                        <thead className="bg-gray-50 dark:bg-slate-800">
                                            <tr>
                                                <th className="px-3 py-2 text-left">Strike</th>
                                                <th className="px-3 py-2 text-right">Last</th>
                                                <th className="px-3 py-2 text-right">OI</th>
                                                <th className="px-3 py-2 text-right">IV</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-gray-200 dark:divide-slate-700">
                                            {optionsData.puts?.slice(0, 10).map((put: any, idx: number) => (
                                                <tr key={idx} className={put.in_the_money ? 'bg-danger-50 dark:bg-danger-900/20' : ''}>
                                                    <td className="px-3 py-2 font-semibold">{put.strike}</td>
                                                    <td className="px-3 py-2 text-right">{put.last_price.toFixed(2)}</td>
                                                    <td className="px-3 py-2 text-right">{put.open_interest.toLocaleString()}</td>
                                                    <td className="px-3 py-2 text-right">{(put.implied_volatility * 100).toFixed(1)}%</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Strategies */}
                    {optionsData.strategies && optionsData.strategies.length > 0 && (
                        <div className="card">
                            <h2 className="text-2xl font-bold mb-6">Recommended Strategies</h2>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {optionsData.strategies.map((strategy: any, idx: number) => (
                                    <div key={idx} className="p-4 border border-gray-200 dark:border-slate-700 rounded-lg">
                                        <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">
                                            {strategy.strategy}
                                        </h3>
                                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                                            {strategy.description}
                                        </p>
                                        <div className="flex gap-4 text-sm">
                                            <div>
                                                <span className="text-gray-600 dark:text-gray-400">Max Profit: </span>
                                                <span className="font-semibold text-success-600">{strategy.potential_profit}</span>
                                            </div>
                                            <div>
                                                <span className="text-gray-600 dark:text-gray-400">Max Loss: </span>
                                                <span className="font-semibold text-danger-600">{strategy.max_loss}</span>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* AI Insights */}
                    {optionsData.insights && (
                        <div className="card bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/30 dark:to-blue-900/30 border border-primary-100 dark:border-primary-800">
                            <div className="flex items-center gap-2 mb-4">
                                <Sparkles className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                                <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                                    AI Options Insights
                                </h3>
                            </div>
                            <p className="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-line">
                                {optionsData.insights}
                            </p>
                        </div>
                    )}
                </>
            )}

            {optionsData?.error && (
                <div className="card text-center py-16">
                    <Target className="w-16 h-16 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
                    <p className="text-gray-500 dark:text-gray-400 font-medium">{optionsData.error}</p>
                </div>
            )}
        </div>
    )
}

