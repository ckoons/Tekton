#!/usr/bin/env python3
"""
Example client for Sophia API.

This script demonstrates how to use the Sophia client to interact with Sophia's API.
"""

import asyncio
import json
import sys
import os
from shared.env import TektonEnviron
import logging
from datetime import datetime

# Add the parent directory to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sophia.client import SophiaClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("sophia.example")

# Default Sophia URL
DEFAULT_SOPHIA_URL = "http://localhost:8006"

async def submit_metrics_example(client):
    """Example of submitting metrics to Sophia."""
    logger.info("Submitting metrics example...")
    
    # Submit a simple performance metric
    response = await client.submit_metric(
        metric_id="response_time",
        value=0.245,
        source="example_client",
        context={
            "component": "client",
            "operation": "example_operation",
            "environment": "development"
        },
        tags=["example", "performance", "client"]
    )
    
    logger.info(f"Submit metric response: {response}")
    
    # Submit a batch of metrics
    metrics = [
        {
            "metric_id": "cpu_usage",
            "value": 24.5,
            "source": "example_client",
            "tags": ["resource", "cpu"]
        },
        {
            "metric_id": "memory_usage",
            "value": 156.7,
            "source": "example_client",
            "tags": ["resource", "memory"]
        },
        {
            "metric_id": "request_count",
            "value": 42,
            "source": "example_client",
            "tags": ["usage", "requests"]
        }
    ]
    
    responses = await client.submit_metrics_batch(metrics)
    logger.info(f"Submit metrics batch response: {responses}")
    
    return response

async def query_metrics_example(client):
    """Example of querying metrics from Sophia."""
    logger.info("Querying metrics example...")
    
    # Query metrics with filtering
    metrics = await client.query_metrics(
        metric_id="response_time",
        source="example_client",
        tags=["example"],
        limit=10
    )
    
    logger.info(f"Query metrics response: {len(metrics)} metrics found")
    if metrics:
        logger.info(f"First metric: {metrics[0]}")
    
    # Query with aggregation
    aggregation = await client.aggregate_metrics(
        metric_id="response_time",
        aggregation="avg",
        interval="1h"
    )
    
    logger.info(f"Aggregation response: {aggregation}")
    
    return metrics

async def experiment_example(client):
    """Example of creating and managing experiments in Sophia."""
    logger.info("Experiment management example...")
    
    # Create a new experiment
    experiment_id = await client.create_experiment(
        name="Response Time Optimization",
        description="Testing different query optimization techniques to improve response time",
        experiment_type="a_b_test",
        target_components=["database", "api"],
        hypothesis="Query optimization technique B will reduce response time by at least 15%",
        metrics=["response_time", "cpu_usage"],
        parameters={
            "technique_a": "index_only",
            "technique_b": "query_rewrite"
        }
    )
    
    logger.info(f"Created experiment with ID: {experiment_id}")
    
    # Get experiment details
    experiment = await client.get_experiment(experiment_id)
    logger.info(f"Experiment details: {experiment}")
    
    # Start the experiment
    start_response = await client.start_experiment(experiment_id)
    logger.info(f"Start experiment response: {start_response}")
    
    # We would normally wait for the experiment to complete here
    logger.info("Normally we would wait for experiment to complete...")
    
    # For demonstration, let's update the experiment status
    update_response = await client.update_experiment(
        experiment_id=experiment_id,
        updates={
            "status": "completed"
        }
    )
    logger.info(f"Update experiment response: {update_response}")
    
    return experiment_id

async def recommendation_example(client):
    """Example of creating and managing recommendations in Sophia."""
    logger.info("Recommendation management example...")
    
    # Create a new recommendation
    recommendation_id = await client.create_recommendation(
        title="Implement query caching for repeated operations",
        description="Analysis shows that 35% of queries are repeated within 5 minutes. Implementing a TTL-based query cache could significantly reduce database load.",
        recommendation_type="performance",
        target_components=["database", "api"],
        priority="high",
        rationale="Query analysis shows high repetition rate with minimal data change between queries",
        expected_impact={
            "response_time": "20% reduction",
            "database_load": "30% reduction",
            "throughput": "15% increase"
        },
        implementation_complexity="medium"
    )
    
    logger.info(f"Created recommendation with ID: {recommendation_id}")
    
    # Get recommendation details
    recommendation = await client.get_recommendation(recommendation_id)
    logger.info(f"Recommendation details: {recommendation}")
    
    # Update recommendation status
    status_response = await client.update_recommendation_status(
        recommendation_id=recommendation_id,
        status="approved",
        notes="Approved for implementation in next sprint"
    )
    logger.info(f"Update status response: {status_response}")
    
    return recommendation_id

