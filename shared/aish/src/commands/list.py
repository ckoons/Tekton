"""
List command handler for aish.
Handles the unified CI listing with various filters and output formats.
"""

import sys
import operator
from pathlib import Path

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from registry.ci_registry import get_registry


def handle_list_command(args):
    """
    Handle list command variations:
    - aish list                    # All CIs in text format
    - aish list commands           # Existing command help (handled elsewhere)
    - aish list context            # Show context state for all CIs
    - aish list context <ci-name>  # Show full context for specific CI
    - aish list type terminal      # Filter by type
    - aish list json              # JSON output
    - aish list json terminal     # JSON output with filter
    """
    if not args:
        # Default: show all CIs in text format
        registry = get_registry()
        print(registry.format_list())
        return
    
    # Handle context command first
    if args[0].lower() == 'context':
        handle_context_list(args[1:] if len(args) > 1 else [])
        return
    
    # Parse arguments
    output_json = False
    filter_type = None
    
    i = 0
    while i < len(args):
        arg = args[i].lower()
        
        if arg == 'json':
            output_json = True
        elif arg == 'type' and i + 1 < len(args):
            # Next argument is the type filter
            i += 1
            filter_type = args[i].lower()
        elif filter_type is None and arg in ['terminal', 'greek', 'project', 'tool', 'wrapped_ci', 'forward', 'local', 'remote']:
            # Direct filter without 'type' keyword
            filter_type = arg
        
        i += 1
    
    # Get registry and refresh
    registry = get_registry()
    
    # Get CIs based on filter
    if filter_type:
        cis = registry.get_by_type(filter_type)
    else:
        cis = registry.get_all()
    
    # Output in requested format
    if output_json:
        import json
        print(json.dumps(cis, indent=2))
    else:
        print(registry.format_list())


def handle_context_list(args):
    """
    Handle context listing commands:
    - aish list context            # Show context state summary for all CIs
    - aish list context <ci-name>  # Show full context details for specific CI
    """
    registry = get_registry()
    
    if not args:
        # Show summary for all CIs
        show_context_summary(registry)
    else:
        # Show detailed context for specific CI
        ci_name = args[0]
        show_context_details(registry, ci_name)


def show_context_summary(registry):
    """Show context state summary for all CIs."""
    print("CI Context States (Apollo-Rhetor Coordination)")
    print("=" * 80)
    print(f"{'CI Name':<15} {'Next':<6} {'Staged':<8} {'Last User Message (first 30 chars)':<35}")
    print("-" * 80)
    
    # Get all CIs and their context states
    all_cis = registry.get_all()
    all_context_states = registry.get_all_context_states()
    
    # Sort CIs by name
    ci_list = list(all_cis.values())
    ci_list.sort(key=operator.itemgetter('name'))
    
    for ci in ci_list:
        ci_name = ci['name']
        context_state = all_context_states.get(ci_name, {})
        
        # Check for next and staged prompts
        has_next = "Yes" if context_state.get('next_context_prompt') else "No"
        has_staged = "Yes" if context_state.get('staged_context_prompt') else "No"
        
        # Get first 30 chars of last output or user message
        last_output = context_state.get('last_output', '')
        if last_output:
            # Check if it's the new exchange format (dict) or old format (string)
            if isinstance(last_output, dict):
                # New format: show user message first 30 chars
                user_msg = last_output.get('user_message', '')
                output_preview = user_msg.replace('\n', ' ').strip()[:30]
                if len(user_msg) > 30:
                    output_preview += "..."
            else:
                # Old format: show output first 30 chars
                output_preview = last_output.replace('\n', ' ').strip()[:30]
                if len(last_output) > 30:
                    output_preview += "..."
        else:
            output_preview = "(no output)"
        
        print(f"{ci_name:<15} {has_next:<6} {has_staged:<8} {output_preview:<35}")
    
    print("\nUse 'aish list context <ci-name>' to see full details for a specific CI")


def show_context_details(registry, ci_name):
    """Show detailed context information for a specific CI."""
    ci = registry.get_by_name(ci_name)
    if not ci:
        print(f"Error: CI '{ci_name}' not found")
        return
    
    context_state = registry.get_ci_context_state(ci_name)
    if not context_state:
        print(f"No context state found for '{ci_name}'")
        return
    
    print(f"Context Details for: {ci_name}")
    print("=" * 80)
    
    # Show next context prompt
    next_prompt = context_state.get('next_context_prompt')
    print("\n[Next Context Prompt]")
    if next_prompt:
        print("Status: Ready for injection")
        for i, prompt in enumerate(next_prompt):
            print(f"\n  Message {i+1}:")
            print(f"    Role: {prompt.get('role', 'unknown')}")
            print(f"    Content: {prompt.get('content', '')}")
    else:
        print("Status: None")
    
    # Show staged context prompt
    staged_prompt = context_state.get('staged_context_prompt')
    print("\n[Staged Context Prompt]")
    if staged_prompt:
        print("Status: Staged by Apollo (awaiting Rhetor decision)")
        for i, prompt in enumerate(staged_prompt):
            print(f"\n  Message {i+1}:")
            print(f"    Role: {prompt.get('role', 'unknown')}")
            print(f"    Content: {prompt.get('content', '')}")
    else:
        print("Status: None")
    
    # Show last exchange (user message + CI response)
    last_output = context_state.get('last_output')
    print("\n[Last Exchange]")
    if last_output:
        if isinstance(last_output, dict):
            # New format: show full exchange
            print("Status: Captured")
            print("\nUser Message:")
            print("-" * 60)
            print(last_output.get('user_message', '(no message)'))
            print("-" * 60)
            
            ai_response = last_output.get('ai_response', {})
            print("\nAI Response:")
            print("-" * 60)
            print(ai_response.get('content', '(no content)'))
            print("-" * 60)
            
            # Show metadata
            print(f"\nModel: {ai_response.get('model', 'unknown')}")
            if 'usage' in ai_response:
                print(f"Tokens: {ai_response['usage'].get('total_tokens', 'unknown')}")
            if 'latency' in ai_response:
                print(f"Latency: {ai_response['latency']:.2f}s")
            if 'timestamp' in last_output:
                from datetime import datetime
                timestamp = datetime.fromtimestamp(last_output['timestamp'])
                print(f"Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            # Old format: just show the output
            print("Status: Captured (legacy format)")
            print("-" * 60)
            print(last_output)
            print("-" * 60)
    else:
        print("Status: No output captured")