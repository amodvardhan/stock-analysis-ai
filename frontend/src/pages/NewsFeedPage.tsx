import { useEffect, useState } from 'react'
import { marketService, NewsResponse, NewsItem } from '../api/marketService'
import { toast } from 'react-hot-toast'
import { Newspaper, TrendingUp, TrendingDown, Minus, ExternalLink, Sparkles } from 'lucide-react'

export const NewsFeedPage = () => {
    const [news, setNews] = useState<NewsResponse | null>(null)
    const [loading, setLoading] = useState(true)
    const [symbol, setSymbol] = useState<string>('')
    const [market, setMarket] = useState('india_nse')

    useEffect(() => {
        loadNews()
    }, [symbol, market])

    const loadNews = async () => {
        try {
            setLoading(true)
            const data = await marketService.getNews(symbol || undefined, market, 20, 7)
            setNews(data)
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to load news')
        } finally {
            setLoading(false)
        }
    }

    const getSentimentIcon = (label: string) => {
        switch (label) {
            case 'positive':
                return <TrendingUp className="w-4 h-4 text-success-600" />
            case 'negative':
                return <TrendingDown className="w-4 h-4 text-danger-600" />
            default:
                return <Minus className="w-4 h-4 text-gray-400" />
        }
    }

    const getSentimentColor = (label: string) => {
        switch (label) {
            case 'positive':
                return 'bg-success-50 dark:bg-success-900/20 border-success-200 dark:border-success-800'
            case 'negative':
                return 'bg-danger-50 dark:bg-danger-900/20 border-danger-200 dark:border-danger-800'
            default:
                return 'bg-gray-50 dark:bg-slate-800 border-gray-200 dark:border-slate-700'
        }
    }

    if (loading && !news) {
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
                        <Newspaper className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                        <h1 className="text-3xl lg:text-4xl font-bold text-gray-900 dark:text-gray-100">
                            Financial News Feed
                        </h1>
                    </div>
                    <p className="text-gray-500 dark:text-gray-400 text-sm">
                        Latest financial news with AI-powered sentiment analysis
                    </p>
                </div>
            </div>

            {/* Filters */}
            <div className="card">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                            Stock Symbol (Optional)
                        </label>
                        <input
                            type="text"
                            value={symbol}
                            onChange={(e) => setSymbol(e.target.value)}
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
                    <div className="flex items-end">
                        <button
                            onClick={loadNews}
                            className="btn-primary w-full"
                        >
                            Refresh News
                        </button>
                    </div>
                </div>
            </div>

            {/* Summary */}
            {news && news.summary && (
                <div className="card bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/30 dark:to-blue-900/30 border border-primary-100 dark:border-primary-800">
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                        <div>
                            <p className="text-sm text-gray-600 dark:text-gray-400">Total News</p>
                            <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                                {news.summary.total_news}
                            </p>
                        </div>
                        <div>
                            <p className="text-sm text-gray-600 dark:text-gray-400">Positive</p>
                            <p className="text-2xl font-bold text-success-600 dark:text-success-400">
                                {news.summary.positive_count}
                            </p>
                        </div>
                        <div>
                            <p className="text-sm text-gray-600 dark:text-gray-400">Negative</p>
                            <p className="text-2xl font-bold text-danger-600 dark:text-danger-400">
                                {news.summary.negative_count}
                            </p>
                        </div>
                        <div>
                            <p className="text-sm text-gray-600 dark:text-gray-400">Neutral</p>
                            <p className="text-2xl font-bold text-gray-600 dark:text-gray-400">
                                {news.summary.neutral_count}
                            </p>
                        </div>
                        <div>
                            <p className="text-sm text-gray-600 dark:text-gray-400">Overall Sentiment</p>
                            <p className={`text-2xl font-bold capitalize ${
                                news.summary.overall_sentiment === 'positive'
                                    ? 'text-success-600 dark:text-success-400'
                                    : news.summary.overall_sentiment === 'negative'
                                    ? 'text-danger-600 dark:text-danger-400'
                                    : 'text-gray-600 dark:text-gray-400'
                            }`}>
                                {news.summary.overall_sentiment}
                            </p>
                        </div>
                    </div>
                </div>
            )}

            {/* News Items */}
            {news && news.news_items.length > 0 ? (
                <div className="space-y-4">
                    {news.news_items.map((item: NewsItem, index: number) => (
                        <div
                            key={index}
                            className={`card border-l-4 ${
                                item.sentiment.label === 'positive'
                                    ? 'border-l-success-500'
                                    : item.sentiment.label === 'negative'
                                    ? 'border-l-danger-500'
                                    : 'border-l-gray-400'
                            }`}
                        >
                            <div className="flex items-start justify-between gap-4">
                                <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-2">
                                        {getSentimentIcon(item.sentiment.label)}
                                        <span className="text-xs font-semibold text-gray-500 dark:text-gray-400">
                                            {item.source}
                                        </span>
                                        <span className="text-xs text-gray-400 dark:text-gray-500">
                                            {new Date(item.published_at).toLocaleDateString()}
                                        </span>
                                    </div>
                                    <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-2">
                                        {item.title}
                                    </h3>
                                    {item.summary && (
                                        <p className="text-gray-600 dark:text-gray-400 mb-3">
                                            {item.summary}
                                        </p>
                                    )}
                                    <div className="flex items-center gap-4 text-sm">
                                        <div className="flex items-center gap-1">
                                            <span className="text-gray-600 dark:text-gray-400">Sentiment:</span>
                                            <span className={`font-semibold capitalize ${
                                                item.sentiment.label === 'positive'
                                                    ? 'text-success-600 dark:text-success-400'
                                                    : item.sentiment.label === 'negative'
                                                    ? 'text-danger-600 dark:text-danger-400'
                                                    : 'text-gray-600 dark:text-gray-400'
                                            }`}>
                                                {item.sentiment.label} ({item.sentiment.score}/100)
                                            </span>
                                        </div>
                                        <div className="flex items-center gap-1">
                                            <span className="text-gray-600 dark:text-gray-400">Impact:</span>
                                            <span className="font-semibold capitalize">
                                                {item.sentiment.market_impact}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                                {item.url && (
                                    <a
                                        href={item.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="flex-shrink-0 p-2 text-primary-600 dark:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/30 rounded-lg transition-colors"
                                    >
                                        <ExternalLink className="w-5 h-5" />
                                    </a>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="card text-center py-16">
                    <Newspaper className="w-16 h-16 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
                    <p className="text-gray-500 dark:text-gray-400 font-medium">No news available</p>
                    <p className="text-sm text-gray-400 dark:text-gray-500 mt-2">Try adjusting your filters</p>
                </div>
            )}

            {/* AI Insights */}
            {news && news.insights && (
                <div className="card bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/30 dark:to-blue-900/30 border border-primary-100 dark:border-primary-800">
                    <div className="flex items-center gap-2 mb-4">
                        <Sparkles className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                        <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                            AI News Insights
                        </h3>
                    </div>
                    <p className="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-line">
                        {news.insights}
                    </p>
                </div>
            )}
        </div>
    )
}

