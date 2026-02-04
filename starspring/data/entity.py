"""
Entity decorators and base classes for ORM

Provides Spring Boot-style entity annotations for database models.
"""

from typing import Any, Optional, Type, TypeVar, List, get_type_hints
from datetime import datetime
from enum import Enum
import inspect


T = TypeVar('T')


class GenerationType(Enum):
    """ID generation strategies"""
    AUTO = "auto"
    IDENTITY = "identity"
    SEQUENCE = "sequence"
    UUID = "uuid"


class ColumnMetadata:
    """Metadata for a database column"""
    
    def __init__(
        self,
        name: Optional[str] = None,
        type: Optional[Type] = None,
        nullable: bool = True,
        unique: bool = False,
        default: Any = None,
        length: Optional[int] = None,
        primary_key: bool = False,
        auto_increment: bool = False
    ):
        self.name = name
        self.type = type
        self.nullable = nullable
        self.unique = unique
        self.default = default
        self.length = length
        self.primary_key = primary_key
        self.auto_increment = auto_increment


class RelationshipMetadata:
    """Metadata for entity relationships"""
    
    def __init__(
        self,
        target_entity: Type,
        relationship_type: str,
        mapped_by: Optional[str] = None,
        cascade: Optional[List[str]] = None,
        lazy: bool = True
    ):
        self.target_entity = target_entity
        self.relationship_type = relationship_type
        self.mapped_by = mapped_by
        self.cascade = cascade or []
        self.lazy = lazy


class EntityMetadata:
    """Metadata for an entity class"""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.columns: dict[str, ColumnMetadata] = {}
        self.relationships: dict[str, RelationshipMetadata] = {}
        self.primary_key: Optional[str] = None


# SQLAlchemy integration
from sqlalchemy.orm import registry as SARegistry
from sqlalchemy import Table, Column as SAColumn, Integer, String, Boolean, DateTime, MetaData, ForeignKey
from sqlalchemy.types import TypeEngine

# Global registry for imperative mapping
mapper_registry = SARegistry()

def _get_sa_type(py_type: Type) -> TypeEngine:
    """Convert Python type to SQLAlchemy type"""
    if py_type == int:
        return Integer
    elif py_type == str:
        return String
    elif py_type == bool:
        return Boolean
    elif py_type == datetime:
        return DateTime
    return String  # Default fallback

def Entity(table_name: Optional[str] = None):
    """
    Mark a class as a database entity
    
    Similar to JPA's @Entity annotation.
    """
    def decorator(cls: Type[T]) -> Type[T]:
        # Generate table name from class name if not provided
        if table_name is None:
            import re
            name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
            name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
            final_table_name = name
        else:
            final_table_name = table_name
        
        # Store entity metadata (legacy support for parsing)
        metadata = EntityMetadata(final_table_name)
        cls._entity_metadata = metadata  # type: ignore
        cls._is_entity = True  # type: ignore
        
        # Columns list for SQLAlchemy Table
        sa_columns = []
        processed_fields = set()  # Track which fields we've already processed
        
        # Process class annotations to find columns WITH type hints
        if hasattr(cls, '__annotations__'):
            type_hints = get_type_hints(cls)
            for field_name, field_type in type_hints.items():
                # Check if field has column metadata
                if hasattr(cls, field_name):
                    field_value = getattr(cls, field_name)
                    if isinstance(field_value, ColumnMetadata):
                        # Update metadata
                        field_value.name = field_value.name or field_name
                        field_value.type = field_value.type or field_type
                        metadata.columns[field_name] = field_value
                        processed_fields.add(field_name)
                        
                        if field_value.primary_key:
                            metadata.primary_key = field_name
                            
                        # Create SQLAlchemy Column
                        sa_col_args = [
                            field_value.name,
                            _get_sa_type(field_value.type)
                        ]
                        
                        sa_col_kwargs = {
                            'nullable': field_value.nullable,
                            'unique': field_value.unique,
                            'primary_key': field_value.primary_key
                        }
                        
                        if field_value.auto_increment:
                            sa_col_kwargs['autoincrement'] = True
                            
                        # Handle defaults
                        # Note: We rely on BaseEntity.__init__ for python-side defaults mostly,
                        # but we can set server defaults here if needed.
                        # For now, we skip server_default to keep logic simple and consistent with BaseEntity.
                            
                        sa_columns.append(SAColumn(*sa_col_args, **sa_col_kwargs))
                        
                        # CRITICAL FIX: Remove the attribute from the class so SQLAlchemy can 
                        # install its instrumented descriptor. If we leave the ColumnMetadata object,
                        # SQLAlchemy might not replace it, detecting it as a user-defined default.
                        if field_name in cls.__dict__:
                            delattr(cls, field_name)
        
        # ALSO process class attributes that are ColumnMetadata but WITHOUT type annotations
        # This handles cases like: username = Column(unique=True)
        for field_name in list(cls.__dict__.keys()):
            if field_name.startswith('_') or field_name in processed_fields:
                continue  # Skip private/processed fields
                
            field_value = getattr(cls, field_name)
            if isinstance(field_value, ColumnMetadata):
                # Infer type from ColumnMetadata.type if available, otherwise default to str
                field_type = field_value.type or str
                
                # Update metadata
                field_value.name = field_value.name or field_name
                field_value.type = field_type
                metadata.columns[field_name] = field_value
                
                if field_value.primary_key:
                    metadata.primary_key = field_name
                    
                # Create SQLAlchemy Column
                sa_col_args = [
                    field_value.name,
                    _get_sa_type(field_value.type)
                ]
                
                sa_col_kwargs = {
                    'nullable': field_value.nullable,
                    'unique': field_value.unique,
                    'primary_key': field_value.primary_key
                }
                
                if field_value.auto_increment:
                    sa_col_kwargs['autoincrement'] = True
                    
                sa_columns.append(SAColumn(*sa_col_args, **sa_col_kwargs))
                
                # Remove the attribute from the class
                if field_name in cls.__dict__:
                    delattr(cls, field_name)
        
        # Create SQLAlchemy Table and Map
        # Check if already mapped to avoid double mapping on reloads
        try:
            # We map strictly if not already mapped.
            # Using imperative mapping pattern.
            table = Table(final_table_name, mapper_registry.metadata, *sa_columns, extend_existing=True)
            mapper_registry.map_imperatively(cls, table)
        except Exception:
            # If mapping fails (e.g. already mapped), we ignore for now or log
            pass
            
        return cls
    
    return decorator


