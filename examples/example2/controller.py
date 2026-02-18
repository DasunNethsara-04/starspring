from pydantic import BaseModel
from starspring import TemplateController, GetMapping, ModelAndView, PostMapping, PutMapping, DeleteMapping, \
    PatchMapping

from service import UserService


class UserCreateForm(BaseModel):
    name: str
    email: str
    age: int


@TemplateController("")
class WebController:
    def __init__(self, user_service: UserService) -> None:
        self.user_service = user_service

    @GetMapping("/")
    async def index(self):
        return ModelAndView("index.html", {
            "title": "Welcome",
            "message": "Hello from StarSpring"
        })

    @GetMapping("/create-user")
    async def add_user(self):
        return ModelAndView("/users/create-user.html", {})

    @PostMapping("/create-user")
    async def create_user(self, form: UserCreateForm):
        if not form.name or not form.email or not form.age:
            return ModelAndView("/users/create-user.html", {
                "success": False,
                "title": "Error",
                "message": "Name/Email/Age required!"
            }, status_code=400)
        try:
            # Form data is now automatically parsed into the Pydantic model!
            user = await self.user_service.create_user(form.name, form.email, form.age)

            return ModelAndView("/users/create-user.html", {
                "success": True,
                "user": user,
                "message": "User created successfully!"
            }, status_code=201)
        except ValueError as e:
            return ModelAndView("/users/create-user.html", {
                "success": False,
                "title": "Error",
                "message": str(e)
            }, status_code=400)

    @GetMapping("/all-users")
    async def all_users(self):
        users = await self.user_service.get_all_users()
        if len(users) == 0:
            return ModelAndView("/users/all-users.html", {
                "success": False,
                "message": "No users found!",
                "users": []
            }, status_code=404)
        return ModelAndView("/users/all-users.html", {
            "success": True,
            "users": users
        }, status_code=200)

    @GetMapping("/users/{id}/edit")
    async def edit_user(self, id: int):
        user = await self.user_service.get_user_by_id(id)
        if user is None:
            return ModelAndView("/users/all-users.html", {
                "success": False,
                "title": "Error",
                "message": "User not found!"
            }, status_code=404)
        return ModelAndView("/users/edit-user.html", {
            "success": True,
            "user": user,
        }, status_code=200)

    @PutMapping("/users/{id}/edit")
    async def update_user(self, id: int, form: UserCreateForm):
        if not form.name or not form.email or not form.age:
            return ModelAndView("/users/create-user.html", {
                "success": False,
                "title": "Error",
                "message": "Name/Email/Age required!"
            }, status_code=400)
        try:
            user = await self.user_service.update_user(id, form.name, form.email, form.age)
            return ModelAndView("/users/edit-user.html", {
                "success": True,
                "user": user,
                "message": "User updated successfully!"
            }, status_code=200)
        except ValueError as e:
            return ModelAndView("/users/edit-user.html", {
                "success": False,
                "title": "Error",
                "message": str(e)
            }, status_code=400)

    @PatchMapping("/users/{id}/toggle")
    async def deactivate_user(self, id: int):
        try:
            status = await self.user_service.toggle_user_state(id)
            users = await self.user_service.get_all_users()
            return ModelAndView("/users/all-users.html", {
                "success": True,
                "message": "User activated!" if status else "User deactivated!",
                "users": users
            }, status_code=200)
        except ValueError as e:
            return ModelAndView("/users/edit-user.html", {
                "success": False,
                "title": "Error",
                "message": str(e)
            }, status_code=400)

    @DeleteMapping("/users/{id}/delete")
    async def delete_user(self, id: int):
        users = await self.user_service.get_all_users()
        try:
            await self.user_service.delete_user(id)
            return ModelAndView("/users/all-users.html", {
                "success": True,
                "message": "User deleted successfully!",
                "users": users
            }, status_code=200)
        except ValueError as e:
            return ModelAndView("/users/all-users.html", {
                "success": False,
                "title": "Error",
                "users": users,
                "message": str(e)
            }, status_code=400)
