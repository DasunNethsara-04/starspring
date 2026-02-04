"""
Logging middleware

Provides request/response logging.
"""

import time
import logging
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


# Configure logger
logger = logging.getLogger("starspring")


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Request/response logging middleware
    
    Logs all incoming requests and their response times.
    """
    
    def __init__(self, app, log_level: int = logging.INFO):
        super().__init__(app)
        self.log_level = log_level
        
        # Configure logger if not already configured
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(log_level)
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Log request
        start_time = time.time()
        
        logger.log(
            self.log_level,
            f"→ {request.method} {request.url.path}"
        )
        
        # Process request
        response = await call_next(request)
        
        # Log response
        duration = (time.time() - start_time) * 1000  # Convert to ms
        
        logger.log(
            self.log_level,
            f"← {request.method} {request.url.path} "
            f"[{response.status_code}] {duration:.2f}ms"
        )
        
        return response
