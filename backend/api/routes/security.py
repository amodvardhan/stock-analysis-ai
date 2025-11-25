"""
=============================================================================
Security API Routes
=============================================================================
Endpoints for MFA, biometric authentication, and security features.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
from pydantic import BaseModel
import structlog

from core.database import get_db
from db.models import User
from api.routes.auth import get_current_user
from services.security_service import SecurityService

logger = structlog.get_logger()
router = APIRouter()


class MFASetupResponse(BaseModel):
    secret: str
    qr_code: str
    backup_codes: List[str]
    message: str


class MFAVerifyRequest(BaseModel):
    token: str


@router.post("/mfa/setup", response_model=MFASetupResponse)
async def setup_mfa(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> MFASetupResponse:
    """Setup Multi-Factor Authentication for the user."""
    try:
        result = await SecurityService.setup_mfa(
            db=db,
            user_id=str(current_user.id),
            user_email=current_user.email
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return MFASetupResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("mfa_setup_error", user_id=str(current_user.id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"MFA setup failed: {str(e)}"
        )


@router.post("/mfa/verify")
async def verify_mfa(
    request: MFAVerifyRequest,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Verify MFA token."""
    try:
        # In production, retrieve secret from database
        # For now, this is a placeholder
        user_secret = ""  # Would be retrieved from user's stored secret
        
        is_valid = await SecurityService.verify_mfa_token(
            user_secret=user_secret,
            token=request.token
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid MFA token"
            )
        
        return {
            "verified": True,
            "message": "MFA token verified successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("mfa_verification_error", user_id=str(current_user.id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"MFA verification failed: {str(e)}"
        )


@router.post("/webauthn/setup")
async def setup_webauthn(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Setup WebAuthn (biometric) authentication."""
    try:
        result = await SecurityService.setup_webauthn(
            db=db,
            user_id=str(current_user.id)
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
        logger.error("webauthn_setup_error", user_id=str(current_user.id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"WebAuthn setup failed: {str(e)}"
        )


@router.post("/webauthn/verify")
async def verify_webauthn(
    credential: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Verify WebAuthn credential."""
    try:
        is_valid = await SecurityService.verify_webauthn(
            db=db,
            user_id=str(current_user.id),
            credential=credential
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid WebAuthn credential"
            )
        
        return {
            "verified": True,
            "message": "Biometric authentication successful"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("webauthn_verification_error", user_id=str(current_user.id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"WebAuthn verification failed: {str(e)}"
        )

