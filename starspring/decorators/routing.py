"""
Routing decorators for HTTP methods

Provides Spring Boot-style routing annotations like @GetMapping, @PostMapping, etc.
"""

from typing import Callable, List, Optional, Any, get_type_hints
from functools import wraps
import inspect
from pydantic import BaseModel, ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse

from starspring.core.response import ResponseEntity
from starspring.core.exceptions import StarSpringException, ValidationException


class RouteInfo:
    """Metadata for a route"""
    
    def __init__(
        self,
        path: str,
        methods: List[str],
        handler: Callable,
        handler_name: str
    ):
        self.path = path
        self.methods = methods
        self.handler = handler
        self.handler_name = handler_name


def _create_route_decorator(path: str, methods: List[str]) -> Callable:
    """
    Internal function to create route decorators
    
    Args:
        path: URL path for the route
        methods: HTTP methods for the route
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        # Store route metadata on the function
        func._route_path = path  # type: ignore
        func._route_methods = methods  # type: ignore
        # Don't wrap here - wrapping happens when route is registered
        return func
    
    return decorator


def create_route_handler(bound_method: Callable) -> Callable:
    """
    Create a route handler from a bound method
    
    This wraps the bound method with request handling logic.
    
    Args:
        bound_method: Bound controller method
        
    Returns:
        Async handler function for Starlette
    """
    # Get the original unbound function to inspect its signature
    func = bound_method.__func__ if hasattr(bound_method, '__func__') else bound_method
    
    async def handler(request: Request, **path_params):
        # Handle method override for HTML forms
        # HTML forms only support GET and POST, so we allow _method field to override
        cached_form_data = None
        if request.method == "POST":
            try:
                # Check if there's a _method field in form data
                content_type = request.headers.get("content-type", "")
                if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
                    # Read and cache form data (can only be read once)
                    cached_form_data = await request.form()
                    method_override = cached_form_data.get("_method")
                    if method_override and method_override.upper() in ["PUT", "PATCH", "DELETE"]:
                        # Override the request method
                        request.scope["method"] = method_override.upper()
            except Exception:
                # If we can't read form data, continue with original method
                pass
        
        # Get function signature and type hints
        sig = inspect.signature(func)
        try:
            type_hints = get_type_hints(func)
        except Exception:
            type_hints = {}
        
        # Prepare arguments for the handler
        kwargs = {}
        request_injected = False
        
        # Process each parameter (skip 'self' as method is already bound)
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            param_type = type_hints.get(param_name)
            
            # Check if parameter is in path parameters
            # Priority: 1. kwargs passed to handler, 2. request.path_params (from Starlette)
            if param_name in path_params:
                value = path_params[param_name]
                # Type conversion for path parameters
                if param_type and param_type != str:
                    try:
                        value = param_type(value)
                    except (ValueError, TypeError):
                        pass
                kwargs[param_name] = value
            elif request.path_params and param_name in request.path_params:
                value = request.path_params[param_name]
                # Type conversion for path parameters
                if param_type and param_type != str:
                    try:
                        value = param_type(value)
                    except (ValueError, TypeError):
                        pass
                kwargs[param_name] = value
            
            # Check if parameter is a Pydantic model (request body)
            elif param_type and (
                (inspect.isclass(param_type) and issubclass(param_type, BaseModel))
            ):
                try:
                    # Try form data first (for HTML forms)
                    content_type = request.headers.get("content-type", "")
                    if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
                        # Use cached form data if available, otherwise read it
                        form_data = cached_form_data if cached_form_data is not None else await request.form()
                        # Convert FormData to dict for Pydantic (exclude _method field)
                        form_dict = {key: value for key, value in form_data.items() if key != "_method"}
                        kwargs[param_name] = param_type(**form_dict)
                    else:
                        # Fall back to JSON for API requests
                        body = await request.json()
                        kwargs[param_name] = param_type(**body)
                except ValidationError as e:
                    raise ValidationException(
                        message="Validation failed",
                        details={"errors": e.errors()}
                    )
                except Exception:
                    # If body parsing fails, skip this parameter
                    pass
            
            # Check if parameter is Request type or named 'request' (legacy/convenience)
            elif param_type == Request or param_name in ('request', 'req'):
                kwargs[param_name] = request
                request_injected = True
            
            # Check query parameters
            elif param_name in request.query_params:
                value = request.query_params[param_name]
                # Type conversion for query parameters
                if param_type and param_type != str:
                    try:
                        value = param_type(value)
                    except (ValueError, TypeError):
                        pass
                kwargs[param_name] = value
            
            # Use default value if available
            elif param.default != inspect.Parameter.empty:
                kwargs[param_name] = param.default

            # Fallback: Inject Request object if it's a required parameter that hasn't been resolved yet
            # AND it's not a primitive type (unless we have no type hint, in which case we guess it might be request)
            elif not request_injected:
                # Don't inject into typed primitives (int, str, bool, float)
                is_primitive = param_type in (int, str, bool, float)
                
                # Try to extract from JSON body for primitives if not found yet
                json_body = None
                if is_primitive or param_type is None:
                    try:
                        # Only attempt to read body for methods that support it
                        if request.method in ["POST", "PUT", "PATCH"]:
                            # Use a cached property or similar to avoid re-reading stream if possible? 
                            # Starlette requests cache .json() result automatically after first await.
                            json_body = await request.json()
                    except Exception:
                        pass
                
                if json_body and isinstance(json_body, dict) and param_name in json_body:
                     kwargs[param_name] = json_body[param_name]
                elif not is_primitive:
                    kwargs[param_name] = request
                    request_injected = True
        
        # Call the bound method
        result = bound_method(**kwargs)
        
        # Handle async functions
        if inspect.iscoroutine(result):
            result = await result
        
        # Handle ModelAndView (template responses)
        from starspring.template import ModelAndView, render_template
        from starlette.responses import HTMLResponse
        if isinstance(result, ModelAndView):
            html_content = render_template(result.get_view_name(), result.get_model())
            return HTMLResponse(content=html_content, status_code=result.get_status_code())
        
        # Convert ResponseEntity to Starlette response
        if isinstance(result, ResponseEntity):
            return result.to_starlette_response()
        
        # Handle Pydantic models
        if hasattr(result, 'model_dump'):
            return JSONResponse(content=result.model_dump())
        elif hasattr(result, 'dict'):
            return JSONResponse(content=result.dict())
        elif hasattr(result, 'to_dict'):
            return JSONResponse(content=result.to_dict())
        
        # Handle lists (including empty lists and lists of Pydantic/Entity models)
        if isinstance(result, list):
            if len(result) == 0:
                return JSONResponse(content=[])
            elif hasattr(result[0], 'model_dump'):
                return JSONResponse(content=[item.model_dump() for item in result])
            elif hasattr(result[0], 'dict'):
                return JSONResponse(content=[item.dict() for item in result])
            elif hasattr(result[0], 'to_dict'):
                return JSONResponse(content=[item.to_dict() for item in result])
            else:
                return JSONResponse(content=result)
        
        # Handle dicts
        if isinstance(result, dict):
            return JSONResponse(content=result)
        
        # Return as-is for other types (Starlette will handle it if it's a Response, otherwise it might fail)
        return result
    
    return handler


def GetMapping(path: str) -> Callable:
    """
    Map HTTP GET requests to a handler method
    
    Similar to Spring Boot's @GetMapping annotation.
    
    Args:
        path: URL path for the route
        
    Example:
        @GetMapping("/users/{id}")
        def get_user(self, id: int):
            return user
    """
    return _create_route_decorator(path, ["GET"])


def PostMapping(path: str) -> Callable:
    """
    Map HTTP POST requests to a handler method
    
    Similar to Spring Boot's @PostMapping annotation.
    
    Args:
        path: URL path for the route
        
    Example:
        @PostMapping("/users")
        def create_user(self, user: UserCreateRequest):
            return created_user
    """
    return _create_route_decorator(path, ["POST"])


def PutMapping(path: str) -> Callable:
    """
    Map HTTP PUT requests to a handler method
    
    Similar to Spring Boot's @PutMapping annotation.
    
    Args:
        path: URL path for the route
        
    Example:
        @PutMapping("/users/{id}")
        def update_user(self, id: int, user: UserUpdateRequest):
            return updated_user
    """
    return _create_route_decorator(path, ["PUT", "POST"])


def DeleteMapping(path: str) -> Callable:
    """
    Map HTTP DELETE requests to a handler method
    
    Similar to Spring Boot's @DeleteMapping annotation.
    
    Args:
        path: URL path for the route
        
    Example:
        @DeleteMapping("/users/{id}")
        def delete_user(self, id: int):
            return ResponseEntity.no_content()
    """
    return _create_route_decorator(path, ["DELETE", "POST"])


def PatchMapping(path: str) -> Callable:
    """
    Map HTTP PATCH requests to a handler method
    
    Similar to Spring Boot's @PatchMapping annotation.
    
    Args:
        path: URL path for the route
        
    Example:
        @PatchMapping("/users/{id}")
        def patch_user(self, id: int, updates: dict):
            return patched_user
    """
    return _create_route_decorator(path, ["PATCH", "POST"])


def RequestMapping(path: str, methods: Optional[List[str]] = None) -> Callable:
    """
    Map HTTP requests to a handler method
    
    Similar to Spring Boot's @RequestMapping annotation.
    
    Args:
        path: URL path for the route
        methods: List of HTTP methods (defaults to GET)
        
    Example:
        @RequestMapping("/users", methods=["GET", "POST"])
        def handle_users(self):
            return users
    """
    if methods is None:
        methods = ["GET"]
    return _create_route_decorator(path, methods)
