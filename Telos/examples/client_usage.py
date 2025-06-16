#!/usr/bin/env python3
"""
Example Usage of the Telos Client

This script demonstrates how to use the TelosClient and TelosUIClient to interact
with the Telos requirements management component.
"""

import asyncio
import logging
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("telos_example")

# Try to import from the telos package
try:
    from telos.client import TelosClient, TelosUIClient, get_telos_client, get_telos_ui_client
except ImportError:
    import sys
    import os
    
    # Add the parent directory to sys.path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    
    # Try importing again
    from telos.client import TelosClient, TelosUIClient, get_telos_client, get_telos_ui_client


async def project_management_example():
    """Example of using the Telos client for project management."""
    logger.info("=== Project Management Example ===")
    
    # Create a Telos client
    client = await get_telos_client()
    
    try:
        # Create a new project
        project_name = "API Development Project"
        project_description = "RESTful API development for the customer portal"
        project_metadata = {
            "priority": "high",
            "deadline": "2025-06-30",
            "stakeholders": ["Product", "Engineering", "QA"]
        }
        
        logger.info(f"Creating project: {project_name}")
        project = await client.create_project(
            name=project_name,
            description=project_description,
            metadata=project_metadata
        )
        
        project_id = project["project_id"]
        logger.info(f"Created project with ID: {project_id}")
        
        # Create requirements for the project
        requirements = [
            {
                "title": "User Authentication",
                "description": "Users must be able to authenticate using OAuth2 with support for multiple identity providers.",
                "priority": "high",
                "type": "functional"
            },
            {
                "title": "Rate Limiting",
                "description": "The API must implement rate limiting to prevent abuse and ensure fair usage.",
                "priority": "medium",
                "type": "security"
            },
            {
                "title": "Response Time",
                "description": "All API endpoints must respond within 200ms for 99% of requests under normal load.",
                "priority": "high",
                "type": "performance"
            }
        ]
        
        logger.info(f"Creating {len(requirements)} requirements for project {project_id}")
        for req in requirements:
            req_result = await client.create_requirement(
                project_id=project_id,
                title=req["title"],
                description=req["description"],
                priority=req["priority"],
                requirement_type=req["type"]
            )
            logger.info(f"Created requirement: {req['title']} with ID: {req_result['requirement_id']}")
        
        # Get project details
        logger.info(f"Getting details for project {project_id}")
        project_details = await client.get_project(project_id)
        logger.info(f"Project details: {project_details['name']} - {project_details['description']}")
        
        # Get requirements for the project
        logger.info(f"Getting requirements for project {project_id}")
        project_requirements = await client.get_requirements(project_id)
        logger.info(f"Found {len(project_requirements)} requirements")
        
        # Filter requirements by priority
        high_priority_reqs = await client.get_requirements(
            project_id,
            filters={"priority": "high"}
        )
        logger.info(f"Found {len(high_priority_reqs)} high-priority requirements")
    
    except Exception as e:
        logger.error(f"Error in project management example: {e}")
    
    finally:
        # Close the client
        await client.close()


async def requirements_analysis_example():
    """Example of using the Telos client for requirements analysis."""
    logger.info("=== Requirements Analysis Example ===")
    
    # Create a Telos client
    client = await get_telos_client()
    
    try:
        # First, we need a project with requirements
        project_name = "Mobile App Development"
        logger.info(f"Creating project: {project_name}")
        project = await client.create_project(name=project_name)
        project_id = project["project_id"]
        
        # Create several requirements
        requirements = [
            {
                "title": "Offline Mode",
                "description": "The app should work offline and sync when the connection is restored.",
                "priority": "high",
                "type": "functional"
            },
            {
                "title": "Push Notifications",
                "description": "Users should receive push notifications for important events.",
                "priority": "medium",
                "type": "functional"
            },
            {
                "title": "Battery Usage",
                "description": "The app should minimize battery usage.",
                "priority": "medium",
                "type": "non-functional"
            },
            {
                "title": "User Interface",
                "description": "The UI should be responsive and follow material design guidelines.",
                "priority": "high",
                "type": "ux"
            }
        ]
        
        for req in requirements:
            await client.create_requirement(
                project_id=project_id,
                title=req["title"],
                description=req["description"],
                priority=req["priority"],
                requirement_type=req["type"]
            )
        
        # Analyze requirements
        logger.info(f"Analyzing requirements for project {project_id}")
        analysis = await client.analyze_requirements(project_id)
        
        logger.info("Analysis results:")
        for key, value in analysis.get("analysis", {}).items():
            if isinstance(value, dict):
                logger.info(f"  {key}:")
                for subkey, subvalue in value.items():
                    logger.info(f"    {subkey}: {subvalue}")
            else:
                logger.info(f"  {key}: {value}")
        
        # Analyze requirements with specific analysis type
        logger.info(f"Performing quality analysis for project {project_id}")
        quality_analysis = await client.analyze_requirements(
            project_id,
            analysis_type="quality"
        )
        
        logger.info("Quality analysis results:")
        for key, value in quality_analysis.get("analysis", {}).get("quality", {}).items():
            logger.info(f"  {key}: {value}")
            
    except Exception as e:
        logger.error(f"Error in requirements analysis example: {e}")
    
    finally:
        # Close the client
        await client.close()


