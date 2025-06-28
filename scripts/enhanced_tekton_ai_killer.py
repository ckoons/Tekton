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

from shared.ai.registry_client import AIRegistryClient
from shared.utils.logging_setup import setup_component_logging


class AIKiller:
    """Manages AI specialist termination."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.registry_client = AIRegistryClient()
        
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
        # Get AI info from registry
        registry = self.registry_client.list_platform_ais()
        
        if ai_id not in registry:
            self.logger.warning(f"AI {ai_id} not found in registry")
            return False
        
        ai_info = registry[ai_id]
        pid = ai_info.get('metadata', {}).get('pid')
        
        # Try to kill by PID if available
        if pid:
            try:
                process = psutil.Process(pid)
                process.terminate()
                process.wait(timeout=5)
                self.logger.info(f"Terminated AI {ai_id} (PID: {pid})")
            except psutil.NoSuchProcess:
                self.logger.warning(f"Process {pid} not found")
            except psutil.TimeoutExpired:
                try:
                    process.kill()
                    self.logger.info(f"Force killed AI {ai_id} (PID: {pid})")
                except Exception as e:
                    self.logger.error(f"Failed to kill process {pid}: {e}")
            except Exception as e:
                self.logger.error(f"Error killing AI {ai_id}: {e}")
        
        # Always deregister from registry
        self.registry_client.deregister_platform_ai(ai_id)
        return True
    
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