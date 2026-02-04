"""
Template package initialization
"""

from starspring.template.model_and_view import ModelAndView
from starspring.template.engine import (
    TemplateEngine,
    get_template_engine,
    set_template_engine,
    render_template
)

__all__ = [
    'ModelAndView',
    'TemplateEngine',
    'get_template_engine',
    'set_template_engine',
    'render_template',
]
