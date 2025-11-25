import { apiClient } from './client';

export interface BacktestRequest {
    symbol: string;
    market: string;
    start_date: string;
    end_date: string;
    initial_capital: number;
    strategy: {
        type: string;
        [key: string]: any;
    };
    commission?: number;
}

export interface BacktestResponse {
    symbol: string;
    market: string;
    start_date: string;
    end_date: string;
    strategy: any;
    initial_capital: number;
    performance: {
        total_return: number;
        total_return_percent: number;
        sharpe_ratio: number;
        max_drawdown: number;
        max_drawdown_percent: number;
        total_trades: number;
        win_rate: number;
    };
    trades: Array<{
        date: string;
        type: string;
        price: number;
        shares: number;
        cost?: number;
        proceeds?: number;
    }>;
    equity_curve: Array<{
        date: string;
        equity: number;
    }>;
    backtested_at: string;
}

export interface Strategy {
    type: string;
    name: string;
    description: string;
    parameters: Record<string, any>;
}

export const backtestingService = {
    async runBacktest(request: BacktestRequest): Promise<BacktestResponse> {
        const response = await apiClient.post('api/v1/backtesting/run', request);
        return response.data;
    },

    async getStrategies(): Promise<{ strategies: Strategy[] }> {
        const response = await apiClient.get('api/v1/backtesting/strategies');
        return response.data;
    }
};

