import { apiClient } from './client'
import { WatchlistListResponse, WatchlistCreateRequest } from '@/types';

export const watchlistService = {
    /**
     * Get all watchlist items
     */
    async getWatchlist(): Promise<WatchlistListResponse> {
        const response = await apiClient.get('/api/v1/watchlist/');
        return response.data;
    },

    /**
     * Add or update stock in watchlist
     */
    async addOrUpdate(item: WatchlistCreateRequest) {
        const response = await apiClient.post('/api/v1/watchlist/', item);
        return response.data;
    },

    /**
     * Remove stock from watchlist
     */
    async remove(id: number) {
        const response = await apiClient.delete(`/api/v1/watchlist/${id}`);
        return response.data;
    },
};
