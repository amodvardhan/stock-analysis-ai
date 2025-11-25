import React from 'react';
import {
    PieChart,
    Pie,
    Cell,
    ResponsiveContainer,
    Legend,
    Tooltip,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    ReferenceLine
} from 'recharts';
import { AlertTriangle, Shield, TrendingDown } from 'lucide-react';

interface RiskData {
    category: string;
    value: number;
    color: string;
}

interface PortfolioRisk {
    total_risk: number;
    diversification_score: number;
    sector_concentration: Record<string, number>;
    risk_breakdown: RiskData[];
    cvar_95?: number; // Conditional Value at Risk at 95%
    max_drawdown?: number;
}

interface Props {
    riskData: PortfolioRisk;
    height?: number;
}

export const RiskAssessmentChart: React.FC<Props> = ({ riskData, height = 400 }) => {
    const { risk_breakdown, sector_concentration, total_risk, diversification_score, cvar_95, max_drawdown } = riskData;

    // Transform sector concentration for bar chart
    const sectorData = Object.entries(sector_concentration).map(([sector, percentage]) => ({
        sector: sector.length > 15 ? `${sector.substring(0, 15)}...` : sector,
        percentage: Number(percentage),
        risk_level: percentage > 30 ? 'high' : percentage > 15 ? 'medium' : 'low'
    }));

    const CustomTooltip = ({ active, payload }: any) => {
        if (active && payload && payload.length) {
            const data = payload[0];
            return (
                <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
                    <p className="font-semibold text-gray-900 mb-1">{data.name || data.payload.sector}</p>
                    <p className="text-sm text-gray-600">
                        {data.value ? `${data.value.toFixed(1)}%` : `${data.payload.percentage.toFixed(1)}%`}
                    </p>
                </div>
            );
        }
        return null;
    };

    const getRiskLevel = (risk: number): { label: string; color: string; icon: React.ReactNode } => {
        if (risk >= 70) {
            return {
                label: 'Very High',
                color: 'text-red-600 bg-red-50 border-red-200',
                icon: <AlertTriangle className="w-5 h-5 text-red-600" />
            };
        } else if (risk >= 50) {
            return {
                label: 'High',
                color: 'text-orange-600 bg-orange-50 border-orange-200',
                icon: <AlertTriangle className="w-5 h-5 text-orange-600" />
            };
        } else if (risk >= 30) {
            return {
                label: 'Moderate',
                color: 'text-yellow-600 bg-yellow-50 border-yellow-200',
                icon: <Shield className="w-5 h-5 text-yellow-600" />
            };
        } else {
            return {
                label: 'Low',
                color: 'text-green-600 bg-green-50 border-green-200',
                icon: <Shield className="w-5 h-5 text-green-600" />
            };
        }
    };

    const riskLevel = getRiskLevel(total_risk);

    return (
        <div className="space-y-6">
            {/* Overall Risk Score */}
            <div className={`card ${riskLevel.color} border-2`}>
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                        {riskLevel.icon}
                        <div>
                            <h3 className="text-xl font-bold">Portfolio Risk Assessment</h3>
                            <p className="text-sm opacity-80">Overall Risk Score</p>
                        </div>
                    </div>
                    <div className="text-right">
                        <div className="text-4xl font-bold">{total_risk.toFixed(0)}</div>
                        <div className="text-sm opacity-80">/ 100</div>
                    </div>
                </div>
                <div className="grid grid-cols-2 gap-4 mt-4">
                    <div className="bg-white bg-opacity-70 rounded-lg p-3">
                        <p className="text-xs text-gray-600 mb-1">Diversification Score</p>
                        <p className="text-2xl font-bold">{diversification_score.toFixed(0)}%</p>
                    </div>
                    {cvar_95 && (
                        <div className="bg-white bg-opacity-70 rounded-lg p-3">
                            <p className="text-xs text-gray-600 mb-1">CVaR (95%)</p>
                            <p className="text-2xl font-bold">${cvar_95.toFixed(2)}</p>
                        </div>
                    )}
                    {max_drawdown && (
                        <div className="bg-white bg-opacity-70 rounded-lg p-3">
                            <p className="text-xs text-gray-600 mb-1">Max Drawdown</p>
                            <p className="text-2xl font-bold text-red-600">{max_drawdown.toFixed(2)}%</p>
                        </div>
                    )}
                </div>
            </div>

            {/* Risk Breakdown Pie Chart */}
            <div className="card">
                <h3 className="text-lg font-bold mb-4">Risk Breakdown</h3>
                <ResponsiveContainer width="100%" height={height / 2}>
                    <PieChart>
                        <Pie
                            data={risk_breakdown}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                            outerRadius={100}
                            fill="#8884d8"
                            dataKey="value"
                        >
                            {risk_breakdown.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                        </Pie>
                        <Tooltip content={<CustomTooltip />} />
                        <Legend />
                    </PieChart>
                </ResponsiveContainer>
            </div>

            {/* Sector Concentration Bar Chart */}
            <div className="card">
                <h3 className="text-lg font-bold mb-4">Sector Concentration Risk</h3>
                <ResponsiveContainer width="100%" height={height / 2}>
                    <BarChart data={sectorData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                        <XAxis
                            dataKey="sector"
                            stroke="#6b7280"
                            fontSize={11}
                            angle={-45}
                            textAnchor="end"
                            height={80}
                        />
                        <YAxis
                            stroke="#6b7280"
                            fontSize={11}
                            tickFormatter={(value) => `${value}%`}
                        />
                        <Tooltip content={<CustomTooltip />} />
                        <Bar dataKey="percentage" radius={[4, 4, 0, 0]}>
                            {sectorData.map((entry, index) => (
                                <Cell
                                    key={`cell-${index}`}
                                    fill={
                                        entry.risk_level === 'high' ? '#ef4444' :
                                        entry.risk_level === 'medium' ? '#f59e0b' :
                                        '#10b981'
                                    }
                                />
                            ))}
                        </Bar>
                        <ReferenceLine y={30} stroke="#ef4444" strokeDasharray="3 3" label="High Risk Threshold" />
                        <ReferenceLine y={15} stroke="#f59e0b" strokeDasharray="3 3" label="Medium Risk Threshold" />
                    </BarChart>
                </ResponsiveContainer>
                <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <p className="text-sm text-yellow-800">
                        <strong>Note:</strong> Sector concentration above 30% indicates high risk. 
                        Consider diversifying across different sectors to reduce portfolio risk.
                    </p>
                </div>
            </div>
        </div>
    );
};

