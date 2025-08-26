#!/usr/bin/env python3
"""
Properly initialize Ergon with token tracking
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load Tekton environment first
from shared.env import TektonEnvironLock
TektonEnvironLock.load()

from shared.aish.src.registry.ci_registry import get_registry
from Rhetor.rhetor.core.token_manager import get_token_manager

def initialize_ergon():
    """Initialize Ergon with proper token tracking."""
    registry = get_registry()
    token_mgr = get_token_manager()
    
    print("\nInitializing Ergon with token management...")
    
    # Check forward state
    forward_state = registry.get_forward_state('ergon-ci')
    if not forward_state:
        print("❌ Ergon is not forwarded. Please run:")
        print("   aish forward ergon <terminal>")
        return False
    
    model = forward_state.get('model', 'claude-opus-4-1-20250805')
    print(f"✓ Found forward state with model: {model}")
    
    # Initialize token tracking
    token_mgr.init_ci_tracking('ergon-ci', model)
    print(f"✓ Token tracking initialized")
    
    # Set fresh start
    registry.set_needs_fresh_start('ergon-ci', True)
    print(f"✓ Fresh start flag set (will skip --continue)")
    
    # Show limits
    limit = token_mgr.get_model_limit(model)
    print(f"\nToken Configuration:")
    print(f"  Model: {model}")
    print(f"  Token Limit: {limit:,}")
    print(f"  Warning at: {int(limit * 0.60):,} (60%)")
    print(f"  Suggest at: {int(limit * 0.75):,} (75%)")
    print(f"  Auto at: {int(limit * 0.85):,} (85%)")
    print(f"  Critical at: {int(limit * 0.95):,} (95%)")
    
    print("\n✅ Ergon is ready!")
    print("\nNext steps:")
    print("1. Send a test message to Ergon")
    print("2. Monitor with: python scripts/check_ergon_status.py")
    print("3. If needed: aish sundown ergon-ci")
    
    return True

if __name__ == "__main__":
    initialize_ergon()