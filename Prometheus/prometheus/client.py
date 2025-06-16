"""
Prometheus/Epimethius Client

Client for interacting with the Prometheus/Epimethius Planning System.
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

import aiohttp
from aiohttp import ClientSession, ClientTimeout

logger = logging.getLogger("prometheus.client")

class PrometheusClient:
    """
    Client for the Prometheus/Epimethius Planning System.
    
    This client provides methods for interacting with both the forward-looking
    planning (Prometheus) and retrospective analysis (Epimethius) capabilities.
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        session: Optional[ClientSession] = None,
        timeout: int = 60,
        max_retries: int = 3,
        retry_delay: int = 1
    ):
        """
        Initialize the Prometheus/Epimethius client.
        
        Args:
            base_url: Base URL for the Prometheus/Epimethius API (default: from GlobalConfig)
            session: aiohttp ClientSession (a new one will be created if not provided)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            retry_delay: Delay between retries in seconds
        """
        # Set up base URL using GlobalConfig if not provided
        if base_url is None:
            try:
                from shared.utils.global_config import GlobalConfig
                global_config = GlobalConfig.get_instance()
                prometheus_url = global_config.get_service_url('prometheus')
                self.base_url = f"{prometheus_url}/api"
            except:
                # Fallback if GlobalConfig not available
                self.base_url = "http://localhost:8006/api"
        else:
            self.base_url = base_url
        
        # Ensure base_url ends with /
        if not self.base_url.endswith("/"):
            self.base_url += "/"
        
        # Set up session
        self._session = session
        self._own_session = session is None
        self._timeout = timeout
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        
        logger.debug(f"Initialized Prometheus/Epimethius client with base URL: {self.base_url}")
    
    async def _get_session(self) -> ClientSession:
        """
        Get the aiohttp session, creating a new one if necessary.
        
        Returns:
            aiohttp ClientSession
        """
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=ClientTimeout(total=self._timeout)
            )
            self._own_session = True
        
        return self._session
    
    async def close(self):
        """Close the aiohttp session if it was created by this client."""
        if self._own_session and self._session and not self._session.closed:
            await self._session.close()
            self._session = None
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make a request to the Prometheus/Epimethius API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            params: Query parameters
            data: Request body
            headers: HTTP headers
            
        Returns:
            Response data as dictionary
            
        Raises:
            aiohttp.ClientError: If the request fails
        """
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        
        _headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if headers:
            _headers.update(headers)
        
        retries = 0
        while True:
            try:
                if method == "GET":
                    async with session.get(url, params=params, headers=_headers) as response:
                        response.raise_for_status()
                        return await response.json()
                elif method == "POST":
                    async with session.post(url, params=params, json=data, headers=_headers) as response:
                        response.raise_for_status()
                        return await response.json()
                elif method == "PUT":
                    async with session.put(url, params=params, json=data, headers=_headers) as response:
                        response.raise_for_status()
                        return await response.json()
                elif method == "DELETE":
                    async with session.delete(url, params=params, headers=_headers) as response:
                        response.raise_for_status()
                        return await response.json()
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
            
            except aiohttp.ClientError as e:
                retries += 1
                if retries > self._max_retries:
                    logger.error(f"Failed to {method} {url} after {retries} retries: {e}")
                    raise
                
                logger.warning(f"Request failed ({retries}/{self._max_retries}), retrying in {self._retry_delay}s: {e}")
                await asyncio.sleep(self._retry_delay)
    
    # Health check
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the Prometheus/Epimethius service.
        
        Returns:
            Health check response
        """
        return await self._request("GET", "health")
    
    # Prometheus (Forward Planning) Methods
    
    async def create_plan(
        self,
        name: str,
        description: str,
        start_date: str,
        end_date: str,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new plan.
        
        Args:
            name: Plan name
            description: Plan description
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            tags: List of tags
            metadata: Additional metadata
            
        Returns:
            Plan ID
        """
        data = {
            "name": name,
            "description": description,
            "start_date": start_date,
            "end_date": end_date,
            "tags": tags or [],
            "metadata": metadata or {}
        }
        
        response = await self._request("POST", "plans", data=data)
        return response["plan_id"]
    
    async def get_plan(self, plan_id: str) -> Dict[str, Any]:
        """
        Get a plan by ID.
        
        Args:
            plan_id: Plan ID
            
        Returns:
            Plan details
        """
        return await self._request("GET", f"plans/{plan_id}")
    
    async def update_plan(
        self,
        plan_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update a plan.
        
        Args:
            plan_id: Plan ID
            name: New plan name
            description: New plan description
            start_date: New start date (ISO format)
            end_date: New end date (ISO format)
            tags: New list of tags
            metadata: New additional metadata
            
        Returns:
            Updated plan details
        """
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if start_date is not None:
            data["start_date"] = start_date
        if end_date is not None:
            data["end_date"] = end_date
        if tags is not None:
            data["tags"] = tags
        if metadata is not None:
            data["metadata"] = metadata
        
        return await self._request("PUT", f"plans/{plan_id}", data=data)
    
    async def delete_plan(self, plan_id: str) -> Dict[str, Any]:
        """
        Delete a plan.
        
        Args:
            plan_id: Plan ID
            
        Returns:
            Deletion status
        """
        return await self._request("DELETE", f"plans/{plan_id}")
    
    async def list_plans(
        self,
        limit: int = 100,
        offset: int = 0,
        tag: Optional[str] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List plans.
        
        Args:
            limit: Maximum number of plans to return
            offset: Offset for pagination
            tag: Filter by tag
            search: Search term
            
        Returns:
            List of plans
        """
        params = {
            "limit": limit,
            "offset": offset
        }
        if tag:
            params["tag"] = tag
        if search:
            params["search"] = search
        
        return await self._request("GET", "plans", params=params)
    
    async def add_task(
        self,
        plan_id: str,
        name: str,
        description: str,
        duration: float,
        duration_unit: str = "days",
        assigned_to: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        status: str = "pending",
        priority: str = "medium",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a task to a plan.
        
        Args:
            plan_id: Plan ID
            name: Task name
            description: Task description
            duration: Task duration
            duration_unit: Duration unit (days, hours, etc.)
            assigned_to: Resource ID assigned to the task
            dependencies: List of task IDs that this task depends on
            status: Task status (pending, in_progress, completed, blocked)
            priority: Task priority (low, medium, high, critical)
            tags: List of tags
            metadata: Additional metadata
            
        Returns:
            Task ID
        """
        data = {
            "name": name,
            "description": description,
            "duration": duration,
            "duration_unit": duration_unit,
            "status": status,
            "priority": priority,
            "tags": tags or [],
            "metadata": metadata or {}
        }
        
        if assigned_to is not None:
            data["assigned_to"] = assigned_to
        
        if dependencies is not None:
            data["dependencies"] = dependencies
        
        response = await self._request("POST", f"plans/{plan_id}/tasks", data=data)
        return response["task_id"]
    
    async def update_task(
        self,
        plan_id: str,
        task_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        duration: Optional[float] = None,
        duration_unit: Optional[str] = None,
        assigned_to: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update a task.
        
        Args:
            plan_id: Plan ID
            task_id: Task ID
            name: New task name
            description: New task description
            duration: New task duration
            duration_unit: New duration unit
            assigned_to: New resource ID assigned to the task
            dependencies: New list of task IDs that this task depends on
            status: New task status
            priority: New task priority
            tags: New list of tags
            metadata: New additional metadata
            
        Returns:
            Updated task details
        """
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if duration is not None:
            data["duration"] = duration
        if duration_unit is not None:
            data["duration_unit"] = duration_unit
        if assigned_to is not None:
            data["assigned_to"] = assigned_to
        if dependencies is not None:
            data["dependencies"] = dependencies
        if status is not None:
            data["status"] = status
        if priority is not None:
            data["priority"] = priority
        if tags is not None:
            data["tags"] = tags
        if metadata is not None:
            data["metadata"] = metadata
        
        return await self._request("PUT", f"plans/{plan_id}/tasks/{task_id}", data=data)
    
    async def get_task(self, plan_id: str, task_id: str) -> Dict[str, Any]:
        """
        Get a task by ID.
        
        Args:
            plan_id: Plan ID
            task_id: Task ID
            
        Returns:
            Task details
        """
        return await self._request("GET", f"plans/{plan_id}/tasks/{task_id}")
    
    async def delete_task(self, plan_id: str, task_id: str) -> Dict[str, Any]:
        """
        Delete a task.
        
        Args:
            plan_id: Plan ID
            task_id: Task ID
            
        Returns:
            Deletion status
        """
        return await self._request("DELETE", f"plans/{plan_id}/tasks/{task_id}")
    
    async def list_tasks(
        self,
        plan_id: str,
        limit: int = 100,
        offset: int = 0,
        status: Optional[str] = None,
        assigned_to: Optional[str] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List tasks in a plan.
        
        Args:
            plan_id: Plan ID
            limit: Maximum number of tasks to return
            offset: Offset for pagination
            status: Filter by status
            assigned_to: Filter by assigned resource
            search: Search term
            
        Returns:
            List of tasks
        """
        params = {
            "limit": limit,
            "offset": offset
        }
        if status:
            params["status"] = status
        if assigned_to:
            params["assigned_to"] = assigned_to
        if search:
            params["search"] = search
        
        return await self._request("GET", f"plans/{plan_id}/tasks", params=params)
    
    async def update_task_progress(
        self,
        plan_id: str,
        task_id: str,
        status: str,
        actual_start_date: Optional[str] = None,
        actual_end_date: Optional[str] = None,
        actual_duration: Optional[float] = None,
        actual_duration_unit: Optional[str] = None,
        completion_percentage: Optional[float] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update task progress.
        
        Args:
            plan_id: Plan ID
            task_id: Task ID
            status: Task status (pending, in_progress, completed, blocked)
            actual_start_date: Actual start date (ISO format)
            actual_end_date: Actual end date (ISO format)
            actual_duration: Actual duration
            actual_duration_unit: Actual duration unit
            completion_percentage: Completion percentage (0-100)
            notes: Progress notes
            
        Returns:
            Updated task details
        """
        data = {
            "status": status
        }
        
        if actual_start_date is not None:
            data["actual_start_date"] = actual_start_date
        
        if actual_end_date is not None:
            data["actual_end_date"] = actual_end_date
        
        if actual_duration is not None:
            data["actual_duration"] = actual_duration
        
        if actual_duration_unit is not None:
            data["actual_duration_unit"] = actual_duration_unit
        
        if completion_percentage is not None:
            data["completion_percentage"] = completion_percentage
        
        if notes is not None:
            data["notes"] = notes
        
        return await self._request("PUT", f"plans/{plan_id}/tasks/{task_id}/progress", data=data)
    
    async def add_resource(
        self,
        plan_id: str,
        name: str,
        type: str,
        skills: Optional[List[str]] = None,
        availability: float = 1.0,
        cost_rate: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a resource to a plan.
        
        Args:
            plan_id: Plan ID
            name: Resource name
            type: Resource type (human, equipment, etc.)
            skills: List of skills
            availability: Availability (0.0 to 1.0, where 1.0 is full-time)
            cost_rate: Cost rate
            metadata: Additional metadata
            
        Returns:
            Resource ID
        """
        data = {
            "name": name,
            "type": type,
            "skills": skills or [],
            "availability": availability,
            "metadata": metadata or {}
        }
        
        if cost_rate is not None:
            data["cost_rate"] = cost_rate
        
        response = await self._request("POST", f"plans/{plan_id}/resources", data=data)
        return response["resource_id"]
    
    async def update_resource(
        self,
        plan_id: str,
        resource_id: str,
        name: Optional[str] = None,
        type: Optional[str] = None,
        skills: Optional[List[str]] = None,
        availability: Optional[float] = None,
        cost_rate: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update a resource.
        
        Args:
            plan_id: Plan ID
            resource_id: Resource ID
            name: New resource name
            type: New resource type
            skills: New list of skills
            availability: New availability
            cost_rate: New cost rate
            metadata: New additional metadata
            
        Returns:
            Updated resource details
        """
        data = {}
        if name is not None:
            data["name"] = name
        if type is not None:
            data["type"] = type
        if skills is not None:
            data["skills"] = skills
        if availability is not None:
            data["availability"] = availability
        if cost_rate is not None:
            data["cost_rate"] = cost_rate
        if metadata is not None:
            data["metadata"] = metadata
        
        return await self._request("PUT", f"plans/{plan_id}/resources/{resource_id}", data=data)
    
    async def get_resource(self, plan_id: str, resource_id: str) -> Dict[str, Any]:
        """
        Get a resource by ID.
        
        Args:
            plan_id: Plan ID
            resource_id: Resource ID
            
        Returns:
            Resource details
        """
        return await self._request("GET", f"plans/{plan_id}/resources/{resource_id}")
    
    async def delete_resource(self, plan_id: str, resource_id: str) -> Dict[str, Any]:
        """
        Delete a resource.
        
        Args:
            plan_id: Plan ID
            resource_id: Resource ID
            
        Returns:
            Deletion status
        """
        return await self._request("DELETE", f"plans/{plan_id}/resources/{resource_id}")
    
    async def list_resources(
        self,
        plan_id: str,
        limit: int = 100,
        offset: int = 0,
        type: Optional[str] = None,
        skill: Optional[str] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List resources in a plan.
        
        Args:
            plan_id: Plan ID
            limit: Maximum number of resources to return
            offset: Offset for pagination
            type: Filter by type
            skill: Filter by skill
            search: Search term
            
        Returns:
            List of resources
        """
        params = {
            "limit": limit,
            "offset": offset
        }
        if type:
            params["type"] = type
        if skill:
            params["skill"] = skill
        if search:
            params["search"] = search
        
        return await self._request("GET", f"plans/{plan_id}/resources", params=params)
    
    async def calculate_critical_path(self, plan_id: str) -> Dict[str, Any]:
        """
        Calculate the critical path for a plan.
        
        Args:
            plan_id: Plan ID
            
        Returns:
            Critical path analysis
        """
        return await self._request("GET", f"plans/{plan_id}/critical-path")
    
    async def generate_timeline(
        self,
        plan_id: str,
        format: str = "default",
        include_resources: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a timeline for a plan.
        
        Args:
            plan_id: Plan ID
            format: Timeline format (default, gantt, etc.)
            include_resources: Whether to include resources in the timeline
            
        Returns:
            Timeline data
        """
        params = {
            "format": format,
            "include_resources": str(include_resources).lower()
        }
        
        return await self._request("GET", f"plans/{plan_id}/timeline", params=params)
    
    async def get_plan_summary(self, plan_id: str) -> Dict[str, Any]:
        """
        Get a summary of a plan.
        
        Args:
            plan_id: Plan ID
            
        Returns:
            Plan summary
        """
        return await self._request("GET", f"plans/{plan_id}/summary")
    
    async def generate_plan_analysis(self, plan_id: str) -> Dict[str, Any]:
        """
        Generate an LLM-powered analysis of a plan.
        
        Args:
            plan_id: Plan ID
            
        Returns:
            Plan analysis
        """
        return await self._request("GET", f"plans/{plan_id}/analysis")
    
    # Epimethius (Retrospective Analysis) Methods
    
    async def create_retrospective(
        self,
        plan_id: str,
        name: str,
        description: str,
        date: str,
        participants: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a retrospective for a plan.
        
        Args:
            plan_id: Plan ID
            name: Retrospective name
            description: Retrospective description
            date: Retrospective date (ISO format)
            participants: List of participant names
            tags: List of tags
            metadata: Additional metadata
            
        Returns:
            Retrospective ID
        """
        data = {
            "plan_id": plan_id,
            "name": name,
            "description": description,
            "date": date,
            "participants": participants or [],
            "tags": tags or [],
            "metadata": metadata or {}
        }
        
        response = await self._request("POST", "retrospectives", data=data)
        return response["retrospective_id"]
    
    async def get_retrospective(self, retrospective_id: str) -> Dict[str, Any]:
        """
        Get a retrospective by ID.
        
        Args:
            retrospective_id: Retrospective ID
            
        Returns:
            Retrospective details
        """
        return await self._request("GET", f"retrospectives/{retrospective_id}")
    
    async def list_retrospectives(
        self,
        plan_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        tag: Optional[str] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List retrospectives.
        
        Args:
            plan_id: Filter by plan ID
            limit: Maximum number of retrospectives to return
            offset: Offset for pagination
            tag: Filter by tag
            search: Search term
            
        Returns:
            List of retrospectives
        """
        params = {
            "limit": limit,
            "offset": offset
        }
        if plan_id:
            params["plan_id"] = plan_id
        if tag:
            params["tag"] = tag
        if search:
            params["search"] = search
        
        return await self._request("GET", "retrospectives", params=params)
    
    async def add_retrospective_feedback(
        self,
        retrospective_id: str,
        type: str,
        description: str,
        source: Optional[str] = None,
        priority: str = "medium",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add feedback to a retrospective.
        
        Args:
            retrospective_id: Retrospective ID
            type: Feedback type (positive, negative, neutral)
            description: Feedback description
            source: Feedback source (who provided it)
            priority: Feedback priority (low, medium, high)
            metadata: Additional metadata
            
        Returns:
            Feedback ID
        """
        data = {
            "type": type,
            "description": description,
            "priority": priority,
            "metadata": metadata or {}
        }
        
        if source is not None:
            data["source"] = source
        
        response = await self._request("POST", f"retrospectives/{retrospective_id}/feedback", data=data)
        return response["feedback_id"]
    
    async def get_retrospective_feedback(
        self,
        retrospective_id: str,
        feedback_id: str
    ) -> Dict[str, Any]:
        """
        Get feedback by ID.
        
        Args:
            retrospective_id: Retrospective ID
            feedback_id: Feedback ID
            
        Returns:
            Feedback details
        """
        return await self._request(
            "GET",
            f"retrospectives/{retrospective_id}/feedback/{feedback_id}"
        )
    
    async def list_retrospective_feedback(
        self,
        retrospective_id: str,
        type: Optional[str] = None,
        source: Optional[str] = None,
        priority: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List feedback for a retrospective.
        
        Args:
            retrospective_id: Retrospective ID
            type: Filter by feedback type
            source: Filter by feedback source
            priority: Filter by feedback priority
            
        Returns:
            List of feedback
        """
        params = {}
        if type:
            params["type"] = type
        if source:
            params["source"] = source
        if priority:
            params["priority"] = priority
        
        return await self._request(
            "GET",
            f"retrospectives/{retrospective_id}/feedback",
            params=params
        )
    
    async def generate_variance_analysis(self, plan_id: str) -> Dict[str, Any]:
        """
        Generate variance analysis for a plan.
        
        Args:
            plan_id: Plan ID
            
        Returns:
            Variance analysis
        """
        return await self._request("GET", f"plans/{plan_id}/variance-analysis")
    
    async def generate_performance_metrics(self, plan_id: str) -> Dict[str, Any]:
        """
        Generate performance metrics for a plan.
        
        Args:
            plan_id: Plan ID
            
        Returns:
            Performance metrics
        """
        return await self._request("GET", f"plans/{plan_id}/performance-metrics")
    
    async def generate_improvement_suggestions(
        self,
        retrospective_id: str,
        max_suggestions: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Generate improvement suggestions based on a retrospective.
        
        Args:
            retrospective_id: Retrospective ID
            max_suggestions: Maximum number of suggestions to generate
            
        Returns:
            List of improvement suggestions
        """
        params = {
            "max_suggestions": max_suggestions
        }
        
        response = await self._request(
            "GET",
            f"retrospectives/{retrospective_id}/improvement-suggestions",
            params=params
        )
        
        return response["suggestions"]
    
    async def generate_retrospective_summary(
        self,
        retrospective_id: str
    ) -> Dict[str, Any]:
        """
        Generate an LLM-powered summary of a retrospective.
        
        Args:
            retrospective_id: Retrospective ID
            
        Returns:
            Retrospective summary
        """
        return await self._request("GET", f"retrospectives/{retrospective_id}/summary")


async def get_prometheus_client(
    base_url: Optional[str] = None,
    component_id: str = "prometheus.planning"
) -> PrometheusClient:
    """
    Get a Prometheus/Epimethius client, optionally discovering the service via Hermes.
    
    Args:
        base_url: Base URL for the Prometheus/Epimethius API
        component_id: Component ID for service discovery
        
    Returns:
        PrometheusClient instance
        
    Raises:
        ValueError: If the service couldn't be found
    """
    # If base_url is provided, use it directly
    if base_url:
        return PrometheusClient(base_url=base_url)
    
    # Try to get the URL using GlobalConfig
    try:
        from shared.utils.global_config import GlobalConfig
        global_config = GlobalConfig.get_instance()
        prometheus_url = global_config.get_service_url('prometheus')
        return PrometheusClient(base_url=f"{prometheus_url}/api")
    except:
        pass
    
    # Try to discover the service via Hermes
    try:
        # Import Hermes client (with fallback to direct import)
        try:
            from tekton.utils.component_client import get_component_endpoint
        except ImportError:
            try:
                from hermes.api.client import HermesClient
            except ImportError:
                logger.warning("Hermes client not available. Using default URL.")
                return PrometheusClient()
        
        # Try to get the endpoint from Hermes
        hermes_url = os.environ.get("HERMES_URL", "http://localhost:8000/api")
        
        if "get_component_endpoint" in locals():
            # Use Tekton utility
            endpoint = await get_component_endpoint(component_id, hermes_url)
            if endpoint:
                return PrometheusClient(base_url=endpoint)
        else:
            # Use Hermes client directly
            async with HermesClient(hermes_url) as hermes:
                component = await hermes.get_component(component_id)
                if component and "endpoint" in component:
                    return PrometheusClient(base_url=component["endpoint"])
        
        # If we got here, discovery failed
        logger.warning(f"Could not discover {component_id} via Hermes. Using default URL.")
        return PrometheusClient()
    
    except Exception as e:
        logger.warning(f"Error during service discovery: {e}. Using default URL.")
        return PrometheusClient()