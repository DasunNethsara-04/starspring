"""
Repository pattern implementation

Provides Spring Boot-style repository pattern for data access with automatic query generation.
"""

from typing import TypeVar, Generic, List, Optional, Any, Type
from starspring.data.orm_gateway import get_orm_gateway
import inspect
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class Repository(Generic[T]):
    """
    Generic repository base class
    
    Provides CRUD operations for entities.
    Similar to Spring Data JPA's Repository interface.
    
    Example:
        @Repository
        class UserRepository(Repository[User]):
            def find_by_email(self, email: str) -> Optional[User]:
                # Custom query method
                pass
    """
    
    def __init__(self, entity_class: Type[T]):
        """
        Initialize repository
        
        Args:
            entity_class: The entity class this repository manages
        """
        self.entity_class = entity_class
        self._gateway_instance = None  # Lazy initialization
    
    @property
    def _gateway(self):
        """Lazy-load the ORM gateway"""
        if self._gateway_instance is None:
            self._gateway_instance = get_orm_gateway()
        return self._gateway_instance
    
    async def save(self, entity: T) -> T:
        """
        Save an entity
        
        Args:
            entity: Entity to save
            
        Returns:
            Saved entity
        """
        return await self._gateway.save(entity)
    
    async def find_by_id(self, id: Any) -> Optional[T]:
        """
        Find an entity by ID
        
        Args:
            id: Entity ID
            
        Returns:
            Entity if found, None otherwise
        """
        return await self._gateway.find_by_id(self.entity_class, id)
    
    async def find_all(self) -> List[T]:
        """
        Find all entities
        
        Returns:
            List of all entities
        """
        return await self._gateway.find_all(self.entity_class)
    
    async def delete(self, entity: T) -> None:
        """
        Delete an entity
        
        Args:
            entity: Entity to delete
        """
        await self._gateway.delete(entity)
    
    async def delete_by_id(self, id: Any) -> bool:
        """
        Delete an entity by ID
        
        Args:
            id: Entity ID
            
        Returns:
            True if deleted, False if not found
        """
        entity = await self.find_by_id(id)
        if entity:
            await self.delete(entity)
            return True
        return False
    
    async def update(self, entity: T) -> T:
        """
        Update an entity
        
        Args:
            entity: Entity to update
            
        Returns:
            Updated entity
        """
        return await self._gateway.update(entity)
    
    async def exists(self, id: Any) -> bool:
        """
        Check if an entity exists
        
        Args:
            id: Entity ID
            
        Returns:
            True if exists, False otherwise
        """
        return await self._gateway.exists(self.entity_class, id)
    
    async def count(self) -> int:
        """
        Count all entities
        
        Returns:
            Number of entities
        """
        entities = await self.find_all()
        return len(entities)


class CrudRepository(Repository[T]):
    """
    Alias for Repository
    
    Provides Spring Data JPA-style naming.
    """
    pass


