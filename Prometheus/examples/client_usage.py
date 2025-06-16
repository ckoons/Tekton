#!/usr/bin/env python3
"""
Prometheus/Epimethius Client Usage Example

This example demonstrates how to use the Prometheus/Epimethius client
to interact with the planning system.
"""

import asyncio
import logging
from datetime import datetime, timedelta
import sys
import os

# Add the parent directory to the path to allow importing the prometheus module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import Prometheus/Epimethius client
from prometheus.client import PrometheusClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("prometheus_example")


async def demonstrate_planning_capabilities(client):
    """
    Demonstrate the planning capabilities of Prometheus.
    
    Args:
        client: PrometheusClient instance
    """
    logger.info("===== Demonstrating Prometheus Planning Capabilities =====")
    
    # Create a new plan
    plan_id = await client.create_plan(
        name="Example Project Plan",
        description="A demonstration project plan for the client usage example",
        start_date=datetime.now().isoformat(),
        end_date=(datetime.now() + timedelta(days=30)).isoformat()
    )
    logger.info(f"Created plan with ID: {plan_id}")
    
    # Create resources
    resources = [
        {
            "name": "Developer 1",
            "type": "human",
            "skills": ["python", "backend"],
            "availability": 1.0  # Full-time
        },
        {
            "name": "Developer 2",
            "type": "human",
            "skills": ["javascript", "frontend"],
            "availability": 0.5  # Part-time
        },
        {
            "name": "Project Manager",
            "type": "human",
            "skills": ["management", "planning"],
            "availability": 0.25  # Quarter-time
        }
    ]
    
    resource_ids = []
    for resource in resources:
        resource_id = await client.add_resource(plan_id, **resource)
        resource_ids.append(resource_id)
        logger.info(f"Added resource: {resource['name']} with ID: {resource_id}")
    
    # Create tasks with dependencies
    tasks = [
        {
            "name": "Requirements Analysis",
            "description": "Gather and analyze project requirements",
            "duration": 3,
            "duration_unit": "days",
            "assigned_to": resource_ids[2],  # Project Manager
            "dependencies": []
        },
        {
            "name": "Backend API Design",
            "description": "Design the backend API architecture",
            "duration": 5,
            "duration_unit": "days",
            "assigned_to": resource_ids[0],  # Developer 1
            "dependencies": [0]  # Depends on Requirements Analysis
        },
        {
            "name": "Frontend UI Design",
            "description": "Design the user interface",
            "duration": 4,
            "duration_unit": "days",
            "assigned_to": resource_ids[1],  # Developer 2
            "dependencies": [0]  # Depends on Requirements Analysis
        },
        {
            "name": "Backend Implementation",
            "description": "Implement the backend API",
            "duration": 10,
            "duration_unit": "days",
            "assigned_to": resource_ids[0],  # Developer 1
            "dependencies": [1]  # Depends on Backend API Design
        },
        {
            "name": "Frontend Implementation",
            "description": "Implement the user interface",
            "duration": 8,
            "duration_unit": "days",
            "assigned_to": resource_ids[1],  # Developer 2
            "dependencies": [2]  # Depends on Frontend UI Design
        },
        {
            "name": "Integration",
            "description": "Integrate frontend and backend",
            "duration": 3,
            "duration_unit": "days",
            "assigned_to": resource_ids[0],  # Developer 1
            "dependencies": [3, 4]  # Depends on both implementations
        },
        {
            "name": "Testing",
            "description": "Test the integrated application",
            "duration": 5,
            "duration_unit": "days",
            "assigned_to": resource_ids[1],  # Developer 2
            "dependencies": [5]  # Depends on Integration
        },
        {
            "name": "Deployment",
            "description": "Deploy the application to production",
            "duration": 1,
            "duration_unit": "days",
            "assigned_to": resource_ids[0],  # Developer 1
            "dependencies": [6]  # Depends on Testing
        }
    ]
    
    task_ids = []
    for i, task in enumerate(tasks):
        # Convert the dependency indexes to actual task IDs
        task["dependencies"] = [task_ids[dep] for dep in task["dependencies"]] if task["dependencies"] else []
        
        task_id = await client.add_task(plan_id, **task)
        task_ids.append(task_id)
        logger.info(f"Added task: {task['name']} with ID: {task_id}")
    
    # Generate timeline
    timeline = await client.generate_timeline(plan_id)
    logger.info(f"Generated timeline: Start: {timeline['start_date']}, End: {timeline['end_date']}")
    
    # Calculate critical path
    critical_path = await client.calculate_critical_path(plan_id)
    logger.info(f"Critical path: {[tasks[i]['name'] for i in critical_path['critical_tasks_indices']]}")
    
    # Get plan summary
    plan_summary = await client.get_plan_summary(plan_id)
    logger.info(f"Plan summary: {len(plan_summary['tasks'])} tasks, "
               f"Duration: {plan_summary['duration_days']} days, "
               f"Resources: {len(plan_summary['resources'])}")
    
    # Generate LLM analysis (if available)
    try:
        analysis = await client.generate_plan_analysis(plan_id)
        logger.info(f"LLM Analysis: {analysis['summary']}")
        
        for risk in analysis['risks']:
            logger.info(f"Risk: {risk['description']} (Probability: {risk['probability']})")
        
        for recommendation in analysis['recommendations']:
            logger.info(f"Recommendation: {recommendation}")
    except Exception as e:
        logger.warning(f"LLM analysis not available: {e}")
    
    return plan_id, task_ids


