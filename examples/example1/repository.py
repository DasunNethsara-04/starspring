from typing import Optional

from starspring import Repository, StarRepository

from entity import User


@Repository
class UserRepository(StarRepository[User]):
    async def get_active_users(self, is_active: bool = True) -> Optional[list[User]]:
        pass

    async def find_by_email(self, email: str) -> Optional[User]:
        pass

    async def find_by_username(self, username: str) -> Optional[User]:
        pass
