"""
=============================================================================
Advanced Risk Management Service
=============================================================================
Dynamic risk protocols, CVaR models, and stop-loss triggers.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import numpy as np
import structlog

logger = structlog.get_logger()


class RiskManagementService:
    """Advanced risk management service."""
    
    @staticmethod
    def calculate_cvar(
        returns: List[float],
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """
        Calculate Conditional Value at Risk (CVaR).
        
        Args:
            returns: List of historical returns
            confidence_level: Confidence level (default 0.95 for 95%)
        
        Returns:
            CVaR metrics
        """
        try:
            if not returns or len(returns) < 10:
                return {
                    "error": "Insufficient data for CVaR calculation",
                    "min_required": 10
                }
            
            returns_array = np.array(returns)
            
            # Calculate VaR (Value at Risk)
            var = np.percentile(returns_array, (1 - confidence_level) * 100)
            
            # Calculate CVaR (average of losses beyond VaR)
            cvar = returns_array[returns_array <= var].mean()
            
            # Calculate expected shortfall
            expected_shortfall = abs(cvar) if cvar < 0 else 0
            
            return {
                "var": float(var),
                "cvar": float(cvar),
                "expected_shortfall": float(expected_shortfall),
                "confidence_level": confidence_level,
                "calculated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("cvar_calculation_error", error=str(e))
            return {"error": str(e)}
    
    @staticmethod
    def calculate_portfolio_risk(
        holdings: List[Dict[str, Any]],
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive portfolio risk metrics.
        
        Args:
            holdings: List of portfolio holdings
            market_data: Market data for risk calculations
        
        Returns:
            Portfolio risk metrics
        """
        try:
            total_value = sum(h.get("current_value", 0) for h in holdings)
            
            # Calculate sector concentration
            sector_allocation = {}
            for holding in holdings:
                sector = holding.get("sector", "Unknown")
                value = holding.get("current_value", 0)
                sector_allocation[sector] = sector_allocation.get(sector, 0) + value
            
            # Calculate concentration risk
            max_sector_allocation = max(sector_allocation.values()) if sector_allocation else 0
            concentration_risk = (max_sector_allocation / total_value * 100) if total_value > 0 else 0
            
            # Calculate diversification score
            num_sectors = len(sector_allocation)
            num_holdings = len(holdings)
            diversification_score = min(100, (num_sectors / 10 * 50) + (num_holdings / 20 * 50))
            
            # Calculate portfolio volatility
            returns = [h.get("return_percentage", 0) / 100 for h in holdings if h.get("return_percentage")]
            portfolio_volatility = np.std(returns) if returns else 0
            
            # Calculate CVaR
            cvar_result = RiskManagementService.calculate_cvar(returns) if returns else {}
            
            # Calculate max drawdown
            values = [h.get("current_value", 0) for h in holdings]
            max_drawdown = RiskManagementService._calculate_max_drawdown(values)
            
            return {
                "total_portfolio_value": total_value,
                "sector_allocation": {k: (v / total_value * 100) for k, v in sector_allocation.items()},
                "concentration_risk": concentration_risk,
                "diversification_score": diversification_score,
                "portfolio_volatility": portfolio_volatility,
                "cvar_95": cvar_result.get("cvar", 0),
                "max_drawdown": max_drawdown,
                "risk_level": RiskManagementService._determine_risk_level(
                    concentration_risk,
                    portfolio_volatility,
                    max_drawdown
                ),
                "calculated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("portfolio_risk_calculation_error", error=str(e))
            return {"error": str(e)}
    
    @staticmethod
    def _calculate_max_drawdown(values: List[float]) -> float:
        """Calculate maximum drawdown."""
        if not values or len(values) < 2:
            return 0.0
        
        peak = values[0]
        max_dd = 0.0
        
        for value in values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak if peak > 0 else 0
            if drawdown > max_dd:
                max_dd = drawdown
        
        return max_dd * 100  # Return as percentage
    
    @staticmethod
    def _determine_risk_level(
        concentration_risk: float,
        volatility: float,
        max_drawdown: float
    ) -> str:
        """Determine overall risk level."""
        risk_score = 0
        
        if concentration_risk > 40:
            risk_score += 40
        elif concentration_risk > 25:
            risk_score += 20
        
        if volatility > 0.3:
            risk_score += 30
        elif volatility > 0.15:
            risk_score += 15
        
        if max_drawdown > 30:
            risk_score += 30
        elif max_drawdown > 15:
            risk_score += 15
        
        if risk_score >= 70:
            return "very_high"
        elif risk_score >= 50:
            return "high"
        elif risk_score >= 30:
            return "moderate"
        else:
            return "low"
    
    @staticmethod
    def calculate_stop_loss(
        entry_price: float,
        risk_tolerance: str = "moderate",
        volatility: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculate optimal stop-loss price.
        
        Args:
            entry_price: Entry price
            risk_tolerance: User's risk tolerance
            volatility: Stock volatility (optional)
        
        Returns:
            Stop-loss recommendations
        """
        try:
            # Base stop-loss percentages by risk tolerance
            base_stops = {
                "conservative": 0.03,  # 3%
                "moderate": 0.05,      # 5%
                "aggressive": 0.08     # 8%
            }
            
            base_percentage = base_stops.get(risk_tolerance, 0.05)
            
            # Adjust based on volatility
            if volatility:
                if volatility > 0.3:
                    base_percentage *= 1.5  # Wider stop for volatile stocks
                elif volatility < 0.1:
                    base_percentage *= 0.7  # Tighter stop for stable stocks
            
            stop_loss_price = entry_price * (1 - base_percentage)
            stop_loss_percentage = base_percentage * 100
            
            return {
                "entry_price": entry_price,
                "stop_loss_price": stop_loss_price,
                "stop_loss_percentage": stop_loss_percentage,
                "risk_tolerance": risk_tolerance,
                "recommended_action": "Set stop-loss order at calculated price",
                "calculated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("stop_loss_calculation_error", error=str(e))
            return {"error": str(e)}
    
    @staticmethod
    def check_risk_limits(
        portfolio_value: float,
        order_value: float,
        user_risk_tolerance: str
    ) -> Dict[str, Any]:
        """
        Check if order violates risk limits.
        
        Args:
            portfolio_value: Total portfolio value
            order_value: Value of the order
            user_risk_tolerance: User's risk tolerance
        
        Returns:
            Risk check result
        """
        try:
            # Calculate position size as percentage of portfolio
            position_size = (order_value / portfolio_value * 100) if portfolio_value > 0 else 0
            
            # Risk limits by tolerance
            limits = {
                "conservative": 5,   # Max 5% per position
                "moderate": 10,       # Max 10% per position
                "aggressive": 20     # Max 20% per position
            }
            
            max_position_size = limits.get(user_risk_tolerance, 10)
            
            is_within_limits = position_size <= max_position_size
            
            return {
                "is_within_limits": is_within_limits,
                "position_size_percentage": position_size,
                "max_allowed_percentage": max_position_size,
                "risk_tolerance": user_risk_tolerance,
                "recommendation": "Proceed" if is_within_limits else "Reduce position size",
                "checked_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("risk_limit_check_error", error=str(e))
            return {"error": str(e)}

