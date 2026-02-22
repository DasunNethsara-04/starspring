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

        # Auto-create the database schema if needed (MySQL/MariaDB only)
        self._ensure_database_exists()

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

    def _ensure_database_exists(self) -> None:
        """
        Auto-create the MySQL/MariaDB database if it does not exist.

        Parses the database name from the URL, connects to the MySQL server
        without selecting a database, and issues CREATE DATABASE IF NOT EXISTS.
        This is a no-op for SQLite and PostgreSQL.
        """
        # Only applies to MySQL / MariaDB dialects
        if not self.url.startswith(("mysql", "mariadb")):
            return

        try:
            from sqlalchemy import create_engine, text
            from sqlalchemy.engine import make_url

            parsed = make_url(self.url)
            db_name = parsed.database
            if not db_name:
                return

            # Build the root URL manually from individual components so we
            # guarantee no database name leaks through (set(database=None)
            # is unreliable with some pymysql versions).
            driver = parsed.drivername          # e.g. mysql+pymysql
            user = parsed.username or "root"
            password = parsed.password or ""
            host = parsed.host or "localhost"
            port = parsed.port or 3306
            root_url = f"{driver}://{user}:{password}@{host}:{port}/"

            root_engine = create_engine(root_url, pool_pre_ping=False)
            with root_engine.connect() as conn:
                conn.execute(
                    text(f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
                         f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                )
            root_engine.dispose()

            logger.info(f"Database '{db_name}' is ready (created if not existed)")

        except Exception as e:
            # Non-fatal — the main engine creation will surface a clearer error
            logger.warning(f"Could not auto-create database: {e}")

    
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
