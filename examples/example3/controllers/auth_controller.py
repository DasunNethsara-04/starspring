from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starspring import TemplateController, GetMapping, PostMapping, ModelAndView

from services.user_service import UserService


class LoginForm(BaseModel):
    username: str
    password: str


class RegisterForm(BaseModel):
    username: str
    email: str
    password: str
    confirm_password: str


@TemplateController("")
class AuthController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    @GetMapping("/")
    async def home(self, request: Request):
        if request.session.get("username"):
            return RedirectResponse(url="/dashboard", status_code=302)
        return ModelAndView("home.html", {})

    @GetMapping("/login")
    async def login_page(self, request: Request):
        if request.session.get("user"):
            return RedirectResponse(url="/dashboard", status_code=302)
        return ModelAndView("auth/login.html", {})

    @PostMapping("/login")
    async def login(self, form: LoginForm, request: Request):
        user = await self.user_service.authenticate(form.username, form.password)
        if not user:
            return ModelAndView("auth/login.html", {
                "error": "Invalid username or password."
            }, status_code=401)
        if not user.is_active:
            return ModelAndView("auth/login.html", {
                "error": "Your account is deactivated."
            }, status_code=403)

        request.session["user_id"] = user.id
        request.session["username"] = user.username
        request.session["role"] = user.role
        return RedirectResponse(url="/dashboard", status_code=302)

    @GetMapping("/register")
    async def register_page(self, request: Request):
        if request.session.get("user"):
            return RedirectResponse(url="/dashboard", status_code=302)
        return ModelAndView("auth/register.html", {})

    @PostMapping("/register")
    async def register(self, form: RegisterForm, request: Request):
        if form.password != form.confirm_password:
            return ModelAndView("auth/register.html", {
                "error": "Passwords do not match."
            }, status_code=400)
        try:
            user = await self.user_service.register(form.username, form.email, form.password)
            request.session["user_id"] = user.id
            request.session["username"] = user.username
            request.session["role"] = user.role
            return RedirectResponse(url="/dashboard", status_code=302)
        except ValueError as e:
            return ModelAndView("auth/register.html", {
                "error": str(e)
            }, status_code=400)

    @GetMapping("/logout")
    async def logout(self, request: Request):
        request.session.clear()
        return RedirectResponse(url="/login", status_code=302)

    @GetMapping("/dashboard")
    async def dashboard(self, request: Request):
        if not request.session.get("username"):
            return RedirectResponse(url="/login", status_code=302)
        return ModelAndView("dashboard.html", {
            "username": request.session.get("username"),
            "role": request.session.get("role"),
            "session_username": request.session.get("username"),
            "session_role": request.session.get("role"),
        })
