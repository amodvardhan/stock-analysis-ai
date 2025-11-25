import React from 'react';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Cell
} from 'recharts';

interface VolumeData {
    date: string;
    volume: number;
    price: number;
    priceChange: number;
}

interface Props {
    data: VolumeData[];
    height?: number;
}

export const VolumeChart: React.FC<Props> = ({ data, height = 200 }) => {
    const chartData = data.map((item) => ({
        ...item,
        volumeColor: item.priceChange >= 0 ? '#10b981' : '#ef4444',
    }));

    const CustomTooltip = ({ active, payload }: any) => {
        if (active && payload && payload.length) {
            const data = payload[0].payload;
            return (
                <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
                    <p className="font-semibold text-gray-900 mb-2">{data.date}</p>
                    <div className="space-y-1 text-sm">
                        <div className="flex justify-between gap-4">
                            <span className="text-gray-600">Volume:</span>
                            <span className="font-medium">{data.volume.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between gap-4">
                            <span className="text-gray-600">Price:</span>
                            <span className="font-medium">${data.price.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between gap-4">
                            <span className="text-gray-600">Change:</span>
                            <span className={`font-medium ${data.priceChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {data.priceChange >= 0 ? '+' : ''}{data.priceChange.toFixed(2)}%
                            </span>
                        </div>
                    </div>
                </div>
            );
        }
        return null;
    };

    // Calculate average volume for reference line
    const avgVolume = data.reduce((sum, item) => sum + item.volume, 0) / data.length;

    return (
        <div className="w-full">
            <div className="mb-2 flex items-center justify-between">
                <h4 className="text-sm font-semibold text-gray-700">Trading Volume</h4>
                <div className="text-xs text-gray-500">
                    Avg: {avgVolume.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                </div>
            </div>
            <ResponsiveContainer width="100%" height={height}>
                <BarChart data={chartData} margin={{ top: 10, right: 30, left: 20, bottom: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis
                        dataKey="date"
                        stroke="#6b7280"
                        fontSize={11}
                        tickFormatter={(value) => {
                            const date = new Date(value);
                            return `${date.getMonth() + 1}/${date.getDate()}`;
                        }}
                    />
                    <YAxis
                        stroke="#6b7280"
                        fontSize={11}
                        tickFormatter={(value) => {
                            if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
                            if (value >= 1000) return `${(value / 1000).toFixed(1)}K`;
                            return value.toString();
                        }}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar
                        dataKey="volume"
                        radius={[4, 4, 0, 0]}
                        opacity={0.7}
                    >
                        {chartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.volumeColor} />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
            <div className="mt-2 flex items-center gap-4 text-xs text-gray-500">
                <div className="flex items-center gap-1">
                    <div className="w-3 h-3 bg-green-500 rounded"></div>
                    <span>Price Up</span>
                </div>
                <div className="flex items-center gap-1">
                    <div className="w-3 h-3 bg-red-500 rounded"></div>
                    <span>Price Down</span>
                </div>
            </div>
        </div>
    );
};

