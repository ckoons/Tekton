#!/usr/bin/env python3
"""
Orphan Process Cleanup Service
Runs periodically to clean up orphaned Tekton CI processes.
"""

import asyncio
import sys
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from aish.cleanup_orphan_processes import cleanup_orphans, identify_orphans
    from inbox_orphan_cleanup import InboxOrphanCleaner
    from landmarks import service_boundary, monitoring_point, architecture_decision
except ImportError:
    # Fallback if landmarks not available
    def service_boundary(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def monitoring_point(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def architecture_decision(**kwargs):
        def decorator(func):
            return func
        return decorator

# Configure logging
logger = logging.getLogger('orphan_cleanup_service')
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

@architecture_decision(
    title="Orphan cleanup as shared service",
    rationale="Integrate with Tekton's async service pattern rather than cron",
    alternatives_considered=["Cron job", "Systemd timer", "Manual cleanup"],
    impacts=["resource_management", "system_stability"],
    decided_by="Casey",
    date="2025-01-04"
)
class OrphanCleanupService:
    """Service to periodically clean up orphaned Tekton processes."""
    
    def __init__(self, 
                 check_interval: float = 21600.0,  # 6 hours default
                 min_age_hours: float = 2.0,       # 2 hour minimum age
                 dry_run: bool = False):
        """
        Initialize the orphan cleanup service.
        
        Args:
            check_interval: Seconds between cleanup runs (default 6 hours)
            min_age_hours: Minimum age in hours before considering process orphaned
            dry_run: If True, only log what would be cleaned
        """
        self.check_interval = check_interval
        self.min_age_hours = min_age_hours
        self.dry_run = dry_run
        self.running = False
        self._task = None
        self.last_cleanup = None
        self.next_cleanup = None
        
        # Initialize inbox cleaner
        self.inbox_cleaner = InboxOrphanCleaner()
        
        # Ensure minimum interval of 1 hour
        if self.check_interval < 3600:
            logger.warning(f"Check interval {check_interval}s too short, setting to 1 hour")
            self.check_interval = 3600
    
    @service_boundary(
        title="Orphan cleanup service",
        inputs=["System process list", "AI registry"],
        outputs=["Terminated orphan processes", "Cleanup logs"],
        dependencies=["psutil", "AI registry"]
    )
    async def start(self):
        """Start the orphan cleanup service."""
        if self.running:
            logger.warning("Orphan cleanup service already running")
            return
        
        self.running = True
        self._task = asyncio.create_task(self._run_cleanup_loop())
        logger.info(f"Orphan cleanup service started (interval: {self.check_interval/3600:.1f} hours)")
        
        # Calculate next cleanup time
        self.next_cleanup = datetime.now() + timedelta(seconds=self.check_interval)
        logger.info(f"Next cleanup scheduled for: {self.next_cleanup.strftime('%Y-%m-%d %H:%M:%S')}")
    
    async def stop(self):
        """Stop the orphan cleanup service."""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Orphan cleanup service stopped")
    
    @monitoring_point(
        title="Orphan cleanup execution",
        metrics=["orphans_found", "orphans_cleaned", "cleanup_duration"],
        alerts=["cleanup_failed", "excessive_orphans"]
    )
    async def _run_cleanup_loop(self):
        """Main cleanup loop."""
        while self.running:
            try:
                # Run cleanup
                start_time = datetime.now()
                orphan_count = await self._run_cleanup()
                
                # Also clean up inbox orphans
                inbox_orphans = await self.inbox_cleaner.cleanup(self.dry_run)
                
                duration = (datetime.now() - start_time).total_seconds()
                
                self.last_cleanup = start_time
                
                # Log results
                logger.info(f"Cleanup completed: {orphan_count} process orphans {'found' if self.dry_run else 'cleaned'}, "
                          f"{inbox_orphans} inbox orphans {'found' if self.dry_run else 'cleaned'} in {duration:.1f}s")
                
                # Alert if too many orphans
                if orphan_count > 10:
                    logger.warning(f"Excessive orphans detected: {orphan_count}")
                
                # Calculate next cleanup time
                self.next_cleanup = datetime.now() + timedelta(seconds=self.check_interval)
                logger.info(f"Next cleanup scheduled for: {self.next_cleanup.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Wait for next interval
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                # Wait a bit before retrying
                await asyncio.sleep(60)
    
    async def _run_cleanup(self) -> int:
        """Run the cleanup in an async context."""
        # LANDMARK: Async-Sync Bridge
        # The cleanup functions are synchronous (using psutil) but we run them
        # in a thread pool executor to maintain async compatibility with the
        # Tekton service architecture. This prevents blocking the event loop.
        loop = asyncio.get_event_loop()
        
        # First identify orphans
        orphans, _ = await loop.run_in_executor(
            None, 
            identify_orphans,
            self.min_age_hours,
            False  # Not verbose in service mode
        )
        
        orphan_count = len(orphans)
        
        if orphan_count > 0:
            logger.info(f"Found {orphan_count} orphan processes")
            
            # Run actual cleanup
            await loop.run_in_executor(
                None,
                cleanup_orphans,
                self.dry_run,
                self.min_age_hours,
                False  # Not verbose in service mode
            )
        
        return orphan_count
    
    def status(self) -> dict:
        """Get service status."""
        return {
            "running": self.running,
            "check_interval_hours": self.check_interval / 3600,
            "min_age_hours": self.min_age_hours,
            "dry_run": self.dry_run,
            "last_cleanup": self.last_cleanup.isoformat() if self.last_cleanup else None,
            "next_cleanup": self.next_cleanup.isoformat() if self.next_cleanup else None
        }


async def main():
    """Run the service standalone."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Orphan Process Cleanup Service')
    parser.add_argument('--interval', type=float, default=6.0,
                       help='Hours between cleanup runs (default: 6.0, min: 1.0)')
    parser.add_argument('--min-age', type=float, default=2.0,
                       help='Minimum age in hours before considering process orphaned (default: 2.0)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Only log what would be cleaned, don\'t actually clean')
    
    args = parser.parse_args()
    
    # Convert hours to seconds
    interval_seconds = args.interval * 3600
    
    # Create and start service
    service = OrphanCleanupService(
        check_interval=interval_seconds,
        min_age_hours=args.min_age,
        dry_run=args.dry_run
    )
    
    try:
        await service.start()
        
        # Keep running until interrupted
        while True:
            await asyncio.sleep(60)
            
            # Optionally log status
            status = service.status()
            if status['next_cleanup']:
                next_time = datetime.fromisoformat(status['next_cleanup'])
                time_until = (next_time - datetime.now()).total_seconds()
                if time_until < 300:  # Less than 5 minutes
                    logger.info(f"Next cleanup in {time_until/60:.1f} minutes")
    
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        await service.stop()


if __name__ == "__main__":
    asyncio.run(main())