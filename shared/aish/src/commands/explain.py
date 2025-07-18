#!/usr/bin/env python3
"""
Explain command for Claude Code IDE.

Analyzes error messages and provides helpful suggestions.
"""

from src.introspect import TektonInspector


def explain_command(args: list, shell=None) -> str:
    """
    Execute explain command.
    
    Usage:
        aish explain "error message"
        aish explain AttributeError: 'AIShell' object has no attribute 'broadcast_message'
        
    Args:
        args: Command arguments (error message)
        shell: AIShell instance (optional)
        
    Returns:
        Explanation and suggestions for fixing the error
    """
    if not args or args[0] in ['-h', '--help']:
        return """Usage: aish explain <error message>

Analyze an error message and get suggestions for fixing it.

Arguments:
  error message    The Python error to analyze

Examples:
  aish explain "AttributeError: 'AIShell' object has no attribute 'broadcast_message'"
  aish explain "TypeError: send_message() takes 2 positional arguments but 3 were given"
  aish explain "NameError: name 'MessageHandler' is not defined"

Supported Errors:
  - AttributeError: Suggests correct method names
  - TypeError: Shows correct signatures
  - NameError: Suggests imports
  - ImportError: Shows correct module paths"""
    
    # Join all arguments as the error message
    error_message = ' '.join(args)
    
    # Create inspector
    inspector = TektonInspector()
    
    # Analyze the error
    analysis = inspector.explain_error(error_message)
    
    # Format output
    lines = []
    
    if analysis['error_type']:
        lines.append(f"Error Type: {analysis['error_type']}")
    
    if analysis['explanation']:
        lines.append(f"\n{analysis['explanation']}")
    
    if analysis['suggestions']:
        lines.append("\nSuggestions:")
        for suggestion in analysis['suggestions']:
            lines.append(f"  • {suggestion}")
    
    if analysis['examples']:
        lines.append("\nExample usage:")
        for example in analysis['examples']:
            lines.append(f"  {example}")
    
    # Add general help based on error type
    if 'AttributeError' in error_message and analysis['object_name']:
        lines.append(f"\nTo see all available methods:")
        lines.append(f"  aish introspect {analysis['object_name']}")
    
    if 'NameError' in error_message:
        lines.append("\nCommon fixes:")
        lines.append("  • Check if the class is imported")
        lines.append("  • Use 'aish context <file>' to see what's in scope")
    
    if 'TypeError' in error_message:
        lines.append("\nTo see the correct signature:")
        lines.append("  • Use 'aish introspect ClassName' to see method signatures")
    
    if not lines:
        lines.append("Unable to analyze this error. Try:")
        lines.append("  • aish introspect <ClassName> - to see available methods")
        lines.append("  • aish context <file> - to see what's in scope")
    
    return '\n'.join(lines)