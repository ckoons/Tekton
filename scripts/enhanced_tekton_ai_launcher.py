#!/usr/bin/env python3
# @tekton-module: Enhanced AI Launcher for Tekton components
# @tekton-depends: registry_client, env_config, subprocess
# @tekton-provides: ai-lifecycle-management, ai-launching, ai-monitoring
# @tekton-version: 2.0.0
# @tekton-executable: true
# @tekton-cli: true

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

# Import landmarks
try:
    from landmarks import (
        architecture_decision,
        performance_boundary,
        api_contract,
        danger_zone,
        integration_point,
        state_checkpoint
    )
except ImportError:
    # If landmarks not available, create no-op decorators
    def architecture_decision(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def performance_boundary(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def api_contract(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def danger_zone(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def state_checkpoint(**kwargs):
        def decorator(func):
            return func
        return decorator

# Add Tekton root to path
script_path = os.path.realpath(__file__)
tekton_root = os.path.dirname(os.path.dirname(script_path))
sys.path.insert(0, tekton_root)

# Registry client removed - using fixed ports
from shared.utils.env_config import get_component_config
from shared.utils.logging_setup import setup_component_logging

# @tekton-constant: Components excluded from AI support
# @tekton-rationale: These components don't benefit from AI assistance
AI_EXCLUDED_COMPONENTS = {'ui_dev_tools', 'ui-dev-tools', 'ui_devtools'}


# @tekton-function: Calculate expected AI port from component main port
# @tekton-rationale: Deterministic port allocation prevents race conditions
def get_expected_ai_port(main_port: int) -> int:
    """
    Calculate expected AI port based on component's main port.
    
    Uses port bases from environment configuration.
    
    Examples with defaults (TEKTON_PORT_BASE=8000, TEKTON_AI_PORT_BASE=45000):
        Hermes (8001) -> 45001
        Engram (8002) -> 45002
        Rhetor (8003) -> 45003
        Apollo (8012) -> 45012
        Athena (8005) -> 45005
    """
    # Import here to avoid circular dependency
    from shared.utils.ai_port_utils import get_ai_port
    return get_ai_port(main_port)


# @tekton-class: Main AI launcher for managing specialist lifecycle
# @tekton-singleton: false
# @tekton-lifecycle: launcher
@architecture_decision(
    title="Centralized AI Launcher Architecture",
    rationale="Single launcher manages all AI specialists for consistency and resource control",
    alternatives_considered=["Component-embedded AIs", "Distributed launchers"],
    impacts=["centralized_control", "launch_performance", "monitoring_capability"]
)
@state_checkpoint(
    title="AI Process State Tracking",
    state_type="runtime",
    persistence=False,
    consistency_requirements="Process handles and registry sync"
)
class AILauncher:
    """Manages AI specialist launching."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.config = get_component_config()
        # Registry client removed - AIs use fixed ports
        self.launched_ais: Dict[str, subprocess.Popen] = {}
        
        # Setup logging
        log_level = 'DEBUG' if verbose else 'INFO'
        self.logger = setup_component_logging('ai_launcher', log_level)
    
    async def _wait_for_ai_direct(self, ai_id: str, port: int, timeout: int = 30) -> bool:
        """Wait for AI to be ready by trying to connect directly."""
        import time
        import socket
        start = time.time()
        while time.time() - start < timeout:
            try:
                s = socket.socket()
                s.settimeout(1)
                s.connect(('localhost', port))
                s.close()
                return True
            except:
                await asyncio.sleep(1)
        return False
    
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
        
    # @tekton-method: Launch AI specialist for component
    # @tekton-async: true
    # @tekton-critical: true
    # @tekton-side-effects: process-creation, port-allocation
    @performance_boundary(
        title="AI Launch Sequence",
        sla="<30s for AI readiness",
        optimization_notes="Parallel launch support, readiness checking"
    )
    @integration_point(
        title="AI Process Launch",
        target_component="AI specialists",
        protocol="subprocess + socket",
        data_flow="Launch parameters, readiness verification"
    )
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
        
        # Check if already running by trying to connect to expected port
        expected_ai_port = get_expected_ai_port(self.config.get_port(component))
        try:
            import socket
            s = socket.socket()
            s.settimeout(1)
            s.connect(('localhost', expected_ai_port))
            s.close()
            self.logger.info(f"AI {ai_id} already running on port {expected_ai_port}")
            return True
        except:
            pass  # Not running
        
        # Check if component exists and is configured
        if not self.check_component_config(component):
            self.logger.info(f"Component {component} not properly configured")
            return False
        
        # Calculate expected AI port based on component's main port
        expected_ai_port = None
        component_config = getattr(self.config, component, None)
        if component_config and hasattr(component_config, 'port'):
            main_port = component_config.port
            expected_ai_port = get_expected_ai_port(main_port)
            self.logger.debug(f"Component {component} main port: {main_port}, expected AI port: {expected_ai_port}")
        else:
            self.logger.warning(f"Could not determine expected port for {component}")
        
        # Allocate port for AI (will try to get the expected one)
        # Use fixed port calculation
        ai_port = expected_ai_port
        if not ai_port:
            self.logger.error(f"Could not allocate port for {ai_id}")
            return False
        
        # Log the allocation result
        if expected_ai_port and ai_port == expected_ai_port:
            self.logger.info(f"✓ Allocated expected port {ai_port} for {ai_id}")
        elif expected_ai_port and ai_port != expected_ai_port:
            self.logger.error(f"✗ Port mismatch for {ai_id}: expected {expected_ai_port}, got {ai_port}")
            # Still continue but with error logged
        else:
            self.logger.info(f"Allocated port {ai_port} for {ai_id}")
        
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
            self.logger.debug(f"Launch command: {' '.join(cmd)}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**os.environ, 'PYTHONPATH': tekton_root}
            )
            
            self.launched_ais[ai_id] = process
            
            # No registry registration needed - using fixed ports
            self.logger.info(f"AI {ai_id} launched on fixed port {ai_port} (PID: {process.pid})")
            
            # Wait for AI to be ready (skip for Hermes - it receives health checks, doesn't perform them)
            if component.lower() == 'hermes':
                self.logger.info(f"Successfully launched {ai_id} (skipped readiness check for Hermes)")
                return True
            elif await self._wait_for_ai_direct(ai_id, ai_port, timeout=30):
                self.logger.info(f"Successfully launched {ai_id}")
                self.logger.debug(f"AI {ai_id} ready - PID: {process.pid}")
                return True
            else:
                self.logger.error(f"AI {ai_id} failed to become ready")
                self.kill_ai(ai_id)
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to launch {ai_id}: {e}")
            return False
    
    # @tekton-method: Kill AI specialist process
    # @tekton-critical: true
    # @tekton-cleanup: true
    @danger_zone(
        title="AI Process Termination",
        risk_level="medium",
        risks=["Orphaned processes", "Registry inconsistency"],
        mitigation="Graceful termination with timeout and force kill"
    )
    def kill_ai(self, ai_id: str) -> bool:
        """Kill a specific AI specialist."""
        # Deregister from registry
        # No registry deregistration needed - using fixed ports
        
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
    
    def show_port_mapping(self):
        """Display expected port mapping for all components."""
        self.logger.info("Expected AI Port Mapping:")
        self.logger.info("=" * 50)
        
        components = []
        for attr_name in dir(self.config):
            if attr_name.startswith('_'):
                continue
            
            try:
                comp_config = getattr(self.config, attr_name)
                if hasattr(comp_config, 'port') and attr_name not in AI_EXCLUDED_COMPONENTS:
                    main_port = comp_config.port
                    expected_ai_port = get_expected_ai_port(main_port)
                    components.append((attr_name, main_port, expected_ai_port))
            except:
                continue
        
        # Sort by main port
        components.sort(key=lambda x: x[1])
        
        for comp_name, main_port, ai_port in components:
            self.logger.info(f"{comp_name:15} : {main_port} → {ai_port}")
        
        self.logger.info("=" * 50)


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Launch AI specialists for Tekton components'
    )
    parser.add_argument(
        'components', 
        nargs='*',  # Changed to * to make optional when using --show-mapping
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
    parser.add_argument(
        '--show-mapping',
        action='store_true',
        help='Show expected port mapping and exit'
    )
    
    args = parser.parse_args()
    
    # AI is always enabled with fixed ports - no need to check
    
    launcher = AILauncher(verbose=args.verbose)
    
    # Handle show-mapping option
    if args.show_mapping:
        launcher.show_port_mapping()
        sys.exit(0)
    
    # Ensure components are specified if not showing mapping
    if not args.components:
        parser.error("Please specify components to launch or use 'all'")
    
    try:
        await launcher.launch_multiple(args.components)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        if not args.no_cleanup:
            launcher.cleanup()


if __name__ == '__main__':
    asyncio.run(main())