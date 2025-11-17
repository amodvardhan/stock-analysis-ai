"""
=============================================================================
AI Hub - Configuration Management
=============================================================================
Centralized configuration using Pydantic Settings.
All settings are loaded from environment variables with sensible defaults.
=============================================================================
"""

from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    
    # -------------------------
    # Application Settings
    # -------------------------
    ENVIRONMENT: str = Field(default="development", description="Application environment")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    SECRET_KEY: str = Field(..., description="Secret key for JWT tokens (REQUIRED)")
    
    # -------------------------
    # Database Configuration
    # -------------------------
    DATABASE_URL: str = Field(
        ...,
        description="PostgreSQL connection string (REQUIRED)"
    )
    REDIS_URL: str = Field(
        default="redis://localhost:6379",
        description="Redis connection string"
    )
    
    # -------------------------
    # CORS Settings (FIXED)
    # -------------------------
    CORS_ORIGINS: Union[str, List[str]] = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="Allowed CORS origins for frontend"
    )
    
    # -------------------------
    # LLM Configuration
    # -------------------------
    OPENAI_API_KEY: str = Field(..., description="OpenAI API key (REQUIRED)")
    OPENAI_MODEL: str = Field(
        default="gpt-4o-mini",
        description="OpenAI model to use"
    )
    OPENAI_TEMPERATURE: float = Field(
        default=0.1,
        description="LLM temperature (0.0-1.0)"
    )
    
    # -------------------------
    # Market Data APIs
    # -------------------------
    ALPHA_VANTAGE_API_KEY: str = Field(
        default="",
        description="Alpha Vantage API key (optional)"
    )
    
    # -------------------------
    # Authentication
    # -------------------------
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="JWT token expiration time in minutes"
    )
    
    # -------------------------
    # Email Configuration
    # -------------------------
    SMTP_HOST: str = Field(default="smtp.gmail.com", description="SMTP server host")
    SMTP_PORT: int = Field(default=587, description="SMTP server port")
    SMTP_USER: str = Field(default="", description="SMTP username")
    SMTP_PASSWORD: str = Field(default="", description="SMTP password")
    SMTP_FROM: str = Field(default="noreply@aihub.com", description="From email address")
    
    # -------------------------
    # SMS Configuration (Optional)
    # -------------------------
    TWILIO_ACCOUNT_SID: str = Field(default="", description="Twilio Account SID")
    TWILIO_AUTH_TOKEN: str = Field(default="", description="Twilio Auth Token")
    TWILIO_PHONE_NUMBER: str = Field(default="", description="Twilio phone number")
    
    # -------------------------
    # LLM Observability
    # -------------------------
    LANGSMITH_API_KEY: str = Field(default="", description="LangSmith API key")
    LANGSMITH_PROJECT: str = Field(
        default="aihub-stock-intelligence",
        description="LangSmith project name"
    )
    LANGSMITH_TRACING_V2: bool = Field(
        default=False,
        description="Enable LangSmith tracing"
    )
    
    # -------------------------
    # Stock Monitoring Settings
    # -------------------------
    STOCK_MONITORING_INTERVAL_MINUTES: int = Field(
        default=15,
        description="How often to check watchlist stocks (minutes)"
    )
    PRICE_ALERT_THRESHOLD_PERCENT: float = Field(
        default=5.0,
        description="Price movement % that triggers alert"
    )
    
    # -------------------------
    # Pydantic Configuration
    # -------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """
        Parse CORS_ORIGINS from string to list if needed.
        Handles: "http://localhost:3000,http://localhost:5173"
        Also handles: empty string, None, already a list
        """
        # If it's already a list, return it
        if isinstance(v, list):
            return v
        
        # If it's None or empty string, return default
        if not v or v == "":
            return ["http://localhost:3000", "http://localhost:5173"]
        
        # If it's a string, split by comma
        if isinstance(v, str):
            # Remove any whitespace and filter out empty strings
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        
        # Fallback to default
        return ["http://localhost:3000", "http://localhost:5173"]


# -------------------------
# Global Settings Instance
# -------------------------
settings = Settings()
