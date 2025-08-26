#!/usr/bin/env python3
"""
Aish Sunrise Command - Restore CI Context with Continuity

This command restores a CI's preserved context after sundown,
allowing them to continue their work with full awareness of what came before.
"""

import asyncio
import json
from typing import Optional
from pathlib import Path
import sys

# Add parent paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from aish.src.registry.ci_registry import get_registry
from aish.src.utils.output_formatter import format_output
from Apollo.apollo.core.sundown_sunrise import get_sundown_sunrise_manager

# Import landmarks with fallback
try:
    from landmarks import (
        cli_command,
        ci_agency_point,
        integration_point
    )
except ImportError:
    def cli_command(**kwargs):
        def decorator(func): return func
        return decorator
    def ci_agency_point(**kwargs):
        def decorator(func): return func
        return decorator
    def integration_point(**kwargs):
        def decorator(func): return func
        return decorator


@cli_command(
    name="sunrise",
    description="Restore CI context after sundown",
    category="context_management",
    examples=[
        "aish sunrise numa-ci",
        "aish sunrise ergon-ci --fresh",
        "aish sunrise --check"
    ]
)
@ci_agency_point(
    name="CI Sunrise Restoration",
    description="Restore CI's preserved context with continuity",
    preserves_agency=True
)
async def sunrise(ci_name: Optional[str] = None, fresh: bool = False, check: bool = False):
    """
    Restore CI context after sundown.
    
    Args:
        ci_name: Specific CI to restore (optional)
        fresh: Start fresh without restoring context
        check: Check which CIs have sundown states
    """
    registry = get_registry()
    manager = get_sundown_sunrise_manager()
    
    if check:
        # Check which CIs have sundown states
        from shared.env import TektonEnviron
        tekton_root = Path(TektonEnviron.get('TEKTON_ROOT', '.'))
        sundown_dir = tekton_root / 'Apollo' / 'sundown'
        
        if not sundown_dir.exists():
            return format_output({
                "status": "no_sundown_states",
                "message": "No CIs currently in sundown"
            })
        
        sundown_files = list(sundown_dir.glob("*.json"))
        ci_states = []
        
        for file in sundown_files:
            try:
                with open(file) as f:
                    state = json.load(f)
                    ci_states.append({
                        "ci": state.get("ci_name", file.stem),
                        "sundown_time": state.get("timestamp", "unknown"),
                        "reason": state.get("reason", "unknown"),
                        "has_summary": bool(state.get("summary"))
                    })
            except:
                continue
        
        return format_output({
            "command": "sunrise",
            "sundown_states": ci_states,
            "total": len(ci_states),
            "usage": "aish sunrise <ci-name> to restore"
        })
    
    elif ci_name:
        # Restore specific CI
        try:
            if fresh:
                # Start fresh without context
                registry.set_needs_fresh_start(ci_name, False)
                
                return format_output({
                    "action": "fresh_start",
                    "ci": ci_name,
                    "status": "success",
                    "message": f"CI '{ci_name}' will start fresh without previous context"
                })
            
            # Restore context
            result = await manager.restore_context(ci_name)
            
            if not result.get("success"):
                return format_output({
                    "action": "sunrise",
                    "ci": ci_name,
                    "status": "no_context",
                    "message": f"No sundown state found for '{ci_name}'",
                    "suggestion": "CI may not have been sundown or state may have expired"
                })
            
            # Clear fresh start flag
            registry.set_needs_fresh_start(ci_name, False)
            
            # Reinitialize token tracking
            from Rhetor.rhetor.core.token_manager import get_token_manager
            token_mgr = get_token_manager()
            forward_state = registry.get_forward_state(ci_name)
            
            if forward_state:
                model = forward_state.get('model', 'claude-3-sonnet')
                token_mgr.init_ci_tracking(ci_name, model)
            
            return format_output({
                "action": "sunrise",
                "ci": ci_name,
                "status": "success",
                "context_restored": {
                    "summary": result.get("summary", ""),
                    "key_topics": result.get("key_topics", []),
                    "next_steps": result.get("next_steps", [])
                },
                "message": f"Context restored for '{ci_name}' - ready to continue",
                "note": "CI can now continue with full awareness of previous work"
            })
            
        except Exception as e:
            return format_output({
                "error": f"Sunrise failed for '{ci_name}': {str(e)}",
                "suggestion": "Check CI status and sundown state"
            })
    
    else:
        # Show sunrise help
        return format_output({
            "command": "sunrise",
            "description": "Restore CI context after sundown",
            "usage": [
                "aish sunrise <ci-name>     # Restore CI with context",
                "aish sunrise <ci-name> --fresh  # Start fresh without context",
                "aish sunrise --check       # See which CIs have sundown states"
            ],
            "note": "Sunrise restores CI continuity and awareness"
        })


def main():
    """CLI entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Sunrise - Restore CI context")
    parser.add_argument("ci_name", nargs="?", help="CI to restore")
    parser.add_argument("--fresh", action="store_true", help="Start fresh without context")
    parser.add_argument("--check", action="store_true", help="Check sundown states")
    
    args = parser.parse_args()
    
    result = asyncio.run(sunrise(args.ci_name, args.fresh, args.check))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()