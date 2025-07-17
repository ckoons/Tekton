#!/usr/bin/env python3
"""
aish project commands - Manage Tekton project CI forwarding

Commands:
    aish project list       - List all Tekton managed projects with CI and forwarding info
    aish project forward    - Forward project CI to current terminal
    aish project unforward  - Remove project CI forwarding
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import requests
from datetime import datetime

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.env import TektonEnviron
from shared.urls import tekton_url


def load_project_registry() -> Dict:
    """Load the Tekton project registry"""
    registry_path = Path.home() / ".tekton" / "projects" / "registry.json"
    
    if not registry_path.exists():
        return {"projects": []}
    
    try:
        with open(registry_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading project registry: {e}")
        return {"projects": []}


def load_forwarding_registry() -> Dict:
    """Load the forwarding registry"""
    registry_path = Path.home() / ".tekton" / "aish" / "forwarding.json"
    
    if not registry_path.exists():
        return {"version": "1.0", "forwards": {}, "last_updated": datetime.now().isoformat()}
    
    try:
        with open(registry_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading forwarding registry: {e}")
        return {"version": "1.0", "forwards": {}, "last_updated": datetime.now().isoformat()}


def save_forwarding_registry(registry: Dict):
    """Save the forwarding registry"""
    registry_path = Path.home() / ".tekton" / "aish" / "forwarding.json"
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    
    registry["last_updated"] = datetime.now().isoformat()
    
    try:
        with open(registry_path, 'w') as f:
            json.dump(registry, f, indent=2)
    except Exception as e:
        print(f"Error saving forwarding registry: {e}")


def get_active_terminals() -> Dict[str, Tuple[str, str]]:
    """Get active terminals from Terma. Returns dict of terminal_name -> (pid, status)"""
    try:
        # Get Terma endpoint
        terma_url = tekton_url('terma', '/api/terminals')
        response = requests.get(terma_url, timeout=2)
        
        if response.status_code == 200:
            terminals = response.json()
            # Convert to dict for easy lookup
            return {
                t.get('name', 'unnamed'): (t.get('pid', '?'), t.get('status', 'unknown'))
                for t in terminals
            }
    except:
        # If Terma isn't running or accessible, return empty
        pass
    
    return {}


def list_projects(args: List[str]) -> bool:
    """List all Tekton managed projects with CI and forwarding info"""
    # Load registries
    project_registry = load_project_registry()
    forwarding_registry = load_forwarding_registry()
    active_terminals = get_active_terminals()
    
    projects = project_registry.get("projects", [])
    
    if not projects:
        print("No Tekton managed projects found.")
        print("\nUse the Tekton UI to create projects.")
        return True
    
    print("Tekton Managed Projects:")
    print("-" * 70)
    print(f"{'Project':<20} {'CI':<20} {'Forward':<30}")
    print("-" * 70)
    
    for project in projects:
        project_name = project.get('name', 'Unknown')
        companion_ai = project.get('companion_ai', 'none')
        
        # Check if this project is forwarded
        forward_key = f"project:{project_name}"
        forwarded_to = forwarding_registry.get("forwards", {}).get(forward_key, "none")
        
        # Check if the terminal is active
        if forwarded_to != "none" and forwarded_to in active_terminals:
            pid, status = active_terminals[forwarded_to]
            forward_display = f"{forwarded_to} ({status})"
        elif forwarded_to != "none":
            forward_display = f"{forwarded_to} (inactive)"
        else:
            forward_display = "none"
        
        # Special handling for Tekton project
        if project_name == "Tekton":
            companion_ai = "numa-ai"  # Tekton uses Numa as its CI
        
        print(f"{project_name:<20} {companion_ai:<20} {forward_display:<30}")
    
    print("-" * 70)
    print(f"\nTotal projects: {len(projects)}")
    
    # Show legend if there are any forwards
    if any(f.startswith("project:") for f in forwarding_registry.get("forwards", {})):
        print("\nNote: (active) = terminal is running, (inactive) = terminal not found")
    
    return True


def forward_project(args: List[str]) -> bool:
    """Forward project CI to current terminal"""
    if not args:
        print("Usage: aish project forward <project-name>")
        return False
    
    project_name = args[0]
    
    # Get current terminal name
    terminal_name = TektonEnviron.get('TERMA_TERMINAL_NAME')
    if not terminal_name:
        print("Error: Not running in a Terma terminal")
        print("Project forwarding requires a named Terma terminal session")
        return False
    
    # Load project registry to verify project exists
    project_registry = load_project_registry()
    projects = project_registry.get("projects", [])
    
    project = None
    for p in projects:
        if p.get('name', '').lower() == project_name.lower():
            project = p
            break
    
    if not project:
        print(f"Error: Project '{project_name}' not found")
        print("\nAvailable projects:")
        for p in projects:
            print(f"  - {p.get('name', 'Unknown')}")
        return False
    
    # Load forwarding registry
    forwarding_registry = load_forwarding_registry()
    
    # Add the forward
    forward_key = f"project:{project['name']}"
    forwarding_registry["forwards"][forward_key] = terminal_name
    
    # Save registry
    save_forwarding_registry(forwarding_registry)
    
    companion_ai = project.get('companion_ai', 'none')
    if project['name'] == 'Tekton':
        companion_ai = 'numa-ai'
    
    print(f"✓ Forwarded project '{project['name']}' (CI: {companion_ai}) to terminal '{terminal_name}'")
    print(f"\nMessages to 'project:{project['name']}' will now appear in this terminal")
    
    return True


def unforward_project(args: List[str]) -> bool:
    """Remove project CI forwarding"""
    if not args:
        print("Usage: aish project unforward <project-name>")
        return False
    
    project_name = args[0]
    
    # Load forwarding registry
    forwarding_registry = load_forwarding_registry()
    
    # Check if forward exists
    forward_key = f"project:{project_name}"
    if forward_key not in forwarding_registry.get("forwards", {}):
        print(f"Project '{project_name}' is not currently forwarded")
        return True
    
    # Remove the forward
    terminal_name = forwarding_registry["forwards"].pop(forward_key)
    
    # Save registry
    save_forwarding_registry(forwarding_registry)
    
    print(f"✓ Removed forward for project '{project_name}' (was forwarded to '{terminal_name}')")
    
    return True


def handle_project_command(args: List[str]) -> bool:
    """Handle aish project commands"""
    if not args or args[0] == 'help':
        print("Usage: aish project <command> [options]")
        print()
        print("Commands:")
        print("  list                List all Tekton managed projects")
        print("  forward <project>   Forward project CI to current terminal")
        print("  unforward <project> Remove project CI forwarding")
        print()
        print("Examples:")
        print("  aish project list")
        print("  aish project forward MyWebApp")
        print("  aish project unforward MyWebApp")
        return True
    
    command = args[0]
    command_args = args[1:] if len(args) > 1 else []
    
    if command == 'list':
        return list_projects(command_args)
    elif command == 'forward':
        return forward_project(command_args)
    elif command == 'unforward':
        return unforward_project(command_args)
    else:
        print(f"Unknown project command: {command}")
        print("Use 'aish project help' for usage")
        return False