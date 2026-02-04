"""
Minimal save test
"""

import sys
import asyncio
sys.path.insert(0, '.')

from pathlib import Path
from starspring import StarSpringApplication
from datetime import datetime

async def test_save():
    print("Testing minimal save...")
    
    # Create application
    config_path = Path("examples/blog_app/application.yaml")
    app = StarSpringApplication(
        title="Test",
        debug=False,
        config_path=str(config_path)
    )
    
    app.scan_components("examples.blog_app")
    
    # Get ORM gateway directly
    from starspring.data.orm_gateway import get_orm_gateway
    from sqlalchemy import text
    
    gateway = get_orm_gateway()
    
    # Try direct SQL insert
    sql = """
    INSERT INTO users (email, username, name, bio, active, created_at, updated_at)
    VALUES (:email, :username, :name, :bio, :active, :created_at, :updated_at)
    """
    
    params = {
        "email": "test@example.com",
        "username": "testuser",
        "name": "Test User",
        "bio": None,
        "active": True,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    try:
        result = gateway.session.execute(text(sql), params)
        gateway.session.commit()
        print(f"✅ Inserted user with ID: {result.lastrowid}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_save())
