#!/usr/bin/env python3
"""
Apply the singleton fix to Hermes endpoints.py

This script shows the minimal changes needed to fix the registration persistence issue.
"""

print("""
To fix Hermes registration persistence, make these changes to endpoints.py:

1. Add this import at the top:
   from hermes.api.singleton_fix import get_shared_registration_manager

2. Replace the get_registration_manager function (around line 44) with:

def get_registration_manager():
    \"\"\"Get the shared registration manager instance.\"\"\"
    return get_shared_registration_manager()

That's it! The registrations will now persist across requests.

The fix works by:
- Creating a module-level singleton that survives between requests
- Sharing the same ServiceRegistry instance for all operations
- Keeping registered components in memory

To apply this fix:
1. Copy singleton_fix.py to the Hermes api directory
2. Edit endpoints.py to use get_shared_registration_manager()
3. Restart Hermes

The components will then stay registered until Hermes restarts.
""")