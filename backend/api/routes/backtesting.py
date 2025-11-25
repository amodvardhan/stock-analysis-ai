"""
=============================================================================
Backtesting API Routes
=============================================================================
Endpoints for testing trading strategies against historical data.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import structlog

from core.database import get_db
from db.models import User
from api.routes.auth import get_current_user
from services.backtesting_service import BacktestingService

logger = structlog.get_logger()
router = APIRouter()


class BacktestRequest(BaseModel):
    symbol: str
    market: str
    start_date: str
    end_date: str
    initial_capital: float
    strategy: Dict[str, Any]
    commission: Optional[float] = 0.001


class BacktestResponse(BaseModel):
    symbol: str
    market: str
    start_date: str
    end_date: str
    strategy: Dict[str, Any]
    initial_capital: float
    performance: Dict[str, Any]
    trades: List[Dict[str, Any]]
    equity_curve: List[Dict[str, Any]]
    backtested_at: str


@router.post("/run", response_model=BacktestResponse)
async def run_backtest(
    request: BacktestRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> BacktestResponse:
    """
    Run a backtest for a trading strategy.
    
    Request body:
    - symbol: Stock symbol
    - market: Market identifier
    - start_date: Start date (YYYY-MM-DD)
    - end_date: End date (YYYY-MM-DD)
    - initial_capital: Starting capital
    - strategy: Strategy configuration
    - commission: Trading commission rate (optional)
    """
    try:
        logger.info(
            "backtest_requested",
            user_id=str(current_user.id),
            symbol=request.symbol,
            market=request.market,
            start_date=request.start_date,
            end_date=request.end_date,
            strategy=request.strategy.get("type")
        )
        
        # Validate dates
        from datetime import datetime
        try:
            start_dt = datetime.strptime(request.start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(request.end_date, "%Y-%m-%d")
            if start_dt >= end_dt:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Start date must be before end date"
                )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid date format. Use YYYY-MM-DD: {str(e)}"
            )
        
        # Validate strategy
        if not request.strategy or "type" not in request.strategy:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Strategy must include a 'type' field"
            )
        
        result = await BacktestingService.backtest_strategy(
            symbol=request.symbol,
            market=request.market,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital,
            strategy=request.strategy,
            commission=request.commission or 0.001
        )
        
        if "error" in result:
            logger.warning(
                "backtest_failed",
                user_id=str(current_user.id),
                symbol=request.symbol,
                error=result["error"]
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return BacktestResponse(**result)
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error("backtest_validation_error", user_id=str(current_user.id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        logger.error("backtest_error", user_id=str(current_user.id), error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Backtest failed: {str(e)}"
        )


@router.get("/strategies")
async def get_available_strategies(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get list of available backtesting strategies."""
    return {
        "strategies": [
            {
                "type": "simple_momentum",
                "name": "Simple Momentum",
                "description": "Buy when price increases by threshold, sell when it decreases",
                "parameters": {
                    "lookback_period": {"type": "integer", "default": 20, "min": 5, "max": 100},
                    "entry_threshold": {"type": "float", "default": 0.02, "min": 0.01, "max": 0.1}
                }
            },
            {
                "type": "mean_reversion",
                "name": "Mean Reversion",
                "description": "Buy when price is below mean (oversold), sell when it returns to mean",
                "parameters": {
                    "lookback_period": {"type": "integer", "default": 20, "min": 5, "max": 100},
                    "std_threshold": {"type": "float", "default": 2.0, "min": 1.0, "max": 3.0}
                }
            },
            {
                "type": "rsi_strategy",
                "name": "RSI Strategy",
                "description": "Buy when RSI < oversold level, sell when RSI > overbought level",
                "parameters": {
                    "oversold_level": {"type": "integer", "default": 30, "min": 20, "max": 40},
                    "overbought_level": {"type": "integer", "default": 70, "min": 60, "max": 80}
                }
            }
        ]
    }

