"""
Template engine for rendering HTML templates

Integrates Jinja2 with Spring Boot-style patterns.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import os


try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape, Template
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False
    Environment = None
    FileSystemLoader = None


class TemplateEngine:
    """
    Template rendering engine
    
    Wraps Jinja2 with Spring Boot-style configuration.
    """
    
    def __init__(
        self,
        template_dir: str = "templates",
        auto_reload: bool = True,
        cache_size: int = 400
    ):
        """
        Initialize template engine
        
        Args:
            template_dir: Directory containing templates
            auto_reload: Whether to reload templates on change
            cache_size: Template cache size
        """
        if not JINJA2_AVAILABLE:
            raise ImportError(
                "Jinja2 is required for template rendering. "
                "Install it with: pip install jinja2"
            )
        
        self.template_dir = template_dir
        
        # Create template directory if it doesn't exist
        Path(template_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml']),
            auto_reload=auto_reload,
            cache_size=cache_size
        )
        
        # Add custom filters and functions
        self._setup_filters()
    
    def _setup_filters(self):
        """Setup custom Jinja2 filters"""
        # Add custom filters here
        self.env.filters['format_date'] = self._format_date
        self.env.filters['format_currency'] = self._format_currency
    
    def _format_date(self, value, format='%Y-%m-%d'):
        """Format datetime objects"""
        if value is None:
            return ''
        try:
            return value.strftime(format)
        except:
            return str(value)
    
    def _format_currency(self, value, currency='$'):
        """Format currency values"""
        if value is None:
            return ''
        try:
            return f"{currency}{value:,.2f}"
        except:
            return str(value)
    
    def render(self, template_name: str, context: Dict[str, Any] = None) -> str:
        """
        Render a template
        
        Args:
            template_name: Template file name
            context: Template context variables
            
        Returns:
            Rendered HTML string
        """
        context = context or {}
        template = self.env.get_template(template_name)
        return template.render(**context)
    
    def render_string(self, template_string: str, context: Dict[str, Any] = None) -> str:
        """
        Render a template from string
        
        Args:
            template_string: Template content as string
            context: Template context variables
            
        Returns:
            Rendered HTML string
        """
        context = context or {}
        template = self.env.from_string(template_string)
        return template.render(**context)
    
    def add_global(self, name: str, value: Any):
        """
        Add a global variable to all templates
        
        Args:
            name: Variable name
            value: Variable value
        """
        self.env.globals[name] = value
    
    def add_filter(self, name: str, func: callable):
        """
        Add a custom filter
        
        Args:
            name: Filter name
            func: Filter function
        """
        self.env.filters[name] = func


# Global template engine instance
_template_engine: Optional[TemplateEngine] = None


def get_template_engine() -> TemplateEngine:
    """Get the global template engine instance"""
    global _template_engine
    if _template_engine is None:
        _template_engine = TemplateEngine()
    return _template_engine


def set_template_engine(engine: TemplateEngine):
    """Set the global template engine instance"""
    global _template_engine
    _template_engine = engine


def render_template(template_name: str, context: Dict[str, Any] = None) -> str:
    """
    Convenience function to render a template
    
    Args:
        template_name: Template file name
        context: Template context variables
        
    Returns:
        Rendered HTML string
    """
    return get_template_engine().render(template_name, context)
