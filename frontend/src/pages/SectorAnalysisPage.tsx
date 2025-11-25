import { useEffect, useState } from 'react'
import { marketService, SectorAnalysis } from '../api/marketService'
import { toast } from 'react-hot-toast'
import { BarChart3, TrendingUp, TrendingDown, Activity, Sparkles } from 'lucide-react'
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, Cell } from 'recharts'

export const SectorAnalysisPage = () => {
    const [analysis, setAnalysis] = useState<SectorAnalysis | null>(null)
    const [loading, setLoading] = useState(true)
    const [market, setMarket] = useState('india_nse')
    const [selectedSector, setSelectedSector] = useState<string>('')
    const [compareSectors, setCompareSectors] = useState(false)

    useEffect(() => {
        loadAnalysis()
    }, [market, selectedSector, compareSectors])

    const loadAnalysis = async () => {
        try {
            setLoading(true)
            const data = await marketService.getSectorAnalysis(
                market,
                selectedSector || undefined,
                compareSectors
            )
            setAnalysis(data)
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to load sector analysis')
        } finally {
            setLoading(false)
        }
    }

    const getChartData = () => {
        if (!analysis || !analysis.sectors) return []
        
        return Object.entries(analysis.sectors)
            .map(([sector, data]: [string, any]) => ({
                sector,
                performance: data.avg_change || 0
            }))
            .sort((a, b) => b.performance - a.performance)
    }

    const getColor = (value: number) => {
        if (value >= 0) return '#10b981' // success-500
        return '#ef4444' // danger-500
    }

    if (loading && !analysis) {
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
                        <BarChart3 className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                        <h1 className="text-3xl lg:text-4xl font-bold text-gray-900 dark:text-gray-100">
                            Sector Analysis
                        </h1>
                    </div>
                    <p className="text-gray-500 dark:text-gray-400 text-sm">
                        Comprehensive sector-wise performance analysis
                    </p>
                </div>
                <div className="flex gap-3">
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
                    <label className="flex items-center gap-2 cursor-pointer">
                        <input
                            type="checkbox"
                            checked={compareSectors}
                            onChange={(e) => setCompareSectors(e.target.checked)}
                            className="w-4 h-4"
                        />
                        <span className="text-sm text-gray-700 dark:text-gray-300">Compare Sectors</span>
                    </label>
                </div>
            </div>

            {/* Sector Selector */}
            {analysis && analysis.sectors && (
                <div className="card">
                    <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                        Select Sector (Optional)
                    </label>
                    <select
                        value={selectedSector}
                        onChange={(e) => setSelectedSector(e.target.value)}
                        className="input-field"
                    >
                        <option value="">All Sectors</option>
                        {Object.keys(analysis.sectors).map((sector) => (
                            <option key={sector} value={sector}>
                                {sector}
                            </option>
                        ))}
                    </select>
                </div>
            )}

            {/* Sector Comparison Chart */}
            {analysis && analysis.sectors && !selectedSector && (
                <div className="card">
                    <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                        <BarChart3 className="w-6 h-6" />
                        Sector Performance Comparison
                    </h2>
                    <ResponsiveContainer width="100%" height={400}>
                        <BarChart data={getChartData()}>
                            <XAxis dataKey="sector" angle={-45} textAnchor="end" height={100} />
                            <YAxis />
                            <Tooltip
                                formatter={(value: number) => [`${value.toFixed(2)}%`, 'Performance']}
                            />
                            <Legend />
                            <Bar dataKey="performance" name="Performance %">
                                {getChartData().map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={getColor(entry.performance)} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            )}

            {/* Sector Ranking */}
            {analysis && analysis.comparison && (
                <div className="card">
                    <h2 className="text-2xl font-bold mb-6">Sector Ranking</h2>
                    <div className="space-y-3">
                        {analysis.comparison.ranking.map((item, index) => (
                            <div
                                key={item.sector}
                                className="flex items-center justify-between p-4 rounded-lg border border-gray-200 dark:border-slate-700"
                            >
                                <div className="flex items-center gap-4">
                                    <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                                        index === 0
                                            ? 'bg-success-100 dark:bg-success-900/30 text-success-700 dark:text-success-300'
                                            : index === analysis.comparison!.ranking.length - 1
                                            ? 'bg-danger-100 dark:bg-danger-900/30 text-danger-700 dark:text-danger-300'
                                            : 'bg-gray-100 dark:bg-slate-800 text-gray-700 dark:text-gray-300'
                                    }`}>
                                        #{item.rank}
                                    </div>
                                    <div>
                                        <p className="font-semibold text-gray-900 dark:text-gray-100">
                                            {item.sector}
                                        </p>
                                        <p className="text-sm text-gray-600 dark:text-gray-400">
                                            Rank {item.rank}
                                        </p>
                                    </div>
                                </div>
                                <div className={`text-2xl font-bold ${
                                    item.performance >= 0
                                        ? 'text-success-600 dark:text-success-400'
                                        : 'text-danger-600 dark:text-danger-400'
                                }`}>
                                    {item.performance >= 0 ? '+' : ''}{item.performance.toFixed(2)}%
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Individual Sector Details */}
            {analysis && selectedSector && analysis.sector_data && (
                <div className="card">
                    <h2 className="text-2xl font-bold mb-6">{selectedSector} Sector Details</h2>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                            <p className="text-sm text-gray-600 dark:text-gray-400">Average Change</p>
                            <p className={`text-2xl font-bold ${
                                (analysis.sector_data.avg_change || 0) >= 0
                                    ? 'text-success-600 dark:text-success-400'
                                    : 'text-danger-600 dark:text-danger-400'
                            }`}>
                                {(analysis.sector_data.avg_change || 0) >= 0 ? '+' : ''}
                                {(analysis.sector_data.avg_change || 0).toFixed(2)}%
                            </p>
                        </div>
                        <div>
                            <p className="text-sm text-gray-600 dark:text-gray-400">Total Stocks</p>
                            <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                                {analysis.sector_data.total_stocks || 0}
                            </p>
                        </div>
                        <div>
                            <p className="text-sm text-gray-600 dark:text-gray-400">Top Gainers</p>
                            <p className="text-2xl font-bold text-success-600 dark:text-success-400">
                                {analysis.sector_data.top_gainers?.length || 0}
                            </p>
                        </div>
                        <div>
                            <p className="text-sm text-gray-600 dark:text-gray-400">Top Losers</p>
                            <p className="text-2xl font-bold text-danger-600 dark:text-danger-400">
                                {analysis.sector_data.top_losers?.length || 0}
                            </p>
                        </div>
                    </div>
                </div>
            )}

            {/* All Sectors List */}
            {analysis && analysis.sectors && !selectedSector && (
                <div className="card">
                    <h2 className="text-2xl font-bold mb-6">All Sectors</h2>
                    <div className="space-y-3">
                        {Object.entries(analysis.sectors)
                            .sort(([, a]: [string, any], [, b]: [string, any]) => 
                                (b.avg_change || 0) - (a.avg_change || 0)
                            )
                            .map(([sector, data]: [string, any]) => (
                                <div
                                    key={sector}
                                    className="flex items-center justify-between p-4 rounded-lg border border-gray-200 dark:border-slate-700 hover:shadow-md transition-shadow cursor-pointer"
                                    onClick={() => setSelectedSector(sector)}
                                >
                                    <div>
                                        <p className="font-semibold text-gray-900 dark:text-gray-100">
                                            {sector}
                                        </p>
                                        <p className="text-sm text-gray-600 dark:text-gray-400">
                                            Avg Change: {(data.avg_change || 0).toFixed(2)}%
                                        </p>
                                    </div>
                                    <div className={`text-xl font-bold ${
                                        (data.avg_change || 0) >= 0
                                            ? 'text-success-600 dark:text-success-400'
                                            : 'text-danger-600 dark:text-danger-400'
                                    }`}>
                                        {(data.avg_change || 0) >= 0 ? '+' : ''}
                                        {(data.avg_change || 0).toFixed(2)}%
                                    </div>
                                </div>
                            ))}
                    </div>
                </div>
            )}

            {/* AI Insights */}
            {analysis && analysis.insights && (
                <div className="card bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/30 dark:to-blue-900/30 border border-primary-100 dark:border-primary-800">
                    <div className="flex items-center gap-2 mb-4">
                        <Sparkles className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                        <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                            AI Sector Insights
                        </h3>
                    </div>
                    <p className="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-line">
                        {analysis.insights}
                    </p>
                </div>
            )}
        </div>
    )
}

