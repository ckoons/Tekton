#!/usr/bin/env python3
"""
Check AI port alignment with expected values.
Uses configurable port bases from environment.
"""
import sys
import os
import socket

# Add Tekton root to path
script_path = os.path.realpath(__file__)
tekton_root = os.path.dirname(os.path.dirname(script_path))
sys.path.insert(0, tekton_root)

from shared.utils.env_config import get_component_config
from shared.utils.ai_port_utils import get_ai_port

def get_expected_ai_port(main_port: int) -> int:
    """Calculate expected AI port based on component's main port."""
    return get_ai_port(main_port)

def check_port_open(host: str, port: int) -> bool:
    """Check if a port is open."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((host, port)) == 0
    sock.close()
    return result

def main():
    
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
    
    # Check ports
    print("AI Port Alignment Check (Fixed Port System)")
    print("=" * 70)
    print(f"{'Component':<15} {'Main Port':<12} {'AI Port':<12} {'AI Running':<12}")
    print("-" * 70)
    
    running_count = 0
    total_count = 0
    
    for ai_id, data in sorted(expected.items()):
        component = data['component']
        main_port = data['main_port']
        ai_port = data['expected_port']
        is_running = check_port_open('localhost', ai_port)
        
        if is_running:
            running_count += 1
            status = "✓ Running"
        else:
            status = "✗ Not running"
            
        total_count += 1
        print(f"{component:<15} {main_port:<12} {ai_port:<12} {status:<12}")
    
    print("=" * 70)
    print(f"Total AI components: {total_count}")
    print(f"Running: {running_count}")
    print(f"Not running: {total_count - running_count}")
    print(f"\nPort formula: AI port = {os.environ.get('TEKTON_AI_PORT_BASE', '45000')} + (main_port - {os.environ.get('TEKTON_PORT_BASE', '8000')})")

if __name__ == '__main__':
    main()