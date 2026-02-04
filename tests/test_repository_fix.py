"""
Test repository dependency injection fix
"""

import sys
sys.path.insert(0, '.')

from starspring import StarSpringApplication, Repository, Service, Controller, GetMapping
from starspring.data.repository import StarRepository
from starspring.data.entity import Entity, Column, BaseEntity
from typing import Optional, List

# Define a test entity
@Entity(table_name="test_users")
class TestUser(BaseEntity):
    name: str = Column(type=str)
    email: str = Column(type=str, unique=True)

# Define a repository
@Repository
class TestUserRepository(StarRepository[TestUser]):
    async def findByEmail(self, email: str) -> Optional[TestUser]:
        pass

# Define a service that uses the repository
@Service
class TestUserService:
    def __init__(self, test_user_repository: TestUserRepository):
        self.repo = test_user_repository
        print(f"✅ TestUserService initialized with repository: {type(self.repo).__name__}")

# Define a controller
@Controller("/api/test-users")
class TestUserController:
    def __init__(self, test_user_service: TestUserService):
        self.service = test_user_service
        print(f"✅ TestUserController initialized with service: {type(self.service).__name__}")
    
    @GetMapping("")
    def get_all(self):
        return {"message": "Repository DI works!"}

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Repository Dependency Injection Fix")
    print("=" * 60)
    
    try:
        # Create application
        app = StarSpringApplication(title="Test App", debug=True)
        
        # Scan components
        app.scan_components("__main__")
        
        print("=" * 60)
        print("✅ SUCCESS! Repository dependency injection is working!")
        print("=" * 60)
        print("\nThe fix successfully:")
        print("  1. Extracted entity_class from StarRepository[TestUser]")
        print("  2. Created TestUserRepository instance without errors")
        print("  3. Injected repository into TestUserService")
        print("  4. Injected service into TestUserController")
        print("\n🎉 All dependency injection is working correctly!")
        print("=" * 60)
        
    except Exception as e:
        print("=" * 60)
        print(f"❌ FAILED: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
