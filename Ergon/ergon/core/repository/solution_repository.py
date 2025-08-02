"""
Solution Repository for Ergon v2.

This module implements CRUD operations for solutions in the registry,
including tools, agents, MCP servers, and workflows.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.v2_models import Solution, SolutionType
from ..database.engine import get_db_session

# Import landmarks with fallback
try:
    from landmarks import state_checkpoint, performance_boundary
except ImportError:
    # Create no-op decorators if landmarks module is not available
    def state_checkpoint(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    def performance_boundary(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

logger = logging.getLogger(__name__)


@state_checkpoint(
    title="Solution Repository State",
    state_type="persistent",
    persistence=True,
    consistency_requirements="ACID transactions for solution data",
    recovery_strategy="Database rollback on failure"
)
@performance_boundary(
    title="Solution CRUD Performance",
    sla="<100ms for single operations, <500ms for list queries",
    metrics={"index_fields": ["type", "name", "capabilities"], "cache": "query results"},
    optimization_notes="Use database indexes, query result caching"
)
class SolutionRepository:
    """
    Repository for managing solutions in the registry.
    
    Provides CRUD operations for:
    - Tools
    - Agents  
    - MCP servers
    - Libraries
    - Frameworks
    - Workflows
    """
    
    async def create_solution(self, solution_data: Dict[str, Any]) -> Solution:
        """
        Create a new solution in the registry.
        
        Args:
            solution_data: Dictionary containing solution information
            
        Returns:
            Created Solution object
        """
        async with get_db_session() as session:
            try:
                # Create solution instance
                solution = Solution(
                    name=solution_data["name"],
                    type=SolutionType(solution_data["type"]),
                    description=solution_data.get("description", ""),
                    version=solution_data.get("version", "1.0.0"),
                    source_url=solution_data.get("source_url"),
                    documentation_url=solution_data.get("documentation_url"),
                    author=solution_data.get("author", "unknown"),
                    license=solution_data.get("license", "unknown"),
                    tags=solution_data.get("tags", []),
                    capabilities=solution_data.get("capabilities", {}),
                    dependencies=solution_data.get("dependencies", {}),
                    configuration_template=solution_data.get("configuration_template", {}),
                    usage_examples=solution_data.get("usage_examples", []),
                    extra_metadata=solution_data.get("metadata", {})
                )
                
                session.add(solution)
                await session.commit()
                await session.refresh(solution)
                
                logger.info(f"Created solution: {solution.name} (type: {solution.type.value})")
                return solution
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to create solution: {e}")
                raise
                
    async def get_solution(self, solution_id: int) -> Optional[Solution]:
        """
        Get a solution by ID.
        
        Args:
            solution_id: Solution ID
            
        Returns:
            Solution object or None if not found
        """
        async with get_db_session() as session:
            result = await session.execute(
                select(Solution).where(Solution.id == solution_id)
            )
            solution = result.scalar_one_or_none()
            
            if solution:
                # Update last accessed
                solution.last_accessed = datetime.utcnow()
                await session.commit()
                
            return solution
            
    async def get_solution_by_name(self, name: str) -> Optional[Solution]:
        """
        Get a solution by name.
        
        Args:
            name: Solution name
            
        Returns:
            Solution object or None if not found
        """
        async with get_db_session() as session:
            result = await session.execute(
                select(Solution).where(Solution.name == name)
            )
            solution = result.scalar_one_or_none()
            
            if solution:
                # Update last accessed
                solution.last_accessed = datetime.utcnow()
                await session.commit()
                
            return solution
            
    async def update_solution(self, solution_id: int, update_data: Dict[str, Any]) -> Optional[Solution]:
        """
        Update a solution.
        
        Args:
            solution_id: Solution ID
            update_data: Dictionary of fields to update
            
        Returns:
            Updated Solution object or None if not found
        """
        async with get_db_session() as session:
            try:
                # Get solution
                result = await session.execute(
                    select(Solution).where(Solution.id == solution_id)
                )
                solution = result.scalar_one_or_none()
                
                if not solution:
                    return None
                    
                # Update fields
                for field, value in update_data.items():
                    if hasattr(solution, field) and field not in ["id", "created_at"]:
                        setattr(solution, field, value)
                        
                solution.updated_at = datetime.utcnow()
                
                await session.commit()
                await session.refresh(solution)
                
                logger.info(f"Updated solution: {solution.name}")
                return solution
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to update solution {solution_id}: {e}")
                raise
                
    async def delete_solution(self, solution_id: int) -> bool:
        """
        Delete a solution.
        
        Args:
            solution_id: Solution ID
            
        Returns:
            True if deleted, False if not found
        """
        async with get_db_session() as session:
            try:
                # Get solution
                result = await session.execute(
                    select(Solution).where(Solution.id == solution_id)
                )
                solution = result.scalar_one_or_none()
                
                if not solution:
                    return False
                    
                await session.delete(solution)
                await session.commit()
                
                logger.info(f"Deleted solution: {solution.name}")
                return True
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to delete solution {solution_id}: {e}")
                raise
                
    async def list_solutions(
        self,
        solution_type: Optional[SolutionType] = None,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None,
        capability: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "created_at",
        order_desc: bool = True
    ) -> tuple[List[Solution], int]:
        """
        List solutions with filtering and pagination.
        
        Args:
            solution_type: Filter by type
            search: Search in name and description
            tags: Filter by tags
            capability: Filter by capability key
            limit: Maximum results
            offset: Offset for pagination
            order_by: Field to order by
            order_desc: Order descending if True
            
        Returns:
            Tuple of (solutions list, total count)
        """
        async with get_db_session() as session:
            # Build base query
            query = select(Solution)
            count_query = select(func.count(Solution.id))
            
            # Apply filters
            conditions = []
            
            if solution_type:
                conditions.append(Solution.type == solution_type)
                
            if search:
                search_pattern = f"%{search}%"
                conditions.append(
                    or_(
                        Solution.name.ilike(search_pattern),
                        Solution.description.ilike(search_pattern)
                    )
                )
                
            if tags:
                # Check if any of the provided tags are in the solution's tags
                for tag in tags:
                    conditions.append(
                        func.json_extract(Solution.tags, f'$[*]').like(f'%{tag}%')
                    )
                    
            if capability:
                # Check if capability exists in capabilities JSON
                conditions.append(
                    func.json_extract(Solution.capabilities, f'$.{capability}').isnot(None)
                )
                
            # Apply conditions
            if conditions:
                where_clause = and_(*conditions)
                query = query.where(where_clause)
                count_query = count_query.where(where_clause)
                
            # Get total count
            count_result = await session.execute(count_query)
            total = count_result.scalar()
            
            # Apply ordering
            order_field = getattr(Solution, order_by, Solution.created_at)
            if order_desc:
                query = query.order_by(order_field.desc())
            else:
                query = query.order_by(order_field)
                
            # Apply pagination
            query = query.limit(limit).offset(offset)
            
            # Execute query
            result = await session.execute(query)
            solutions = result.scalars().all()
            
            return solutions, total
            
    async def increment_usage_count(self, solution_id: int):
        """
        Increment the usage count for a solution.
        
        Args:
            solution_id: Solution ID
        """
        async with get_db_session() as session:
            try:
                result = await session.execute(
                    select(Solution).where(Solution.id == solution_id)
                )
                solution = result.scalar_one_or_none()
                
                if solution:
                    solution.usage_count += 1
                    solution.last_accessed = datetime.utcnow()
                    await session.commit()
                    
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to increment usage count for solution {solution_id}: {e}")
                
    async def get_popular_solutions(self, limit: int = 10) -> List[Solution]:
        """
        Get most popular solutions by usage count.
        
        Args:
            limit: Maximum results
            
        Returns:
            List of popular solutions
        """
        async with get_db_session() as session:
            result = await session.execute(
                select(Solution)
                .order_by(Solution.usage_count.desc())
                .limit(limit)
            )
            return result.scalars().all()
            
    async def get_recent_solutions(self, limit: int = 10) -> List[Solution]:
        """
        Get recently added solutions.
        
        Args:
            limit: Maximum results
            
        Returns:
            List of recent solutions
        """
        async with get_db_session() as session:
            result = await session.execute(
                select(Solution)
                .order_by(Solution.created_at.desc())
                .limit(limit)
            )
            return result.scalars().all()
            
    async def search_by_capabilities(self, required_capabilities: List[str]) -> List[Solution]:
        """
        Find solutions that have all required capabilities.
        
        Args:
            required_capabilities: List of required capability keys
            
        Returns:
            List of matching solutions
        """
        async with get_db_session() as session:
            query = select(Solution)
            
            # Check each required capability
            for capability in required_capabilities:
                query = query.where(
                    func.json_extract(Solution.capabilities, f'$.{capability}').isnot(None)
                )
                
            result = await session.execute(query)
            return result.scalars().all()