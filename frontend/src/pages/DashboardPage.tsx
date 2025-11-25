import { useEffect, useState, useMemo } from 'react'
import { TrendingUp, Briefcase, Eye, Clock, Sparkles, ArrowRight, Globe, Activity, TrendingDown, Wifi, WifiOff } from 'lucide-react'
import { useAuthStore } from '@/stores/authStore'
import { useNavigate } from 'react-router-dom'
import { marketService } from '@/api/marketService'
import { toast } from 'react-hot-toast'
import { useWebSocket } from '../hooks/useWebSocket'
import { formatPrice, formatPriceLocale, getCurrencySymbol } from '../utils/currency'

export const DashboardPage = () => {
    const user = useAuthStore((state) => state.user)
    const navigate = useNavigate()
    const [marketOverview, setMarketOverview] = useState<any>(null)
    const [marketMovers, setMarketMovers] = useState<any>(null)
    const [loading, setLoading] = useState(true)
    const [market, setMarket] = useState('india_nse')

    // Extract symbols for WebSocket subscription
    const symbols = useMemo(() => {
        if (!marketMovers) return []
        const allStocks = [
            ...(marketMovers.gainers || []),
            ...(marketMovers.losers || [])
        ]
        return [...new Set(allStocks.map((stock: any) => stock.symbol))]
    }, [marketMovers])

    // Connect to WebSocket for real-time price updates
    const { isConnected, priceUpdates } = useWebSocket(symbols, market)

    useEffect(() => {
        loadMarketData()
    }, [])

    const loadMarketData = async () => {
        try {
            setLoading(true)
            const [overview, movers] = await Promise.all([
                marketService.getMarketOverview(market, true, true).catch(() => null),
                marketService.getMarketMovers(market, 'all', 5).catch(() => null)
            ])
            setMarketOverview(overview)
            setMarketMovers(movers)
        } catch (error: any) {
            toast.error('Failed to load market data')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Welcome Section */}
            <div className="mb-8">
                <div className="flex items-center gap-2 mb-2">
                    <Sparkles className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                    <h1 className="text-3xl lg:text-4xl font-bold text-gray-900 dark:text-gray-100">
                        Welcome back, <span className="text-gradient">{user?.full_name?.split(' ')[0]}</span>!
                    </h1>
                </div>
                <p className="text-gray-600 dark:text-gray-400 text-lg">
                    Here's your stock market intelligence dashboard
                </p>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
                <div className="metric-card group bg-gradient-to-br from-blue-500 via-blue-600 to-blue-700 text-white animate-slide-up" style={{ animationDelay: '0ms' }}>
                    <div className="relative z-10 flex items-center justify-between">
                        <div>
                            <p className="text-blue-100 text-sm font-medium mb-1">Total Analyses</p>
                            <p className="text-3xl lg:text-4xl font-bold">0</p>
                        </div>
                        <div className="w-12 h-12 lg:w-14 lg:h-14 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                            <TrendingUp className="w-6 h-6 lg:w-7 lg:h-7" />
                        </div>
                    </div>
                </div>

                <div className="metric-card group bg-gradient-to-br from-success-500 via-success-600 to-success-700 text-white animate-slide-up" style={{ animationDelay: '100ms' }}>
                    <div className="relative z-10 flex items-center justify-between">
                        <div>
                            <p className="text-success-100 text-sm font-medium mb-1">Portfolio Value</p>
                            <p className="text-3xl lg:text-4xl font-bold">{getCurrencySymbol(market)}0</p>
                        </div>
                        <div className="w-12 h-12 lg:w-14 lg:h-14 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                            <Briefcase className="w-6 h-6 lg:w-7 lg:h-7" />
                        </div>
                    </div>
                </div>

                <div className="metric-card group bg-gradient-to-br from-purple-500 via-purple-600 to-purple-700 text-white animate-slide-up" style={{ animationDelay: '200ms' }}>
                    <div className="relative z-10 flex items-center justify-between">
                        <div>
                            <p className="text-purple-100 text-sm font-medium mb-1">Watchlist</p>
                            <p className="text-3xl lg:text-4xl font-bold">0</p>
                        </div>
                        <div className="w-12 h-12 lg:w-14 lg:h-14 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                            <Eye className="w-6 h-6 lg:w-7 lg:h-7" />
                        </div>
                    </div>
                </div>

                <div className="metric-card group bg-gradient-to-br from-orange-500 via-orange-600 to-orange-700 text-white animate-slide-up" style={{ animationDelay: '300ms' }}>
                    <div className="relative z-10 flex items-center justify-between">
                        <div>
                            <p className="text-orange-100 text-sm font-medium mb-1">Last Analysis</p>
                            <p className="text-lg lg:text-xl font-bold">Never</p>
                        </div>
                        <div className="w-12 h-12 lg:w-14 lg:h-14 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                            <Clock className="w-6 h-6 lg:w-7 lg:h-7" />
                        </div>
                    </div>
                </div>
            </div>

            {/* Market Overview - Integrated */}
            {marketOverview && (
                <div className="card animate-slide-up" style={{ animationDelay: '400ms' }}>
                    <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center gap-3">
                        <Globe className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Market Overview</h2>
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                            {isConnected ? (
                                <>
                                    <Wifi className="w-4 h-4 text-green-500" />
                                    <span className="text-green-600 dark:text-green-400">Live</span>
                                </>
                            ) : (
                                <>
                                    <WifiOff className="w-4 h-4 text-gray-400" />
                                    <span className="text-gray-500 dark:text-gray-400">Connecting...</span>
                                </>
                            )}
                        </div>
                    </div>
                    
                    {/* Key Indices */}
                    {marketOverview.indices && (
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                            {Object.entries(marketOverview.indices).slice(0, 3).map(([name, data]: [string, any]) => (
                                <div key={name} className="p-4 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-slate-800 dark:to-slate-700 rounded-lg border border-gray-200 dark:border-slate-600">
                                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">{name}</p>
                                    <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                                        {formatPriceLocale(data.value, market, { maximumFractionDigits: 0 })}
                                    </p>
                                    <div className={`flex items-center gap-1 mt-1 ${data.change_percent >= 0 ? 'text-success-600' : 'text-danger-600'}`}>
                                        {data.change_percent >= 0 ? (
                                            <TrendingUp className="w-4 h-4" />
                                        ) : (
                                            <TrendingDown className="w-4 h-4" />
                                        )}
                                        <span className="text-sm font-semibold">
                                            {data.change_percent >= 0 ? '+' : ''}{data.change_percent?.toFixed(2)}%
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Top Movers */}
                    {marketMovers && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {/* Top Gainers */}
                            {marketMovers.gainers && marketMovers.gainers.length > 0 && (
                                <div>
                                    <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3 flex items-center gap-2">
                                        <TrendingUp className="w-5 h-5 text-success-600" />
                                        Top Gainers
                                    </h3>
                                    <div className="space-y-2">
                                        {marketMovers.gainers.slice(0, 3).map((stock: any, idx: number) => {
                                            const liveUpdate = priceUpdates.get(stock.symbol)
                                            const current_price = liveUpdate?.current_price ?? stock.current_price
                                            const change_percent = liveUpdate?.change_percent ?? stock.change_percent
                                            
                                            return (
                                            <div key={idx} className="flex items-center justify-between p-3 bg-success-50 dark:bg-success-900/20 rounded-lg">
                                                <div>
                                                    <p className="font-semibold text-gray-900 dark:text-gray-100">{stock.symbol}</p>
                                                    <p className="text-sm text-gray-600 dark:text-gray-400">{stock.company_name}</p>
                                                </div>
                                                <div className="text-right">
                                                    <p className="font-bold text-success-600 dark:text-success-400">
                                                            +{change_percent?.toFixed(2)}%
                                                    </p>
                                                        <div className="flex items-center justify-end gap-2">
                                                    <p className="text-sm text-gray-600 dark:text-gray-400">
                                                                {formatPrice(current_price, market)}
                                                    </p>
                                                            {liveUpdate && (
                                                                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" title="Live price"></div>
                                                            )}
                                                        </div>
                                                    </div>
                                                </div>
                                            )
                                        })}
                                    </div>
                                </div>
                            )}

                            {/* Top Losers */}
                            {marketMovers.losers && marketMovers.losers.length > 0 && (
                                <div>
                                    <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3 flex items-center gap-2">
                                        <TrendingDown className="w-5 h-5 text-danger-600" />
                                        Top Losers
                                    </h3>
                                    <div className="space-y-2">
                                        {marketMovers.losers.slice(0, 3).map((stock: any, idx: number) => {
                                            const liveUpdate = priceUpdates.get(stock.symbol)
                                            const current_price = liveUpdate?.current_price ?? stock.current_price
                                            const change_percent = liveUpdate?.change_percent ?? stock.change_percent
                                            
                                            return (
                                            <div key={idx} className="flex items-center justify-between p-3 bg-danger-50 dark:bg-danger-900/20 rounded-lg">
                                                <div>
                                                    <p className="font-semibold text-gray-900 dark:text-gray-100">{stock.symbol}</p>
                                                    <p className="text-sm text-gray-600 dark:text-gray-400">{stock.company_name}</p>
                                                </div>
                                                <div className="text-right">
                                                    <p className="font-bold text-danger-600 dark:text-danger-400">
                                                            {change_percent?.toFixed(2)}%
                                                    </p>
                                                        <div className="flex items-center justify-end gap-2">
                                                    <p className="text-sm text-gray-600 dark:text-gray-400">
                                                                {formatPrice(current_price, market)}
                                                    </p>
                                                            {liveUpdate && (
                                                                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" title="Live price"></div>
                                                            )}
                                                        </div>
                                                    </div>
                                                </div>
                                            )
                                        })}
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}

            {/* Getting Started */}
            <div className="card animate-slide-up" style={{ animationDelay: '500ms' }}>
                <div className="flex items-center gap-3 mb-6">
                    <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl flex items-center justify-center">
                        <Sparkles className="w-5 h-5 text-white" />
                    </div>
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Getting Started</h2>
                </div>
                <div className="space-y-4">
                    <div 
                        className="group flex items-start gap-4 p-5 bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/30 dark:to-blue-900/30 rounded-xl border border-primary-100 dark:border-primary-800 hover:shadow-md transition-all duration-200 cursor-pointer"
                        onClick={() => navigate('/analysis')}
                    >
                        <div className="w-10 h-10 bg-gradient-to-br from-primary-600 to-primary-700 text-white rounded-xl flex items-center justify-center flex-shrink-0 font-bold shadow-md group-hover:scale-110 transition-transform">
                            1
                        </div>
                        <div className="flex-1">
                            <div className="flex items-center justify-between">
                                <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-1">Analyze Your First Stock</h3>
                                <ArrowRight className="w-5 h-5 text-primary-600 dark:text-primary-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                            </div>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                                Use our AI-powered analysis to get comprehensive insights on any stock
                            </p>
                        </div>
                    </div>

                    <div 
                        className="group flex items-start gap-4 p-5 bg-gradient-to-r from-success-50 to-emerald-50 dark:from-success-900/30 dark:to-emerald-900/30 rounded-xl border border-success-100 dark:border-success-800 hover:shadow-md transition-all duration-200 cursor-pointer"
                        onClick={() => navigate('/watchlist')}
                    >
                        <div className="w-10 h-10 bg-gradient-to-br from-success-600 to-success-700 text-white rounded-xl flex items-center justify-center flex-shrink-0 font-bold shadow-md group-hover:scale-110 transition-transform">
                            2
                        </div>
                        <div className="flex-1">
                            <div className="flex items-center justify-between">
                                <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-1">Add Stocks to Watchlist</h3>
                                <ArrowRight className="w-5 h-5 text-success-600 dark:text-success-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                            </div>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                                Monitor stocks you're interested in and get real-time price alerts
                            </p>
                        </div>
                    </div>

                    <div 
                        className="group flex items-start gap-4 p-5 bg-gradient-to-r from-purple-50 to-violet-50 dark:from-purple-900/30 dark:to-violet-900/30 rounded-xl border border-purple-100 dark:border-purple-800 hover:shadow-md transition-all duration-200 cursor-pointer"
                        onClick={() => navigate('/portfolio')}
                    >
                        <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-purple-700 text-white rounded-xl flex items-center justify-center flex-shrink-0 font-bold shadow-md group-hover:scale-110 transition-transform">
                            3
                        </div>
                        <div className="flex-1">
                            <div className="flex items-center justify-between">
                                <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-1">Track Your Portfolio</h3>
                                <ArrowRight className="w-5 h-5 text-purple-600 dark:text-purple-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                            </div>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                                Add your holdings and track performance with real-time updates
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
