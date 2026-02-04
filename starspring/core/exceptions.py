"""
Exception hierarchy for StarSpring framework

Provides Spring Boot-style exception classes with automatic HTTP status mapping.
"""

from typing import Optional, Dict, Any


class StarSpringException(Exception):
    """Base exception for all StarSpring framework exceptions"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON response"""
        result = {
            "error": self.__class__.__name__,
            "message": self.message,
            "status": self.status_code,
        }
        if self.details:
            result["details"] = self.details
        return result


class BadRequestException(StarSpringException):
    """Exception for 400 Bad Request errors"""
    
    def __init__(self, message: str = "Bad Request", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, details=details)


class UnauthorizedException(StarSpringException):
    """Exception for 401 Unauthorized errors"""
    
    def __init__(self, message: str = "Unauthorized", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=401, details=details)


class ForbiddenException(StarSpringException):
    """Exception for 403 Forbidden errors"""
    
    def __init__(self, message: str = "Forbidden", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=403, details=details)


class NotFoundException(StarSpringException):
    """Exception for 404 Not Found errors"""
    
    def __init__(self, message: str = "Resource Not Found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=404, details=details)


class ConflictException(StarSpringException):
    """Exception for 409 Conflict errors"""
    
    def __init__(self, message: str = "Conflict", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=409, details=details)


class ValidationException(StarSpringException):
    """Exception for validation errors"""
    
    def __init__(self, message: str = "Validation Failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=422, details=details)


class InternalServerException(StarSpringException):
    """Exception for 500 Internal Server errors"""
    
    def __init__(self, message: str = "Internal Server Error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)
