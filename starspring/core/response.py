"""
Response utilities similar to Spring Boot's ResponseEntity

Provides structured response classes for API endpoints.
"""

from typing import Optional, Dict, Any, Generic, TypeVar
from enum import Enum
from pydantic import BaseModel


T = TypeVar('T')


class HttpStatus(Enum):
    """HTTP status codes"""
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    INTERNAL_SERVER_ERROR = 500


class ApiResponse(BaseModel, Generic[T]):
    """
    Generic API response wrapper
    
    Example:
        return ApiResponse(
            success=True,
            data=user,
            message="User created successfully"
        )
    """
    success: bool
    data: Optional[T] = None
    message: Optional[str] = None
    errors: Optional[Dict[str, Any]] = None
    
    class Config:
        arbitrary_types_allowed = True


class ResponseEntity(Generic[T]):
    """
    Response entity similar to Spring Boot's ResponseEntity
    
    Provides fluent API for building HTTP responses with status codes and headers.
    
    Example:
        return ResponseEntity.ok(user)
        return ResponseEntity.created(user).header("Location", "/api/users/1")
        return ResponseEntity.not_found().body({"error": "User not found"})
    """
    
    def __init__(
        self,
        body: Optional[T] = None,
        status: int = 200,
        headers: Optional[Dict[str, str]] = None
    ):
        self.body = body
        self.status = status
        self.headers = headers or {}
    
    def header(self, key: str, value: str) -> 'ResponseEntity[T]':
        """Add a header to the response"""
        self.headers[key] = value
        return self
    
    def to_starlette_response(self):
        """Convert to Starlette JSONResponse"""
        from starlette.responses import JSONResponse
        
        # Handle Pydantic models and entities
        if hasattr(self.body, 'model_dump'):
            content = self.body.model_dump()
        elif hasattr(self.body, 'dict'):
            content = self.body.dict()
        elif hasattr(self.body, 'to_dict'):
            content = self.body.to_dict()
        elif isinstance(self.body, list):
            content = [
                item.model_dump() if hasattr(item, 'model_dump') 
                else item.dict() if hasattr(item, 'dict')
                else item.to_dict() if hasattr(item, 'to_dict')
                else item
                for item in self.body
            ]
        else:
            content = self.body
        
        return JSONResponse(
            content=content,
            status_code=self.status,
            headers=self.headers
        )
    
    # Static factory methods for common responses
    
    @staticmethod
    def ok(body: Optional[T] = None) -> 'ResponseEntity[T]':
        """Create a 200 OK response"""
        return ResponseEntity(body=body, status=HttpStatus.OK.value)
    
    @staticmethod
    def created(body: Optional[T] = None) -> 'ResponseEntity[T]':
        """Create a 201 Created response"""
        return ResponseEntity(body=body, status=HttpStatus.CREATED.value)
    
    @staticmethod
    def accepted(body: Optional[T] = None) -> 'ResponseEntity[T]':
        """Create a 202 Accepted response"""
        return ResponseEntity(body=body, status=HttpStatus.ACCEPTED.value)
    
    @staticmethod
    def no_content() -> 'ResponseEntity[None]':
        """Create a 204 No Content response"""
        return ResponseEntity(body=None, status=HttpStatus.NO_CONTENT.value)
    
    @staticmethod
    def bad_request(body: Optional[T] = None) -> 'ResponseEntity[T]':
        """Create a 400 Bad Request response"""
        return ResponseEntity(body=body, status=HttpStatus.BAD_REQUEST.value)
    
    @staticmethod
    def unauthorized(body: Optional[T] = None) -> 'ResponseEntity[T]':
        """Create a 401 Unauthorized response"""
        return ResponseEntity(body=body, status=HttpStatus.UNAUTHORIZED.value)
    
    @staticmethod
    def forbidden(body: Optional[T] = None) -> 'ResponseEntity[T]':
        """Create a 403 Forbidden response"""
        return ResponseEntity(body=body, status=HttpStatus.FORBIDDEN.value)
    
    @staticmethod
    def not_found(body: Optional[T] = None) -> 'ResponseEntity[T]':
        """Create a 404 Not Found response"""
        return ResponseEntity(body=body, status=HttpStatus.NOT_FOUND.value)
    
    @staticmethod
    def status(status_code: int, body: Optional[T] = None) -> 'ResponseEntity[T]':
        """Create a response with custom status code"""
        return ResponseEntity(body=body, status=status_code)
