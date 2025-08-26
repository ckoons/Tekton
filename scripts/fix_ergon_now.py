#!/usr/bin/env python3
"""
IMMEDIATE FIX for Ergon's "Prompt too long" error
Forces fresh start without --continue
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment
from shared.env import TektonEnvironLock
TektonEnvironLock.load()

from shared.aish.src.registry.ci_registry import get_registry

def fix_ergon_now():
    """Force Ergon to fresh start immediately."""
    registry = get_registry()
    ci_name = 'ergon-ci'
    
    print("\nFORCING ERGON TO FRESH START")
    print("=" * 60)
    
    # Force fresh start
    registry.set_needs_fresh_start(ci_name, True)
    registry.set_needs_fresh_start('ergon', True)  # Also set for 'ergon' without -ci
    
    # Clear any queued prompts
    registry.clear_next_prompt(ci_name)
    registry.clear_next_prompt('ergon')
    
    # Clear sunrise context if any
    registry.clear_sunrise_context(ci_name)
    registry.clear_sunrise_context('ergon')
    
    print("✓ Set needs_fresh_start = True for both 'ergon' and 'ergon-ci'")
    print("✓ Cleared any queued prompts")
    print("✓ Cleared sunrise context")
    
    # Verify
    needs_fresh_ci = registry.get_needs_fresh_start(ci_name)
    needs_fresh = registry.get_needs_fresh_start('ergon')
    
    print(f"\nVerification:")
    print(f"  ergon-ci needs fresh: {needs_fresh_ci}")
    print(f"  ergon needs fresh: {needs_fresh}")
    
    print("\nNEXT MESSAGE TO ERGON:")
    print("  • Will NOT use --continue")
    print("  • Will start with clean context")
    print("  • Should NOT get 'Prompt too long' error")
    
    print("\n" + "=" * 60)
    print("ERGON IS NOW FIXED")
    print("=" * 60)
    print("\nTry sending a message to Ergon now.")
    print("It should work without the prompt size error.")

if __name__ == "__main__":
    fix_ergon_now()