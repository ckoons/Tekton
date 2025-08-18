#!/usr/bin/env python3
"""
Quick verification script for sunset/sunrise functionality.
Shows current state and allows manual testing.
"""

import sys
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # Get to Tekton root
from shared.aish.src.registry.ci_registry import get_registry

def main():
    registry = get_registry()
    
    print("Sunset/Sunrise Registry Status")
    print("=" * 60)
    
    # Show all CIs with sunset/sunrise state
    all_states = registry.get_all_context_states()
    
    has_state = False
    for ci_name, state in all_states.items():
        next_prompt = state.get('next_prompt')
        sunrise_context = state.get('sunrise_context')
        
        if next_prompt or sunrise_context:
            has_state = True
            print(f"\n{ci_name}:")
            if next_prompt:
                print(f"  next_prompt: {next_prompt[:100]}...")
            if sunrise_context:
                print(f"  sunrise_context: {sunrise_context[:100]}...")
    
    if not has_state:
        print("\nNo CIs currently have sunset/sunrise state set.")
    
    print("\n" + "=" * 60)
    print("Available commands:")
    print("  registry.set_next_prompt(ci_name, prompt)")
    print("  registry.get_next_prompt(ci_name)")
    print("  registry.set_sunrise_context(ci_name, context)")
    print("  registry.get_sunrise_context(ci_name)")
    print("  registry.clear_next_prompt(ci_name)")
    print("  registry.clear_sunrise_context(ci_name)")
    print("\nThe registry is ready for Apollo/Rhetor sunset/sunrise orchestration!")
    
    # Clean up any test data
    for ci_name in ['athena', 'numa', 'apollo', 'rhetor', 'synthesis']:
        registry.clear_next_prompt(ci_name)
        registry.clear_sunrise_context(ci_name)
    
    print("\n✅ Test data cleaned up. Registry ready for production use.")
    return 0  # Success

if __name__ == "__main__":
    sys.exit(main())