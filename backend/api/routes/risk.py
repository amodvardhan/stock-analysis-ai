"""
=============================================================================
Risk Management API Routes
=============================================================================
Endpoints for portfolio risk analysis and management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
from pydantic import BaseModel
import structlog

from core.database import get_db
from db.models import User
from api.routes.auth import get_current_user
from services.risk_management_service import RiskManagementService
from services.portfolio_service import PortfolioService

logger = structlog.get_logger()
router = APIRouter()


class CVaRRequest(BaseModel):
    returns: List[float]
    confidence_level: float = 0.95


class StopLossRequest(BaseModel):
    entry_price: float
    risk_tolerance: str = "moderate"
    volatility: float = None


class RiskLimitCheckRequest(BaseModel):
    portfolio_value: float
    order_value: float
    user_risk_tolerance: str


@router.post("/cvar")
async def calculate_cvar(
    request: CVaRRequest,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Calculate Conditional Value at Risk (CVaR)."""
    try:
        result = RiskManagementService.calculate_cvar(
            returns=request.returns,
            confidence_level=request.confidence_level
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("cvar_calculation_error", user_id=str(current_user.id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"CVaR calculation failed: {str(e)}"
        )


@router.get("/portfolio/{portfolio_id}")
async def get_portfolio_risk(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get comprehensive portfolio risk metrics."""
    try:
        # Get portfolio holdings
        holdings_data = await PortfolioService.get_portfolio_holdings(
            db=db,
            portfolio_id=portfolio_id
        )
        
        # Prepare holdings for risk calculation
        holdings = [
            {
                "current_value": h.get("current_value", 0),
                "sector": h.get("stock", {}).get("sector", "Unknown"),
                "return_percentage": h.get("unrealized_pl_percentage", 0) or 0
            }
            for h in holdings_data
        ]
        
        # Get market data (simplified - would fetch actual market data)
        market_data = {}
        
        result = RiskManagementService.calculate_portfolio_risk(
            holdings=holdings,
            market_data=market_data
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("portfolio_risk_error", user_id=str(current_user.id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Portfolio risk calculation failed: {str(e)}"
        )


@router.post("/stop-loss")
async def calculate_stop_loss(
    request: StopLossRequest,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Calculate optimal stop-loss price."""
    try:
        result = RiskManagementService.calculate_stop_loss(
            entry_price=request.entry_price,
            risk_tolerance=request.risk_tolerance,
            volatility=request.volatility
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("stop_loss_calculation_error", user_id=str(current_user.id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stop-loss calculation failed: {str(e)}"
        )


@router.post("/check-limits")
async def check_risk_limits(
    request: RiskLimitCheckRequest,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Check if order violates risk limits."""
    try:
        result = RiskManagementService.check_risk_limits(
            portfolio_value=request.portfolio_value,
            order_value=request.order_value,
            user_risk_tolerance=request.user_risk_tolerance
        )
        
        return result
        
    except Exception as e:
        logger.error("risk_limit_check_error", user_id=str(current_user.id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Risk limit check failed: {str(e)}"
        )

