#!/usr/bin/env python3
"""
Context command for Claude Code IDE.

Analyzes a Python file to show what classes and methods are available in scope.
"""

import os
from src.introspect import TektonInspector


def context_command(args: list, shell=None) -> str:
    """
    Execute context command.
    
    Usage:
        aish context <file.py>
        aish context            # Uses current file if detectable
        
    Args:
        args: Command arguments  
        shell: AIShell instance (optional)
        
    Returns:
        Available classes and methods in the file's scope
    """
    if args and args[0] in ['-h', '--help']:
        return """Usage: aish context [file.py]

Analyze a Python file to see what classes and methods are available in scope.

Arguments:
  file.py       Python file to analyze (optional, tries to detect current)

Examples:
  aish context my_script.py
  aish context ./shared/aish/src/core/shell.py
  aish context    # Analyze current file if detectable

Shows:
  - Imported classes and their methods
  - Local classes defined in the file
  - Local functions defined in the file
  - Import statements and aliases"""
    
    # Determine file to analyze
    if args and args[0] != '--help':
        file_path = args[0]
    else:
        # Try to detect current file (could be enhanced with editor integration)
        file_path = os.environ.get('CLAUDE_CURRENT_FILE')
        if not file_path:
            return "No file specified. Usage: aish context <file.py>"
    
    # Expand path
    file_path = os.path.expanduser(file_path)
    if not os.path.isabs(file_path):
        file_path = os.path.abspath(file_path)
    
    if not os.path.exists(file_path):
        return f"File not found: {file_path}"
    
    if not file_path.endswith('.py'):
        return f"Not a Python file: {file_path}"
    
    # Analyze the file
    inspector = TektonInspector()
    context = inspector.get_context_info(file_path)
    
    if context.get('error'):
        return f"Error: {context['message']}"
    
    # Format output
    lines = [f"Context for: {context['file']}\n"]
    
    if context['imports']:
        lines.append("Imported:")
        for name, info in sorted(context['imports'].items()):
            if isinstance(info, dict) and info.get('methods'):
                lines.append(f"  {name} ({info.get('module', 'unknown')})")
                # Show first few methods
                methods = sorted(info['methods'].keys())[:5]
                for method in methods:
                    lines.append(f"    - {method}()")
                if len(info['methods']) > 5:
                    lines.append(f"    ... and {len(info['methods']) - 5} more methods")
            else:
                lines.append(f"  {name}")
    
    if context['local_classes']:
        lines.append("\nLocal Classes:")
        for name, info in sorted(context['local_classes'].items()):
            lines.append(f"  {name} (line {info['line']})")
            for method in info['methods'][:3]:
                lines.append(f"    - {method}()")
            if len(info['methods']) > 3:
                lines.append(f"    ... and {len(info['methods']) - 3} more methods")
    
    if context['local_functions']:
        lines.append("\nLocal Functions:")
        for name, info in sorted(context['local_functions'].items()):
            args_str = ', '.join(info['args'])
            lines.append(f"  {name}({args_str}) - line {info['line']}")
    
    return '\n'.join(lines)