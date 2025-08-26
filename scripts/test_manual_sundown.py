#!/usr/bin/env python3
"""
Test what happens with manual sundown command
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment
from shared.env import TektonEnvironLock
TektonEnvironLock.load()

from shared.aish.src.registry.ci_registry import get_registry

def test_manual_sundown():
    """Test manual sundown behavior."""
    registry = get_registry()
    ci_name = 'ergon-ci'
    
    print("\nMANUAL SUNDOWN TEST")
    print("=" * 60)
    
    print("\nBEFORE SUNDOWN:")
    needs_fresh = registry.get_needs_fresh_start(ci_name)
    print(f"  needs_fresh_start: {needs_fresh}")
    print(f"  Expected command: claude --print {'(no continue)' if needs_fresh else '--continue'}")
    
    print("\nWHAT SHOULD HAPPEN:")
    print("  1. User runs: aish sundown ergon-ci")
    print("  2. System sends sundown prompt to CI")
    print("  3. Command used: claude --print --continue")
    print("  4. CI responds with summary (has full context)")
    print("  5. AFTER response: set needs_fresh_start = True")
    
    print("\nWHAT CURRENTLY HAPPENS (BUG):")
    print("  1. User runs: aish sundown ergon-ci")
    print("  2. System immediately sets needs_fresh_start = True")
    print("  3. Sundown prompt sent without --continue (WRONG)")
    print("  4. CI has no context to summarize")
    
    print("\nTHE FIX NEEDED:")
    print("  • Don't set needs_fresh_start until AFTER response")
    print("  • Always use --continue for sundown prompt")
    print("  • Only set fresh start flag after CI responds")
    
    # Demonstrate the issue
    print("\nDEMO OF ISSUE:")
    print("-" * 40)
    
    # Reset to normal state
    registry.set_needs_fresh_start(ci_name, False)
    print("Reset to normal conversation state")
    
    # Simulate what sundown command does
    print("\nSimulating 'aish sundown ergon-ci':")
    print("  1. Setting needs_fresh_start = True (TOO EARLY!)")
    registry.set_needs_fresh_start(ci_name, True)
    
    needs_fresh = registry.get_needs_fresh_start(ci_name)
    print(f"  2. needs_fresh_start is now: {needs_fresh}")
    print(f"  3. Sundown prompt will use: claude --print (NO continue)")
    print("  4. CI won't have context to summarize!")
    
    # Reset for fix
    print("\nCORRECT APPROACH:")
    registry.set_needs_fresh_start(ci_name, False)
    print("  1. Keep needs_fresh_start = False")
    print("  2. Send: 'Please summarize...' with --continue")
    print("  3. CI responds with full context available")
    print("  4. THEN set needs_fresh_start = True")
    print("  5. Next message starts fresh")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_manual_sundown()