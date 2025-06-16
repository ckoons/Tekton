#!/usr/bin/env python3
"""
Example Usage of the Harmonia Client

This script demonstrates how to use the HarmoniaClient and HarmoniaStateClient to interact
with the Harmonia workflow orchestration component.
"""

import asyncio
import logging
from typing import Dict, List, Any
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("harmonia_example")

# Try to import from the harmonia package
try:
    from harmonia.client import (
        HarmoniaClient,
        HarmoniaStateClient,
        get_harmonia_client,
        get_harmonia_state_client
    )
except ImportError:
    import sys
    import os
    
    # Add the parent directory to sys.path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    
    # Try importing again
    from harmonia.client import (
        HarmoniaClient,
        HarmoniaStateClient,
        get_harmonia_client,
        get_harmonia_state_client
    )


async def simple_workflow_example():
    """Example of using the Harmonia client for a simple workflow."""
    logger.info("=== Simple Workflow Example ===")
    
    # Create a Harmonia client
    client = await get_harmonia_client()
    
    try:
        # Define a simple workflow with sequential tasks
        workflow_name = "Data Processing Workflow"
        workflow_description = "A simple workflow to process and analyze data"
        
        # Define the tasks
        tasks = [
            {
                "id": "fetch_data",
                "type": "api_request",
                "config": {
                    "url": "https://api.example.com/data",
                    "method": "GET",
                    "headers": {"Accept": "application/json"}
                },
                "next": "transform_data"
            },
            {
                "id": "transform_data",
                "type": "data_transform",
                "config": {
                    "operations": [
                        {"type": "filter", "field": "status", "value": "active"},
                        {"type": "sort", "field": "timestamp", "direction": "desc"}
                    ]
                },
                "next": "analyze_data"
            },
            {
                "id": "analyze_data",
                "type": "data_analysis",
                "config": {
                    "metrics": ["count", "average", "distribution"],
                    "dimensions": ["category", "region"]
                },
                "next": "generate_report"
            },
            {
                "id": "generate_report",
                "type": "report_generation",
                "config": {
                    "format": "pdf",
                    "template": "summary_report",
                    "include_charts": True
                }
            }
        ]
        
        # Define the input schema
        input_schema = {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "format": "date"},
                "end_date": {"type": "string", "format": "date"},
                "categories": {"type": "array", "items": {"type": "string"}}
            }
        }
        
        # Define the output schema
        output_schema = {
            "type": "object",
            "properties": {
                "report_url": {"type": "string"},
                "summary": {"type": "object"},
                "processed_records": {"type": "integer"}
            }
        }
        
        # Create the workflow
        logger.info(f"Creating workflow: {workflow_name}")
        workflow = await client.create_workflow(
            name=workflow_name,
            description=workflow_description,
            tasks=tasks,
            input_schema=input_schema,
            output_schema=output_schema
        )
        
        workflow_id = workflow["workflow_id"]
        logger.info(f"Created workflow with ID: {workflow_id}")
        
        # Execute the workflow
        workflow_input = {
            "start_date": "2025-01-01",
            "end_date": "2025-03-31",
            "categories": ["technology", "health", "finance"]
        }
        
        logger.info(f"Executing workflow {workflow_id} with input data")
        execution = await client.execute_workflow(
            workflow_id=workflow_id,
            input_data=workflow_input
        )
        
        execution_id = execution["execution_id"]
        logger.info(f"Started workflow execution with ID: {execution_id}")
        
        # Poll for workflow status
        max_polls = 5
        poll_interval = 2  # seconds
        
        for i in range(max_polls):
            logger.info(f"Polling execution status ({i+1}/{max_polls})...")
            status = await client.get_workflow_status(execution_id)
            
            logger.info(f"Execution status: {status['status']}")
            
            if status["status"] in ["completed", "failed", "cancelled"]:
                logger.info(f"Workflow execution {status['status']}")
                if "output" in status:
                    logger.info(f"Output: {status['output']}")
                if "error" in status:
                    logger.info(f"Error: {status['error']}")
                break
            
            # Wait before next poll
            await asyncio.sleep(poll_interval)
        
        # Cancel the workflow if it's still running
        if status["status"] not in ["completed", "failed", "cancelled"]:
            logger.info(f"Cancelling workflow execution {execution_id}")
            cancelled = await client.cancel_workflow(execution_id)
            logger.info(f"Workflow cancellation {'successful' if cancelled else 'failed'}")
    
    except Exception as e:
        logger.error(f"Error in simple workflow example: {e}")
    
    finally:
        # Close the client
        await client.close()


