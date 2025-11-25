import { useEffect, useState } from 'react'
import { marketService } from '../api/marketService'
import { toast } from 'react-hot-toast'
import { Users, TrendingUp, Award, Sparkles, Plus, X } from 'lucide-react'

export const PeerComparisonPage = () => {
    const [comparison, setComparison] = useState<any>(null)
    const [loading, setLoading] = useState(false)
    const [symbols, setSymbols] = useState<string[]>(['RELIANCE', 'TCS'])
    const [newSymbol, setNewSymbol] = useState('')
    const [market, setMarket] = useState('india_nse')

    useEffect(() => {
        if (symbols.length >= 2) {
            loadComparison()
        }
    }, [symbols, market])

    const loadComparison = async () => {
        try {
            setLoading(true)
            const data = await marketService.compareStocks(symbols, market)
            setComparison(data)
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to load comparison')
        } finally {
            setLoading(false)
        }
    }

    const addSymbol = () => {
        if (newSymbol && !symbols.includes(newSymbol.toUpperCase()) && symbols.length < 10) {
            setSymbols([...symbols, newSymbol.toUpperCase()])
            setNewSymbol('')
        }
    }

    const removeSymbol = (symbol: string) => {
        if (symbols.length > 2) {
            setSymbols(symbols.filter(s => s !== symbol))
        }
    }

    if (loading && !comparison) {
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
                        <Users className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                        <h1 className="text-3xl lg:text-4xl font-bold text-gray-900 dark:text-gray-100">
                            Peer Comparison
                        </h1>
                    </div>
                    <p className="text-gray-500 dark:text-gray-400 text-sm">
                        Compare multiple stocks side-by-side
                    </p>
                </div>
            </div>

            {/* Symbol Selector */}
            <div className="card">
                <div className="flex flex-wrap gap-2 mb-4">
                    {symbols.map((symbol) => (
                        <div
                            key={symbol}
                            className="flex items-center gap-2 px-4 py-2 bg-primary-100 dark:bg-primary-900/30 rounded-lg"
                        >
                            <span className="font-semibold text-primary-700 dark:text-primary-300">{symbol}</span>
                            {symbols.length > 2 && (
                                <button
                                    onClick={() => removeSymbol(symbol)}
                                    className="text-primary-600 dark:text-primary-400 hover:text-primary-800 dark:hover:text-primary-200"
                                >
                                    <X className="w-4 h-4" />
                                </button>
                            )}
                        </div>
                    ))}
                </div>
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={newSymbol}
                        onChange={(e) => setNewSymbol(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && addSymbol()}
                        placeholder="Add symbol (max 10)"
                        className="input-field flex-1"
                        disabled={symbols.length >= 10}
                    />
                    <button
                        onClick={addSymbol}
                        disabled={symbols.length >= 10 || !newSymbol}
                        className="btn-primary"
                    >
                        <Plus className="w-4 h-4" />
                    </button>
                </div>
                <div className="mt-4">
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
            </div>

            {comparison && !comparison.error && (
                <>
                    {/* Best Performers */}
                    {comparison.best_performers && (
                        <div className="card">
                            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                                <Award className="w-6 h-6" />
                                Best Performers
                            </h2>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div className="p-4 bg-success-50 dark:bg-success-900/20 rounded-lg border border-success-200 dark:border-success-800">
                                    <p className="text-sm text-success-700 dark:text-success-300 mb-1">Price Performance</p>
                                    <p className="text-2xl font-bold text-success-900 dark:text-success-200">
                                        {comparison.best_performers.price_performance}
                                    </p>
                                </div>
                                <div className="p-4 bg-primary-50 dark:bg-primary-900/20 rounded-lg border border-primary-200 dark:border-primary-800">
                                    <p className="text-sm text-primary-700 dark:text-primary-300 mb-1">Best ROE</p>
                                    <p className="text-2xl font-bold text-primary-900 dark:text-primary-200">
                                        {comparison.best_performers.roe}
                                    </p>
                                </div>
                                <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
                                    <p className="text-sm text-purple-700 dark:text-purple-300 mb-1">Revenue Growth</p>
                                    <p className="text-2xl font-bold text-purple-900 dark:text-purple-200">
                                        {comparison.best_performers.revenue_growth}
                                    </p>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Comparison Matrix */}
                    {comparison.comparison && (
                        <div className="card overflow-hidden">
                            <h2 className="text-2xl font-bold mb-6">Comparison Matrix</h2>
                            <div className="overflow-x-auto">
                                <table className="w-full">
                                    <thead className="bg-gray-50 dark:bg-slate-800">
                                        <tr>
                                            <th className="px-4 py-3 text-left">Metric</th>
                                            {comparison.comparison.symbols?.map((symbol: string) => (
                                                <th key={symbol} className="px-4 py-3 text-right font-semibold">
                                                    {symbol}
                                                </th>
                                            ))}
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-gray-200 dark:divide-slate-700">
                                        {Object.entries(comparison.comparison.metrics || {}).map(([metric, values]: [string, any]) => (
                                            <tr key={metric} className="hover:bg-gray-50 dark:hover:bg-slate-800">
                                                <td className="px-4 py-3 font-medium text-gray-900 dark:text-gray-100 capitalize">
                                                    {metric.replace(/_/g, ' ')}
                                                </td>
                                                {comparison.comparison.symbols?.map((symbol: string) => (
                                                    <td key={symbol} className="px-4 py-3 text-right text-gray-700 dark:text-gray-300">
                                                        {values[symbol] !== null && values[symbol] !== undefined ? (
                                                            typeof values[symbol] === 'number' 
                                                                ? values[symbol].toFixed(2) 
                                                                : values[symbol]
                                                        ) : 'N/A'}
                                                    </td>
                                                ))}
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}

                    {/* AI Insights */}
                    {comparison.insights && (
                        <div className="card bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/30 dark:to-blue-900/30 border border-primary-100 dark:border-primary-800">
                            <div className="flex items-center gap-2 mb-4">
                                <Sparkles className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                                <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                                    AI Comparison Insights
                                </h3>
                            </div>
                            <p className="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-line">
                                {comparison.insights}
                            </p>
                        </div>
                    )}
                </>
            )}

            {symbols.length < 2 && (
                <div className="card text-center py-16">
                    <Users className="w-16 h-16 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
                    <p className="text-gray-500 dark:text-gray-400 font-medium">
                        Add at least 2 stocks to compare
                    </p>
                </div>
            )}
        </div>
    )
}

