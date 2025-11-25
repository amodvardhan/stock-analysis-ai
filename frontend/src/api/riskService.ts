import { apiClient } from './client';

export interface CVaRRequest {
    returns: number[];
    confidence_level?: number;
}

export interface CVaRResponse {
    var: number;
    cvar: number;
    expected_shortfall: number;
    confidence_level: number;
    calculated_at: string;
}

export interface PortfolioRiskResponse {
    total_portfolio_value: number;
    sector_allocation: Record<string, number>;
    concentration_risk: number;
    diversification_score: number;
    portfolio_volatility: number;
    cvar_95: number;
    max_drawdown: number;
    risk_level: string;
    calculated_at: string;
}

export interface StopLossRequest {
    entry_price: number;
    risk_tolerance?: 'conservative' | 'moderate' | 'aggressive';
    volatility?: number;
}

export interface StopLossResponse {
    entry_price: number;
    stop_loss_price: number;
    stop_loss_percentage: number;
    risk_tolerance: string;
    recommended_action: string;
    calculated_at: string;
}

export const riskService = {
    async calculateCVaR(request: CVaRRequest): Promise<CVaRResponse> {
        const response = await apiClient.post('api/v1/risk/cvar', request);
        return response.data;
    },

    async getPortfolioRisk(portfolioId: number): Promise<PortfolioRiskResponse> {
        const response = await apiClient.get(`api/v1/risk/portfolio/${portfolioId}`);
        return response.data;
    },

    async calculateStopLoss(request: StopLossRequest): Promise<StopLossResponse> {
        const response = await apiClient.post('api/v1/risk/stop-loss', request);
        return response.data;
    },

    async checkRiskLimits(request: {
        portfolio_value: number;
        order_value: number;
        user_risk_tolerance: string;
    }): Promise<{
        is_within_limits: boolean;
        position_size_percentage: number;
        max_allowed_percentage: number;
        recommendation: string;
    }> {
        const response = await apiClient.post('api/v1/risk/check-limits', request);
        return response.data;
    }
};

