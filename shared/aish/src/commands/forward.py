"""
AI forwarding command handler.
"""

import os
import sys
from pathlib import Path

# Try to import landmarks if available
try:
    from landmarks import architecture_decision, integration_point, api_contract, state_checkpoint
except ImportError:
    # Landmarks not available, create no-op decorators
    def architecture_decision(name, description, rationale=""):
        def decorator(func):
            return func
        return decorator
    
    def integration_point(name, description, rationale=""):
        def decorator(func):
            return func
        return decorator
    
    def api_contract(name, description, rationale=""):
        def decorator(func):
            return func
        return decorator
    
    def state_checkpoint(name, description, rationale=""):
        def decorator(func):
            return func
        return decorator

# Add path for forwarding registry
sys.path.insert(0, str(Path(__file__).parent.parent))
from forwarding.forwarding_registry import ForwardingRegistry


@architecture_decision(
    title="AI Message Forwarding",
    description="Routes AI messages to human terminals for attention",
    rationale="Enables human-in-the-loop AI interactions by forwarding messages to terminal inboxes",
    alternatives_considered=["Direct AI-to-AI only", "Central message queue"],
    impacts=["collaboration", "AI transparency", "human oversight"],
    decided_by="Casey",
    decision_date="2025-01-17"
)
def handle_forward_command(args):
    """Handle 'aish forward' commands"""
    
    if len(args) == 0:
        print_forward_usage()
        return 1
    
    command = args[0]
    registry = ForwardingRegistry()
    
    if command == "list":
        return list_forwards(registry)
    
    elif command == "remove" and len(args) == 2:
        # Handle 'aish forward remove <ai>'
        ai_name = args[1]
        return handle_unforward_command([ai_name])
    
    elif len(args) == 2:
        ai_name, terminal_name = args
        return set_forward(registry, ai_name, terminal_name)
    
    else:
        print_forward_usage()
        return 1


def print_forward_usage():
    """Print usage information"""
    print("Usage: aish forward <ai-name> <terminal-name>")
    print("       aish forward list")
    print("       aish forward remove <ai-name>")
    print("")
    print("Examples:")
    print("  aish forward apollo jill      # Forward apollo messages to jill")
    print("  aish forward rhetor alice     # Forward rhetor messages to alice")
    print("  aish forward list             # Show active forwards")
    print("  aish forward remove apollo    # Remove forwarding")


@state_checkpoint(
    title="Forward Registration",
    description="Establishes AI-to-terminal message routing",
    state_type="forwarding_rule",
    validation="AI name validated, forwarding registered"
)
def set_forward(registry, ai_name, terminal_name):
    """Set up forwarding"""
    # Validate AI name
    valid_ais = ['apollo', 'athena', 'rhetor', 'prometheus', 'synthesis', 
                 'metis', 'harmonia', 'numa', 'noesis', 'engram', 'penia',
                 'hermes', 'ergon', 'sophia', 'telos', 'hephaestus']
    
    if ai_name not in valid_ais:
        print(f"Unknown AI: {ai_name}")
        print(f"Valid AIs: {', '.join(valid_ais)}")
        return 1
    
    # Set forwarding
    registry.set_forward(ai_name, terminal_name)
    print(f"✓ Forwarding {ai_name} messages to {terminal_name}")
    return 0


def list_forwards(registry):
    """List active forwards"""
    forwards = registry.list_forwards()
    
    if not forwards:
        print("No forwarding active")
        return 0
    
    # Separate AI forwards and project forwards
    ai_forwards = {}
    project_forwards = {}
    
    for key, terminal_name in forwards.items():
        if key.startswith("project:"):
            project_name = key[8:]  # Remove "project:" prefix
            project_forwards[project_name] = terminal_name
        else:
            ai_forwards[key] = terminal_name
    
    # Show AI forwards
    if ai_forwards:
        print("Active AI Forwards:")
        print("-" * 30)
        for ai_name, terminal_name in ai_forwards.items():
            print(f"  {ai_name:<12} → {terminal_name}")
    
    # Show project forwards
    if project_forwards:
        if ai_forwards:
            print()  # Add spacing if both types exist
        print("Active Project Forwards:")
        print("-" * 30)
        for project_name, terminal_name in project_forwards.items():
            print(f"  {project_name:<12} → {terminal_name}")
    
    return 0


@state_checkpoint(
    title="Forward Removal",
    description="Removes AI-to-terminal message routing",
    state_type="forwarding_rule",
    validation="Forwarding rule removed from registry"
)
def handle_unforward_command(args):
    """Handle 'aish unforward' commands"""
    
    if len(args) != 1:
        print("Usage: aish unforward <ai-name>")
        return 1
    
    ai_name = args[0]
    registry = ForwardingRegistry()
    
    if registry.get_forward(ai_name):
        terminal_name = registry.get_forward(ai_name)
        registry.remove_forward(ai_name)
        print(f"✓ Stopped forwarding {ai_name} (was going to {terminal_name})")
        return 0
    else:
        print(f"No forwarding active for {ai_name}")
        return 1