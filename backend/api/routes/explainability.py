"""
=============================================================================
AI Explainability API Routes
=============================================================================
Endpoints for getting detailed explanations of AI recommendations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from pydantic import BaseModel
import structlog

from core.database import get_db
from db.models import User
from api.routes.auth import get_current_user
from services.explainability_service import ExplainabilityService

logger = structlog.get_logger()
router = APIRouter()


class ExplanationRequest(BaseModel):
    recommendation: Dict[str, Any]
    technical_analysis: Dict[str, Any]
    fundamental_analysis: Dict[str, Any]
    sentiment_analysis: Dict[str, Any]


@router.post("/explain")
async def explain_recommendation(
    request: ExplanationRequest,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get detailed explanation for an AI recommendation."""
    try:
        logger.info(
            "explanation_requested",
            user_id=str(current_user.id),
            recommendation=request.recommendation.get("action")
        )
        
        explanation = ExplainabilityService.explain_recommendation(
            recommendation=request.recommendation,
            technical_analysis=request.technical_analysis,
            fundamental_analysis=request.fundamental_analysis,
            sentiment_analysis=request.sentiment_analysis
        )
        
        if "error" in explanation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=explanation["error"]
            )
        
        return explanation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("explanation_error", user_id=str(current_user.id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Explanation generation failed: {str(e)}"
        )


@router.get("/features")
async def get_feature_importance(
    recommendation: Dict[str, Any],
    technical_analysis: Dict[str, Any],
    fundamental_analysis: Dict[str, Any],
    sentiment_analysis: Dict[str, Any],
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get feature importance scores for a recommendation."""
    try:
        explanation = ExplainabilityService.explain_recommendation(
            recommendation=recommendation,
            technical_analysis=technical_analysis,
            fundamental_analysis=fundamental_analysis,
            sentiment_analysis=sentiment_analysis
        )
        
        return {
            "feature_importance": explanation.get("feature_importance", []),
            "shap_values": explanation.get("shap_values", {})
        }
        
    except Exception as e:
        logger.error("feature_importance_error", user_id=str(current_user.id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Feature importance calculation failed: {str(e)}"
        )

