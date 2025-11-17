/**
 * Main Stock Analysis Component
 * 
 * This is the core feature - allows users to analyze stocks using AI
 */
import React, { useState } from 'react';
import { Search, TrendingUp, TrendingDown, AlertCircle, Target } from 'lucide-react';
import toast from 'react-hot-toast';
import { analysisAPI } from '../lib/api';
import { StockAnalysisRequest, StockAnalysisResponse } from '../types';

export const StockAnalysis: React.FC = () => {
    const [symbol, setSymbol] = useState('');
    const [market, setMarket] = useState<'india_nse' | 'india_bse' | 'us_nyse' | 'us_nasdaq'>('india_nse');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<StockAnalysisResponse | null>(null);

    const handleAnalyze = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!symbol.trim()) {
            toast.error('Please enter a stock symbol');
            return;
        }

        setLoading(true);
        setResult(null);

        try {
            const request: StockAnalysisRequest = {
                symbol: symbol.toUpperCase(),
                market,
            };

            const response = await analysisAPI.analyze(request);
            setResult(response.data);
            toast.success('Analysis completed!');
        } catch (error: any) {
            console.error('Analysis failed:', error);
            toast.error(error.response?.data?.detail || 'Analysis failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const getRecommendationColor = (rec: string) => {
        if (rec.includes('buy')) return 'text-green-600 bg-green-50';
        if (rec.includes('sell')) return 'text-red-600 bg-red-50';
        return 'text-yellow-600 bg-yellow-50';
    };

    const getRecommendationIcon = (rec: string) => {
        if (rec.includes('buy')) return <TrendingUp className="w-6 h-6" />;
        if (rec.includes('sell')) return <TrendingDown className="w-6 h-6" />;
        return <AlertCircle className="w-6 h-6" />;
    };

    return (
        <div className="max-w-6xl mx-auto p-6">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">
                    AI Stock Analysis
                </h1>
                <p className="text-gray-600">
                    Get comprehensive AI-powered analysis using multi-agent system
                </p>
            </div>

            {/* Analysis Form */}
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
                <form onSubmit={handleAnalyze} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Stock Symbol
                            </label>
                            <input
                                type="text"
                                value={symbol}
                                onChange={(e) => setSymbol(e.target.value)}
                                placeholder="e.g., RELIANCE, AAPL"
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                disabled={loading}
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Market
                            </label>
                            <select
                                value={market}
                                onChange={(e) => setMarket(e.target.value as any)}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                disabled={loading}
                            >
                                <option value="india_nse">NSE (India)</option>
                                <option value="india_bse">BSE (India)</option>
                                <option value="us_nyse">NYSE (US)</option>
                                <option value="us_nasdaq">NASDAQ (US)</option>
                            </select>
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 flex items-center justify-center gap-2 disabled:bg-gray-400 disabled:cursor-not-allowed"
                    >
                        {loading ? (
                            <>
                                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                                Analyzing... (This takes 15-30 seconds)
                            </>
                        ) : (
                            <>
                                <Search className="w-5 h-5" />
                                Analyze Stock
                            </>
                        )}
                    </button>
                </form>
            </div>

            {/* Analysis Results */}
            {result && (
                <div className="space-y-6">
                    {/* Final Recommendation Card */}
                    <div className={`rounded-lg shadow-lg p-6 ${getRecommendationColor(result.final_recommendation.final_recommendation)}`}>
                        <div className="flex items-start gap-4">
                            <div className="p-3 rounded-full bg-white">
                                {getRecommendationIcon(result.final_recommendation.final_recommendation)}
                            </div>
                            <div className="flex-1">
                                <div className="flex items-center justify-between mb-2">
                                    <h2 className="text-2xl font-bold uppercase">
                                        {result.final_recommendation.final_recommendation.replace('_', ' ')}
                                    </h2>
                                    <div className="text-right">
                                        <div className="text-sm font-medium">Confidence</div>
                                        <div className="text-3xl font-bold">
                                            {result.final_recommendation.confidence}%
                                        </div>
                                    </div>
                                </div>

                                {/* Price Targets */}
                                <div className="grid grid-cols-3 gap-4 mt-4 p-4 bg-white rounded-lg">
                                    {result.final_recommendation.entry_price && (
                                        <div>
                                            <div className="text-sm text-gray-600">Entry Price</div>
                                            <div className="text-lg font-bold">
                                                ₹{result.final_recommendation.entry_price.toFixed(2)}
                                            </div>
                                        </div>
                                    )}
                                    {result.final_recommendation.target_price && (
                                        <div>
                                            <div className="text-sm text-gray-600">Target Price</div>
                                            <div className="text-lg font-bold text-green-600">
                                                ₹{result.final_recommendation.target_price.toFixed(2)}
                                            </div>
                                        </div>
                                    )}
                                    {result.final_recommendation.stop_loss && (
                                        <div>
                                            <div className="text-sm text-gray-600">Stop Loss</div>
                                            <div className="text-lg font-bold text-red-600">
                                                ₹{result.final_recommendation.stop_loss.toFixed(2)}
                                            </div>
                                        </div>
                                    )}
                                </div>

                                {/* Risk & Time Horizon */}
                                <div className="grid grid-cols-2 gap-4 mt-4">
                                    <div className="p-3 bg-white rounded-lg">
                                        <div className="text-sm text-gray-600">Risk Level</div>
                                        <div className="font-bold uppercase">
                                            {result.final_recommendation.risk_level}
                                        </div>
                                    </div>
                                    {result.final_recommendation.time_horizon && (
                                        <div className="p-3 bg-white rounded-lg">
                                            <div className="text-sm text-gray-600">Time Horizon</div>
                                            <div className="font-bold">
                                                {result.final_recommendation.time_horizon}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Synthesis Reasoning */}
                    <div className="bg-white rounded-lg shadow-md p-6">
                        <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                            <Target className="w-5 h-5" />
                            Investment Thesis
                        </h3>
                        <div className="prose max-w-none">
                            <p className="text-gray-700 whitespace-pre-line">
                                {result.final_recommendation.synthesis_reasoning}
                            </p>
                        </div>
                    </div>

                    {/* Action Plan */}
                    {result.final_recommendation.action_plan && (
                        <div className="bg-white rounded-lg shadow-md p-6">
                            <h3 className="text-xl font-bold mb-4">Action Plan</h3>
                            <div className="prose max-w-none">
                                <p className="text-gray-700 whitespace-pre-line">
                                    {result.final_recommendation.action_plan}
                                </p>
                            </div>
                        </div>
                    )}

                    {/* Individual Agent Analyses */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {/* Technical Analysis */}
                        <div className="bg-white rounded-lg shadow-md p-6">
                            <h3 className="text-lg font-bold mb-3 text-blue-600">
                                Technical Analysis
                            </h3>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Recommendation:</span>
                                    <span className="font-bold uppercase">
                                        {result.analyses.technical?.recommendation || 'N/A'}
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Confidence:</span>
                                    <span className="font-bold">
                                        {result.analyses.technical?.confidence || 0}%
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Risk:</span>
                                    <span className="font-bold uppercase">
                                        {result.analyses.technical?.risk_level || 'N/A'}
                                    </span>
                                </div>
                            </div>
                        </div>

                        {/* Fundamental Analysis */}
                        <div className="bg-white rounded-lg shadow-md p-6">
                            <h3 className="text-lg font-bold mb-3 text-green-600">
                                Fundamental Analysis
                            </h3>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Recommendation:</span>
                                    <span className="font-bold uppercase">
                                        {result.analyses.fundamental?.recommendation || 'N/A'}
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Confidence:</span>
                                    <span className="font-bold">
                                        {result.analyses.fundamental?.confidence || 0}%
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Valuation:</span>
                                    <span className="font-bold uppercase">
                                        {result.analyses.fundamental?.valuation_assessment || 'N/A'}
                                    </span>
                                </div>
                            </div>
                        </div>

                        {/* Sentiment Analysis */}
                        <div className="bg-white rounded-lg shadow-md p-6">
                            <h3 className="text-lg font-bold mb-3 text-purple-600">
                                Sentiment Analysis
                            </h3>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Sentiment:</span>
                                    <span className="font-bold uppercase">
                                        {result.analyses.sentiment?.overall_sentiment || 'N/A'}
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Confidence:</span>
                                    <span className="font-bold">
                                        {result.analyses.sentiment?.confidence || 0}%
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">News Count:</span>
                                    <span className="font-bold">
                                        {result.analyses.sentiment?.sentiment_details?.news_count || 0}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};
