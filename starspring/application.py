"""
StarSpring Application

Main application class that bootstraps the framework.
"""

import inspect
import logging
from typing import List, Type, Optional, Callable
from pathlib import Path

from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.middleware import Middleware

from starspring.core.context import ApplicationContext, get_application_context, set_application_context
from starspring.config.properties import ApplicationProperties, set_properties
from starspring.config.environment import Environment, set_environment
from starspring.middleware.exception import ExceptionHandlerMiddleware
from starspring.middleware.cors import CORSConfig, create_cors_middleware
from starspring.middleware.logging import LoggingMiddleware
from starspring.decorators.routing import create_route_handler

logger = logging.getLogger(__name__)



class StarSpringApplication:
    """
    Main application class
    
    Bootstraps the StarSpring framework and creates a Starlette ASGI application.
    Similar to Spring Boot's SpringApplication.
    
    Example:
        app = StarSpringApplication()
        app.scan_components("myapp.controllers")
        app.add_cors(enable_cors())
        
        if __name__ == "__main__":
            app.run()
    """
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        debug: bool = None,
        title: str = "StarSpring Application",
        version: str = "1.0.0"
    ):
        """
        Initialize the application
        
        Args:
            config_path: Path to configuration file
            debug: Debug mode (auto-detected from environment if None)
            title: Application title
            version: Application version
        """
        # Initialize environment
        self.environment = Environment()
        set_environment(self.environment)
        
        # Set debug mode
        if debug is None:
            debug = self.environment.is_development()
        self.debug = debug
        
        # Initialize application context (reuse existing if present)
        existing_context = None
        try:
            existing_context = get_application_context()
        except:
            pass
        
        if existing_context:
            self.context = existing_context
        else:
            self.context = ApplicationContext()
            set_application_context(self.context)
        
        # Initialize properties
        self.properties = ApplicationProperties()
        if config_path:
            self.properties.load(config_path)
        elif Path("application.yaml").exists():
            self.properties.load("application.yaml")
            logger.info("Auto-loaded application.yaml")
        elif Path("application.yml").exists():
            self.properties.load("application.yml")
            logger.info("Auto-loaded application.yml")
        set_properties(self.properties)
        
        # Initialize database if configured
        self._init_database()
        
        # Application metadata
        self.title = title
        self.version = version
        
        # Middleware stack
        self._middleware: List[Middleware] = []
        
        # Routes
        self._routes: List[Route] = []
        
        # Static files
        self._static_mounts: List[Mount] = []
        
        # Lifecycle hooks
        self._startup_hooks: List[Callable] = []
        self._shutdown_hooks: List[Callable] = []
        
        # Add default middleware
        self._add_default_middleware()
        
        # Starlette app (created on demand)
        self._app: Optional[Starlette] = None
    
    def _add_default_middleware(self):
        """Add default middleware"""
        # Exception handler (should be first)
        self._middleware.append(
            Middleware(ExceptionHandlerMiddleware, debug=self.debug)
        )
        
        # Logging middleware
        self._middleware.append(
            Middleware(LoggingMiddleware)
        )
    
    def _init_database(self):
        """Initialize database connection if configured"""
        try:
            # Check if database URL is configured
            db_url = self.properties.get("database.url")
            if not db_url:
                logger.info("No database configured (database.url not found)")
                return
            
            # Import database modules
            from starspring.data.database_config import DatabaseConfig
            from starspring.data.orm_gateway import SQLAlchemyGateway, set_orm_gateway
            
            # Initialize database configuration
            db_config = DatabaseConfig()
            
            # Create and set ORM gateway
            gateway = SQLAlchemyGateway(db_config.SessionFactory)
            set_orm_gateway(gateway)
            
            logger.info("Database initialized successfully")
            
        except ImportError as e:
            logger.warning(f"Database dependencies not installed: {e}")
            logger.warning("Install with: pip install sqlalchemy")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            if self.debug:
                raise
    
    def _auto_create_tables_if_enabled(self):
        """
        Automatically create database tables from entity metadata
        
        Similar to Spring Boot's ddl-auto feature.
        Called after component scanning when entity classes are available.
        """
        try:
            from starspring.data.orm_gateway import get_orm_gateway
            from starspring.data.entity import mapper_registry
            
            # Check if ddl-auto is enabled
            ddl_auto = self.properties.get("database.ddl-auto", "create-if-not-exists")
            if ddl_auto not in ["create", "create-if-not-exists", "update"]:
                return
            
            # Get ORM gateway
            try:
                gateway = get_orm_gateway()
            except RuntimeError:
                # No database configured
                return
            
            # Use SQLAlchemy's metadata.create_all to create tables
            # This uses the imperative mappings we set up in the @Entity decorator
            # We get the engine from the gateway's session
            engine = gateway.session.get_bind()
            
            # Debug: Log what tables are registered
            table_names = list(mapper_registry.metadata.tables.keys())
            logger.info(f"Tables registered in mapper_registry: {table_names}")
            
            if not table_names:
                logger.warning("No tables found in mapper_registry.metadata! Entities may not be imported yet.")
            
            mapper_registry.metadata.create_all(engine)
            
            logger.info(f"Auto-created tables: {table_names}")
            
        except Exception as e:
            logger.error(f"Failed to auto-create tables: {e}")
            if self.debug:
                raise
    
    def add_cors(self, config: CORSConfig) -> 'StarSpringApplication':
        """
        Add CORS middleware
        
        Args:
            config: CORS configuration
            
        Returns:
            Self for chaining
        """
        # CORS should be added early in the middleware stack
        from starlette.middleware.cors import CORSMiddleware
        self._middleware.insert(1, Middleware(
            CORSMiddleware,
            **config.to_middleware_kwargs()
        ))
        return self
    
    def add_middleware(self, middleware_class, **options) -> 'StarSpringApplication':
        """
        Add custom middleware
        
        Args:
            middleware_class: Middleware class
            **options: Middleware options
            
        Returns:
            Self for chaining
        """
        self._middleware.append(Middleware(middleware_class, **options))
        return self
    
    def scan_components(self, *module_paths: str) -> 'StarSpringApplication':
        """
        Scan and register components from modules
        
        Args:
            *module_paths: Module paths to scan (e.g., "myapp.controllers")
            
        Returns:
            Self for chaining
        """
        import importlib
        import pkgutil
        
        # Initialize scanned modules list if not exists
        if not hasattr(self, '_scanned_modules'):
            self._scanned_modules = []
        
        for module_path in module_paths:
            try:
                # Import the module
                module = importlib.import_module(module_path)
                self._scanned_modules.append(module)  # Track module
                logger.debug(f"Scanning module: {module_path}")
                logger.debug(f"Registered beans: {list(self.context._beans.keys())}")
                
                # Scan for controllers and register routes
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if hasattr(obj, '_is_controller'):
                        logger.debug(f"Found controller: {name}")
                        self._register_controller(obj)
                
                # If it's a package, scan submodules
                if hasattr(module, '__path__'):
                    for importer, modname, ispkg in pkgutil.walk_packages(
                        path=module.__path__,
                        prefix=module.__name__ + '.',
                    ):
                        submodule = importlib.import_module(modname)
                        self._scanned_modules.append(submodule)  # Track submodule
                        for name, obj in inspect.getmembers(submodule, inspect.isclass):
                            if hasattr(obj, '_is_controller'):
                                self._register_controller(obj)
            
            except ImportError as e:
                logger.warning(f"Could not import module '{module_path}': {e}")
        
        # Auto-create database tables from entities
        self._auto_create_tables_if_enabled()
        
        return self
    
    def _auto_scan_components(self):
        """
        Auto-scan common component modules
        
        Attempts to import and scan standard module names like:
        controller, service, repository, entity, etc.
        """
        import importlib
        
        # Common module names to try (order matters - entities first, then repos, services, controllers)
        common_modules = [
            'entity', 'entities', 'model', 'models',
            'repository', 'repositories', 
            'service', 'services',
            'controller', 'controllers'
        ]
        
        scanned = []
        for module_name in common_modules:
            try:
                importlib.import_module(module_name)
                scanned.append(module_name)
            except ImportError:
                pass  # Module doesn't exist, skip silently
        
        if scanned:
            logger.info(f"Auto-scanned modules: {', '.join(scanned)}")
            self.scan_components(*scanned)
        else:
            logger.debug("No common modules found for auto-scanning")
    
    def _register_controller(self, controller_class: Type):
        """Register a controller and its routes"""
        # Get controller instance from context
        controller = self.context.get_bean(controller_class)
        
        # Get controller prefix
        prefix = getattr(controller_class, '_controller_prefix', '')
        
        # Scan for route methods
        for name, method in inspect.getmembers(controller_class, inspect.isfunction):
            if hasattr(method, '_route_path'):
                path = method._route_path
                methods = method._route_methods
                
                # Combine prefix and path
                full_path = f"{prefix}{path}".replace('//', '/')
                
                # Get the bound method and wrap it with request handling
                bound_method = getattr(controller, name)
                handler = create_route_handler(bound_method)
                
                # Create route
                route = Route(
                    full_path,
                    endpoint=handler,
                    methods=methods
                )
                self._routes.append(route)
                logger.debug(f"Registered route: {methods} {full_path}")
    
    def add_static_files(
        self,
        path: str,
        directory: str,
        name: str = "static"
    ) -> 'StarSpringApplication':
        """
        Add static file serving
        
        Args:
            path: URL path prefix
            directory: Directory to serve files from
            name: Mount name
            
        Returns:
            Self for chaining
        """
        self._static_mounts.append(
            Mount(path, StaticFiles(directory=directory), name=name)
        )
        return self
    
    def on_startup(self, func: Callable) -> 'StarSpringApplication':
        """
        Register a startup hook
        
        Args:
            func: Function to call on startup
            
        Returns:
            Self for chaining
        """
        self._startup_hooks.append(func)
        return self
    
    def on_shutdown(self, func: Callable) -> 'StarSpringApplication':
        """
        Register a shutdown hook
        
        Args:
            func: Function to call on shutdown
            
        Returns:
            Self for chaining
        """
        self._shutdown_hooks.append(func)
        return self
    
    def build(self) -> Starlette:
        """
        Build the Starlette application
        
        Returns:
            Configured Starlette application
        """
        if self._app is None:
            # Combine routes and static mounts
            all_routes = self._routes + self._static_mounts
            
            # Create Starlette app
            self._app = Starlette(
                debug=self.debug,
                routes=all_routes,
                middleware=self._middleware,
                on_startup=self._startup_hooks,
                on_shutdown=self._shutdown_hooks,
            )
        
        return self._app
    
    def run(
        self,
        host: str = "0.0.0.0",
        port: int = 8000,
        **uvicorn_options
    ):
        """
        Run the application with Uvicorn
        
        Args:
            host: Host to bind to
            port: Port to bind to
            **uvicorn_options: Additional Uvicorn options
        """
        import uvicorn
        
        # Auto-scan components if no manual scanning was done
        if not hasattr(self, '_scanned_modules') or not self._scanned_modules:
            self._auto_scan_components()
        
        app = self.build()
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            **uvicorn_options
        )
    
    @property
    def app(self) -> Starlette:
        """Get the Starlette application"""
        return self.build()


def create_application(
    config_path: Optional[str] = None,
    **kwargs
) -> StarSpringApplication:
    """
    Factory function to create a StarSpring application
    
    Args:
        config_path: Path to configuration file
        **kwargs: Additional application options
        
    Returns:
        StarSpring application instance
    """
    return StarSpringApplication(config_path=config_path, **kwargs)
