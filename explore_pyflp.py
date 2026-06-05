import pyflp
import inspect

print("=== pyflp location ===")
print(pyflp.__file__)

# Explore Project creation
print("\n=== Project creation ===")
from pyflp import Project
sig = inspect.signature(Project.__init__)
print(f"Project.__init__ signature: {sig}")

print("\n=== Project attributes ===")
print([m for m in dir(Project) if not m.startswith('_')])

# Channel
from pyflp._channel import Channel
print("\n=== Channel attributes ===")
print([m for m in dir(Channel) if not m.startswith('_')])

# Check if there's a write/create method
from pyflp._project import Project as ProjectWrite
print("\n=== Project write/dump ===")
import pyflp
print(dir(pyflp))

# Look for any write/dump/save function
for attr in dir(pyflp):
    if 'dump' in attr.lower() or 'save' in attr.lower() or 'write' in attr.lower() or 'create' in attr.lower():
        print(f"  Found: {attr}")
