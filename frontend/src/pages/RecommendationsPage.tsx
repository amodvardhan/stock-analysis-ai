import React, { useState, useEffect } from 'react';
import { recommendationService } from '../api/recommendationService';
import { RecommendationsResponse, StockRecommendation } from '../types';
import { toast } from 'react-hot-toast';
import { TrendingUp, TrendingDown, BarChart3, Target, AlertCircle, Sparkles, Calendar } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';

const RecommendationsPage: React.FC = () => {
    const [period, setPeriod] = useState<'daily' | 'weekly'>('daily');
    const [dailyData, setDailyData] = useState<RecommendationsResponse | null>(null);
    const [weeklyData, setWeeklyData] = useState<RecommendationsResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [market, setMarket] = useState('india_nse');

    useEffect(() => {
        loadRecommendations();
    }, [period, market]);

    const loadRecommendations = async () => {
        try {
            setLoading(true);
            if (period === 'daily') {
                const data = await recommendationService.getDailyRecommendations(market);
                setDailyData(data);
            } else {
                const data = await recommendationService.getWeeklyRecommendations(market);
                setWeeklyData(data);
            }
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to load recommendations');
        } finally {
            setLoading(false);
        }
    };

    const currentData = period === 'daily' ? dailyData : weeklyData;

    if (loading && !currentData) {
        return (
            <div className="flex justify-center items-center h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
                <div>
                    <div className="flex items-center gap-2 mb-2">
                        <Sparkles className="w-6 h-6 text-primary-600" />
                        <h1 className="text-3xl lg:text-4xl font-bold text-gray-900">AI Stock Recommendations</h1>
                    </div>
                    <p className="text-gray-500 text-sm">
                        Top 5 stocks based on deep market analysis, technical indicators, and AI-powered insights
                    </p>
                </div>
            </div>

            {/* Period Tabs */}
            <div className="flex gap-3 mb-6">
                <button
                    onClick={() => setPeriod('daily')}
                    className={`px-6 py-3 rounded-xl font-semibold transition-all ${period === 'daily'
                        ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white shadow-lg'
                        : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
                        }`}
                >
                    <Calendar className="w-4 h-4 inline mr-2" />
                    Top 5 of the Day
                </button>
                <button
                    onClick={() => setPeriod('weekly')}
                    className={`px-6 py-3 rounded-xl font-semibold transition-all ${period === 'weekly'
                        ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white shadow-lg'
                        : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
                        }`}
                >
                    <Calendar className="w-4 h-4 inline mr-2" />
                    Top 5 of the Week
                </button>
            </div>

            {/* Market Selector */}
            <div className="mb-6">
                <label className="block text-sm font-semibold text-gray-700 mb-2">Market</label>
                <select
                    value={market}
                    onChange={(e) => setMarket(e.target.value)}
                    className="input-field max-w-xs"
                >
                    <option value="india_nse">India NSE</option>
                    <option value="india_bse">India BSE</option>
                    <option value="us_nyse">US NYSE</option>
                    <option value="us_nasdaq">US NASDAQ</option>
                </select>
            </div>

            {/* Recommendations Grid */}
            {currentData && currentData.recommendations.length > 0 ? (
                <div className="grid grid-cols-1 gap-6">
                    {currentData.recommendations.map((rec, index) => (
                        <RecommendationCard key={rec.symbol} recommendation={rec} rank={index + 1} />
                    ))}
                </div>
            ) : (
                <div className="card text-center py-16">
                    <AlertCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500 font-medium">No recommendations available</p>
                    <p className="text-sm text-gray-400 mt-2">Please try again later</p>
                </div>
            )}

            {/* Analysis Metadata */}
            {currentData && (
                <div className="card bg-gradient-to-r from-primary-50 to-blue-50 border border-primary-100">
                    <div className="flex items-center gap-2 mb-2">
                        <BarChart3 className="w-5 h-5 text-primary-600" />
                        <h3 className="font-semibold text-gray-900">Analysis Details</h3>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                            <p className="text-gray-600">Risk Tolerance</p>
                            <p className="font-semibold text-gray-900 capitalize">
                                {currentData.analysis_metadata.user_risk_tolerance}
                            </p>
                        </div>
                        <div>
                            <p className="text-gray-600">Stocks Analyzed</p>
                            <p className="font-semibold text-gray-900">
                                {currentData.analysis_metadata.stocks_analyzed}
                            </p>
                        </div>
                        <div>
                            <p className="text-gray-600">Analysis Depth</p>
                            <p className="font-semibold text-gray-900 capitalize">
                                {currentData.analysis_metadata.analysis_depth}
                            </p>
                        </div>
                        <div>
                            <p className="text-gray-600">Generated At</p>
                            <p className="font-semibold text-gray-900">
                                {new Date(currentData.generated_at).toLocaleTimeString()}
                            </p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

// Recommendation Card Component
interface RecommendationCardProps {
    recommendation: StockRecommendation;
    rank: number;
}

const RecommendationCard: React.FC<RecommendationCardProps> = ({ recommendation, rank }) => {
    const [showDetails, setShowDetails] = useState(false);
    const { symbol, company_name, current_price, score, recommendation: rec, confidence, reasoning,
        historical_performance, forecast, price_history, risk_level,
        ai_reasoning, market_context, comparative_advantages, risk_factors, entry_strategy, time_horizon } = recommendation;

    // Prepare chart data
    const chartData = price_history.map((price, index) => ({
        day: index + 1,
        price: price
    }));

    const scoreColor = score >= 80 ? 'from-success-500 to-success-600' :
        score >= 60 ? 'from-primary-500 to-primary-600' :
            'from-warning-500 to-warning-600';

    const recColor = rec === 'buy' || rec === 'strong_buy' ? 'text-success-600' :
        rec === 'hold' ? 'text-warning-600' : 'text-danger-600';

    return (
        <div className="card overflow-hidden hover:shadow-lg transition-all duration-300">
            {/* Header */}
            <div className={`bg-gradient-to-r ${scoreColor} text-white p-6`}>
                <div className="flex items-start justify-between">
                    <div className="flex items-center gap-4">
                        <div className="w-16 h-16 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                            <span className="text-3xl font-bold">#{rank}</span>
                        </div>
                        <div>
                            <h3 className="text-2xl font-bold">{symbol}</h3>
                            <p className="text-white/90 text-sm">{company_name}</p>
                        </div>
                    </div>
                    <div className="text-right">
                        <div className="text-3xl font-bold">₹{current_price.toFixed(2)}</div>
                        <div className="text-white/90 text-sm">Current Price</div>
                    </div>
                </div>
            </div>

            {/* Key Metrics */}
            <div className="p-6 border-b border-gray-200">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <MetricItem
                        label="Recommendation Score"
                        value={`${score.toFixed(1)}/100`}
                        icon={<Target className="w-4 h-4" />}
                    />
                    <MetricItem
                        label="AI Recommendation"
                        value={rec.toUpperCase()}
                        icon={<Sparkles className="w-4 h-4" />}
                        valueColor={recColor}
                    />
                    <MetricItem
                        label="Confidence"
                        value={`${confidence.toFixed(1)}%`}
                        icon={<TrendingUp className="w-4 h-4" />}
                    />
                    <MetricItem
                        label="Risk Level"
                        value={risk_level.toUpperCase()}
                        icon={<AlertCircle className="w-4 h-4" />}
                    />
                </div>
            </div>

            {/* Price History Chart */}
            {price_history.length > 0 && (
                <div className="p-6 border-b border-gray-200">
                    <h4 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                        <BarChart3 className="w-5 h-5 text-primary-600" />
                        Price History (Last 30 Days)
                    </h4>
                    <ResponsiveContainer width="100%" height={200}>
                        <AreaChart data={chartData}>
                            <defs>
                                <linearGradient id={`color${symbol}`} x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                            <XAxis dataKey="day" stroke="#6b7280" />
                            <YAxis stroke="#6b7280" />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }}
                                formatter={(value: number) => [`₹${value.toFixed(2)}`, 'Price']}
                            />
                            <Area
                                type="monotone"
                                dataKey="price"
                                stroke="#3b82f6"
                                strokeWidth={2}
                                fillOpacity={1}
                                fill={`url(#color${symbol})`}
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            )}

            {/* Historical Performance */}
            <div className="p-6 border-b border-gray-200">
                <h4 className="font-semibold text-gray-900 mb-4">Historical Performance</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <PerformanceItem
                        label="1 Day"
                        value={historical_performance["1d_change"]}
                        suffix="%"
                    />
                    <PerformanceItem
                        label="7 Days"
                        value={historical_performance["7d_change"]}
                        suffix="%"
                    />
                    <PerformanceItem
                        label="30 Days"
                        value={historical_performance["30d_change"]}
                        suffix="%"
                    />
                    <PerformanceItem
                        label="90 Days"
                        value={historical_performance["90d_change"]}
                        suffix="%"
                    />
                </div>
                <div className="mt-4 grid grid-cols-2 gap-4">
                    <div>
                        <p className="text-sm text-gray-600">52W High</p>
                        <p className="font-semibold text-gray-900">₹{historical_performance.high_52w.toFixed(2)}</p>
                    </div>
                    <div>
                        <p className="text-sm text-gray-600">52W Low</p>
                        <p className="font-semibold text-gray-900">₹{historical_performance.low_52w.toFixed(2)}</p>
                    </div>
                </div>
            </div>

            {/* Forecast */}
            <div className="p-6 border-b border-gray-200">
                <h4 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-success-600" />
                    AI Forecast
                </h4>
                <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 bg-success-50 rounded-lg border border-success-200">
                        <p className="text-sm text-success-700 mb-1">7-Day Forecast</p>
                        <p className="text-2xl font-bold text-success-900">₹{forecast.price_7d.toFixed(2)}</p>
                        <p className={`text-sm font-semibold ${forecast.expected_change_7d >= 0 ? 'text-success-600' : 'text-danger-600'}`}>
                            {forecast.expected_change_7d >= 0 ? '+' : ''}{forecast.expected_change_7d.toFixed(2)}%
                        </p>
                    </div>
                    <div className="p-4 bg-primary-50 rounded-lg border border-primary-200">
                        <p className="text-sm text-primary-700 mb-1">30-Day Forecast</p>
                        <p className="text-2xl font-bold text-primary-900">₹{forecast.price_30d.toFixed(2)}</p>
                        <p className={`text-sm font-semibold ${forecast.expected_change_30d >= 0 ? 'text-success-600' : 'text-danger-600'}`}>
                            {forecast.expected_change_30d >= 0 ? '+' : ''}{forecast.expected_change_30d.toFixed(2)}%
                        </p>
                    </div>
                </div>
                <p className="text-xs text-gray-500 mt-3">{forecast.forecast_basis}</p>
                <p className="text-xs text-gray-500">Forecast Confidence: {forecast.confidence.toFixed(1)}%</p>
            </div>

            {/* AI-Powered Analysis */}
            <div className="p-6">
                <button
                    onClick={() => setShowDetails(!showDetails)}
                    className="w-full flex items-center justify-between text-left"
                >
                    <h4 className="font-semibold text-gray-900 flex items-center gap-2">
                        <Sparkles className="w-5 h-5 text-primary-600" />
                        Deep AI Analysis & Reasoning
                    </h4>
                    <span className="text-primary-600">{showDetails ? '▼' : '▶'}</span>
                </button>
                {showDetails && (
                    <div className="mt-4 space-y-4">
                        {/* AI Reasoning (Enhanced) */}
                        {ai_reasoning && (
                            <div className="p-4 bg-gradient-to-r from-primary-50 to-blue-50 rounded-lg border border-primary-200">
                                <h5 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                                    <Sparkles className="w-4 h-4 text-primary-600" />
                                    AI Comparative Analysis
                                </h5>
                                <p className="text-sm text-gray-700 leading-relaxed">{ai_reasoning}</p>
                            </div>
                        )}

                        {/* Market Context */}
                        {market_context && (
                            <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                                <h5 className="font-semibold text-gray-900 mb-2">Market Context</h5>
                                <p className="text-sm text-gray-700 leading-relaxed">{market_context}</p>
                            </div>
                        )}

                        {/* Base Reasoning */}
                        <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                            <h5 className="font-semibold text-gray-900 mb-2">Analysis Summary</h5>
                            <p className="text-sm text-gray-700 leading-relaxed">{reasoning}</p>
                        </div>

                        {/* Comparative Advantages */}
                        {comparative_advantages && comparative_advantages.length > 0 && (
                            <div className="p-4 bg-success-50 rounded-lg border border-success-200">
                                <h5 className="font-semibold text-success-900 mb-2 flex items-center gap-2">
                                    <TrendingUp className="w-4 h-4 text-success-600" />
                                    Key Advantages
                                </h5>
                                <ul className="list-disc list-inside space-y-1">
                                    {comparative_advantages.map((advantage, idx) => (
                                        <li key={idx} className="text-sm text-success-800">{advantage}</li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        {/* Risk Factors */}
                        {risk_factors && risk_factors.length > 0 && (
                            <div className="p-4 bg-danger-50 rounded-lg border border-danger-200">
                                <h5 className="font-semibold text-danger-900 mb-2 flex items-center gap-2">
                                    <AlertCircle className="w-4 h-4 text-danger-600" />
                                    Risk Factors
                                </h5>
                                <ul className="list-disc list-inside space-y-1">
                                    {risk_factors.map((risk, idx) => (
                                        <li key={idx} className="text-sm text-danger-800">{risk}</li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        {/* Entry Strategy */}
                        {entry_strategy && (
                            <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                                <h5 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
                                    <Target className="w-4 h-4 text-blue-600" />
                                    Entry Strategy
                                </h5>
                                <p className="text-sm text-blue-800 leading-relaxed">{entry_strategy}</p>
                            </div>
                        )}

                        {/* Time Horizon */}
                        {time_horizon && (
                            <div className="p-4 bg-orange-50 rounded-lg border border-orange-200">
                                <h5 className="font-semibold text-orange-900 mb-2">Recommended Time Horizon</h5>
                                <p className="text-sm text-orange-800 font-medium">{time_horizon}</p>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

// Helper Components
interface MetricItemProps {
    label: string;
    value: string;
    icon: React.ReactNode;
    valueColor?: string;
}

const MetricItem: React.FC<MetricItemProps> = ({ label, value, icon, valueColor = 'text-gray-900' }) => (
    <div>
        <div className="flex items-center gap-2 text-gray-600 text-sm mb-1">
            {icon}
            <span>{label}</span>
        </div>
        <p className={`font-bold ${valueColor}`}>{value}</p>
    </div>
);

interface PerformanceItemProps {
    label: string;
    value: number;
    suffix?: string;
}

const PerformanceItem: React.FC<PerformanceItemProps> = ({ label, value, suffix = '' }) => {
    const isPositive = value >= 0;
    const color = isPositive ? 'text-success-600' : 'text-danger-600';
    const Icon = isPositive ? TrendingUp : TrendingDown;

    return (
        <div className="p-3 bg-gray-50 rounded-lg">
            <p className="text-xs text-gray-600 mb-1">{label}</p>
            <div className="flex items-center gap-1">
                <Icon className={`w-4 h-4 ${color}`} />
                <p className={`font-bold ${color}`}>
                    {isPositive ? '+' : ''}{value.toFixed(2)}{suffix}
                </p>
            </div>
        </div>
    );
};

export default RecommendationsPage;

