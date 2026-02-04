"""
Test if the ORM gateway fix works
"""

import sys
sys.path.insert(0, '.')

print("=" * 70)
print("Testing ORM Gateway with Raw SQL")
print("=" * 70)

try:
    # Create application
    print("\n1. Creating application with database...")
    from pathlib import Path
    from starspring import StarSpringApplication
    
    config_path = Path("examples/blog_app/application.yaml")
    app = StarSpringApplication(
        title="Test",
        debug=True,
        config_path=str(config_path)
    )
    
    # Create a simple test table
    print("\n2. Creating test table...")
    from starspring.data.orm_gateway import get_orm_gateway
    from sqlalchemy import text
    
    gateway = get_orm_gateway()
    
    # Create posts table if it doesn't exist
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        slug TEXT NOT NULL UNIQUE,
        content TEXT NOT NULL,
        excerpt TEXT,
        published BOOLEAN DEFAULT 0,
        published_at DATETIME,
        author_id INTEGER NOT NULL,
        created_at DATETIME NOT NULL,
        updated_at DATETIME NOT NULL
    )
    """
    
    gateway.session.execute(text(create_table_sql))
    gateway.session.commit()
    print("   ✅ Table created")
    
    # Test find_all
    print("\n3. Testing find_all with empty table...")
    from examples.blog_app.entities import Post
    
    posts = await gateway.find_all(Post)
    print(f"   ✅ Found {len(posts)} posts (expected 0)")
    
    print("\n" + "=" * 70)
    print("✅ SUCCESS! ORM gateway works with raw SQL!")
    print("=" * 70)
    
except Exception as e:
    print("\n" + "=" * 70)
    print(f"❌ ERROR: {e}")
    print("=" * 70)
    import traceback
    traceback.print_exc()

# Run async test
import asyncio

async def test():
    from pathlib import Path
    from starspring import StarSpringApplication
    from starspring.data.orm_gateway import get_orm_gateway
    from sqlalchemy import text
    from examples.blog_app.entities import Post
    
    config_path = Path("examples/blog_app/application.yaml")
    app = StarSpringApplication(title="Test", debug=True, config_path=str(config_path))
    
    gateway = get_orm_gateway()
    
    # Create table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        slug TEXT NOT NULL UNIQUE,
        content TEXT NOT NULL,
        excerpt TEXT,
        published BOOLEAN DEFAULT 0,
        published_at DATETIME,
        author_id INTEGER NOT NULL,
        created_at DATETIME NOT NULL,
        updated_at DATETIME NOT NULL
    )
    """
    
    gateway.session.execute(text(create_table_sql))
    gateway.session.commit()
    
    # Test find_all
    posts = await gateway.find_all(Post)
    print(f"\n✅ ORM Gateway Test: Found {len(posts)} posts")
    return True

if __name__ == "__main__":
    asyncio.run(test())
