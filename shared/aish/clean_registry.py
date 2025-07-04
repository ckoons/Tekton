#!/usr/bin/env python3
"""
Clean the AI Registry - Remove stale entries and verify running processes
"""

import json
import os
import sys
import psutil
import socket
from pathlib import Path

def check_process_exists(pid):
    """Check if a process with given PID exists."""
    try:
        return psutil.pid_exists(pid)
    except:
        # Fallback method
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False

def check_port_open(port):
    """Check if a port is actually listening."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

def clean_registry(dry_run=False):
    """Clean the AI registry of stale entries."""
    registry_path = Path.home() / '.tekton' / 'ai_registry' / 'platform_ai_registry.json'
    
    if not registry_path.exists():
        print("Registry not found at:", registry_path)
        return
    
    # Read current registry
    with open(registry_path, 'r') as f:
        registry = json.load(f)
    
    print(f"Current registry has {len(registry)} entries")
    
    # Track what we'll remove
    to_remove = []
    healthy = []
    
    for ai_name, entry in registry.items():
        port = entry.get('port')
        pid = entry.get('metadata', {}).get('pid')
        
        process_exists = check_process_exists(pid) if pid else False
        port_open = check_port_open(port) if port else False
        
        if process_exists and port_open:
            healthy.append(ai_name)
            print(f"✓ {ai_name}: PID {pid} running, port {port} open")
        else:
            to_remove.append(ai_name)
            status = []
            if not process_exists:
                status.append(f"PID {pid} not found")
            if not port_open:
                status.append(f"port {port} closed")
            print(f"✗ {ai_name}: {', '.join(status)}")
    
    print(f"\nHealthy: {len(healthy)}, Stale: {len(to_remove)}")
    
    if to_remove:
        if dry_run:
            print("\nDry run - would remove:", ', '.join(to_remove))
        else:
            # Remove stale entries
            for ai_name in to_remove:
                del registry[ai_name]
            
            # Write cleaned registry
            with open(registry_path, 'w') as f:
                json.dump(registry, f, indent=2)
            
            print(f"\nRemoved {len(to_remove)} stale entries")
            print("Registry cleaned!")
    else:
        print("\nRegistry is clean - no stale entries found")

def reset_registry():
    """Completely reset the registry."""
    registry_path = Path.home() / '.tekton' / 'ai_registry' / 'platform_ai_registry.json'
    
    if registry_path.exists():
        # Back up current registry
        backup_path = registry_path.with_suffix('.json.backup')
        with open(registry_path, 'r') as f:
            current = json.load(f)
        with open(backup_path, 'w') as f:
            json.dump(current, f, indent=2)
        print(f"Backed up current registry to: {backup_path}")
    
    # Create empty registry
    with open(registry_path, 'w') as f:
        json.dump({}, f)
    
    print("Registry reset to empty state")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Clean AI Registry')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be removed')
    parser.add_argument('--reset', action='store_true', help='Completely reset registry')
    
    args = parser.parse_args()
    
    if args.reset:
        response = input("This will completely reset the registry. Continue? (yes/no): ")
        if response.lower() == 'yes':
            reset_registry()
        else:
            print("Aborted")
    else:
        clean_registry(dry_run=args.dry_run)