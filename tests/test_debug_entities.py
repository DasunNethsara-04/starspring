"""
Debug entity registration
"""

import sys
sys.path.insert(0, '.')

from pathlib import Path
from starspring import StarSpringApplication

print("=" * 70)
print("Debugging Entity Registration")
print("=" * 70)

# Create application
config_path = Path("examples/blog_app/application.yaml")
app = StarSpringApplication(
    title="Debug",
    debug=True,
    config_path=str(config_path)
)

print("\n1. Scanning components...")
app.scan_components("examples.blog_app")

print("\n2. Checking registered beans...")
from starspring.core.context import get_application_context
ctx = get_application_context()

print(f"\nTotal beans: {len(ctx._beans)}")
for bean_name, bean_def in ctx._beans.items():
    bean_class = bean_def.bean_class
    has_entity = hasattr(bean_class, '_entity_metadata')
    print(f"  - {bean_name}: {bean_class.__name__} (entity: {has_entity})")

print("\n3. Looking for entity classes in modules...")
import importlib
from examples.blog_app import entities

entity_classes = []
for name in dir(entities):
    obj = getattr(entities, name)
    if hasattr(obj, '_entity_metadata'):
        entity_classes.append(obj)
        print(f"  ✅ Found entity: {obj.__name__}")

print(f"\nTotal entities found: {len(entity_classes)}")
