#!/usr/bin/env python3
"""
Enhanced Tekton CI Killer

Terminates CI specialists for Tekton components.
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

# Check if environment is loaded
from shared.env import TektonEnviron
if not TektonEnviron.is_loaded():
    # We're running as a subprocess with environment passed via env=
    # The environment is already correct, just not "loaded" in Python's memory
    # Don't exit - just continue
    pass
else:
    # Use frozen environment if loaded
    os.environ = TektonEnviron.all()

# Registry client removed - using process scanning
from shared.utils.logging_setup import setup_component_logging


class CIKiller:
    """Manages CI specialist termination."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        # Registry removed - will scan processes directly
        
        # Setup logging
        log_level = 'DEBUG' if verbose else 'INFO'
        self.logger = setup_component_logging('ai_killer', log_level)
        
        # Get environment-specific CI port range - NO DEFAULTS!
        ai_port_base = TektonEnviron.get('TEKTON_AI_PORT_BASE')
        if not ai_port_base:
            self.logger.error(f"TEKTON_AI_PORT_BASE not set in .env.local at {TektonEnviron.get('TEKTON_ROOT', '.')}")
            self.logger.error("Each Tekton instance has unique port ranges. Cannot proceed without proper configuration.")
            raise ValueError("TEKTON_AI_PORT_BASE must be set in .env.local")
        self.ai_port_base = int(ai_port_base)
        self.logger.info(f"CI killer initialized for port base: {self.ai_port_base}")
        
    def kill_ai_by_id(self, ai_id: str) -> bool:
        """
        Kill an CI specialist by ID.
        
        Args:
            ai_id: CI identifier
            
        Returns:
            True if killed successfully
        """
        # Find process by scanning for the CI id with generic_specialist
        killed = False
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                cmdline_str = ' '.join(cmdline) if cmdline else ''
                
                # Look for generic_specialist with this specific CI/AI id (both naming conventions)
                if 'generic_specialist' in cmdline_str and (f'--ci-id {ai_id}' in cmdline_str or f'--ai-id {ai_id}' in cmdline_str):
                    # Extract port from command line to check environment
                    port = self._extract_port_from_cmdline(cmdline)
                    if port and self._is_port_in_environment(port):
                        proc.terminate()
                        proc.wait(timeout=5)
                        self.logger.info(f"Terminated CI {ai_id} on port {port} (PID: {proc.pid})")
                        killed = True
                    else:
                        self.logger.debug(f"Skipping CI {ai_id} on port {port} - not in this environment (base: {self.ai_port_base})")
            except psutil.NoSuchProcess:
                pass  # Process already gone
            except psutil.TimeoutExpired:
                try:
                    proc.kill()
                    self.logger.info(f"Force killed CI {ai_id} (PID: {proc.pid})")
                    killed = True
                except Exception as e:
                    self.logger.error(f"Failed to kill process {proc.pid}: {e}")
            except Exception as e:
                self.logger.error(f"Error checking process: {e}")
        
        return killed
    
    def _extract_port_from_cmdline(self, cmdline: List[str]) -> Optional[int]:
        """Extract port number from command line arguments."""
        try:
            for i, arg in enumerate(cmdline):
                if arg == '--port' and i + 1 < len(cmdline):
                    return int(cmdline[i + 1])
        except (ValueError, IndexError):
            pass
        return None
    
    def _is_port_in_environment(self, port: int) -> bool:
        """Check if port belongs to this environment's CI port range."""
        # CI ports are typically TEKTON_AI_PORT_BASE + offset (0-99 range)
        # Main Tekton: 44000-44099, Coder-A: 44000-44099, Coder-C: 42000-42099
        return self.ai_port_base <= port < self.ai_port_base + 100
    
    def kill_ai_by_component(self, component: str) -> bool:
        """
        Kill CI specialist for a component.
        
        Args:
            component: Component name
            
        Returns:
            True if killed successfully
        """
        ai_id = f"{component.lower()}-ci"
        return self.kill_ai_by_id(ai_id)
    
    def kill_all_ais(self) -> int:
        """
        Kill all CI specialists in this environment.
        
        Returns:
            Number of CIs killed
        """
        killed_count = 0
        
        # Find all generic_specialist processes and check if they're in our environment
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                cmdline_str = ' '.join(cmdline) if cmdline else ''
                
                if 'generic_specialist' in cmdline_str and ('--ci-id' in cmdline_str or '--ai-id' in cmdline_str):
                    # Extract port and check environment
                    port = self._extract_port_from_cmdline(cmdline)
                    if port and self._is_port_in_environment(port):
                        proc.terminate()
                        proc.wait(timeout=5)
                        self.logger.info(f"Terminated CI on port {port} (PID: {proc.pid})")
                        killed_count += 1
                        
            except psutil.NoSuchProcess:
                pass
            except psutil.TimeoutExpired:
                try:
                    proc.kill()
                    self.logger.info(f"Force killed CI (PID: {proc.pid})")
                    killed_count += 1
                except Exception as e:
                    self.logger.error(f"Failed to kill process {proc.pid}: {e}")
            except Exception as e:
                self.logger.error(f"Error checking process: {e}")
        
        return killed_count
    
    def kill_multiple(self, targets: List[str]) -> int:
        """
        Kill multiple CI specialists.
        
        Args:
            targets: List of CI IDs or component names
            
        Returns:
            Number of CIs killed
        """
        killed_count = 0
        
        for target in targets:
            if target.lower() == 'all':
                return self.kill_all_ais()
            
            # Try as CI ID first
            if self.kill_ai_by_id(target):
                killed_count += 1
            # Try as component name
            elif self.kill_ai_by_component(target):
                killed_count += 1
            else:
                self.logger.warning(f"Could not find CI for: {target}")
        
        return killed_count


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Terminate CI specialists for Tekton components'
    )
    parser.add_argument(
        'targets',
        nargs='+',
        help='CI IDs or component names to kill (or "all")'
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
    
    killer = CIKiller(verbose=args.verbose)
    
    # Show what will be killed
    if not args.force and 'all' not in [t.lower() for t in args.targets]:
        print(f"Will attempt to terminate CIs for: {', '.join(args.targets)}")
        print(f"Environment CI port base: {killer.ai_port_base}")
        
        response = input("\nContinue? [y/N]: ")
        if response.lower() != 'y':
            print("Aborted.")
            sys.exit(0)
    
    # Kill CIs
    killed = killer.kill_multiple(args.targets)
    print(f"Terminated {killed} CI specialist(s)")


if __name__ == '__main__':
    main()
