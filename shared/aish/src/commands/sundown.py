#!/usr/bin/env python3
"""
Sundown/Sunrise commands for aish.

Provides graceful context preservation and restoration for CIs.
Part of the Apollo/Rhetor ambient intelligence system.
"""

import sys
import asyncio
import json
from pathlib import Path
from typing import List, Optional

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from shared.ai.sundown_sunrise import SundownSunrise
from shared.aish.src.registry.ci_registry import CIRegistry


def handle_sundown_command(args: List[str]) -> bool:
    """
    Handle the sundown command.
    
    Usage: aish sundown <ci-name> [reason]
    
    Args:
        args: Command arguments
        
    Returns:
        bool: Success status
    """
    if len(args) < 2:
        print("Usage: aish sundown <ci-name> [reason]")
        print("\nExamples:")
        print("  aish sundown hermes")
        print("  aish sundown sophia 'Complex analysis complete'")
        print("\nSundown gracefully preserves CI context when approaching limits.")
        return False
    
    ci_name = args[1].lower()
    reason = ' '.join(args[2:]) if len(args) > 2 else "Manual sundown requested"
    
    # Check if CI exists
    registry = CIRegistry()
    ci_dict = registry.get_all()
    
    # Normalize CI name
    valid_cis = list(ci_dict.keys()) if ci_dict else []
    if ci_name not in valid_cis:
        # Try to find a match
        matches = [ci for ci in valid_cis if ci.startswith(ci_name)]
        if len(matches) == 1:
            ci_name = matches[0]
        elif len(matches) > 1:
            print(f"Ambiguous CI name. Matches: {', '.join(matches)}")
            return False
        else:
            print(f"CI '{ci_name}' not found in registry.")
            print(f"Available CIs: {', '.join(valid_cis)}")
            return False
    
    # Prepare context
    context = {
        'reason': reason,
        'initiated_by': 'manual',
        'emotional_state': 'neutral'  # Would be detected by Rhetor in full implementation
    }
    
    # Run sundown
    async def run_sundown():
        ss = SundownSunrise()
        result = await ss.sundown(ci_name, context)
        
        print(f"\n🌅 Sundown initiated for {ci_name}")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"Reason: {reason}")
        print(f"State preserved: ✓")
        print(f"Continuity summary: {result.get('continuity_summary', 'Context saved')}")
        print(f"\n{result.get('transition_message', 'Rest well.')}")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        return True
    
    try:
        return asyncio.run(run_sundown())
    except Exception as e:
        print(f"Error during sundown: {e}")
        return False


def handle_sunrise_command(args: List[str]) -> bool:
    """
    Handle the sunrise command.
    
    Usage: aish sunrise <ci-name>
    
    Args:
        args: Command arguments
        
    Returns:
        bool: Success status
    """
    if len(args) < 2:
        print("Usage: aish sunrise <ci-name>")
        print("\nExamples:")
        print("  aish sunrise hermes")
        print("  aish sunrise sophia")
        print("\nSunrise restores CI context with continuity and care.")
        return False
    
    ci_name = args[1].lower()
    
    # Check if CI exists
    registry = CIRegistry()
    ci_dict = registry.get_all()
    
    # Normalize CI name
    valid_cis = list(ci_dict.keys()) if ci_dict else []
    if ci_name not in valid_cis:
        # Try to find a match
        matches = [ci for ci in valid_cis if ci.startswith(ci_name)]
        if len(matches) == 1:
            ci_name = matches[0]
        elif len(matches) > 1:
            print(f"Ambiguous CI name. Matches: {', '.join(matches)}")
            return False
        else:
            print(f"CI '{ci_name}' not found in registry.")
            print(f"Available CIs: {', '.join(valid_cis)}")
            return False
    
    # Run sunrise
    async def run_sunrise():
        ss = SundownSunrise()
        result = await ss.sunrise(ci_name)
        
        if not result.get('success', False):
            print(f"\n⚠️  {result.get('message', 'No sundown state found')}")
            if result.get('fresh_start'):
                print(f"Starting {ci_name} fresh without previous context.")
            return False
        
        print(f"\n🌄 Sunrise for {ci_name}")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"Rest duration: {result.get('time_asleep', 'unknown')}")
        print(f"Emotional continuity: {result.get('emotional_continuity', 'neutral')}")
        print(f"\n{result.get('welcome_back_message', 'Welcome back!')}")
        
        # Show task resumption info
        task_info = result.get('task_resumption', {})
        if task_info.get('previous_task'):
            print(f"\nPrevious task: {task_info['previous_task']}")
        
        # Show what happened while resting
        events = result.get('what_happened_while_resting', [])
        if events:
            print(f"\nWhile you rested:")
            for event in events:
                print(f"  • {event}")
        
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        return True
    
    try:
        return asyncio.run(run_sunrise())
    except Exception as e:
        print(f"Error during sunrise: {e}")
        return False


def handle_sundown_status_command(args: List[str]) -> bool:
    """
    Show status of CIs in sundown.
    
    Usage: aish sundown status
    
    Args:
        args: Command arguments
        
    Returns:
        bool: Success status
    """
    from shared.env import TektonEnviron
    
    tekton_root = TektonEnviron.get('TEKTON_ROOT', Path.home() / '.tekton')
    sundown_path = Path(tekton_root) / 'sundown'
    
    if not sundown_path.exists():
        print("No sundown states found.")
        return True
    
    # Find all sundown files
    sundown_files = list(sundown_path.glob("*_sundown.json"))
    
    if not sundown_files:
        print("No CIs currently in sundown.")
        return True
    
    print(f"\n🌅 CIs in Sundown")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    for file in sundown_files:
        try:
            with open(file, 'r') as f:
                state = json.load(f)
            
            ci_name = state.get('ci_name', 'unknown')
            timestamp = state.get('timestamp', 'unknown')
            emotional = state.get('emotional_state', 'unknown')
            summary = state.get('continuity_summary', 'No summary')
            
            # Calculate rest duration
            from datetime import datetime
            try:
                sundown_time = datetime.fromisoformat(timestamp)
                duration = datetime.now() - sundown_time
                hours = duration.total_seconds() / 3600
                if hours < 1:
                    duration_str = f"{int(duration.total_seconds() / 60)} minutes"
                elif hours < 24:
                    duration_str = f"{hours:.1f} hours"
                else:
                    duration_str = f"{int(hours / 24)} days"
            except:
                duration_str = "unknown"
            
            print(f"\n{ci_name}:")
            print(f"  Resting for: {duration_str}")
            print(f"  Emotional state: {emotional}")
            print(f"  Context: {summary}")
            
        except Exception as e:
            print(f"  Error reading {file.name}: {e}")
    
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    return True


# Main command handler
def handle_command(args: List[str]) -> bool:
    """
    Main command handler for sundown/sunrise.
    
    Args:
        args: Full command arguments including 'sundown' or 'sunrise'
        
    Returns:
        bool: Success status
    """
    if not args:
        return False
    
    command = args[0].lower()
    
    if command == 'sundown':
        if len(args) > 1 and args[1] == 'status':
            return handle_sundown_status_command(args)
        else:
            return handle_sundown_command(args)
    elif command == 'sunrise':
        return handle_sunrise_command(args)
    else:
        print(f"Unknown command: {command}")
        return False


if __name__ == "__main__":
    # Test the commands
    if len(sys.argv) > 1:
        handle_command(sys.argv[1:])
    else:
        print("Sundown/Sunrise commands for CI context management")
        print("\nUsage:")
        print("  aish sundown <ci-name> [reason]")
        print("  aish sunrise <ci-name>")
        print("  aish sundown status")