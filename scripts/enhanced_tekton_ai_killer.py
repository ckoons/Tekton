#!/usr/bin/env python3
"""
Enhanced Tekton AI Killer

Terminates AI specialists for Tekton components.
"""
import os
import sys
import argparse
import psutil
from typing import List, Dict, Optional

# Add Tekton root to path
script_path = os.path.realpath(__file__)
tekton_root = os.path.dirname(os.path.dirname(script_path))
sys.path.insert(0, tekton_root)

# Registry client removed - using process scanning
from shared.utils.logging_setup import setup_component_logging


class AIKiller:
    """Manages AI specialist termination."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        # Registry removed - will scan processes directly
        
        # Setup logging
        log_level = 'DEBUG' if verbose else 'INFO'
        self.logger = setup_component_logging('ai_killer', log_level)
        
    def kill_ai_by_id(self, ai_id: str) -> bool:
        """
        Kill an AI specialist by ID.
        
        Args:
            ai_id: AI identifier
            
        Returns:
            True if killed successfully
        """
        # Find process by scanning for the AI id with generic_specialist
        killed = False
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                # Look for generic_specialist with this specific AI id
                if cmdline and 'generic_specialist' in ' '.join(cmdline) and f'--ai-id {ai_id}' in ' '.join(cmdline):
                    proc.terminate()
                    proc.wait(timeout=5)
                    self.logger.info(f"Terminated AI {ai_id} (PID: {proc.pid})")
                    killed = True
            except psutil.NoSuchProcess:
                pass  # Process already gone
            except psutil.TimeoutExpired:
                try:
                    proc.kill()
                    self.logger.info(f"Force killed AI {ai_id} (PID: {proc.pid})")
                    killed = True
                except Exception as e:
                    self.logger.error(f"Failed to kill process {proc.pid}: {e}")
            except Exception as e:
                self.logger.error(f"Error checking process: {e}")
        
        return killed
    
    def kill_ai_by_component(self, component: str) -> bool:
        """
        Kill AI specialist for a component.
        
        Args:
            component: Component name
            
        Returns:
            True if killed successfully
        """
        ai_id = f"{component.lower()}-ai"
        return self.kill_ai_by_id(ai_id)
    
    def kill_all_ais(self) -> int:
        """
        Kill all registered AI specialists.
        
        Returns:
            Number of AIs killed
        """
        registry = self.registry_client.list_platform_ais()
        killed_count = 0
        
        for ai_id in list(registry.keys()):
            if self.kill_ai_by_id(ai_id):
                killed_count += 1
        
        return killed_count
    
    def kill_multiple(self, targets: List[str]) -> int:
        """
        Kill multiple AI specialists.
        
        Args:
            targets: List of AI IDs or component names
            
        Returns:
            Number of AIs killed
        """
        killed_count = 0
        
        for target in targets:
            if target.lower() == 'all':
                return self.kill_all_ais()
            
            # Try as AI ID first
            if self.kill_ai_by_id(target):
                killed_count += 1
            # Try as component name
            elif self.kill_ai_by_component(target):
                killed_count += 1
            else:
                self.logger.warning(f"Could not find AI for: {target}")
        
        return killed_count


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Terminate AI specialists for Tekton components'
    )
    parser.add_argument(
        'targets',
        nargs='+',
        help='AI IDs or component names to kill (or "all")'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '-f', '--force',
        action='store_true',
        help='Force kill without confirmation'
    )
    
    args = parser.parse_args()
    
    killer = AIKiller(verbose=args.verbose)
    
    # Show what will be killed
    if not args.force and 'all' not in [t.lower() for t in args.targets]:
        registry = killer.registry_client.list_platform_ais()
        to_kill = []
        
        for target in args.targets:
            ai_id = target if target in registry else f"{target.lower()}-ai"
            if ai_id in registry:
                to_kill.append(ai_id)
        
        if to_kill:
            print("Will terminate the following AIs:")
            for ai_id in to_kill:
                ai_info = registry[ai_id]
                print(f"  - {ai_id} ({ai_info.get('component', 'unknown')})")
            
            response = input("\nContinue? [y/N]: ")
            if response.lower() != 'y':
                print("Aborted.")
                sys.exit(0)
    
    # Kill AIs
    killed = killer.kill_multiple(args.targets)
    print(f"Terminated {killed} AI specialist(s)")


if __name__ == '__main__':
    main()