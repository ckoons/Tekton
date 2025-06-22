#!/usr/bin/env python3
"""
Simple utility to delete old operational data files.

This is a temporary solution until the full SharedServices infrastructure is built.
Deletes files older than configured retention period from operational directories.
"""

import os
import sys
import time
import json
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("delete_old_records")


class DeleteOldOperationalRecords:
    """Simple utility to clean up old operational data files."""
    
    def __init__(self, dry_run: bool = False):
        """
        Initialize the cleanup utility.
        
        Args:
            dry_run: If True, only log what would be deleted without actually deleting
        """
        self.dry_run = dry_run
        self.tekton_root = os.environ.get('TEKTON_ROOT', '/opt/tekton')
        self.config = self._load_config()
        self.stats = {
            'files_scanned': 0,
            'files_deleted': 0,
            'bytes_freed': 0,
            'errors': 0
        }
        
    def _load_config(self) -> Dict[str, any]:
        """Load configuration from environment variables."""
        config = {
            # Global retention (days)
            'retention_days': int(os.environ.get('TEKTON_DATA_RETENTION_DAYS', '2')),
            
            # Component-specific retention (days)
            'landmark_retention': int(os.environ.get('TEKTON_LANDMARK_RETENTION_DAYS', '2')),
            'registration_retention': int(os.environ.get('TEKTON_REGISTRATION_RETENTION_DAYS', '1')),
            'message_retention': int(os.environ.get('TEKTON_MESSAGE_RETENTION_DAYS', '3')),
            'ci_memory_retention': int(os.environ.get('TEKTON_CI_MEMORY_RETENTION_DAYS', '7')),
            
            # Paths to clean (relative to TEKTON_ROOT)
            'cleanup_paths': [
                ('landmarks/data/*.json', 'landmark_retention'),
                ('Hermes/registrations/*-agent-*.json', 'registration_retention'),
                ('.tekton/data/apollo/message_data/*.json', 'message_retention'),
                ('.tekton/data/apollo/context_data/*.json', 'message_retention'),
                ('ci_memory/*/conversations.json', 'ci_memory_retention'),
                ('ci_memory/*/current_session.json', 'ci_memory_retention'),
            ],
            
            # Files to never delete
            'exclude_patterns': [
                '**/registry.json',
                '**/.gitkeep',
                '**/README.md',
                '**/budget_policies.json',  # Keep budget policies
            ]
        }
        
        return config
        
    def should_delete(self, file_path: Path, retention_key: str) -> Tuple[bool, str]:
        """
        Determine if a file should be deleted based on age.
        
        Args:
            file_path: Path to the file
            retention_key: Key to look up retention period in config
            
        Returns:
            Tuple of (should_delete, reason)
        """
        # Check if file exists
        if not file_path.exists():
            return False, "File does not exist"
            
        # Check exclude patterns
        for pattern in self.config['exclude_patterns']:
            if file_path.match(pattern):
                return False, f"Excluded by pattern: {pattern}"
                
        # Get file age
        try:
            mtime = file_path.stat().st_mtime
            age_days = (time.time() - mtime) / (24 * 3600)
            retention_days = self.config.get(retention_key, self.config['retention_days'])
            
            if age_days > retention_days:
                return True, f"File is {age_days:.1f} days old (retention: {retention_days} days)"
            else:
                return False, f"File is {age_days:.1f} days old (retention: {retention_days} days)"
                
        except Exception as e:
            logger.error(f"Error checking file age for {file_path}: {e}")
            return False, f"Error checking file age: {e}"
            
    def clean_directory(self, pattern: str, retention_key: str) -> None:
        """
        Clean files matching pattern that are older than retention period.
        
        Args:
            pattern: Glob pattern for files to check
            retention_key: Key to look up retention period in config
        """
        base_path = Path(self.tekton_root)
        full_pattern = base_path / pattern
        
        logger.info(f"Scanning {full_pattern} with retention key '{retention_key}'")
        
        # Find all matching files
        files = list(base_path.glob(pattern))
        
        for file_path in files:
            self.stats['files_scanned'] += 1
            
            should_delete, reason = self.should_delete(file_path, retention_key)
            
            if should_delete:
                file_size = file_path.stat().st_size
                
                if self.dry_run:
                    logger.info(f"[DRY RUN] Would delete {file_path} ({file_size} bytes) - {reason}")
                else:
                    try:
                        file_path.unlink()
                        self.stats['files_deleted'] += 1
                        self.stats['bytes_freed'] += file_size
                        logger.info(f"Deleted {file_path} ({file_size} bytes) - {reason}")
                    except Exception as e:
                        self.stats['errors'] += 1
                        logger.error(f"Failed to delete {file_path}: {e}")
            else:
                logger.debug(f"Keeping {file_path} - {reason}")
                
    def run(self) -> Dict[str, any]:
        """
        Run the cleanup process.
        
        Returns:
            Statistics about the cleanup
        """
        start_time = time.time()
        
        logger.info(f"Starting cleanup (dry_run={self.dry_run})")
        logger.info(f"TEKTON_ROOT: {self.tekton_root}")
        logger.info(f"Configuration: {json.dumps(self.config, indent=2)}")
        
        # Process each cleanup path
        for pattern, retention_key in self.config['cleanup_paths']:
            try:
                self.clean_directory(pattern, retention_key)
            except Exception as e:
                logger.error(f"Error processing pattern {pattern}: {e}")
                self.stats['errors'] += 1
                
        # Calculate summary
        elapsed_time = time.time() - start_time
        self.stats['elapsed_seconds'] = elapsed_time
        self.stats['mb_freed'] = self.stats['bytes_freed'] / (1024 * 1024)
        
        # Log summary
        logger.info("=" * 60)
        logger.info("CLEANUP SUMMARY:")
        logger.info(f"  Files scanned: {self.stats['files_scanned']}")
        logger.info(f"  Files deleted: {self.stats['files_deleted']}")
        logger.info(f"  Space freed: {self.stats['mb_freed']:.2f} MB")
        logger.info(f"  Errors: {self.stats['errors']}")
        logger.info(f"  Time elapsed: {elapsed_time:.2f} seconds")
        if self.dry_run:
            logger.info("  ** DRY RUN - No files were actually deleted **")
        logger.info("=" * 60)
        
        return self.stats


def main():
    """Main entry point for command line usage."""
    parser = argparse.ArgumentParser(
        description="Delete old operational data files from Tekton"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be deleted without actually deleting'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set log level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        
    # Create and run cleaner
    cleaner = DeleteOldOperationalRecords(dry_run=args.dry_run)
    stats = cleaner.run()
    
    # Exit with error code if there were errors
    sys.exit(1 if stats['errors'] > 0 else 0)


if __name__ == '__main__':
    main()