from starspring import Service, Transactional
from starspring_security import BCryptPasswordEncoder
from entities.user import User
from repository.user_repository import UserRepository

_encoder = BCryptPasswordEncoder()


@Service
class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    @Transactional
    async def register(self, username: str, email: str, password: str) -> User:
        existing = await self.user_repository.find_by_username(username)
        if existing:
            raise ValueError(f"Username '{username}' is already taken.")

        existing_email = await self.user_repository.find_by_email(email)
        if existing_email:
            raise ValueError(f"Email '{email}' is already registered.")

        user = User(
            username=username,
            email=email,
            password=_encoder.encode(password),
            role="USER",
            is_active=True,
        )
        return await self.user_repository.save(user)

    async def authenticate(self, username: str, password: str) -> User | None:
        user = await self.user_repository.find_by_username(username)
        if user and _encoder.matches(password, user.password):
            return user
        return None

    async def get_all_users(self) -> list[User]:
        return await self.user_repository.find_all()

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self.user_repository.find_by_id(user_id)

    @Transactional
    async def delete_user(self, user_id: int):
        user = await self.user_repository.find_by_id(user_id)
        if not user:
            raise ValueError("User not found.")
        await self.user_repository.delete(user)

    @Transactional
    async def promote_to_admin(self, user_id: int) -> User:
        user = await self.user_repository.find_by_id(user_id)
        if not user:
            raise ValueError("User not found.")
        user.role = "ADMIN"
        return await self.user_repository.save(user)
