# Prometheus Integration Guide

This document provides guidance on integrating Prometheus with other Tekton components and external systems.

## Integration with Tekton Components

Prometheus integrates with multiple Tekton components to provide comprehensive planning and preparation capabilities.

### Integration with Telos

Prometheus connects with Telos to retrieve requirements and project constraints:

```python
from prometheus.utils.telos_connector import TelosConnector

async def initialize_telos_integration():
    """Initialize the connection with Telos."""
    telos_connector = TelosConnector(base_url="http://localhost:8008/api")
    
    # Import requirements from Telos
    project_id = "telos-project-id"
    requirements = await telos_connector.get_requirements(project_id)
    
    # Create a plan based on requirements
    plan = await telos_connector.create_plan_from_requirements(
        requirements, 
        dependency_mapping=True
    )
    
    return plan
```

#### Key Integration Points:

1. **Requirements Import**: Import requirements from Telos projects
2. **Dependency Extraction**: Extract dependencies from requirement relationships
3. **Validation Rules**: Apply requirement validation rules during planning
4. **Bidirectional Tracing**: Maintain traceability between requirements and plan tasks
5. **Status Updates**: Push task status updates to requirement verification state

### Integration with Rhetor

Prometheus uses Rhetor for LLM-powered plan analysis and improvement suggestions:

```python
from prometheus.utils.rhetor_adapter import RhetorAdapter

async def analyze_plan_with_llm(plan_id):
    """Use Rhetor to analyze a plan."""
    rhetor_adapter = RhetorAdapter(base_url="http://localhost:8003/api")
    
    # Get plan data
    plan_data = await get_plan_data(plan_id)
    
    # Analyze plan with LLM
    analysis = await rhetor_adapter.analyze_plan(
        plan_data,
        analysis_types=["risks", "optimizations", "recommendations"]
    )
    
    return analysis
```

#### Key Integration Points:

1. **Plan Analysis**: Analyze plans for risks and optimization opportunities
2. **Improvement Suggestions**: Generate improvement recommendations
3. **Retrospective Summarization**: Summarize retrospectives and extract insights
4. **Document Generation**: Generate documentation based on plans
5. **Budget Templates**: Apply specific prompting templates for planning tasks

### Integration with Engram

Prometheus stores and retrieves planning knowledge and historical project data in Engram:

```python
from prometheus.utils.engram_connector import EngramConnector

async def store_project_knowledge(plan_id, plan_data, metadata=None):
    """Store project knowledge in Engram."""
    engram_connector = EngramConnector(base_url="http://localhost:8001/api")
    
    # Store plan data
    memory_id = await engram_connector.store_plan(
        plan_id=plan_id,
        plan_data=plan_data,
        metadata=metadata,
        vector_embed=True
    )
    
    # Store relationships
    await engram_connector.store_plan_relationships(
        plan_id=plan_id,
        relationships=extract_relationships(plan_data)
    )
    
    return memory_id
```

#### Key Integration Points:

1. **Knowledge Storage**: Store planning knowledge and historical data
2. **Similarity Search**: Find similar past projects for reference
3. **Precedent Analysis**: Analyze past similar tasks for duration estimation
4. **Context Retrieval**: Retrieve relevant context during planning
5. **Relationship Storage**: Store relationships between plan elements

### Integration with Synthesis

Prometheus hands off plans to Synthesis for execution:

```python
from prometheus.utils.synthesis_connector import SynthesisConnector

async def execute_plan(plan_id):
    """Send a plan to Synthesis for execution."""
    synthesis_connector = SynthesisConnector(base_url="http://localhost:8009/api")
    
    # Get plan data
    plan_data = await get_plan_data(plan_id)
    
    # Transform plan to execution format
    execution_plan = transform_to_execution_plan(plan_data)
    
    # Send to Synthesis
    execution_id = await synthesis_connector.start_execution(execution_plan)
    
    # Set up progress callback
    await synthesis_connector.subscribe_to_execution_events(
        execution_id,
        callback_url="http://localhost:8006/api/executions/callbacks"
    )
    
    return execution_id
```

#### Key Integration Points:

