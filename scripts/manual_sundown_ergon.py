#!/usr/bin/env python3
"""
Correctly trigger sundown for Ergon
This sends the sundown prompt WITH context, then sets fresh start
"""

import sys
import subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment
from shared.env import TektonEnvironLock
TektonEnvironLock.load()

from shared.aish.src.registry.ci_registry import get_registry

def manual_sundown_ergon():
    """Correctly trigger sundown for Ergon."""
    registry = get_registry()
    ci_name = 'ergon-ci'
    
    print("\nMANUAL SUNDOWN FOR ERGON")
    print("=" * 60)
    
    # Step 1: Ensure we're NOT in fresh start mode
    print("\n1. Preparing for sundown...")
    registry.set_needs_fresh_start(ci_name, False)
    print("   ✓ Ensured context will be preserved")
    
    # Step 2: Send sundown message (this will use --continue)
    print("\n2. Sending sundown prompt to Ergon...")
    sundown_prompt = (
        "It's time to wrap up for today. Please summarize:\n"
        "1. What you've been working on\n"
        "2. Key decisions or insights\n"
        "3. What should be continued tomorrow\n"
        "Keep it concise but complete."
    )
    
    # Send via aish (will use --continue because needs_fresh is False)
    cmd = ['./shared/aish/aish', 'ergon-ci', sundown_prompt]
    print("   Command: aish ergon-ci '[sundown prompt]'")
    print("   This will use: claude --print --continue")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("   ✓ Sundown message sent")
        if "Buffered" in result.stdout:
            print("   Note: Message was buffered, waiting for human input")
    else:
        print(f"   ⚠️  Error: {result.stderr}")
    
    # Step 3: NOW set fresh start for next interaction
    print("\n3. Setting fresh start for next session...")
    registry.set_needs_fresh_start(ci_name, True)
    print("   ✓ Next message will start fresh without --continue")
    
    print("\n" + "=" * 60)
    print("SUNDOWN COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Ergon will respond with summary (has full context)")
    print("2. Next message to Ergon will start fresh")
    print("3. No more 'Prompt too long' errors")

if __name__ == "__main__":
    manual_sundown_ergon()