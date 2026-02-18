import email

from starspring import Service, Transactional

from entity import User
from repository import UserRepository


@Service
class UserService:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    async def get_all_users(self):
        users = await self.user_repo.find_all()
        if not users:
            return []
        return users

    async def get_users_by_email(self, email: str):
        return await self.user_repo.find_by_email(email)

    async def get_user_by_id(self, user_id: int):
        return await self.user_repo.find_by_id(user_id)

    @Transactional
    async def create_user(self, name: str, email: str, age: str):
        existing = await self.user_repo.find_by_email(email)
        if existing:
            raise ValueError(f"User with email {email} already exists")
        post = User(name=name, email=email, age=age)
        return await self.user_repo.save(post)

    @Transactional
    async def update_user(self, id: int, name: str, email: str, age: str):
        user = await self.user_repo.find_by_id(id)
        if not user:
            raise ValueError(f"User with email {email} does not exist")
        user.name = name
        user.email = email
        user.age = age
        return await self.user_repo.update(user)

    @Transactional
    async def toggle_user_state(self, id: int):
        user = await self.user_repo.find_by_id(id)
        if not user:
            raise ValueError(f"User with email {email} does not exist")
        user.is_active = not user.is_active
        await self.user_repo.update(user)
        return {"status": user.is_active}

    @Transactional
    async def delete_user(self, id: int):
        user = await self.user_repo.find_by_id(id)
        if not user:
            raise ValueError(f"User with email {email} does not exist")
        await self.user_repo.delete(user)
        return {"deleted": True}


