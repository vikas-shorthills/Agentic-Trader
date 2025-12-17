"""
Trade Agent API - Main Entry Point

For development:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

"""

import uvicorn

from app.application import create_application
from app.config.settings import settings
from app.loggers.logging_config import get_logger, setup_logging

setup_logging(log_level = settings.ADK_LOG_LEVEL,log_file=None,app_name=settings.APP_NAME,environment=settings.ENVIRONMENT)

logger = get_logger(__name__)

app = create_application()

if __name__ == "__main__":
    """
    Run the application directly using uvicorn.
    """
    logger.info("=" * 60)
    logger.info("Starting development server")
    logger.info("=" * 60)
    logger.info(f"Server: http://{settings.ADK_HOST}:{settings.ADK_PORT}")
    logger.info(f"ADK Web UI: http://{settings.ADK_HOST}:{settings.ADK_PORT}/dev-ui/")
    logger.info(f"API Docs: http://{settings.ADK_HOST}:{settings.ADK_PORT}/docs")
    logger.info(f"Health Check: http://{settings.ADK_HOST}:{settings.ADK_PORT}/health")
    logger.info("=" * 60)

    uvicorn.run(
        "app.main:app",
        host=settings.ADK_HOST,
        port=settings.ADK_PORT,
        # reload=settings.is_local,
        log_level=settings.ADK_LOG_LEVEL.lower(),
    )
 