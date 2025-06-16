#!/usr/bin/env python
"""
Memory cleanup utility script.

This script provides tools for cleaning up old or unnecessary memories
from the Ergon memory system.
"""

import os
import sys
import asyncio
import logging
import argparse
from datetime import datetime, timedelta
from typing import List, Optional

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ergon.core.database.engine import get_db_session
from ergon.core.memory.models.schema import Memory
from ergon.core.memory.utils.categories import MemoryCategory
from ergon.utils.config.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('memory_cleanup')

async def list_agents():
    """List all agents with memory counts."""
    with get_db_session() as db:
        # Get all agents with memory counts
        query = """
        SELECT a.id, a.name, COUNT(m.id) as memory_count 
        FROM agents a
        LEFT JOIN memories m ON a.id = m.agent_id
        GROUP BY a.id, a.name
        ORDER BY memory_count DESC
        """
        
        results = db.execute(query).fetchall()
        
        if not results:
            print("No agents found with memories.")
            return
        
        print(f"{'ID':^5} | {'Name':^30} | {'Memory Count':^12}")
        print("-" * 55)
        
        for agent_id, name, count in results:
            print(f"{agent_id:^5} | {name[:30]:^30} | {count:^12}")

async def cleanup_memories(
    agent_id: Optional[int] = None,
    days_threshold: int = 30,
    categories: Optional[List[str]] = None,
    exclude_categories: Optional[List[str]] = None,
    max_importance: Optional[int] = None,
    dry_run: bool = True
):
    """
    Clean up old memories.
    
    Args:
        agent_id: Optional agent ID to target (None for all agents)
        days_threshold: Age threshold in days for deletion
        categories: Categories to include in cleanup (None for all)
        exclude_categories: Categories to exclude from cleanup
        max_importance: Maximum importance level to include in cleanup
        dry_run: If True, only show what would be deleted
    """
    exclude_categories = exclude_categories or [
        MemoryCategory.PERSONAL,
        MemoryCategory.PREFERENCE
    ]
    
    # Calculate cutoff date
    cutoff_date = datetime.now() - timedelta(days=days_threshold)
    
    with get_db_session() as db:
        # Build query for memories to delete
        query = db.query(Memory).filter(Memory.created_at < cutoff_date)
        
        if agent_id:
            query = query.filter(Memory.agent_id == agent_id)
            
        if categories:
            query = query.filter(Memory.category.in_(categories))
            
        if exclude_categories:
            query = query.filter(~Memory.category.in_(exclude_categories))
            
        if max_importance:
            query = query.filter(Memory.importance <= max_importance)
        
        # Get count and sample of matching memories
        total_count = query.count()
        sample = query.limit(5).all()
        
        if total_count == 0:
            print("No memories match the cleanup criteria.")
            return
        
        # Print summary
        print(f"Found {total_count} memories matching cleanup criteria:")
        print(f"- Created before: {cutoff_date}")
        if agent_id:
            print(f"- Agent ID: {agent_id}")
        if categories:
            print(f"- Categories: {', '.join(categories)}")
        if exclude_categories:
            print(f"- Excluded categories: {', '.join(exclude_categories)}")
        if max_importance:
            print(f"- Max importance: {max_importance}")
            
        # Print sample
        print("\nSample of memories that would be deleted:")
        for i, memory in enumerate(sample):
            print(f"{i+1}. [{memory.category}] {memory.content[:100]}... (importance: {memory.importance})")
            
        # Confirm deletion if not dry run
        if dry_run:
            print(f"\nDRY RUN: {total_count} memories would be deleted.")
        else:
            confirm = input(f"\nDelete {total_count} memories? [y/N] ")
            if confirm.lower() != 'y':
                print("Cleanup canceled.")
                return
                
            # Delete from database
            deleted_count = query.delete(synchronize_session=False)
            db.commit()
            
            print(f"Successfully deleted {deleted_count} memories.")
            
            # Note about vector cleanup
            print("\nNOTE: This command only removes memories from the SQL database.")
            print("Vector embeddings may still remain in the vector store.")
            print("To clean up vector embeddings completely, consider rebuilding the vector index.")

def main():
    """Main function for the script."""
    parser = argparse.ArgumentParser(description="Memory cleanup utility")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List agents with memory counts")
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up old memories")
    cleanup_parser.add_argument(
        "--agent-id", "-a", 
        type=int, 
        help="Agent ID to target (default: all agents)"
    )
    cleanup_parser.add_argument(
        "--days", "-d", 
        type=int, 
        default=30,
        help="Age threshold in days (default: 30)"
    )
    cleanup_parser.add_argument(
        "--categories", "-c", 
        nargs="+", 
        help="Categories to include (default: all categories)"
    )
    cleanup_parser.add_argument(
        "--exclude", "-e", 
        nargs="+", 
        default=["personal", "preference"],
        help="Categories to exclude (default: personal, preference)"
    )
    cleanup_parser.add_argument(
        "--max-importance", "-i", 
        type=int, 
        help="Maximum importance level (default: all)"
    )
    cleanup_parser.add_argument(
        "--execute", 
        action="store_true",
        help="Execute deletion (without this flag, dry run only)"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.command == "list":
        asyncio.run(list_agents())
    elif args.command == "cleanup":
        asyncio.run(cleanup_memories(
            agent_id=args.agent_id,
            days_threshold=args.days,
            categories=args.categories,
            exclude_categories=args.exclude,
            max_importance=args.max_importance,
            dry_run=not args.execute
        ))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()