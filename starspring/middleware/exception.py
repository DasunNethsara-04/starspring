"""
Exception handling middleware

Provides global exception handling for the application.
"""

from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from pydantic import ValidationError

from starspring.core.exceptions import StarSpringException


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """
    Global exception handler middleware
    
    Catches all exceptions and converts them to proper HTTP responses.
    Similar to Spring Boot's @ControllerAdvice.
    """
    
    def __init__(self, app, debug: bool = False):
        super().__init__(app)
        self.debug = debug
    
    async def dispatch(self, request: Request, call_next: Callable):
        try:
            response = await call_next(request)
            return response
        except StarSpringException as e:
            # Handle framework exceptions
            return self._create_error_response(
                status_code=e.status_code,
                error=e.__class__.__name__,
                message=e.message,
                details=e.details
            )
        except ValidationError as e:
            # Handle Pydantic validation errors
            return self._create_error_response(
                status_code=422,
                error="ValidationError",
                message="Validation failed",
                details={"errors": e.errors()}
            )
        except Exception as e:
            # Handle unexpected exceptions
            error_details = {"type": e.__class__.__name__}
            if self.debug:
                import traceback
                error_details["traceback"] = traceback.format_exc()
            
            return self._create_error_response(
                status_code=500,
                error="InternalServerError",
                message=str(e) if self.debug else "An internal error occurred",
                details=error_details if self.debug else None
            )
    
    def _create_error_response(
        self,
        status_code: int,
        error: str,
        message: str,
        details: dict = None
    ) -> JSONResponse:
        """Create a standardized error response"""
        content = {
            "success": False,
            "error": error,
            "message": message,
            "status": status_code
        }
        
        if details:
            content["details"] = details
        
        return JSONResponse(
            status_code=status_code,
            content=content
        )
