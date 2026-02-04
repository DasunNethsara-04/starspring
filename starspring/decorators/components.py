"""
Component decorators for dependency injection

Provides Spring Boot-style component annotations like @Controller, @Service, etc.
"""

from typing import Optional, Type, TypeVar, Callable
from functools import wraps
from starspring.core.context import get_application_context, BeanScope


T = TypeVar('T')


def Controller(prefix: str = "") -> Callable[[Type[T]], Type[T]]:
    """
    Mark a class as a REST controller
    
    Similar to Spring Boot's @RestController annotation.
    
    Args:
        prefix: URL prefix for all routes in this controller
        
    Example:
        @Controller("/api/users")
        class UserController:
            pass
    """
    def decorator(cls: Type[T]) -> Type[T]:
        # Store metadata on the class
        cls._is_controller = True  # type: ignore
        cls._controller_prefix = prefix  # type: ignore
        cls._routes = []  # type: ignore
        
        # Register in application context
        context = get_application_context()
        context.register_bean(cls, scope=BeanScope.SINGLETON)
        
        return cls
    
    return decorator


def Service(cls: Optional[Type[T]] = None, *, name: Optional[str] = None) -> Type[T]:
    """
    Mark a class as a service component
    
    Similar to Spring Boot's @Service annotation.
    
    Example:
        @Service
        class UserService:
            pass
    """
    def decorator(target_cls: Type[T]) -> Type[T]:
        # Store metadata
        target_cls._is_service = True  # type: ignore
        
        # Register in application context
        context = get_application_context()
        context.register_bean(target_cls, scope=BeanScope.SINGLETON, name=name)
        
        return target_cls
    
    # Handle both @Service and @Service() syntax
    if cls is None:
        return decorator  # type: ignore
    else:
        return decorator(cls)


def Component(cls: Optional[Type[T]] = None, *, name: Optional[str] = None) -> Type[T]:
    """
    Mark a class as a generic component
    
    Similar to Spring Boot's @Component annotation.
    
    Example:
        @Component
        class EmailSender:
            pass
    """
    def decorator(target_cls: Type[T]) -> Type[T]:
        # Store metadata
        target_cls._is_component = True  # type: ignore
        
        # Register in application context
        context = get_application_context()
        context.register_bean(target_cls, scope=BeanScope.SINGLETON, name=name)
        
        return target_cls
    
    # Handle both @Component and @Component() syntax
    if cls is None:
        return decorator  # type: ignore
    else:
        return decorator(cls)


def Repository(cls: Optional[Type[T]] = None, *, name: Optional[str] = None) -> Type[T]:
    """
    Mark a class as a repository component
    
    Similar to Spring Boot's @Repository annotation.
    
    Example:
        @Repository
        class UserRepository:
            pass
    """
    def decorator(target_cls: Type[T]) -> Type[T]:
        # Store metadata
        target_cls._is_repository = True  # type: ignore
        
        # Register in application context
        context = get_application_context()
        context.register_bean(target_cls, scope=BeanScope.SINGLETON, name=name)
        
        return target_cls
    
    # Handle both @Repository and @Repository() syntax
    if cls is None:
        return decorator  # type: ignore
    else:
        return decorator(cls)


def TemplateController(prefix: str = "") -> Callable[[Type[T]], Type[T]]:
    """
    Mark a class as a template controller
    
    Similar to Spring MVC's @Controller annotation.
    Template controllers return ModelAndView objects for HTML responses.
    
    Args:
        prefix: URL prefix for all routes in this controller
        
    Example:
        @TemplateController("/")
        class HomeController:
            @GetMapping("/")
            def index(self) -> ModelAndView:
                return ModelAndView("index.html", {"title": "Home"})
    """
    def decorator(cls: Type[T]) -> Type[T]:
        # Store metadata on the class
        cls._is_controller = True  # type: ignore
        cls._is_template_controller = True  # type: ignore
        cls._controller_prefix = prefix  # type: ignore
        cls._routes = []  # type: ignore
        
        # Register in application context
        context = get_application_context()
        context.register_bean(cls, scope=BeanScope.SINGLETON)
        
        return cls
    
    return decorator


def Autowired(func: Callable) -> Callable:
    """
    Mark a method for dependency injection
    
    Similar to Spring Boot's @Autowired annotation.
    This is mainly for documentation purposes as dependency injection
    happens automatically in the constructor.
    
    Example:
        @Autowired
        def __init__(self, user_service: UserService):
            self.user_service = user_service
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    
    wrapper._is_autowired = True  # type: ignore
    return wrapper
