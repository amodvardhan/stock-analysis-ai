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
    id: number
    symbol: string
    company_name: string
    quantity: number
    purchase_price: number
    current_price?: number
    current_value?: number
    profit_loss?: number
    profit_loss_percent?: number
    purchase_date: string
}

export interface PortfolioSummary {
    total_holdings: number
    total_invested: number
    current_value: number
    total_profit_loss: number
    total_profit_loss_percent: number
    best_performer?: PortfolioHolding
    worst_performer?: PortfolioHolding
}

// Watchlist Types
export interface WatchlistItem {
    id: number
    symbol: string
    company_name: string
    current_price?: number
    alert_threshold_percent: number
    target_buy_price?: number
    target_sell_price?: number
    notes?: string
    created_at: string
}
