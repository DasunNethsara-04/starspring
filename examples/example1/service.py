from starspring import Service, ResponseEntity, Transactional

from entity import User
from repository import UserRepository


@Service
class UserService:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    async def get_user_by_email(self, email: str):
        return await self.user_repo.find_by_email(email)

    async def get_user_by_id(self, id: int):
        return await self.user_repo.find_by_id(id)

    async def get_user_by_username(self, username: str):
        return await self.user_repo.find_by_username(username)

    @Transactional
    async def create_user(self, name: str, email: str):
        existing: User = await self.user_repo.find_by_email(email)
        if existing:
            raise ValueError(f"User with email {email} already exists")
        user = User(name=name, email=email)
        return await self.user_repo.save(user)

    @Transactional
    async def update_user(self, id: int, name: str, email: str):
        user = await self.user_repo.find_by_id(id)
        if not user:
            raise ValueError(f"User with id {id} does not exist")
        user.name = name
        user.email = email
        return await self.user_repo.update(user)

    @Transactional
    async def deactivate_user(self, id: int):
        user = await self.user_repo.find_by_id(id)
        if not user:
            raise ValueError(f"User with id {id} does not exist")
        user.is_active = False
        return await self.user_repo.update(user)

    @Transactional
    async def activate_user(self, id: int):
        user = await self.user_repo.find_by_id(id)
        if not user:
            raise ValueError(f"User with id {id} does not exist")
        user.is_active = True
        return await self.user_repo.update(user)

    @Transactional
    async def delete_user(self, id: int):
        user = await self.user_repo.find_by_id(id)
        if not user:
            raise ValueError(f"User with id {id} does not exist")
        await self.user_repo.delete(user)
        return {"deleted": True}