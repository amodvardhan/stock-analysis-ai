import { TrendingUp, TrendingDown, Minus, AlertCircle, Calendar, DollarSign, BarChart3, Activity, Info } from 'lucide-react'
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, AreaChart, Area, Line } from 'recharts'
import { CandlestickChart, VolumeChart } from '@/components/charts'
import { useTheme } from '@/contexts/ThemeContext'

interface PreparedData {
    analysis: any
    technical: any
    fundamental: any
    final_recommendation: any
    getActionColor: (action: string) => string
    getActionIcon: (action: string) => string
    indicatorChartData: any[]
}

interface Props {
    preparedData: PreparedData
}

export const AnalysisResult = ({ preparedData }: Props) => {
    const { theme } = useTheme()
    const {
        analysis,
        technical,
        fundamental,
        final_recommendation,
        getActionColor,
        getActionIcon,
        indicatorChartData
    } = preparedData

    const { symbol, market } = analysis

    // Prepare candlestick data (mock for now - would come from API)
    const candlestickData = technical?.historical_data || [
        { date: '2024-01-01', open: 100, high: 105, low: 98, close: 103, volume: 1000000 },
        { date: '2024-01-02', open: 103, high: 108, low: 101, close: 106, volume: 1200000 },
        { date: '2024-01-03', open: 106, high: 110, low: 104, close: 109, volume: 1500000 },
    ]

    // Prepare volume data
    const volumeData = candlestickData.map((item: any, index: number) => ({
        date: item.date,
        volume: item.volume,
        price: item.close,
        priceChange: index > 0 ? ((item.close - candlestickData[index - 1].close) / candlestickData[index - 1].close) * 100 : 0
    }))

    // Icon rendering helper
    const renderActionIcon = (actionType: string) => {
        switch (actionType) {
            case 'buy': return <TrendingUp className="w-8 h-8" />
            case 'sell': return <TrendingDown className="w-8 h-8" />
            default: return <Minus className="w-8 h-8" />
        }
    }

    const isDark = theme === 'dark'

    return (
        <div className="space-y-6">
            {/* Professional Header Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className={`card ${isDark ? 'bg-gradient-to-br from-blue-900/20 to-blue-800/20 border-blue-700/50' : 'bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200'}`}>
                    <div className="flex items-center justify-between">
                        <div>
                            <p className={`text-sm font-medium mb-1 ${isDark ? 'text-blue-300' : 'text-blue-600'}`}>Symbol</p>
                            <p className={`text-2xl font-bold ${isDark ? 'text-blue-100' : 'text-blue-700'}`}>{symbol}</p>
                        </div>
                        <BarChart3 className={`w-10 h-10 ${isDark ? 'text-blue-400' : 'text-blue-600'} opacity-50`} />
                    </div>
                </div>

                <div className={`card ${isDark ? 'bg-gradient-to-br from-purple-900/20 to-purple-800/20 border-purple-700/50' : 'bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200'}`}>
                    <div className="flex items-center justify-between">
                        <div>
                            <p className={`text-sm font-medium mb-1 ${isDark ? 'text-purple-300' : 'text-purple-600'}`}>Market</p>
                            <p className={`text-2xl font-bold ${isDark ? 'text-purple-100' : 'text-purple-700'}`}>{market.toUpperCase()}</p>
                        </div>
                        <Activity className={`w-10 h-10 ${isDark ? 'text-purple-400' : 'text-purple-600'} opacity-50`} />
                    </div>
                </div>

                <div className={`card ${isDark ? 'bg-gradient-to-br from-green-900/20 to-green-800/20 border-green-700/50' : 'bg-gradient-to-br from-green-50 to-green-100 border-green-200'}`}>
                    <div className="flex items-center justify-between">
                        <div>
                            <p className={`text-sm font-medium mb-1 ${isDark ? 'text-green-300' : 'text-green-600'}`}>Current Price</p>
                            <p className={`text-2xl font-bold ${isDark ? 'text-green-100' : 'text-green-700'}`}>
                                ${technical?.ema?.current_price?.toFixed(2) || 'N/A'}
                            </p>
                        </div>
                        <DollarSign className={`w-10 h-10 ${isDark ? 'text-green-400' : 'text-green-600'} opacity-50`} />
                    </div>
                </div>

                <div className={`card ${isDark ? 'bg-gradient-to-br from-orange-900/20 to-orange-800/20 border-orange-700/50' : 'bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200'}`}>
                    <div className="flex items-center justify-between">
                        <div>
                            <p className={`text-sm font-medium mb-1 ${isDark ? 'text-orange-300' : 'text-orange-600'}`}>Confidence</p>
                            <p className={`text-2xl font-bold ${isDark ? 'text-orange-100' : 'text-orange-700'}`}>{final_recommendation?.confidence}%</p>
                        </div>
                        <Calendar className={`w-10 h-10 ${isDark ? 'text-orange-400' : 'text-orange-600'} opacity-50`} />
                    </div>
                </div>
            </div>

            {/* Main Recommendation Card - Professional Design */}
            <div className={`card ${getActionColor(final_recommendation?.action)} border-2 ${isDark ? 'bg-opacity-90' : ''}`}>
                <div className="flex items-center gap-4 mb-6">
                    <div className={`p-4 ${isDark ? 'bg-white/10' : 'bg-white/70'} rounded-2xl backdrop-blur-sm`}>
                        {renderActionIcon(getActionIcon(final_recommendation?.action))}
                    </div>
                    <div className="flex-1">
                        <h3 className="text-3xl font-bold capitalize mb-2">{final_recommendation?.action}</h3>
                        <p className={`text-sm ${isDark ? 'opacity-70' : 'opacity-80'}`}>
                            Confidence: {final_recommendation?.confidence}% | {new Date().toLocaleDateString()}
                        </p>
                    </div>
                </div>

                <div className={`${isDark ? 'bg-white/5' : 'bg-white/70'} rounded-xl p-5 mb-4 backdrop-blur-sm`}>
                    <h4 className="font-semibold mb-3 flex items-center gap-2">
                        <BarChart3 className="w-5 h-5" />
                        AI Analysis Summary
                    </h4>
                    <p className="text-sm leading-relaxed">{final_recommendation?.reasoning}</p>
                </div>

                <div className={`flex items-start gap-3 p-4 ${isDark ? 'bg-white/5' : 'bg-white/70'} rounded-xl backdrop-blur-sm`}>
                    <AlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
                    <div>
                        <h4 className="font-semibold mb-2">Risk Assessment</h4>
                        <p className="text-sm leading-relaxed">{final_recommendation?.risk_assessment}</p>
                    </div>
                </div>
            </div>

            {/* Professional Candlestick Chart */}
            {candlestickData && candlestickData.length > 0 && (
                <div className="card">
                    <div className="flex items-center justify-between mb-6">
                        <h3 className="text-2xl font-bold flex items-center gap-2">
                            <BarChart3 className="w-6 h-6" />
                            Price Chart
                        </h3>
                        <div className="flex gap-2">
                            <button className="px-3 py-1.5 text-xs font-medium rounded-lg bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300">1D</button>
                            <button className="px-3 py-1.5 text-xs font-medium rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">1W</button>
                            <button className="px-3 py-1.5 text-xs font-medium rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">1M</button>
                            <button className="px-3 py-1.5 text-xs font-medium rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">3M</button>
                        </div>
                    </div>
                    <CandlestickChart data={candlestickData} height={400} showVolume={true} />
                </div>
            )}

            {/* Volume Analysis */}
            {volumeData && volumeData.length > 0 && (
                <div className="card">
                    <h3 className="text-xl font-bold mb-4">Volume Analysis</h3>
                    <VolumeChart data={volumeData} height={250} />
                </div>
            )}

            {/* Technical Analysis Section */}
            {technical && (
                <div className="card">
                    <h3 className="text-2xl font-bold mb-6 flex items-center gap-2">
                        <Activity className="w-6 h-6" />
                        Technical Indicators
                    </h3>

                    {/* Moving Averages Line Chart */}
                    <div className="mb-8">
                        <h4 className="font-semibold mb-4">Moving Averages (EMA)</h4>
                        <div className={`${isDark ? 'bg-gray-800/50' : 'bg-gray-50'} rounded-xl p-4`}>
                            <ResponsiveContainer width="100%" height={300}>
                                <AreaChart data={indicatorChartData}>
                                    <defs>
                                        <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#475569' : '#e5e7eb'} />
                                    <XAxis dataKey="name" stroke={isDark ? '#cbd5e1' : '#6b7280'} />
                                    <YAxis stroke={isDark ? '#cbd5e1' : '#6b7280'} />
                                    <Tooltip
                                        contentStyle={{
                                            backgroundColor: isDark ? '#1e293b' : '#fff',
                                            border: `1px solid ${isDark ? '#334155' : '#e5e7eb'}`,
                                            borderRadius: '8px',
                                            color: isDark ? '#f1f5f9' : '#0f172a'
                                        }}
                                    />
                                    <Legend />
                                    <Area type="monotone" dataKey="value" stroke="#3b82f6" fillOpacity={1} fill="url(#colorPrice)" name="Current Price" />
                                    <Line type="monotone" dataKey="ema9" stroke="#10b981" strokeWidth={2} name="EMA 9" />
                                    <Line type="monotone" dataKey="ema21" stroke="#f59e0b" strokeWidth={2} name="EMA 21" />
                                    <Line type="monotone" dataKey="ema50" stroke="#ef4444" strokeWidth={2} name="EMA 50" />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Indicators Grid - Enhanced */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        {/* EMA Card */}
                        <div className={`p-5 rounded-xl border ${isDark ? 'bg-blue-900/20 border-blue-700/50' : 'bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200'}`}>
                            <h4 className={`font-semibold mb-4 ${isDark ? 'text-blue-200' : 'text-blue-900'}`}>Moving Averages</h4>
                            <div className="space-y-3 text-sm">
                                <div className="flex justify-between items-center">
                                    <span className={isDark ? 'text-blue-300' : 'text-blue-700'}>EMA 9:</span>
                                    <span className={`font-bold ${isDark ? 'text-blue-100' : 'text-blue-900'}`}>${technical.ema.ema_9.toFixed(2)}</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className={isDark ? 'text-blue-300' : 'text-blue-700'}>EMA 21:</span>
                                    <span className={`font-bold ${isDark ? 'text-blue-100' : 'text-blue-900'}`}>${technical.ema.ema_21.toFixed(2)}</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className={isDark ? 'text-blue-300' : 'text-blue-700'}>EMA 50:</span>
                                    <span className={`font-bold ${isDark ? 'text-blue-100' : 'text-blue-900'}`}>${technical.ema.ema_50.toFixed(2)}</span>
                                </div>
                                <div className="pt-3 border-t border-blue-300/50">
                                    <div className="flex justify-between items-center">
                                        <span className={isDark ? 'text-blue-300' : 'text-blue-700'}>Trend:</span>
                                        <span className={`px-3 py-1 rounded-lg text-xs font-bold ${technical.ema.signal === 'bullish' ? 'bg-green-500/20 text-green-400 border border-green-500/30' :
                                            technical.ema.signal === 'bearish' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
                                                'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                                            }`}>
                                            {technical.ema.trend.replace('_', ' ').toUpperCase()}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* RSI Card */}
                        <div className={`p-5 rounded-xl border ${isDark ? 'bg-purple-900/20 border-purple-700/50' : 'bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200'}`}>
                            <h4 className={`font-semibold mb-4 ${isDark ? 'text-purple-200' : 'text-purple-900'}`}>RSI Indicator</h4>
                            <div className="space-y-4">
                                <div className="relative">
                                    <div className="flex mb-2 items-center justify-between">
                                        <span className={`text-xs font-semibold ${isDark ? 'text-purple-300' : 'text-purple-700'}`}>RSI Value</span>
                                        <span className={`text-sm font-bold ${isDark ? 'text-purple-100' : 'text-purple-900'}`}>
                                            {technical.rsi.value.toFixed(2)}
                                        </span>
                                    </div>
                                    <div className={`overflow-hidden h-3 rounded-full ${isDark ? 'bg-purple-900/50' : 'bg-purple-200'}`}>
                                        <div
                                            style={{ width: `${Math.min(technical.rsi.value, 100)}%` }}
                                            className={`h-full transition-all ${technical.rsi.value > 70 ? 'bg-red-500' :
                                                technical.rsi.value < 30 ? 'bg-green-500' :
                                                    'bg-purple-500'
                                                }`}
                                        />
                                    </div>
                                </div>
                                <div className={`px-3 py-2 rounded-lg text-center text-xs font-bold ${technical.rsi.signal === 'overbought' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
                                    technical.rsi.signal === 'oversold' ? 'bg-green-500/20 text-green-400 border border-green-500/30' :
                                        'bg-gray-500/20 text-gray-400 border border-gray-500/30'
                                    }`}>
                                    {technical.rsi.signal.toUpperCase()}
                                </div>
                            </div>
                        </div>

                        {/* MACD Card */}
                        <div className={`p-5 rounded-xl border ${isDark ? 'bg-green-900/20 border-green-700/50' : 'bg-gradient-to-br from-green-50 to-green-100 border-green-200'}`}>
                            <h4 className={`font-semibold mb-4 ${isDark ? 'text-green-200' : 'text-green-900'}`}>MACD</h4>
                            <div className="space-y-3 text-sm">
                                <div className="flex justify-between">
                                    <span className={isDark ? 'text-green-300' : 'text-green-700'}>MACD Line:</span>
                                    <span className={`font-bold ${isDark ? 'text-green-100' : 'text-green-900'}`}>{technical.macd.macd_line.toFixed(2)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className={isDark ? 'text-green-300' : 'text-green-700'}>Signal Line:</span>
                                    <span className={`font-bold ${isDark ? 'text-green-100' : 'text-green-900'}`}>{technical.macd.signal_line.toFixed(2)}</span>
                                </div>
                                <div className="pt-3 border-t border-green-300/50">
                                    <div className="flex justify-between items-center">
                                        <span className={isDark ? 'text-green-300' : 'text-green-700'}>Signal:</span>
                                        <span className={`px-3 py-1 rounded-lg text-xs font-bold ${technical.macd.signal === 'bullish' ? 'bg-green-500/20 text-green-400 border border-green-500/30' :
                                            'bg-red-500/20 text-red-400 border border-red-500/30'
                                            }`}>
                                            {technical.macd.signal.toUpperCase()}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Bollinger Bands Card */}
                        <div className={`p-5 rounded-xl border ${isDark ? 'bg-orange-900/20 border-orange-700/50' : 'bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200'}`}>
                            <h4 className={`font-semibold mb-4 ${isDark ? 'text-orange-200' : 'text-orange-900'}`}>Bollinger Bands</h4>
                            <div className="space-y-3 text-sm">
                                <div className="flex justify-between">
                                    <span className={isDark ? 'text-orange-300' : 'text-orange-700'}>Upper:</span>
                                    <span className={`font-bold ${isDark ? 'text-orange-100' : 'text-orange-900'}`}>${technical.bollinger_bands.upper_band.toFixed(2)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className={isDark ? 'text-orange-300' : 'text-orange-700'}>Lower:</span>
                                    <span className={`font-bold ${isDark ? 'text-orange-100' : 'text-orange-900'}`}>${technical.bollinger_bands.lower_band.toFixed(2)}</span>
                                </div>
                                <div className="pt-3 border-t border-orange-300/50">
                                    <div className="flex justify-between items-center">
                                        <span className={isDark ? 'text-orange-300' : 'text-orange-700'}>Signal:</span>
                                        <span className={`px-3 py-1 rounded-lg text-xs font-bold ${technical.bollinger_bands.signal === 'overbought' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
                                            technical.bollinger_bands.signal === 'oversold' ? 'bg-green-500/20 text-green-400 border border-green-500/30' :
                                                'bg-gray-500/20 text-gray-400 border border-gray-500/30'
                                            }`}>
                                            {technical.bollinger_bands.signal.toUpperCase()}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Technical Summary - Enhanced */}
                    <div className={`mt-8 p-6 rounded-xl border-2 ${isDark ? 'bg-gradient-to-r from-blue-900/30 to-purple-900/30 border-blue-700/50' :
                        'bg-gradient-to-r from-primary-50 to-primary-100 border-primary-200'
                        }`}>
                        <h4 className={`font-bold text-lg mb-6 ${isDark ? 'text-primary-200' : 'text-primary-900'}`}>Technical Summary</h4>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            <div className="text-center">
                                <div className={`text-5xl font-bold mb-2 ${technical.summary.overall_signal === 'buy' ? 'text-green-500' :
                                    technical.summary.overall_signal === 'sell' ? 'text-red-500' :
                                        'text-yellow-500'
                                    }`}>
                                    {technical.summary.overall_signal.toUpperCase()}
                                </div>
                                <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>Overall Signal</p>
                            </div>
                            <div className="text-center">
                                <div className="text-5xl font-bold text-green-500 mb-2">
                                    {technical.summary.bullish_indicators}
                                </div>
                                <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>Bullish Indicators</p>
                            </div>
                            <div className="text-center">
                                <div className="text-5xl font-bold text-red-500 mb-2">
                                    {technical.summary.bearish_indicators}
                                </div>
                                <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>Bearish Indicators</p>
                            </div>
                        </div>
                        <div className="mt-6 text-center">
                            <span className={`text-sm ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>Confidence: </span>
                            <span className={`text-2xl font-bold ${isDark ? 'text-primary-300' : 'text-primary-700'}`}>
                                {technical.summary.confidence.toFixed(0)}%
                            </span>
                        </div>
                    </div>
                </div>
            )}

            {/* Fundamental Data - Enhanced */}
            {fundamental && !fundamental.error && (
                <div className="card">
                    <h3 className="text-2xl font-bold mb-6 flex items-center gap-2">
                        <Info className="w-6 h-6" />
                        Fundamental Analysis
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className={`p-5 rounded-xl border ${isDark ? 'bg-gray-800/50 border-gray-700' : 'bg-gray-50 border-gray-200'}`}>
                            <h4 className="font-semibold mb-4">Valuation</h4>
                            <div className="space-y-3 text-sm">
                                <div className="flex justify-between">
                                    <span className={isDark ? 'text-gray-400' : 'text-gray-600'}>P/E Ratio:</span>
                                    <span className={`font-medium ${isDark ? 'text-gray-200' : 'text-gray-900'}`}>
                                        {fundamental.valuation?.pe_ratio?.toFixed(2) || 'N/A'}
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className={isDark ? 'text-gray-400' : 'text-gray-600'}>Price to Book:</span>
                                    <span className={`font-medium ${isDark ? 'text-gray-200' : 'text-gray-900'}`}>
                                        {fundamental.valuation?.price_to_book?.toFixed(2) || 'N/A'}
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div className={`p-5 rounded-xl border ${isDark ? 'bg-gray-800/50 border-gray-700' : 'bg-gray-50 border-gray-200'}`}>
                            <h4 className="font-semibold mb-4">Profitability</h4>
                            <div className="space-y-3 text-sm">
                                <div className="flex justify-between">
                                    <span className={isDark ? 'text-gray-400' : 'text-gray-600'}>Profit Margin:</span>
                                    <span className={`font-medium ${isDark ? 'text-gray-200' : 'text-gray-900'}`}>
                                        {(fundamental.profitability?.profit_margins * 100)?.toFixed(2)}%
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className={isDark ? 'text-gray-400' : 'text-gray-600'}>ROE:</span>
                                    <span className={`font-medium ${isDark ? 'text-gray-200' : 'text-gray-900'}`}>
                                        {(fundamental.profitability?.roe * 100)?.toFixed(2)}%
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div className={`p-5 rounded-xl border ${isDark ? 'bg-gray-800/50 border-gray-700' : 'bg-gray-50 border-gray-200'}`}>
                            <h4 className="font-semibold mb-4">Company Profile</h4>
                            <div className="space-y-3 text-sm">
                                <div className="flex justify-between">
                                    <span className={isDark ? 'text-gray-400' : 'text-gray-600'}>Sector:</span>
                                    <span className={`font-medium ${isDark ? 'text-gray-200' : 'text-gray-900'}`}>
                                        {fundamental.company_profile?.sector || 'N/A'}
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className={isDark ? 'text-gray-400' : 'text-gray-600'}>Industry:</span>
                                    <span className={`font-medium ${isDark ? 'text-gray-200' : 'text-gray-900'}`}>
                                        {fundamental.company_profile?.industry || 'N/A'}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