1. **Plan Execution**: Send plans to Synthesis for execution
2. **Progress Tracking**: Receive execution progress updates
3. **Status Synchronization**: Keep plan status in sync with execution
4. **Task Completion**: Process task completion events
5. **Execution Adjustments**: Adjust execution based on plan changes

### Integration with Hermes

Prometheus registers with Hermes for service discovery and message passing:

```python
from prometheus.utils.hermes_helper import HermesHelper

async def register_with_hermes():
    """Register Prometheus with Hermes."""
    hermes_helper = HermesHelper(base_url="http://localhost:8000/api")
    
    # Register the component
    registration_result = await hermes_helper.register_component(
        component_id="prometheus",
        name="Prometheus Planning Engine",
        version="0.1.0",
        description="Planning and preparation component of Tekton",
        capabilities=["planning", "critical_path_analysis", "retrospectives"],
        endpoints={
            "http": "http://localhost:8006/api",
            "ws": "ws://localhost:8006/ws"
        }
    )
    
    # Subscribe to events
    await hermes_helper.subscribe_to_events(
        events=["telos.requirement.updated", "synthesis.execution.completed"]
    )
    
    return registration_result
```

#### Key Integration Points:

1. **Component Registration**: Register capabilities with Hermes
2. **Service Discovery**: Discover other components via Hermes
3. **Event Subscription**: Subscribe to relevant events
4. **Event Publication**: Publish events when plans change
5. **Message Passing**: Send and receive messages to/from other components

## Integration with External Systems

### HTTP APIs

Prometheus provides a RESTful API that can be integrated with external systems:

```python
import httpx

async def integrate_with_external_system():
    """Example of external system integration via HTTP."""
    async with httpx.AsyncClient() as client:
        # Get plans from Prometheus
        response = await client.get("http://localhost:8006/api/plans")
        plans = response.json()
        
        # Send plan data to external system
        external_response = await client.post(
            "https://external-system.example.com/api/import-plans",
            json=plans
        )
        
        return external_response.json()
```

### Webhooks

Prometheus supports webhooks for event notifications:

```python
from prometheus.api.app import app
from fastapi import FastAPI, Request

@app.post("/api/webhooks/register")
async def register_webhook(webhook: WebhookRegistration):
    """Register a webhook for event notifications."""
    webhook_id = await webhook_manager.register(
        url=webhook.url,
        events=webhook.events,
        secret=webhook.secret
    )
    return {"webhook_id": webhook_id}
```

To configure an external system to receive webhooks:

1. Register a webhook endpoint with Prometheus
2. Implement the webhook endpoint in your external system
3. Process the webhook payload when events occur

### File Export/Import

Prometheus supports file-based export and import for integration with systems that don't have APIs:

```python
@app.post("/api/plans/{plan_id}/export")
async def export_plan(plan_id: str, format: str = "json"):
    """Export a plan to a file format."""
    plan_data = await get_plan_data(plan_id)
    
    if format == "json":
        return JSONResponse(content=plan_data)
    elif format == "csv":
        return StreamingResponse(
            generate_csv(plan_data),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=plan_{plan_id}.csv"}
        )
    elif format == "mpp":
        return StreamingResponse(
            generate_mpp(plan_data),
            media_type="application/vnd.ms-project",
            headers={"Content-Disposition": f"attachment; filename=plan_{plan_id}.mpp"}
        )
    else:
        raise HTTPException(status_code=400, detail="Unsupported format")
```

## Integration Patterns

### Event-Driven Integration

Prometheus uses an event-driven architecture for real-time integration:

1. **Component publishes events**: When a state change occurs (e.g., plan updated)
2. **Hermes routes events**: To subscribed components
3. **Components react to events**: Process the event and update their state

Example:

```python
# Publishing an event
await hermes_helper.publish_event(
    event_type="prometheus.plan.updated",
    payload={
        "plan_id": plan_id,
        "updated_by": user_id,
        "timestamp": datetime.now().isoformat(),
        "changes": changes
    }
)

# Handling an event
@app.post("/api/events")
async def handle_event(event: Event):
    """Handle incoming events from Hermes."""
    if event.type == "telos.requirement.updated":
        await handle_requirement_update(event.payload)
    elif event.type == "synthesis.execution.completed":
        await handle_execution_completed(event.payload)
```

