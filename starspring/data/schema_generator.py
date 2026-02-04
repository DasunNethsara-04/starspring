"""
Schema generator for automatic table creation

Generates database schema from entity metadata, similar to Spring Boot's ddl-auto feature.
"""

from typing import Type, List
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)


class SchemaGenerator:
    """
    Generates database schema from entity metadata
    
    Similar to Spring Boot's Hibernate ddl-auto feature.
    """
    
    def __init__(self, session):
        """
        Initialize schema generator
        
        Args:
            session: SQLAlchemy session
        """
        self.session = session
    
    def create_tables_from_entities(self, entity_classes: List[Type]) -> None:
        """
        Create database tables from entity classes
        
        Args:
            entity_classes: List of entity classes with @Entity decorator
        """
        logger.info("Creating database tables from entities...")
        
        for entity_class in entity_classes:
            if not hasattr(entity_class, '_entity_metadata'):
                logger.warning(f"Skipping {entity_class.__name__} - not an entity")
                continue
            
            try:
                self._create_table_for_entity(entity_class)
            except Exception as e:
                logger.error(f"Failed to create table for {entity_class.__name__}: {e}")
                raise
        
        self.session.commit()
        logger.info(f"Successfully created {len(entity_classes)} tables")
    
    def _create_table_for_entity(self, entity_class: Type) -> None:
        """
        Create a single table from entity metadata
        
        Args:
            entity_class: Entity class with metadata
        """
        metadata = entity_class._entity_metadata
        table_name = metadata.table_name
        
        # Check if table already exists
        check_sql = f"""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='{table_name}'
        """
        result = self.session.execute(text(check_sql))
        if result.fetchone():
            logger.debug(f"Table '{table_name}' already exists, skipping")
            return
        
        # Build CREATE TABLE statement
        columns = []
        
        for field_name, col_meta in metadata.columns.items():
            col_def = self._build_column_definition(field_name, col_meta)
            columns.append(col_def)
        
        columns_sql = ",\n    ".join(columns)
        create_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
    {columns_sql}
        )
        """
        
        logger.info(f"Creating table: {table_name}")
        self.session.execute(text(create_sql))
    
    def _build_column_definition(self, field_name: str, col_meta) -> str:
        """
        Build column definition SQL
        
        Args:
            field_name: Field name
            col_meta: Column metadata
            
        Returns:
            Column definition SQL
        """
        from datetime import datetime
        
        # Determine SQL type
        col_type = col_meta.type
        if col_type == int:
            sql_type = "INTEGER"
        elif col_type == str:
            length = col_meta.length or 255
            sql_type = f"TEXT"  # SQLite uses TEXT for all strings
        elif col_type == bool:
            sql_type = "BOOLEAN"
        elif col_type == datetime:
            sql_type = "DATETIME"
        elif col_type == float:
            sql_type = "REAL"
        else:
            sql_type = "TEXT"  # Default fallback
        
        # Build column definition
        parts = [field_name, sql_type]
        
        # Primary key
        if col_meta.primary_key:
            parts.append("PRIMARY KEY")
        
        # Auto increment
        if col_meta.auto_increment:
            parts.append("AUTOINCREMENT")
        
        # Nullable
        if not col_meta.nullable:
            parts.append("NOT NULL")
        
        # Unique
        if col_meta.unique:
            parts.append("UNIQUE")
        
        # Default value
        if col_meta.default is not None and not callable(col_meta.default):
            if isinstance(col_meta.default, bool):
                default_val = "1" if col_meta.default else "0"
            elif isinstance(col_meta.default, str):
                default_val = f"'{col_meta.default}'"
            elif isinstance(col_meta.default, (int, float)):
                default_val = str(col_meta.default)
            else:
                # Skip complex defaults
                return " ".join(parts)
            parts.append(f"DEFAULT {default_val}")
        
        return " ".join(parts)
