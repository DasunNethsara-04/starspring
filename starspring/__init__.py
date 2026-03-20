"""
StarSpring - Spring Boot-inspired Python Web Framework

A Python web framework built on Starlette that provides Spring Boot-inspired
syntax and patterns, including dependency injection, decorator-based routing,
repository patterns, ORM, template engine, and comprehensive middleware support.
"""

from starspring.application import StarSpringApplication, create_application

# Core components
from starspring.core.context import ApplicationContext, BeanScope
from starspring.core.controller import BaseController
from starspring.core.response import ResponseEntity, ApiResponse
from starspring.core.exceptions import (
    StarSpringException,
    NotFoundException,
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    ConflictException,
    ValidationException,
    InternalServerException
)

# Decorators
from starspring.decorators.components import (
    Controller,
    TemplateController,
    Service,
    Component,
    Repository,
    Autowired
)
from starspring.decorators.routing import (
    GetMapping,
    PostMapping,
    PutMapping,
    DeleteMapping,
    PatchMapping,
    RequestMapping
)
from starspring.decorators.configuration import (
    Configuration,
    Bean,
    Value
)

# Data layer
from starspring.data.repository import Repository as RepositoryBase, CrudRepository, StarRepository
from starspring.data.entity import (
    Entity,
    Column,
    Id,
    GeneratedValue,
    ManyToOne,
    OneToMany,
    ManyToMany,
    BaseEntity,
    GenerationType
)
from starspring.data.transaction import Transactional

# Template engine
from starspring.template import ModelAndView, TemplateEngine, render_template

# Middleware
from starspring.middleware.cors import enable_cors, CORSConfig

# Configuration
from starspring.config.properties import ApplicationProperties
from starspring.config.environment import Environment

# Client
from starspring.client.rest_client import RestTemplate

__version__ = "0.2.2"

__all__ = [
    # Application
    'StarSpringApplication',
    'create_application',
    
    # Core
    'ApplicationContext',
    'BeanScope',
    'BaseController',
    'ResponseEntity',
    'ApiResponse',
    
    # Exceptions
    'StarSpringException',
    'NotFoundException',
    'BadRequestException',
    'UnauthorizedException',
    'ForbiddenException',
    'ConflictException',
    'ValidationException',
    'InternalServerException',
    
    # Component decorators
    'Controller',
    'TemplateController',
    'Service',
    'Component',
    'Repository',
    'Autowired',
    
    # Routing decorators
    'GetMapping',
    'PostMapping',
    'PutMapping',
    'DeleteMapping',
    'PatchMapping',
    'RequestMapping',
    
    # Configuration decorators
    'Configuration',
    'Bean',
    'Value',
    
    # Data layer
    'RepositoryBase',
    'CrudRepository',
    'StarRepository',
    'Entity',
    'Column',
    'Id',
    'GeneratedValue',
    'ManyToOne',
    'OneToMany',
    'ManyToMany',
    'BaseEntity',
    'GenerationType',
    'Transactional',
    
    # Template engine
    'ModelAndView',
    'TemplateEngine',
    'render_template',
    
    # Middleware
    'enable_cors',
    'CORSConfig',
    
    # Configuration
    'ApplicationProperties',
    'Environment',
    
    # Client
    'RestTemplate',
]