async def parallel_workflow_example():
    """Example of using the Harmonia client for a parallel workflow."""
    logger.info("=== Parallel Workflow Example ===")
    
    # Create a Harmonia client
    client = await get_harmonia_client()
    
    try:
        # Define a workflow with parallel tasks
        workflow_name = "Content Generation Pipeline"
        
        # Define the tasks with parallel execution
        tasks = [
            {
                "id": "get_topic",
                "type": "topic_selection",
                "config": {
                    "method": "trending",
                    "categories": ["science", "technology"]
                },
                "next": ["generate_article", "generate_images", "generate_social"]
            },
            {
                "id": "generate_article",
                "type": "text_generation",
                "config": {
                    "length": "medium",
                    "style": "informative",
                    "include_references": True
                },
                "next": "assemble_content"
            },
            {
                "id": "generate_images",
                "type": "image_generation",
                "config": {
                    "count": 3,
                    "style": "realistic",
                    "aspect_ratio": "16:9"
                },
                "next": "assemble_content"
            },
            {
                "id": "generate_social",
                "type": "social_post_generation",
                "config": {
                    "platforms": ["twitter", "linkedin", "facebook"],
                    "include_hashtags": True
                },
                "next": "assemble_content"
            },
            {
                "id": "assemble_content",
                "type": "content_assembly",
                "config": {
                    "layout": "article_with_sidebar",
                    "optimize_for_web": True
                },
                "join": ["generate_article", "generate_images", "generate_social"],
                "next": "publish_content"
            },
            {
                "id": "publish_content",
                "type": "content_publishing",
                "config": {
                    "platforms": ["website", "newsletter", "social_media"],
                    "schedule": "immediate"
                }
            }
        ]
        
        # Create the workflow
        logger.info(f"Creating parallel workflow: {workflow_name}")
        workflow = await client.create_workflow(
            name=workflow_name,
            tasks=tasks
        )
        
        workflow_id = workflow["workflow_id"]
        logger.info(f"Created workflow with ID: {workflow_id}")
        
        # Execute the workflow
        logger.info(f"Executing workflow {workflow_id}")
        execution = await client.execute_workflow(workflow_id=workflow_id)
        
        execution_id = execution["execution_id"]
        logger.info(f"Started workflow execution with ID: {execution_id}")
        
        # Get initial status
        status = await client.get_workflow_status(execution_id)
        logger.info(f"Initial execution status: {status['status']}")
        
        if "task_statuses" in status:
            logger.info("Task statuses:")
            for task_id, task_status in status.get("task_statuses", {}).items():
                logger.info(f"  {task_id}: {task_status}")
    
    except Exception as e:
        logger.error(f"Error in parallel workflow example: {e}")
    
    finally:
        # Close the client
        await client.close()


async def workflow_state_example():
    """Example of using the Harmonia State client for workflow state management."""
    logger.info("=== Workflow State Example ===")
    
    # Create Harmonia clients
    workflow_client = await get_harmonia_client()
    state_client = await get_harmonia_state_client()
    
    try:
        # Create a workflow
        workflow_name = "Long-Running Analysis Workflow"
        
        # Define a simple workflow
        tasks = [
            {
                "id": "initialize",
                "type": "setup",
                "next": "process_batch"
            },
            {
                "id": "process_batch",
                "type": "batch_processing",
                "next": "save_results"
            },
            {
                "id": "save_results",
                "type": "data_storage"
            }
        ]
        
        # Create the workflow
        workflow = await workflow_client.create_workflow(
            name=workflow_name,
            tasks=tasks
        )
        
        workflow_id = workflow["workflow_id"]
        logger.info(f"Created workflow with ID: {workflow_id}")
        
        # Execute the workflow
        execution = await workflow_client.execute_workflow(workflow_id=workflow_id)
        execution_id = execution["execution_id"]
        logger.info(f"Started workflow execution with ID: {execution_id}")
        
        # Save workflow state
        workflow_state = {
            "progress": 0.25,
            "current_batch": 1,
            "total_batches": 4,
            "processed_items": 250,
            "errors": [],
            "timestamp": time.time()
        }
        
        logger.info(f"Saving workflow state for execution {execution_id}")
        success = await state_client.save_state(
            execution_id=execution_id,
            state=workflow_state
        )
        
        logger.info(f"State saved successfully: {success}")
        
        # Create a checkpoint
        logger.info(f"Creating checkpoint for execution {execution_id}")
        checkpoint = await state_client.create_checkpoint(execution_id=execution_id)
        
        checkpoint_id = checkpoint["checkpoint_id"]
        logger.info(f"Created checkpoint with ID: {checkpoint_id}")
        
        # Update the state
        workflow_state["progress"] = 0.5
        workflow_state["current_batch"] = 2
        workflow_state["processed_items"] = 500
        workflow_state["timestamp"] = time.time()
        
        logger.info(f"Updating workflow state for execution {execution_id}")
        await state_client.save_state(
            execution_id=execution_id,
            state=workflow_state
        )
        
        # Load the state
        logger.info(f"Loading workflow state for execution {execution_id}")
        loaded_state = await state_client.load_state(execution_id=execution_id)
        
        logger.info("Loaded state:")
        for key, value in loaded_state.items():
            logger.info(f"  {key}: {value}")
    
    except Exception as e:
        logger.error(f"Error in workflow state example: {e}")
    
    finally:
        # Close the clients
        await workflow_client.close()
        await state_client.close()


