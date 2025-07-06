"""
AI forwarding command handler.
"""

import os
import sys
from pathlib import Path

# Add path for forwarding registry
sys.path.insert(0, str(Path(__file__).parent.parent))
from forwarding.forwarding_registry import ForwardingRegistry


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
        print("No AI forwarding active")
        return 0
    
    print("Active AI Forwards:")
    print("-" * 30)
    for ai_name, terminal_name in forwards.items():
        print(f"  {ai_name:<12} → {terminal_name}")
    
    return 0


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