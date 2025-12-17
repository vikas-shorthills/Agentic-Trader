import logging
import json
import sys
import os
from datetime import datetime
from typing import Any, Dict, Optional
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path


class JSONFormatter(logging.Formatter):
    """
    Production-grade JSON formatter for structured logging.
    Compatible with log aggregation tools (ELK, Splunk, CloudWatch, etc.)
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON with structured fields.
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add app_name if available
        if hasattr(record, "app_name"):
            log_data["app_name"] = record.app_name
        
        # Add correlation/session ID if available
        if hasattr(record, "session_id"):
            log_data["session_id"] = record.session_id
        if hasattr(record, "correlation_id"):
            log_data["correlation_id"] = record.correlation_id
        
        # Add request context if available
        if hasattr(record, "method"):
            log_data["http_method"] = record.method
        if hasattr(record, "path"):
            log_data["http_path"] = record.path
        if hasattr(record, "status_code"):
            log_data["http_status"] = record.status_code
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            log_data["exception_type"] = record.exc_info[0].__name__ if record.exc_info[0] else None
        
        # Add any extra fields
        if hasattr(record, "extra_fields") and record.extra_fields:
            log_data.update(record.extra_fields)
        
        # Add process/thread info
        log_data["process_id"] = os.getpid()
        log_data["thread_id"] = record.thread
        log_data["thread_name"] = record.threadName
        
        return json.dumps(log_data, ensure_ascii=False)


class StructuredFormatter(logging.Formatter):
    """
    Human-readable structured formatter for development.
    Includes color coding and readable timestamps.
    """
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m',       # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record in human-readable format.
        """
        # Color code based on level
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        # Base log line
        log_parts = [
            f"{timestamp}",
            f"{color}{record.levelname:8}{reset}",
            f"[{record.name}]",
            f"{record.getMessage()}"
        ]
        
        # Add context if available
        context_parts = []
        if hasattr(record, "app_name"):
            context_parts.append(f"app={record.app_name}")
        if hasattr(record, "session_id"):
            context_parts.append(f"session={record.session_id}")
        if hasattr(record, "correlation_id"):
            context_parts.append(f"correlation={record.correlation_id}")
        if hasattr(record, "method") and hasattr(record, "path"):
            context_parts.append(f"{record.method} {record.path}")
        
        if context_parts:
            log_parts.append(f"({', '.join(context_parts)})")
        
        # Add exception if present
        if record.exc_info:
            log_parts.append(f"\n{self.formatException(record.exc_info)}")
        
        return " | ".join(log_parts)


class SensitiveDataFilter(logging.Filter):
    """
    Filter to redact sensitive information from logs.
    """
    
    SENSITIVE_PATTERNS = [
        r'password["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
        r'api[_-]?key["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
        r'token["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
        r'secret["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
        r'authorization["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
    ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter and redact sensitive data from log messages.
        """
        import re
        message = record.getMessage()
        for pattern in self.SENSITIVE_PATTERNS:
            message = re.sub(pattern, r'\1=***REDACTED***', message, flags=re.IGNORECASE)
        record.msg = message
        return True


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    app_name: str = "ADK_AGENT",
    environment: str = "development",
    log_format: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    enable_json: Optional[bool] = None,
    enable_rotation: bool = True,
) -> None:
    """
    Production-grade logging setup with structured logging, rotation, and environment awareness.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path. If None, logs only to stdout
        app_name: Application name to include in logs
        environment: Environment name (development, staging, production)
        log_format: Override format ('json' or 'text'). Auto-detected from environment if None
        max_bytes: Maximum log file size before rotation (default: 10MB)
        backup_count: Number of backup log files to keep (default: 5)
        enable_json: Force JSON format. If None, auto-detects from environment
        enable_rotation: Enable log file rotation (default: True)
    """
    
    # Auto-detect JSON format for production
    if enable_json is None:
        enable_json = environment.lower() in ("production", "staging", "prod")
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Clear existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Choose formatter based on environment
    if enable_json:
        formatter = JSONFormatter()
    else:
        formatter = StructuredFormatter()
    
    # Console handler (always stdout for containerized deployments)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    console_handler.setFormatter(formatter)
    
    # Add sensitive data filter in production
    if enable_json:
        console_handler.addFilter(SensitiveDataFilter())
    
    root_logger.addHandler(console_handler)
    
    # File handler with rotation (if log_file is provided)
    if log_file:
        try:
            # Ensure log directory exists
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            if enable_rotation:
                # Use time-based rotation for production, size-based for development
                if enable_json:
                    # Daily rotation for production
                    file_handler = TimedRotatingFileHandler(
                        filename=log_file,
                        when='midnight',
                        interval=1,
                        backupCount=backup_count,
                        encoding='utf-8',
                        utc=True
                    )
                else:
                    # Size-based rotation for development
                    file_handler = RotatingFileHandler(
                        filename=log_file,
                        maxBytes=max_bytes,
                        backupCount=backup_count,
                        encoding='utf-8'
                    )
            else:
                # Simple file handler without rotation
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
            
            file_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
            file_handler.setFormatter(formatter)
            
            # Add sensitive data filter
            if enable_json:
                file_handler.addFilter(SensitiveDataFilter())
            
            root_logger.addHandler(file_handler)
            logging.info(f"File logging enabled: {log_file}")
            
        except (OSError, PermissionError) as e:
            # Gracefully handle file permission errors
            logging.warning(f"Could not create log file {log_file}: {e}. Continuing with console logging only.")
    
    # Configure third-party library log levels
    # Reduce noise from verbose libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    # ADK library logging
    logging.getLogger('google.adk').setLevel(logging.INFO)
    logging.getLogger('google.adk.agents').setLevel(logging.INFO)
    logging.getLogger('google.adk.runners').setLevel(logging.INFO)
    logging.getLogger('google.adk.sessions').setLevel(logging.INFO)
    logging.getLogger('google.adk.tools').setLevel(logging.INFO)
    
    # Add app name filter to all log records
    class AppNameFilter(logging.Filter):
        def __init__(self, app_name: str):
            super().__init__()
            self.app_name = app_name
        
        def filter(self, record: logging.LogRecord) -> bool:
            record.app_name = self.app_name
            return True
    
    root_logger.addFilter(AppNameFilter(app_name))
    
    # Log initialization with structured data
    init_log = {
        "app_name": app_name,
        "environment": environment,
        "log_level": log_level.upper(),
        "log_format": "json" if enable_json else "text",
        "file_logging": log_file is not None,
    }
    
    if enable_json:
        logging.info("Logging initialized", extra={"extra_fields": init_log})
    else:
        logging.info(f"Logging initialized for {app_name} | environment={environment} | level={log_level.upper()} | format={'JSON' if enable_json else 'TEXT'}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    Args:
        name: Name of the module (typically __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """
    Custom logger adapter for adding contextual information to logs.
    Useful for adding request IDs, user IDs, correlation IDs, etc.
    """
    
    def process(self, msg, kwargs):
        """Add extra fields to the log record."""
        if "extra" not in kwargs:
            kwargs["extra"] = {}
        
        # Merge adapter's extra with call's extra
        extra_fields = {**self.extra, **kwargs.get("extra", {})}
        kwargs["extra"] = {"extra_fields": extra_fields}
        
        return msg, kwargs