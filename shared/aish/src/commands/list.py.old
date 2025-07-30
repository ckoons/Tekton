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