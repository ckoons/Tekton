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


def resolve_model_alias(model: str) -> str:
    """Resolve generic model names to specific model identifiers.
    
    Handles common aliases like 'claude', 'gpt4', etc.
    """
    model_lower = model.lower()
    
    # Claude aliases - Updated for Claude 4+
    if model_lower in ['claude', 'claude-sonnet']:
        return 'claude-3-5-sonnet-latest'
    elif model_lower == 'claude-haiku':
        return 'claude-3-5-haiku-latest'
    elif model_lower in ['claude-opus', 'claude-best']:
        return 'claude-opus-4-1-20250805'
    elif 'claude-4' in model_lower:
        # Handle claude-4-sonnet, claude-4-opus, etc.
        return model  # Keep as-is, likely already specific
    
    # GPT aliases
    elif model_lower in ['gpt4', 'gpt-4', 'openai']:
        return 'gpt-4-turbo-preview'
    elif model_lower in ['gpt3', 'gpt-3', 'gpt-3.5']:
        return 'gpt-3.5-turbo'
    elif model_lower == 'gpt4o':
        return 'gpt-4o'
    
    # Local model aliases (size-based)
    elif model_lower in ['small', 'fast']:
        return 'gpt-oss:20b'
    elif model_lower in ['medium', 'balanced']:
        return 'gpt-oss:70b'
    elif model_lower in ['large', 'reasoning', 'deep']:
        return 'gpt-oss:120b'
    
    # Capability-based aliases
    elif model_lower == 'code':
        return 'codestral:22b'  # Assume available if user asks
    elif model_lower == 'math':
        return 'deepseek-r1:32b'  # Assume available if user asks
    
    # No alias found, return as-is
    return model


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
    
    # Resolve the model alias to specific model
    resolved_model = resolve_model_alias(model)
    
    # Set forward state in registry with resolved model
    if registry.set_forward_state(ci_name, resolved_model, args):
        print(f"✓ Forwarded {ci_name} to {model}")
        if resolved_model != model:
            print(f"  Resolved to: {resolved_model}")
        if args:
            print(f"  Additional args: {args}")
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
    
    # Resolve the model alias to specific model
    resolved_model = resolve_model_alias(model)
    
    # Set forward state in registry with resolved model
    if registry.set_forward_state(ci_name, resolved_model, args):
        print(f"✓ Forwarded {ci_name} to {model}")
        if resolved_model != model:
            print(f"  Resolved to: {resolved_model}")
        if args:
            print(f"  Additional args: {args}")
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
    print("Model Forwarding - Route CI to specific CI models")
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
    print("Supported Model Aliases:")
    print("  claude         - Latest Claude Sonnet")
    print("  claude-opus    - Claude Opus (best)")
    print("  claude-haiku   - Claude Haiku (fast)")
    print("  gpt4           - GPT-4 Turbo")
    print("  small/fast     - Small local model (20B)")
    print("  medium         - Medium local model (70B)")
    print("  large/deep     - Large reasoning model (120B)")
    print("  code           - Code-optimized model")
    print("  <custom>       - Any specific model name")