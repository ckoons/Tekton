#!/usr/bin/env python3
"""
Registry Flush Service
Periodically flushes the CI registry to disk and validates entries.
"""

import asyncio
import sys
import os
import logging
from datetime import datetime
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aish.src.registry.ci_registry import get_registry

# Configure logging
logger = logging.getLogger('registry_flush_service')

class RegistryFlushService:
    """Service to periodically flush CI registry to disk."""
    
    def __init__(self, 
                 flush_interval: float = 300.0,  # 5 minutes default
                 validate_on_start: bool = True):
        """
        Initialize the registry flush service.
        
        Args:
            flush_interval: Seconds between flush operations (default 5 minutes)
            validate_on_start: Whether to validate entries on startup
        """
        self.flush_interval = flush_interval
        self.validate_on_start = validate_on_start
        self.running = False
        self._task = None
        self.last_flush = None
        self.next_flush = None
        self.flush_count = 0
        
    async def start(self):
        """Start the registry flush service."""
        self.running = True
        logger.info("Starting registry flush service")
        
        # Get registry instance
        self.registry = get_registry()
        
        # Validate on startup if configured
        if self.validate_on_start:
            self._validate_entries()
        
        # Start periodic flush task
        self._task = asyncio.create_task(self._periodic_flush())
        
    async def stop(self):
        """Stop the registry flush service."""
        self.running = False
        logger.info("Stopping registry flush service")
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        # Final flush before stopping
        self._flush_registry()
        
    async def _periodic_flush(self):
        """Periodically flush the registry."""
        while self.running:
            try:
                self.next_flush = datetime.now().timestamp() + self.flush_interval
                await asyncio.sleep(self.flush_interval)
                
                if self.running:
                    self._flush_registry()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic flush: {e}")
                await asyncio.sleep(10)  # Brief pause before retry
    
    def _flush_registry(self):
        """Flush the registry to disk."""
        try:
            if hasattr(self.registry, 'flush_wrapped_cis'):
                result = self.registry.flush_wrapped_cis()
                if result:
                    self.last_flush = datetime.now().timestamp()
                    self.flush_count += 1
                    logger.info(f"Registry flush #{self.flush_count} completed")
                else:
                    logger.warning("Registry flush returned False")
            else:
                logger.debug("Registry does not have flush_wrapped_cis method")
                
        except Exception as e:
            logger.error(f"Failed to flush registry: {e}")
    
    def _validate_entries(self):
        """Validate registry entries and remove dead ones."""
        try:
            logger.info("Validating registry entries...")
            
            # The registry already validates on load, but we can do additional checks
            all_cis = self.registry.get_all()
            wrapped_cis = [ci for ci in all_cis.values() 
                          if ci.get('type') in ['ci_terminal', 'ci_tool']]
            
            dead_count = 0
            for ci in wrapped_cis:
                pid = ci.get('pid')
                if pid:
                    try:
                        os.kill(pid, 0)  # Check if process exists
                    except (ProcessLookupError, PermissionError):
                        # Process is dead
                        name = ci.get('name')
                        if name:
                            logger.info(f"Removing dead CI: {name} (PID {pid})")
                            self.registry.unregister_wrapped_ci(name)
                            dead_count += 1
            
            if dead_count > 0:
                logger.info(f"Removed {dead_count} dead CI entries")
                self._flush_registry()  # Flush after cleanup
                
        except Exception as e:
            logger.error(f"Failed to validate entries: {e}")
    
    def status(self):
        """Get service status."""
        return {
            "running": self.running,
            "flush_interval": self.flush_interval,
            "last_flush": self.last_flush,
            "next_flush": self.next_flush,
            "flush_count": self.flush_count
        }


# For testing
if __name__ == "__main__":
    async def test():
        service = RegistryFlushService(flush_interval=10)  # 10 seconds for testing
        await service.start()
        
        print("Registry flush service running. Press Ctrl+C to stop.")
        try:
            while True:
                await asyncio.sleep(5)
                print(f"Status: {service.status()}")
        except KeyboardInterrupt:
            pass
        finally:
            await service.stop()
    
    asyncio.run(test())