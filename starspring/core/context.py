"""
Application context and dependency injection container

Provides Spring Boot-style dependency injection with automatic component scanning
and dependency resolution.
"""

from typing import Dict, Any, Type, TypeVar, Optional, Callable, get_type_hints
import inspect
from enum import Enum


T = TypeVar('T')


class BeanScope(Enum):
    """Bean scope types"""
    SINGLETON = "singleton"
    PROTOTYPE = "prototype"


class BeanDefinition:
    """Metadata for a registered bean"""
    
    def __init__(
        self,
        bean_class: Type,
        scope: BeanScope = BeanScope.SINGLETON,
        factory: Optional[Callable] = None,
        name: Optional[str] = None
    ):
        self.bean_class = bean_class
        self.scope = scope
        self.factory = factory
        self.name = name or bean_class.__name__
        self.instance: Optional[Any] = None


class ApplicationContext:
    """
    Application context for managing beans and dependency injection
    
    Similar to Spring's ApplicationContext, this class manages the lifecycle
    of components and handles dependency injection.
    """
    
    def __init__(self):
        self._beans: Dict[str, BeanDefinition] = {}
        self._instances: Dict[str, Any] = {}
        self._type_to_name: Dict[Type, str] = {}
    
    def register_bean(
        self,
        bean_class: Type[T],
        scope: BeanScope = BeanScope.SINGLETON,
        factory: Optional[Callable] = None,
        name: Optional[str] = None
    ) -> None:
        """
        Register a bean in the application context
        
        Args:
            bean_class: The class to register
            scope: Bean scope (singleton or prototype)
            factory: Optional factory function to create the bean
            name: Optional custom name for the bean
        """
        bean_name = name or bean_class.__name__
        bean_def = BeanDefinition(bean_class, scope, factory, bean_name)
        self._beans[bean_name] = bean_def
        self._type_to_name[bean_class] = bean_name
    
    def get_bean(self, bean_class: Type[T], name: Optional[str] = None) -> T:
        """
        Get a bean instance from the context
        
        Args:
            bean_class: The class type to retrieve
            name: Optional bean name
            
        Returns:
            Instance of the requested bean
            
        Raises:
            ValueError: If bean is not registered
        """
        bean_name = name or self._type_to_name.get(bean_class)
        
        if not bean_name or bean_name not in self._beans:
            raise ValueError(f"No bean registered for {bean_class.__name__}")
        
        bean_def = self._beans[bean_name]
        
        # For singleton scope, return cached instance
        if bean_def.scope == BeanScope.SINGLETON:
            if bean_def.instance is None:
                bean_def.instance = self._create_bean(bean_def)
            return bean_def.instance
        
        # For prototype scope, create new instance each time
        return self._create_bean(bean_def)
    
    def _create_bean(self, bean_def: BeanDefinition) -> Any:
        """
        Create a bean instance with dependency injection
        
        Args:
            bean_def: Bean definition
            
        Returns:
            New instance of the bean with dependencies injected
        """
        # Use factory if provided
        if bean_def.factory:
            return bean_def.factory()
        
        # Get constructor parameters
        sig = inspect.signature(bean_def.bean_class.__init__)
        params = {}
        
        # Get type hints for constructor
        try:
            type_hints = get_type_hints(bean_def.bean_class.__init__)
        except Exception:
            type_hints = {}
        
        # Inject dependencies
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            # Get the type annotation
            param_type = type_hints.get(param_name)
            
            if param_type and param_type in self._type_to_name:
                # Recursively get the dependency
                params[param_name] = self.get_bean(param_type)
            elif param.default != inspect.Parameter.empty:
                # Use default value if available
                params[param_name] = param.default
        
        # Create instance with injected dependencies
        return bean_def.bean_class(**params)
    
    def has_bean(self, bean_class: Type, name: Optional[str] = None) -> bool:
        """Check if a bean is registered"""
        bean_name = name or self._type_to_name.get(bean_class)
        return bean_name is not None and bean_name in self._beans
    
    def get_all_beans(self) -> Dict[str, Any]:
        """Get all singleton bean instances"""
        result = {}
        for name, bean_def in self._beans.items():
            if bean_def.scope == BeanScope.SINGLETON:
                result[name] = self.get_bean(bean_def.bean_class, name)
        return result
    
    def clear(self) -> None:
        """Clear all beans from the context"""
        self._beans.clear()
        self._instances.clear()
        self._type_to_name.clear()


# Global application context instance
_app_context: Optional[ApplicationContext] = None


def get_application_context() -> ApplicationContext:
    """Get the global application context"""
    global _app_context
    if _app_context is None:
        _app_context = ApplicationContext()
    return _app_context


def set_application_context(context: ApplicationContext) -> None:
    """Set the global application context"""
    global _app_context
    _app_context = context
