#!/usr/bin/env python3
"""
Hermes Registration Example

This script demonstrates how to use the Hermes service registration and discovery system.
It shows how to register services, discover other services, and update service health.
"""

import asyncio
import time
import random
import os
from pathlib import Path
import uuid
from datetime import datetime

# Ensure Hermes is in Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from hermes.core.registration import ServiceRegistry
from hermes.core.logging import get_logger, configure_logging

# Configure logging
configure_logging(level="INFO")
logger = get_logger("hermes.examples.registration")

async def register_service(registry, service_type, name, capabilities):
    """Register a service with the registry."""
    # Generate a unique ID for the service
    service_id = f"{service_type}-{uuid.uuid4().hex[:8]}"
    
    # Register the service
    success = await registry.register(
        service_id=service_id,
        name=name,
        version="1.0.0",
        endpoint=f"http://localhost:{10000 + random.randint(1000, 9999)}",
        capabilities=capabilities,
        metadata={
            "type": service_type,
            "environment": "development",
            "created_at": datetime.now().isoformat()
        }
    )
    
    if success:
        logger.info(f"Successfully registered service: {name} ({service_id})")
    else:
        logger.error(f"Failed to register service: {name}")
    
    return service_id

async def update_service_health(registry, service_id, status="healthy"):
    """Update the health status of a service."""
    # Generate random metrics
    metrics = {
        "response_time_ms": random.randint(10, 500),
        "requests_per_minute": random.randint(1, 100),
        "error_rate": random.random() * 0.1,  # 0-10% error rate
        "memory_usage_mb": random.randint(50, 500)
    }
    
    # Update health status
    success = await registry.update_health(
        service_id=service_id,
        status=status,
        metrics=metrics
    )
    
    if success:
        logger.info(f"Updated health for service {service_id}: {status}")
    else:
        logger.warning(f"Failed to update health for service {service_id}")
    
    return success

async def discover_services(registry, capabilities=None, status=None):
    """Discover services based on capabilities and status."""
    # Find services
    services = await registry.find_services(capabilities=capabilities, status=status)
    
    logger.info(f"Found {len(services)} services matching criteria:")
    logger.info(f"  Capabilities: {capabilities or 'any'}")
    logger.info(f"  Status: {status or 'any'}")
    
    for service in services:
        logger.info(f"  - {service['name']} ({service['service_id']})")
        logger.info(f"    Capabilities: {service['capabilities']}")
        logger.info(f"    Status: {service.get('status', 'unknown')}")
        logger.info(f"    Endpoint: {service['endpoint']}")
    
    return services

async def registration_example():
    """Demonstrate service registration and discovery."""
    logger.info("=== Service Registration Example ===")
    
    # Initialize service registry
    registry = ServiceRegistry()
    
    # Start the registry
    await registry.start()
    logger.info("Service registry started")
    
    # Register different types of services
    llm_service_id = await register_service(
        registry=registry,
        service_type="llm",
        name="Claude 3 Opus",
        capabilities=["llm", "reasoning", "tool_use", "image_understanding"]
    )
    
    memory_service_id = await register_service(
        registry=registry,
        service_type="memory",
        name="Engram Memory Service",
        capabilities=["memory", "vector_search"]
    )
    
    tools_service_id = await register_service(
        registry=registry,
        service_type="tools",
        name="Ergon Tool Registry",
        capabilities=["tool_registry", "tool_execution"]
    )
    
    knowledge_service_id = await register_service(
        registry=registry,
        service_type="knowledge",
        name="Athena Knowledge Graph",
        capabilities=["knowledge_graph", "reasoning"]
    )
    
    # Update health status for services
    await update_service_health(registry, llm_service_id, "healthy")
    await update_service_health(registry, memory_service_id, "healthy")
    await update_service_health(registry, tools_service_id, "healthy")
    
    # Set one service as degraded
    await update_service_health(registry, knowledge_service_id, "degraded")
    
    # Wait a moment for updates to propagate
    await asyncio.sleep(1)
    
    # Discover all services
    all_services = await discover_services(registry)
    
    # Discover services by capability
    llm_services = await discover_services(registry, capabilities=["llm"])
    memory_services = await discover_services(registry, capabilities=["memory"])
    
    # Discover services by status
    healthy_services = await discover_services(registry, status="healthy")
    degraded_services = await discover_services(registry, status="degraded")
    
    # Discover services by both capability and status
    healthy_reasoning_services = await discover_services(
        registry, 
        capabilities=["reasoning"],
        status="healthy"
    )
    
    # Get a specific service
    try:
        service_info = await registry.get_service(llm_service_id)
        logger.info(f"Retrieved specific service: {service_info['name']}")
        logger.info(f"  Capabilities: {service_info['capabilities']}")
        logger.info(f"  Status: {service_info.get('status', 'unknown')}")
    except Exception as e:
        logger.error(f"Error retrieving specific service: {e}")
    
    # Update a service to unhealthy
    await update_service_health(registry, tools_service_id, "unhealthy")
    
    # Discover only healthy services
    healthy_services_after = await discover_services(registry, status="healthy")
    
    # Cleanup (optional)
    logger.info("Cleanup: Unregistering services")
    await registry.unregister(llm_service_id)
    await registry.unregister(memory_service_id)
    await registry.unregister(tools_service_id)
    await registry.unregister(knowledge_service_id)
    
    # Stop the registry
    await registry.stop()
    logger.info("Service registry stopped")

