"""
Base controller class

Provides common functionality for all controllers.
"""

from typing import Optional
from starlette.requests import Request


class BaseController:
    """
    Base class for all controllers
    
    Provides access to common utilities and request context.
    Similar to Spring Boot's base controller pattern.
    """
    
    def __init__(self):
        self._request: Optional[Request] = None
    
    @property
    def request(self) -> Optional[Request]:
        """Get the current request object"""
        return self._request
    
    def set_request(self, request: Request) -> None:
        """Set the current request object (called by framework)"""
        self._request = request
    
    def get_header(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """Get a request header value"""
        if self._request:
            return self._request.headers.get(name, default)
        return default
    
    def get_query_param(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """Get a query parameter value"""
        if self._request:
            return self._request.query_params.get(name, default)
        return default
    
    def get_path_param(self, name: str) -> Optional[str]:
        """Get a path parameter value"""
        if self._request:
            return self._request.path_params.get(name)
        return None
