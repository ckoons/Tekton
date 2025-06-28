#!/usr/bin/env python3
"""
Enhanced Tekton AI Launcher

Manages AI specialists for Tekton components. Works with enhanced_tekton_launcher.py
to provide AI lifecycle management.
"""
import os
import sys
import asyncio
import subprocess
import argparse
import json
from typing import List, Dict, Optional, Set, Any
from pathlib import Path

# Add Tekton root to path
script_path = os.path.realpath(__file__)
tekton_root = os.path.dirname(os.path.dirname(script_path))
sys.path.insert(0, tekton_root)

from shared.ai.registry_client import AIRegistryClient
from shared.utils.env_config import get_component_config
from shared.utils.logging_setup import setup_component_logging

# Components that should NOT have AI specialists
AI_EXCLUDED_COMPONENTS = {'ui_dev_tools', 'ui-dev-tools', 'ui_devtools'}


class AILauncher:
    """Manages AI specialist launching."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.config = get_component_config()
        self.registry_client = AIRegistryClient()
        self.launched_ais: Dict[str, subprocess.Popen] = {}
        
        # Setup logging
        log_level = 'DEBUG' if verbose else 'INFO'
        self.logger = setup_component_logging('ai_launcher', log_level)
    
    def check_component_config(self, component: str) -> bool:
        """
        Check if a component is properly configured.
        
        Args:
            component: Component name
            
        Returns:
            True if component has required configuration
        """
        try:
            comp_config = getattr(self.config, component.lower().replace('-', '_'))
            has_port = hasattr(comp_config, 'port')
            if not has_port:
                self.logger.debug(f"Component {component} missing port configuration")
            return has_port
        except AttributeError:
            self.logger.debug(f"Component {component} not found in configuration")
            return False
    
    def get_ai_config(self, component: str) -> Optional[Dict[str, Any]]:
        """
        Get AI configuration for a component dynamically.
        
        Args:
            component: Component name
            
        Returns:
            AI configuration dict or None if component doesn't support AI
        """
        # Normalize component name
        comp_lower = component.lower()
        
        # Check if excluded
        if comp_lower in AI_EXCLUDED_COMPONENTS:
            self.logger.debug(f"Component {component} is excluded from AI support")
            return None
        
        # Check if component exists in config
        try:
            comp_config = getattr(self.config, comp_lower.replace('-', '_'))
        except AttributeError:
            self.logger.debug(f"Component {component} not found in configuration")
            return None
        
        # Generate AI configuration
        component_title = component.replace('_', ' ').replace('-', ' ').title()
        
        # Use the generic AI specialist for all components
        module_path = 'shared.ai.generic_specialist'
        
        self.logger.debug(f"Generated AI config for {component}: module={module_path}")
        
        return {
            'ai_id': f'{comp_lower}-ai',
            'description': f'AI specialist for {component_title}',
            'launch_module': module_path,
            'component_config': comp_config
        }
        
    async def launch_ai(self, component: str) -> bool:
        """
        Launch AI specialist for a component.
        
        Args:
            component: Component name
            
        Returns:
            True if launched successfully
        """
        # Get dynamic AI configuration
        ai_config = self.get_ai_config(component)
        if not ai_config:
            self.logger.error(f"Component '{component}' does not support AI specialists")
            return False
            
        ai_id = ai_config['ai_id']
        
        # Check if already running
        existing = self.registry_client.get_ai_socket(ai_id)
        if existing:
            self.logger.info(f"AI {ai_id} already running on port {existing[1]}")
            return True
        
        # Check if component exists and is configured
        if not self.check_component_config(component):
            self.logger.info(f"Component {component} not properly configured")
            return False
        
        # Allocate port for AI
        ai_port = self.registry_client.allocate_port()
        if not ai_port:
            self.logger.error(f"Could not allocate port for {ai_id}")
            return False
        
        # Launch AI process
        try:
            cmd = [
                sys.executable, '-m', ai_config['launch_module'],
                '--port', str(ai_port),
                '--component', component,
                '--ai-id', ai_id
            ]
            
            if self.verbose:
                cmd.append('--verbose')
            
            self.logger.info(f"Launching {ai_id} on port {ai_port}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**os.environ, 'PYTHONPATH': tekton_root}
            )
            
            self.launched_ais[ai_id] = process
            
            # Register with registry
            self.registry_client.register_platform_ai(
                ai_id=ai_id,
                port=ai_port,
                component=component,
                metadata={
                    'description': ai_config['description'],
                    'pid': process.pid
                }
            )
            
            # Wait for AI to be ready (skip for Hermes - it receives health checks, doesn't perform them)
            if component.lower() == 'hermes':
                self.logger.info(f"Successfully launched {ai_id} (skipped readiness check for Hermes)")
                return True
            elif await self.registry_client.wait_for_ai(ai_id, timeout=30):
                self.logger.info(f"Successfully launched {ai_id}")
                return True
            else:
                self.logger.error(f"AI {ai_id} failed to become ready")
                self.kill_ai(ai_id)
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to launch {ai_id}: {e}")
            return False
    
    def kill_ai(self, ai_id: str) -> bool:
        """Kill a specific AI specialist."""
        # Deregister from registry
        self.registry_client.deregister_platform_ai(ai_id)
        
        # Kill process if we launched it
        if ai_id in self.launched_ais:
            process = self.launched_ais[ai_id]
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            del self.launched_ais[ai_id]
            self.logger.info(f"Killed AI {ai_id}")
            return True
            
        return False
    
    async def launch_multiple(self, components: List[str]):
        """Launch multiple AI specialists."""
        tasks = []
        
        for component in components:
            if component.lower() == 'all':
                # Get all components from config
                all_components = []
                for attr_name in dir(self.config):
                    if attr_name.startswith('_'):
                        continue
                    
                    # Check if it's a component config (has a port)
                    try:
                        comp_config = getattr(self.config, attr_name)
                        if hasattr(comp_config, 'port'):
                            # Check if this component supports AI
                            if attr_name not in AI_EXCLUDED_COMPONENTS:
                                all_components.append(attr_name)
                    except:
                        continue
                
                # Launch AI for each component
                for comp in all_components:
                    tasks.append(self.launch_ai(comp))
            else:
                tasks.append(self.launch_ai(component.lower()))
        
        if not tasks:
            self.logger.warning("No AI specialists to launch")
            return
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Report results
        launched = sum(1 for r in results if r is True)
        self.logger.info(f"Launched {launched}/{len(results)} AI specialists")
    
    def cleanup(self):
        """Clean up all launched AIs."""
        for ai_id in list(self.launched_ais.keys()):
            self.kill_ai(ai_id)


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Launch AI specialists for Tekton components'
    )
    parser.add_argument(
        'components', 
        nargs='+',
        help='Components to launch AIs for (or "all")'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--no-wait',
        action='store_true',
        help='Don\'t wait for AIs to be ready'
    )
    parser.add_argument(
        '--no-cleanup',
        action='store_true',
        help='Don\'t clean up launched AIs on exit (for use by enhanced_tekton_launcher)'
    )
    
    args = parser.parse_args()
    
    # Check if AI is enabled globally from Tekton config
    config = get_component_config()
    if not config.tekton.register_ai:
        print("AI support is disabled. Set TEKTON_REGISTER_AI=true in .env.tekton to enable.")
        sys.exit(1)
    
    launcher = AILauncher(verbose=args.verbose)
    
    try:
        await launcher.launch_multiple(args.components)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        if not args.no_cleanup:
            launcher.cleanup()


if __name__ == '__main__':
    asyncio.run(main())