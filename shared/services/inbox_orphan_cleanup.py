#!/usr/bin/env python3
"""
Inbox Orphan Cleanup Service
Cleans up orphaned inbox files from terminated terminals.
"""

import os
import json
import logging
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import List, Set, Optional
from pathlib import Path

try:
    from shared.urls import terma_url as get_terma_url
except ImportError:
    get_terma_url = None

# Configure logging
logger = logging.getLogger('inbox_orphan_cleanup')

class InboxOrphanCleaner:
    """Cleans up orphaned inbox files from terminated terminals."""
    
    def __init__(self, 
                 terma_endpoint: str = None,
                 tekton_root: Optional[str] = None):
        """
        Initialize the inbox orphan cleaner.
        
        Args:
            terma_endpoint: URL of the Terma service
            tekton_root: Root directory of Tekton (defaults to env var)
        """
        if terma_endpoint:
            self.terma_endpoint = terma_endpoint
        elif get_terma_url:
            self.terma_endpoint = get_terma_url("")
        else:
            self.terma_endpoint = 'http://localhost:8004'
        self.tekton_root = tekton_root or os.environ.get('TEKTON_ROOT', '/Users/cskoons/projects/github/Tekton')
        self.inbox_dir = os.path.join(self.tekton_root, ".tekton", "terma")
        
    async def get_active_terminals(self) -> List[dict]:
        """Get list of active terminals from Terma."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.terma_endpoint}/api/mcp/v2/terminals/list", 
                                     timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('terminals', [])
                    else:
                        logger.warning(f"Failed to get terminals: HTTP {response.status}")
                        return []
        except Exception as e:
            logger.warning(f"Failed to connect to Terma: {e}")
            # If Terma is down, assume no terminals are active
            return []
    
    def cleanup_orphaned_inboxes(self, active_terminal_ids: Set[str], dry_run: bool = False) -> int:
        """
        Remove inbox files for terminals that are no longer active.
        
        Args:
            active_terminal_ids: Set of active terminal IDs
            dry_run: If True, only log what would be cleaned
            
        Returns:
            Number of orphaned files cleaned
        """
        cleaned_count = 0
        
        # Check shared inbox snapshot
        snapshot_file = os.path.join(self.inbox_dir, ".inbox_snapshot")
        if os.path.exists(snapshot_file):
            try:
                with open(snapshot_file, 'r') as f:
                    data = json.load(f)
                session_id = data.get('session_id')
                
                # Check if this session is still active
                if session_id and not any(tid.startswith(session_id[:8]) for tid in active_terminal_ids):
                    if dry_run:
                        logger.info(f"Would remove orphaned inbox snapshot for session {session_id[:8]}")
                    else:
                        os.remove(snapshot_file)
                        logger.info(f"Removed orphaned inbox snapshot for session {session_id[:8]}")
                    cleaned_count += 1
                    
            except Exception as e:
                logger.warning(f"Failed to check inbox snapshot: {e}")
        
        # Check for terminal-specific inbox files (future-proofing)
        inboxes_dir = os.path.join(self.inbox_dir, "inboxes")
        if os.path.exists(inboxes_dir):
            for inbox_file in os.listdir(inboxes_dir):
                if inbox_file.endswith('.inbox'):
                    terminal_id = inbox_file[:-6]  # Remove .inbox extension
                    
                    # Check if this terminal is still active
                    if terminal_id not in active_terminal_ids:
                        inbox_path = os.path.join(inboxes_dir, inbox_file)
                        if dry_run:
                            logger.info(f"Would remove orphaned inbox file: {inbox_file}")
                        else:
                            os.remove(inbox_path)
                            logger.info(f"Removed orphaned inbox file: {inbox_file}")
                        cleaned_count += 1
        
        # Clean up orphaned command files
        cmd_dir = os.path.join(self.inbox_dir, "commands")
        if os.path.exists(cmd_dir):
            for cmd_file in os.listdir(cmd_dir):
                if cmd_file.endswith('.json'):
                    # Extract session ID from command filename if present
                    # Command files might contain session ID in the name
                    file_is_orphaned = True
                    
                    # Check if any active terminal ID is in the filename
                    for tid in active_terminal_ids:
                        if tid[:8] in cmd_file:
                            file_is_orphaned = False
                            break
                    
                    # If no active terminal claims this command file and it's old
                    if file_is_orphaned:
                        cmd_path = os.path.join(cmd_dir, cmd_file)
                        try:
                            # Check file age (clean if older than 1 hour)
                            file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cmd_path))
                            if file_age > timedelta(hours=1):
                                if dry_run:
                                    logger.info(f"Would remove orphaned command file: {cmd_file}")
                                else:
                                    os.remove(cmd_path)
                                    logger.info(f"Removed orphaned command file: {cmd_file}")
                                cleaned_count += 1
                        except Exception as e:
                            logger.warning(f"Failed to check command file {cmd_file}: {e}")
        
        return cleaned_count
    
    async def cleanup(self, dry_run: bool = False) -> int:
        """
        Perform a full cleanup of orphaned inbox files.
        
        Args:
            dry_run: If True, only log what would be cleaned
            
        Returns:
            Number of orphaned files cleaned
        """
        # Get active terminals
        terminals = await self.get_active_terminals()
        active_ids = {t['terma_id'] for t in terminals}
        
        logger.info(f"Found {len(active_ids)} active terminals")
        
        # Perform cleanup
        cleaned = self.cleanup_orphaned_inboxes(active_ids, dry_run)
        
        if cleaned > 0:
            logger.info(f"{'Would clean' if dry_run else 'Cleaned'} {cleaned} orphaned inbox files")
        else:
            logger.debug("No orphaned inbox files found")
            
        return cleaned


class InboxCleanupService:
    """Service to periodically clean up orphaned inbox files."""
    
    def __init__(self,
                 check_interval: float = 3600.0,  # 1 hour default
                 dry_run: bool = False):
        """
        Initialize the inbox cleanup service.
        
        Args:
            check_interval: Seconds between cleanup runs
            dry_run: If True, only log what would be cleaned
        """
        self.check_interval = check_interval
        self.dry_run = dry_run
        self.cleaner = InboxOrphanCleaner()
        self.running = False
        self._task = None
        
    async def start(self):
        """Start the inbox cleanup service."""
        if self.running:
            logger.warning("Inbox cleanup service already running")
            return
            
        self.running = True
        self._task = asyncio.create_task(self._run_cleanup_loop())
        logger.info(f"Inbox cleanup service started (interval: {self.check_interval/3600:.1f} hours)")
        
    async def stop(self):
        """Stop the inbox cleanup service."""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Inbox cleanup service stopped")
        
    async def _run_cleanup_loop(self):
        """Main cleanup loop."""
        while self.running:
            try:
                # Run cleanup
                cleaned = await self.cleaner.cleanup(self.dry_run)
                
                # Wait for next interval
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.error(f"Error in inbox cleanup loop: {e}")
                # Wait a bit before retrying
                await asyncio.sleep(60)


async def main():
    """Run the inbox cleanup standalone or as a one-shot."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Inbox Orphan Cleanup')
    parser.add_argument('--service', action='store_true',
                       help='Run as a continuous service')
    parser.add_argument('--interval', type=float, default=1.0,
                       help='Hours between cleanup runs (service mode, default: 1.0)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Only log what would be cleaned')
    
    args = parser.parse_args()
    
    # Configure logging for standalone mode
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    if args.service:
        # Run as service
        service = InboxCleanupService(
            check_interval=args.interval * 3600,
            dry_run=args.dry_run
        )
        
        try:
            await service.start()
            # Keep running until interrupted
            while True:
                await asyncio.sleep(60)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            await service.stop()
    else:
        # Run one-shot cleanup
        cleaner = InboxOrphanCleaner()
        cleaned = await cleaner.cleanup(args.dry_run)
        print(f"{'Would clean' if args.dry_run else 'Cleaned'} {cleaned} orphaned inbox files")


if __name__ == "__main__":
    asyncio.run(main())