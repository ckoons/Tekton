#!/usr/bin/env python3
"""
Verify port configuration against official port assignments.
"""
import sys
import os

# Add Tekton root to path
script_path = os.path.realpath(__file__)
tekton_root = os.path.dirname(os.path.dirname(script_path))
sys.path.insert(0, tekton_root)

from shared.utils.env_config import get_component_config

# Official port assignments from config/port_assignments.md
OFFICIAL_PORTS = {
    'hephaestus': 8080,
    'engram': 8000,
    'hermes': 8001,
    'ergon': 8002,
    'rhetor': 8003,
    'terma': 8004,
    'athena': 8005,
    'prometheus': 8006,
    'harmonia': 8007,
    'telos': 8008,
    'synthesis': 8009,
    'tekton_core': 8010,
    'metis': 8011,
    'apollo': 8012,
    'penia': 8013,
    'budget': 8013,  # Note: same as penia!
    'sophia': 8014,
    'noesis': 8015,
    'numa': 8016,
}

def get_expected_ai_port(main_port: int) -> int:
    """Calculate expected AI port based on component's main port."""
    return 45000 + (main_port - 8000)

def main():
    config = get_component_config()
    
    print("Port Configuration Verification")
    print("=" * 80)
    print(f"{'Component':<15} {'Config Port':<12} {'Official':<12} {'Status':<10} {'AI Port':<10}")
    print("-" * 80)
    
    issues = []
    
    # Check each component
    for component, official_port in sorted(OFFICIAL_PORTS.items()):
        comp_config = getattr(config, component, None)
        if comp_config and hasattr(comp_config, 'port'):
            config_port = comp_config.port
            status = "✓ OK" if config_port == official_port else "✗ MISMATCH"
            ai_port = get_expected_ai_port(official_port)
            
            if config_port != official_port:
                issues.append(f"{component}: config={config_port}, official={official_port}")
            
            print(f"{component:<15} {config_port:<12} {official_port:<12} {status:<10} {ai_port:<10}")
        else:
            print(f"{component:<15} {'N/A':<12} {official_port:<12} {'MISSING':<10} {get_expected_ai_port(official_port):<10}")
    
    print("=" * 80)
    
    if issues:
        print(f"\nFound {len(issues)} configuration issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\nAll port configurations match official assignments!")
    
    # Note about budget/penia
    print("\n📝 Note: Budget and Penia are the same component (Greek name variant)")

if __name__ == '__main__':
    main()