from starlette.requests import Request
from starlette.responses import RedirectResponse
from starspring import TemplateController, GetMapping, PostMapping, ModelAndView

from services.user_service import UserService


@TemplateController("/admin")
class AdminController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def _require_admin(self, request: Request):
        """Returns a redirect if user is not an admin, else None."""
        if not request.session.get("username"):
            return RedirectResponse(url="/login", status_code=302)
        if request.session.get("role") != "ADMIN":
            return RedirectResponse(url="/dashboard", status_code=302)
        return None

    @GetMapping("/users")
    async def list_users(self, request: Request):
        guard = self._require_admin(request)
        if guard:
            return guard
        users = await self.user_service.get_all_users()
        return ModelAndView("admin/users.html", {
            "username": request.session.get("username"),
            "role": request.session.get("role"),
            "session_username": request.session.get("username"),
            "session_role": request.session.get("role"),
            "users": users,
        })

    @PostMapping("/users/{user_id}/delete")
    async def delete_user(self, user_id: int, request: Request):
        guard = self._require_admin(request)
        if guard:
            return guard
        try:
            await self.user_service.delete_user(user_id)
        except ValueError:
            pass
        return RedirectResponse(url="/admin/users", status_code=302)

    @PostMapping("/users/{user_id}/promote")
    async def promote_user(self, user_id: int, request: Request):
        guard = self._require_admin(request)
        if guard:
            return guard
        try:
            await self.user_service.promote_to_admin(user_id)
        except ValueError:
            pass
        return RedirectResponse(url="/admin/users", status_code=302)
