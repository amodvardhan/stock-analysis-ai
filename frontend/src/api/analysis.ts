import { apiClient } from './client'
import type { StockAnalysisRequest, StockAnalysis } from '@/types'

export const analysisAPI = {
    async analyzeStock(request: StockAnalysisRequest): Promise<StockAnalysis> {
        const { data } = await apiClient.post('/api/v1/analysis/analyze', request)
        return data
    },

    async getAnalysisHistory(): Promise<StockAnalysis[]> {
        const { data } = await apiClient.get('/api/v1/analysis/history')
        return data
    },

    async getAnalysisById(id: string): Promise<StockAnalysis> {
        const { data } = await apiClient.get(`/api/v1/analysis/${id}`)
        return data
    },
}
