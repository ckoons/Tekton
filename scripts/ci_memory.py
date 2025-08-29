#!/usr/bin/env python3
"""
Enable/Disable Memory for Tekton CIs
Provides surgical control over memory system for each CI.
"""

import asyncio
import sys
from pathlib import Path
import argparse
import logging
import json

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment
from shared.env import TektonEnvironLock
TektonEnvironLock.load()

from Rhetor.rhetor.core.memory_middleware.system_integration import (
    TektonMemorySystem,
    initialize_tekton_memory
)
from shared.aish.src.registry.ci_registry import get_registry

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MemoryController:
    """Controls memory system with surgical precision."""
    
    def __init__(self):
        self.memory_system = TektonMemorySystem()
        self.registry = get_registry()
        
    async def enable_all(self):
        """Enable memory for all CIs."""
        print("Enabling memory for ALL CIs...")
        initialized = await self.memory_system.initialize_all_ci_memory()
        print(f"✓ Memory enabled for {len(initialized)} CIs")
        return initialized
        
    async def enable_ci(self, ci_name: str, config=None):
        """Enable memory for specific CI."""
        print(f"Enabling memory for {ci_name}...")
        self.memory_system.adapter.initialize_ci_memory(ci_name, config)
        
        # Mark as enabled in config
        self.memory_system.config['ci_configs'][ci_name.lower()] = config or {'enabled': True}
        self.memory_system.save_config()
        
        print(f"✓ Memory enabled for {ci_name}")
        return True
        
    async def disable_all(self):
        """Disable memory for all CIs (emergency stop)."""
        print("EMERGENCY STOP: Disabling memory for ALL CIs...")
        
        # Disable global flag
        self.memory_system.config['global']['enabled'] = False
        
        # Disable each CI
        all_cis = list(self.registry.get_all().keys())
        for ci_name in all_cis:
            self.memory_system.config['ci_configs'][ci_name.lower()] = {'enabled': False}
            
        self.memory_system.save_config()
        print(f"✓ Memory disabled for {len(all_cis)} CIs")
        return all_cis
        
    async def disable_ci(self, ci_name: str):
        """Disable memory for specific CI."""
        print(f"Disabling memory for {ci_name}...")
        
        # Mark as disabled in config
        self.memory_system.config['ci_configs'][ci_name.lower()] = {'enabled': False}
        self.memory_system.save_config()
        
        print(f"✓ Memory disabled for {ci_name}")
        return True
        
    def get_status(self, verbose=False):
        """Get memory system status."""
        status = self.memory_system.get_system_status()
        
        # Add per-CI enabled status
        all_cis = list(self.registry.get_all().keys())
        ci_status = {}
        
        for ci_name in all_cis:
            ci_config = self.memory_system.config['ci_configs'].get(ci_name.lower(), {})
            ci_status[ci_name] = {
                'enabled': ci_config.get('enabled', False),
                'config': ci_config
            }
            
        status['ci_status'] = ci_status
        return status


async def main():
    """Main entry point with surgical controls."""
    parser = argparse.ArgumentParser(
        description='Control memory system for Tekton CIs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Enable for all CIs
  %(prog)s --all
  
  # Enable for specific CI
  %(prog)s --ci ergon-ci
  
  # Emergency stop - disable all
  %(prog)s --stop
  
  # Disable specific CI
  %(prog)s --down ergon-ci
  
  # Show status
  %(prog)s --status
        """
    )
    
    # Action arguments (mutually exclusive)
    action = parser.add_mutually_exclusive_group()
    action.add_argument('--all', action='store_true',
                       help='Enable memory for all CIs')
    action.add_argument('--ci', metavar='NAME',
                       help='Enable memory for specific CI')
    action.add_argument('--stop', action='store_true',
                       help='EMERGENCY STOP - disable memory for all CIs')
    action.add_argument('--down', metavar='NAME',
                       help='Disable memory for specific CI')
    action.add_argument('--status', action='store_true',
                       help='Show memory system status')
    
    # Optional configuration
    parser.add_argument('--injection-style',
                       choices=['natural', 'structured', 'minimal'],
                       default='minimal',  # Default to minimal to avoid token explosion
                       help='How to inject memories (default: minimal)')
    parser.add_argument('--max-size', type=int, default=2000,
                       help='Maximum memory injection size in characters (default: 2000)')
    parser.add_argument('--verbose', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Require at least one action
    if not any([args.all, args.ci, args.stop, args.down, args.status]):
        parser.print_help()
        return 1
    
    controller = MemoryController()
    
    try:
        print("\n" + "="*60)
        print("TEKTON CI MEMORY SYSTEM")
        print("="*60 + "\n")
        
        if args.stop:
            # Emergency stop
            disabled = await controller.disable_all()
            print(f"\n🛑 EMERGENCY STOP COMPLETE")
            print(f"Memory disabled for: {', '.join(disabled)}")
            
        elif args.down:
            # Disable specific CI
            await controller.disable_ci(args.down)
            
        elif args.all:
            # Enable for all
            initialized = await controller.enable_all()
            if args.verbose:
                print(f"\nInitialized CIs:")
                for ci in initialized:
                    print(f"  - {ci}")
                    
        elif args.ci:
            # Enable for specific CI
            config = {
                'enabled': True,
                'injection_style': args.injection_style,
                'max_injection_size': args.max_size
            }
            await controller.enable_ci(args.ci, config)
            
        elif args.status:
            # Show status
            status = controller.get_status(args.verbose)
            
            print(f"Global enabled: {status['enabled']}")
            print(f"Total CIs: {len(status['ci_status'])}")
            
            enabled_cis = [ci for ci, info in status['ci_status'].items() 
                          if info['enabled']]
            disabled_cis = [ci for ci, info in status['ci_status'].items() 
                           if not info['enabled']]
            
            if enabled_cis:
                print(f"\n✓ Enabled CIs ({len(enabled_cis)}):")
                for ci in enabled_cis:
                    print(f"  - {ci}")
                    
            if disabled_cis:
                print(f"\n✗ Disabled CIs ({len(disabled_cis)}):")
                for ci in disabled_cis:
                    print(f"  - {ci}")
                    
            if args.verbose and status.get('ci_statuses'):
                print("\n" + "-"*40)
                print("DETAILED STATUS")
                print("-"*40)
                for ci_name, ci_status in status['ci_statuses'].items():
                    print(f"\n{ci_name}:")
                    for key, value in ci_status.items():
                        print(f"  {key}: {value}")
                        
        print("\n" + "="*60)
        return 0
        
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))