async def requirement_refinement_example():
    """Example of using the Telos client for requirement refinement."""
    logger.info("=== Requirement Refinement Example ===")
    
    # Create a Telos client
    client = await get_telos_client()
    
    try:
        # First, we need a project with a requirement
        project = await client.create_project(name="Data Processing Pipeline")
        project_id = project["project_id"]
        
        # Create a requirement that needs refinement
        vague_requirement = await client.create_requirement(
            project_id=project_id,
            title="Data Processing Performance",
            description="The system must process data quickly and efficiently.",
            priority="high",
            requirement_type="performance"
        )
        
        requirement_id = vague_requirement["requirement_id"]
        logger.info(f"Created vague requirement with ID: {requirement_id}")
        
        # Refine the requirement with feedback
        feedback = (
            "This requirement is too vague. We need specific metrics for 'quickly' and "
            "'efficiently'. Consider specifying throughput, latency, and resource utilization "
            "targets. Also, define different requirements for batch vs. real-time processing."
        )
        
        logger.info(f"Refining requirement {requirement_id} with feedback")
        refined_requirement = await client.refine_requirement(
            requirement_id=requirement_id,
            feedback=feedback
        )
        
        logger.info("Refined requirement:")
        logger.info(f"  Title: {refined_requirement.get('title')}")
        logger.info(f"  Description: {refined_requirement.get('description')}")
        logger.info(f"  Priority: {refined_requirement.get('priority')}")
        logger.info(f"  Type: {refined_requirement.get('type')}")
    
    except Exception as e:
        logger.error(f"Error in requirement refinement example: {e}")
    
    finally:
        # Close the client
        await client.close()


async def telos_ui_example():
    """Example of using the Telos UI client."""
    logger.info("=== Telos UI Example ===")
    
    # Create Telos clients
    telos_client = await get_telos_client()
    ui_client = await get_telos_ui_client()
    
    try:
        # First, we need a project with requirements
        project = await telos_client.create_project(name="Website Redesign")
        project_id = project["project_id"]
        
        # Create some requirements
        requirement = await telos_client.create_requirement(
            project_id=project_id,
            title="Responsive Design",
            description="The website must be fully responsive and work on all device sizes.",
            priority="high",
            requirement_type="ux"
        )
        
        requirement_id = requirement["requirement_id"]
        
        # Use the UI client for interactive refinement
        logger.info(f"Starting interactive refinement for requirement {requirement_id}")
        refinement_session = await ui_client.interactive_refine(
            project_id=project_id,
            requirement_id=requirement_id
        )
        
        logger.info(f"Started refinement session with ID: {refinement_session.get('session_id')}")
        logger.info(f"Session URL: {refinement_session.get('session_url')}")
        
        # Generate a visualization for the project
        logger.info(f"Generating dependency visualization for project {project_id}")
        visualization = await ui_client.visualize_project(
            project_id=project_id,
            visualization_type="dependency"
        )
        
        logger.info(f"Visualization URL: {visualization.get('visualization', {}).get('url')}")
        logger.info(f"Visualization format: {visualization.get('visualization', {}).get('format')}")
    
    except Exception as e:
        logger.error(f"Error in Telos UI example: {e}")
    
    finally:
        # Close the clients
        await telos_client.close()
        await ui_client.close()


async def error_handling_example():
    """Example of handling errors with the Telos client."""
    logger.info("=== Error Handling Example ===")
    
    # Create a Telos client with a non-existent component ID
    try:
        client = await get_telos_client(component_id="telos.nonexistent")
        # This should raise ComponentNotFoundError
        
    except Exception as e:
        logger.info(f"Caught expected error: {type(e).__name__}: {e}")
    
    # Create a valid client
    client = await get_telos_client()
    
    try:
        # Try to invoke a non-existent capability
        try:
            await client.invoke_capability("nonexistent_capability", {})
        except Exception as e:
            logger.info(f"Caught expected error: {type(e).__name__}: {e}")
            
        # Try to get a non-existent project
        try:
            await client.get_project("nonexistent-project-id")
        except Exception as e:
            logger.info(f"Caught expected error: {type(e).__name__}: {e}")
    
    finally:
        # Close the client
        await client.close()


async def main():
    """Run all examples."""
    try:
        await project_management_example()
        await requirements_analysis_example()
        await requirement_refinement_example()
        await telos_ui_example()
        await error_handling_example()
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())