async def intelligence_measurement_example(client):
    """Example of measuring intelligence in Sophia."""
    logger.info("Intelligence measurement example...")
    
    # Record an intelligence measurement
    measurement_id = await client.record_intelligence_measurement(
        component_id="example_component",
        dimension="reasoning",
        measurement_method="capability_test",
        score=0.78,
        confidence=0.85,
        context={
            "test_scenario": "logical deduction",
            "complexity": "medium"
        },
        evidence={
            "test_results": {
                "correct": 78,
                "incorrect": 22,
                "total": 100
            },
            "performance_metrics": {
                "accuracy": 0.78,
                "f1_score": 0.81
            }
        }
    )
    
    logger.info(f"Created intelligence measurement with ID: {measurement_id}")
    
    # Get component intelligence profile
    profile = await client.get_component_intelligence_profile("example_component")
    logger.info(f"Component intelligence profile: {profile}")
    
    return measurement_id

async def component_registration_example(client):
    """Example of registering a component with Sophia."""
    logger.info("Component registration example...")
    
    # Register a component
    success = await client.register_component(
        component_id="example_component",
        name="Example Component",
        description="An example component for demonstration purposes",
        component_type="service",
        version="0.1.0",
        capabilities=["example", "demonstration"],
        dependencies=["sophia"]
    )
    
    logger.info(f"Component registration {'succeeded' if success else 'failed'}")
    
    # Get component details
    component = await client.get_component("example_component")
    logger.info(f"Component details: {component}")
    
    # Analyze component performance
    analysis = await client.analyze_component_performance("example_component")
    logger.info(f"Component performance analysis: {analysis}")
    
    return success

async def research_project_example(client):
    """Example of creating a research project in Sophia."""
    logger.info("Research project example...")
    
    # Create a research project
    project_id = await client.create_research_project(
        title="Collaboration Efficiency in Multi-Agent Systems",
        description="Investigating how different communication patterns affect collaboration efficiency in multi-agent systems",
        approach="collaborative_intelligence",
        research_questions=[
            "How does communication frequency affect task completion time?",
            "What communication structures yield optimal resource utilization?"
        ],
        hypothesis="Hierarchical communication patterns with adaptive frequency yield optimal efficiency",
        target_components=["example_component", "sophia"],
        data_requirements={
            "metrics": ["communication_count", "task_completion_time", "resource_utilization"],
            "period": "30 days"
        },
        expected_outcomes=[
            "Communication pattern efficiency model",
            "Adaptive communication frequency algorithm"
        ],
        estimated_duration="90 days"
    )
    
    logger.info(f"Created research project with ID: {project_id}")
    
    # Get project details
    project = await client.get_research_project(project_id)
    logger.info(f"Research project details: {project}")
    
    return project_id

async def run_examples():
    """Run all examples."""
    # Create client
    client = SophiaClient(base_url=TektonEnviron.get("SOPHIA_URL", DEFAULT_SOPHIA_URL))
    
    try:
        # Check if Sophia is available
        if not await client.is_available():
            logger.error("Sophia is not available. Please make sure it's running.")
            return
        
        # Run examples
        await submit_metrics_example(client)
        await query_metrics_example(client)
        await experiment_example(client)
        await recommendation_example(client)
        await intelligence_measurement_example(client)
        await component_registration_example(client)
        await research_project_example(client)
        
        logger.info("All examples completed successfully!")
    except Exception as e:
        logger.error(f"Error running examples: {e}")
    finally:
        # Close client
        await client.close()

def main():
    """Main entry point."""
    asyncio.run(run_examples())

if __name__ == "__main__":
    main()