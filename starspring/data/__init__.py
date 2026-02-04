"""
Data package initialization
"""

from starspring.data.repository import Repository, CrudRepository, StarRepository
from starspring.data.entity import (
    Entity,
    Column,
    Id,
    GeneratedValue,
    ManyToOne,
    OneToMany,
    ManyToMany,
    BaseEntity,
    GenerationType,
    ColumnMetadata,
    RelationshipMetadata,
    EntityMetadata
)
from starspring.data.orm_gateway import ORMGateway, SQLAlchemyGateway, get_orm_gateway, set_orm_gateway
from starspring.data.transaction import Transactional
from starspring.data.query_builder import QueryMethodParser, SQLQueryGenerator

__all__ = [
    'Repository',
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
    'ColumnMetadata',
    'RelationshipMetadata',
    'EntityMetadata',
    'ORMGateway',
    'SQLAlchemyGateway',
    'get_orm_gateway',
    'set_orm_gateway',
    'Transactional',
    'QueryMethodParser',
    'SQLQueryGenerator',
]
