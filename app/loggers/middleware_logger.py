"""
FastAPI middleware for request/response logging with correlation IDs.
"""

import time
import uuid
import json
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all HTTP requests and responses with timing information.
    Adds correlation ID to each request for tracing across modules.
    """
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details."""
        # Get correlation ID from header or body
        correlation_id = request.headers.get("sessionId", "NA")
        if correlation_id == "NA" and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    body_data = json.loads(body)
                    correlation_id = body_data.get("sessionId", "NA")
            except:
                pass
        # request.state.correlation_id = correlation_id
        # Start timing
        start_time = time.time()
        # Log incoming request
        logger.info(
            f"Incoming request: {request.method} {request.url.path}",
            extra={
                "session_id": correlation_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client_host": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            }
        )
        # Process request
        try:
            response = await call_next(request)
            # Calculate duration
            duration = time.time() - start_time
            # Log response
            logger.info(
                f"Request completed: {request.method} {request.url.path}",
                extra={
                    "session_id": correlation_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration * 1000, 2),
                }
            )
            return response
        except Exception as e:
            duration = time.time() - start_time
            # Log error
            logger.error(
                f"Request failed: {request.method} {request.url.path}",
                exc_info=True,
                extra={
                    "session_id": correlation_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round(duration * 1000, 2),
                    "error": str(e),
                }
            )
            raise
 