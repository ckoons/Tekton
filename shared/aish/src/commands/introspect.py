#!/usr/bin/env python3
"""
Introspect command for Claude Code IDE.

Provides real-time class and method information to prevent guessing.
"""

import sys
from typing import Optional
from src.introspect import TektonInspector, IntrospectionCache

# Import landmarks with fallback
try:
    from landmarks import api_contract
except ImportError:
    def api_contract(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator


@api_contract(
    title="aish introspect command",
    description="Primary CI interface for class/method discovery",
    endpoint="aish introspect <class>",
    method="CLI",
    request_schema={"class_name": "string", "options": ["--json", "--no-cache"]},
    response_schema={"class_info": "formatted string or JSON"},
    performance_requirements="<200ms first call, <5ms cached"
)
def introspect_command(args: list, shell=None) -> str:
    """
    Execute introspect command.
    
    Usage:
        aish introspect ClassName
        aish introspect module.ClassName
        aish introspect ClassName --json
        aish introspect ClassName | grep method_name
    
    Args:
        args: Command arguments
        shell: AIShell instance (optional)
        
    Returns:
        Formatted class information
    """
    if not args or args[0] in ['-h', '--help']:
        return """Usage: aish introspect <ClassName> [options]

Inspect a Python class to see all available methods and signatures.
Built specifically for Companion Intelligences (CIs) to code with confidence!

Arguments:
  ClassName     Name of the class to inspect (e.g., AIShell, MessageHandler)
                Can include module path (e.g., core.shell.AIShell)

Options:
  --json        Output in JSON format
  --no-cache    Skip cache and force fresh introspection
  --help        Show this help message

Examples:
  aish introspect AIShell
  aish introspect core.message_handler.MessageHandler
  aish introspect TektonEnviron --json
  aish introspect AIShell | grep send

Common Classes:
  AIShell       - Main shell interface
  MessageHandler - Message routing and forwarding
  TektonEnviron - Environment configuration
  AIManager     - CI component management

CI Note: Use this liberally! Better to check than guess. If you notice
patterns where you frequently need to check the same things, let us know
so we can make the tool even better for you."""
    
    # Parse arguments
    class_name = args[0]
    use_json = '--json' in args
    no_cache = '--no-cache' in args
    
    # Create inspector and cache
    inspector = TektonInspector()
    cache = IntrospectionCache() if not no_cache else None
    
    # Check cache first
    if cache:
        cached = cache.get(class_name)
        if cached:
            return inspector.format_class_info(cached, 'json' if use_json else 'human')
    
    # Perform introspection
    info = inspector.get_class_info(class_name)
    
    # Cache successful results
    if cache and not info.get('error'):
        cache.set(class_name, info, info.get('file'))
    
    # Format and return
    return inspector.format_class_info(info, 'json' if use_json else 'human')