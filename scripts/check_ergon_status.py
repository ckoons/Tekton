#!/usr/bin/env python3
"""
Check Ergon's current token usage and status
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load Tekton environment first
from shared.env import TektonEnvironLock
TektonEnvironLock.load()

from shared.aish.src.registry.ci_registry import get_registry
from Rhetor.rhetor.core.token_manager import get_token_manager
from Rhetor.rhetor.core.token_logger import get_token_logger

def check_ergon():
    """Check Ergon's complete status."""
    registry = get_registry()
    token_mgr = get_token_manager()
    logger = get_token_logger()
    
    print("\n" + "=" * 60)
    print("ERGON STATUS CHECK")
    print("=" * 60 + "\n")
    
    # 1. Forward state
    print("1. Forward State:")
    forward_state = registry.get_forward_state('ergon-ci')
    if forward_state:
        print(f"   Model: {forward_state.get('model', 'unknown')}")
        print(f"   Active: Yes")
    else:
        print("   Not forwarded")
    
    # 2. Fresh start flag
    print("\n2. Context Management:")
    needs_fresh = registry.get_needs_fresh_start('ergon-ci')
    print(f"   Needs fresh start: {needs_fresh}")
    print(f"   Will {'skip' if needs_fresh else 'include'} --continue flag")
    
    # 3. Token usage
    print("\n3. Token Usage:")
    if 'ergon-ci' in token_mgr.usage_tracker:
        status = token_mgr.get_status('ergon-ci')
        print(f"   Model: {status['model']}")
        print(f"   Usage: {status['usage_percentage']:.1f}%")
        print(f"   Level: {status['sundown_level']}")
        print(f"   Messages: {status['message_count']}")
        
        should_sundown, reason = token_mgr.should_sundown('ergon-ci')
        if should_sundown:
            print(f"   ⚠️  SUNDOWN NEEDED: {reason}")
    else:
        print("   Not tracking tokens")
    
    # 4. Recent history
    print("\n4. Recent Activity:")
    history = logger.analyze_usage_patterns('ergon-ci')
    if history['status'] != 'no_data':
        print(f"   Samples: {history['samples']}")
        print(f"   Avg usage: {history['avg_usage']:.1f}%")
        print(f"   Max usage: {history['max_usage']:.1f}%")
        print(f"   Trend: {history['trend']}")
    else:
        print("   No usage data logged yet")
    
    # 5. Recommendations
    print("\n5. Recommendations:")
    if needs_fresh:
        print("   ✓ Already set for fresh start")
        print("   → Send a simple test message")
    elif forward_state and 'ergon-ci' in token_mgr.usage_tracker:
        usage = token_mgr.get_usage_percentage('ergon-ci')
        if usage > 0.85:
            print("   🛑 Critical usage - run: aish sundown ergon-ci")
        elif usage > 0.60:
            print("   ⚠️  High usage - consider sundown")
        else:
            print("   ✓ Usage is healthy")
    else:
        print("   → Set up forward: aish forward ergon <terminal>")
    
    print("\n" + "=" * 60 + "\n")

if __name__ == "__main__":
    check_ergon()