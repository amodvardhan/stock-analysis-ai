import { apiClient } from './client'

export interface MarketOverview {
    market: string
    timestamp: string
    indices: Record<string, {
        value: number
        change: number
        change_percent: number
        status: string
    }>
    sectors: Record<string, {
        performance: number
        top_gainers: any[]
        top_losers: any[]
        avg_change: number
    }>
    statistics: {
        total_stocks: number
        advancing: number
        declining: number
        unchanged: number
        total_volume: number
        market_cap: number
    }
    ai_insights: string
    overall_sentiment: string
}

export interface MarketMover {
    symbol: string
    company_name: string
    current_price: number
    previous_close: number
    change: number
    change_percent: number
    volume: number
    market_cap: number
}

export interface MarketMovers {
    market: string
    movers_type: string
    timestamp: string
    gainers: MarketMover[]
    losers: MarketMover[]
    most_active: MarketMover[]
    volume_leaders: MarketMover[]
    insights: string
}

export interface SectorAnalysis {
    market: string
    sector?: string
    timestamp: string
    sectors?: Record<string, any>
    sector_data?: any
    comparison?: {
        best_performer: string
        worst_performer: string
        ranking: Array<{
            sector: string
            performance: number
            rank: number
        }>
    }
    insights: string
}

export interface NewsItem {
    title: string
    source: string
    published_at: string
    url: string
    summary: string
    sentiment: {
        label: 'positive' | 'negative' | 'neutral'
        score: number
        key_points: string[]
        market_impact: 'high' | 'medium' | 'low'
    }
}

export interface NewsResponse {
    symbol?: string
    market?: string
    timestamp: string
    news_items: NewsItem[]
    summary: {
        total_news: number
        positive_count: number
        negative_count: number
        neutral_count: number
        overall_sentiment: string
    }
    insights: string
}

export const marketService = {
    async getMarketOverview(
        market: string = 'india_nse',
        includeSectors: boolean = true,
        includeIndices: boolean = true
    ): Promise<MarketOverview> {
        const response = await apiClient.get('/api/v1/market/overview', {
            params: { market, include_sectors: includeSectors, include_indices: includeIndices }
        })
        return response.data
    },

    async getMarketMovers(
        market: string = 'india_nse',
        moversType: string = 'all',
        limit: number = 20
    ): Promise<MarketMovers> {
        const response = await apiClient.get('/api/v1/market/movers', {
            params: { market, movers_type: moversType, limit }
        })
        return response.data
    },

    async getSectorAnalysis(
        market: string = 'india_nse',
        sector?: string,
        compareSectors: boolean = false
    ): Promise<SectorAnalysis> {
        const response = await apiClient.get('/api/v1/market/sectors', {
            params: { market, sector, compare_sectors: compareSectors }
        })
        return response.data
    },

    async getNews(
        symbol?: string,
        market?: string,
        limit: number = 10,
        daysBack: number = 7
    ): Promise<NewsResponse> {
        const response = await apiClient.get('/api/v1/market/news', {
            params: { symbol, market, limit, days_back: daysBack }
        })
        return response.data
    },

    async getOptionsChain(
        symbol: string,
        market: string = 'india_nse',
        expirationDate?: string
    ): Promise<any> {
        const response = await apiClient.get(`/api/v1/market/options/${symbol}`, {
            params: { market, expiration_date: expirationDate }
        })
        return response.data
    },

    async getFinancialAnalysis(
        symbol: string,
        market: string = 'india_nse'
    ): Promise<any> {
        const response = await apiClient.get(`/api/v1/market/financials/${symbol}`, {
            params: { market }
        })
        return response.data
    },

    async compareStocks(
        symbols: string[],
        market: string = 'india_nse'
    ): Promise<any> {
        const response = await apiClient.post('/api/v1/market/compare', { symbols }, {
            params: { market }
        })
        return response.data
    },

    async getCorporateActions(
        symbol: string,
        market: string = 'india_nse',
        actionType: string = 'all'
    ): Promise<any> {
        const response = await apiClient.get(`/api/v1/market/corporate-actions/${symbol}`, {
            params: { market, action_type: actionType }
        })
        return response.data
    },

    async getEarningsCalendar(
        market: string = 'india_nse',
        daysAhead: number = 30
    ): Promise<any> {
        const response = await apiClient.get('/api/v1/market/earnings', {
            params: { market, days_ahead: daysAhead }
        })
        return response.data
    },

    async getIPOCalendar(
        market: string = 'india_nse',
        daysAhead: number = 90
    ): Promise<any> {
        const response = await apiClient.get('/api/v1/market/ipos', {
            params: { market, days_ahead: daysAhead }
        })
        return response.data
    }
}

