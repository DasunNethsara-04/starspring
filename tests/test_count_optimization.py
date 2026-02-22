
import asyncio
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from starspring import StarSpringApplication
from starspring.core.context import get_application_context

import logging
logging.basicConfig(level=logging.INFO)

async def verify_count_optimization():
    print("=" * 70)
    import os
    # Change to example3 directory so relative imports in entities/repos work
    example_path = Path("examples/example3")
    os.chdir(example_path)
    sys.path.insert(0, ".")

    # Use existing example3 as a test bed
    config_path = Path("application.yaml")
    app = StarSpringApplication(
        title="Verification App",
        debug=True,
        config_path=str(config_path)
    )
    
    print(f"Database URL from properties: {app.properties.get('database.url')}")
    
    # Scan components
    app.scan_components("entities", "repository", "services")
    
    # Get context and beans
    ctx = get_application_context()
    
    from entities.user import User
    from repository.user_repository import UserRepository
    
    user_repo = ctx.get_bean(UserRepository)
    
    # 1. Check initial count
    initial_count = await user_repo.count()
    print(f"Initial user count: {initial_count}")
    
    # 2. Add some users
    print("Adding 5 test users...")
    for i in range(5):
        user = User(
            username=f"test_user_{i}_{initial_count}",
            email=f"test_{i}_{initial_count}@example.com",
            password="test_password"
        )
        await user_repo.save(user)
    
    # 3. Check new count
    new_count = await user_repo.count()
    print(f"New user count: {new_count}")
    
    # 4. Assert
    assert new_count == initial_count + 5
    print("\n✅ Verification SUCCESS: count() returned the correct number of records!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(verify_count_optimization())
