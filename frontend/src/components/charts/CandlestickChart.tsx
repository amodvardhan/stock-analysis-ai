import React from 'react';
import {
    ComposedChart,
    Line,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    ReferenceLine,
    Cell
} from 'recharts';

interface CandlestickData {
    date: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
}

interface Props {
    data: CandlestickData[];
    height?: number;
    showVolume?: boolean;
}

export const CandlestickChart: React.FC<Props> = ({ data, height = 400, showVolume = true }) => {
    // Transform data for candlestick visualization
    const chartData = data.map((item) => ({
        ...item,
        // For candlestick visualization
        body: Math.abs(item.close - item.open),
        isPositive: item.close >= item.open,
        // Volume bar color based on price movement
        volumeColor: item.close >= item.open ? '#10b981' : '#ef4444',
    }));

    const CustomTooltip = ({ active, payload }: any) => {
        if (active && payload && payload.length) {
            const data = payload[0].payload;
            return (
                <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg">
                    <p className="font-semibold text-gray-900 mb-2">{data.date}</p>
                    <div className="space-y-1 text-sm">
                        <div className="flex justify-between gap-4">
                            <span className="text-gray-600">Open:</span>
                            <span className="font-medium">${data.open.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between gap-4">
                            <span className="text-gray-600">High:</span>
                            <span className="font-medium text-green-600">${data.high.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between gap-4">
                            <span className="text-gray-600">Low:</span>
                            <span className="font-medium text-red-600">${data.low.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between gap-4">
                            <span className="text-gray-600">Close:</span>
                            <span className={`font-medium ${data.isPositive ? 'text-green-600' : 'text-red-600'}`}>
                                ${data.close.toFixed(2)}
                            </span>
                        </div>
                        {showVolume && (
                            <div className="flex justify-between gap-4 pt-2 border-t">
                                <span className="text-gray-600">Volume:</span>
                                <span className="font-medium">{data.volume.toLocaleString()}</span>
                            </div>
                        )}
                        <div className="flex justify-between gap-4">
                            <span className="text-gray-600">Change:</span>
                            <span className={`font-medium ${data.isPositive ? 'text-green-600' : 'text-red-600'}`}>
                                {data.isPositive ? '+' : ''}
                                {((data.close - data.open) / data.open * 100).toFixed(2)}%
                            </span>
                        </div>
                    </div>
                </div>
            );
        }
        return null;
    };

    return (
        <div className="w-full">
            <ResponsiveContainer width="100%" height={height}>
                <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis
                        dataKey="date"
                        stroke="#6b7280"
                        fontSize={12}
                        tickFormatter={(value) => {
                            const date = new Date(value);
                            return `${date.getMonth() + 1}/${date.getDate()}`;
                        }}
                    />
                    <YAxis
                        yId="price"
                        orientation="left"
                        stroke="#6b7280"
                        fontSize={12}
                        domain={['auto', 'auto']}
                        tickFormatter={(value) => `$${value.toFixed(0)}`}
                    />
                    {showVolume && (
                        <YAxis
                            yId="volume"
                            orientation="right"
                            stroke="#9ca3af"
                            fontSize={12}
                            tickFormatter={(value) => {
                                if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
                                if (value >= 1000) return `${(value / 1000).toFixed(1)}K`;
                                return value.toString();
                            }}
                        />
                    )}
                    <Tooltip content={<CustomTooltip />} />
                    <ReferenceLine y={0} stroke="#9ca3af" strokeDasharray="2 2" />

                    {/* Candlestick body (open-close) */}
                    <Bar
                        yId="price"
                        dataKey="body"
                        fill="#10b981"
                        baseValue={(item: any) => Math.min(item.open, item.close)}
                    >
                        {chartData.map((entry, index) => (
                            <Cell
                                key={`cell-${index}`}
                                fill={entry.isPositive ? '#10b981' : '#ef4444'}
                            />
                        ))}
                    </Bar>

                    {/* High-Low wicks */}
                    <Line
                        yId="price"
                        type="monotone"
                        dataKey="high"
                        stroke="#10b981"
                        strokeWidth={1}
                        dot={false}
                        connectNulls
                    />
                    <Line
                        yId="price"
                        type="monotone"
                        dataKey="low"
                        stroke="#ef4444"
                        strokeWidth={1}
                        dot={false}
                        connectNulls
                    />

                    {/* Volume bars */}
                    {showVolume && (
                        <Bar
                            yId="volume"
                            dataKey="volume"
                            fill="#9ca3af"
                            opacity={0.3}
                            radius={[2, 2, 0, 0]}
                        >
                            {chartData.map((entry, index) => (
                                <Cell key={`volume-cell-${index}`} fill={entry.volumeColor} />
                            ))}
                        </Bar>
                    )}
                </ComposedChart>
            </ResponsiveContainer>
        </div>
    );
};

