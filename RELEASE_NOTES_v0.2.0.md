# StarSpring v0.2.0 🎉

This release brings powerful new features for building web applications with HTML forms and template rendering!

## What's New

### 🚀 Major Features

**Automatic Form Data Parsing**
No more manual `await request.form()`! Forms are automatically parsed into Pydantic models:

```python
@PostMapping("/users")
async def create_user(self, form: UserCreateForm):  # Automatic!
    user = await self.user_service.create(form.name, form.email)
    return ModelAndView("success.html", {"user": user}, status_code=201)
```

**Custom HTTP Status Codes**
Set custom status codes for template responses:

```python
return ModelAndView("users/created.html", {"user": user}, status_code=201)
return ModelAndView("errors/404.html", {"message": "Not found"}, status_code=404)
```

**HTTP Method Override**
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

### 📝 Improvements
- Updated documentation with comprehensive examples
- Professional `pyproject.toml` configuration with PDM
- Better form handling for template controllers
- Cleaner build artifacts (no more bundled dependencies)

## Installation

```bash
pip install starspring==0.2.0

# Or with all optional dependencies
pip install starspring[standard]
```

## What's Changed
* Templating bug fixes by @DasunNethsara-04 in https://github.com/DasunNethsara-04/starspring/pull/2

## New Contributors
* @DasunNethsara-04 made their first contribution in https://github.com/DasunNethsara-04/starspring/pull/2

**Full Changelog**: https://github.com/DasunNethsara-04/starspring/compare/v0.1.0...v0.2.0
