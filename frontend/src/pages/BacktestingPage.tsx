import { useState, useEffect } from 'react';
import { Play, TrendingUp, BarChart3, Target, AlertCircle, Calendar } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { backtestingService, BacktestRequest, Strategy } from '../api/backtestingService';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { useTheme } from '@/contexts/ThemeContext';

export const BacktestingPage = () => {
    const { theme } = useTheme();
    const [strategies, setStrategies] = useState<Strategy[]>([]);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<any>(null);
    
    const [formData, setFormData] = useState<BacktestRequest>({
        symbol: '',
        market: 'india_nse',
        start_date: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        end_date: new Date().toISOString().split('T')[0],
        initial_capital: 100000,
        strategy: {
            type: 'simple_momentum',
            lookback_period: 20,
            entry_threshold: 0.02
        },
        commission: 0.001
    });

    useEffect(() => {
        loadStrategies();
    }, []);

    const loadStrategies = async () => {
        try {
            const data = await backtestingService.getStrategies();
            setStrategies(data.strategies);
        } catch (error: any) {
            toast.error('Failed to load strategies');
        }
    };

    const handleStrategyChange = (strategyType: string) => {
        const strategy = strategies.find(s => s.type === strategyType);
        if (strategy) {
            const defaultParams: any = {};
            Object.keys(strategy.parameters).forEach(key => {
                defaultParams[key] = strategy.parameters[key].default;
            });
            setFormData({
                ...formData,
                strategy: {
                    type: strategyType,
                    ...defaultParams
                }
            });
        }
    };

    const handleRunBacktest = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setResult(null);

        try {
            const response = await backtestingService.runBacktest(formData);
            setResult(response);
            toast.success('Backtest completed successfully!');
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Backtest failed');
        } finally {
            setLoading(false);
        }
    };

    const isDark = theme === 'dark';

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div className="mb-6">
                <div className="flex items-center gap-2 mb-2">
                    <BarChart3 className="w-6 h-6 text-gray-900 dark:text-gray-100" />
                    <h1 className="text-3xl lg:text-4xl font-bold text-gray-900 dark:text-gray-100">Strategy Backtesting</h1>
                </div>
                <p className="text-gray-600 dark:text-gray-400 text-lg">
                    Test trading strategies against historical data
                </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Form */}
                <div className="lg:col-span-1">
                    <div className="card">
                        <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-gray-100">Backtest Configuration</h2>
                        <form onSubmit={handleRunBacktest} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Stock Symbol</label>
                                <input
                                    type="text"
                                    value={formData.symbol}
                                    onChange={(e) => setFormData({ ...formData, symbol: e.target.value.toUpperCase() })}
                                    className="input-field"
                                    placeholder="RELIANCE"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Market</label>
                                <select
                                    value={formData.market}
                                    onChange={(e) => setFormData({ ...formData, market: e.target.value })}
                                    className="input-field"
                                >
                                    <option value="india_nse">India NSE</option>
                                    <option value="india_bse">India BSE</option>
                                    <option value="us_nyse">US NYSE</option>
                                    <option value="us_nasdaq">US NASDAQ</option>
                                </select>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Start Date</label>
                                    <input
                                        type="date"
                                        value={formData.start_date}
                                        onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                                        className="input-field"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">End Date</label>
                                    <input
                                        type="date"
                                        value={formData.end_date}
                                        onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                                        className="input-field"
                                        required
                                    />
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Initial Capital</label>
                                <input
                                    type="number"
                                    value={formData.initial_capital}
                                    onChange={(e) => setFormData({ ...formData, initial_capital: parseFloat(e.target.value) })}
                                    className="input-field"
                                    min="1000"
                                    step="1000"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Strategy</label>
                                <select
                                    value={formData.strategy.type}
                                    onChange={(e) => handleStrategyChange(e.target.value)}
                                    className="input-field"
                                >
                                    {strategies.map(s => (
                                        <option key={s.type} value={s.type}>{s.name}</option>
                                    ))}
                                </select>
                            </div>

                            {formData.strategy.type === 'simple_momentum' && (
                                <>
                                    <div>
                                        <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Lookback Period</label>
                                        <input
                                            type="number"
                                            value={formData.strategy.lookback_period}
                                            onChange={(e) => setFormData({
                                                ...formData,
                                                strategy: { ...formData.strategy, lookback_period: parseInt(e.target.value) }
                                            })}
                                            className="input-field"
                                            min="5"
                                            max="100"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Entry Threshold (%)</label>
                                        <input
                                            type="number"
                                            value={formData.strategy.entry_threshold * 100}
                                            onChange={(e) => setFormData({
                                                ...formData,
                                                strategy: { ...formData.strategy, entry_threshold: parseFloat(e.target.value) / 100 }
                                            })}
                                            className="input-field"
                                            min="1"
                                            max="10"
                                            step="0.1"
                                        />
                                    </div>
                                </>
                            )}

                            <button
                                type="submit"
                                disabled={loading}
                                className="btn-primary w-full flex items-center justify-center gap-2"
                            >
                                {loading ? (
                                    <>
                                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                                        Running...
                                    </>
                                ) : (
                                    <>
                                        <Play className="w-4 h-4" />
                                        Run Backtest
                                    </>
                                )}
                            </button>
                        </form>
                    </div>
                </div>

                {/* Results */}
                <div className="lg:col-span-2 space-y-6">
                    {result ? (
                        <>
                            {/* Performance Metrics */}
                            <div className="card">
                                <h2 className="text-xl font-bold mb-4 flex items-center gap-2 text-gray-900 dark:text-gray-100">
                                    <Target className="w-5 h-5" />
                                    Performance Metrics
                                </h2>
                                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                                    <div className={`p-4 rounded-xl ${isDark ? 'bg-green-900/20 border border-green-700/50' : 'bg-green-50 border border-green-200'}`}>
                                        <p className={`text-sm ${isDark ? 'text-green-300' : 'text-green-600'} mb-1`}>Total Return</p>
                                        <p className={`text-2xl font-bold ${isDark ? 'text-green-100' : 'text-green-700'}`}>
                                            {result.performance.total_return_percent.toFixed(2)}%
                                        </p>
                                    </div>
                                    <div className={`p-4 rounded-xl ${isDark ? 'bg-blue-900/20 border border-blue-700/50' : 'bg-blue-50 border border-blue-200'}`}>
                                        <p className={`text-sm ${isDark ? 'text-blue-300' : 'text-blue-600'} mb-1`}>Sharpe Ratio</p>
                                        <p className={`text-2xl font-bold ${isDark ? 'text-blue-100' : 'text-blue-700'}`}>
                                            {result.performance.sharpe_ratio.toFixed(2)}
                                        </p>
                                    </div>
                                    <div className={`p-4 rounded-xl ${isDark ? 'bg-red-900/20 border border-red-700/50' : 'bg-red-50 border border-red-200'}`}>
                                        <p className={`text-sm ${isDark ? 'text-red-300' : 'text-red-600'} mb-1`}>Max Drawdown</p>
                                        <p className={`text-2xl font-bold ${isDark ? 'text-red-100' : 'text-red-700'}`}>
                                            {result.performance.max_drawdown_percent.toFixed(2)}%
                                        </p>
                                    </div>
                                    <div className={`p-4 rounded-xl ${isDark ? 'bg-purple-900/20 border border-purple-700/50' : 'bg-purple-50 border border-purple-200'}`}>
                                        <p className={`text-sm ${isDark ? 'text-purple-300' : 'text-purple-600'} mb-1`}>Total Trades</p>
                                        <p className={`text-2xl font-bold ${isDark ? 'text-purple-100' : 'text-purple-700'}`}>
                                            {result.performance.total_trades}
                                        </p>
                                    </div>
                                    <div className={`p-4 rounded-xl ${isDark ? 'bg-orange-900/20 border border-orange-700/50' : 'bg-orange-50 border border-orange-200'}`}>
                                        <p className={`text-sm ${isDark ? 'text-orange-300' : 'text-orange-600'} mb-1`}>Win Rate</p>
                                        <p className={`text-2xl font-bold ${isDark ? 'text-orange-100' : 'text-orange-700'}`}>
                                            {result.performance.win_rate.toFixed(1)}%
                                        </p>
                                    </div>
                                    <div className={`p-4 rounded-xl ${isDark ? 'bg-indigo-900/20 border border-indigo-700/50' : 'bg-indigo-50 border border-indigo-200'}`}>
                                        <p className={`text-sm ${isDark ? 'text-indigo-300' : 'text-indigo-600'} mb-1`}>Final Capital</p>
                                        <p className={`text-2xl font-bold ${isDark ? 'text-indigo-100' : 'text-indigo-700'}`}>
                                            ${result.performance.final_capital?.toFixed(2) || 'N/A'}
                                        </p>
                                    </div>
                                </div>
                            </div>

                            {/* Equity Curve */}
                            {result.equity_curve && result.equity_curve.length > 0 && (
                                <div className="card">
                                    <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-gray-100">Equity Curve</h2>
                                    <ResponsiveContainer width="100%" height={300}>
                                        <AreaChart data={result.equity_curve}>
                                            <defs>
                                                <linearGradient id="colorEquity" x1="0" y1="0" x2="0" y2="1">
                                                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                                                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                                                </linearGradient>
                                            </defs>
                                            <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#475569' : '#e5e7eb'} />
                                            <XAxis 
                                                dataKey="date" 
                                                stroke={isDark ? '#cbd5e1' : '#6b7280'}
                                                tickFormatter={(value) => new Date(value).toLocaleDateString()}
                                            />
                                            <YAxis stroke={isDark ? '#cbd5e1' : '#6b7280'} />
                                            <Tooltip 
                                                contentStyle={{
                                                    backgroundColor: isDark ? '#1e293b' : '#fff',
                                                    border: `1px solid ${isDark ? '#334155' : '#e5e7eb'}`,
                                                    borderRadius: '8px'
                                                }}
                                                formatter={(value: number) => [`$${value.toFixed(2)}`, 'Equity']}
                                            />
                                            <Area 
                                                type="monotone" 
                                                dataKey="equity" 
                                                stroke="#3b82f6" 
                                                fillOpacity={1} 
                                                fill="url(#colorEquity)" 
                                            />
                                        </AreaChart>
                                    </ResponsiveContainer>
                                </div>
                            )}

                            {/* Recent Trades */}
                            {result.trades && result.trades.length > 0 && (
                                <div className="card">
                                    <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-gray-100">Recent Trades</h2>
                                    <div className="overflow-x-auto">
                                        <table className="w-full">
                                            <thead className={isDark ? 'bg-slate-800' : 'bg-gray-50'}>
                                                <tr className={`border-b ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
                                                    <th className="text-left py-2 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Date</th>
                                                    <th className="text-left py-2 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Type</th>
                                                    <th className="text-right py-2 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Price</th>
                                                    <th className="text-right py-2 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Shares</th>
                                                    <th className="text-right py-2 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Value</th>
                                                </tr>
                                            </thead>
                                            <tbody className={isDark ? 'bg-slate-800' : 'bg-white'}>
                                                {result.trades.slice(-10).map((trade: any, index: number) => (
                                                    <tr key={index} className={`border-b ${isDark ? 'border-gray-700 hover:bg-slate-800/50' : 'border-gray-100 hover:bg-gray-50'}`}>
                                                        <td className="py-2 px-4 text-sm text-gray-900 dark:text-gray-100">{new Date(trade.date).toLocaleDateString()}</td>
                                                        <td className="py-2 px-4">
                                                            <span className={`px-2 py-1 rounded text-xs font-bold ${
                                                                trade.type === 'BUY' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
                                                                'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
                                                            }`}>
                                                                {trade.type}
                                                            </span>
                                                        </td>
                                                        <td className="py-2 px-4 text-sm text-right text-gray-900 dark:text-gray-100">${trade.price.toFixed(2)}</td>
                                                        <td className="py-2 px-4 text-sm text-right text-gray-900 dark:text-gray-100">{trade.shares}</td>
                                                        <td className="py-2 px-4 text-sm text-right text-gray-900 dark:text-gray-100">
                                                            ${((trade.cost || trade.proceeds) || 0).toFixed(2)}
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            )}
                        </>
                    ) : (
                        <div className="card text-center py-16">
                            <BarChart3 className="w-16 h-16 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
                            <p className="text-gray-500 dark:text-gray-400 font-medium">No backtest results yet</p>
                            <p className="text-sm text-gray-400 dark:text-gray-500 mt-2">
                                Configure and run a backtest to see results
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

