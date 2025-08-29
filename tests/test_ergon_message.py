#!/usr/bin/env python3
"""
Test what happens when Ergon receives a message
Simulates the claude_handler flow without actually calling Claude
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment
from shared.env import TektonEnvironLock
TektonEnvironLock.load()

from shared.aish.src.registry.ci_registry import get_registry
from Rhetor.rhetor.core.token_manager import get_token_manager

def simulate_message(message: str):
    """Simulate sending a message to Ergon."""
    registry = get_registry()
    token_mgr = get_token_manager()
    
    ci_name = 'ergon-ci'
    
    print(f"\nSimulating message to {ci_name}:")
    print(f"Message: '{message[:50]}...'" if len(message) > 50 else f"Message: '{message}'")
    print("-" * 60)
    
    # 1. Check fresh start flag
    needs_fresh = registry.get_needs_fresh_start(ci_name)
    print(f"1. Fresh start check: {'YES - will skip --continue' if needs_fresh else 'NO - will use --continue'}")
    
    # 2. Check if tracking
    if ci_name not in token_mgr.usage_tracker:
        print(f"2. Token tracking: NOT INITIALIZED")
        print("   → Run: python scripts/initialize_ergon.py")
        return
    
    # 3. Simulate token estimation
    
    # Add message to tracking
    token_mgr.update_usage(ci_name, 'conversation_history', message)
    
    # Get current status
    status = token_mgr.get_status(ci_name)
    usage_pct = status['usage_percentage']
    
    print(f"2. Token usage: {usage_pct:.1f}%")
    
    # 4. Check thresholds
    if usage_pct >= 95:
        print("   🛑 BLOCKED: Exceeds 95% limit")
        print("   → Message would NOT be sent to Claude")
        print("   → User sees error: 'PROMPT TOO LARGE'")
        print("   → Action required: aish sundown ergon-ci")
    elif usage_pct >= 85:
        print("   ⚠️  AUTO-TRIGGER threshold reached (85%)")
        print("   → Should trigger sundown (not yet implemented)")
        print("   → Currently: Message would still be sent")
    elif usage_pct >= 75:
        print("   ⚠️  SUGGEST threshold reached (75%)")
        print("   → Sundown suggested but not required")
    elif usage_pct >= 60:
        print("   ⚠️  WARNING threshold reached (60%)")
        print("   → Monitor closely")
    else:
        print("   ✓ Healthy usage")
    
    # 5. Show what would happen
    print(f"\n3. What would happen:")
    if usage_pct >= 95:
        print("   • Message BLOCKED")
        print("   • Fresh start flag SET")
        print("   • Error returned to user")
    else:
        if needs_fresh:
            print("   • Claude called WITHOUT --continue")
            print("   • Fresh conversation started")
        else:
            print("   • Claude called WITH --continue")
            print("   • Conversation continues")
    
    print("-" * 60)
    print(f"Current token usage: {usage_pct:.1f}%")
    print(f"Tokens used: ~{sum(status.get('usage', {}).values())}")
    print(f"Model limit: {token_mgr.get_model_limit(status['model']):,}")

if __name__ == "__main__":
    # Test with different message sizes
    test_messages = [
        "Hello Ergon, how are you?",
        "Please help me implement a complex authentication system " * 10,
        "A" * 10000  # Large message
    ]
    
    print("\n" + "=" * 60)
    print("ERGON MESSAGE SIMULATION")
    print("=" * 60)
    
    for i, msg in enumerate(test_messages, 1):
        print(f"\n--- Test {i} ---")
        simulate_message(msg)
        
    print("\n" + "=" * 60)
    print("Simulation complete. Ergon is NOT actually called.")
    print("=" * 60)