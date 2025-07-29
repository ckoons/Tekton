"""
List command handler for aish.
Handles the unified CI listing with various filters and output formats.
"""

import sys
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
        registry.refresh()  # Get latest info
        print(registry.format_text_output())
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
        elif filter_type is None and arg in ['terminal', 'greek', 'project', 'forward', 'local', 'remote']:
            # Direct filter without 'type' keyword
            filter_type = arg
        
        i += 1
    
    # Get registry and refresh
    registry = get_registry()
    registry.refresh()
    
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
        print(registry.format_text_output(cis))


def handle_context_list(args):
    """
    Handle context listing commands:
    - aish list context            # Show context state summary for all CIs
    - aish list context <ci-name>  # Show full context details for specific CI
    """
    registry = get_registry()
    registry.refresh()
    
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
    print(f"{'CI Name':<15} {'Next':<6} {'Staged':<8} {'Last Output (first 30 chars)':<35}")
    print("-" * 80)
    
    # Get all CIs and their context states
    all_cis = registry.get_all()
    all_context_states = registry.get_all_context_states()
    
    for ci in sorted(all_cis, key=lambda x: x['name']):
        ci_name = ci['name']
        context_state = all_context_states.get(ci_name, {})
        
        # Check for next and staged prompts
        has_next = "Yes" if context_state.get('next_context_prompt') else "No"
        has_staged = "Yes" if context_state.get('staged_context_prompt') else "No"
        
        # Get first 30 chars of last output
        last_output = context_state.get('last_output', '')
        if last_output:
            # Clean up whitespace and truncate
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
    
    # Show last output
    last_output = context_state.get('last_output')
    print("\n[Last Output]")
    if last_output:
        print("Status: Captured")
        print("-" * 60)
        print(last_output)
        print("-" * 60)
    else:
        print("Status: No output captured")