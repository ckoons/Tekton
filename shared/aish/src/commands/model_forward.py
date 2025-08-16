"""
Model forwarding command handler for CI terminals.
Allows forwarding CI terminals to specific models like Claude.
"""

import os
import sys
from pathlib import Path

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from shared.aish.src.registry.ci_registry import get_registry


def handle_model_forward_command(args):
    """
    Handle 'aish forward <ci-name> <model>' commands for model switching
    
    Args:
        args: List of arguments [ci-name, model, ...]
    
    Returns:
        0 on success, 1 on error
    """
    
    if len(args) < 2:
        print_model_forward_usage()
        return 1
    
    # Check for list command
    if args[0] == "list":
        return list_model_forwards()
    
    ci_name = args[0]
    model = args[1]
    model_args = " ".join(args[2:]) if len(args) > 2 else ""
    
    # Special handling for Claude models
    if model in ["claude", "claude-opus", "claude-sonnet", "claude-haiku"]:
        return set_claude_forward(ci_name, model, model_args)
    
    # Handle other models
    return set_model_forward(ci_name, model, model_args)


def handle_model_unforward_command(args):
    """
    Handle 'aish unforward <ci-name>' commands to return to default model
    
    Args:
        args: List of arguments [ci-name]
    
    Returns:
        0 on success, 1 on error
    """
    
    if len(args) != 1:
        print("Usage: aish unforward <ci-name>")
        print("Example: aish unforward apollo-ci")
        return 1
    
    ci_name = args[0]
    registry = get_registry()
    
    # Check if CI exists
    ci_info = registry.get_by_name(ci_name)
    if not ci_info:
        print(f"CI '{ci_name}' not found in registry")
        return 1
    
    # Clear forward state
    if registry.clear_forward_state(ci_name):
        print(f"✓ Cleared forward for {ci_name}, returning to default model")
        return 0
    else:
        print(f"Failed to clear forward state for {ci_name}")
        return 1


def set_claude_forward(ci_name, model, args):
    """Set up Claude forwarding for a CI"""
    
    registry = get_registry()
    
    # Check if CI exists
    ci_info = registry.get_by_name(ci_name)
    if not ci_info:
        print(f"CI '{ci_name}' not found in registry")
        print("Use 'aish list' to see available CIs")
        return 1
    
    # Determine Claude variant
    if model == "claude":
        claude_cmd = "claude --print"
    elif model == "claude-opus":
        claude_cmd = "claude --model claude-3-opus-20240229 --print"
    elif model == "claude-sonnet":
        claude_cmd = "claude --model claude-3-sonnet-20240229 --print"
    elif model == "claude-haiku":
        claude_cmd = "claude --model claude-3-haiku-20240307 --print"
    else:
        claude_cmd = f"claude --model {model} --print"
    
    # Add any additional arguments
    if args:
        claude_cmd += f" {args}"
    
    # Set forward state in registry (persistent)
    if registry.set_forward_state(ci_name, "claude", claude_cmd):
        print(f"✓ Forwarded {ci_name} to {model}")
        print(f"  Command: {claude_cmd}")
        print(f"  Use 'aish unforward {ci_name}' to return to default model")
        return 0
    else:
        print(f"Failed to set forward state for {ci_name}")
        return 1


def set_model_forward(ci_name, model, args):
    """Set up generic model forwarding for a CI"""
    
    registry = get_registry()
    
    # Check if CI exists
    ci_info = registry.get_by_name(ci_name)
    if not ci_info:
        print(f"CI '{ci_name}' not found in registry")
        print("Use 'aish list' to see available CIs")
        return 1
    
    # Build model command
    model_cmd = model
    if args:
        model_cmd += f" {args}"
    
    # Set forward state in registry (persistent)
    if registry.set_forward_state(ci_name, model, model_cmd):
        print(f"✓ Forwarded {ci_name} to {model}")
        if args:
            print(f"  Arguments: {args}")
        print(f"  Use 'aish unforward {ci_name}' to return to default model")
        return 0
    else:
        print(f"Failed to set forward state for {ci_name}")
        return 1


def list_model_forwards():
    """List all active model forwards"""
    
    registry = get_registry()
    forwards = registry.list_forward_states()
    
    if not forwards:
        print("No model forwarding active")
        return 0
    
    print("Active Model Forwards:")
    print("-" * 50)
    
    for ci_name, state in forwards.items():
        model = state.get('model', 'unknown')
        args = state.get('args', '')
        started = state.get('started', '')
        
        print(f"  {ci_name:<20} → {model}")
        if args:
            print(f"    Command: {args}")
        if started:
            print(f"    Started: {started}")
    
    print()
    print("Use 'aish unforward <ci-name>' to clear forwarding")
    
    return 0


def print_model_forward_usage():
    """Print usage information for model forwarding"""
    print("Model Forwarding - Route CI to specific AI models")
    print()
    print("Usage:")
    print("  aish forward <ci-name> <model> [args...]  # Forward to model")
    print("  aish forward list                         # List active forwards")
    print("  aish unforward <ci-name>                  # Return to default")
    print()
    print("Examples:")
    print("  aish forward apollo-ci claude            # Use Claude for Apollo")
    print("  aish forward rhetor-ci claude-opus       # Use Claude Opus")
    print("  aish forward sophia-ci claude --system 'You are wise'")
    print("  aish forward list                        # Show all forwards")
    print("  aish unforward apollo-ci                 # Back to default")
    print()
    print("Supported Models:")
    print("  claude         - Claude with --print mode")
    print("  claude-opus    - Claude 3 Opus")
    print("  claude-sonnet  - Claude 3 Sonnet")
    print("  claude-haiku   - Claude 3 Haiku")
    print("  <custom>       - Any custom model command")