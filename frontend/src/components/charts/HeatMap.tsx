import React, { useMemo } from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface HeatMapData {
    symbol: string;
    company_name: string;
    sector?: string;
    change_percent: number;
    volume?: number;
    market_cap?: number;
}

interface Props {
    data: HeatMapData[];
    groupBy?: 'sector' | 'market';
    sizeBy?: 'volume' | 'market_cap' | 'none';
    height?: number;
}

export const HeatMap: React.FC<Props> = ({
    data,
    groupBy = 'sector',
    sizeBy = 'market_cap',
    height = 600
}) => {
    // Group data by sector or market
    const groupedData = useMemo(() => {
        const groups: Record<string, HeatMapData[]> = {};

        data.forEach((item) => {
            const key = groupBy === 'sector'
                ? (item.sector || 'Unknown')
                : 'All';

            if (!groups[key]) {
                groups[key] = [];
            }
            groups[key].push(item);
        });

        return groups;
    }, [data, groupBy]);

    // Get color based on change percentage
    const getColor = (changePercent: number): string => {
        if (changePercent > 5) return 'bg-green-600';
        if (changePercent > 2) return 'bg-green-500';
        if (changePercent > 0) return 'bg-green-400';
        if (changePercent > -2) return 'bg-red-400';
        if (changePercent > -5) return 'bg-red-500';
        return 'bg-red-600';
    };

    // Get text color based on change percentage
    const getTextColor = (changePercent: number): string => {
        return changePercent >= 0 ? 'text-white' : 'text-white';
    };

    // Get size based on volume or market cap
    const getSize = (item: HeatMapData): string => {
        if (sizeBy === 'none') return 'w-24 h-24';

        let value = 0;
        if (sizeBy === 'volume' && item.volume) {
            value = item.volume;
        } else if (sizeBy === 'market_cap' && item.market_cap) {
            value = item.market_cap;
        }

        // Normalize to size classes
        if (value > 1000000000) return 'w-32 h-32 text-lg'; // Large
        if (value > 100000000) return 'w-28 h-28 text-base'; // Medium
        if (value > 10000000) return 'w-24 h-24 text-sm'; // Small
        return 'w-20 h-20 text-xs'; // Extra small
    };

    // Get icon based on change
    const getIcon = (changePercent: number) => {
        if (changePercent > 0) return <TrendingUp className="w-4 h-4" />;
        if (changePercent < 0) return <TrendingDown className="w-4 h-4" />;
        return <Minus className="w-4 h-4" />;
    };

    return (
        <div className="w-full space-y-6">
            {Object.entries(groupedData).map(([group, items]) => (
                <div key={group} className="space-y-3">
                    <h3 className="text-lg font-semibold text-gray-900 capitalize">
                        {group} ({items.length} stocks)
                    </h3>
                    <div
                        className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3"
                        style={{ maxHeight: `${height}px`, overflowY: 'auto' }}
                    >
                        {items.map((item) => (
                            <div
                                key={item.symbol}
                                className={`${getColor(item.change_percent)} ${getTextColor(item.change_percent)} ${getSize(item)} rounded-lg p-3 flex flex-col items-center justify-center cursor-pointer hover:scale-105 transition-transform shadow-md`}
                                title={`${item.company_name} - ${item.change_percent.toFixed(2)}%`}
                            >
                                <div className="font-bold text-xs mb-1 truncate w-full text-center">
                                    {item.symbol}
                                </div>
                                <div className="flex items-center gap-1 mb-1">
                                    {getIcon(item.change_percent)}
                                    <span className="font-semibold text-xs">
                                        {item.change_percent >= 0 ? '+' : ''}
                                        {item.change_percent.toFixed(1)}%
                                    </span>
                                </div>
                                {item.company_name && (
                                    <div className="text-xs opacity-80 truncate w-full text-center">
                                        {item.company_name.length > 15
                                            ? `${item.company_name.substring(0, 15)}...`
                                            : item.company_name}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            ))}

            {/* Legend */}
            <div className="flex items-center gap-6 p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-gray-700">Performance:</span>
                    <div className="flex items-center gap-1">
                        <div className="w-4 h-4 bg-red-600 rounded"></div>
                        <span className="text-xs text-gray-600">&lt; -5%</span>
                    </div>
                    <div className="flex items-center gap-1">
                        <div className="w-4 h-4 bg-red-400 rounded"></div>
                        <span className="text-xs text-gray-600">-2% to -5%</span>
                    </div>
                    <div className="flex items-center gap-1">
                        <div className="w-4 h-4 bg-green-400 rounded"></div>
                        <span className="text-xs text-gray-600">0% to 2%</span>
                    </div>
                    <div className="flex items-center gap-1">
                        <div className="w-4 h-4 bg-green-500 rounded"></div>
                        <span className="text-xs text-gray-600">2% to 5%</span>
                    </div>
                    <div className="flex items-center gap-1">
                        <div className="w-4 h-4 bg-green-600 rounded"></div>
                        <span className="text-xs text-gray-600">&gt; 5%</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

