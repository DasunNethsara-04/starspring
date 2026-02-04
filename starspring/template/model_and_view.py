"""
Template engine integration

Provides Jinja2 template rendering with Spring Boot-style patterns.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import os


class ModelAndView:
    """
    Container for model and view name
    
    Similar to Spring MVC's ModelAndView.
    
    Example:
        @GetMapping("/users")
        def list_users(self) -> ModelAndView:
            users = self.user_service.find_all()
            return ModelAndView("users/list.html", {"users": users})
    """
    
    def __init__(self, view_name: str, model: Optional[Dict[str, Any]] = None):
        """
        Initialize ModelAndView
        
        Args:
            view_name: Template file name
            model: Dictionary of model attributes
        """
        self.view_name = view_name
        self.model = model or {}
    
    def add_object(self, key: str, value: Any) -> 'ModelAndView':
        """
        Add an object to the model
        
        Args:
            key: Attribute name
            value: Attribute value
            
        Returns:
            Self for method chaining
        """
        self.model[key] = value
        return self
    
    def add_all_objects(self, objects: Dict[str, Any]) -> 'ModelAndView':
        """
        Add multiple objects to the model
        
        Args:
            objects: Dictionary of attributes
            
        Returns:
            Self for method chaining
        """
        self.model.update(objects)
        return self
    
    def get_model(self) -> Dict[str, Any]:
        """Get the model dictionary"""
        return self.model
    
    def get_view_name(self) -> str:
        """Get the view name"""
        return self.view_name
