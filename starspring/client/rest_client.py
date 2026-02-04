"""
REST client utilities

Provides Spring Boot-style RestTemplate for HTTP requests.
"""

from typing import Optional, Type, TypeVar, Dict, Any
from pydantic import BaseModel
import httpx


T = TypeVar('T')


class RestTemplate:
    """
    REST client template
    
    Similar to Spring Boot's RestTemplate.
    Provides convenient methods for making HTTP requests with automatic
    JSON serialization/deserialization and Pydantic model support.
    
    Example:
        rest = RestTemplate(base_url="https://api.example.com")
        user = rest.get("/users/1", response_model=User)
        new_user = rest.post("/users", body=user_data, response_model=User)
    """
    
    def __init__(
        self,
        base_url: str = "",
        timeout: float = 30.0,
        headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize REST template
        
        Args:
            base_url: Base URL for all requests
            timeout: Request timeout in seconds
            headers: Default headers for all requests
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.default_headers = headers or {}
    
    def _build_url(self, path: str) -> str:
        """Build full URL from path"""
        if path.startswith('http://') or path.startswith('https://'):
            return path
        return f"{self.base_url}{path}"
    
    def _merge_headers(self, headers: Optional[Dict[str, str]]) -> Dict[str, str]:
        """Merge default headers with request headers"""
        merged = self.default_headers.copy()
        if headers:
            merged.update(headers)
        return merged
    
    def _serialize_body(self, body: Any) -> Dict[str, Any]:
        """Serialize request body"""
        if isinstance(body, BaseModel):
            return body.model_dump()
        elif hasattr(body, 'dict'):
            return body.dict()
        return body
    
    def _deserialize_response(
        self,
        response: httpx.Response,
        response_model: Optional[Type[T]] = None
    ) -> T:
        """Deserialize response"""
        if response_model:
            data = response.json()
            if isinstance(data, list):
                return [response_model(**item) for item in data]  # type: ignore
            return response_model(**data)
        return response.json()  # type: ignore
    
    async def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        response_model: Optional[Type[T]] = None
    ) -> T:
        """
        Make a GET request
        
        Args:
            path: Request path
            params: Query parameters
            headers: Request headers
            response_model: Pydantic model for response deserialization
            
        Returns:
            Response data
        """
        url = self._build_url(path)
        merged_headers = self._merge_headers(headers)
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=params, headers=merged_headers)
            response.raise_for_status()
            return self._deserialize_response(response, response_model)
    
    async def post(
        self,
        path: str,
        body: Any = None,
        headers: Optional[Dict[str, str]] = None,
        response_model: Optional[Type[T]] = None
    ) -> T:
        """
        Make a POST request
        
        Args:
            path: Request path
            body: Request body
            headers: Request headers
            response_model: Pydantic model for response deserialization
            
        Returns:
            Response data
        """
        url = self._build_url(path)
        merged_headers = self._merge_headers(headers)
        serialized_body = self._serialize_body(body) if body else None
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=serialized_body, headers=merged_headers)
            response.raise_for_status()
            return self._deserialize_response(response, response_model)
    
    async def put(
        self,
        path: str,
        body: Any = None,
        headers: Optional[Dict[str, str]] = None,
        response_model: Optional[Type[T]] = None
    ) -> T:
        """
        Make a PUT request
        
        Args:
            path: Request path
            body: Request body
            headers: Request headers
            response_model: Pydantic model for response deserialization
            
        Returns:
            Response data
        """
        url = self._build_url(path)
        merged_headers = self._merge_headers(headers)
        serialized_body = self._serialize_body(body) if body else None
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.put(url, json=serialized_body, headers=merged_headers)
            response.raise_for_status()
            return self._deserialize_response(response, response_model)
    
    async def delete(
        self,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        response_model: Optional[Type[T]] = None
    ) -> Optional[T]:
        """
        Make a DELETE request
        
        Args:
            path: Request path
            headers: Request headers
            response_model: Pydantic model for response deserialization
            
        Returns:
            Response data (if any)
        """
        url = self._build_url(path)
        merged_headers = self._merge_headers(headers)
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.delete(url, headers=merged_headers)
            response.raise_for_status()
            
            # DELETE might not return content
            if response.status_code == 204 or not response.content:
                return None
            
            return self._deserialize_response(response, response_model)
    
    async def patch(
        self,
        path: str,
        body: Any = None,
        headers: Optional[Dict[str, str]] = None,
        response_model: Optional[Type[T]] = None
    ) -> T:
        """
        Make a PATCH request
        
        Args:
            path: Request path
            body: Request body
            headers: Request headers
            response_model: Pydantic model for response deserialization
            
        Returns:
            Response data
        """
        url = self._build_url(path)
        merged_headers = self._merge_headers(headers)
        serialized_body = self._serialize_body(body) if body else None
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.patch(url, json=serialized_body, headers=merged_headers)
            response.raise_for_status()
            return self._deserialize_response(response, response_model)