async def service_monitoring_simulation():
    """Simulate continuous service monitoring."""
    logger.info("\n=== Service Monitoring Simulation ===")
    
    # Initialize service registry
    registry = ServiceRegistry()
    await registry.start()
    
    # Register a service
    service_id = await register_service(
        registry=registry,
        service_type="api",
        name="Simulation API Service",
        capabilities=["api", "http"]
    )
    
    # Simulate service operation for 30 seconds
    logger.info(f"Simulating service operation for 30 seconds (service: {service_id})")
    
    start_time = time.time()
    while time.time() - start_time < 30:
        # Determine a random health status
        # 80% chance of healthy, 15% chance of degraded, 5% chance of unhealthy
        status_roll = random.random()
        if status_roll < 0.8:
            status = "healthy"
        elif status_roll < 0.95:
            status = "degraded"
        else:
            status = "unhealthy"
        
        # Update service health
        await update_service_health(registry, service_id, status)
        
        # Get current service information from registry
        try:
            service_info = await registry.get_service(service_id)
            metrics = service_info.get("metrics", {})
            
            logger.info(f"Service status: {service_info.get('status', 'unknown')}")
            if metrics:
                logger.info(f"  Response time: {metrics.get('response_time_ms')}ms")
                logger.info(f"  Requests/min: {metrics.get('requests_per_minute')}")
                logger.info(f"  Error rate: {metrics.get('error_rate'):.2%}")
                logger.info(f"  Memory usage: {metrics.get('memory_usage_mb')}MB")
        except Exception as e:
            logger.error(f"Error getting service info: {e}")
        
        # Wait for next update
        await asyncio.sleep(5)
    
    # Cleanup
    await registry.unregister(service_id)
    await registry.stop()
    logger.info("Service monitoring simulation complete")

async def service_discovery_demo():
    """Demonstrate looking up services based on capabilities."""
    logger.info("\n=== Service Discovery Demo ===")
    
    # Initialize service registry
    registry = ServiceRegistry()
    await registry.start()
    
    # Register several services with different capabilities
    service_ids = []
    
    # Register LLMs
    service_ids.append(await register_service(
        registry=registry,
        service_type="llm",
        name="Claude 3 Opus",
        capabilities=["llm", "reasoning", "tool_use", "image_understanding"]
    ))
    
    service_ids.append(await register_service(
        registry=registry,
        service_type="llm",
        name="Claude 3 Sonnet",
        capabilities=["llm", "reasoning", "tool_use"]
    ))
    
    service_ids.append(await register_service(
        registry=registry,
        service_type="llm",
        name="Claude 3 Haiku",
        capabilities=["llm", "reasoning"]
    ))
    
    # Register Databases
    service_ids.append(await register_service(
        registry=registry,
        service_type="database",
        name="Vector Database",
        capabilities=["database", "vector_search", "embedding"]
    ))
    
    service_ids.append(await register_service(
        registry=registry,
        service_type="database",
        name="Graph Database",
        capabilities=["database", "graph", "query"]
    ))
    
    service_ids.append(await register_service(
        registry=registry,
        service_type="database",
        name="Key-Value Database",
        capabilities=["database", "key_value", "cache"]
    ))
    
    # Register Tools
    service_ids.append(await register_service(
        registry=registry,
        service_type="tool",
        name="Web Search Tool",
        capabilities=["tool", "web_search", "external"]
    ))
    
    service_ids.append(await register_service(
        registry=registry,
        service_type="tool",
        name="Code Execution Tool",
        capabilities=["tool", "code_execution", "sandbox"]
    ))
    
    # Update health for all services
    for service_id in service_ids:
        await update_service_health(registry, service_id, "healthy")
    
    # Simulate application looking for appropriate services
    logger.info("\nSimulating application searching for appropriate services:")
    
    # Scenario 1: Need an LLM with image understanding
    logger.info("\nScenario 1: Looking for an LLM with image understanding capability")
    image_capable_llms = await discover_services(
        registry,
        capabilities=["llm", "image_understanding"],
        status="healthy"
    )
    
    if image_capable_llms:
        logger.info(f"Found {len(image_capable_llms)} suitable services for image tasks")
        for service in image_capable_llms:
            logger.info(f"  Selected: {service['name']}")
    else:
        logger.info("No suitable services found for image tasks")
    
    # Scenario 2: Need any database service
    logger.info("\nScenario 2: Looking for any available database service")
    databases = await discover_services(
        registry,
        capabilities=["database"],
        status="healthy"
    )
    
    if databases:
        logger.info(f"Found {len(databases)} database services")
        random_db = random.choice(databases)
        logger.info(f"  Randomly selected: {random_db['name']}")
        logger.info(f"  Capabilities: {random_db['capabilities']}")
    else:
        logger.info("No database services found")
    
    # Scenario 3: Need a vector database specifically
    logger.info("\nScenario 3: Looking for a vector database specifically")
    vector_dbs = await discover_services(
        registry,
        capabilities=["database", "vector_search"],
        status="healthy"
    )
    
    if vector_dbs:
        logger.info(f"Found {len(vector_dbs)} vector database services")
        for service in vector_dbs:
            logger.info(f"  Selected: {service['name']}")
    else:
        logger.info("No vector database services found")
    
    # Cleanup
    for service_id in service_ids:
        await registry.unregister(service_id)
    
    await registry.stop()
    logger.info("Service discovery demo complete")

async def main():
    """Run all registration examples."""
    try:
        logger.info("Starting Hermes registration examples")
        
        # Basic registration example
        await registration_example()
        
        # Service discovery demo
        await service_discovery_demo()
        
        # Uncomment to run the longer monitoring simulation
        # await service_monitoring_simulation()
        
        logger.info("All registration examples completed successfully")
        
    except Exception as e:
        logger.error(f"Error in registration examples: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Ensure registry is stopped
        logger.info("Registration examples complete")

if __name__ == "__main__":
    asyncio.run(main())