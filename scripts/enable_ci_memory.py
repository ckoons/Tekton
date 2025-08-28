#!/usr/bin/env python3
"""
Enable Memory for All Tekton CIs
Run this to initialize memory system for all CIs.
"""

import asyncio
import sys
from pathlib import Path
import argparse
import logging

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


async def enable_memory(args):
    """Enable memory for CIs based on arguments."""
    
    print("\n" + "="*60)
    print("TEKTON CI MEMORY SYSTEM")
    print("="*60 + "\n")
    
    memory_system = TektonMemorySystem()
    
    if args.all:
        # Initialize for all CIs
        print("Initializing memory for ALL CIs...")
        initialized = await memory_system.initialize_all_ci_memory()
        print(f"\n✓ Memory enabled for {len(initialized)} CIs:")
        for ci in initialized:
            print(f"  - {ci}")
            
    elif args.ci:
        # Initialize for specific CI
        print(f"Initializing memory for {args.ci}...")
        
        # Get config if specified
        config = None
        if args.config:
            config = {
                'injection_style': args.injection_style,
                'training_stage': args.training_stage,
                'memory_tiers': args.memory_tiers.split(',') if args.memory_tiers else ['short', 'medium', 'long']
            }
        
        memory_system.adapter.initialize_ci_memory(args.ci, config)
        print(f"✓ Memory enabled for {args.ci}")
        
    # Show status
    if args.status or args.all:
        print("\n" + "-"*40)
        print("MEMORY SYSTEM STATUS")
        print("-"*40)
        
        status = memory_system.get_system_status()
        print(f"Enabled: {status['enabled']}")
        print(f"Initialized CIs: {', '.join(status['initialized_cis'])}")
        
        if args.verbose:
            print("\nDetailed Status:")
            for ci_name, ci_status in status['ci_statuses'].items():
                print(f"\n{ci_name}:")
                print(f"  Total injections: {ci_status.get('total_injections', 0)}")
                print(f"  Total extractions: {ci_status.get('total_extractions', 0)}")
                print(f"  Habit stage: {ci_status.get('habit_stage', 'unknown')}")
                print(f"  Memory usage rate: {ci_status.get('memory_usage_rate', 'N/A')}")
    
    # Save config if requested
    if args.save:
        memory_system.save_config()
        print(f"\n✓ Configuration saved to {memory_system.config_file}")
    
    return memory_system


async def test_memory(ci_name: str):
    """Quick test of memory functionality."""
    print(f"\n" + "-"*40)
    print(f"TESTING MEMORY FOR {ci_name.upper()}")
    print("-"*40)
    
    # Get the adapter
    from Rhetor.rhetor.core.memory_middleware.universal_adapter import get_universal_adapter
    adapter = get_universal_adapter()
    
    # Test injection
    test_message = "What are the key components of a distributed system?"
    enriched = await adapter.inject_memory(ci_name, test_message)
    
    print(f"\nOriginal: {test_message}")
    print(f"Enriched: {enriched[:200]}..." if len(enriched) > 200 else f"Enriched: {enriched}")
    
    # Simulate response
    test_response = "A distributed system consists of multiple components..."
    await adapter.extract_memory(ci_name, test_message, test_response)
    
    print("\n✓ Memory injection and extraction working")


async def configure_ci(args):
    """Configure memory for specific CI."""
    memory_system = TektonMemorySystem()
    
    config = {
        'injection_style': args.injection_style,
        'training_stage': args.training_stage,
        'memory_tiers': args.memory_tiers.split(',') if args.memory_tiers else ['short', 'medium', 'long'],
        'focus': args.focus or 'general'
    }
    
    memory_system.update_ci_config(args.ci, config)
    print(f"✓ Updated configuration for {args.ci}")
    
    if args.verbose:
        print(f"\nNew configuration:")
        for key, value in config.items():
            print(f"  {key}: {value}")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Enable memory for Tekton CIs')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Enable command
    enable_parser = subparsers.add_parser('enable', help='Enable memory')
    enable_parser.add_argument('--all', action='store_true', help='Enable for all CIs')
    enable_parser.add_argument('--ci', help='Enable for specific CI')
    enable_parser.add_argument('--config', action='store_true', help='Use custom config')
    enable_parser.add_argument('--injection-style', 
                              choices=['natural', 'structured', 'minimal'],
                              default='natural')
    enable_parser.add_argument('--training-stage',
                              choices=['explicit', 'shortened', 'minimal', 'occasional', 'autonomous'],
                              default='explicit')
    enable_parser.add_argument('--memory-tiers', help='Comma-separated tiers')
    enable_parser.add_argument('--status', action='store_true', help='Show status')
    enable_parser.add_argument('--save', action='store_true', help='Save configuration')
    enable_parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    # Configure command
    config_parser = subparsers.add_parser('configure', help='Configure CI memory')
    config_parser.add_argument('ci', help='CI name to configure')
    config_parser.add_argument('--injection-style',
                              choices=['natural', 'structured', 'minimal'],
                              default='natural')
    config_parser.add_argument('--training-stage',
                              choices=['explicit', 'shortened', 'minimal', 'occasional', 'autonomous'],
                              default='explicit')
    config_parser.add_argument('--memory-tiers', help='Comma-separated tiers')
    config_parser.add_argument('--focus', help='Memory focus area')
    config_parser.add_argument('--verbose', action='store_true')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test memory for CI')
    test_parser.add_argument('ci', help='CI name to test')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show memory status')
    status_parser.add_argument('--verbose', action='store_true')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'enable':
            await enable_memory(args)
        elif args.command == 'configure':
            await configure_ci(args)
        elif args.command == 'test':
            memory_system = TektonMemorySystem()
            await memory_system.initialize_all_ci_memory()
            await test_memory(args.ci)
        elif args.command == 'status':
            memory_system = TektonMemorySystem()
            status = memory_system.get_system_status()
            
            print("\n" + "="*60)
            print("MEMORY SYSTEM STATUS")
            print("="*60)
            print(f"\nEnabled: {status['enabled']}")
            print(f"Initialized CIs: {', '.join(status['initialized_cis'])}")
            
            if args.verbose:
                print("\n" + "-"*40)
                print("DETAILED CI STATUS")
                print("-"*40)
                for ci_name, ci_status in status['ci_statuses'].items():
                    print(f"\n{ci_name}:")
                    for key, value in ci_status.items():
                        print(f"  {key}: {value}")
        
        print("\n✓ Operation completed successfully")
        return 0
        
    except KeyboardInterrupt:
        print("\nOperation cancelled")
        return 1
    except Exception as e:
        logger.error(f"Operation failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))