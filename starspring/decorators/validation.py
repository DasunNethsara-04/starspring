"""
Validation decorators

Provides validation support for controllers.
"""

from typing import Callable, Type
from functools import wraps


def Validated(cls: Type) -> Type:
    """
    Enable validation on a controller
    
    Similar to Spring Boot's @Validated annotation.
    When used, all Pydantic models in request handlers will be validated.
    
    Example:
        @Controller("/api/users")
        @Validated
        class UserController:
            @PostMapping("/")
            def create_user(self, user: UserCreateRequest):
                return user
    
    Note: Validation is enabled by default in StarSpring, so this decorator
    is mainly for documentation purposes and future extensibility.
    """
    cls._is_validated = True  # type: ignore
    return cls
