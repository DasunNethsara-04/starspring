from starspring import Repository, StarRepository
from entities.user import User


@Repository
class UserRepository(StarRepository[User]):
    async def find_by_username(self, username: str) -> User | None:
        pass

    async def find_by_email(self, email: str) -> User | None:
        pass
