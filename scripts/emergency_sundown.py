#!/usr/bin/env python3
"""
Emergency sundown script for Ergon
Run this to force Ergon into sundown state and clear context
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load Tekton environment first
from shared.env import TektonEnvironLock
TektonEnvironLock.load()

from shared.aish.src.registry.ci_registry import get_registry
from Rhetor.rhetor.core.token_manager import get_token_manager

def emergency_reset():
    """Force Ergon to reset context."""
    registry = get_registry()
    token_mgr = get_token_manager()
    
    # Set Ergon to need fresh start (skip --continue)
    registry.set_needs_fresh_start('ergon-ci', True)
    
    # Reset token tracking
    if 'ergon-ci' in token_mgr.usage_tracker:
        token_mgr.reset_ci('ergon-ci')
    
    # Clear any next_prompt that might be stuck
    registry.clear_next_prompt('ergon-ci')
    
    print("✓ Ergon reset to fresh state")
    print("  - Will skip --continue on next message")
    print("  - Token tracking reset")
    print("  - Ready for fresh start")
    
    # Show current forward state
    forward_state = registry.get_forward_state('ergon-ci')
    if forward_state:
        print(f"\nCurrent forward state: {forward_state.get('model', 'unknown')}")
    
    return True

if __name__ == "__main__":
    emergency_reset()
    print("\nNext steps:")
    print("1. Send a simple message to Ergon to test")
    print("2. If still failing, try: aish forward remove ergon")
    print("3. Then: aish forward ergon <terminal> --no-continue")