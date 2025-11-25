"""
=============================================================================
AI Hub - Stock Analysis Pydantic Schemas
=============================================================================
Request and response models for stock analysis endpoints.
=============================================================================
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class StockAnalysisRequest(BaseModel):
    """Request schema for stock analysis."""
    symbol: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Stock ticker symbol (e.g., RELIANCE, AAPL)",
        examples=["RELIANCE", "AAPL", "TCS"]
    )
    market: str = Field(
        default="india_nse",
        pattern="^(india_nse|india_bse|us_nyse|us_nasdaq)$",
        description="Stock market"
    )
    company_name: Optional[str] = Field(
        None,
        description="Full company name (improves sentiment analysis)"
    )
    user_risk_tolerance: str = Field(
        default="moderate",
        pattern="^(conservative|moderate|aggressive)$",
        description="User's risk tolerance"
    )


class StockAnalysisResponse(BaseModel):
    """Response schema for stock analysis."""
    symbol: str
    market: str
    final_recommendation: Dict[str, Any]
    analyses: Dict[str, Any]
    metadata: Dict[str, Any]


class WatchlistAddRequest(BaseModel):
    """Request to add stock to watchlist."""
    symbol: str = Field(..., min_length=1, max_length=20)
    market: str = Field(default="india_nse")
    alert_on_price_change: bool = Field(default=True, description="Enable price change alerts")
    alert_threshold_percent: float = Field(
        default=5.0,
        ge=0.1,
        le=50.0,
        description="Price change % that triggers alert"
    )
    alert_on_ai_signal: bool = Field(default=True, description="Enable AI signal alerts")
    target_buy_price: Optional[float] = Field(None, gt=0)
    target_sell_price: Optional[float] = Field(None, gt=0)
    notes: Optional[str] = Field(None, max_length=1000)


class WatchlistStockResponse(BaseModel):
    """Stock information in watchlist response."""
    id: int
    symbol: str
    company_name: str
    market: str
    sector: Optional[str]
    industry: Optional[str]
    current_price: Optional[float]
    
    model_config = ConfigDict(from_attributes=True)


class WatchlistResponse(BaseModel):
    """Response schema for watchlist item."""
    id: int
    stock: WatchlistStockResponse
    alert_on_price_change: bool
    alert_threshold_percent: float
    alert_on_ai_signal: bool
    target_buy_price: Optional[float]
    target_sell_price: Optional[float]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class WatchlistListResponse(BaseModel):
    """Response schema for watchlist list."""
    items: List[WatchlistResponse]
    count: int


class PortfolioAddRequest(BaseModel):
    """Request to add stock to portfolio."""
    symbol: str = Field(..., min_length=1, max_length=20)
    market: str = Field(default="india_nse")
    quantity: float = Field(..., gt=0, description="Number of shares")
    purchase_price: float = Field(..., gt=0, description="Price per share")
    purchase_date: datetime = Field(default_factory=datetime.utcnow)


class PortfolioResponse(BaseModel):
    """Response schema for portfolio holding."""
    id: int
    symbol: str
    company_name: str
    quantity: float
    purchase_price: float
    current_price: Optional[float]
    current_value: Optional[float]
    profit_loss: Optional[float]
    profit_loss_percent: Optional[float]
    purchase_date: datetime
    
    model_config = ConfigDict(from_attributes=True)
