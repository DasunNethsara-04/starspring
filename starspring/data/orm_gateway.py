"""
ORM Gateway abstraction

Provides a unified interface for different ORMs.
"""

from typing import TypeVar, Generic, List, Optional, Any, Type
from abc import ABC, abstractmethod


T = TypeVar('T')


class ORMGateway(ABC, Generic[T]):
    """
    Abstract ORM gateway interface
    
    Provides a unified interface for database operations across different ORMs.
    """
    
    @abstractmethod
    async def save(self, entity: T) -> T:
        """Save an entity"""
        pass
    
    @abstractmethod
    async def find_by_id(self, entity_class: Type[T], id: Any) -> Optional[T]:
        """Find an entity by ID"""
        pass
    
    @abstractmethod
    async def find_all(self, entity_class: Type[T]) -> List[T]:
        """Find all entities"""
        pass
    
    @abstractmethod
    async def delete(self, entity: T) -> None:
        """Delete an entity"""
        pass
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        """Update an entity"""
        pass
    
    @abstractmethod
    async def exists(self, entity_class: Type[T], id: Any) -> bool:
        """Check if an entity exists"""
        pass
    
    @abstractmethod
    async def execute_query(self, sql: str, params: dict, entity_class: Type[T], operation: str) -> Any:
        """
        Execute a custom SQL query
        
        Args:
            sql: SQL query string
            params: Query parameters
            entity_class: Entity class for result mapping
            operation: Query operation type (find, count, delete, exists)
            
        Returns:
            Query results based on operation type
        """
        pass
    
    @abstractmethod
    def begin_transaction(self):
        """Begin a transaction"""
        pass
    
    @abstractmethod
    def commit(self):
        """Commit a transaction"""
        pass
    
    @abstractmethod
    def rollback(self):
        """Rollback a transaction"""
        pass


class SQLAlchemyGateway(ORMGateway[T]):
    """
    SQLAlchemy implementation of ORM gateway
    
    Provides SQLAlchemy-specific database operations.
    """
    
    def __init__(self, session_factory):
        """
        Initialize with SQLAlchemy session factory
        
        Args:
            session_factory: SQLAlchemy sessionmaker instance
        """
        self.session_factory = session_factory
        self._session = None
        self._transaction_stack = []
    
    @property
    def session(self):
        """Get or create session"""
        if self._session is None:
            self._session = self.session_factory()
        return self._session
    
    def _auto_commit(self):
        """Commit only if not in a transaction"""
        if not self._transaction_stack and not self.session.in_transaction():
            self.session.commit()
        # Else: let the active transaction handle it
            
    # Standard commit is for transaction management (decrementing depth)
    
    async def save(self, entity: T) -> T:
        """Save an entity using SQLAlchemy ORM"""
        # Since entities are mapped imperatively, we can just use the session
        self.session.add(entity)
        # Flush to generate ID
        self.session.flush()
        self.session.refresh(entity)
        
        self._auto_commit()
        return entity
    
    async def find_by_id(self, entity_class: Type[T], id: Any) -> Optional[T]:
        """Find an entity by ID using SQLAlchemy ORM"""
        return self.session.get(entity_class, id)
    
    async def find_all(self, entity_class: Type[T]) -> List[T]:
        """Find all entities using SQLAlchemy ORM"""
        from sqlalchemy import select
        stmt = select(entity_class)
        result = self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def delete(self, entity: T) -> None:
        """Delete an entity using SQLAlchemy ORM"""
        self.session.delete(entity)
        self._auto_commit()
    
    async def update(self, entity: T) -> T:
        """Update an entity using SQLAlchemy ORM"""
        # Merge handles re-attaching detached instances
        merged = self.session.merge(entity)
        self.session.flush()
        self._auto_commit()
        return merged
    
    async def exists(self, entity_class: Type[T], id: Any) -> bool:
        """Check if an entity exists using SQLAlchemy ORM"""
        obj = self.session.get(entity_class, id)
        return obj is not None
    
    async def execute_query(self, sql: str, params: dict, entity_class: Type[T], operation: str) -> Any:
        """
        Execute a custom SQL query
        
        Note: We are slowly deprecating raw SQL strings in favor of SQLAlchemy expressions,
        but we support this for the 'query_builder' which currently generates strings.
        Ideally query_builder needs update to generate Select objects.
        """
        from sqlalchemy import text
        from starspring.data.query_builder import QueryOperation
        
        # This fallback implementation still works for raw strings generated by the old query builder
        sql_alchemy = sql
        param_values = {}
        for param_name, value in params.items():
            sql_alchemy = sql_alchemy.replace('?', f':{param_name}', 1)
            param_values[param_name] = value
            
        result = self.session.execute(text(sql_alchemy), param_values)
        
        if operation == QueryOperation.FIND or operation.value == 'find':
            # Map raw rows back to entities?
            # Issue: raw SQL returns rows, not objects if we don't use select(Entity).from_statement(...)
            # Better approach: Iterate rows and manually construct if we must, 
            # OR assume the query selects all columns matching the entity.
            
            # Since query_builder generates "SELECT * FROM ...", mapping by name is safer.
            rows = result.fetchall()
            entities = []
            cols = result.keys()
            for row in rows:
                data = {col: val for col, val in zip(cols, row)}
                entities.append(entity_class(**data))
            return entities
            
        elif operation == QueryOperation.COUNT or operation.value == 'count':
            return result.scalar()
            
        elif operation == QueryOperation.EXISTS or operation.value == 'exists':
            return result.scalar() > 0
            
        elif operation == QueryOperation.DELETE or operation.value == 'delete':
            self._auto_commit()
            return None
        
        return None
    
    # Stack to track transactions (Root + specific Nested ones)
    
    def begin_transaction(self):
        """Begin a transaction (supports nesting via SAVEPOINTs)"""
        if not self.session.in_transaction():
            # Root transaction
            txn = self.session.begin()
            self._transaction_stack.append(txn)
        else:
            # Nested transaction (SAVEPOINT)
            txn = self.session.begin_nested()
            self._transaction_stack.append(txn)
    
    def commit(self):
        """Commit the current transaction level"""
        if self._transaction_stack:
            txn = self._transaction_stack.pop()
            txn.commit()
        else:
             # Fallback if manual commit called without explicit begin
            self.session.commit()
    
    def rollback(self):
        """Rollback the current usage level"""
        if self._transaction_stack:
            txn = self._transaction_stack.pop()
            txn.rollback()
        else:
            self.session.rollback()
    
    def close(self):
        """Close the session"""
        if self._session:
            self._session.close()
            self._session = None
            self._transaction_stack = []


# Global ORM gateway instance
_orm_gateway: Optional[ORMGateway] = None


def get_orm_gateway() -> ORMGateway:
    """Get the global ORM gateway instance"""
    global _orm_gateway
    if _orm_gateway is None:
        raise RuntimeError("ORM gateway not initialized. Call set_orm_gateway() first.")
    return _orm_gateway


def set_orm_gateway(gateway: ORMGateway) -> None:
    """Set the global ORM gateway instance"""
    global _orm_gateway
    _orm_gateway = gateway