### Request-Response Integration

For synchronous operations, Prometheus uses a request-response pattern:

```python
# Making a request to another component
async def get_requirements_from_telos(project_id):
    """Get requirements from Telos."""
    url = await hermes_helper.get_component_endpoint("telos", "http")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{url}/projects/{project_id}/requirements")
        return response.json()

# Responding to a request from another component
@app.get("/api/plans/{plan_id}/for-execution")
async def get_plan_for_execution(plan_id: str):
    """Get a plan formatted for execution by Synthesis."""
    plan_data = await get_plan_data(plan_id)
    execution_plan = transform_to_execution_plan(plan_data)
    return execution_plan
```

### Shared Memory Integration

Prometheus uses Engram as shared memory for persistent integration:

```python
# Storing data for other components
async def store_shared_plan_data(plan_id, plan_data):
    """Store plan data in Engram for other components to access."""
    memory_id = await engram_connector.store(
        namespace="prometheus.plans",
        key=plan_id,
        data=plan_data,
        metadata={
            "component": "prometheus",
            "type": "plan",
            "timestamp": datetime.now().isoformat()
        }
    )
    return memory_id

# Retrieving data stored by other components
async def get_shared_requirement_data(requirement_id):
    """Get requirement data stored by Telos in Engram."""
    requirement_data = await engram_connector.retrieve(
        namespace="telos.requirements",
        key=requirement_id
    )
    return requirement_data
```

## Implementation Examples

### Creating a Plan from Telos Requirements

```python
async def create_plan_from_telos_requirements(project_id):
    """Create a plan based on Telos requirements."""
    # Get requirements from Telos
    telos_connector = TelosConnector(base_url="http://localhost:8008/api")
    requirements = await telos_connector.get_requirements(project_id)
    
    # Analyze requirements for planning
    rhetor_adapter = RhetorAdapter(base_url="http://localhost:8003/api")
    planning_analysis = await rhetor_adapter.analyze_requirements_for_planning(requirements)
    
    # Create plan structure
    plan = {
        "name": f"Plan for {project_id}",
        "description": "Auto-generated from Telos requirements",
        "start_date": datetime.now().isoformat(),
        "end_date": (datetime.now() + timedelta(days=30)).isoformat(),
        "requirements_source": project_id,
        "tasks": []
    }
    
    # Convert requirements to tasks
    for req in requirements:
        # Create task from requirement
        task = {
            "name": req["title"],
            "description": req["description"],
            "requirement_id": req["id"],
            "duration": planning_analysis["estimates"].get(req["id"], {}).get("duration", 5),
            "duration_unit": "days",
            "status": "pending",
            "priority": req.get("priority", "medium"),
            "dependencies": []
        }
        
        # Add dependencies
        for dep in req.get("dependencies", []):
            task["dependencies"].append(dep)
        
        plan["tasks"].append(task)
    
    # Create the plan in Prometheus
    client = PrometheusClient(base_url="http://localhost:8006/api")
    plan_id = await client.create_plan(
        name=plan["name"],
        description=plan["description"],
        start_date=plan["start_date"],
        end_date=plan["end_date"],
        metadata={"requirements_source": project_id}
    )
    
    # Add tasks to the plan
    for task in plan["tasks"]:
        await client.add_task(
            plan_id=plan_id,
            name=task["name"],
            description=task["description"],
            duration=task["duration"],
            duration_unit=task["duration_unit"],
            status=task["status"],
            priority=task["priority"],
            metadata={"requirement_id": task["requirement_id"]}
        )
    
    # Set up task dependencies
    for i, task in enumerate(plan["tasks"]):
        for dep in task["dependencies"]:
            # Find the task ID for the dependency
            for j, task2 in enumerate(plan["tasks"]):
                if task2["requirement_id"] == dep:
                    await client.add_dependency(
                        plan_id=plan_id,
                        task_id=f"task-{i+1}",
                        dependency_id=f"task-{j+1}"
                    )
    
    return plan_id
```

### Sending a Plan to Synthesis for Execution

