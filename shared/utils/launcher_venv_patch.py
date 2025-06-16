#!/usr/bin/env python3
"""
Patch for enhanced_tekton_launcher.py to add virtual environment support.
This shows the modifications needed to integrate venv activation.
"""

import json
from pathlib import Path


def get_venv_for_component(component_name: str) -> str:
    """Get the appropriate virtual environment for a component."""
    # Load mapping
    mapping_file = Path(__file__).parent / "venv-mapping.json"
    if mapping_file.exists():
        with open(mapping_file) as f:
            mapping = json.load(f)
        return mapping.get(component_name.lower(), "tekton-core")
    
    # Fallback logic if mapping doesn't exist
    component_lower = component_name.lower()
    
    if component_lower in ["engram", "hermes", "sophia", "athena"]:
        return "tekton-ml"
    elif component_lower in ["budget", "rhetor", "synthesis"]:
        return "tekton-ai"
    elif component_lower in ["ergon", "metis", "harmonia"]:
        return "tekton-data"
    else:
        return "tekton-core"


def get_venv_python(venv_name: str, base_dir: Path = None) -> str:
    """Get the Python executable path for a virtual environment."""
    if base_dir is None:
        base_dir = Path.home() / "venvs"
    
    venv_path = base_dir / venv_name
    
    # Check if venv exists
    if not venv_path.exists():
        # Fallback to system Python
        return sys.executable
    
    # Return python executable path
    if platform.system() == "Windows":
        return str(venv_path / "Scripts" / "python.exe")
    else:
        return str(venv_path / "bin" / "python")


# Add this to the launcher's launch_component_process method:
"""
# MODIFICATION FOR enhanced_tekton_launcher.py
# Add after line 332 (cmd = self.get_component_command(component_name))

# Activate appropriate virtual environment
venv_name = get_venv_for_component(component_name)
venv_python = get_venv_python(venv_name)

# Replace 'python' or 'python3' in cmd with venv python
if cmd and len(cmd) > 0:
    if cmd[0] in ['python', 'python3']:
        cmd[0] = venv_python
    elif cmd[0] == 'uv' and len(cmd) > 2 and cmd[1] == 'run':
        # For uv run commands, inject --python argument
        cmd.insert(2, '--python')
        cmd.insert(3, venv_python)

# Log venv usage
if self.verbose:
    self.log(f"Using venv: {venv_name}", "venv", component_name)
"""


# Example of modified get_component_command method:
def get_component_command_with_venv(self, component_name: str) -> List[str]:
    """Get launch command for a component with venv support."""
    # Original logic to determine the command
    comp_info = self.config.get_component(component_name)
    
    # Get venv information
    venv_name = get_venv_for_component(component_name)
    venv_python = get_venv_python(venv_name)
    
    # Existing command logic...
    if comp_info.launch_command:
        cmd = comp_info.launch_command.split()
    else:
        # Default commands based on component
        cmd = ["python", "-m", component_name.lower()]
    
    # Replace python with venv python
    if cmd and len(cmd) > 0:
        if cmd[0] in ['python', 'python3']:
            cmd[0] = venv_python
    
    return cmd


# Add environment variable for venv awareness:
"""
# MODIFICATION FOR enhanced_tekton_launcher.py  
# Add after line 336 (env[f"{component_name.upper()}_PORT"] = str(port))

# Add venv information to environment
venv_name = get_venv_for_component(component_name)
env['TEKTON_VENV'] = venv_name
env['VIRTUAL_ENV'] = str(Path.home() / 'venvs' / venv_name)
"""