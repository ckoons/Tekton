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

# Try to import landmarks if available
try:
    from landmarks import architecture_decision, integration_point, api_contract, state_checkpoint
except ImportError:
    # Landmarks not available, create no-op decorators
    def architecture_decision(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def api_contract(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def state_checkpoint(**kwargs):
        def decorator(func):
            return func
        return decorator


def load_project_registry() -> Dict:
    """Load the Tekton project registry"""
    tekton_root = TektonEnviron.get('TEKTON_ROOT')
    if not tekton_root:
        print("Error: TEKTON_ROOT not set")
        return {"projects": []}
    
    registry_path = Path(tekton_root) / ".tekton" / "projects" / "projects.json"
    
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
    tekton_root = TektonEnviron.get('TEKTON_ROOT')
    if not tekton_root:
        print("Error: TEKTON_ROOT not set")
        return {"version": "1.0", "forwards": {}, "last_updated": datetime.now().isoformat()}
    
    registry_path = Path(tekton_root) / ".tekton" / "aish" / "forwarding.json"
    
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
    tekton_root = TektonEnviron.get('TEKTON_ROOT')
    if not tekton_root:
        print("Error: TEKTON_ROOT not set")
        return
    
    registry_path = Path(tekton_root) / ".tekton" / "aish" / "forwarding.json"
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
    
    # Get CI registry to find ports
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
    from shared.aish.src.registry.ci_registry import get_registry
    ci_registry = get_registry()
    
    print("Tekton Managed Projects:")
    print("-" * 90)
    print(f"{'Project':<20} {'CI':<20} {'Port':<10} {'Forward':<30}")
    print("-" * 90)
    
    for project in projects:
        project_name = project.get('name', 'Unknown')
        companion_ai = project.get('companion_intelligence', 'none')
        
        # Get port from CI registry
        port_display = "n/a"
        if companion_ai and companion_ai != 'none':
            # Special case for Tekton
            if project_name.lower() == 'tekton':
                companion_ai = "numa"
                numa_ci = ci_registry.get_by_name('numa')
                if numa_ci:
                    # numa uses endpoint not port field
                    if 'port' in numa_ci:
                        port_display = str(numa_ci['port'])
                    elif 'endpoint' in numa_ci:
                        # Extract port from endpoint URL
                        endpoint = numa_ci['endpoint']
                        port_display = endpoint.split(':')[-1].rstrip('/')
                    else:
                        port_display = 'n/a'
            else:
                ci_name = f"{project_name.lower()}-ai"
                project_ci = ci_registry.get_by_name(ci_name)
                if project_ci:
                    port_display = str(project_ci.get('port', 'n/a'))
                companion_ai = ci_name
        else:
            companion_ai = "none"
        
        # Check if this project is forwarded
        forward_key = f"project:{project_name}"
        forwarded_to = forwarding_registry.get("forwards", {}).get(forward_key, "none")
        
        # Check if the terminal is active
        if isinstance(forwarded_to, dict):
            # forwarded_to is a dict, extract terminal name
            forwarded_to = forwarded_to.get('terminal', 'none')
        
        if forwarded_to != "none" and forwarded_to in active_terminals:
            terminal_info = active_terminals[forwarded_to]
            if isinstance(terminal_info, dict):
                # Handle dict format
                status = terminal_info.get('status', 'unknown')
                forward_display = f"{forwarded_to} ({status})"
            else:
                # Handle tuple format (pid, status)
                pid, status = terminal_info
                forward_display = f"{forwarded_to} ({status})"
        elif forwarded_to != "none":
            forward_display = f"{forwarded_to} (inactive)"
        else:
            forward_display = "none"
        
        print(f"{project_name:<20} {companion_ai:<20} {port_display:<10} {forward_display:<30}")
    
    print("-" * 90)
    print(f"\nTotal projects: {len(projects)}")
    
    # Show legend if there are any forwards
    if any(f.startswith("project:") for f in forwarding_registry.get("forwards", {})):
        print("\nNote: (active) = terminal is running, (inactive) = terminal not found")
    
    return True


def forward_project(args: List[str]) -> bool:
    """Forward project CI to terminal"""
    if not args:
        print("Usage: aish project forward <project-name> [terminal-name]")
        print("  If terminal-name is omitted, forwards to current terminal")
        return False
    
    project_name = args[0]
    
    # Check if target terminal was specified
    if len(args) > 1:
        target_terminal = args[1]
        # Verify the target terminal exists via Terma
        active_terminals = get_active_terminals()
        if not active_terminals:
            print("Warning: Cannot verify terminal names - Terma may not be running")
            print("Proceeding with specified terminal name")
        elif target_terminal not in active_terminals:
            print(f"Error: Terminal '{target_terminal}' not found")
            print(f"\nActive terminals:")
            for term_name, (pid, status) in active_terminals.items():
                print(f"  - {term_name} [{pid}] ({status})")
            return False
        terminal_name = target_terminal
    else:
        # Get current terminal name
        terminal_name = TektonEnviron.get('TERMA_TERMINAL_NAME')
        if not terminal_name:
            print("Error: Not running in a Terma terminal")
            print("Project forwarding requires a named Terma terminal session")
            print("Use: aish project forward <project-name> <terminal-name>")
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
    
    # Load project registry to find actual project name (case-insensitive)
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
    
    # Use actual project name for key
    forward_key = f"project:{project['name']}"
    if forward_key not in forwarding_registry.get("forwards", {}):
        print(f"Project '{project['name']}' is not currently forwarded")
        return True
    
    # Remove the forward
    terminal_name = forwarding_registry["forwards"].pop(forward_key)
    
    # Save registry
    save_forwarding_registry(forwarding_registry)
    
    print(f"✓ Removed forward for project '{project_name}' (was forwarded to '{terminal_name}')")
    
    return True


@architecture_decision(
    title="Project CI Management",
    description="Manages Companion Intelligence forwarding for Tekton projects",
    rationale="Each project can have its own CI that forwards messages to specific terminals",
    alternatives_considered=["Single global CI", "Direct project notifications"],
    impacts=["project autonomy", "CI scalability", "workflow flexibility"],
    decided_by="Casey",
    decision_date="2025-01-17"
)
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