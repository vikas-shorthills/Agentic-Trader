"""Application settings and configuration."""
from pydantic_settings import BaseSettings
from typing import Optional



class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # LiteLLM Configuration
    LITELLM_MODEL: str = "hackathon-gemini-2.5-flash"
    LITELLM_PROXY_API_KEY: str = ""
    LITELLM_PROXY_API_BASE: str = ""
    
    # Application Configuration
    app_name: str = "AthenaTrader"
    log_level: str = "INFO"
    ENVIRONMENT: str = "development"  # development, staging, production
    ADK_LOG_LEVEL: str = "INFO"
    APP_NAME: str = "AthenaTrader"
    ADK_HOST: str = "0.0.0.0"
    ADK_PORT: int = 8000
    API_VERSION: str = "1.0.0"
    SESSION_BACKEND: str = "database"
    SESSION_DB_URL: str = "sqlite+aiosqlite:///./storage/adk_sessions.db"   
    SESSION_SQLITE_PATH: str = "./storage/adk_sessions.db"
    
    # API Keys
    ALPHA_VANTAGE_API_KEY: str = ""
    FINNHUB_API_KEY: str = ""  # Finnhub API key for news data
    
    # Zerodha API Configuration
    zerodha_api_key: Optional[str] = None
    zerodha_api_secret: Optional[str] = None
    zerodha_access_token: Optional[str] = None
    zerodha_redirect_url: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()