def Column(
    name: Optional[str] = None,
    type: Optional[Type] = None,
    nullable: bool = True,
    unique: bool = False,
    default: Any = None,
    length: Optional[int] = None
):
    """
    Define a database column
    
    Similar to JPA's @Column annotation.
    
    Args:
        name: Column name in database
        type: Column data type
        nullable: Whether column can be NULL
        unique: Whether column must be unique
        default: Default value
        length: Maximum length for string columns
        
    Example:
        @Column(name="email_address", unique=True, nullable=False)
        email: str
    """
    return ColumnMetadata(
        name=name,
        type=type,
        nullable=nullable,
        unique=unique,
        default=default,
        length=length
    )


def Id():
    """
    Mark a field as the primary key
    
    Similar to JPA's @Id annotation.
    
    Example:
        @Id
        @Column(type=int)
        id: int
    """
    return ColumnMetadata(primary_key=True)


def GeneratedValue(strategy: GenerationType = GenerationType.AUTO):
    """
    Mark a field as auto-generated
    
    Similar to JPA's @GeneratedValue annotation.
    
    Args:
        strategy: Generation strategy
        
    Example:
        @Id
        @GeneratedValue(strategy=GenerationType.IDENTITY)
        @Column(type=int)
        id: int
    """
    return ColumnMetadata(auto_increment=True, primary_key=True)


def ManyToOne(target_entity: Type, lazy: bool = True):
    """
    Define a many-to-one relationship
    
    Similar to JPA's @ManyToOne annotation.
    
    Args:
        target_entity: Target entity class
        lazy: Whether to lazy load the relationship
        
    Example:
        @ManyToOne(target_entity=User)
        author: User
    """
    return RelationshipMetadata(
        target_entity=target_entity,
        relationship_type="many_to_one",
        lazy=lazy
    )


def OneToMany(target_entity: Type, mapped_by: str, cascade: Optional[List[str]] = None):
    """
    Define a one-to-many relationship
    
    Similar to JPA's @OneToMany annotation.
    
    Args:
        target_entity: Target entity class
        mapped_by: Field name in target entity that owns the relationship
        cascade: Cascade operations
        
    Example:
        @OneToMany(target_entity=Comment, mapped_by="post")
        comments: List[Comment]
    """
    return RelationshipMetadata(
        target_entity=target_entity,
        relationship_type="one_to_many",
        mapped_by=mapped_by,
        cascade=cascade or []
    )


def ManyToMany(target_entity: Type, mapped_by: Optional[str] = None):
    """
    Define a many-to-many relationship
    
    Similar to JPA's @ManyToMany annotation.
    
    Args:
        target_entity: Target entity class
        mapped_by: Field name in target entity (if this is the inverse side)
        
    Example:
        @ManyToMany(target_entity=Tag)
        tags: List[Tag]
    """
    return RelationshipMetadata(
        target_entity=target_entity,
        relationship_type="many_to_many",
        mapped_by=mapped_by
    )


class BaseEntity:
    """
    Base class for all entities
    
    Provides common fields like id, created_at, updated_at.
    Similar to Spring Data JPA's base entity pattern.
    """
    
    id: int = GeneratedValue()
    created_at: datetime = Column(type=datetime, nullable=False, default=datetime.now)
    updated_at: datetime = Column(type=datetime, nullable=False, default=datetime.now)
    
    def __init__(self, **kwargs):
        # First, set provided values from kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
            
        # Then, check for missing values that have defaults in metadata
        if hasattr(self.__class__, '_entity_metadata'):
            metadata: EntityMetadata = self.__class__._entity_metadata
            for col_name, col_meta in metadata.columns.items():
                # If attribute is not set explicitly (or is still the class-level ColumnMetadata), resolve default
                # We check if it's in kwargs first.
                if col_name not in kwargs:
                    # Check current value on instance - might be the class attribute (ColumnMetadata)
                    current_val = getattr(self, col_name, None)
                    
                    # If it's a ColumnMetadata object or missing, we need to try to set a default
                    if isinstance(current_val, ColumnMetadata) or current_val is None:
                        if col_meta.default is not None:
                            if callable(col_meta.default):
                                setattr(self, col_name, col_meta.default())
                            else:
                                setattr(self, col_name, col_meta.default)
                        elif col_meta.nullable:
                            setattr(self, col_name, None)
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={getattr(self, 'id', None)})>"
    
    def to_dict(self) -> dict:
        """Convert entity to dictionary"""
        result = {}
        if hasattr(self.__class__, '_entity_metadata'):
            metadata: EntityMetadata = self.__class__._entity_metadata
            for field_name in metadata.columns.keys():
                if hasattr(self, field_name):
                    value = getattr(self, field_name)
                    # Handle datetime serialization
                    if isinstance(value, datetime):
                        result[field_name] = value.isoformat()
                    else:
                        result[field_name] = value
        return result
