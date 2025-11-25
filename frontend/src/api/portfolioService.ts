import { apiClient } from './client'
import { PortfolioSummary, AddHoldingRequest } from '@/types';

export const portfolioService = {
    /**
     * Get complete portfolio summary with holdings and metrics
     */
    async getPortfolioSummary(): Promise<PortfolioSummary> {
        const response = await apiClient.get('/api/v1/portfolio/summary');
        return response.data;
    },

    /**
     * Get all holdings
     */
    async getHoldings() {
        const response = await apiClient.get('/api/v1/portfolio/holdings');
        return response.data;
    },

    /**
     * Add stock to portfolio
     */
    async addHolding(data: AddHoldingRequest) {
        const response = await apiClient.post('/api/v1/portfolio/holdings', data);
        return response.data;
    },

    /**
     * Remove holding from portfolio
     */
    async removeHolding(holdingId: number) {
        const response = await apiClient.delete(`/api/v1/portfolio/holdings/${holdingId}`);
        return response.data;
    },

    /**
     * Refresh portfolio prices
     */
    async refreshPortfolio() {
        const response = await apiClient.post('/api/v1/portfolio/refresh');
        return response.data;
    },
};
