"""
Test automatic table creation
"""

import sys
sys.path.insert(0, '.')

from pathlib import Path
from starspring import StarSpringApplication

print("=" * 70)
print("Testing Automatic Table Creation")
print("=" * 70)

# Create application
config_path = Path("examples/blog_app/application.yaml")
app = StarSpringApplication(
    title="Test Auto Tables",
    debug=True,
    config_path=str(config_path)
)

print("\n1. Scanning components...")
app.scan_components("examples.blog_app")

print("\n2. Checking if tables were created...")
from starspring.data.orm_gateway import get_orm_gateway
from sqlalchemy import text

gateway = get_orm_gateway()

# Check for tables
check_sql = """
SELECT name FROM sqlite_master 
WHERE type='table' 
ORDER BY name
"""

result = gateway.session.execute(text(check_sql))
tables = [row[0] for row in result.fetchall()]

print(f"\n✅ Tables found in database: {tables}")

if 'users' in tables and 'posts' in tables and 'comments' in tables and 'tags' in tables:
    print("\n" + "=" * 70)
    print("✅ SUCCESS! All tables created automatically!")
    print("=" * 70)
    print("\nTables created:")
    for table in tables:
        print(f"  ✅ {table}")
else:
    print("\n❌ ERROR: Not all tables were created")
    print(f"Expected: users, posts, comments, tags")
    print(f"Found: {tables}")
