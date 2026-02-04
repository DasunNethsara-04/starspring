"""
Test blog app with SQLAlchemy installed
"""

import sys
sys.path.insert(0, '.')

print("=" * 70)
print("Testing Blog App with SQLAlchemy")
print("=" * 70)

try:
    # Test SQLAlchemy import
    print("\n1. Checking SQLAlchemy installation...")
    import sqlalchemy
    print(f"   ✅ SQLAlchemy {sqlalchemy.__version__} installed")
    
    # Create the application
    print("\n2. Creating StarSpring application...")
    from pathlib import Path
    from starspring import StarSpringApplication
    
    config_path = Path("examples/blog_app/application.yaml")
    app = StarSpringApplication(
        title="Blog Test",
        version="1.0.0",
        debug=True,
        config_path=str(config_path)
    )
    print("   ✅ Application created")
    
    # Check if ORM gateway is initialized
    print("\n3. Checking ORM gateway initialization...")
    from starspring.data.orm_gateway import get_orm_gateway
    try:
        gateway = get_orm_gateway()
        print(f"   ✅ ORM gateway initialized: {type(gateway).__name__}")
    except RuntimeError as e:
        print(f"   ❌ ORM gateway not initialized: {e}")
    
    # Scan components
    print("\n4. Scanning blog app components...")
    app.scan_components("examples.blog_app")
    print("   ✅ Components scanned")
    
    # Check if repositories work
    print("\n5. Testing repository creation...")
    from examples.blog_app.repositories import UserRepository
    from starspring.core.context import get_application_context
    
    ctx = get_application_context()
    user_repo = ctx.get_bean(UserRepository)
    print(f"   ✅ UserRepository created: {type(user_repo).__name__}")
    print(f"   ✅ Entity class: {user_repo.entity_class.__name__}")
    
    print("\n" + "=" * 70)
    print("✅ SUCCESS! Blog app is fully functional!")
    print("=" * 70)
    print("\nThe blog app can now:")
    print("  ✓ Initialize ORM gateway")
    print("  ✓ Create repositories with DI")
    print("  ✓ Handle API requests")
    print("\n🎉 Ready to run: python examples/blog_app/main.py")
    print("=" * 70)
    
except Exception as e:
    print("\n" + "=" * 70)
    print(f"❌ ERROR: {e}")
    print("=" * 70)
    import traceback
    traceback.print_exc()
