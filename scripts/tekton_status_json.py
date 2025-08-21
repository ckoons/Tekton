#!/usr/bin/env python3
"""
Simple Tekton status command with JSON output for Quality of Life improvements.
"""
import json
import sys
import os
import socket
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.env import TektonEnviron, TektonEnvironLock

# Check if specific coder environment requested
coder_env = TektonEnviron.get('CODER_ENV')
if coder_env:
    # For different coder environments, we need to handle this at the launcher level
    # The original tekton launcher sets up the environment properly
    # For now, we just use whatever environment is already loaded
    pass

# Only load if not already loaded (by parent process)
if not TektonEnviron.is_loaded():
    # Try to load - this requires TEKTON_ROOT to be set
    if 'TEKTON_ROOT' in os.environ:
        TektonEnvironLock.load()
    else:
        # Fallback - use current environment as-is
        print("Warning: TektonEnviron not loaded and TEKTON_ROOT not set", file=sys.stderr)

def check_port(port):
    """Check if a port is in use."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    except:
        return False

def get_forwarding_status():
    """Get current forwarding configuration."""
    tekton_root = TektonEnviron.get('TEKTON_ROOT')
    if not tekton_root:
        return {}
    forwarding_file = Path(tekton_root) / '.tekton' / 'aish' / 'forwarding.json'
    if forwarding_file.exists():
        try:
            with open(forwarding_file, 'r') as f:
                data = json.load(f)
                return data.get('forwards', {})
        except:
            return {}
    return {}

def get_active_terminals():
    """Get list of active terminals from Terma."""
    try:
        import requests
        terma_port = int(TektonEnviron.get('TERMA_PORT', '8300'))
        response = requests.get(f"http://localhost:{terma_port}/api/terminals", timeout=2)
        if response.status_code == 200:
            terminals = response.json()
            return [t['name'] for t in terminals if t.get('active', False)]
    except:
        pass
    return []

def main():
    """Generate status JSON."""
    
    # Get all components
    components = {}
    
    # Define known components and their ports from TektonEnviron
    known_components = {
        'terma': {
            'port': TektonEnviron.get('TERMA_PORT', '8300'),
            'ai_port': None
        },
        'hephaestus': {
            'port': TektonEnviron.get('HEPHAESTUS_PORT', '8080'),
            'ai_port': None
        },
        'rhetor': {
            'port': TektonEnviron.get('RHETOR_PORT', '8003'), 
            'ai_port': None
        },
        'numa': {
            'port': TektonEnviron.get('NUMA_PORT', '8316'),
            'ai_port': TektonEnviron.get('NUMA_AI_PORT', '42016')
        },
        'apollo': {
            'port': TektonEnviron.get('APOLLO_PORT', '8312'),
            'ai_port': TektonEnviron.get('APOLLO_AI_PORT', '42012')
        },
        'athena': {
            'port': TektonEnviron.get('ATHENA_PORT', '8313'),
            'ai_port': TektonEnviron.get('ATHENA_AI_PORT', '42013')
        }
    }
    
    for name, info in known_components.items():
        port = int(info['port'])
        ai_port = int(info['ai_port']) if info['ai_port'] else None
        
        # Check if component is running
        is_running = check_port(port)
        
        components[name] = {
            "status": "running" if is_running else "stopped",
            "port": port
        }
        
        if ai_port:
            components[name]["ai_port"] = ai_port
    
    # Get forwarding info
    forwarding = get_forwarding_status()
    
    # Get active terminals
    active_sessions = get_active_terminals()
    
    # Build status object
    status = {
        "timestamp": datetime.now().isoformat(),
        "components": components,
        "forwarding": forwarding,
        "active_sessions": active_sessions
    }
    
    # Output JSON
    if '--pretty' in sys.argv:
        print(json.dumps(status, indent=2))
    else:
        print(json.dumps(status))
    
    # Return 0 if all core components are running
    core_components = ['terma', 'hephaestus', 'rhetor']
    all_running = all(
        components.get(name, {}).get('status') == 'running' 
        for name in core_components
    )
    
    return 0 if all_running else 1

if __name__ == "__main__":
    sys.exit(main())