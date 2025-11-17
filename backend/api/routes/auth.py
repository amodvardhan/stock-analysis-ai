"""
=============================================================================
AI Hub - Authentication Routes
=============================================================================
Handles user registration, login, and profile management.

Endpoints:
- POST /signup - Register new user
- POST /login - Authenticate user (supports both JSON and form data)
- GET /me - Get current user profile
- PUT /me - Update user profile
=============================================================================
"""

from datetime import datetime, timedelta
from typing import Optional, Union
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from core.database import get_db
from db.models import User
from schemas.user_schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
    TokenResponse
)
from utils.security import hash_password, verify_password, create_access_token, decode_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = structlog.get_logger()
router = APIRouter()
security = HTTPBearer()


# =============================================================================
# Dependency: Get Current User
# =============================================================================
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency to get the currently authenticated user.
    
    This function:
    1. Extracts JWT token from Authorization header
    2. Validates and decodes the token
    3. Fetches user from database
    4. Returns user object or raises 401 error
    
    Usage in routes:
        @router.get("/protected")
        async def protected_route(current_user: User = Depends(get_current_user)):
            return {"user": current_user.email}
    """
    token = credentials.credentials
    email = decode_access_token(token)
    
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Fetch user from database
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    return user


# =============================================================================
# Route: User Registration
# =============================================================================
@router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account and receive authentication token"
)
async def signup(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Register a new user account.
    
    Steps:
    1. Check if email already exists
    2. Hash the password
    3. Create user in database
    4. Generate JWT token
    5. Return token
    """
    logger.info("user_signup_requested", email=user_data.email)
    
    # Check if user already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        phone_number=user_data.phone_number,
        risk_tolerance="moderate",  # Default
        email_notifications=True,
        sms_notifications=False,
        is_active=True,
        is_verified=False  # Email verification would happen separately
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Generate token
    access_token = create_access_token(data={"sub": new_user.email})
    
    logger.info("user_created", user_id=str(new_user.id), email=new_user.email)
    
    return TokenResponse(access_token=access_token)


# =============================================================================
# Route: User Login (supports both JSON and OAuth2 form data)
# =============================================================================
@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login user",
    description="Authenticate user and receive JWT token (supports JSON and form data)"
)
async def login(
    credentials: Union[UserLogin, None] = Body(default=None),
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Authenticate user and return JWT token.
    
    Supports both:
    - JSON: {"email": "user@example.com", "password": "password123"}
    - Form data: username=user@example.com&password=password123
    
    Steps:
    1. Extract credentials from JSON or form data
    2. Find user by email
    3. Verify password
    4. Update last_login timestamp
    5. Generate and return JWT token
    """
    # Determine which format was used (JSON or form)
    if credentials:
        # JSON format
        email = credentials.email
        password = credentials.password
    else:
        # OAuth2 form format (username field contains email)
        email = form_data.username
        password = form_data.password
    
    logger.info("user_login_requested", email=email)
    
    # Find user
    result = await db.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(password, user.hashed_password):
        logger.warning("login_failed_invalid_password", email=email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    user.updated_at = datetime.utcnow()
    await db.commit()
    
    # Generate token
    access_token = create_access_token(data={"sub": user.email})
    
    logger.info("user_logged_in", user_id=str(user.id), email=user.email)
    
    return TokenResponse(access_token=access_token)


# =============================================================================
# Route: Get Current User Profile
# =============================================================================
@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Retrieve authenticated user's profile information"
)
async def get_me(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Get the current authenticated user's profile.
    
    This is a protected route - requires valid JWT token.
    """
    return UserResponse.model_validate(current_user)


# =============================================================================
# Route: Update User Profile
# =============================================================================
@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update user profile",
    description="Update current user's profile information"
)
async def update_me(
    updates: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Update the current user's profile.
    
    Only updates fields that are provided in the request.
    """
    logger.info("user_update_requested", user_id=str(current_user.id))
    
    # Update only provided fields
    update_data = updates.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    current_user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(current_user)
    
    logger.info("user_updated", user_id=str(current_user.id))
    
    return UserResponse.model_validate(current_user)
