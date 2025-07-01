#!/usr/bin/env python3
"""
Check AI port alignment with expected values.
"""
import json
from pathlib import Path
import sys
import os

# Add Tekton root to path
script_path = os.path.realpath(__file__)
tekton_root = os.path.dirname(os.path.dirname(script_path))
sys.path.insert(0, tekton_root)

from shared.utils.env_config import get_component_config

def get_expected_ai_port(main_port: int) -> int:
    """Calculate expected AI port based on component's main port."""
    return 45000 + (main_port - 8000)

def main():
    # Load current registry
    registry_file = Path.home() / '.tekton' / 'ai_registry' / 'platform_ai_registry.json'
    with open(registry_file) as f:
        registry = json.load(f)
    
    # Get component config
    config = get_component_config()
    
    # Build expected mapping
    expected = {}
    for attr_name in dir(config):
        if attr_name.startswith('_'):
            continue
        
        try:
            comp_config = getattr(config, attr_name)
            if hasattr(comp_config, 'port'):
                main_port = comp_config.port
                ai_id = f"{attr_name}-ai"
                expected[ai_id] = {
                    'component': attr_name,
                    'main_port': main_port,
                    'expected_port': get_expected_ai_port(main_port)
                }
        except:
            continue
    
    # Compare
    print("AI Port Alignment Check")
    print("=" * 70)
    print(f"{'AI ID':<20} {'Component':<15} {'Current':<10} {'Expected':<10} {'Status':<10}")
    print("-" * 70)
    
    misaligned = []
    for ai_id, data in sorted(registry.items()):
        current_port = data['port']
        if ai_id in expected:
            exp_port = expected[ai_id]['expected_port']
            status = "✓ OK" if current_port == exp_port else "✗ MISMATCH"
            if current_port != exp_port:
                misaligned.append(ai_id)
            print(f"{ai_id:<20} {data['component']:<15} {current_port:<10} {exp_port:<10} {status:<10}")
        else:
            print(f"{ai_id:<20} {data['component']:<15} {current_port:<10} {'N/A':<10} {'?':<10}")
    
    print("=" * 70)
    print(f"Total AIs: {len(registry)}")
    print(f"Misaligned: {len(misaligned)}")
    
    if misaligned:
        print("\nMisaligned AIs:")
        for ai_id in misaligned:
            print(f"  - {ai_id}")

if __name__ == '__main__':
    main()