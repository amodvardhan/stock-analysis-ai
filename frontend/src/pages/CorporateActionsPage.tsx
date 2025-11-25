import { useEffect, useState } from 'react'
import { marketService } from '../api/marketService'
import { toast } from 'react-hot-toast'
import { FileText, DollarSign, Split, Calendar } from 'lucide-react'

export const CorporateActionsPage = () => {
    const [actions, setActions] = useState<any>(null)
    const [loading, setLoading] = useState(true)
    const [symbol, setSymbol] = useState('RELIANCE')
    const [market, setMarket] = useState('india_nse')
    const [actionType, setActionType] = useState('all')

    useEffect(() => {
        if (symbol) {
            loadActions()
        }
    }, [symbol, market, actionType])

    const loadActions = async () => {
        try {
            setLoading(true)
            const data = await marketService.getCorporateActions(symbol, market, actionType)
            setActions(data)
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to load corporate actions')
        } finally {
            setLoading(false)
        }
    }

    if (loading && !actions) {
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
                        <FileText className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                        <h1 className="text-3xl lg:text-4xl font-bold text-gray-900 dark:text-gray-100">
                            Corporate Actions
                        </h1>
                    </div>
                    <p className="text-gray-500 dark:text-gray-400 text-sm">
                        Track dividends, splits, and other corporate actions
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
                            Action Type
                        </label>
                        <select
                            value={actionType}
                            onChange={(e) => setActionType(e.target.value)}
                            className="input-field"
                        >
                            <option value="all">All</option>
                            <option value="dividend">Dividends</option>
                            <option value="split">Splits</option>
                        </select>
                    </div>
                </div>
            </div>

            {actions && !actions.error && (
                <>
                    {/* Upcoming Dividend */}
                    {actions.upcoming_dividend && (
                        <div className="card bg-gradient-to-r from-success-50 to-emerald-50 dark:from-success-900/30 dark:to-emerald-900/30 border border-success-100 dark:border-success-800">
                            <div className="flex items-center gap-2 mb-4">
                                <Calendar className="w-5 h-5 text-success-600 dark:text-success-400" />
                                <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">
                                    Upcoming Dividend
                                </h2>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <p className="text-sm text-gray-600 dark:text-gray-400">Ex-Dividend Date</p>
                                    <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                                        {actions.upcoming_dividend.ex_date}
                                    </p>
                                </div>
                                <div>
                                    <p className="text-sm text-gray-600 dark:text-gray-400">Amount</p>
                                    <p className="text-2xl font-bold text-success-600 dark:text-success-400">
                                        ₹{actions.upcoming_dividend.amount?.toFixed(2) || 'N/A'}
                                    </p>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Dividends */}
                    {actions.dividends && actions.dividends.length > 0 && (
                        <div className="card">
                            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                                <DollarSign className="w-6 h-6 text-success-600 dark:text-success-400" />
                                Dividend History
                            </h2>
                            <div className="overflow-x-auto">
                                <table className="w-full">
                                    <thead className="bg-gray-50 dark:bg-slate-800">
                                        <tr>
                                            <th className="px-4 py-3 text-left">Date</th>
                                            <th className="px-4 py-3 text-right">Amount</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-gray-200 dark:divide-slate-700">
                                        {actions.dividends.map((dividend: any, idx: number) => (
                                            <tr key={idx} className="hover:bg-gray-50 dark:hover:bg-slate-800">
                                                <td className="px-4 py-3">{dividend.date}</td>
                                                <td className="px-4 py-3 text-right font-semibold text-success-600 dark:text-success-400">
                                                    ₹{dividend.amount.toFixed(2)}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}

                    {/* Splits */}
                    {actions.splits && actions.splits.length > 0 && (
                        <div className="card">
                            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                                <Split className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                                Stock Split History
                            </h2>
                            <div className="overflow-x-auto">
                                <table className="w-full">
                                    <thead className="bg-gray-50 dark:bg-slate-800">
                                        <tr>
                                            <th className="px-4 py-3 text-left">Date</th>
                                            <th className="px-4 py-3 text-right">Ratio</th>
                                            <th className="px-4 py-3 text-left">Description</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-gray-200 dark:divide-slate-700">
                                        {actions.splits.map((split: any, idx: number) => (
                                            <tr key={idx} className="hover:bg-gray-50 dark:hover:bg-slate-800">
                                                <td className="px-4 py-3">{split.date}</td>
                                                <td className="px-4 py-3 text-right font-semibold">
                                                    {split.ratio.toFixed(2)}:1
                                                </td>
                                                <td className="px-4 py-3">{split.description}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}

                    {(!actions.dividends || actions.dividends.length === 0) && 
                     (!actions.splits || actions.splits.length === 0) && (
                        <div className="card text-center py-16">
                            <FileText className="w-16 h-16 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
                            <p className="text-gray-500 dark:text-gray-400 font-medium">
                                No corporate actions found for this stock
                            </p>
                        </div>
                    )}
                </>
            )}
        </div>
    )
}