async def error_handling_example():
    """Example of handling errors with the Harmonia client."""
    logger.info("=== Error Handling Example ===")
    
    # Create a Harmonia client with a non-existent component ID
    try:
        client = await get_harmonia_client(component_id="harmonia.nonexistent")
        # This should raise ComponentNotFoundError
        
    except Exception as e:
        logger.info(f"Caught expected error: {type(e).__name__}: {e}")
    
    # Create a valid client
    client = await get_harmonia_client()
    
    try:
        # Try to get status for a non-existent execution
        try:
            await client.get_workflow_status("nonexistent-execution-id")
        except Exception as e:
            logger.info(f"Caught expected error: {type(e).__name__}: {e}")
            
        # Try to cancel a non-existent execution
        try:
            await client.cancel_workflow("nonexistent-execution-id")
        except Exception as e:
            logger.info(f"Caught expected error: {type(e).__name__}: {e}")
    
    finally:
        # Close the client
        await client.close()


async def main():
    """Run all examples."""
    try:
        await simple_workflow_example()
        await parallel_workflow_example()
        await workflow_state_example()
        await error_handling_example()
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


async def template_instantiation_example():
    """Example of using templates and instantiating workflows from them."""
    logger.info("=== Template Instantiation Example ===")
    
    # Create a Harmonia client
    client = await get_harmonia_client()
    
    try:
        # Define a workflow with parameters
        workflow_name = "Parametrized Data Processing"
        
        # Define the tasks with parameters
        tasks = [
            {
                "id": "fetch_data",
                "type": "data_source",
                "config": {
                    "source": "${param.data_source}",
                    "format": "${param.data_format}"
                },
                "next": "process_data"
            },
            {
                "id": "process_data",
                "type": "data_processing",
                "config": {
                    "operations": "${param.processing_operations}",
                    "filter": "${param.filter_criteria}"
                },
                "next": "output_data"
            },
            {
                "id": "output_data",
                "type": "data_output",
                "config": {
                    "destination": "${param.output_destination}",
                    "format": "${param.output_format}"
                }
            }
        ]
        
        # Create the workflow
        logger.info(f"Creating template workflow: {workflow_name}")
        workflow = await client.create_workflow(
            name=workflow_name,
            tasks=tasks
        )
        
        workflow_id = workflow["workflow_id"]
        logger.info(f"Created workflow with ID: {workflow_id}")
        
        # Create a template from the workflow
        template_name = "Data Processing Template"
        parameters = {
            "data_source": {
                "type": "string",
                "required": True,
                "description": "Source of the data to process"
            },
            "data_format": {
                "type": "string",
                "required": False,
                "default": "csv",
                "description": "Format of the input data"
            },
            "processing_operations": {
                "type": "array",
                "required": True,
                "description": "List of operations to perform"
            },
            "filter_criteria": {
                "type": "object",
                "required": False,
                "default": {},
                "description": "Criteria for filtering data"
            },
            "output_destination": {
                "type": "string",
                "required": True,
                "description": "Destination for processed data"
            },
            "output_format": {
                "type": "string",
                "required": False,
                "default": "json",
                "description": "Format for the output data"
            }
        }
        
        logger.info(f"Creating template: {template_name}")
        template = await client.create_template(
            name=template_name,
            workflow_definition_id=workflow_id,
            parameters=parameters
        )
        
        template_id = template["template_id"]
        logger.info(f"Created template with ID: {template_id}")
        
        # Instantiate the template with parameter values
        parameter_values = {
            "data_source": "s3://example-bucket/data.csv",
            "data_format": "csv",
            "processing_operations": [
                {"type": "normalize", "field": "values"},
                {"type": "aggregate", "function": "sum", "field": "values"}
            ],
            "filter_criteria": {
                "date_range": {"start": "2025-01-01", "end": "2025-12-31"},
                "categories": ["category1", "category2"]
            },
            "output_destination": "s3://example-bucket/processed/",
            "output_format": "parquet"
        }
        
        logger.info(f"Instantiating template {template_id}")
        instantiation = await client.instantiate_template(
            template_id=template_id,
            parameter_values=parameter_values
        )
        
        instantiated_workflow_id = instantiation["workflow_id"]
        logger.info(f"Created workflow from template: {instantiated_workflow_id}")
        
        # Execute the instantiated workflow
        logger.info(f"Executing instantiated workflow {instantiated_workflow_id}")
        execution = await client.execute_workflow(
            workflow_id=instantiated_workflow_id
        )
        
        execution_id = execution["execution_id"]
        logger.info(f"Started execution with ID: {execution_id}")
        
        # Get status
        status = await client.get_workflow_status(execution_id)
        logger.info(f"Execution status: {status['status']}")
    
    except Exception as e:
        logger.error(f"Error in template instantiation example: {e}")
    
    finally:
        # Close the client
        await client.close()