```python
async def send_plan_to_synthesis(plan_id):
    """Send a plan to Synthesis for execution."""
    # Get plan data
    client = PrometheusClient(base_url="http://localhost:8006/api")
    plan = await client.get_plan(plan_id)
    tasks = await client.get_tasks(plan_id)
    
    # Transform to Synthesis execution format
    execution_plan = {
        "name": plan["name"],
        "description": plan["description"],
        "source": "prometheus",
        "source_id": plan_id,
        "steps": []
    }
    
    # Convert tasks to steps
    task_id_map = {}  # Maps Prometheus task IDs to Synthesis step IDs
    for i, task in enumerate(tasks):
        step_id = f"step_{i+1}"
        task_id_map[task["id"]] = step_id
        
        step = {
            "id": step_id,
            "name": task["name"],
            "description": task["description"],
            "type": determine_step_type(task),
            "parameters": determine_step_parameters(task),
            "dependencies": []  # Will be filled in later
        }
        
        execution_plan["steps"].append(step)
    
    # Add dependencies
    for task in tasks:
        if "dependencies" in task and task["dependencies"]:
            step_id = task_id_map[task["id"]]
            for dep_id in task["dependencies"]:
                if dep_id in task_id_map:
                    dep_step_id = task_id_map[dep_id]
                    for step in execution_plan["steps"]:
                        if step["id"] == step_id:
                            step["dependencies"].append(dep_step_id)
    
    # Send to Synthesis
    synthesis_connector = SynthesisConnector(base_url="http://localhost:8009/api")
    execution_id = await synthesis_connector.start_execution(execution_plan)
    
    # Update plan with execution ID
    await client.update_plan(
        plan_id=plan_id,
        metadata={"execution_id": execution_id}
    )
    
    # Set up progress tracking
    await synthesis_connector.subscribe_to_execution_events(
        execution_id,
        callback_url="http://localhost:8006/api/executions/callbacks"
    )
    
    return execution_id
```

## Troubleshooting Integration Issues

### Common Integration Problems

1. **Component Unavailability**:
   - Symptom: Connection errors when trying to integrate
   - Solution: Check if the component is running and registered with Hermes

2. **Authentication Issues**:
   - Symptom: 401/403 errors when making API calls
   - Solution: Ensure authentication tokens are valid and included in requests

3. **Data Format Mismatches**:
   - Symptom: 400 errors or data corruption
   - Solution: Validate data formats against the component's API specifications

4. **Missing Dependencies**:
   - Symptom: Functionality not working as expected
   - Solution: Ensure all required components are running and properly integrated

5. **Event Subscription Issues**:
   - Symptom: Not receiving expected events
   - Solution: Verify event subscriptions and check Hermes event routing

### Integration Logging

Enable detailed integration logging for troubleshooting:

```python
import logging

# Set up logger
logger = logging.getLogger("prometheus.integration")
logger.setLevel(logging.DEBUG)

# Set up handler
handler = logging.FileHandler("integration.log")
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

# Log integration events
async def log_integration_event(component, event_type, details=None):
    """Log an integration event."""
    logger.info(f"Integration with {component}: {event_type}")
    if details:
        logger.debug(f"Details: {details}")
```

## Environment Variables

Configure integration behavior with environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `PROMETHEUS_PORT` | Port for the Prometheus API | 8006 |
| `HERMES_URL` | URL of the Hermes API | http://localhost:8000/api |
| `TELOS_URL` | URL of the Telos API | http://localhost:8008/api |
| `RHETOR_URL` | URL of the Rhetor API | http://localhost:8003/api |
| `ENGRAM_URL` | URL of the Engram API | http://localhost:8001/api |
| `SYNTHESIS_URL` | URL of the Synthesis API | http://localhost:8009/api |
| `INTEGRATION_TIMEOUT` | Timeout for integration calls (seconds) | 30 |
| `INTEGRATION_RETRY_COUNT` | Number of retries for failed calls | 3 |
| `INTEGRATION_RETRY_DELAY` | Delay between retries (seconds) | 1 |
| `WEBHOOK_SECRET` | Secret for webhook signatures | random |

## Conclusion

Prometheus is designed to integrate seamlessly with the Tekton ecosystem and external systems. By following the patterns and examples in this guide, you can effectively connect Prometheus with other components to create comprehensive planning and execution workflows.