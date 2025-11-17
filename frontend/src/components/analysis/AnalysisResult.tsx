import { TrendingUp, TrendingDown, Minus, AlertCircle, Calendar, DollarSign, BarChart3, Activity } from 'lucide-react'
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, BarChart, Bar } from 'recharts'
import type { StockAnalysis } from '@/types'

interface Props {
    analysis: StockAnalysis
}

export const AnalysisResult = ({ analysis }: Props) => {
    const { final_recommendation, analyses, symbol, market } = analysis
    const technical = analyses?.technical?.indicators
    const fundamental = analyses?.fundamental?.fundamental_details
    const sentiment = analyses?.sentiment

    const getActionColor = (action: string) => {
        switch (action) {
            case 'buy': return 'text-green-600 bg-green-50 border-green-200'
            case 'sell': return 'text-red-600 bg-red-50 border-red-200'
            default: return 'text-yellow-600 bg-yellow-50 border-yellow-200'
        }
    }

    const getActionIcon = (action: string) => {
        switch (action) {
            case 'buy': return <TrendingUp className="w-8 h-8" />
            case 'sell': return <TrendingDown className="w-8 h-8" />
            default: return <Minus className="w-8 h-8" />
        }
    }

    // Prepare chart data for indicators
    const prepareIndicatorChartData = () => {
        if (!technical) return []

        const { ema, rsi, macd, bollinger_bands } = technical

        return [
            {
                name: 'Current Price',
                value: ema?.current_price || 0,
                ema9: ema?.ema_9 || 0,
                ema21: ema?.ema_21 || 0,
                ema50: ema?.ema_50 || 0,
            }
        ]
    }

    const prepareSignalData = () => {
        if (!technical) return []

        return [
            {
                name: 'RSI',
                value: technical.rsi?.value || 0,
                threshold: 50,
                overbought: 70,
                oversold: 30
            }
        ]
    }

    return (
        <div className="space-y-6">
            {/* Header Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="card bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-blue-600 font-medium">Symbol</p>
                            <p className="text-2xl font-bold text-blue-700">{symbol}</p>
                        </div>
                        <BarChart3 className="w-10 h-10 text-blue-600 opacity-50" />
                    </div>
                </div>

                <div className="card bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-purple-600 font-medium">Market</p>
                            <p className="text-2xl font-bold text-purple-700">{market.toUpperCase()}</p>
                        </div>
                        <Activity className="w-10 h-10 text-purple-600 opacity-50" />
                    </div>
                </div>

                <div className="card bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-green-600 font-medium">Current Price</p>
                            <p className="text-2xl font-bold text-green-700">
                                ${technical?.ema?.current_price?.toFixed(2) || 'N/A'}
                            </p>
                        </div>
                        <DollarSign className="w-10 h-10 text-green-600 opacity-50" />
                    </div>
                </div>

                <div className="card bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-orange-600 font-medium">Confidence</p>
                            <p className="text-2xl font-bold text-orange-700">{final_recommendation?.confidence}%</p>
                        </div>
                        <Calendar className="w-10 h-10 text-orange-600 opacity-50" />
                    </div>
                </div>
            </div>

            {/* Main Recommendation Card */}
            <div className={`card ${getActionColor(final_recommendation?.action)} border-2`}>
                <div className="flex items-center gap-4 mb-4">
                    <div className="p-3 bg-white bg-opacity-70 rounded-full">
                        {getActionIcon(final_recommendation?.action)}
                    </div>
                    <div className="flex-1">
                        <h3 className="text-3xl font-bold capitalize">{final_recommendation?.action}</h3>
                        <p className="text-sm opacity-80 mt-1">
                            Confidence: {final_recommendation?.confidence}% | Analyzed on {new Date().toLocaleDateString()}
                        </p>
                    </div>
                </div>

                <div className="bg-white bg-opacity-70 rounded-lg p-4 mb-3">
                    <h4 className="font-semibold mb-2 flex items-center gap-2">
                        <BarChart3 className="w-4 h-4" />
                        Analysis Summary
                    </h4>
                    <p className="text-sm">{final_recommendation?.reasoning}</p>
                </div>

                <div className="flex items-start gap-2 p-4 bg-white bg-opacity-70 rounded-lg">
                    <AlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
                    <div>
                        <h4 className="font-semibold mb-1">Risk Assessment</h4>
                        <p className="text-sm">{final_recommendation?.risk_assessment}</p>
                    </div>
                </div>
            </div>

            {/* Technical Analysis Section */}
            {technical && (
                <div className="card">
                    <h3 className="text-2xl font-bold mb-6 flex items-center gap-2">
                        <Activity className="w-6 h-6 text-primary-600" />
                        Technical Analysis
                    </h3>

                    {/* Moving Averages Chart */}
                    <div className="mb-6">
                        <h4 className="font-semibold mb-3">Moving Averages (EMA)</h4>
                        <div className="bg-gray-50 rounded-lg p-4">
                            <ResponsiveContainer width="100%" height={200}>
                                <BarChart data={prepareIndicatorChartData()}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="name" />
                                    <YAxis />
                                    <Tooltip />
                                    <Legend />
                                    <Bar dataKey="value" fill="#3b82f6" name="Current Price" />
                                    <Bar dataKey="ema9" fill="#10b981" name="EMA 9" />
                                    <Bar dataKey="ema21" fill="#f59e0b" name="EMA 21" />
                                    <Bar dataKey="ema50" fill="#ef4444" name="EMA 50" />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Indicators Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        {/* EMA */}
                        <div className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg border border-blue-200">
                            <h4 className="font-semibold mb-3 text-blue-900">Moving Averages</h4>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-blue-700">EMA 9:</span>
                                    <span className="font-bold text-blue-900">${technical.ema.ema_9.toFixed(2)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-blue-700">EMA 21:</span>
                                    <span className="font-bold text-blue-900">${technical.ema.ema_21.toFixed(2)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-blue-700">EMA 50:</span>
                                    <span className="font-bold text-blue-900">${technical.ema.ema_50.toFixed(2)}</span>
                                </div>
                                <div className="pt-2 border-t border-blue-300">
                                    <div className="flex justify-between items-center">
                                        <span className="text-blue-700">Trend:</span>
                                        <span className={`px-2 py-1 rounded text-xs font-bold ${technical.ema.signal === 'bullish' ? 'bg-green-200 text-green-800' :
                                            technical.ema.signal === 'bearish' ? 'bg-red-200 text-red-800' :
                                                'bg-yellow-200 text-yellow-800'
                                            }`}>
                                            {technical.ema.trend.replace('_', ' ').toUpperCase()}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* RSI */}
                        <div className="p-4 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg border border-purple-200">
                            <h4 className="font-semibold mb-3 text-purple-900">RSI Indicator</h4>
                            <div className="space-y-3">
                                <div className="relative pt-1">
                                    <div className="flex mb-2 items-center justify-between">
                                        <div>
                                            <span className="text-xs font-semibold inline-block text-purple-700">
                                                RSI Value
                                            </span>
                                        </div>
                                        <div className="text-right">
                                            <span className="text-xs font-semibold inline-block text-purple-900">
                                                {technical.rsi.value.toFixed(2)}
                                            </span>
                                        </div>
                                    </div>
                                    <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-purple-200">
                                        <div
                                            style={{ width: `${Math.min(technical.rsi.value, 100)}%` }}
                                            className={`shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center ${technical.rsi.value > 70 ? 'bg-red-500' :
                                                technical.rsi.value < 30 ? 'bg-green-500' :
                                                    'bg-purple-500'
                                                }`}
                                        ></div>
                                    </div>
                                </div>
                                <div className={`px-3 py-2 rounded text-center text-xs font-bold ${technical.rsi.signal === 'overbought' ? 'bg-red-200 text-red-800' :
                                    technical.rsi.signal === 'oversold' ? 'bg-green-200 text-green-800' :
                                        'bg-gray-200 text-gray-800'
                                    }`}>
                                    {technical.rsi.signal.toUpperCase()}
                                </div>
                                <p className="text-xs text-purple-700 text-center">
                                    {technical.rsi.interpretation}
                                </p>
                            </div>
                        </div>

                        {/* MACD */}
                        <div className="p-4 bg-gradient-to-br from-green-50 to-green-100 rounded-lg border border-green-200">
                            <h4 className="font-semibold mb-3 text-green-900">MACD</h4>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-green-700">MACD Line:</span>
                                    <span className="font-bold text-green-900">{technical.macd.macd_line.toFixed(2)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-green-700">Signal Line:</span>
                                    <span className="font-bold text-green-900">{technical.macd.signal_line.toFixed(2)}</span>
                                </div>
                                <div className="pt-2 border-t border-green-300">
                                    <div className="flex justify-between items-center">
                                        <span className="text-green-700">Signal:</span>
                                        <span className={`px-2 py-1 rounded text-xs font-bold ${technical.macd.signal === 'bullish' ? 'bg-green-200 text-green-800' :
                                            'bg-red-200 text-red-800'
                                            }`}>
                                            {technical.macd.signal.toUpperCase()}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Bollinger Bands */}
                        <div className="p-4 bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg border border-orange-200">
                            <h4 className="font-semibold mb-3 text-orange-900">Bollinger Bands</h4>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-orange-700">Upper:</span>
                                    <span className="font-bold text-orange-900">${technical.bollinger_bands.upper_band.toFixed(2)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-orange-700">Lower:</span>
                                    <span className="font-bold text-orange-900">${technical.bollinger_bands.lower_band.toFixed(2)}</span>
                                </div>
                                <div className="pt-2 border-t border-orange-300">
                                    <div className="flex justify-between items-center">
                                        <span className="text-orange-700">Signal:</span>
                                        <span className={`px-2 py-1 rounded text-xs font-bold ${technical.bollinger_bands.signal === 'overbought' ? 'bg-red-200 text-red-800' :
                                            technical.bollinger_bands.signal === 'oversold' ? 'bg-green-200 text-green-800' :
                                                'bg-gray-200 text-gray-800'
                                            }`}>
                                            {technical.bollinger_bands.signal.toUpperCase()}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Overall Summary */}
                    <div className="mt-6 p-6 bg-gradient-to-r from-primary-50 to-primary-100 rounded-lg border-2 border-primary-200">
                        <h4 className="font-bold text-lg mb-4 text-primary-900">Technical Summary</h4>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div className="text-center">
                                <div className={`text-4xl font-bold mb-1 ${technical.summary.overall_signal === 'buy' ? 'text-green-600' :
                                    technical.summary.overall_signal === 'sell' ? 'text-red-600' :
                                        'text-yellow-600'
                                    }`}>
                                    {technical.summary.overall_signal.toUpperCase()}
                                </div>
                                <p className="text-sm text-gray-600">Overall Signal</p>
                            </div>
                            <div className="text-center">
                                <div className="text-4xl font-bold text-green-600 mb-1">
                                    {technical.summary.bullish_indicators}
                                </div>
                                <p className="text-sm text-gray-600">Bullish Indicators</p>
                            </div>
                            <div className="text-center">
                                <div className="text-4xl font-bold text-red-600 mb-1">
                                    {technical.summary.bearish_indicators}
                                </div>
                                <p className="text-sm text-gray-600">Bearish Indicators</p>
                            </div>
                        </div>
                        <div className="mt-4 text-center">
                            <span className="text-sm text-gray-700">Confidence: </span>
                            <span className="text-lg font-bold text-primary-700">
                                {technical.summary.confidence.toFixed(0)}%
                            </span>
                        </div>
                    </div>
                </div>
            )}

            {/* Fundamental Data */}
            {fundamental && !fundamental.error && (
                <div className="card">
                    <h3 className="text-2xl font-bold mb-4">Fundamental Analysis</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="p-4 bg-gray-50 rounded-lg">
                            <h4 className="font-semibold mb-2">Valuation</h4>
                            <div className="space-y-1 text-sm">
                                <div className="flex justify-between">
                                    <span>P/E Ratio:</span>
                                    <span className="font-medium">{fundamental.valuation?.pe_ratio?.toFixed(2) || 'N/A'}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span>Price to Book:</span>
                                    <span className="font-medium">{fundamental.valuation?.price_to_book?.toFixed(2) || 'N/A'}</span>
                                </div>
                            </div>
                        </div>

                        <div className="p-4 bg-gray-50 rounded-lg">
                            <h4 className="font-semibold mb-2">Profitability</h4>
                            <div className="space-y-1 text-sm">
                                <div className="flex justify-between">
                                    <span>Profit Margin:</span>
                                    <span className="font-medium">{(fundamental.profitability?.profit_margins * 100)?.toFixed(2)}%</span>
                                </div>
                                <div className="flex justify-between">
                                    <span>ROE:</span>
                                    <span className="font-medium">{(fundamental.profitability?.roe * 100)?.toFixed(2)}%</span>
                                </div>
                            </div>
                        </div>

                        <div className="p-4 bg-gray-50 rounded-lg">
                            <h4 className="font-semibold mb-2">Company Profile</h4>
                            <div className="space-y-1 text-sm">
                                <div className="flex justify-between">
                                    <span>Sector:</span>
                                    <span className="font-medium">{fundamental.company_profile?.sector || 'N/A'}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span>Industry:</span>
                                    <span className="font-medium">{fundamental.company_profile?.industry || 'N/A'}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
