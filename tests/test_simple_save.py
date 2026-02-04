"""
Simple save test
"""

import sys
import asyncio
sys.path.insert(0, '.')

from pathlib import Path
from starspring import StarSpringApplication
from examples.blog_app.entities import User
from datetime import datetime

async def test_save():
    print("Testing save operation...")
    
    # Create application
    config_path = Path("examples/blog_app/application.yaml")
    app = StarSpringApplication(
        title="Test",
        debug=True,
        config_path=str(config_path)
    )
    
    app.scan_components("examples.blog_app")
    
    # Get repository
    from starspring.core.context import get_application_context
    from examples.blog_app.repositories import UserRepository
    
    ctx = get_application_context()
    user_repo = ctx.get_bean(UserRepository)
    
    # Create user
    user = User()
    user.email = "test@example.com"
    user.username = "testuser"
    user.name = "Test User"
    user.active = True
    user.created_at = datetime.now()
    user.updated_at = datetime.now()
    
    print(f"User object: {user.__dict__}")
    
    try:
        saved_user = await user_repo.save(user)
        print(f"✅ Saved user: {saved_user.username} (ID: {saved_user.id})")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_save())
