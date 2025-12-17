"""Session service factory and singleton.

This module provides a configured ADK ``SessionService`` instance for
the application. The concrete backend is selected via application
settings and can be:

* ``inmemory`` – the default in-memory session store
* ``database`` – a database-backed store using ADK's DatabaseSessionService (supports any SQLAlchemy-compatible database URL)

"""

from __future__ import annotations

import os
from typing import Any, Optional

from google.adk.sessions.database_session_service import DatabaseSessionService
from google.adk.sessions.in_memory_session_service import InMemorySessionService

from app.config.settings import Settings,settings
from app.loggers.logging_config import get_logger

logger = get_logger(__name__)

_session_service: Optional[Any] = None


def _create_session_service(config: Settings) -> Any:
    """Create a configured ADK session service instance.

    The backend is selected using :data:`config.SESSION_BACKEND`.

    Args:
        config: Application settings used to configure the backend.

    Returns:
        ADK ``SessionService`` compatible instance.

    Raises:
        ValueError: If an unsupported backend is configured.
    """
    backend = (config.SESSION_BACKEND or "inmemory").lower()

    if backend == "inmemory":
        logger.info("Creating InMemorySessionService for sessions")
        return InMemorySessionService()

    if backend == "database":
        db_url = config.SESSION_DB_URL

        # Fallback to SQLite if no SESSION_DB_URL provided
        if not db_url:
            db_path = os.path.abspath(config.SESSION_SQLITE_PATH)
            db_url = f"sqlite+aiosqlite:///{db_path}"
            logger.info(f"No SESSION_DB_URL configured, using SQLite at {db_url}")

        # Ensure parent directory exists for SQLite databases
        if db_url.startswith("sqlite"):
            # Extract file path from SQLite URL (format: sqlite+aiosqlite:///path/to/db.db)
            db_file_path = db_url.split("://")[-1].lstrip("/")
            db_dir = os.path.dirname(db_file_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
                logger.debug(f"Ensured directory exists: {db_dir}")

        logger.info(f"Creating DatabaseSessionService with URL: {db_url}")
        return DatabaseSessionService(db_url=db_url)

    raise ValueError(f"Unsupported session backend: {backend}. Supported: inmemory, database")


def get_session_service() -> Any:
    """Get the configured ADK session service singleton.

    Returns:
        ADK ``SessionService`` compatible instance.
    """
    global _session_service

    if _session_service is None:
        logger.info("Lazy-initializing session service singleton")
        _session_service = _create_session_service(settings)
        logger.info("Session service initialized successfully")

    return _session_service


def reset_session_service() -> None:
    """Reset the session service singleton.

    This helper is intended for unit tests only. It clears the cached
    session service instance.
    """
    global _session_service
    _session_service = None
    logger.debug("Session service singleton reset")
 