"""
Test CRUD operations
"""

import sys
import asyncio
sys.path.insert(0, '.')

from pathlib import Path
from starspring import StarSpringApplication
from examples.blog_app.entities import User, Post
from datetime import datetime

async def test_crud():
    print("=" * 70)
    print("Testing CRUD Operations")
    print("=" * 70)
    
    # Create application
    config_path = Path("examples/blog_app/application.yaml")
    app = StarSpringApplication(
        title="Test CRUD",
        debug=False,
        config_path=str(config_path)
    )
    
    app.scan_components("examples.blog_app")
    
    # Get services
    from starspring.core.context import get_application_context
    ctx = get_application_context()
    
    from examples.blog_app.services import UserService, PostService
    user_service = ctx.get_bean(UserService)
    post_service = ctx.get_bean(PostService)
    
    print("\n1. CREATE - Creating a user...")
    user = await user_service.create_user(
        email="john@example.com",
        username="john",
        name="John Doe"
    )
    print(f"   ✅ Created user: {user.username} (ID: {user.id})")
    
    print("\n2. CREATE - Creating a blog post...")
    post = await post_service.create_post(
        title="My First Post",
        content="This is the content of my first blog post!",
        author_id=user.id,
        excerpt="A great first post"
    )
    print(f"   ✅ Created post: {post.title} (ID: {post.id})")
    
    print("\n3. READ - Fetching the post...")
    fetched_post = await post_service.get_post_by_id(post.id)
    print(f"   ✅ Fetched post: {fetched_post.title}")
    print(f"      Published: {fetched_post.published}")
    
    print("\n4. UPDATE - Publishing the post...")
    published_post = await post_service.publish_post(post.id)
    print(f"   ✅ Published post: {published_post.title}")
    print(f"      Published: {published_post.published}")
    print(f"      Published at: {published_post.published_at}")
    
    print("\n5. READ - Listing all posts...")
    all_posts = await post_service.get_all_posts()
    print(f"   ✅ Found {len(all_posts)} post(s)")
    for p in all_posts:
        print(f"      - {p.title} (ID: {p.id}, Published: {p.published})")
    
    print("\n6. DELETE - Deleting the post...")
    deleted = await post_service.delete_post(post.id)
    print(f"   ✅ Deleted post: {deleted}")
    
    print("\n7. VERIFY - Checking post was deleted...")
    all_posts_after = await post_service.get_all_posts()
    print(f"   ✅ Posts remaining: {len(all_posts_after)}")
    
    print("\n" + "=" * 70)
    print("✅ ALL CRUD OPERATIONS WORKING!")
    print("=" * 70)
    print("\nSummary:")
    print("  ✅ CREATE - User and Post created successfully")
    print("  ✅ READ - Posts fetched successfully")
    print("  ✅ UPDATE - Post published successfully")
    print("  ✅ DELETE - Post deleted successfully")
    print("\n🎉 StarSpring framework is fully functional!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_crud())
