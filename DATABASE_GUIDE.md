# StarSpring Database & ORM Guide

A comprehensive guide to working with databases in StarSpring, including entity definition, repository patterns, and query methods.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Database Configuration](#database-configuration)
- [Defining Entities](#defining-entities)
- [Working with Repositories](#working-with-repositories)
- [Query Method Patterns](#query-method-patterns)
- [Transactions](#transactions)
- [Advanced Features](#advanced-features)
- [Troubleshooting](#troubleshooting)

---

## Overview

StarSpring provides a built-in ORM layer powered by SQLAlchemy with Spring Data-inspired repository patterns. Key features include:

- **Auto-implemented repository methods** based on naming conventions
- **Automatic table creation** from entity definitions
- **Transaction management** with the `@Transactional` decorator
- **Type-safe queries** with full async support
- **Multiple database support**: SQLite, PostgreSQL, MySQL

---

## Installation

### Database Drivers

Install the appropriate driver for your database:

**SQLite** (built-in with Python):
```bash
pip install sqlalchemy
```

**PostgreSQL**:
```bash
pip install psycopg2-binary sqlalchemy
# or for async support
pip install asyncpg sqlalchemy
```

**MySQL**:
```bash
pip install pymysql sqlalchemy
# or for async support
pip install aiomysql sqlalchemy
```

---

## Database Configuration

### Basic Configuration

Create an `application.yaml` file in your project root:

```yaml
database:
  url: "sqlite:///app.db"
  ddl-auto: "create-if-not-exists"
```

### Connection URL Formats

**SQLite**:
```yaml
database:
  url: "sqlite:///./database.db"      # Relative path
  url: "sqlite:////absolute/path.db"  # Absolute path
  url: "sqlite:///:memory:"           # In-memory database
```

**PostgreSQL**:
```yaml
database:
  url: "postgresql://user:password@localhost:5432/mydb"
  url: "postgresql://postgres:secret@db.example.com:5432/production"
```

**MySQL**:
```yaml
database:
  url: "mysql+pymysql://user:password@localhost:3306/mydb"
  url: "mysql+pymysql://root:secret@db.example.com:3306/production"
```

### Advanced Configuration

```yaml
database:
  url: "postgresql://user:password@localhost/mydb"
  ddl-auto: "create-if-not-exists"  # Options: create, create-if-not-exists, update, none
  pool-size: 10                      # Connection pool size
  max-overflow: 20                   # Maximum overflow connections
  echo: false                        # Log SQL queries (true for debugging)
  pool-pre-ping: true                # Test connections before use
```

**DDL Auto Options**:
- `create`: Drop and recreate tables on startup
- `create-if-not-exists`: Create tables only if they don't exist (recommended for development)
- `update`: Update existing schema (use with caution)
- `none`: No automatic table creation

---

## Defining Entities

### Basic Entity

Entities are Python classes decorated with `@Entity` that map to database tables:

```python
from starspring import BaseEntity, Column, Entity

@Entity(table_name="users")
class User(BaseEntity):
    # BaseEntity automatically provides: id, created_at, updated_at
    
    username = Column(type=str, unique=True, nullable=False, length=50)
    email = Column(type=str, unique=True, nullable=False)
    is_active = Column(type=bool, default=True)
    role = Column(type=str, default="USER")
```

### Column Types

StarSpring supports all standard Python types:

```python
from datetime import datetime

@Entity(table_name="posts")
class Post(BaseEntity):
    title = Column(type=str, nullable=False, length=200)
    content = Column(type=str, nullable=False)
    published = Column(type=bool, default=False)
    view_count = Column(type=int, default=0)
    rating = Column(type=float, default=0.0)
    published_at = Column(type=datetime, nullable=True)
```

### Column Options

```python
Column(
    type=str,           # Python type: str, int, bool, float, datetime
    nullable=True,      # Allow NULL values (default: True)
    unique=False,       # Unique constraint (default: False)
    default=None,       # Default value (can be a value or callable)
    length=None         # Maximum length for string columns
)
```

### BaseEntity Fields

All entities inheriting from `BaseEntity` automatically get:

- `id`: Auto-incrementing integer primary key
- `created_at`: Timestamp when record was created
- `updated_at`: Timestamp when record was last updated

---

## Working with Repositories

### Creating a Repository

Repositories provide data access methods for entities:

```python
from starspring import Repository, StarRepository
from typing import Optional
from entity import User

@Repository
class UserRepository(StarRepository[User]):
    # Auto-implemented methods - just define the signature!
    
    async def find_by_username(self, username: str) -> Optional[User]:
        pass
    
    async def find_by_email(self, email: str) -> Optional[User]:
        pass
    
    async def find_by_is_active(self, is_active: bool) -> list[User]:
        pass
```

### Built-in Repository Methods

Every `StarRepository` includes these methods:

```python
# Save or update an entity
user = User(username="john", email="john@example.com")
saved_user = await user_repo.save(user)

# Find by ID
user = await user_repo.find_by_id(1)

# Find all records
all_users = await user_repo.find_all()

# Delete an entity
await user_repo.delete(user)

# Count all records
total = await user_repo.count()
```

### Using Repositories in Services

```python
from starspring import Service, Transactional

@Service
class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    @Transactional
    async def create_user(self, username: str, email: str) -> User:
        # Check if user exists
        existing = await self.user_repo.find_by_email(email)
        if existing:
            raise ValueError(f"User with email {email} already exists")
        
        # Create and save
        user = User(username=username, email=email)
        return await self.user_repo.save(user)
    
    async def get_active_users(self) -> list[User]:
        return await self.user_repo.find_by_is_active(True)
```

---

## Query Method Patterns

StarSpring automatically implements repository methods based on their names. Just define the method signature with `pass` as the body.

### Find Operations

**Single field queries**:
```python
async def find_by_username(self, username: str) -> Optional[User]:
    pass
# SQL: SELECT * FROM users WHERE username = ?

async def find_by_email(self, email: str) -> Optional[User]:
    pass
# SQL: SELECT * FROM users WHERE email = ?
```

**Multiple field queries**:
```python
async def find_by_username_and_is_active(
    self, username: str, is_active: bool
) -> Optional[User]:
    pass
# SQL: SELECT * FROM users WHERE username = ? AND is_active = ?

async def find_by_role_and_is_active(
    self, role: str, is_active: bool
) -> list[User]:
    pass
# SQL: SELECT * FROM users WHERE role = ? AND is_active = ?
```

**Comparison operators**:
```python
async def find_by_age_greater_than(self, age: int) -> list[User]:
    pass
# SQL: SELECT * FROM users WHERE age > ?

async def find_by_age_less_than(self, age: int) -> list[User]:
    pass
# SQL: SELECT * FROM users WHERE age < ?

async def find_by_created_at_between(
    self, start: datetime, end: datetime
) -> list[User]:
    pass
# SQL: SELECT * FROM users WHERE created_at BETWEEN ? AND ?
```

**Pattern matching**:
```python
async def find_by_username_containing(self, keyword: str) -> list[User]:
    pass
# SQL: SELECT * FROM users WHERE username LIKE %?%

async def find_by_email_starting_with(self, prefix: str) -> list[User]:
    pass
# SQL: SELECT * FROM users WHERE email LIKE ?%
```

### Count Operations

```python
async def count_by_is_active(self, is_active: bool) -> int:
    pass
# SQL: SELECT COUNT(*) FROM users WHERE is_active = ?

async def count_by_role(self, role: str) -> int:
    pass
# SQL: SELECT COUNT(*) FROM users WHERE role = ?
```

### Exists Operations

```python
async def exists_by_email(self, email: str) -> bool:
    pass
# SQL: SELECT EXISTS(SELECT 1 FROM users WHERE email = ?)

async def exists_by_username(self, username: str) -> bool:
    pass
# SQL: SELECT EXISTS(SELECT 1 FROM users WHERE username = ?)
```

### Delete Operations

```python
async def delete_by_email(self, email: str) -> int:
    pass
# SQL: DELETE FROM users WHERE email = ?

async def delete_by_is_active(self, is_active: bool) -> int:
    pass
# SQL: DELETE FROM users WHERE is_active = ?
```

### Return Type Conventions

- `Optional[Entity]`: Returns single entity or None
- `list[Entity]`: Returns list of entities (can be empty)
- `int`: Returns count or number of affected rows
- `bool`: Returns True/False for exists operations

---

## Transactions

### Using @Transactional

The `@Transactional` decorator ensures database operations are atomic:

```python
from starspring import Service, Transactional

@Service
class PostService:
    def __init__(self, post_repo: PostRepository, user_repo: UserRepository):
        self.post_repo = post_repo
        self.user_repo = user_repo
    
    @Transactional
    async def publish_post(self, post_id: int, user_id: int) -> Post:
        # All operations succeed or all fail together
        post = await self.post_repo.find_by_id(post_id)
        user = await self.user_repo.find_by_id(user_id)
        
        if not post or not user:
            raise ValueError("Post or user not found")
        
        post.published = True
        post.published_at = datetime.now()
        
        # If this fails, the entire transaction rolls back
        return await self.post_repo.save(post)
```

### Transaction Behavior

- **Automatic commit**: Transaction commits if method completes successfully
- **Automatic rollback**: Transaction rolls back if an exception is raised
- **Nested transactions**: Supported via savepoints

---

## Advanced Features

### Custom Query Methods

For complex queries, implement the method body manually:

```python
from starspring.data.orm_gateway import QueryOperation

@Repository
class PostRepository(StarRepository[Post]):
    async def find_recent_published_posts(self, limit: int = 10) -> list[Post]:
        return await self._gateway.execute_query(
            "SELECT * FROM posts WHERE published = :published "
            "ORDER BY published_at DESC LIMIT :limit",
            {"published": True, "limit": limit},
            Post,
            QueryOperation.FIND
        )
    
    async def get_post_statistics(self) -> dict:
        result = await self._gateway.execute_query(
            "SELECT COUNT(*) as total, "
            "SUM(CASE WHEN published THEN 1 ELSE 0 END) as published "
            "FROM posts",
            {},
            dict,
            QueryOperation.FIND
        )
        return result[0] if result else {"total": 0, "published": 0}
```

### Relationships (Coming Soon)

Future versions will support:
- `@ManyToOne`: Many-to-one relationships
- `@OneToMany`: One-to-many relationships
- `@ManyToMany`: Many-to-many relationships

---

## Troubleshooting

### "ORM gateway not initialized"

**Cause**: Database configuration is missing or invalid.

**Solution**: Ensure `application.yaml` contains a valid `database.url`:
```yaml
database:
  url: "sqlite:///app.db"
```

### "No module named 'pymysql'" or "No module named 'psycopg2'"

**Cause**: Database driver not installed.

**Solution**: Install the appropriate driver:
```bash
# For MySQL
pip install pymysql

# For PostgreSQL
pip install psycopg2-binary
```

### "No module named 'sqlalchemy'"

**Cause**: SQLAlchemy not installed.

**Solution**:
```bash
pip install sqlalchemy
```

### Query methods not working

**Cause**: Repository doesn't extend `StarRepository[Entity]`.

**Solution**: Ensure your repository has the correct type parameter:
```python
# Wrong
class UserRepository(StarRepository):
    pass

# Correct
class UserRepository(StarRepository[User]):
    pass
```

### Table not created automatically

**Cause**: `ddl-auto` is set to `none` or entity not scanned.

**Solution**:
1. Check `application.yaml`:
   ```yaml
   database:
     ddl-auto: "create-if-not-exists"
   ```
2. Ensure entity module is scanned (auto-scanned if named `entity.py`)

### Column not appearing in database

**Cause**: Column definition missing or entity not reloaded.

**Solution**:
1. Verify column is defined with `Column()` function
2. Delete database file and restart (for SQLite in development)
3. Use `ddl-auto: create` to force table recreation (development only)

---

## Best Practices

1. **Use transactions for multi-step operations**: Always wrap multiple database operations in `@Transactional`

2. **Define specific return types**: Use `Optional[Entity]` for single results, `list[Entity]` for multiple

3. **Leverage auto-implemented methods**: Use naming conventions instead of writing SQL when possible

4. **Keep repositories focused**: One repository per entity

5. **Use services for business logic**: Don't put business logic in repositories or controllers

6. **Handle None results**: Always check for None when using `Optional` return types

7. **Use connection pooling in production**: Configure appropriate `pool-size` and `max-overflow`

8. **Enable SQL logging during development**: Set `echo: true` to debug queries

---

## Example: Complete CRUD Application

```python
# entity.py
from starspring import BaseEntity, Column, Entity

@Entity(table_name="products")
class Product(BaseEntity):
    name = Column(type=str, nullable=False, length=100)
    price = Column(type=float, nullable=False)
    in_stock = Column(type=bool, default=True)
    category = Column(type=str, nullable=False)

# repository.py
from starspring import Repository, StarRepository

@Repository
class ProductRepository(StarRepository[Product]):
    async def find_by_category(self, category: str) -> list[Product]:
        pass
    
    async def find_by_in_stock(self, in_stock: bool) -> list[Product]:
        pass
    
    async def find_by_price_less_than(self, price: float) -> list[Product]:
        pass

# service.py
from starspring import Service, Transactional

@Service
class ProductService:
    def __init__(self, product_repo: ProductRepository):
        self.product_repo = product_repo
    
    @Transactional
    async def create_product(self, name: str, price: float, category: str) -> Product:
        product = Product(name=name, price=price, category=category)
        return await self.product_repo.save(product)
    
    async def get_available_products(self) -> list[Product]:
        return await self.product_repo.find_by_in_stock(True)
    
    async def get_products_by_category(self, category: str) -> list[Product]:
        return await self.product_repo.find_by_category(category)

# controller.py
from starspring import Controller, GetMapping, PostMapping, ResponseEntity

@Controller("/api/products")
class ProductController:
    def __init__(self, product_service: ProductService):
        self.product_service = product_service
    
    @GetMapping("")
    async def list_products(self):
        products = await self.product_service.get_available_products()
        return ResponseEntity.ok(products)
    
    @GetMapping("/category/{category}")
    async def get_by_category(self, category: str):
        products = await self.product_service.get_products_by_category(category)
        return ResponseEntity.ok(products)
    
    @PostMapping("")
    async def create_product(self, name: str, price: float, category: str):
        product = await self.product_service.create_product(name, price, category)
        return ResponseEntity.created(product)
```

---

**For more examples, see the [examples directory](file:///d:/projects/frameworks/by%20antigravity/examples) in the StarSpring repository.**
