"""Application settings and configuration."""
from pydantic_settings import BaseSettings
from typing import Optional



class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # LiteLLM Configuration
    GEMINI_2_5_PRO : str = "hackathon-gemini-2.5-pro"
    GEMINI_2_5_FLASH : str = "hackathon-gemini-2.5-flash"
    GEMINI_2_0_FLASH : str = "hackathon-gemini-2.0-flash"
    AZURE_GPT_5_2 : str = "hackathon-azure-gpt-5.2"
    AZURE_GPT_5_1 : str = "hackathon-azure-gpt-5.1"
    AZURE_GPT_5 : str = "hackathon-azure-gpt-5"
    AZURE_GPT_5_PRO : str = "hackathon-azure-gpt-5-pro"
    AZURE_GPT_4_1 : str = "hackathon-azure-gpt-4.1"

    LITELLM_PROXY_API_KEY: str = ""
    LITELLM_PROXY_API_BASE: str = ""
    
    # Application Configuration
    app_name: str = "AthenaTrader"
    log_level: str = "INFO"
    ENVIRONMENT: str = "development"  # development, staging, production
    ADK_LOG_LEVEL: str = "INFO"
    APP_NAME: str = "AthenaTrader"
    ADK_HOST: str = "0.0.0.0"
    ADK_PORT: int = 7777
    API_VERSION: str = "1.0.0"
    SESSION_BACKEND: str = "database"
    SESSION_DB_URL: str = "sqlite+aiosqlite:///./storage/adk_sessions.db"   
    SESSION_SQLITE_PATH: str = "./storage/adk_sessions.db"
    
    # API Keys
    ALPHA_VANTAGE_API_KEY: str = ""
    
    # Zerodha API Configuration
    zerodha_api_key: str = ""
    zerodha_api_secret: str = ""
    zerodha_access_token: str = ""
    zerodha_redirect_url: str = ""
    
    class Config:
        env_file = [".env", "app/.env"]
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()

