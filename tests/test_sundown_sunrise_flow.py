#!/usr/bin/env python3
"""
Test the complete sundown/sunrise state machine flow
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment
from shared.env import TektonEnvironLock
TektonEnvironLock.load()

from shared.aish.src.registry.ci_registry import get_registry

def test_state_flow():
    """Test the state machine transitions."""
    registry = get_registry()
    ci_name = 'ergon-ci'
    
    print("\n" + "=" * 60)
    print("SUNDOWN/SUNRISE STATE MACHINE TEST")
    print("=" * 60)
    
    # Check current state
    print("\n1. CURRENT STATE CHECK")
    print("-" * 40)
    
    needs_fresh = registry.get_needs_fresh_start(ci_name)
    next_prompt = registry.get_next_prompt(ci_name)
    sunrise_context = registry.get_sunrise_context(ci_name)
    
    print(f"CI: {ci_name}")
    print(f"Needs fresh start: {needs_fresh}")
    print(f"Next prompt queued: {bool(next_prompt)}")
    print(f"Has sunrise context: {bool(sunrise_context)}")
    
    # Determine state
    if needs_fresh:
        state = "State 1: Fresh Start (Post-Sundown)"
        next_cmd = "claude --print (NO continue)"
    else:
        state = "State 2: Normal Conversation"
        next_cmd = "claude --print --continue"
    
    print(f"\nCurrent State: {state}")
    print(f"Next command will be: {next_cmd}")
    
    # Test state transitions
    print("\n2. STATE TRANSITIONS")
    print("-" * 40)
    
    print("\nState 1 → State 2 (Sunrise → Normal):")
    print("  • User sends message")
    print("  • System checks needs_fresh_start = True")
    print("  • Command: claude --print [context + message]")
    print("  • After response: set needs_fresh_start = False")
    
    print("\nState 2 → State 2 (Normal conversation):")
    print("  • User sends message")
    print("  • System checks needs_fresh_start = False")
    print("  • Command: claude --print --continue [message]")
    print("  • State remains in normal")
    
    print("\nState 2 → State 3 (Trigger Sundown at 85%):")
    print("  • Token usage hits 85%")
    print("  • System injects sundown prompt")
    print("  • Command: claude --print --continue [sundown prompt]")
    print("  • CI summarizes WITH context available")
    
    print("\nState 3 → State 1 (Post-Sundown):")
    print("  • After sundown response")
    print("  • System sets needs_fresh_start = True")
    print("  • Next message will start fresh")
    
    # Test scenarios
    print("\n3. TEST SCENARIOS")
    print("-" * 40)
    
    print("\nScenario A: Fresh start after sundown")
    registry.set_needs_fresh_start(ci_name, True)
    needs_fresh = registry.get_needs_fresh_start(ci_name)
    print(f"  Set needs_fresh_start = True")
    print(f"  Verified: {needs_fresh}")
    print(f"  Next message will NOT use --continue")
    
    print("\nScenario B: Normal conversation")
    registry.set_needs_fresh_start(ci_name, False)
    needs_fresh = registry.get_needs_fresh_start(ci_name)
    print(f"  Set needs_fresh_start = False")
    print(f"  Verified: {not needs_fresh}")
    print(f"  Next message WILL use --continue")
    
    print("\nScenario C: Sundown trigger (simulation)")
    print("  At 85% tokens:")
    print("  1. Keep needs_fresh_start = False (stay in context)")
    print("  2. Send: 'Please summarize your work...'")
    print("  3. Use: claude --print --continue")
    print("  4. After response: set needs_fresh_start = True")
    
    # Current issue with Ergon
    print("\n4. ERGON'S CURRENT ISSUE")
    print("-" * 40)
    print("Problem: 'Prompt is too long' error")
    print("Causes:")
    print("  1. Accumulated context over time")
    print("  2. No automatic sundown at 85%")
    print("  3. Buffered messages add to prompt size")
    print("\nSolution:")
    print("  1. Manually trigger sundown: aish sundown ergon-ci")
    print("  2. This uses --continue to get summary")
    print("  3. Sets needs_fresh_start = True")
    print("  4. Next message starts fresh without --continue")
    
    print("\n" + "=" * 60)
    print("END OF TEST")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    test_state_flow()