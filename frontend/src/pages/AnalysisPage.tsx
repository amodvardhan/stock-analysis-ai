import { useState, useMemo, useEffect } from 'react'
import { StockAnalysisForm } from '@/components/analysis/StockAnalysisForm'
import { AnalysisResult } from '@/components/analysis/AnalysisResult'
import type { StockAnalysis } from '@/types'
import { Sparkles, BarChart3, FileText, Newspaper, TrendingUp } from 'lucide-react'
import { marketService } from '@/api/marketService'
import { toast } from 'react-hot-toast'

export const AnalysisPage = () => {
    const [analysis, setAnalysis] = useState<StockAnalysis | null>(null)
    const [activeTab, setActiveTab] = useState<'overview' | 'technical' | 'fundamental' | 'financials' | 'news'>('overview')
    const [financials, setFinancials] = useState<any>(null)
    const [news, setNews] = useState<any>(null)
    const [loadingFinancials, setLoadingFinancials] = useState(false)
    const [loadingNews, setLoadingNews] = useState(false)

    // Load additional data when analysis is complete
    useEffect(() => {
        if (analysis?.symbol) {
            loadAdditionalData(analysis.symbol, analysis.market || 'india_nse')
        }
    }, [analysis?.symbol])

    const loadAdditionalData = async (symbol: string, market: string) => {
        // Load financials
        if (activeTab === 'financials' && !financials) {
            setLoadingFinancials(true)
            try {
                const data = await marketService.getFinancialAnalysis(symbol, market)
                setFinancials(data)
            } catch (error: any) {
                toast.error('Failed to load financials')
            } finally {
                setLoadingFinancials(false)
            }
        }

        // Load news
        if (activeTab === 'news' && !news) {
            setLoadingNews(true)
            try {
                const data = await marketService.getNews(symbol, market, 10, 7)
                setNews(data)
            } catch (error: any) {
                toast.error('Failed to load news')
            } finally {
                setLoadingNews(false)
            }
        }
    }

    useEffect(() => {
        if (analysis?.symbol && (activeTab === 'financials' || activeTab === 'news')) {
            loadAdditionalData(analysis.symbol, analysis.market || 'india_nse')
        }
    }, [activeTab, analysis?.symbol, analysis?.market])

    // Data transformation logic - prepare data for presentation component
    const preparedData = useMemo(() => {
        if (!analysis) return null

        const { final_recommendation, analyses } = analysis
        const technical = analyses?.technical?.indicators
        const fundamental = analyses?.fundamental?.fundamental_details
        const sentiment = analyses?.sentiment

        // Helper functions for UI logic
        const getActionColor = (action: string) => {
            switch (action) {
                case 'buy': return 'text-green-600 bg-green-50 border-green-200'
                case 'sell': return 'text-red-600 bg-red-50 border-red-200'
                default: return 'text-yellow-600 bg-yellow-50 border-yellow-200'
            }
        }

        const getActionIcon = (action: string) => {
            switch (action) {
                case 'buy': return 'buy'
                case 'sell': return 'sell'
                default: return 'hold'
            }
        }

        // Prepare chart data for indicators
        const indicatorChartData = technical ? (() => {
            const { ema } = technical
            return [{
                name: 'Current Price',
                value: ema?.current_price || 0,
                ema9: ema?.ema_9 || 0,
                ema21: ema?.ema_21 || 0,
                ema50: ema?.ema_50 || 0,
            }]
        })() : []

        return {
            analysis,
            technical,
            fundamental,
            sentiment,
            final_recommendation,
            getActionColor,
            getActionIcon,
            indicatorChartData
        }
    }, [analysis])

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="mb-6">
                <div className="flex items-center gap-2 mb-2">
                    <Sparkles className="w-6 h-6 text-primary-600" />
                    <h1 className="text-3xl lg:text-4xl font-bold text-gray-900">Stock Analysis</h1>
                </div>
                <p className="text-gray-600 text-lg">
                    Get AI-powered technical and fundamental analysis for any stock
                </p>
            </div>

            <StockAnalysisForm onAnalysisComplete={setAnalysis} />

            {preparedData && (
                <div className="animate-slide-up">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="w-1 h-8 bg-gradient-to-b from-primary-600 to-primary-700 rounded-full"></div>
                        <h2 className="text-2xl lg:text-3xl font-bold text-gray-900 dark:text-gray-100">
                            Analysis: <span className="text-gradient">{analysis?.symbol || 'N/A'}</span>
                        </h2>
                    </div>

                    {/* Tabs for different analysis sections */}
                    <div className="mb-6">
                        <div className="flex gap-2 overflow-x-auto pb-2">
                            <button
                                onClick={() => setActiveTab('overview')}
                                className={`px-4 py-2 rounded-xl font-semibold transition-all whitespace-nowrap flex items-center gap-2 ${activeTab === 'overview'
                                    ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white shadow-lg'
                                    : 'bg-white dark:bg-slate-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-slate-700 border border-gray-200 dark:border-slate-700'
                                    }`}
                            >
                                <Sparkles className="w-4 h-4" />
                                Overview
                            </button>
                            <button
                                onClick={() => setActiveTab('technical')}
                                className={`px-4 py-2 rounded-xl font-semibold transition-all whitespace-nowrap flex items-center gap-2 ${activeTab === 'technical'
                                    ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white shadow-lg'
                                    : 'bg-white dark:bg-slate-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-slate-700 border border-gray-200 dark:border-slate-700'
                                    }`}
                            >
                                <BarChart3 className="w-4 h-4" />
                                Technical
                            </button>
                            <button
                                onClick={() => setActiveTab('fundamental')}
                                className={`px-4 py-2 rounded-xl font-semibold transition-all whitespace-nowrap flex items-center gap-2 ${activeTab === 'fundamental'
                                    ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white shadow-lg'
                                    : 'bg-white dark:bg-slate-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-slate-700 border border-gray-200 dark:border-slate-700'
                                    }`}
                            >
                                <TrendingUp className="w-4 h-4" />
                                Fundamental
                            </button>
                            <button
                                onClick={() => setActiveTab('financials')}
                                className={`px-4 py-2 rounded-xl font-semibold transition-all whitespace-nowrap flex items-center gap-2 ${activeTab === 'financials'
                                    ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white shadow-lg'
                                    : 'bg-white dark:bg-slate-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-slate-700 border border-gray-200 dark:border-slate-700'
                                    }`}
                            >
                                <FileText className="w-4 h-4" />
                                Financials
                            </button>
                            <button
                                onClick={() => setActiveTab('news')}
                                className={`px-4 py-2 rounded-xl font-semibold transition-all whitespace-nowrap flex items-center gap-2 ${activeTab === 'news'
                                    ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white shadow-lg'
                                    : 'bg-white dark:bg-slate-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-slate-700 border border-gray-200 dark:border-slate-700'
                                    }`}
                            >
                                <Newspaper className="w-4 h-4" />
                                News & Sentiment
                            </button>
                        </div>
                    </div>

                    {/* Tab Content */}
                    {activeTab === 'overview' && (
                        <AnalysisResult preparedData={preparedData} />
                    )}

                    {activeTab === 'technical' && (
                        <div className="card">
                            <h3 className="text-2xl font-bold mb-6">Technical Analysis</h3>
                            <AnalysisResult preparedData={preparedData} />
                        </div>
                    )}

                    {activeTab === 'fundamental' && (
                        <div className="card">
                            <h3 className="text-2xl font-bold mb-6">Fundamental Analysis</h3>
                            {preparedData.fundamental ? (
                                <div className="space-y-4">
                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                        {Object.entries(preparedData.fundamental.valuation_metrics || {}).map(([key, value]: [string, any]) => (
                                            <div key={key} className="p-4 border border-gray-200 dark:border-slate-700 rounded-lg">
                                                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1 capitalize">{key.replace(/_/g, ' ')}</p>
                                                <p className="text-xl font-bold text-gray-900 dark:text-gray-100">
                                                    {value !== null && value !== undefined ? (typeof value === 'number' ? value.toFixed(2) : value) : 'N/A'}
                                                </p>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            ) : (
                                <p className="text-gray-500 dark:text-gray-400">Fundamental data not available</p>
                            )}
                        </div>
                    )}

                    {activeTab === 'financials' && (
                        <div className="card">
                            <h3 className="text-2xl font-bold mb-6">Financial Statements</h3>
                            {loadingFinancials ? (
                                <div className="flex justify-center py-12">
                                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                                </div>
                            ) : financials ? (
                                <div className="space-y-6">
                                    {financials.financial_health && (
                                        <div className="p-6 bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/30 dark:to-blue-900/30 rounded-lg border border-primary-100 dark:border-primary-800">
                                            <h4 className="text-xl font-bold mb-4">Financial Health Score</h4>
                                            <div className="flex items-baseline gap-2">
                                                <span className="text-4xl font-bold text-primary-600 dark:text-primary-400">
                                                    {financials.financial_health.score}/100
                                                </span>
                                                <span className="text-2xl font-bold text-primary-600 dark:text-primary-400">
                                                    ({financials.financial_health.grade})
                                                </span>
                                            </div>
                                        </div>
                                    )}
                                    {financials.key_ratios && (
                                        <div>
                                            <h4 className="text-lg font-semibold mb-4">Key Ratios</h4>
                                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                                {Object.entries(financials.key_ratios).map(([key, value]: [string, any]) => (
                                                    <div key={key} className="p-4 border border-gray-200 dark:border-slate-700 rounded-lg">
                                                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-1 capitalize">{key.replace(/_/g, ' ')}</p>
                                                        <p className="text-xl font-bold text-gray-900 dark:text-gray-100">
                                                            {value !== null && value !== undefined ? (typeof value === 'number' ? value.toFixed(2) : value) : 'N/A'}
                                                        </p>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                    {financials.insights && (
                                        <div className="p-4 bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/30 dark:to-blue-900/30 rounded-lg border border-primary-100 dark:border-primary-800">
                                            <h4 className="font-semibold mb-2">AI Financial Insights</h4>
                                            <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-line">{financials.insights}</p>
                                        </div>
                                    )}
                                </div>
                            ) : (
                                <p className="text-gray-500 dark:text-gray-400">Click to load financial statements</p>
                            )}
                        </div>
                    )}

                    {activeTab === 'news' && (
                        <div className="card">
                            <h3 className="text-2xl font-bold mb-6">News & Sentiment</h3>
                            {loadingNews ? (
                                <div className="flex justify-center py-12">
                                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                                </div>
                            ) : news ? (
                                <div className="space-y-4">
                                    {news.news_items && news.news_items.length > 0 ? (
                                        <>
                                            {news.news_items.map((item: any, idx: number) => (
                                                <div key={idx} className="p-4 border border-gray-200 dark:border-slate-700 rounded-lg hover:shadow-md transition-shadow">
                                                    <div className="flex items-start justify-between mb-2">
                                                        <h4 className="font-semibold text-gray-900 dark:text-gray-100">{item.title}</h4>
                                                        <span className={`px-2 py-1 rounded text-xs font-semibold ${item.sentiment?.label === 'positive' ? 'bg-success-100 text-success-700 dark:bg-success-900/30 dark:text-success-300' :
                                                            item.sentiment?.label === 'negative' ? 'bg-danger-100 text-danger-700 dark:bg-danger-900/30 dark:text-danger-300' :
                                                                'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'
                                                            }`}>
                                                            {item.sentiment?.label || 'neutral'}
                                                        </span>
                                                    </div>
                                                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">{item.summary}</p>
                                                    <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-500">
                                                        <span>{item.source}</span>
                                                        <span>{new Date(item.published_at).toLocaleDateString()}</span>
                                                    </div>
                                                </div>
                                            ))}
                                            {news.summary && (
                                                <div className="p-4 bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/30 dark:to-blue-900/30 rounded-lg border border-primary-100 dark:border-primary-800 mt-6">
                                                    <h4 className="font-semibold mb-2">Overall Sentiment</h4>
                                                    <p className="text-sm text-gray-700 dark:text-gray-300">
                                                        {news.summary.overall_sentiment} - {news.summary.positive_count} positive, {news.summary.negative_count} negative, {news.summary.neutral_count} neutral
                                                    </p>
                                                </div>
                                            )}
                                        </>
                                    ) : (
                                        <p className="text-gray-500 dark:text-gray-400">No news available</p>
                                    )}
                                </div>
                            ) : (
                                <p className="text-gray-500 dark:text-gray-400">Click to load news</p>
                            )}
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}
