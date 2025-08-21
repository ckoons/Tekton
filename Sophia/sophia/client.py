"""
Sophia Client

This module provides a client for interacting with the Sophia API.
"""

import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

import httpx

# Import shared utilities if available
try:
    from sophia.utils.tekton_utils import get_config, get_logger, create_http_client
    logger = get_logger("sophia.client")
except ImportError:
    # Fallback to standard logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger("sophia.client")

# Import shared URL builder
try:
    from shared.urls import sophia_url
except ImportError:
    sophia_url = None

class SophiaClient:
    """
    Client for interacting with the Sophia API.
    
    This client provides methods for accessing Sophia's capabilities, including
    metrics collection, experiment management, recommendation management,
    intelligence measurement, and component analysis.
    """
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize the Sophia client.
        
        Args:
            base_url: Base URL for the Sophia API (defaults to SOPHIA_API_URL env variable or http://localhost:8006)
        """
        # Use shared utilities to get configuration if available
        try:
            if base_url:
                self.base_url = base_url
            elif sophia_url:
                self.base_url = sophia_url("")
            else:
                self.base_url = get_config("SOPHIA_API_URL", "http://localhost:8014")
            # Try to use tekton_http shared utility to create client
            self.client = create_http_client(
                base_url=self.base_url,
                timeout=30.0,
                headers={"Content-Type": "application/json"}
            )
            # If client creation failed, use httpx directly
            if self.client is None:
                self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
                logger.info(f"Using httpx client with base URL: {self.base_url}")
            else:
                logger.info(f"Using tekton_http client with base URL: {self.base_url}")
        except ImportError:
            # Fallback to direct httpx usage
            if base_url:
                self.base_url = base_url
            elif sophia_url:
                self.base_url = sophia_url("")
            else:
                self.base_url = "http://localhost:8014"
            self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
            logger.info(f"Using httpx client with base URL: {self.base_url}")
        
    async def close(self):
        """Close the client session."""
        if hasattr(self.client, 'aclose'):
            await self.client.aclose()
        elif hasattr(self.client, 'close'):
            await self.client.close()
        logger.info("Closed Sophia client connection")
        
    async def is_available(self) -> bool:
        """
        Check if Sophia is available.
        
        Returns:
            True if Sophia is available
        """
        try:
            response = await self.client.get("/health")
            
            if response.status_code == 200:
                data = response.json()
                return data.get("status") == "healthy"
            else:
                logger.warning(f"Sophia returned non-200 status code: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error checking Sophia availability: {e}")
            return False
            
    # Metrics API
    
    async def submit_metric(
        self,
        metric_id: str,
        value: Any,
        source: Optional[str] = None,
        timestamp: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Submit a metric to Sophia.
        
        Args:
            metric_id: Unique identifier for the metric type
            value: Value of the metric
            source: Source of the metric (e.g., component ID)
            timestamp: ISO timestamp (defaults to current time)
            context: Additional context for the metric
            tags: Tags for categorizing the metric
            
        Returns:
            Response from the API
        """
        data = {
            "metric_id": metric_id,
            "value": value,
            "source": source,
            "timestamp": timestamp,
            "context": context or {},
            "tags": tags or []
        }
        
        response = await self.client.post("/api/metrics", json=data)
        response.raise_for_status()
        return response.json()
        
    async def submit_metrics_batch(self, metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Submit multiple metrics to Sophia.
        
        Args:
            metrics: List of metrics to submit
            
        Returns:
            List of responses from the API
        """
        responses = []
        
        for metric in metrics:
            response = await self.submit_metric(**metric)
            responses.append(response)
            
        return responses
        
    async def query_metrics(
        self,
        metric_id: Optional[str] = None,
        source: Optional[str] = None,
        tags: Optional[List[str]] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        sort: str = "timestamp:desc"
    ) -> List[Dict[str, Any]]:
        """
        Query metrics from Sophia.
        
        Args:
            metric_id: Filter by metric ID
            source: Filter by source
            tags: Filter by tags
            start_time: Filter by start time (ISO format)
            end_time: Filter by end time (ISO format)
            limit: Maximum number of results to return
            offset: Offset for pagination
            sort: Sort order (e.g., "timestamp:desc")
            
        Returns:
            List of metrics matching the query
        """
        params = {
            "limit": limit,
            "offset": offset,
            "sort": sort
        }
        
        if metric_id:
            params["metric_id"] = metric_id
            
        if source:
            params["source"] = source
            
        if tags:
            params["tags"] = ",".join(tags)
            
        if start_time:
            params["start_time"] = start_time
            
        if end_time:
            params["end_time"] = end_time
            
        response = await self.client.get("/api/metrics", params=params)
        response.raise_for_status()
        return response.json()
        
    async def aggregate_metrics(
        self,
        metric_id: str,
        aggregation: str = "avg",
        interval: Optional[str] = None,
        source: Optional[str] = None,
        tags: Optional[List[str]] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Aggregate metrics for analysis.
        
        Args:
            metric_id: Metric ID to aggregate
            aggregation: Aggregation function (e.g., "avg", "sum", "min", "max")
            interval: Interval for time-based aggregation (e.g., "1h", "1d")
            source: Filter by source
            tags: Filter by tags
            start_time: Filter by start time (ISO format)
            end_time: Filter by end time (ISO format)
            
        Returns:
            Aggregation result
        """
        data = {
            "metric_id": metric_id,
            "aggregation": aggregation
        }
        
        if interval:
            data["interval"] = interval
            
        if source:
            data["source"] = source
            
        if tags:
            data["tags"] = tags
            
        if start_time:
            data["start_time"] = start_time
            
        if end_time:
            data["end_time"] = end_time
            
        response = await self.client.post("/api/metrics/aggregate", json=data)
        response.raise_for_status()
        return response.json()
        
    # Experiments API
    
    async def create_experiment(
        self,
        name: str,
        description: str,
        experiment_type: str,
        target_components: List[str],
        hypothesis: str,
        metrics: List[str],
        parameters: Dict[str, Any],
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        sample_size: Optional[int] = None,
        min_confidence: Optional[float] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Create a new experiment.
        
        Args:
            name: Name of the experiment
            description: Description of the experiment
            experiment_type: Type of experiment
            target_components: List of components involved in the experiment
            hypothesis: Hypothesis being tested
            metrics: List of metrics to be tracked
            parameters: Parameters for the experiment
            start_time: Scheduled start time (ISO format)
            end_time: Scheduled end time (ISO format)
            sample_size: Target sample size
            min_confidence: Minimum confidence level required
            tags: Tags for categorizing the experiment
            
        Returns:
            Experiment ID
        """
        data = {
            "name": name,
            "description": description,
            "experiment_type": experiment_type,
            "target_components": target_components,
            "hypothesis": hypothesis,
            "metrics": metrics,
            "parameters": parameters
        }
        
        if start_time:
            data["start_time"] = start_time
            
        if end_time:
            data["end_time"] = end_time
            
        if sample_size:
            data["sample_size"] = sample_size
            
        if min_confidence:
            data["min_confidence"] = min_confidence
            
        if tags:
            data["tags"] = tags
            
        response = await self.client.post("/api/experiments", json=data)
        response.raise_for_status()
        
        result = response.json()
        return result.get("data", {}).get("experiment_id")
        
    async def get_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """
        Get details of a specific experiment.
        
        Args:
            experiment_id: ID of the experiment
            
        Returns:
            Experiment details
        """
        response = await self.client.get(f"/api/experiments/{experiment_id}")
        response.raise_for_status()
        return response.json()
        
    async def query_experiments(
        self,
        status: Optional[str] = None,
        experiment_type: Optional[str] = None,
        target_components: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        start_after: Optional[str] = None,
        start_before: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Query experiments with filtering.
        
        Args:
            status: Filter by status
            experiment_type: Filter by experiment type
            target_components: Filter by target components
            tags: Filter by tags
            start_after: Filter by start time after (ISO format)
            start_before: Filter by start time before (ISO format)
            limit: Maximum number of results to return
            offset: Offset for pagination
            
        Returns:
            List of experiments matching the query
        """
        params = {
            "limit": limit,
            "offset": offset
        }
        
        if status:
            params["status"] = status
            
        if experiment_type:
            params["experiment_type"] = experiment_type
            
        if target_components:
            params["target_components"] = ",".join(target_components)
            
        if tags:
            params["tags"] = ",".join(tags)
            
        if start_after:
            params["start_after"] = start_after
            
        if start_before:
            params["start_before"] = start_before
            
        response = await self.client.get("/api/experiments", params=params)
        response.raise_for_status()
        return response.json()
        
    async def update_experiment(
        self,
        experiment_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing experiment.
        
        Args:
            experiment_id: ID of the experiment
            updates: Updates to apply
            
        Returns:
            Response from the API
        """
        response = await self.client.put(f"/api/experiments/{experiment_id}", json=updates)
        response.raise_for_status()
        return response.json()
        
    async def start_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """
        Start an experiment.
        
        Args:
            experiment_id: ID of the experiment
            
        Returns:
            Response from the API
        """
        response = await self.client.post(f"/api/experiments/{experiment_id}/start")
        response.raise_for_status()
        return response.json()
        
    async def stop_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """
        Stop an experiment.
        
        Args:
            experiment_id: ID of the experiment
            
        Returns:
            Response from the API
        """
        response = await self.client.post(f"/api/experiments/{experiment_id}/stop")
        response.raise_for_status()
        return response.json()
        
    async def analyze_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """
        Analyze an experiment's results.
        
        Args:
            experiment_id: ID of the experiment
            
        Returns:
            Response from the API
        """
        response = await self.client.post(f"/api/experiments/{experiment_id}/analyze")
        response.raise_for_status()
        return response.json()
        
    async def get_experiment_results(self, experiment_id: str) -> Dict[str, Any]:
        """
        Get results of a completed experiment.
        
        Args:
            experiment_id: ID of the experiment
            
        Returns:
            Experiment results
        """
        response = await self.client.get(f"/api/experiments/{experiment_id}/results")
        response.raise_for_status()
        return response.json()
        
    # Recommendations API
    
    async def create_recommendation(
        self,
        title: str,
        description: str,
        recommendation_type: str,
        target_components: List[str],
        priority: str,
        rationale: str,
        expected_impact: Dict[str, Any],
        implementation_complexity: str,
        supporting_evidence: Optional[Dict[str, Any]] = None,
        experiment_ids: Optional[List[str]] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Create a new recommendation.
        
        Args:
            title: Title of the recommendation
            description: Detailed description of the recommendation
            recommendation_type: Type of recommendation
            target_components: List of components this recommendation applies to
            priority: Priority level
            rationale: Rationale behind the recommendation
            expected_impact: Expected impact of implementing the recommendation
            implementation_complexity: Estimated complexity of implementation
            supporting_evidence: Evidence supporting the recommendation
            experiment_ids: Associated experiment IDs
            tags: Tags for categorizing the recommendation
            
        Returns:
            Recommendation ID
        """
        data = {
            "title": title,
            "description": description,
            "recommendation_type": recommendation_type,
            "target_components": target_components,
            "priority": priority,
            "rationale": rationale,
            "expected_impact": expected_impact,
            "implementation_complexity": implementation_complexity
        }
        
        if supporting_evidence:
            data["supporting_evidence"] = supporting_evidence
            
        if experiment_ids:
            data["experiment_ids"] = experiment_ids
            
        if tags:
            data["tags"] = tags
            
        response = await self.client.post("/api/recommendations", json=data)
        response.raise_for_status()
        
        result = response.json()
        return result.get("data", {}).get("recommendation_id")
        
    async def get_recommendation(self, recommendation_id: str) -> Dict[str, Any]:
        """
        Get details of a specific recommendation.
        
        Args:
            recommendation_id: ID of the recommendation
            
        Returns:
            Recommendation details
        """
        response = await self.client.get(f"/api/recommendations/{recommendation_id}")
        response.raise_for_status()
        return response.json()
        
    async def query_recommendations(
        self,
        status: Optional[str] = None,
        recommendation_type: Optional[str] = None,
        priority: Optional[str] = None,
        target_components: Optional[List[str]] = None,
        experiment_ids: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        created_after: Optional[str] = None,
        created_before: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Query recommendations with filtering.
        
        Args:
            status: Filter by status
            recommendation_type: Filter by recommendation type
            priority: Filter by priority
            target_components: Filter by target components
            experiment_ids: Filter by associated experiment IDs
            tags: Filter by tags
            created_after: Filter by creation time after (ISO format)
            created_before: Filter by creation time before (ISO format)
            limit: Maximum number of results to return
            offset: Offset for pagination
            
        Returns:
            List of recommendations matching the query
        """
        params = {
            "limit": limit,
            "offset": offset
        }
        
        if status:
            params["status"] = status
            
        if recommendation_type:
            params["recommendation_type"] = recommendation_type
            
        if priority:
            params["priority"] = priority
            
        if target_components:
            params["target_components"] = ",".join(target_components)
            
        if experiment_ids:
            params["experiment_ids"] = ",".join(experiment_ids)
            
        if tags:
            params["tags"] = ",".join(tags)
            
        if created_after:
            params["created_after"] = created_after
            
        if created_before:
            params["created_before"] = created_before
            
        response = await self.client.get("/api/recommendations", params=params)
        response.raise_for_status()
        return response.json()
        
    async def update_recommendation(
        self,
        recommendation_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing recommendation.
        
        Args:
            recommendation_id: ID of the recommendation
            updates: Updates to apply
            
        Returns:
            Response from the API
        """
        response = await self.client.put(f"/api/recommendations/{recommendation_id}", json=updates)
        response.raise_for_status()
        return response.json()
        
    async def update_recommendation_status(
        self,
        recommendation_id: str,
        status: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update the status of a recommendation.
        
        Args:
            recommendation_id: ID of the recommendation
            status: New status for the recommendation
            notes: Notes on the status update
            
        Returns:
            Response from the API
        """
        params = {}
        
        if notes:
            params["notes"] = notes
            
        response = await self.client.post(f"/api/recommendations/{recommendation_id}/status/{status}", params=params)
        response.raise_for_status()
        return response.json()
        
    async def verify_recommendation(
        self,
        recommendation_id: str,
        verification_metrics: Dict[str, Any],
        observed_impact: Dict[str, Any],
        verification_status: str,
        verification_notes: Optional[str] = None,
        follow_up_actions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Verify the implementation of a recommendation.
        
        Args:
            recommendation_id: ID of the recommendation
            verification_metrics: Metrics used for verification
            observed_impact: Observed impact after implementation
            verification_status: Result of verification (success/partial/failure)
            verification_notes: Notes on the verification process
            follow_up_actions: Suggested follow-up actions if needed
            
        Returns:
            Response from the API
        """
        data = {
            "recommendation_id": recommendation_id,
            "verification_metrics": verification_metrics,
            "observed_impact": observed_impact,
            "verification_status": verification_status
        }
        
        if verification_notes:
            data["verification_notes"] = verification_notes
            
        if follow_up_actions:
            data["follow_up_actions"] = follow_up_actions
            
        response = await self.client.post(f"/api/recommendations/{recommendation_id}/verify", json=data)
        response.raise_for_status()
        return response.json()
        
    # Intelligence API
    
    async def record_intelligence_measurement(
        self,
        component_id: str,
        dimension: str,
        measurement_method: str,
        score: float,
        confidence: float,
        context: Dict[str, Any],
        evidence: Dict[str, Any],
        evaluator: Optional[str] = None,
        timestamp: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Record an intelligence measurement.
        
        Args:
            component_id: ID of the component being measured
            dimension: Intelligence dimension being measured
            measurement_method: Method used for measurement
            score: Measurement score (0.0-1.0)
            confidence: Confidence in the measurement (0.0-1.0)
            context: Context of the measurement
            evidence: Evidence supporting the measurement
            evaluator: Entity performing the evaluation
            timestamp: Timestamp of the measurement (ISO format)
            tags: Tags for categorizing the measurement
            
        Returns:
            Measurement ID
        """
        data = {
            "component_id": component_id,
            "dimension": dimension,
            "measurement_method": measurement_method,
            "score": score,
            "confidence": confidence,
            "context": context,
            "evidence": evidence
        }
        
        if evaluator:
            data["evaluator"] = evaluator
            
        if timestamp:
            data["timestamp"] = timestamp
            
        if tags:
            data["tags"] = tags
            
        response = await self.client.post("/api/intelligence/measurements", json=data)
        response.raise_for_status()
        
        result = response.json()
        return result.get("data", {}).get("measurement_id")
        
    async def query_intelligence_measurements(
        self,
        component_id: Optional[str] = None,
        dimensions: Optional[List[str]] = None,
        measurement_method: Optional[str] = None,
        min_score: Optional[float] = None,
        max_score: Optional[float] = None,
        min_confidence: Optional[float] = None,
        evaluator: Optional[str] = None,
        measured_after: Optional[str] = None,
        measured_before: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Query intelligence measurements with filtering.
        
        Args:
            component_id: Filter by component ID
            dimensions: Filter by dimensions
            measurement_method: Filter by measurement method
            min_score: Filter by minimum score
            max_score: Filter by maximum score
            min_confidence: Filter by minimum confidence
            evaluator: Filter by evaluator
            measured_after: Filter by measurement time after (ISO format)
            measured_before: Filter by measurement time before (ISO format)
            tags: Filter by tags
            limit: Maximum number of results to return
            offset: Offset for pagination
            
        Returns:
            List of measurements matching the query
        """
        params = {
            "limit": limit,
            "offset": offset
        }
        
        if component_id:
            params["component_id"] = component_id
            
        if dimensions:
            params["dimensions"] = ",".join(dimensions)
            
        if measurement_method:
            params["measurement_method"] = measurement_method
            
        if min_score is not None:
            params["min_score"] = min_score
            
        if max_score is not None:
            params["max_score"] = max_score
            
        if min_confidence is not None:
            params["min_confidence"] = min_confidence
            
        if evaluator:
            params["evaluator"] = evaluator
            
        if measured_after:
            params["measured_after"] = measured_after
            
        if measured_before:
            params["measured_before"] = measured_before
            
        if tags:
            params["tags"] = ",".join(tags)
            
        response = await self.client.get("/api/intelligence/measurements", params=params)
        response.raise_for_status()
        return response.json()
        
    async def get_component_intelligence_profile(
        self,
        component_id: str,
        timestamp: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get the intelligence profile of a component.
        
        Args:
            component_id: ID of the component
            timestamp: Timestamp for historical profile (ISO format)
            
        Returns:
            Component intelligence profile
        """
        params = {}
        
        if timestamp:
            params["timestamp"] = timestamp
            
        response = await self.client.get(f"/api/intelligence/components/{component_id}/profile", params=params)
        response.raise_for_status()
        return response.json()
        
    async def compare_intelligence_profiles(
        self,
        component_ids: List[str],
        dimensions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Compare intelligence between components.
        
        Args:
            component_ids: List of component IDs to compare
            dimensions: Dimensions to compare (all if None)
            
        Returns:
            Comparison result
        """
        data = {
            "component_ids": component_ids
        }
        
        if dimensions:
            data["dimensions"] = dimensions
            
        response = await self.client.post("/api/intelligence/components/compare", json=data)
        response.raise_for_status()
        return response.json()
        
    async def get_intelligence_dimensions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all intelligence dimensions.
        
        Returns:
            Dictionary of intelligence dimensions
        """
        response = await self.client.get("/api/intelligence/dimensions")
        response.raise_for_status()
        return response.json()
        
    async def get_intelligence_dimension(self, dimension: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific intelligence dimension.
        
        Args:
            dimension: Intelligence dimension
            
        Returns:
            Dimension information
        """
        response = await self.client.get(f"/api/intelligence/dimensions/{dimension}")
        response.raise_for_status()
        return response.json()
        
    async def get_ecosystem_intelligence_profile(self) -> Dict[str, Any]:
        """
        Get an intelligence profile for the entire Tekton ecosystem.
        
        Returns:
            Ecosystem intelligence profile
        """
        response = await self.client.get("/api/intelligence/ecosystem/profile")
        response.raise_for_status()
        return response.json()
        
    # Components API
    
    async def register_component(
        self,
        component_id: str,
        name: str,
        description: str,
        component_type: str,
        version: str,
        api_endpoints: Optional[List[str]] = None,
        capabilities: Optional[List[str]] = None,
        dependencies: Optional[List[str]] = None,
        metrics_provided: Optional[List[str]] = None,
        port: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        Register a component with Sophia.
        
        Args:
            component_id: Unique identifier for the component
            name: Human-readable name of the component
            description: Description of the component's purpose
            component_type: Type of component
            version: Version of the component
            api_endpoints: List of API endpoints provided by the component
            capabilities: List of capabilities provided by the component
            dependencies: List of dependencies required by the component
            metrics_provided: List of metrics provided by the component
            port: Port on which the component runs
            tags: Tags for categorizing the component
            
        Returns:
            True if registration was successful
        """
        data = {
            "component_id": component_id,
            "name": name,
            "description": description,
            "component_type": component_type,
            "version": version
        }
        
        if api_endpoints:
            data["api_endpoints"] = api_endpoints
            
        if capabilities:
            data["capabilities"] = capabilities
            
        if dependencies:
            data["dependencies"] = dependencies
            
        if metrics_provided:
            data["metrics_provided"] = metrics_provided
            
        if port:
            data["port"] = port
            
        if tags:
            data["tags"] = tags
            
        response = await self.client.post("/api/components/register", json=data)
        response.raise_for_status()
        
        result = response.json()
        return result.get("success", False)
        
    async def get_component(self, component_id: str) -> Dict[str, Any]:
        """
        Get details of a specific registered component.
        
        Args:
            component_id: ID of the component
            
        Returns:
            Component details
        """
        response = await self.client.get(f"/api/components/{component_id}")
        response.raise_for_status()
        return response.json()
        
    async def query_components(
        self,
        component_type: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        dependencies: Optional[List[str]] = None,
        metrics_provided: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Query registered components with filtering.
        
        Args:
            component_type: Filter by component type
            capabilities: Filter by capabilities
            dependencies: Filter by dependencies
            metrics_provided: Filter by provided metrics
            tags: Filter by tags
            status: Filter by status
            limit: Maximum number of results to return
            offset: Offset for pagination
            
        Returns:
            List of components matching the query
        """
        params = {
            "limit": limit,
            "offset": offset
        }
        
        if component_type:
            params["component_type"] = component_type
            
        if capabilities:
            params["capabilities"] = ",".join(capabilities)
            
        if dependencies:
            params["dependencies"] = ",".join(dependencies)
            
        if metrics_provided:
            params["metrics_provided"] = ",".join(metrics_provided)
            
        if tags:
            params["tags"] = ",".join(tags)
            
        if status:
            params["status"] = status
            
        response = await self.client.get("/api/components", params=params)
        response.raise_for_status()
        return response.json()
        
    async def update_component(
        self,
        component_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update a registered component.
        
        Args:
            component_id: ID of the component
            updates: Updates to apply
            
        Returns:
            Response from the API
        """
        response = await self.client.put(f"/api/components/{component_id}", json=updates)
        response.raise_for_status()
        return response.json()
        
    async def analyze_component_performance(
        self,
        component_id: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze the performance of a component.
        
        Args:
            component_id: ID of the component
            start_time: Filter by start time (ISO format)
            end_time: Filter by end time (ISO format)
            metrics: List of metrics to include in the analysis
            
        Returns:
            Performance analysis
        """
        params = {}
        
        if start_time:
            params["start_time"] = start_time
            
        if end_time:
            params["end_time"] = end_time
            
        if metrics:
            params["metrics"] = ",".join(metrics)
            
        response = await self.client.get(f"/api/components/{component_id}/performance", params=params)
        response.raise_for_status()
        return response.json()
        
    async def analyze_component_interaction(
        self,
        component_ids: List[str],
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze the interaction between components.
        
        Args:
            component_ids: List of component IDs to analyze
            start_time: Filter by start time (ISO format)
            end_time: Filter by end time (ISO format)
            
        Returns:
            Interaction analysis
        """
        data = {
            "component_ids": component_ids
        }
        
        params = {}
        
        if start_time:
            params["start_time"] = start_time
            
        if end_time:
            params["end_time"] = end_time
            
        response = await self.client.post("/api/components/interaction", json=data, params=params)
        response.raise_for_status()
        return response.json()
        
    # Research API
    
    async def create_research_project(
        self,
        title: str,
        description: str,
        approach: str,
        research_questions: List[str],
        hypothesis: Optional[str],
        target_components: List[str],
        data_requirements: Dict[str, Any],
        expected_outcomes: List[str],
        estimated_duration: str,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Create a new research project.
        
        Args:
            title: Title of the research project
            description: Detailed description of the project
            approach: Primary research approach
            research_questions: Research questions being investigated
            hypothesis: Primary hypothesis
            target_components: Components involved in the research
            data_requirements: Data required for the research
            expected_outcomes: Expected outcomes of the research
            estimated_duration: Estimated duration of the project
            tags: Tags for categorizing the project
            
        Returns:
            Project ID
        """
        data = {
            "title": title,
            "description": description,
            "approach": approach,
            "research_questions": research_questions,
            "target_components": target_components,
            "data_requirements": data_requirements,
            "expected_outcomes": expected_outcomes,
            "estimated_duration": estimated_duration
        }
        
        if hypothesis:
            data["hypothesis"] = hypothesis
            
        if tags:
            data["tags"] = tags
            
        response = await self.client.post("/api/research/projects", json=data)
        response.raise_for_status()
        
        result = response.json()
        return result.get("data", {}).get("project_id")
        
    async def get_research_project(self, project_id: str) -> Dict[str, Any]:
        """
        Get details of a specific research project.
        
        Args:
            project_id: ID of the research project
            
        Returns:
            Research project details
        """
        response = await self.client.get(f"/api/research/projects/{project_id}")
        response.raise_for_status()
        return response.json()
        
    async def query_research_projects(
        self,
        status: Optional[str] = None,
        approach: Optional[str] = None,
        target_components: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        created_after: Optional[str] = None,
        created_before: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Query research projects with filtering.
        
        Args:
            status: Filter by status
            approach: Filter by research approach
            target_components: Filter by target components
            tags: Filter by tags
            created_after: Filter by creation time after (ISO format)
            created_before: Filter by creation time before (ISO format)
            limit: Maximum number of results to return
            offset: Offset for pagination
            
        Returns:
            List of research projects matching the query
        """
        params = {
            "limit": limit,
            "offset": offset
        }
        
        if status:
            params["status"] = status
            
        if approach:
            params["approach"] = approach
            
        if target_components:
            params["target_components"] = ",".join(target_components)
            
        if tags:
            params["tags"] = ",".join(tags)
            
        if created_after:
            params["created_after"] = created_after
            
        if created_before:
            params["created_before"] = created_before
            
        response = await self.client.get("/api/research/projects", params=params)
        response.raise_for_status()
        return response.json()
        
    async def update_research_project(
        self,
        project_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing research project.
        
        Args:
            project_id: ID of the research project
            updates: Updates to apply
            
        Returns:
            Response from the API
        """
        response = await self.client.put(f"/api/research/projects/{project_id}", json=updates)
        response.raise_for_status()
        return response.json()