class StarRepository(Repository[T]):
    """
    StarSpring repository with additional batch operations and automatic query generation
    
    Extends the base Repository with:
    - Batch operations for multiple entities
    - Automatic query method execution (findBy*, countBy*, deleteBy*, existsBy*)
    
    Example:
        @Repository
        class UserRepository(StarRepository[User]):
            # These methods are auto-implemented!
            async def findByEmail(self, email: str) -> Optional[User]:
                pass
            
            async def findByActive(self, active: bool) -> List[User]:
                pass
    """
    
    def __init__(self, entity_class: Type[T] = None):
        """
        Initialize StarRepository
        
        Args:
            entity_class: Optional entity class. If not provided, will be extracted from generic type.
        """
        # If entity_class not provided, try to extract from generic type
        if entity_class is None:
            entity_class = self._extract_entity_class()
        
        # Call parent constructor
        super().__init__(entity_class)
    
    def _extract_entity_class(self) -> Type[T]:
        """
        Extract entity class from generic type parameter
        
        Returns:
            Entity class type
        """
        import typing
        
        # Get the class's __orig_bases__ to find the generic parameter
        for base in getattr(self.__class__, '__orig_bases__', []):
            # Check if this is a generic type
            if hasattr(base, '__origin__') and hasattr(base, '__args__'):
                # Get the first type argument (the entity class)
                if base.__args__:
                    return base.__args__[0]
        
        # Fallback: raise error if we can't determine entity class
        raise ValueError(
            f"Could not determine entity class for {self.__class__.__name__}. "
            f"Please specify it as a generic parameter: class MyRepo(StarRepository[MyEntity])"
        )
    
    def __getattribute__(self, name: str):
        """
        Magic method to intercept attribute access
        
        Automatically implements query methods based on method name.
        """
        # Get the attribute normally first
        try:
            attr = object.__getattribute__(self, name)
            
            # If it's a method and it's defined (not just 'pass'), return it
            if callable(attr) and hasattr(attr, '__func__'):
                # Check if method has actual implementation (more than just 'pass' or '...')
                source = inspect.getsource(attr.__func__)
                # If it's just a stub (contains 'pass' or '...' and is short), treat as unimplemented
                is_stub = ('pass' in source or '...' in source) and len(source.strip().split('\n')) <= 3
                if not is_stub:
                    return attr
        except AttributeError:
            pass
        
        # Check if this is a query method that should be auto-implemented
        # Support both camelCase (findByUsername) and snake_case (find_by_username)
        if name.startswith(('findBy', 'countBy', 'deleteBy', 'existsBy')):
            logger.debug(f"Auto-implementing query method: {name}")
            return self._create_query_method(name, original_name=name)
        elif name.startswith(('find_by_', 'count_by_', 'delete_by_', 'exists_by_')):
            # Convert snake_case to camelCase for the parser
            logger.debug(f"Auto-implementing query method (snake_case): {name}")
            camel_name = self._snake_to_camel_method(name)
            # Pass BOTH the camelCase name (for parsing) and original name (for type hints)
            return self._create_query_method(camel_name, original_name=name)
        
        # Default behavior for everything else
        return object.__getattribute__(self, name)
    
    def _snake_to_camel_method(self, snake_name: str) -> str:
        """Convert snake_case method name to camelCase for parser"""
        parts = snake_name.split('_')
        # First part stays lowercase, capitalize rest
        return parts[0] + ''.join(word.capitalize() for word in parts[1:])
    
    
    def _create_query_method(self, method_name: str, original_name: str = None):
        """
        Create a query method dynamically
        
        Args:
            method_name: Name of the method in camelCase for parsing (e.g., 'findByUsername')
            original_name: Original method name as defined in class (e.g., 'find_by_username')
            
        Returns:
            Async function that executes the query
        """
        from starspring.data.query_builder import QueryMethodParser, SQLQueryGenerator, QueryOperation
        
        # Use original_name if provided, otherwise use method_name
        type_hint_name = original_name if original_name else method_name
        
        # Parse the method name
        try:
            parser = QueryMethodParser()
            parsed_query = parser.parse(method_name)
        except Exception as e:
            logger.error(f"Failed to parse query method '{method_name}': {e}")
            raise ValueError(f"Invalid query method name: {method_name}")
        
        # Get table name from entity metadata
        if hasattr(self.entity_class, '_entity_metadata'):
            table_name = self.entity_class._entity_metadata.table_name
        else:
            # Fallback: convert class name to snake_case
            import re
            name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', self.entity_class.__name__)
            table_name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
        
        # Generate SQL
        generator = SQLQueryGenerator(table_name)
        sql, param_names = generator.generate(parsed_query)
        
        # Create the async function
        # Helper to check return type
        import typing  # Import typing for type hint checking
        is_list_return = True # Default to list if ambiguous
        try:
            # Try to get type hints from the stub method if it exists on the class
            if hasattr(self.__class__, type_hint_name):
                 method = getattr(self.__class__, type_hint_name)
                 hints = typing.get_type_hints(method)
                 if 'return' in hints:
                     ret_type = hints['return']
                     # Check if it's a List
                     origin = getattr(ret_type, '__origin__', None)
                     if origin is list or origin is typing.List:
                         is_list_return = True
                     else:
                         # Assume single entity if not List
                         is_list_return = False
        except Exception:
            pass

        async def query_executor(*args, **kwargs):
            """Auto-generated query executor"""
            # Build parameter dictionary
            params = {}
            for i, param_name in enumerate(param_names):
                if i < len(args):
                    params[param_name] = args[i]
                elif param_name in kwargs:
                    params[param_name] = kwargs[param_name]
            
            # Execute the query through the gateway
            result = await self._gateway.execute_query(
                sql,
                params,
                self.entity_class,
                parsed_query.operation
            )
            
            # Unwrap list if expecting single result (for find operations)
            if parsed_query.operation == QueryOperation.FIND and not is_list_return:
                 if isinstance(result, list):
                     if len(result) > 0:
                         return result[0]
                     return None
            
            return result
        
        return query_executor
    
    async def save_all(self, entities: List[T]) -> List[T]:
        """
        Save multiple entities
        
        Args:
            entities: List of entities to save
            
        Returns:
            List of saved entities
        """
        result = []
        for entity in entities:
            saved = await self.save(entity)
            result.append(saved)
        return result
    
    async def delete_all(self, entities: List[T]) -> None:
        """
        Delete multiple entities
        
        Args:
            entities: List of entities to delete
        """
        for entity in entities:
            await self.delete(entity)
    
    async def delete_all_by_id(self, ids: List[Any]) -> None:
        """
        Delete multiple entities by ID
        
        Args:
            ids: List of entity IDs
        """
        for id in ids:
            await self.delete_by_id(id)
