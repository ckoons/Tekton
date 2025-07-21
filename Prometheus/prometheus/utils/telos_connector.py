"""
Telos Connector

This module provides a connector for interacting with the Telos requirements management component.
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
logger = logging.getLogger("prometheus.utils.telos_connector")


class TelosConnector:
    """
    Connector for interacting with the Telos requirements management component.
    """
    
    def __init__(self, telos_url: Optional[str] = None):
        """
        Initialize the Telos connector.
        
        Args:
            telos_url: URL of the Telos API (defaults to environment variable)
        """
        config = GlobalConfig()
        telos_port = config.get_port('telos')
        self.telos_url = telos_url or f"http://localhost:{telos_port}/api"
        self.initialized = False
        self.telos_client = None
    
    async def initialize(self) -> bool:
        """
        Initialize the connector.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        if self.initialized:
            return True
            
        try:
            # Try to import Telos client
            try:
                from telos.client import get_telos_client
                
                # Create client
                hermes_port = GlobalConfig().get_port('hermes')
                self.telos_client = await get_telos_client(hermes_url=f"http://localhost:{hermes_port}/api")
                self.initialized = True
                logger.info(f"Telos connector initialized with direct client")
                return True
                
            except ImportError:
                logger.warning("Could not import Telos client directly.")
                
                # Try to import from tekton-core
                try:
                    from tekton.utils.component_client import ComponentClient
                    
                    # Create client
                    hermes_port = GlobalConfig().get_port('hermes')
                    self.telos_client = ComponentClient(
                        component_id="telos.requirements",
                        hermes_url=f"http://localhost:{hermes_port}/api"
                    )
                    await self.telos_client.initialize()
                    self.initialized = True
                    logger.info(f"Telos connector initialized with component client")
                    return True
                    
                except ImportError:
                    logger.warning("Could not import component client from tekton-core.")
                    
                    # Fallback to HTTP client
                    import aiohttp
                    logger.info(f"Using direct HTTP connection to Telos at {self.telos_url}")
                    self.initialized = True
                    return True
                
        except Exception as e:
            logger.error(f"Error initializing Telos connector: {e}")
            return False
    
    async def get_requirements(self, project_id: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get requirements for a project.
        
        Args:
            project_id: ID of the project
            filters: Optional filters to apply
            
        Returns:
            List of requirements
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            if self.telos_client:
                # Use the client
                parameters = {"project_id": project_id}
                if filters:
                    parameters["filter"] = filters
                    
                result = await self.telos_client.invoke_capability("get_requirements", parameters)
                
                if isinstance(result, dict) and "requirements" in result:
                    return result["requirements"]
                else:
                    logger.error(f"Unexpected response format from Telos: {result}")
                    return []
            else:
                # Use direct HTTP request
                import aiohttp
                
                url = f"{self.telos_url}/projects/{project_id}/requirements"
                params = {}
                if filters:
                    params["filter"] = json.dumps(filters)
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            result = await response.json()
                            if "data" in result and "requirements" in result["data"]:
                                return result["data"]["requirements"]
                            else:
                                logger.error(f"Unexpected response format from Telos: {result}")
                                return []
                        else:
                            logger.error(f"Error getting requirements from Telos: {response.status}")
                            return []
        except Exception as e:
            logger.error(f"Error getting requirements from Telos: {e}")
            return []
    
    async def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a project.
        
        Args:
            project_id: ID of the project
            
        Returns:
            Project information or None if not found
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            if self.telos_client:
                # Use the client
                result = await self.telos_client.invoke_capability("get_project", {"project_id": project_id})
                
                if isinstance(result, dict) and "name" in result:
                    return result
                else:
                    logger.error(f"Unexpected response format from Telos: {result}")
                    return None
            else:
                # Use direct HTTP request
                import aiohttp
                
                url = f"{self.telos_url}/projects/{project_id}"
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            result = await response.json()
                            if "data" in result:
                                return result["data"]
                            else:
                                logger.error(f"Unexpected response format from Telos: {result}")
                                return None
                        else:
                            logger.error(f"Error getting project from Telos: {response.status}")
                            return None
        except Exception as e:
            logger.error(f"Error getting project from Telos: {e}")
            return None
    
    async def create_plan_from_requirements(self, project_id: str, plan_name: str, methodology: str) -> Dict[str, Any]:
        """
        Create a plan from requirements.
        
        Args:
            project_id: ID of the project
            plan_name: Name for the plan
            methodology: Methodology for the plan
            
        Returns:
            Plan data generated from requirements
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            # Get requirements
            requirements = await self.get_requirements(project_id)
            
            if not requirements:
                logger.warning(f"No requirements found for project {project_id}")
                return {"error": "No requirements found"}
                
            # Get project info
            project = await self.get_project(project_id)
            
            if not project:
                logger.warning(f"Project {project_id} not found")
                return {"error": "Project not found"}
                
            # Build plan
            from datetime import datetime, timedelta
            import uuid
            
            plan_id = f"plan-{uuid.uuid4()}"
            start_date = datetime.now()
            
            # In a real implementation, we would analyze requirements to generate a good plan
            # For now, use a simple algorithm
            
            # Calculate end date based on number of requirements
            days_per_requirement = 3
            total_days = len(requirements) * days_per_requirement
            end_date = start_date + timedelta(days=total_days)
            
            # Generate tasks from requirements
            tasks = {}
            for i, req in enumerate(requirements):
                task_id = f"task-{uuid.uuid4()}"
                
                # Simplified task creation
                task_start = start_date + timedelta(days=i * days_per_requirement)
                task_end = task_start + timedelta(days=days_per_requirement)
                
                tasks[task_id] = {
                    "task_id": task_id,
                    "name": f"Implement: {req.get('title', 'Requirement')}",
                    "description": req.get("description", ""),
                    "status": "not_started",
                    "priority": req.get("priority", "medium"),
                    "estimated_effort": days_per_requirement * 8,  # 8 hours per day
                    "actual_effort": 0.0,
                    "assigned_resources": [],
                    "dependencies": [],
                    "requirements": [req.get("requirement_id")],
                    "start_date": task_start.isoformat(),
                    "end_date": task_end.isoformat(),
                    "progress": 0.0,
                    "created_at": datetime.now().timestamp(),
                    "updated_at": datetime.now().timestamp()
                }
            
            # Generate milestones
            milestones = []
            
            # Start milestone
            milestones.append({
                "milestone_id": f"milestone-{uuid.uuid4()}",
                "name": "Project Start",
                "description": "Project initiation",
                "target_date": start_date.isoformat(),
                "status": "not_started",
                "actual_date": None,
                "created_at": datetime.now().timestamp(),
                "updated_at": datetime.now().timestamp()
            })
            
            # Mid milestone
            mid_date = start_date + timedelta(days=total_days // 2)
            milestones.append({
                "milestone_id": f"milestone-{uuid.uuid4()}",
                "name": "Mid-Project Review",
                "description": "Review progress at mid-point",
                "target_date": mid_date.isoformat(),
                "status": "not_started",
                "actual_date": None,
                "created_at": datetime.now().timestamp(),
                "updated_at": datetime.now().timestamp()
            })
            
            # End milestone
            milestones.append({
                "milestone_id": f"milestone-{uuid.uuid4()}",
                "name": "Project Completion",
                "description": "Project deliverables complete",
                "target_date": end_date.isoformat(),
                "status": "not_started",
                "actual_date": None,
                "created_at": datetime.now().timestamp(),
                "updated_at": datetime.now().timestamp()
            })
            
            # Create the plan
            plan = {
                "plan_id": plan_id,
                "name": plan_name,
                "description": f"Plan for project {project.get('name')} created from requirements",
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "methodology": methodology,
                "tasks": tasks,
                "milestones": milestones,
                "requirements": [req.get("requirement_id") for req in requirements],
                "metadata": {
                    "source": "telos",
                    "project_id": project_id,
                    "requirement_count": len(requirements)
                },
                "created_at": datetime.now().timestamp(),
                "updated_at": datetime.now().timestamp(),
                "version": 1
            }
            
            return plan
            
        except Exception as e:
            logger.error(f"Error creating plan from requirements: {e}")
            return {"error": str(e)}