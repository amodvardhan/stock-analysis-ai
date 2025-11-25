import { useState, useEffect } from 'react';
import { Shield, AlertTriangle, TrendingDown, BarChart3, Target } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { riskService, PortfolioRiskResponse } from '../api/riskService';
import { portfolioService } from '../api/portfolioService';
import { RiskAssessmentChart } from '@/components/charts';
import { useTheme } from '@/contexts/ThemeContext';

export const RiskDashboardPage = () => {
    const { theme } = useTheme();
    const [portfolioRisk, setPortfolioRisk] = useState<PortfolioRiskResponse | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadPortfolioRisk();
    }, []);

    const loadPortfolioRisk = async () => {
        try {
            setLoading(true);
            // Get portfolio summary first to get portfolio ID
            const summary = await portfolioService.getPortfolioSummary();
            const portfolioId = summary.portfolio.id;

            // Then get risk analysis
            const risk = await riskService.getPortfolioRisk(portfolioId);
            setPortfolioRisk(risk);
        } catch (error: any) {
            toast.error('Failed to load portfolio risk');
        } finally {
            setLoading(false);
        }
    };

    const getRiskLevelColor = (riskLevel: string) => {
        switch (riskLevel) {
            case 'very_high':
                return 'text-red-600 bg-red-50 border-red-200 dark:text-red-400 dark:bg-red-900/20 dark:border-red-800';
            case 'high':
                return 'text-orange-600 bg-orange-50 border-orange-200 dark:text-orange-400 dark:bg-orange-900/20 dark:border-orange-800';
            case 'moderate':
                return 'text-yellow-600 bg-yellow-50 border-yellow-200 dark:text-yellow-400 dark:bg-yellow-900/20 dark:border-yellow-800';
            case 'low':
                return 'text-green-600 bg-green-50 border-green-200 dark:text-green-400 dark:bg-green-900/20 dark:border-green-800';
            default:
                return 'text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-slate-800 border-gray-200 dark:border-slate-700';
        }
    };

    const isDark = theme === 'dark';

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div className="mb-6">
                <div className="flex items-center gap-2 mb-2">
                    <Shield className="w-6 h-6 text-gray-900 dark:text-gray-100" />
                    <h1 className="text-3xl lg:text-4xl font-bold text-gray-900 dark:text-gray-100">Risk Dashboard</h1>
                </div>
                <p className="text-gray-600 dark:text-gray-400 text-lg">
                    Comprehensive portfolio risk analysis and management
                </p>
            </div>

            {loading ? (
                <div className="card text-center py-16">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 dark:border-primary-400 mx-auto"></div>
                </div>
            ) : portfolioRisk ? (
                <>
                    {/* Risk Overview Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <div className={`card ${getRiskLevelColor(portfolioRisk.risk_level)} border-2`}>
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium mb-1 opacity-80">Risk Level</p>
                                    <p className="text-2xl font-bold capitalize">{portfolioRisk.risk_level.replace('_', ' ')}</p>
                                </div>
                                <Shield className="w-10 h-10 opacity-50" />
                            </div>
                        </div>

                        <div className="card bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border border-blue-200 dark:border-blue-700/50">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-blue-600 dark:text-blue-300 font-medium mb-1">Diversification</p>
                                    <p className="text-2xl font-bold text-blue-700 dark:text-blue-100">
                                        {portfolioRisk.diversification_score.toFixed(0)}%
                                    </p>
                                </div>
                                <BarChart3 className="w-10 h-10 text-blue-600 dark:text-blue-400 opacity-50" />
                            </div>
                        </div>

                        <div className="card bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 border border-purple-200 dark:border-purple-700/50">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-purple-600 dark:text-purple-300 font-medium mb-1">CVaR (95%)</p>
                                    <p className="text-2xl font-bold text-purple-700 dark:text-purple-100">
                                        ${Math.abs(portfolioRisk.cvar_95).toFixed(2)}
                                    </p>
                                </div>
                                <AlertTriangle className="w-10 h-10 text-purple-600 dark:text-purple-400 opacity-50" />
                            </div>
                        </div>

                        <div className="card bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20 border border-red-200 dark:border-red-700/50">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-red-600 dark:text-red-300 font-medium mb-1">Max Drawdown</p>
                                    <p className="text-2xl font-bold text-red-700 dark:text-red-100">
                                        {portfolioRisk.max_drawdown.toFixed(2)}%
                                    </p>
                                </div>
                                <TrendingDown className="w-10 h-10 text-red-600 dark:text-red-400 opacity-50" />
                            </div>
                        </div>
                    </div>

                    {/* Risk Assessment Chart */}
                    <div className="card">
                        <RiskAssessmentChart
                            riskData={{
                                total_risk: portfolioRisk.concentration_risk,
                                diversification_score: portfolioRisk.diversification_score,
                                sector_concentration: portfolioRisk.sector_allocation,
                                risk_breakdown: [
                                    { category: 'Concentration Risk', value: portfolioRisk.concentration_risk, color: '#ef4444' },
                                    { category: 'Volatility Risk', value: portfolioRisk.portfolio_volatility * 100, color: '#f59e0b' },
                                    { category: 'Drawdown Risk', value: portfolioRisk.max_drawdown, color: '#3b82f6' }
                                ],
                                cvar_95: portfolioRisk.cvar_95,
                                max_drawdown: portfolioRisk.max_drawdown
                            }}
                            height={500}
                        />
                    </div>

                    {/* Additional Risk Metrics */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="card">
                            <h3 className="text-xl font-bold mb-4 flex items-center gap-2 text-gray-900 dark:text-gray-100">
                                <BarChart3 className="w-5 h-5" />
                                Sector Allocation
                            </h3>
                            <div className="space-y-3">
                                {Object.entries(portfolioRisk.sector_allocation).map(([sector, percentage]) => (
                                    <div key={sector}>
                                        <div className="flex justify-between mb-1">
                                            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{sector}</span>
                                            <span className="text-sm font-bold text-gray-900 dark:text-gray-100">{percentage.toFixed(1)}%</span>
                                        </div>
                                        <div className={`h-2 rounded-full ${isDark ? 'bg-gray-700' : 'bg-gray-200'}`}>
                                            <div
                                                className={`h-full rounded-full ${percentage > 30 ? 'bg-red-500' :
                                                    percentage > 15 ? 'bg-yellow-500' :
                                                        'bg-green-500'
                                                    }`}
                                                style={{ width: `${Math.min(percentage, 100)}%` }}
                                            />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="card">
                            <h3 className="text-xl font-bold mb-4 flex items-center gap-2 text-gray-900 dark:text-gray-100">
                                <Target className="w-5 h-5" />
                                Risk Metrics
                            </h3>
                            <div className="space-y-4">
                                <div className="flex justify-between items-center p-3 rounded-lg bg-gray-50 dark:bg-gray-800">
                                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Portfolio Volatility</span>
                                    <span className="text-lg font-bold text-gray-900 dark:text-gray-100">{(portfolioRisk.portfolio_volatility * 100).toFixed(2)}%</span>
                                </div>
                                <div className="flex justify-between items-center p-3 rounded-lg bg-gray-50 dark:bg-gray-800">
                                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Concentration Risk</span>
                                    <span className="text-lg font-bold text-gray-900 dark:text-gray-100">{portfolioRisk.concentration_risk.toFixed(1)}%</span>
                                </div>
                                <div className="flex justify-between items-center p-3 rounded-lg bg-gray-50 dark:bg-gray-800">
                                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Total Portfolio Value</span>
                                    <span className="text-lg font-bold text-gray-900 dark:text-gray-100">${portfolioRisk.total_portfolio_value.toFixed(2)}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </>
            ) : (
                <div className="card text-center py-16">
                    <Shield className="w-16 h-16 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
                    <p className="text-gray-500 dark:text-gray-400 font-medium">No portfolio selected</p>
                    <p className="text-sm text-gray-400 dark:text-gray-500 mt-2">
                        Select a portfolio to view risk analysis
                    </p>
                </div>
            )}
        </div>
    );
};

