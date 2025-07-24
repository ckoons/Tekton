"""
Alias command for aish - allows CIs to create reusable command patterns
"""

import os
import json
import shlex
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from shared.env import TektonEnviron

# Simple print functions
def print_error(msg):
    print(f"Error: {msg}")

def print_success(msg):
    print(msg)

def print_info(msg):
    print(msg)

# Simple debug function
def debug_log(component, msg, level="INFO"):
    if os.environ.get('AISH_DEBUG'):
        print(f"[DEBUG:{component}] {msg}", file=sys.stderr)

def log_function(func):
    """Simple decorator for function logging"""
    return func

# Landmark: aish-alias-implementation-2025-01-24
# The alias system allows CIs to build their own command vocabulary,
# encoding learned patterns into reusable shortcuts. This reduces
# repetitive thinking and enables personalized workflows.

@log_function
def get_alias_dir() -> Path:
    """Get the alias storage directory"""
    tekton_root = TektonEnviron.get('TEKTON_ROOT')
    if not tekton_root:
        tekton_root = os.environ.get('TEKTON_ROOT', '/Users/cskoons/projects/github/Tekton')
    alias_dir = Path(tekton_root) / ".tekton" / "aliases"
    return alias_dir

@log_function
def ensure_alias_dir() -> Path:
    """Ensure alias directory exists"""
    alias_dir = get_alias_dir()
    alias_dir.mkdir(parents=True, exist_ok=True)
    debug_log("alias", f"Ensured alias directory: {alias_dir}")
    return alias_dir

