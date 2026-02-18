from typing import Optional

from starspring import Repository, StarRepository

from entity import User

@Repository
class UserRepository(StarRepository[User]):
    async def find_by_email(self, email: str) -> Optional[list[User]]:
        pass

    async def find_by_is_active(self, is_active: bool) -> Optional[User]:
        pass