async def websocket_monitoring_example():
    """Example of monitoring workflow execution via WebSocket."""
    logger.info("=== WebSocket Monitoring Example ===")
    
    # This would be implemented with a real WebSocket client
    # Here we'll simulate the concept
    
    # Create a workflow to monitor
    client = await get_harmonia_client()
    
    try:
        # Create a simple workflow
        workflow = await client.create_workflow(
            name="WebSocket Monitored Workflow",
            tasks=[
                {
                    "id": "task1",
                    "type": "simple_task",
                    "next": "task2"
                },
                {
                    "id": "task2",
                    "type": "simple_task"
                }
            ]
        )
        
        workflow_id = workflow["workflow_id"]
        logger.info(f"Created workflow with ID: {workflow_id}")
        
        # Execute the workflow
        execution = await client.execute_workflow(workflow_id=workflow_id)
        execution_id = execution["execution_id"]
        logger.info(f"Started execution with ID: {execution_id}")
        
        # In a real application, we would connect to the WebSocket endpoint:
        # ws://localhost:8002/ws/executions/{execution_id}
        logger.info(f"Would connect to: ws://localhost:8002/ws/executions/{execution_id}")
        
        # Simulate receiving events
        events = [
            {"event_type": "workflow_started", "execution_id": execution_id, "timestamp": time.time()},
            {"event_type": "task_started", "execution_id": execution_id, "task_id": "task1", "timestamp": time.time()},
            {"event_type": "task_completed", "execution_id": execution_id, "task_id": "task1", "timestamp": time.time()},
            {"event_type": "task_started", "execution_id": execution_id, "task_id": "task2", "timestamp": time.time()},
            {"event_type": "task_completed", "execution_id": execution_id, "task_id": "task2", "timestamp": time.time()},
            {"event_type": "workflow_completed", "execution_id": execution_id, "timestamp": time.time()}
        ]
        
        logger.info("Simulating WebSocket events:")
        for event in events:
            logger.info(f"  Event: {event['event_type']}, Task: {event.get('task_id', 'N/A')}")
            await asyncio.sleep(0.5)  # Simulate delay between events
    
    except Exception as e:
        logger.error(f"Error in WebSocket monitoring example: {e}")
    
    finally:
        # Close the client
        await client.close()


async def main():
    """Run all examples."""
    try:
        await simple_workflow_example()
        await parallel_workflow_example()
        await workflow_state_example()
        await error_handling_example()
        await template_instantiation_example()
        await websocket_monitoring_example()
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())