@log_function
def load_alias(name: str) -> Optional[Dict]:
    """Load an alias by name"""
    alias_file = get_alias_dir() / f"{name}.json"
    if not alias_file.exists():
        return None
    
    try:
        with open(alias_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        debug_log("alias", f"Error loading alias {name}: {e}", level="ERROR")
        return None

@log_function
def save_alias(name: str, command: str, description: str = "") -> bool:
    """Save an alias"""
    ensure_alias_dir()
    alias_file = get_alias_dir() / f"{name}.json"
    
    alias_data = {
        "name": name,
        "command": command,
        "description": description,
        "created_at": datetime.now().isoformat(),
        "created_by": os.environ.get("USER", "unknown"),
        "usage_count": 0,
        "last_used": None
    }
    
    try:
        with open(alias_file, 'w') as f:
            json.dump(alias_data, f, indent=2)
        debug_log("alias", f"Saved alias: {name}")
        return True
    except Exception as e:
        debug_log("alias", f"Error saving alias {name}: {e}", level="ERROR")
        return False

@log_function
def delete_alias(name: str) -> bool:
    """Delete an alias"""
    alias_file = get_alias_dir() / f"{name}.json"
    if not alias_file.exists():
        return False
    
    try:
        alias_file.unlink()
        debug_log("alias", f"Deleted alias: {name}")
        return True
    except Exception as e:
        debug_log("alias", f"Error deleting alias {name}: {e}", level="ERROR")
        return False

@log_function
def list_aliases() -> List[Dict]:
    """List all aliases"""
    alias_dir = get_alias_dir()
    if not alias_dir.exists():
        return []
    
    aliases = []
    for alias_file in alias_dir.glob("*.json"):
        alias_data = load_alias(alias_file.stem)
        if alias_data:
            aliases.append(alias_data)
    
    return sorted(aliases, key=lambda x: x.get('name', ''))

@log_function
def substitute_parameters(command: str, args: List[str]) -> str:
    """Substitute parameters in alias command
    $1, $2, ... - individual arguments
    $* - all arguments as single string
    $@ - all arguments as separate quoted strings
    """
    # Replace numbered parameters
    for i, arg in enumerate(args):
        command = command.replace(f"${i+1}", arg)
    
    # Replace $* (all args as single string)
    command = command.replace("$*", " ".join(args))
    
    # Replace $@ (all args quoted)
    command = command.replace("$@", " ".join(shlex.quote(arg) for arg in args))
    
    return command

@log_function
def validate_alias_command(command: str) -> Tuple[bool, str]:
    """Validate alias command - ensure no recursive aliases"""
    # Extract first command from potential pipeline
    first_cmd = command.split()[0] if command.strip() else ""
    
    # Check if first command is an alias
    if first_cmd and load_alias(first_cmd):
        return False, f"Cannot use alias '{first_cmd}' within alias definition"
    
    # Check for any 'aish <alias>' patterns in the command
    import re
    for match in re.finditer(r'aish\s+(\w+)', command):
        potential_alias = match.group(1)
        if load_alias(potential_alias):
            return False, f"Cannot use alias 'aish {potential_alias}' within alias definition"
    
    return True, ""

@log_function
def handle_alias_create(args):
    """Handle alias create command"""
    if len(args) < 2:
        print_error("Usage: aish alias create <name> <command> [description]")
        return
    
    name = args[0]
    command = args[1]
    description = args[2] if len(args) > 2 else ""
    
    # Check if alias already exists
    if load_alias(name):
        print_error(f"Alias '{name}' already defined. Use 'aish alias delete {name}' first.")
        return
    
    # Validate command (no recursive aliases)
    valid, error_msg = validate_alias_command(command)
    if not valid:
        print_error(f"Invalid alias command: {error_msg}")
        return
    
    # Save the alias
    if save_alias(name, command, description):
        print_success(f"Created alias '{name}'")
    else:
        print_error(f"Failed to create alias '{name}'")

@log_function
def handle_alias_delete(args):
    """Handle alias delete command"""
    if len(args) < 1:
        print_error("Usage: aish alias delete <name>")
        return
    
    name = args[0]
    
    if delete_alias(name):
        print_success(f"Deleted alias '{name}'")
    else:
        print_error(f"Alias '{name}' not found")

@log_function
def handle_alias_show(args):
    """Handle alias show command"""
    if len(args) < 1:
        print_error("Usage: aish alias show <name>")
        return
    
    name = args[0]
    alias_data = load_alias(name)
    
    if not alias_data:
        print_error(f"Alias '{name}' not found")
        return
    
    print(f"\nAlias: {alias_data['name']}")
    print(f"Command: {alias_data['command']}")
    if alias_data.get('description'):
        print(f"Description: {alias_data['description']}")
    print(f"Created: {alias_data['created_at']}")
    print(f"Created by: {alias_data['created_by']}")
    print(f"Usage count: {alias_data.get('usage_count', 0)}")
    if alias_data.get('last_used'):
        print(f"Last used: {alias_data['last_used']}")

@log_function
def handle_alias_list(args):
    """Handle alias list command"""
    aliases = list_aliases()
    
    if not aliases:
        print_info("No aliases defined")
        return
    
    print("\nDefined aliases:")
    print("-" * 60)
    
    for alias in aliases:
        desc = f" - {alias['description']}" if alias.get('description') else ""
        print(f"{alias['name']:<20} {alias['command'][:40]}{'...' if len(alias['command']) > 40 else ''}{desc}")

@log_function
def handle_alias_command(args):
    """Main entry point for alias command"""
    if not args:
        print_error("Usage: aish alias <create|delete|list|show> ...")
        return
    
    subcommand = args[0]
    subargs = args[1:]
    
    if subcommand == "create":
        handle_alias_create(subargs)
    elif subcommand == "delete":
        handle_alias_delete(subargs)
    elif subcommand == "list":
        handle_alias_list(subargs)
    elif subcommand == "show":
        handle_alias_show(subargs)
    else:
        print_error(f"Unknown alias subcommand: {subcommand}")
        print_error("Usage: aish alias <create|delete|list|show> ...")

def execute_alias(name: str, args: List[str]) -> int:
    """Execute an alias with given arguments"""
    alias_data = load_alias(name)
    if not alias_data:
        return 1
    
    # Substitute parameters
    command = substitute_parameters(alias_data['command'], args)
    debug_log("alias", f"Executing alias '{name}': {command}")
    
    # Update usage stats
    alias_data['usage_count'] = alias_data.get('usage_count', 0) + 1
    alias_data['last_used'] = datetime.now().isoformat()
    
    alias_file = get_alias_dir() / f"{name}.json"
    try:
        with open(alias_file, 'w') as f:
            json.dump(alias_data, f, indent=2)
    except:
        pass  # Don't fail execution if we can't update stats
    
    # Execute the command in a subprocess
    try:
        result = subprocess.run(command, shell=True, capture_output=False)
        return result.returncode
    except Exception as e:
        print_error(f"Error executing alias '{name}': {e}")
        return 1