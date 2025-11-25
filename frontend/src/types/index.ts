// User & Auth Types
export interface User {
    id: string
    email: string
    full_name: string
    phone_number?: string
    risk_tolerance: 'conservative' | 'moderate' | 'aggressive'
    email_notifications: boolean
    sms_notifications: boolean
    is_active: boolean
    is_verified: boolean
    created_at: string
    last_login?: string
}

export interface LoginCredentials {
    email: string
    password: string
}

export interface SignupData {
    email: string
    password: string
    full_name: string
    phone_number?: string
}

export interface AuthResponse {
    access_token: string
    token_type: string
}

// Stock Analysis Types
export interface StockAnalysisRequest {
    symbol: string
    market: string
    company_name?: string
    user_risk_tolerance: string
}

export interface TechnicalIndicators {
    ema: {
        ema_9: number
        ema_21: number
        ema_50: number
        current_price: number
        trend: string
        signal: string
    }
    rsi: {
        value: number
        signal: string
        interpretation: string
    }
    macd: {
        macd_line: number
        signal_line: number
        signal: string
    }
    bollinger_bands: {
        upper_band: number
        lower_band: number
        signal: string
    }
    summary: {
        overall_signal: 'buy' | 'sell' | 'hold'
        bullish_indicators: number
        bearish_indicators: number
        confidence: number
    }
}

export interface StockAnalysis {
    id: string
    symbol: string
    market: string
    final_recommendation: {
        action: 'buy' | 'sell' | 'hold'
        confidence: number
        reasoning: string
        risk_assessment: string
    }
    analyses: {
        technical: {
            indicators: TechnicalIndicators
        }
        fundamental: any
        sentiment: any
    }
    created_at: string
}

// Portfolio Types
export interface PortfolioHolding {
    id: number;
    stock: {
        id: number;
        symbol: string;
        company_name: string;
        market: string;
        sector: string | null;
        industry: string | null;
    };
    quantity: number;
    average_buy_price: number;
    total_invested: number;
    current_price: number | null | undefined;
    current_value: number | null | undefined;
    unrealized_pl: number | null;
    unrealized_pl_percentage: number | null;
    realized_pl: number;
    first_buy_date: string;
    last_updated: string;
}

export interface PortfolioMetrics {
    id: number;
    name: string;
    description: string | null;
    total_invested: number;
    current_value: number;
    total_return: number;
    return_percentage: number;
    last_updated: string;
}

export interface PortfolioSummary {
    portfolio: PortfolioMetrics;
    holdings: PortfolioHolding[];
    sector_allocation: Record<string, number>;
    holdings_count: number;
}

export interface AddHoldingRequest {
    symbol: string;
    market: string;
    quantity: number;
    purchase_price: number;
    purchase_date?: string;
    brokerage_fee?: number;
    tax?: number;
    notes?: string;
}

export interface WatchlistStock {
    id: number;
    symbol: string;
    company_name: string;
    market: string;
    sector: string | null;
    industry: string | null;
    current_price: number | null;
}

export interface WatchlistItem {
    id: number;
    stock: WatchlistStock;
    alert_on_price_change: boolean;
    alert_threshold_percent: number;
    alert_on_ai_signal: boolean;
    target_buy_price?: number | null;
    target_sell_price?: number | null;
    notes?: string | null;
    created_at: string;
    updated_at: string;
}

export interface WatchlistListResponse {
    items: WatchlistItem[];
    count: number;
}

export interface WatchlistCreateRequest {
    symbol: string;
    market: string;
    alert_on_price_change?: boolean;
    alert_threshold_percent?: number;
    alert_on_ai_signal?: boolean;
    target_buy_price?: number | null;
    target_sell_price?: number | null;
    notes?: string | null;
}

// Stock Recommendations Types
export interface HistoricalPerformance {
    current_price: number;
    high_52w: number;
    low_52w: number;
    "1d_change": number;  // API returns with alias name
    "7d_change": number;
    "30d_change": number;
    "90d_change": number;
    volatility: number;
}

export interface Forecast {
    price_7d: number;
    price_30d: number;
    expected_change_7d: number;
    expected_change_30d: number;
    confidence: number;
    forecast_basis: string;
}

export interface StockRecommendation {
    symbol: string;
    company_name: string;
    market: string;
    current_price: number;
    score: number;
    recommendation: string;
    confidence: number;
    reasoning: string;
    historical_performance: HistoricalPerformance;
    forecast: Forecast;
    technical_indicators: Record<string, any>;
    fundamental_metrics: Record<string, any>;
    sentiment_score: number;
    risk_level: string;
    price_history: number[];
    analyzed_at: string;
    // AI-powered comparative analysis fields
    rank?: number | null;
    ai_reasoning?: string | null;
    market_context?: string | null;
    comparative_advantages?: string[] | null;
    risk_factors?: string[] | null;
    entry_strategy?: string | null;
    time_horizon?: string | null;
}

export interface RecommendationsResponse {
    period: 'daily' | 'weekly';
    market: string;
    recommendations: StockRecommendation[];
    generated_at: string;
    analysis_metadata: {
        user_risk_tolerance: string;
        stocks_analyzed: number;
        analysis_depth: string;
    };
}
