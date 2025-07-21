"""
Rhetor LLM Adapter

This module provides an adapter for interacting with the Rhetor LLM component.
"""

import os
import sys
import logging
import json
from typing import Dict, List, Any, Optional
import asyncio

# Add Tekton root to path for shared imports
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if tekton_root not in sys.path:
    sys.path.append(tekton_root)

from shared.utils.global_config import GlobalConfig

# Configure logging
logger = logging.getLogger("prometheus.utils.rhetor_adapter")


class RhetorLLMAdapter:
    """
    Adapter for interacting with the Rhetor LLM component.
    """
    
    def __init__(self, rhetor_url: Optional[str] = None):
        """
        Initialize the Rhetor adapter.
        
        Args:
            rhetor_url: URL of the Rhetor API (defaults to environment variable)
        """
        config = GlobalConfig()
        rhetor_port = config.get_port('rhetor')
        self.rhetor_url = rhetor_url or f"http://localhost:{rhetor_port}/api"
        self.initialized = False
        self.rhetor_client = None
    
    async def initialize(self) -> bool:
        """
        Initialize the adapter.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        if self.initialized:
            return True
            
        try:
            # Try to import Rhetor client
            try:
                from rhetor.client import get_rhetor_prompt_client
                
                # Create client
                hermes_port = GlobalConfig().get_port('hermes')
                self.rhetor_client = await get_rhetor_prompt_client(hermes_url=f"http://localhost:{hermes_port}/api")
                self.initialized = True
                logger.info(f"Rhetor adapter initialized with direct client")
                return True
                
            except ImportError:
                logger.warning("Could not import Rhetor client directly.")
                
                # Try to import from tekton-core
                try:
                    from tekton.utils.component_client import ComponentClient
                    
                    # Create client
                    hermes_port = GlobalConfig().get_port('hermes')
                    self.rhetor_client = ComponentClient(
                        component_id="rhetor-prompt",
                        hermes_url=f"http://localhost:{hermes_port}/api"
                    )
                    await self.rhetor_client.initialize()
                    self.initialized = True
                    logger.info(f"Rhetor adapter initialized with component client")
                    return True
                    
                except ImportError:
                    logger.warning("Could not import component client from tekton-core.")
                    
                    # Fallback to HTTP client
                    import aiohttp
                    logger.info(f"Using direct HTTP connection to Rhetor at {self.rhetor_url}")
                    self.initialized = True
                    return True
                
        except Exception as e:
            logger.error(f"Error initializing Rhetor adapter: {e}")
            return False
    
    async def generate_prompt(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a prompt for a task.
        
        Args:
            task: Description of the task
            context: Optional context information
            
        Returns:
            Generated prompt
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            if self.rhetor_client:
                # Use the client
                parameters = {"task": task}
                if context:
                    parameters["context"] = context
                    
                result = await self.rhetor_client.invoke_capability("generate_prompt", parameters)
                
                if isinstance(result, dict) and "prompt" in result:
                    return result["prompt"]
                else:
                    logger.error(f"Unexpected response format from Rhetor: {result}")
                    return self._generate_fallback_prompt(task, context)
            else:
                # Use direct HTTP request
                import aiohttp
                
                url = f"{self.rhetor_url}/generate-prompt"
                data = {"task": task}
                if context:
                    data["context"] = context
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=data) as response:
                        if response.status == 200:
                            result = await response.json()
                            if "data" in result and "prompt" in result["data"]:
                                return result["data"]["prompt"]
                            else:
                                logger.error(f"Unexpected response format from Rhetor: {result}")
                                return self._generate_fallback_prompt(task, context)
                        else:
                            logger.error(f"Error generating prompt from Rhetor: {response.status}")
                            return self._generate_fallback_prompt(task, context)
        except Exception as e:
            logger.error(f"Error generating prompt from Rhetor: {e}")
            return self._generate_fallback_prompt(task, context)
    
    def _generate_fallback_prompt(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a fallback prompt if Rhetor is unavailable.
        
        Args:
            task: Description of the task
            context: Optional context information
            
        Returns:
            Fallback prompt
        """
        prompt = f"""
        Task: {task}
        
        """
        
        if context:
            prompt += "Context:\n"
            for key, value in context.items():
                prompt += f"- {key}: {value}\n"
        
        return prompt
    
    async def breakdown_tasks(self, requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Use LLM to breakdown requirements into tasks.
        
        Args:
            requirements: List of requirement data
            
        Returns:
            List of task data
        """
        if not self.initialized:
            await self.initialize()
            
        # Prepare input for LLM
        req_text = "\nRequirements:\n"
        for i, req in enumerate(requirements):
            req_text += f"{i+1}. {req.get('title', 'Requirement')}: {req.get('description', '')}\n"
        
        task_breakdown_prompt = f"""
        Given the following requirements, break them down into specific implementation tasks.
        For each task, provide the following:
        1. Task name
        2. Description
        3. Priority (high, medium, low)
        4. Estimated effort in hours
        5. Dependencies (references to other tasks)
        
        {req_text}
        
        Return the tasks in a structured format.
        """
        
        try:
            # Call LLM using Rhetor
            if self.rhetor_client:
                result = await self.rhetor_client.invoke_capability("analyze", {
                    "content": task_breakdown_prompt,
                    "analysis_type": "task_breakdown"
                })
                
                # Process result
                if isinstance(result, dict) and "analysis" in result:
                    return self._parse_task_breakdown(result["analysis"], requirements)
                else:
                    logger.error(f"Unexpected response format from Rhetor: {result}")
                    return self._generate_fallback_tasks(requirements)
            else:
                # Use direct HTTP request
                import aiohttp
                
                url = f"{self.rhetor_url}/analyze"
                data = {
                    "content": task_breakdown_prompt,
                    "analysis_type": "task_breakdown"
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=data) as response:
                        if response.status == 200:
                            result = await response.json()
                            if "data" in result and "analysis" in result["data"]:
                                return self._parse_task_breakdown(result["data"]["analysis"], requirements)
                            else:
                                logger.error(f"Unexpected response format from Rhetor: {result}")
                                return self._generate_fallback_tasks(requirements)
                        else:
                            logger.error(f"Error getting task breakdown from Rhetor: {response.status}")
                            return self._generate_fallback_tasks(requirements)
        except Exception as e:
            logger.error(f"Error getting task breakdown from Rhetor: {e}")
            return self._generate_fallback_tasks(requirements)
    
    def _parse_task_breakdown(self, analysis: str, requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Parse task breakdown from LLM response.
        
        Args:
            analysis: Analysis from LLM
            requirements: Original requirements list
            
        Returns:
            List of task data
        """
        # This is a placeholder implementation
        # In a real implementation, we would parse the LLM response to extract task data
        
        # For now, generate fallback tasks
        return self._generate_fallback_tasks(requirements)
    
    def _generate_fallback_tasks(self, requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate fallback tasks from requirements if LLM fails.
        
        Args:
            requirements: List of requirement data
            
        Returns:
            List of task data
        """
        import uuid
        from datetime import datetime
        
        tasks = []
        
        for req in requirements:
            # Generate a task ID
            task_id = f"task-{uuid.uuid4()}"
            
            # Create a task from the requirement
            tasks.append({
                "task_id": task_id,
                "name": f"Implement: {req.get('title', 'Requirement')}",
                "description": req.get("description", ""),
                "priority": req.get("priority", "medium"),
                "estimated_effort": 8.0,  # 8 hours default
                "dependencies": [],
                "requirements": [req.get("requirement_id")],
                "created_at": datetime.now().timestamp(),
                "updated_at": datetime.now().timestamp()
            })
        
        return tasks
    
    async def analyze_retrospective(self, retrospective_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use LLM to analyze retrospective data.
        
        Args:
            retrospective_data: Retrospective data
            
        Returns:
            Analysis results
        """
        if not self.initialized:
            await self.initialize()
            
        # Prepare input for LLM
        retro_text = f"""
        Retrospective: {retrospective_data.get('name', 'Retrospective')}
        Date: {retrospective_data.get('date', 'Unknown')}
        Format: {retrospective_data.get('format', 'Unknown')}
        
        Items:
        """
        
        # Group items by category
        items_by_category = {}
        for item in retrospective_data.get("items", []):
            category = item.get("category", "Uncategorized")
            if category not in items_by_category:
                items_by_category[category] = []
            items_by_category[category].append(item)
        
        # Add items to text
        for category, items in items_by_category.items():
            retro_text += f"\n{category}:\n"
            for item in items:
                votes = item.get("votes", 0)
                vote_str = f" (Votes: {votes})" if votes > 0 else ""
                retro_text += f"- {item.get('content', '')}{vote_str}\n"
        
        # Add action items to text
        if retrospective_data.get("action_items"):
            retro_text += "\nAction Items:\n"
            for action in retrospective_data.get("action_items", []):
                retro_text += f"- {action.get('title', '')}: {action.get('description', '')}\n"
        
        analysis_prompt = f"""
        Analyze the following retrospective data to identify patterns, root causes, and improvement opportunities.
        
        {retro_text}
        
        Provide the following in your analysis:
        1. Key themes and patterns identified
        2. Root causes of issues
        3. Strengths to maintain
        4. Opportunities for improvement
        5. Recommendations for future sprints/projects
        
        Return the analysis in a structured format.
        """
        
        try:
            # Call LLM using Rhetor
            if self.rhetor_client:
                result = await self.rhetor_client.invoke_capability("analyze", {
                    "content": analysis_prompt,
                    "analysis_type": "retrospective_analysis"
                })
                
                # Process result
                if isinstance(result, dict) and "analysis" in result:
                    return {
                        "retrospective_id": retrospective_data.get("retro_id"),
                        "analysis": result["analysis"],
                        "timestamp": result.get("timestamp")
                    }
                else:
                    logger.error(f"Unexpected response format from Rhetor: {result}")
                    return self._generate_fallback_retro_analysis(retrospective_data)
            else:
                # Use direct HTTP request
                import aiohttp
                
                url = f"{self.rhetor_url}/analyze"
                data = {
                    "content": analysis_prompt,
                    "analysis_type": "retrospective_analysis"
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=data) as response:
                        if response.status == 200:
                            result = await response.json()
                            if "data" in result and "analysis" in result["data"]:
                                return {
                                    "retrospective_id": retrospective_data.get("retro_id"),
                                    "analysis": result["data"]["analysis"],
                                    "timestamp": result["data"].get("timestamp")
                                }
                            else:
                                logger.error(f"Unexpected response format from Rhetor: {result}")
                                return self._generate_fallback_retro_analysis(retrospective_data)
                        else:
                            logger.error(f"Error getting retrospective analysis from Rhetor: {response.status}")
                            return self._generate_fallback_retro_analysis(retrospective_data)
        except Exception as e:
            logger.error(f"Error getting retrospective analysis from Rhetor: {e}")
            return self._generate_fallback_retro_analysis(retrospective_data)
    
    def _generate_fallback_retro_analysis(self, retrospective_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate fallback retrospective analysis if LLM fails.
        
        Args:
            retrospective_data: Retrospective data
            
        Returns:
            Fallback analysis
        """
        from datetime import datetime
        
        # Count items by category
        category_counts = {}
        for item in retrospective_data.get("items", []):
            category = item.get("category", "Uncategorized")
            if category not in category_counts:
                category_counts[category] = 0
            category_counts[category] += 1
        
        # Generate analysis text
        analysis = f"""
        # Retrospective Analysis
        
        ## Summary
        
        This retrospective had {len(retrospective_data.get('items', []))} items across {len(category_counts)} categories.
        
        ## Categories
        
        """
        
        for category, count in category_counts.items():
            analysis += f"- {category}: {count} items\n"
        
        analysis += "\n## Action Items\n\n"
        
        for action in retrospective_data.get("action_items", []):
            analysis += f"- {action.get('title', '')}\n"
        
        analysis += "\n## Recommendations\n\n"
        analysis += "1. Follow up on action items\n"
        analysis += "2. Address top voted issues\n"
        analysis += "3. Continue practices mentioned positively\n"
        
        return {
            "retrospective_id": retrospective_data.get("retro_id"),
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
    
    async def generate_improvements(self, performance_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Use LLM to generate improvement suggestions from performance data.
        
        Args:
            performance_data: Performance data
            
        Returns:
            List of improvement suggestions
        """
        if not self.initialized:
            await self.initialize()
            
        # Prepare input for LLM
        performance_text = f"""
        Performance Data:
        - Completion Rate: {performance_data.get('completion_rate', 0) * 100:.1f}%
        - Effort Variance: {performance_data.get('effort_variance', 0):.1f} hours
        """
        
        # Add task completion information
        if "task_completion" in performance_data:
            performance_text += "\n\nTask Completion:\n"
            for task_id, task_data in performance_data.get("task_completion", {}).items():
                performance_text += f"- {task_data.get('name', task_id)}: {task_data.get('actual_progress', 0) * 100:.1f}% complete\n"
        
        # Add milestone information
        if "milestone_achievement" in performance_data:
            performance_text += "\n\nMilestone Achievement:\n"
            for milestone_id, milestone_data in performance_data.get("milestone_achievement", {}).items():
                performance_text += f"- {milestone_data.get('name', milestone_id)}: {milestone_data.get('actual_status', 'unknown')}\n"
        
        improvement_prompt = f"""
        Based on the following performance data, suggest improvements that could enhance future project execution.
        
        {performance_text}
        
        Provide the following for each improvement suggestion:
        1. Title
        2. Description
        3. Priority (high, medium, low)
        4. Implementation plan
        5. Expected benefits
        
        Return 3-5 improvement suggestions in a structured format.
        """
        
        try:
            # Call LLM using Rhetor
            if self.rhetor_client:
                result = await self.rhetor_client.invoke_capability("analyze", {
                    "content": improvement_prompt,
                    "analysis_type": "improvement_suggestions"
                })
                
                # Process result
                if isinstance(result, dict) and "analysis" in result:
                    return self._parse_improvement_suggestions(result["analysis"])
                else:
                    logger.error(f"Unexpected response format from Rhetor: {result}")
                    return self._generate_fallback_improvements(performance_data)
            else:
                # Use direct HTTP request
                import aiohttp
                
                url = f"{self.rhetor_url}/analyze"
                data = {
                    "content": improvement_prompt,
                    "analysis_type": "improvement_suggestions"
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=data) as response:
                        if response.status == 200:
                            result = await response.json()
                            if "data" in result and "analysis" in result["data"]:
                                return self._parse_improvement_suggestions(result["data"]["analysis"])
                            else:
                                logger.error(f"Unexpected response format from Rhetor: {result}")
                                return self._generate_fallback_improvements(performance_data)
                        else:
                            logger.error(f"Error getting improvement suggestions from Rhetor: {response.status}")
                            return self._generate_fallback_improvements(performance_data)
        except Exception as e:
            logger.error(f"Error getting improvement suggestions from Rhetor: {e}")
            return self._generate_fallback_improvements(performance_data)
    
    def _parse_improvement_suggestions(self, analysis: str) -> List[Dict[str, Any]]:
        """
        Parse improvement suggestions from LLM response.
        
        Args:
            analysis: Analysis from LLM
            
        Returns:
            List of improvement suggestions
        """
        # This is a placeholder implementation
        # In a real implementation, we would parse the LLM response
        
        # For now, generate fallback improvements
        return self._generate_fallback_improvements({})
    
    def _generate_fallback_improvements(self, performance_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate fallback improvement suggestions if LLM fails.
        
        Args:
            performance_data: Performance data
            
        Returns:
            List of improvement suggestions
        """
        import uuid
        from datetime import datetime
        
        improvements = []
        
        # Generate some generic improvements
        improvements.append({
            "improvement_id": f"improvement-{uuid.uuid4()}",
            "title": "Enhance Task Estimation",
            "description": "Improve the process of estimating task effort to reduce variance.",
            "source": "performance_analysis",
            "priority": "high",
            "implementation_plan": "1. Review historical data\n2. Train team on estimation techniques\n3. Implement planning poker\n4. Review and adjust",
            "verification_criteria": "Reduced variance between estimated and actual effort",
            "tags": ["estimation", "planning"],
            "created_at": datetime.now().timestamp(),
            "updated_at": datetime.now().timestamp()
        })
        
        improvements.append({
            "improvement_id": f"improvement-{uuid.uuid4()}",
            "title": "Implement Regular Progress Reviews",
            "description": "Conduct regular progress reviews to identify and address issues early.",
            "source": "performance_analysis",
            "priority": "medium",
            "implementation_plan": "1. Schedule weekly reviews\n2. Create dashboard\n3. Define escalation process\n4. Monitor and adjust",
            "verification_criteria": "Issues identified and addressed earlier in the project lifecycle",
            "tags": ["monitoring", "process"],
            "created_at": datetime.now().timestamp(),
            "updated_at": datetime.now().timestamp()
        })
        
        improvements.append({
            "improvement_id": f"improvement-{uuid.uuid4()}",
            "title": "Refine Dependency Management",
            "description": "Improve the identification and management of task dependencies.",
            "source": "performance_analysis",
            "priority": "medium",
            "implementation_plan": "1. Update planning process\n2. Create dependency visualization\n3. Implement early alerts for dependency risks",
            "verification_criteria": "Fewer delays caused by unexpected dependencies",
            "tags": ["dependencies", "planning"],
            "created_at": datetime.now().timestamp(),
            "updated_at": datetime.now().timestamp()
        })
        
        return improvements