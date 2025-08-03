"""
Script to populate Ergon's database with solutions
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from ergon.core.database import get_session
from ergon.models import Solution
from ergon.solutions import SOLUTION_REGISTRY
import json

async def populate_solutions():
    """Populate the database with solutions"""
    async with get_session() as session:
        # Clear existing solutions (optional)
        # await session.execute("DELETE FROM solutions")
        
        for solution_data in SOLUTION_REGISTRY:
            # Check if solution already exists
            existing = await session.execute(
                f"SELECT id FROM solutions WHERE name = '{solution_data['name']}'"
            )
            if existing.fetchone():
                print(f"Solution '{solution_data['name']}' already exists, skipping...")
                continue
                
            # Create new solution
            solution = Solution(
                name=solution_data['name'],
                type=solution_data['type'],
                description=solution_data['description'],
                capabilities=json.dumps(solution_data['capabilities']),
                configuration=json.dumps(solution_data['configuration']),
                implementation=json.dumps(solution_data['implementation']),
                dependencies=json.dumps(solution_data.get('dependencies', [])),
                usage_count=0,
                success_rate=0.95  # Start with high success rate
            )
            
            session.add(solution)
            print(f"Added solution: {solution.name}")
            
        await session.commit()
        print("\nAll solutions added successfully!")
        
        # Display all solutions
        result = await session.execute("SELECT name, type, description FROM solutions")
        solutions = result.fetchall()
        
        print("\nCurrent solutions in database:")
        for i, (name, type_, desc) in enumerate(solutions, 1):
            print(f"{i}. {name} ({type_})")
            print(f"   {desc[:80]}...")

if __name__ == "__main__":
    asyncio.run(populate_solutions())