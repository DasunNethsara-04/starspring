from starspring import Controller, GetMapping, ResponseEntity, PostMapping, PutMapping, DeleteMapping

from service import UserService


@Controller("/api/users")
class UserController:
    def __init__(self, user_service: UserService)->None:
        self.user_service = user_service

    @GetMapping("")
    async def get_all_users(self):
        """Fetch all the users"""
        users = await self.user_service.user_repo.find_all()
        return ResponseEntity.ok(users)

    @GetMapping("/{id}")
    async def get_user_by_id(self, id):
        """Fetch a user by its id"""
        user = await self.user_service.get_user_by_id(id)
        if not user:
            return ResponseEntity.not_found({"status": "not found", "id": id})
        return ResponseEntity.ok(user)

    @GetMapping("/{username}")
    async def get_user_by_username(self, username):
        """Fetch a user by its username"""
        user = await self.user_service.get_user_by_username(username)
        if not user:
            return ResponseEntity.not_found({"status": "not found", "username": username})
        return ResponseEntity.ok(user)

    @PostMapping("")
    async def create_user(self, name: str, email: str):
        """Create a new user"""
        try:
            user = await self.user_service.create_user(name, email)
            return ResponseEntity.ok(user)
        except ValueError as e:
            return ResponseEntity.bad_request(str(e))

    @PutMapping("/{id}")
    async def update_user(self, id: int, name: str, email: str):
        """Update a user"""
        try:
            user = await self.user_service.update_user(id, name, email)
            return ResponseEntity.ok(user)
        except ValueError as e:
            return ResponseEntity.bad_request(str(e))

    @DeleteMapping("/{id}")
    async def delete_user(self, id: int):
        """Delete a user"""
        try:
            await self.user_service.delete_user(id)
            return ResponseEntity.ok({"status": "deleted", "id": id})
        except ValueError as e:
            return ResponseEntity.bad_request(str(e))
