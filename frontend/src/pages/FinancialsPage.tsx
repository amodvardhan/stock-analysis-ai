import { useEffect, useState } from 'react'
import { marketService } from '../api/marketService'
import { toast } from 'react-hot-toast'
import { FileText, TrendingUp, TrendingDown, Award, Sparkles } from 'lucide-react'

export const FinancialsPage = () => {
    const [financials, setFinancials] = useState<any>(null)
    const [loading, setLoading] = useState(true)
    const [symbol, setSymbol] = useState('RELIANCE')
    const [market, setMarket] = useState('india_nse')

    useEffect(() => {
        if (symbol) {
            loadFinancials()
        }
    }, [symbol, market])

    const loadFinancials = async () => {
        try {
            setLoading(true)
            const data = await marketService.getFinancialAnalysis(symbol, market)
            setFinancials(data)
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to load financials')
        } finally {
            setLoading(false)
        }
    }

    const getGradeColor = (grade: string) => {
        switch (grade) {
            case 'A': return 'text-success-600 dark:text-success-400'
            case 'B': return 'text-primary-600 dark:text-primary-400'
            case 'C': return 'text-warning-600 dark:text-warning-400'
            case 'D': return 'text-orange-600 dark:text-orange-400'
            case 'F': return 'text-danger-600 dark:text-danger-400'
            default: return 'text-gray-600 dark:text-gray-400'
        }
    }

    if (loading && !financials) {
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
                            Financial Analysis
                        </h1>
                    </div>
                    <p className="text-gray-500 dark:text-gray-400 text-sm">
                        Comprehensive financial statements and health analysis
                    </p>
                </div>
            </div>

            {/* Filters */}
            <div className="card">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
                </div>
            </div>

            {financials && !financials.error && (
                <>
                    {/* Financial Health Score */}
                    {financials.financial_health && (
                        <div className="card bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/30 dark:to-blue-900/30 border border-primary-100 dark:border-primary-800">
                            <div className="flex items-center justify-between">
                                <div>
                                    <div className="flex items-center gap-2 mb-2">
                                        <Award className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                                        <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">
                                            Financial Health Score
                                        </h2>
                                    </div>
                                    <div className="flex items-baseline gap-2">
                                        <span className={`text-5xl font-bold ${getGradeColor(financials.financial_health.grade)}`}>
                                            {financials.financial_health.score}/100
                                        </span>
                                        <span className={`text-3xl font-bold ${getGradeColor(financials.financial_health.grade)}`}>
                                            ({financials.financial_health.grade})
                                        </span>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Strengths</p>
                                    <ul className="text-sm text-success-600 dark:text-success-400">
                                        {financials.financial_health.strengths?.map((s: string, idx: number) => (
                                            <li key={idx}>• {s}</li>
                                        ))}
                                    </ul>
                                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2 mt-4">Weaknesses</p>
                                    <ul className="text-sm text-danger-600 dark:text-danger-400">
                                        {financials.financial_health.weaknesses?.map((w: string, idx: number) => (
                                            <li key={idx}>• {w}</li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Key Ratios */}
                    {financials.key_ratios && (
                        <div className="card">
                            <h2 className="text-2xl font-bold mb-6">Key Financial Ratios</h2>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                {Object.entries(financials.key_ratios).map(([key, value]: [string, any]) => (
                                    <div key={key} className="p-4 border border-gray-200 dark:border-slate-700 rounded-lg">
                                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-1 capitalize">
                                            {key.replace(/_/g, ' ')}
                                        </p>
                                        <p className="text-xl font-bold text-gray-900 dark:text-gray-100">
                                            {value !== null && value !== undefined ? (
                                                typeof value === 'number' ? value.toFixed(2) : value
                                            ) : 'N/A'}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* AI Insights */}
                    {financials.insights && (
                        <div className="card bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/30 dark:to-blue-900/30 border border-primary-100 dark:border-primary-800">
                            <div className="flex items-center gap-2 mb-4">
                                <Sparkles className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                                <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                                    AI Financial Insights
                                </h3>
                            </div>
                            <p className="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-line">
                                {financials.insights}
                            </p>
                        </div>
                    )}
                </>
            )}

            {financials?.error && (
                <div className="card text-center py-16">
                    <FileText className="w-16 h-16 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
                    <p className="text-gray-500 dark:text-gray-400 font-medium">{financials.error}</p>
                </div>
            )}
        </div>
    )
}

