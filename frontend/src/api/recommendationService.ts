import { apiClient } from './client'
import { RecommendationsResponse } from '@/types';

export const recommendationService = {
    /**
     * Get top 5 stocks of the day
     */
    async getDailyRecommendations(market: string = 'india_nse'): Promise<RecommendationsResponse> {
        const response = await apiClient.get('/api/v1/recommendations/daily', {
            params: { market, limit: 5 }
        });
        return response.data;
    },

    /**
     * Get top 5 stocks of the week
     */
    async getWeeklyRecommendations(market: string = 'india_nse'): Promise<RecommendationsResponse> {
        const response = await apiClient.get('/api/v1/recommendations/weekly', {
            params: { market, limit: 5 }
        });
        return response.data;
    },
};

