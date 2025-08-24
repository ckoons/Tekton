#!/usr/bin/env python3
"""
Run Tekton Shared Services
Manages background services that support the entire platform.
"""

import asyncio
import sys
import os
import signal
import logging
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.orphan_cleanup_service import OrphanCleanupService
from services.ai_config_sync import AIConfigSyncService
from services.registry_flush_service import RegistryFlushService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('shared_services')

class SharedServicesManager:
    """Manages all shared background services."""
    
    def __init__(self):
        self.services = {}
        self.running = False
    
    def add_service(self, name: str, service: Any):
        """Add a service to be managed."""
        self.services[name] = service
        logger.info(f"Added service: {name}")
    
    async def start_all(self):
        """Start all registered services."""
        self.running = True
        logger.info("Starting shared services...")
        
        for name, service in self.services.items():
            try:
                await service.start()
                logger.info(f"Started service: {name}")
            except Exception as e:
                logger.error(f"Failed to start service {name}: {e}")
    
    async def stop_all(self):
        """Stop all registered services."""
        self.running = False
        logger.info("Stopping shared services...")
        
        for name, service in self.services.items():
            try:
                await service.stop()
                logger.info(f"Stopped service: {name}")
            except Exception as e:
                logger.error(f"Failed to stop service {name}: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all services."""
        status = {
            "running": self.running,
            "services": {}
        }
        
        for name, service in self.services.items():
            try:
                if hasattr(service, 'status'):
                    status["services"][name] = service.status()
                else:
                    status["services"][name] = {"running": True}
            except Exception as e:
                status["services"][name] = {"error": str(e)}
        
        return status


async def main():
    """Main entry point for shared services."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Tekton Shared Services Manager')
    parser.add_argument('--orphan-cleanup', action='store_true', default=True,
                       help='Enable orphan process cleanup (default: enabled)')
    parser.add_argument('--orphan-interval', type=float, default=6.0,
                       help='Hours between orphan cleanup (default: 6.0)')
    parser.add_argument('--orphan-min-age', type=float, default=2.0,
                       help='Minimum age for orphan detection (default: 2.0 hours)')
    parser.add_argument('--ci-config-sync', action='store_true', default=True,
                       help='Enable AI config sync (default: enabled)')
    parser.add_argument('--registry-flush', action='store_true', default=True,
                       help='Enable registry flush service (default: enabled)')
    parser.add_argument('--flush-interval', type=float, default=5.0,
                       help='Minutes between registry flushes (default: 5.0)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Run in dry-run mode (no actual changes)')
    
    args = parser.parse_args()
    
    # Create service manager
    manager = SharedServicesManager()
    
    # Add orphan cleanup service
    if args.orphan_cleanup:
        orphan_service = OrphanCleanupService(
            check_interval=args.orphan_interval * 3600,  # Convert to seconds
            min_age_hours=args.orphan_min_age,
            dry_run=args.dry_run
        )
        manager.add_service('orphan_cleanup', orphan_service)
    
    # Add AI config sync service if it exists
    if args.ai_config_sync:
        try:
            config_sync = AIConfigSyncService()
            manager.add_service('ai_config_sync', config_sync)
        except ImportError:
            logger.warning("AI config sync service not available")
        except Exception as e:
            logger.warning(f"Could not initialize AI config sync: {e}")
    
    # Add registry flush service
    if args.registry_flush:
        try:
            registry_flush = RegistryFlushService(
                flush_interval=args.flush_interval * 60,  # Convert to seconds
                validate_on_start=True
            )
            manager.add_service('registry_flush', registry_flush)
        except Exception as e:
            logger.warning(f"Could not initialize registry flush service: {e}")
    
    # Setup signal handlers
    def signal_handler(sig, frame):
        logger.info("Received shutdown signal")
        asyncio.create_task(manager.stop_all())
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start all services
        await manager.start_all()
        
        logger.info("Shared services running. Press Ctrl+C to stop.")
        logger.info(f"Status: {manager.get_status()}")
        
        # Keep running
        while True:
            await asyncio.sleep(300)  # Log status every 5 minutes
            
            status = manager.get_status()
            logger.info(f"Services status check: {len(status['services'])} services running")
    
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    finally:
        await manager.stop_all()
        logger.info("Shared services stopped")


if __name__ == "__main__":
    asyncio.run(main())