async def demonstrate_retrospective_capabilities(client, plan_id, task_ids):
    """
    Demonstrate the retrospective capabilities of Epimethius.
    
    Args:
        client: PrometheusClient instance
        plan_id: ID of the plan to analyze
        task_ids: IDs of the tasks in the plan
    """
    logger.info("\n===== Demonstrating Epimethius Retrospective Capabilities =====")
    
    # First, let's simulate that the project is complete
    for i, task_id in enumerate(task_ids):
        # Simulate actual start and end dates
        actual_start = datetime.now() + timedelta(days=i * 2)
        
        # Add some variance in task completion
        variance = [0, 1, -1, 2, 1, 3, 0, -1][i]  # Different variance for each task
        planned_duration = [3, 5, 4, 10, 8, 3, 5, 1][i]  # From our task definitions
        actual_duration = max(1, planned_duration + variance)
        
        actual_end = actual_start + timedelta(days=actual_duration)
        
        # Update task with actual dates
        await client.update_task_progress(
            plan_id=plan_id,
            task_id=task_id,
            status="completed",
            actual_start_date=actual_start.isoformat(),
            actual_end_date=actual_end.isoformat(),
            actual_duration=actual_duration,
            actual_duration_unit="days"
        )
        
        logger.info(f"Updated task {task_id} with actual duration: {actual_duration} days "
                  f"(planned: {planned_duration} days)")
    
    # Create a retrospective
    retrospective_id = await client.create_retrospective(
        plan_id=plan_id,
        name="Example Project Retrospective",
        description="A demonstration retrospective for the client usage example",
        date=datetime.now().isoformat()
    )
    logger.info(f"Created retrospective with ID: {retrospective_id}")
    
    # Add some feedback
    feedback_items = [
        {
            "type": "positive",
            "description": "Team collaboration was excellent",
            "source": "Project Manager"
        },
        {
            "type": "negative",
            "description": "Integration took longer than expected",
            "source": "Developer 1"
        },
        {
            "type": "positive",
            "description": "Frontend design was well-received by stakeholders",
            "source": "Developer 2"
        },
        {
            "type": "negative",
            "description": "Requirements changed during implementation",
            "source": "Developer 1"
        }
    ]
    
    for feedback in feedback_items:
        feedback_id = await client.add_retrospective_feedback(
            retrospective_id=retrospective_id,
            **feedback
        )
        logger.info(f"Added feedback: {feedback['description']} with ID: {feedback_id}")
    
    # Generate variance analysis
    variance_analysis = await client.generate_variance_analysis(plan_id)
    logger.info(f"Variance analysis: {variance_analysis['summary']}")
    
    for task_variance in variance_analysis['task_variances']:
        logger.info(f"Task {task_variance['name']} variance: {task_variance['duration_variance']} days")
    
    # Generate performance metrics
    metrics = await client.generate_performance_metrics(plan_id)
    logger.info(f"Performance metrics: {metrics['summary']}")
    logger.info(f"On-time completion rate: {metrics['on_time_completion_rate']}%")
    logger.info(f"Average task delay: {metrics['average_delay']} days")
    
    # Generate improvement suggestions
    suggestions = await client.generate_improvement_suggestions(retrospective_id)
    logger.info(f"Improvement suggestions:")
    for suggestion in suggestions:
        logger.info(f"- {suggestion['description']}")
        logger.info(f"  Rationale: {suggestion['rationale']}")
        logger.info(f"  Impact: {suggestion['expected_impact']}")
    
    # Generate LLM retrospective summary (if available)
    try:
        retro_summary = await client.generate_retrospective_summary(retrospective_id)
        logger.info(f"LLM Retrospective Summary: {retro_summary['summary']}")
        
        for lesson in retro_summary['lessons_learned']:
            logger.info(f"Lesson learned: {lesson}")
        
        for action in retro_summary['action_items']:
            logger.info(f"Action item: {action}")
    except Exception as e:
        logger.warning(f"LLM retrospective summary not available: {e}")


async def main():
    """Main function to demonstrate Prometheus/Epimethius capabilities."""
    try:
        # Create client
        client = PrometheusClient(base_url="http://localhost:8006/api")
        logger.info("Connected to Prometheus/Epimethius service")
        
        # Check if the service is available
        try:
            health = await client.health_check()
            logger.info(f"Service health: {health['status']}")
        except Exception as e:
            logger.error(f"Service is not available: {e}")
            logger.info("Make sure the Prometheus/Epimethius service is running")
            logger.info("You can start it with: python -m prometheus.api.app")
            return
        
        # Demonstrate planning capabilities
        plan_id, task_ids = await demonstrate_planning_capabilities(client)
        
        # Demonstrate retrospective capabilities
        await demonstrate_retrospective_capabilities(client, plan_id, task_ids)
        
        logger.info("\nDemonstration complete!")
        
    except Exception as e:
        logger.error(f"Error in demonstration: {e}", exc_info=True)
    finally:
        # Close client session
        if 'client' in locals():
            await client.close()


if __name__ == "__main__":
    asyncio.run(main())