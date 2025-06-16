#!/usr/bin/env python3
"""
Task Decomposer for Metis

This module implements AI-powered task decomposition functionality,
breaking down high-level tasks into manageable subtasks.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from uuid import uuid4

from metis.core.llm_adapter import MetisLLMAdapter
from metis.models.task import Task
from metis.models.subtask import Subtask
from metis.models.enums import TaskStatus, Priority
from metis.models.complexity import ComplexityScore

logger = logging.getLogger("metis.task_decomposer")

class TaskDecomposer:
    """
    AI-powered task decomposition engine.
    
    This class handles the intelligent breakdown of tasks into subtasks
    using LLM capabilities.
    """
    
    def __init__(self, llm_adapter: Optional[MetisLLMAdapter] = None):
        """
        Initialize the task decomposer.
        
        Args:
            llm_adapter: LLM adapter instance (creates new if not provided)
        """
        self.llm_adapter = llm_adapter or MetisLLMAdapter()
        logger.info("Task decomposer initialized")
    
    async def decompose_task(self,
                           task: Task,
                           depth: int = 2,
                           max_subtasks: int = 10,
                           auto_create: bool = True) -> Dict[str, Any]:
        """
        Decompose a task into subtasks using AI.
        
        Args:
            task: The task to decompose
            depth: Maximum decomposition depth (1-5)
            max_subtasks: Maximum subtasks to create (1-20)
            auto_create: Whether to automatically create subtasks
            
        Returns:
            Dictionary containing decomposition results
        """
        # Validate parameters
        depth = max(1, min(5, depth))
        max_subtasks = max(1, min(20, max_subtasks))
        
        try:
            # Call LLM adapter to decompose
            result = await self.llm_adapter.decompose_task(
                task_title=task.title,
                task_description=task.description or "",
                depth=depth,
                max_subtasks=max_subtasks
            )
            
            if not result.get("success"):
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "task_id": task.id
                }
            
            # Process the subtasks
            created_subtasks = []
            if auto_create and result.get("subtasks"):
                for idx, subtask_data in enumerate(result["subtasks"]):
                    subtask = self._create_subtask_from_data(
                        task_id=task.id,
                        subtask_data=subtask_data,
                        order=idx + 1
                    )
                    created_subtasks.append(subtask)
            
            return {
                "success": True,
                "task_id": task.id,
                "subtasks": created_subtasks if auto_create else result.get("subtasks", []),
                "depth": depth,
                "model": result.get("model"),
                "provider": result.get("provider"),
                "timestamp": result.get("timestamp"),
                "auto_created": auto_create
            }
            
        except Exception as e:
            logger.error(f"Task decomposition failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "task_id": task.id
            }
    
    def _create_subtask_from_data(self,
                                task_id: str,
                                subtask_data: Dict[str, Any],
                                order: int) -> Subtask:
        """
        Create a Subtask object from decomposition data.
        
        Args:
            task_id: Parent task ID
            subtask_data: Subtask data from LLM
            order: Execution order
            
        Returns:
            Subtask object
        """
        # Map complexity strings to enum
        complexity_map = {
            "low": 1,
            "medium": 5,
            "high": 8,
            "critical": 10
        }
        
        complexity_value = complexity_map.get(
            subtask_data.get("complexity", "medium").lower(),
            5
        )
        
        # Create complexity score
        complexity = ComplexityScore(
            technical_complexity=complexity_value,
            time_complexity=subtask_data.get("estimated_hours", 1),
            dependency_complexity=len(subtask_data.get("dependencies", [])),
            overall_score=complexity_value
        )
        
        # Create subtask
        subtask = Subtask(
            id=str(uuid4()),
            parent_task_id=task_id,
            title=subtask_data.get("title", f"Subtask {order}"),
            description=subtask_data.get("description", ""),
            estimated_hours=subtask_data.get("estimated_hours", 1),
            order=subtask_data.get("order", order),
            complexity=complexity,
            status=TaskStatus.PENDING
        )
        
        return subtask
    
    async def analyze_decomposition_quality(self,
                                          task: Task,
                                          subtasks: List[Subtask]) -> Dict[str, Any]:
        """
        Analyze the quality of a task decomposition.
        
        Args:
            task: The parent task
            subtasks: List of subtasks
            
        Returns:
            Quality analysis results
        """
        try:
            # Calculate metrics
            total_hours = sum(st.estimated_hours for st in subtasks)
            avg_complexity = sum(st.complexity.overall_score for st in subtasks) / len(subtasks) if subtasks else 0
            
            analysis = {
                "task_id": task.id,
                "subtask_count": len(subtasks),
                "total_estimated_hours": total_hours,
                "average_complexity": avg_complexity,
                "coverage": self._assess_coverage(task, subtasks),
                "granularity": self._assess_granularity(subtasks),
                "balance": self._assess_balance(subtasks),
                "quality_score": 0.0,
                "recommendations": []
            }
            
            # Calculate quality score
            quality_score = (
                analysis["coverage"] * 0.4 +
                analysis["granularity"] * 0.3 +
                analysis["balance"] * 0.3
            )
            analysis["quality_score"] = round(quality_score, 2)
            
            # Generate recommendations
            if analysis["coverage"] < 0.7:
                analysis["recommendations"].append(
                    "Consider adding more subtasks to fully cover the task scope"
                )
            if analysis["granularity"] < 0.7:
                analysis["recommendations"].append(
                    "Some subtasks may be too broad - consider breaking them down further"
                )
            if analysis["balance"] < 0.7:
                analysis["recommendations"].append(
                    "Subtask complexity/effort is imbalanced - consider redistributing work"
                )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Decomposition analysis failed: {str(e)}")
            return {
                "task_id": task.id,
                "error": str(e),
                "quality_score": 0.0
            }
    
    def _assess_coverage(self, task: Task, subtasks: List[Subtask]) -> float:
        """Assess how well subtasks cover the parent task scope."""
        if not subtasks:
            return 0.0
        
        # Simple heuristic based on description overlap
        task_words = set((task.description or "").lower().split())
        subtask_words = set()
        for st in subtasks:
            subtask_words.update((st.description or "").lower().split())
        
        if not task_words:
            return 0.8  # Default if no description
        
        overlap = len(task_words & subtask_words) / len(task_words)
        return min(1.0, overlap * 1.5)  # Scale up slightly
    
    def _assess_granularity(self, subtasks: List[Subtask]) -> float:
        """Assess if subtasks are appropriately sized."""
        if not subtasks:
            return 0.0
        
        # Check if subtasks have reasonable time estimates
        good_estimates = sum(
            1 for st in subtasks
            if 0.5 <= st.estimated_hours <= 8
        )
        
        return good_estimates / len(subtasks)
    
    def _assess_balance(self, subtasks: List[Subtask]) -> float:
        """Assess if subtasks are well-balanced in effort."""
        if not subtasks:
            return 0.0
        
        hours = [st.estimated_hours for st in subtasks]
        if len(hours) < 2:
            return 1.0
        
        # Calculate coefficient of variation
        mean_hours = sum(hours) / len(hours)
        if mean_hours == 0:
            return 1.0
        
        variance = sum((h - mean_hours) ** 2 for h in hours) / len(hours)
        std_dev = variance ** 0.5
        cv = std_dev / mean_hours
        
        # Lower CV is better (more balanced)
        # CV of 0 = perfect balance, CV > 1 = high imbalance
        return max(0.0, min(1.0, 1.0 - cv))