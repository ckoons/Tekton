#!/usr/bin/env python3
"""
Launch or replace a component's AI specialist.
Handles registry cleanup and graceful shutdown of existing instances.
"""

import json
import os
import sys
import socket
import time
import fcntl
from pathlib import Path
import subprocess
import argparse

try:
    from landmarks import architecture_decision, integration_point, danger_zone
except ImportError:
    # Fallback decorators if landmarks not available
    def architecture_decision(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def danger_zone(**kwargs):
        def decorator(func):
            return func
        return decorator

def load_registry():
    """Load the AI registry with file locking."""
    tekton_root = os.environ.get('TEKTON_ROOT', '/Users/cskoons/projects/github/Tekton')
    registry_path = Path(tekton_root) / '.tekton' / 'ai_registry' / 'platform_ai_registry.json'
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    
    if not registry_path.exists():
        return {}
    
    with open(registry_path, 'r') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        try:
            return json.load(f)
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)

def save_registry(registry):
    """Save the AI registry with file locking."""
    tekton_root = os.environ.get('TEKTON_ROOT', '/Users/cskoons/projects/github/Tekton')
    registry_path = Path(tekton_root) / '.tekton' / 'ai_registry' / 'platform_ai_registry.json'
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to temp file first
    temp_path = registry_path.with_suffix('.tmp')
    with open(temp_path, 'w') as f:
        json.dump(registry, f, indent=2)
    
    # Atomic rename
    temp_path.rename(registry_path)

def shutdown_socket(port):
    """Try to gracefully shutdown a socket on the given port."""
    try:
        # Send shutdown command to the AI specialist
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect(('localhost', port))
        sock.send(b'{"command": "shutdown"}\n')
        sock.close()
        time.sleep(0.5)  # Give it time to shut down
    except:
        # If it fails, that's ok - process might already be gone
        pass

@architecture_decision(
    title="Component-specific AI replacement",
    rationale="Need atomic replacement to avoid orphaned AI processes and port conflicts",
    alternatives_considered=["Kill all and restart", "Registry versioning", "Port reuse"],
    impacts=["reliability", "port_management", "process_lifecycle"],
    decided_by="Casey",
    date="2025-01-04"
)
@integration_point(
    title="AI specialist launcher",
    target_component="All Tekton components",
    protocol="Process spawn with registry update",
    data_flow="Component name -> Registry cleanup -> Process launch -> Port registration"
)
def launch_component_ai(component_name, verbose=False):
    """Launch or replace a component's AI specialist."""
    ai_name = f"{component_name}-ai"
    
    if verbose:
        print(f"Launching AI specialist for {component_name}...")
    
    # 1. Clean registry entry for this specific AI
    registry = load_registry()
    if ai_name in registry:
        old_entry = registry[ai_name]
        old_port = old_entry.get('port')
        
        if verbose:
            print(f"Found existing {ai_name} on port {old_port}, cleaning up...")
        
        # Try to gracefully shutdown old socket
        if old_port:
            shutdown_socket(old_port)
        
        # Remove from registry
        del registry[ai_name]
        save_registry(registry)
        
        if verbose:
            print(f"Cleaned registry entry for {ai_name}")
    
    # 2. Launch the new AI specialist
    # Find the component directory
    tekton_root = os.environ.get('TEKTON_ROOT', '/Users/cskoons/projects/github/Tekton')
    
    # Map component names to their directories
    component_dirs = {
        'hermes': 'Hermes',
        'engram': 'Engram', 
        'rhetor': 'Rhetor',
        'apollo': 'Apollo',
        'athena': 'Athena',
        'prometheus': 'Prometheus',
        'telos': 'Telos',
        'metis': 'Metis',
        'harmonia': 'Harmonia',
        'synthesis': 'Synthesis',
        'sophia': 'Sophia',
        'noesis': 'Noesis',
        'penia': 'Penia',
        'ergon': 'Ergon',
        'terma': 'Terma',
        'numa': 'Numa',
        'tekton_core': 'TektonCore',
        'hephaestus': 'Hephaestus'
    }
    
    component_dir = component_dirs.get(component_name.lower())
    if not component_dir:
        print(f"Unknown component: {component_name}")
        return False
    
    # Launch the AI specialist
    launch_script = f"{tekton_root}/scripts/enhanced_tekton_ai_launcher.py"
    if not os.path.exists(launch_script):
        print(f"Launch script not found: {launch_script}")
        return False
    
    cmd = [
        sys.executable,
        launch_script,
        component_name,
        "-v" if verbose else "",
        "--no-cleanup"  # Don't cleanup on exit
    ]
    
    if verbose:
        print(f"Launching: {' '.join(cmd)}")
    
    # Launch in background
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL if not verbose else None,
        stderr=subprocess.DEVNULL if not verbose else None
    )
    
    # Give it a moment to start
    time.sleep(2)
    
    # Verify it registered
    registry = load_registry()
    if ai_name in registry:
        entry = registry[ai_name]
        print(f"✓ {ai_name} launched successfully on port {entry.get('port')}")
        return True
    else:
        print(f"✗ {ai_name} failed to register")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Launch or replace a component AI specialist'
    )
    parser.add_argument(
        'component',
        help='Component name (e.g., rhetor, hermes, apollo)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    success = launch_component_ai(args.component, args.verbose)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()