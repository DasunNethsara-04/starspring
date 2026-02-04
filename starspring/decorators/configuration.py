"""
Configuration decorators

Provides Spring Boot-style configuration annotations.
"""

from typing import Callable, Optional, Type, TypeVar, Any
from functools import wraps
from starspring.core.context import get_application_context


T = TypeVar('T')


def Configuration(cls: Type[T]) -> Type[T]:
    """
    Mark a class as a configuration class
    
    Similar to Spring Boot's @Configuration annotation.
    Configuration classes can contain @Bean methods.
    
    Example:
        @Configuration
        class AppConfig:
            @Bean
            def database(self):
                return Database()
    """
    cls._is_configuration = True  # type: ignore
    
    # Process @Bean methods
    context = get_application_context()
    instance = cls()
    
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if callable(attr) and hasattr(attr, '_is_bean'):
            # Call the bean factory method
            bean_instance = attr(instance)
            bean_type = type(bean_instance)
            bean_name = getattr(attr, '_bean_name', None)
            
            # Register the bean
            context.register_bean(
                bean_type,
                factory=lambda: attr(instance),
                name=bean_name
            )
    
    return cls


def Bean(func: Optional[Callable] = None, *, name: Optional[str] = None) -> Callable:
    """
    Mark a method as a bean factory method
    
    Similar to Spring Boot's @Bean annotation.
    Must be used within a @Configuration class.
    
    Args:
        name: Optional custom name for the bean
        
    Example:
        @Configuration
        class AppConfig:
            @Bean
            def user_service(self):
                return UserService()
    """
    def decorator(target_func: Callable) -> Callable:
        target_func._is_bean = True  # type: ignore
        target_func._bean_name = name  # type: ignore
        return target_func
    
    # Handle both @Bean and @Bean() syntax
    if func is None:
        return decorator
    else:
        return decorator(func)


def Value(key: str, default: Any = None) -> Any:
    """
    Inject a configuration value
    
    Similar to Spring Boot's @Value annotation.
    
    Args:
        key: Configuration key to inject
        default: Default value if key not found
        
    Example:
        class MyService:
            def __init__(self):
                self.api_key = Value("api.key", "default-key")
    
    Note: This is a simplified implementation. In a real application,
    this would integrate with the configuration system.
    """
    # This is a placeholder - actual implementation would read from config
    from starspring.config.properties import get_property
    return get_property(key, default)
