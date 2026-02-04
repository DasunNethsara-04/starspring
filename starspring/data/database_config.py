"""
Database configuration module

Provides database connection configuration for MySQL, PostgreSQL, and SQLite.
"""

from typing import Optional
from starspring.config.properties import get_properties
import logging

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """
    Database configuration
    
    Loads database settings from application properties and creates
    SQLAlchemy engine and session factory.
    """
    
    def __init__(self):
        """Initialize database configuration from properties"""
        try:
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
        except ImportError:
            raise ImportError(
                "SQLAlchemy is required for database support. "
                "Install it with: pip install sqlalchemy"
            )
        
        # Load configuration
        props = get_properties()
        
        self.url = props.get("database.url")
        if not self.url:
            raise ValueError(
                "Database URL not configured. "
                "Add 'database.url' to application.yaml"
            )
        
        self.pool_size = props.get_int("database.pool_size", 10)
        self.max_overflow = props.get_int("database.max_overflow", 20)
        self.echo = props.get_bool("database.echo", False)
        self.pool_pre_ping = props.get_bool("database.pool_pre_ping", True)
        
        # Create engine
        logger.info(f"Initializing database: {self._mask_password(self.url)}")
        
        self.engine = create_engine(
            self.url,
            pool_size=self.pool_size,
            max_overflow=self.max_overflow,
            echo=self.echo,
            pool_pre_ping=self.pool_pre_ping
        )
        
        # Create session factory
        self.SessionFactory = sessionmaker(bind=self.engine)
        
        logger.info("Database initialized successfully")
    
    def _mask_password(self, url: str) -> str:
        """Mask password in database URL for logging"""
        if '@' in url and '://' in url:
            protocol, rest = url.split('://', 1)
            if '@' in rest:
                credentials, host = rest.split('@', 1)
                if ':' in credentials:
                    user, _ = credentials.split(':', 1)
                    return f"{protocol}://{user}:****@{host}"
        return url
    
    def create_tables(self, base):
        """
        Create all tables defined in the Base metadata
        
        Args:
            base: SQLAlchemy declarative base
        """
        logger.info("Creating database tables...")
        base.metadata.create_all(self.engine)
        logger.info("Database tables created")
    
    def drop_tables(self, base):
        """
        Drop all tables defined in the Base metadata
        
        Args:
            base: SQLAlchemy declarative base
        """
        logger.warning("Dropping all database tables...")
        base.metadata.drop_all(self.engine)
        logger.info("Database tables dropped")


# Global database config instance
_database_config: Optional[DatabaseConfig] = None


def get_database_config() -> DatabaseConfig:
    """Get the global database configuration instance"""
    global _database_config
    if _database_config is None:
        _database_config = DatabaseConfig()
    return _database_config


def set_database_config(config: DatabaseConfig):
    """Set the global database configuration instance"""
    global _database_config
    _database_config = config
