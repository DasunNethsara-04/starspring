"""
CORS middleware configuration

Provides easy CORS setup for the application.
"""

from typing import List, Optional
from starlette.middleware.cors import CORSMiddleware as StarletteCORSMiddleware


class CORSConfig:
    """
    CORS configuration
    
    Provides Spring Boot-style CORS configuration.
    """
    
    def __init__(
        self,
        allow_origins: List[str] = None,
        allow_methods: List[str] = None,
        allow_headers: List[str] = None,
        allow_credentials: bool = False,
        allow_origin_regex: Optional[str] = None,
        expose_headers: List[str] = None,
        max_age: int = 600
    ):
        self.allow_origins = allow_origins or ["*"]
        self.allow_methods = allow_methods or ["*"]
        self.allow_headers = allow_headers or ["*"]
        self.allow_credentials = allow_credentials
        self.allow_origin_regex = allow_origin_regex
        self.expose_headers = expose_headers or []
        self.max_age = max_age
    
    def to_middleware_kwargs(self) -> dict:
        """Convert to Starlette CORSMiddleware kwargs"""
        return {
            "allow_origins": self.allow_origins,
            "allow_methods": self.allow_methods,
            "allow_headers": self.allow_headers,
            "allow_credentials": self.allow_credentials,
            "allow_origin_regex": self.allow_origin_regex,
            "expose_headers": self.expose_headers,
            "max_age": self.max_age,
        }


def create_cors_middleware(config: CORSConfig):
    """
    Create CORS middleware from configuration
    
    Args:
        config: CORS configuration
        
    Returns:
        Configured CORS middleware
    """
    def middleware(app):
        return StarletteCORSMiddleware(app, **config.to_middleware_kwargs())
    
    return middleware


# Convenience function for common CORS setup
def enable_cors(
    allow_origins: List[str] = None,
    allow_credentials: bool = False
) -> CORSConfig:
    """
    Enable CORS with common settings
    
    Args:
        allow_origins: List of allowed origins (default: ["*"])
        allow_credentials: Whether to allow credentials
        
    Returns:
        CORS configuration
        
    Example:
        app = StarSpringApplication()
        app.add_cors(enable_cors(
            allow_origins=["http://localhost:3000"],
            allow_credentials=True
        ))
    """
    return CORSConfig(
        allow_origins=allow_origins or ["*"],
        allow_credentials=allow_credentials
    )
