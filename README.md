# StarSpring

A Spring Boot-inspired Python web framework built on Starlette, combining the elegance of Spring's dependency injection with Python's simplicity.

## Table of Contents

- [What is StarSpring?](#what-is-starspring)
- [Key Features](#key-features)
- [Framework Comparison](#framework-comparison)
- [Core Concepts](#core-concepts)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Database & ORM](#database--orm)
- [Building REST APIs](#building-rest-apis)
- [Working with Templates](#working-with-templates)
- [Middleware](#middleware)
- [Security](#security)
- [Advanced Features](#advanced-features)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

---

## What is StarSpring?

StarSpring is a modern Python web framework that brings Spring Boot's proven architectural patterns to the Python ecosystem. It provides:

- **Dependency Injection**: Automatic component scanning and dependency resolution
- **Declarative Programming**: Annotations-based routing, services, and repositories
- **Built-in ORM**: SQLAlchemy integration with Spring Data-style repositories
- **Convention over Configuration**: Auto-configuration with sensible defaults
- **Production-Ready**: Built on Starlette for high performance and ASGI support

StarSpring is ideal for developers who appreciate Spring Boot's structure but prefer Python's ecosystem, or Python developers looking for a more opinionated, enterprise-ready framework.

---

## What's New in v0.2.2 🎉

### starspring-security Integration
Password hashing is now built into StarSpring via the companion [`starspring-security`](https://pypi.org/project/starspring-security/) package — automatically installed with StarSpring.

```python
from starspring_security import BCryptPasswordEncoder

encoder = BCryptPasswordEncoder()
hashed = encoder.encode("my_password")   # BCrypt hash
encoder.matches("my_password", hashed)   # True
```

### Session-Based Authentication
First-class support for session-based auth using Starlette's `SessionMiddleware`.

```python
from starlette.middleware.sessions import SessionMiddleware

app.add_middleware(SessionMiddleware, secret_key="your-secret-key")
```

---

## What's New in v0.2.0

### Automatic Form Data Parsing
HTML forms are now automatically parsed into Pydantic models - no more manual `await request.form()`!

```python
@PostMapping("/users")
async def create_user(self, form: UserCreateForm):  # Automatic parsing!
    user = await self.user_service.create(form.name, form.email, form.age)
    return ModelAndView("success.html", {"user": user}, status_code=201)
```

### Custom HTTP Status Codes
Set custom status codes for template responses:

```python
return ModelAndView("users/created.html", {"user": user}, status_code=201)
return ModelAndView("errors/404.html", {"message": "Not found"}, status_code=404)
```

### HTTP Method Override
Use PUT, PATCH, and DELETE methods in HTML forms with the `_method` field:

```html
<form action="/users/{{ user.id }}" method="POST">
    <input type="hidden" name="_method" value="PUT">
    <!-- form fields -->
</form>
```

```python
@PutMapping("/users/{id}")  # Works with HTML forms!
async def update_user(self, id: int, form: UserForm):
    # Handles both API requests and form submissions
```

---

## Key Features

### Dependency Injection & IoC Container
Automatic component scanning, registration, and dependency resolution with constructor injection.

### Declarative Routing
Define REST endpoints using familiar decorators like `@GetMapping`, `@PostMapping`, `@PutMapping`, and `@DeleteMapping`.

### Spring Data-Style Repositories
Auto-implemented repository methods based on naming conventions:
```python
async def find_by_username(self, username: str) -> User | None:
    pass  # Automatically implemented!
```

### Built-in ORM
SQLAlchemy integration with automatic table creation, transaction management, and entity mapping.

### Auto-Configuration
Automatically loads `application.yaml` and scans common module names (`controller`, `service`, `repository`, `entity`).

### Template Support
Jinja2 integration for server-side rendering with the `@TemplateMapping` decorator.

### Middleware Stack
Built-in exception handling, logging, CORS support, and custom middleware capabilities.

### Type Safety
Full type hint support with automatic parameter injection and validation.

---

## Framework Comparison

| Feature | StarSpring | FastAPI | Flask | Django |
|---------|-----------|---------|-------|--------|
| **Layered Architecture** | Yes | No | No | Yes |
| **Dependency Injection** | Built-in IoC | Function params | Manual/Extensions | Manual |
| **Built-in ORM** | Yes (SQLAlchemy) | No | Extension | Yes (Django ORM) |
| **Auto-Configuration** | Yes | No | No | Partial |
| **Auto-Repositories** | Yes | No | No | No |
| **Async Support** | Native (ASGI) | Native (ASGI) | Limited | Partial |
| **Template Engine** | Jinja2 | Manual | Jinja2 | Django Templates |
| **Admin Interface** | No | No | Extensions | Yes |

**When to choose StarSpring:**
- You're familiar with Spring Boot and want similar patterns in Python
- Building API-first or microservice architectures
- Need strong separation of concerns (Controller/Service/Repository)
- Want automatic dependency injection and component scanning
- Prefer convention over configuration

---

## Core Concepts

### Application Context
The IoC (Inversion of Control) container that manages component lifecycle and dependencies.

### Components
Classes decorated with `@Controller`, `@Service`, or `@Repository` are automatically discovered and registered.

### Dependency Injection
Components are injected via constructor parameters:
```python
@Controller("/api/users")
class UserController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service
```

### Entities
Domain models decorated with `@Entity` that map to database tables.

### Repositories
Data access layer with auto-implemented query methods based on method names.

### Services
Business logic layer, typically transactional, that orchestrates repositories.

### Controllers
HTTP request handlers that define REST endpoints and return responses.

---

## Installation

### Requirements
- Python 3.10 or higher
- pip or uv package manager

### Install from PyPI

```bash
pip install starspring
```

### Install for Development

```bash
git clone https://github.com/DasunNethsara-04/starspring.git
cd starspring
pip install -e .
```

### Optional Dependencies

For PostgreSQL support:
```bash
pip install psycopg2-binary
# or for async
pip install asyncpg
```

For MySQL support:
```bash
pip install pymysql
```

---

## Quick Start

### 1. Create Project Structure

```
my_app/
├── entity.py
├── repository.py
├── service.py
├── controller.py
├── main.py
└── application.yaml
```

### 2. Configure Database (`application.yaml`)

```yaml
database:
  url: "sqlite:///app.db"
  ddl-auto: "create-if-not-exists"

server:
  port: 8000
  host: "0.0.0.0"
```

### 3. Define Entity (`entity.py`)

```python
from starspring import BaseEntity, Column, Entity

@Entity(table_name="users")
class User(BaseEntity):
    # BaseEntity provides: id, created_at, updated_at
    
    username = Column(type=str, unique=True, nullable=False)
    email = Column(type=str, unique=True, nullable=False)
    is_active = Column(type=bool, default=True)
    role = Column(type=str, default="USER")
```

### 4. Create Repository (`repository.py`)

```python
from starspring import Repository, StarRepository
from entity import User

@Repository
class UserRepository(StarRepository[User]):
    # Auto-implemented based on method name!
    async def find_by_username(self, username: str) -> User | None:
        pass
    
    async def find_by_email(self, email: str) -> User | None:
        pass
```

### 5. Implement Service (`service.py`)

```python
from starspring import Service, Transactional
from entity import User
from repository import UserRepository

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
    
    async def get_user(self, username: str) -> User | None:
        return await self.user_repo.find_by_username(username)
```

### 6. Build Controller (`controller.py`)

```python
from starspring import Controller, GetMapping, PostMapping, ResponseEntity
from service import UserService

@Controller("/api/users")
class UserController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service
    
    @PostMapping("/register")
    async def register(self, username: str, email: str):
        try:
            user = await self.user_service.create_user(username, email)
            return ResponseEntity.created(user)
        except ValueError as e:
            return ResponseEntity.bad_request(str(e))
    
    @GetMapping("/{username}")
    async def get_user(self, username: str):
        user = await self.user_service.get_user(username)
        if user:
            return ResponseEntity.ok(user)
        return ResponseEntity.not_found()
    
    @GetMapping("")
    async def list_users(self):
        users = await self.user_service.user_repo.find_all()
        return ResponseEntity.ok(users)
```

### 7. Bootstrap Application (`main.py`)

```python
from starspring import StarSpringApplication

app = StarSpringApplication(title="My User API")

if __name__ == "__main__":
    app.run()
```

### 8. Run the Application

```bash
python main.py
```

Your API is now running at `http://localhost:8000`!

**Test it:**
```bash
# Register a user
curl -X POST http://localhost:8000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "email": "john@example.com"}'

# Get user
curl http://localhost:8000/api/users/john

# List all users
curl http://localhost:8000/api/users
```

---

## Database & ORM

### Configuration

StarSpring uses SQLAlchemy under the hood. Configure your database in `application.yaml`:

```yaml
database:
  url: "postgresql://user:password@localhost/mydb"
  ddl-auto: "create-if-not-exists"  # Options: create, create-if-not-exists, update, none
  pool-size: 10
  max-overflow: 20
```

**Supported databases:**
- SQLite: `sqlite:///app.db`
- PostgreSQL: `postgresql://user:pass@host/db`
- MySQL: `mysql://user:pass@host/db`

### Defining Entities

Entities are Python classes decorated with `@Entity`:

```python
from datetime import datetime
from starspring import BaseEntity, Column, Entity

@Entity(table_name="posts")
class Post(BaseEntity):
    title = Column(type=str, nullable=False, length=200)
    content = Column(type=str, nullable=False)
    published = Column(type=bool, default=False)
    author_id = Column(type=int, nullable=False)
    published_at = Column(type=datetime, nullable=True)
```

**BaseEntity provides:**
- `id`: Auto-incrementing primary key
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update

### Column Options

```python
Column(
    type=str,           # Python type (str, int, bool, datetime)
    nullable=True,      # Allow NULL values
    unique=False,       # Unique constraint
    default=None,       # Default value
    length=None         # Max length for strings
)
```

### Repository Patterns

StarSpring provides Spring Data-style repositories with auto-implemented methods:

```python
from starspring.data.query_builder import QueryOperation

@Repository
class PostRepository(StarRepository[Post]):
    # Find by single field
    async def find_by_title(self, title: str) -> Post | None:
        pass
    
    # Find by multiple fields
    async def find_by_author_id_and_published(
        self, author_id: int, published: bool
    ) -> list[Post]:
        pass
    
    # Custom queries (manual implementation)
    async def find_recent_posts(self, limit: int = 10) -> list[Post]:
        # Implement custom logic here
        return await self._gateway.execute_query(
            "SELECT * FROM posts ORDER BY created_at DESC LIMIT :limit",
            {"limit": limit},
            Post,
            QueryOperation.FIND
        )
```

**Auto-implemented method patterns:**
- `find_by_<field>` - Find by single field
- `find_by_<field>_and_<field>` - Find by multiple fields
- `count_by_<field>` - Count matching records
- `delete_by_<field>` - Delete matching records
- `exists_by_<field>` - Check if exists

**Built-in methods:**
- `save(entity)` - Insert or update
- `find_by_id(id)` - Find by primary key
- `find_all()` - Get all records
- `delete(entity)` - Delete entity
- `count()` - Count all records

### Transactions

Use the `@Transactional` decorator for automatic transaction management:

```python
from starspring import Service, Transactional

@Service
class PostService:
    def __init__(self, post_repo: PostRepository):
        self.post_repo = post_repo
    
    @Transactional
    async def publish_post(self, post_id: int) -> Post:
        post = await self.post_repo.find_by_id(post_id)
        if not post:
            raise ValueError("Post not found")
        
        post.published = True
        post.published_at = datetime.now()
        return await self.post_repo.save(post)
```

---

## Building REST APIs

### Request Mapping Decorators

```python
from starspring import (
    Controller, 
    GetMapping, 
    PostMapping, 
    PutMapping, 
    DeleteMapping,
    PatchMapping
)

@Controller("/api/posts")
class PostController:
    @GetMapping("")
    async def list_posts(self):
        # GET /api/posts
        pass
    
    @GetMapping("/{id}")
    async def get_post(self, id: int):
        # GET /api/posts/123
        pass
    
    @PostMapping("")
    async def create_post(self, title: str, content: str):
        # POST /api/posts
        pass
    
    @PutMapping("/{id}")
    async def update_post(self, id: int, title: str, content: str):
        # PUT /api/posts/123
        pass
    
    @DeleteMapping("/{id}")
    async def delete_post(self, id: int):
        # DELETE /api/posts/123
        pass
```

### Parameter Injection

StarSpring automatically injects parameters from:
- **Path variables**: `/{id}` → `id: int`
- **Query parameters**: `?page=1` → `page: int`
- **Request body**: JSON payload → function parameters

```python
@GetMapping("/search")
async def search_posts(
    self, 
    query: str,           # From ?query=...
    page: int = 1,        # From ?page=... (default: 1)
    limit: int = 10       # From ?limit=... (default: 10)
):
    # Implementation
    pass
```

### Response Handling

**Return entity directly:**
```python
@GetMapping("/{id}")
async def get_post(self, id: int):
    post = await self.post_service.get_post(id)
    return post  # Auto-serialized to JSON
```

**Use ResponseEntity for control:**
```python
from starspring import ResponseEntity

@GetMapping("/{id}")
async def get_post(self, id: int):
    post = await self.post_service.get_post(id)
    if post:
        return ResponseEntity.ok(post)
    return ResponseEntity.not_found()
```

**ResponseEntity methods:**
- `ResponseEntity.ok(body)` - 200 OK
- `ResponseEntity.created(body)` - 201 Created
- `ResponseEntity.accepted(body)` - 202 Accepted
- `ResponseEntity.no_content()` - 204 No Content
- `ResponseEntity.bad_request(body)` - 400 Bad Request
- `ResponseEntity.unauthorized(body)` - 401 Unauthorized
- `ResponseEntity.forbidden(body)` - 403 Forbidden
- `ResponseEntity.not_found(body)` - 404 Not Found
- `ResponseEntity.status(code, body)` - Custom status

### Request Body Validation

```python
from pydantic import BaseModel

class CreatePostRequest(BaseModel):
    title: str
    content: str
    published: bool = False

@PostMapping("")
async def create_post(self, request: CreatePostRequest):
    # Pydantic validates automatically
    post = await self.post_service.create_post(
        title=request.title,
        content=request.content,
        published=request.published
    )
    return ResponseEntity.created(post)
```

---

## Working with Templates

StarSpring integrates Jinja2 for server-side rendering.

### Setup Templates Directory

```
my_app/
├── templates/
│   ├── index.html
│   ├── post.html
│   └── layout.html
├── static/
│   ├── css/
│   └── js/
└── main.py
```

### Configure Template Path

```python
from starspring import StarSpringApplication

app = StarSpringApplication(title="My Blog")
app.add_template_directory("templates")
app.add_static_files("/static", "static")
```

### Template Controller

```python
from starspring import TemplateController, GetMapping, ModelAndView

@TemplateController("")
class WebController:
    def __init__(self, post_service: PostService):
        self.post_service = post_service
    
    @GetMapping("/")
    async def index(self) -> ModelAndView:
        posts = await self.post_service.get_recent_posts()
        return ModelAndView("index.html", {
            "posts": posts,
            "title": "My Blog"
        })
    
    @GetMapping("/post/{id}")
    async def view_post(self, id: int) -> ModelAndView:
        post = await self.post_service.get_post(id)
        return ModelAndView("post.html", {"post": post})
```

### Template Files

**templates/layout.html:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}My Blog{% endblock %}</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <nav>
        <a href="/">Home</a>
    </nav>
    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

**templates/index.html:**
```html
{% extends "layout.html" %}

{% block title %}{{ title }}{% endblock %}

{% block content %}
<h1>Recent Posts</h1>
{% for post in posts %}
    <article>
        <h2><a href="/post/{{ post.id }}">{{ post.title }}</a></h2>
        <p>{{ post.content[:200] }}...</p>
        <small>{{ post.created_at }}</small>
    </article>
{% endfor %}
{% endblock %}
```

---

## Middleware

### Built-in Middleware

StarSpring includes:
- **ExceptionHandlerMiddleware**: Catches and formats exceptions
- **LoggingMiddleware**: Logs requests and responses
- **CORSMiddleware**: Handles Cross-Origin Resource Sharing

### Enable CORS

```python
from starspring import StarSpringApplication
from starspring.middleware.cors import CORSConfig

app = StarSpringApplication(title="My API")

cors_config = CORSConfig(
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    allow_credentials=True
)

app.add_cors(cors_config)
```

### Custom Middleware

```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class CustomMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Before request
        print(f"Request: {request.method} {request.url}")
        
        # Process request
        response = await call_next(request)
        
        # After request
        print(f"Response: {response.status_code}")
        
        return response

# Add to application
from starlette.middleware import Middleware

app = StarSpringApplication(title="My API")
app._middleware.append(Middleware(CustomMiddleware))
```

---

## Security

### Password Hashing with `starspring-security`

StarSpring ships with [`starspring-security`](https://pypi.org/project/starspring-security/) — a standalone password hashing library that works with any Python framework.

#### BCrypt (Default — Recommended)

```python
from starspring_security import BCryptPasswordEncoder

encoder = BCryptPasswordEncoder()           # Default: rounds=12
encoder = BCryptPasswordEncoder(rounds=14)  # Stronger (slower)

hashed = encoder.encode("my_password")
encoder.matches("my_password", hashed)  # True
encoder.matches("wrong", hashed)        # False
```

#### Argon2 (Modern, Memory-Hard)

```bash
pip install starspring-security[argon2]
```

```python
from starspring_security import Argon2PasswordEncoder

encoder = Argon2PasswordEncoder()
hashed = encoder.encode("my_password")
encoder.matches("my_password", hashed)  # True
```

#### SHA-256 (Deprecated ⚠️)

```python
from starspring_security import Sha256PasswordEncoder

encoder = Sha256PasswordEncoder()  # Raises DeprecationWarning
```

SHA-256 is too fast for passwords and vulnerable to brute-force attacks. Use BCrypt or Argon2 instead.

---

### Session-Based Authentication

StarSpring supports session-based authentication via Starlette's `SessionMiddleware`. Sessions are signed using `itsdangerous` — tamper-proof out of the box.

#### Setup

```python
# main.py
from starspring import StarSpringApplication
from starlette.middleware.sessions import SessionMiddleware

app = StarSpringApplication(title="My App")
app.add_middleware(SessionMiddleware, secret_key="your-strong-secret-key")
app.run()
```

#### Using Sessions in Controllers

Inject `Request` into any controller method to read or write session data:

```python
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starspring import TemplateController, GetMapping, PostMapping, ModelAndView
from starspring_security import BCryptPasswordEncoder

encoder = BCryptPasswordEncoder()

@TemplateController("")
class AuthController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    @PostMapping("/login")
    async def login(self, form: LoginForm, request: Request):
        user = await self.user_service.find_by_username(form.username)
        if not user or not encoder.matches(form.password, user.password):
            return ModelAndView("login.html", {"error": "Invalid credentials"}, status_code=401)

        # Store user info in session
        request.session["username"] = user.username
        request.session["role"] = user.role
        return RedirectResponse(url="/dashboard", status_code=302)

    @GetMapping("/logout")
    async def logout(self, request: Request):
        request.session.clear()
        return RedirectResponse(url="/login", status_code=302)

    @GetMapping("/dashboard")
    async def dashboard(self, request: Request):
        if not request.session.get("username"):
            return RedirectResponse(url="/login", status_code=302)
        return ModelAndView("dashboard.html", {
            "username": request.session["username"],
            "role": request.session["role"],
        })
```

#### Role-Based Authorization

```python
@GetMapping("/admin/users")
async def admin_users(self, request: Request):
    if not request.session.get("username"):
        return RedirectResponse(url="/login", status_code=302)
    if request.session.get("role") != "ADMIN":
        return RedirectResponse(url="/dashboard", status_code=302)  # Forbidden
    # ... admin logic
```

#### `application.yaml` Configuration

```yaml
server:
  host: "0.0.0.0"
  port: 8000

database:
  url: "sqlite:///app.db"
  ddl-auto: "create-if-not-exists"
```

> **Note:** Keep your `secret_key` secret and never commit it to version control. Use environment variables in production.

---

## Advanced Features

### Lifecycle Hooks

```python
app = StarSpringApplication(title="My API")

@app.on_startup
async def startup():
    print("Application starting...")
    # Initialize resources

@app.on_shutdown
async def shutdown():
    print("Application shutting down...")
    # Cleanup resources
```

### Environment-Specific Configuration

```yaml
# application.yaml
spring:
  profiles:
    active: ${ENVIRONMENT:development}

---
# Development profile
spring:
  profiles: development
database:
  url: "sqlite:///dev.db"

---
# Production profile
spring:
  profiles: production
database:
  url: "postgresql://user:pass@prod-db/myapp"
```

### Manual Component Registration

```python
from starspring.core.context import get_application_context

# Register bean manually
context = get_application_context()
context.register_bean("my_service", MyService())

# Get bean
service = context.get_bean(MyService)
```

### Custom Repository Methods

```python
from starspring.data.query_builder import QueryOperation

@Repository
class PostRepository(StarRepository[Post]):
    async def find_published_posts(self) -> list[Post]:
        # Custom SQL query
        return await self._gateway.execute_query(
            "SELECT * FROM posts WHERE published = :published",
            {"published": True},
            Post,
            QueryOperation.FIND
        )
```

---

## Examples

Complete examples are available in the `examples/` directory:

- **examples/example1**: Basic CRUD API with users
- **examples/example2**: Blog application with templates and form handling
- **examples/example3**: Session-based authentication with role-based authorization and Bootstrap 5 UI

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

StarSpring is released under the MIT License. See [LICENSE](LICENSE) file for details.

---

## Support

- **Documentation**: [https://github.com/DasunNethsara-04/starspring](https://github.com/DasunNethsara-04/starspring)
- **Issues**: [https://github.com/DasunNethsara-04/starspring/issues](https://github.com/DasunNethsara-04/starspring/issues)
- **Discussions**: [https://github.com/DasunNethsara-04/starspring/discussions](https://github.com/DasunNethsara-04/starspring/discussions)

---

**Built with love for the Python community by developers who appreciate Spring Boot's elegance.**
