# Telos Integration Guide

This guide provides comprehensive information on integrating Telos with other Tekton components and external systems.

## Overview

Telos is designed to integrate seamlessly with the Tekton ecosystem and external tools through standardized interfaces. This document covers:

1. Integration with other Tekton components
2. Client libraries for programmatic access
3. UI integration with Hephaestus
4. WebSocket real-time updates
5. Export/Import capabilities
6. External system integration

## Integration with Tekton Components

### Hermes Integration

Telos registers with Hermes for service discovery and message passing:

```python
from tekton.utils.hermes_helper import HermesHelper

async def register_with_hermes():
    """Register Telos with Hermes."""
    hermes = HermesHelper()
    
    # Register component
    result = await hermes.register_component(
        component_id="telos",
        name="Telos Requirements Manager",
        version="1.0.0",
        description="Requirements management and tracing system",
        capabilities=[
            "requirements_management",
            "requirements_tracking",
            "requirements_validation",
            "requirements_visualization"
        ],
        endpoints={
            "http": "http://localhost:8008/api",
            "ws": "ws://localhost:8008/ws"
        }
    )
    
    # Subscribe to events
    if result.success:
        await hermes.subscribe_to_events([
            "prometheus.plan.created",
            "prometheus.task.updated"
        ])
    
    return result
```

Key integration points with Hermes:

1. **Service Registration**: Register capabilities and endpoints
2. **Service Discovery**: Discover other components via Hermes
3. **Event Subscription**: Subscribe to relevant events
4. **Event Publication**: Publish events when requirements change
5. **Message Passing**: Send and receive messages

### Prometheus Integration

Telos integrates with Prometheus for planning and execution:

```python
from telos.prometheus_connector import PrometheusConnector

async def create_plan_from_requirements(project_id, requirement_ids=None):
    """Create a Prometheus plan from Telos requirements."""
    connector = PrometheusConnector()
    
    # Get requirements
    requirements = await get_requirements(project_id, requirement_ids)
    
    # Transform requirements to plan format
    plan_data = {
        "name": f"Plan for {project_id}",
        "description": "Generated from Telos requirements",
        "requirements": requirements,
        "source": {
            "component": "telos",
            "project_id": project_id
        }
    }
    
    # Create plan in Prometheus
    plan_id = await connector.create_plan(plan_data)
    
    # Update requirements with plan reference
    for req_id in requirement_ids:
        await update_requirement(
            project_id, req_id,
            metadata={
                "plan_id": plan_id,
                "plan_created_at": datetime.now().isoformat()
            }
        )
    
    return plan_id
```

Key integration points with Prometheus:

1. **Plan Creation**: Convert requirements to Prometheus plans
2. **Task Tracking**: Link requirements to plan tasks
3. **Progress Updates**: Receive task status updates for requirement verification
4. **Impact Analysis**: Analyze plan changes against requirements
5. **Execution Readiness**: Validate requirements before planning

### Rhetor Integration

Telos uses Rhetor for LLM-powered requirement refinement:

```python
from telos.rhetor_adapter import RhetorAdapter

async def refine_requirement(project_id, requirement_id, feedback=None):
    """Refine a requirement using Rhetor's LLM capabilities."""
    rhetor = RhetorAdapter()
    
    # Get requirement
    requirement = await get_requirement(project_id, requirement_id)
    
    # Generate refinement prompt
    prompt = generate_refinement_prompt(requirement, feedback)
    
    # Get LLM refinement
    result = await rhetor.generate_completion(
        prompt=prompt,
        model="llm-model-id",
        temperature=0.4,
        max_tokens=1000
    )
    
    # Parse and apply refinements
    refined_requirement = parse_refinement_result(result.completion)
    
    # Update the requirement
    updated = await update_requirement(
        project_id,
        requirement_id,
        **refined_requirement,
        metadata={
            **requirement.metadata,
            "last_refined": datetime.now().isoformat(),
            "refinement_feedback": feedback
        }
    )
    
    return updated
```

Key integration points with Rhetor:

1. **Requirement Refinement**: Improve requirement quality with LLM
2. **Validation Analysis**: Evaluate requirements for completeness and clarity
3. **Natural Language Processing**: Extract key information from requirements
4. **Dependency Detection**: Identify implicit dependencies between requirements
5. **Requirements Generation**: Generate new requirements from high-level descriptions

### Engram Integration

Telos stores requirement knowledge and history in Engram:

```python
from telos.engram_connector import EngramConnector

async def store_requirement_knowledge(project_id, requirement_id):
    """Store requirement knowledge in Engram."""
    engram = EngramConnector()
    
    # Get requirement with full context
    requirement = await get_requirement_with_context(project_id, requirement_id)
    
    # Store in Engram
    memory_id = await engram.store_memory(
        namespace="telos.requirements",
        key=f"{project_id}.{requirement_id}",
        data=requirement,
        metadata={
            "component": "telos",
            "project_id": project_id,
            "requirement_id": requirement_id,
            "title": requirement.title,
            "type": requirement.requirement_type,
            "priority": requirement.priority,
            "status": requirement.status
        },
        vector_embed=True
    )
    
    return memory_id
```

Key integration points with Engram:

1. **Knowledge Storage**: Store requirements and their relationships
2. **Context Retrieval**: Retrieve relevant context for requirements
3. **Similarity Search**: Find similar requirements across projects
4. **Historical Analysis**: Track requirement changes over time
5. **Vector Embeddings**: Semantic search for related requirements

## Client Libraries

### Python Client

Telos provides a Python client library for programmatic access:

```python
from telos.client import TelosClient

async def use_telos_client():
    """Example of using the Telos client."""
    client = TelosClient(base_url="http://localhost:8008/api")
    
    try:
        # Create a project
        project = await client.create_project(
            name="Client Project",
            description="Created via the Python client"
        )
        
        # Add a requirement
        requirement = await client.create_requirement(
            project_id=project["project_id"],
            title="API Feature",
            description="This requirement was created via the client API",
            requirement_type="functional",
            priority="high"
        )
        
        # Validate requirements
        validation = await client.validate_requirements(
            project_id=project["project_id"],
            requirement_ids=[requirement["requirement_id"]],
            validation_types=["completeness", "clarity", "testability"]
        )
        
        return validation
    finally:
        await client.close()
```

### JavaScript/TypeScript Client

For frontend integration, Telos provides a JavaScript/TypeScript client:

```typescript
import { TelosClient } from '@tekton/telos-client';

async function useTelosClient() {
    const client = new TelosClient({
        baseUrl: 'http://localhost:8008/api'
    });
    
    try {
        // Create a project
        const project = await client.createProject({
            name: 'JS Client Project',
            description: 'Created via the JavaScript client'
        });
        
        // Add a requirement
        const requirement = await client.createRequirement(
            project.projectId,
            {
                title: 'Frontend Feature',
                description: 'This requirement was created via the JS client',
                requirementType: 'functional',
                priority: 'high'
            }
        );
        
        // Subscribe to updates
        const unsubscribe = client.subscribeToRequirementUpdates(
            project.projectId,
            requirement.requirementId,
            (update) => {
                console.log('Requirement updated:', update);
            }
        );
        
        return requirement;
    } finally {
        client.dispose();
    }
}
```

### CLI Client

For command-line integration, Telos provides a comprehensive CLI tool:

```bash
# Basic usage
telos --help

# Create a project
telos project create --name "CLI Project" --description "Created via CLI"

# Add a requirement
telos requirement add \
    --project-id proj-123abc \
    --title "CLI Feature" \
    --description "This requirement was created via the CLI" \
    --type functional \
    --priority high

# Export a project
telos project export \
    --project-id proj-123abc \
    --format json \
    --output ./project_export.json

# Analyze requirements for planning
telos requirement analyze \
    --project-id proj-123abc \
    --output ./analysis.json
```

## UI Integration

### Hephaestus Integration

Telos provides a web component for integration with Hephaestus:

```html
<!-- Include the component -->
<script src="telos-component.js"></script>
<link rel="stylesheet" href="telos-component.css">

<!-- Basic usage -->
<telos-requirements 
    project-id="proj-123abc"
    show-tree="true"
    edit-mode="true">
</telos-requirements>

<!-- Customized usage -->
<telos-requirements 
    project-id="proj-123abc"
    show-tree="true"
    edit-mode="true"
    theme="dark"
    filter-status="new,in_progress"
    onselect="handleRequirementSelect">
</telos-requirements>
```

JavaScript integration with the component:

```javascript
// Get a reference to the component
const telosComponent = document.querySelector('telos-requirements');

// Set up event listeners
telosComponent.addEventListener('requirementSelect', (event) => {
    console.log('Selected requirement:', event.detail);
});

telosComponent.addEventListener('requirementUpdate', (event) => {
    console.log('Updated requirement:', event.detail);
});

// Programmatic control
telosComponent.setProject('proj-456def');
telosComponent.refreshData();
telosComponent.expandAll();
telosComponent.collapseAll();
```

### WebSocket Integration

For real-time updates, Telos provides a WebSocket interface:

```javascript
// Create WebSocket connection
const ws = new WebSocket('ws://localhost:8008/ws');

// Initial setup
ws.onopen = () => {
    console.log('Connected to Telos WebSocket');
    
    // Register client
    ws.send(JSON.stringify({
        type: 'REGISTER',
        source: 'client',
        target: 'server',
        timestamp: Date.now(),
        payload: {
            client_id: generateClientId(),
            user_info: {
                name: 'Integration User',
                role: 'developer'
            }
        }
    }));
    
    // Subscribe to project updates
    ws.send(JSON.stringify({
        type: 'PROJECT_SUBSCRIBE',
        source: 'client',
        target: 'server',
        timestamp: Date.now(),
        payload: {
            project_id: 'proj-123abc'
        }
    }));
};

// Handle incoming messages
ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    
    switch (message.type) {
        case 'WELCOME':
            console.log('Server welcome:', message.payload.message);
            break;
        case 'REQUIREMENT_UPDATE':
            handleRequirementUpdate(message.payload);
            break;
        case 'TRACE_UPDATE':
            handleTraceUpdate(message.payload);
            break;
        case 'ERROR':
            console.error('Server error:', message.payload.message);
            break;
        default:
            console.log('Received message:', message);
    }
};

// Clean up
window.addEventListener('beforeunload', () => {
    if (ws.readyState === WebSocket.OPEN) {
        ws.close();
    }
});
```

## Export/Import Capabilities

### JSON Export/Import

Telos supports exporting and importing projects in JSON format:

```python
from telos.export_import import export_project, import_project

async def export_project_to_file(project_id, output_path):
    """Export a project to a JSON file."""
    # Export project
    project_data = await export_project(
        project_id=project_id,
        include_history=True,
        include_traces=True,
        include_validation=True
    )
    
    # Write to file
    with open(output_path, 'w') as f:
        json.dump(project_data, f, indent=2)
    
    return output_path

async def import_project_from_file(input_path):
    """Import a project from a JSON file."""
    # Read file
    with open(input_path, 'r') as f:
        project_data = json.load(f)
    
    # Import project
    imported_project = await import_project(
        project_data=project_data,
        new_project_name=f"{project_data['name']} (Imported)",
        keep_original_ids=False
    )
    
    return imported_project
```

### CSV Export/Import

For integration with spreadsheet tools, Telos supports CSV format:

```python
from telos.export_import import export_requirements_to_csv, import_requirements_from_csv

async def export_requirements_to_csv_file(project_id, output_path):
    """Export requirements to a CSV file."""
    requirements_csv = await export_requirements_to_csv(
        project_id=project_id,
        include_metadata=True
    )
    
    with open(output_path, 'w') as f:
        f.write(requirements_csv)
    
    return output_path

async def import_requirements_from_csv_file(project_id, input_path):
    """Import requirements from a CSV file."""
    with open(input_path, 'r') as f:
        csv_content = f.read()
    
    imported_requirements = await import_requirements_from_csv(
        project_id=project_id,
        csv_content=csv_content,
        update_existing=True,
        skip_missing_fields=True
    )
    
    return imported_requirements
```

### ReqIF Export/Import

For industry-standard requirements interchange, Telos supports ReqIF format:

```python
from telos.export_import import export_to_reqif, import_from_reqif

async def export_project_to_reqif(project_id, output_path):
    """Export a project to a ReqIF file."""
    reqif_content = await export_to_reqif(
        project_id=project_id,
        include_attributes=True
    )
    
    with open(output_path, 'wb') as f:
        f.write(reqif_content)
    
    return output_path

async def import_project_from_reqif(input_path):
    """Import a project from a ReqIF file."""
    with open(input_path, 'rb') as f:
        reqif_content = f.read()
    
    imported_project = await import_from_reqif(
        reqif_content=reqif_content,
        create_new_project=True
    )
    
    return imported_project
```

## External System Integration

### Webhooks

Telos provides webhooks for event notifications to external systems:

```python
# Webhook registration
@app.post("/api/webhooks/register")
async def register_webhook(webhook: WebhookRegistration):
    """Register a webhook for event notifications."""
    webhook_id = await webhook_manager.register(
        url=webhook.url,
        events=webhook.events,
        secret=webhook.secret
    )
    return {"webhook_id": webhook_id}

# Example webhook payload
webhook_payload = {
    "event_type": "requirement.updated",
    "timestamp": "2025-04-15T10:30:00Z",
    "project_id": "proj-123abc",
    "requirement_id": "req-789xyz",
    "changes": {
        "status": {
            "old": "new",
            "new": "in_progress"
        },
        "priority": {
            "old": "medium",
            "new": "high"
        }
    },
    "user": "jane.smith@example.com",
    "signature": "generated_using_secret"
}
```

### REST API Authentication

For secure external access, Telos supports token-based authentication:

```python
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

# API security
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Validate the JWT token and return the user."""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(token_data.username)
    if user is None:
        raise credentials_exception
    return user

# Protected endpoint example
@app.get("/api/projects", response_model=List[Project])
async def list_projects(current_user: User = Depends(get_current_user)):
    """List all projects (requires authentication)."""
    return await requirements_manager.get_all_projects(user_id=current_user.id)
```

### Custom Integration Adapters

For specialized integrations, Telos provides a framework for custom adapters:

```python
from telos.integration.adapter_base import IntegrationAdapter

class JiraAdapter(IntegrationAdapter):
    """Adapter for JIRA integration."""
    
    def __init__(self, base_url, username, api_token):
        """Initialize the JIRA adapter."""
        self.base_url = base_url
        self.auth = (username, api_token)
        self.session = None
    
    async def initialize(self):
        """Initialize the adapter."""
        self.session = aiohttp.ClientSession(auth=aiohttp.BasicAuth(*self.auth))
        return True
    
    async def import_requirements(self, project_id, jira_project_key):
        """Import requirements from JIRA issues."""
        # Implementation
    
    async def export_requirements(self, project_id, jira_project_key):
        """Export requirements to JIRA issues."""
        # Implementation
    
    async def sync_status(self, project_id, jira_project_key):
        """Synchronize status between requirements and JIRA issues."""
        # Implementation
    
    async def dispose(self):
        """Clean up resources."""
        if self.session:
            await self.session.close()
```

## Integration Patterns

### Event-Driven Integration

Telos uses an event-driven architecture for loose coupling:

```python
# Publishing events
async def publish_requirement_updated_event(
    project_id, requirement_id, changes, user=None
):
    """Publish a requirement updated event."""
    event = {
        "event_type": "telos.requirement.updated",
        "timestamp": datetime.now().isoformat(),
        "source": "telos",
        "project_id": project_id,
        "requirement_id": requirement_id,
        "changes": changes,
        "user": user
    }
    
    # Publish to Hermes
    await hermes_helper.publish_event(event)
    
    # Notify webhooks
    await webhook_manager.notify(
        event_type="requirement.updated",
        payload=event
    )
    
    # Send WebSocket updates
    await websocket_manager.broadcast_to_project(
        project_id=project_id,
        message_type="REQUIREMENT_UPDATE",
        payload={
            "project_id": project_id,
            "requirement_id": requirement_id,
            "changes": changes,
            "timestamp": event["timestamp"]
        }
    )
```

### Synchronous Integration

For immediate interactions, Telos provides synchronous APIs:

```python
# Direct API call to Prometheus
async def create_plan_directly(project_id, requirement_ids):
    """Create a plan in Prometheus directly."""
    async with httpx.AsyncClient() as client:
        # Get requirements
        requirements = await get_requirements_for_planning(project_id, requirement_ids)
        
        # Create plan in Prometheus
        response = await client.post(
            "http://localhost:8006/api/plans",
            json={
                "name": f"Plan for {project_id}",
                "description": "Created from Telos requirements",
                "requirements": requirements,
                "metadata": {
                    "source": "telos",
                    "project_id": project_id
                }
            }
        )
        
        response.raise_for_status()
        return response.json()
```

### Batch Integration

For efficient processing, Telos supports batch operations:

```python
# Batch import requirements
@app.post("/api/projects/{project_id}/requirements/batch")
async def batch_import_requirements(
    project_id: str,
    requirements: List[RequirementCreateRequest]
):
    """Import multiple requirements in a single operation."""
    results = []
    
    for req in requirements:
        try:
            result = await requirements_manager.add_requirement(
                project_id=project_id,
                title=req.title,
                description=req.description,
                **req.dict(exclude={"title", "description"})
            )
            results.append({
                "status": "success",
                "requirement_id": result,
                "title": req.title
            })
        except Exception as e:
            results.append({
                "status": "error",
                "title": req.title,
                "error": str(e)
            })
    
    return {
        "results": results,
        "total": len(requirements),
        "success_count": sum(1 for r in results if r["status"] == "success"),
        "error_count": sum(1 for r in results if r["status"] == "error")
    }
```

## Implementation Examples

### Complete Prometheus Integration Example

```python
from telos.prometheus_connector import PrometheusConnector

async def integrate_telos_with_prometheus(project_id, requirement_ids=None):
    """Complete example of Prometheus integration."""
    prometheus = PrometheusConnector()
    
    try:
        # 1. Get all requirements if specific IDs not provided
        if not requirement_ids:
            requirements = await get_all_requirements(project_id)
            requirement_ids = [r["requirement_id"] for r in requirements]
        else:
            requirements = await get_requirements(project_id, requirement_ids)
        
        # 2. Analyze requirements for planning readiness
        analysis = await prometheus.analyze_requirements(
            requirements,
            analysis_types=["complexity", "dependencies", "estimation"]
        )
        
        # 3. Handle requirements that need improvement
        if analysis["planning_readiness"] < 0.7:
            print("Requirements need improvement before planning")
            for recommendation in analysis["recommendations"]:
                print(f"- {recommendation}")
            
            # Optional: Auto-improve requirements with Rhetor
            if auto_improve:
                await improve_requirements(
                    project_id,
                    analysis["improvement_needed"]
                )
        
        # 4. Create a plan
        plan = await prometheus.create_plan(
            name=f"Plan for {project_id}",
            description="Generated from Telos requirements",
            requirements_data={
                "project_id": project_id,
                "requirements": requirements
            },
            start_date=(datetime.now() + timedelta(days=1)).isoformat(),
            end_date=(datetime.now() + timedelta(days=30)).isoformat()
        )
        
        # 5. Link plan back to requirements
        for req_id in requirement_ids:
            await update_requirement(
                project_id, req_id,
                metadata={
                    "plan_id": plan["plan_id"],
                    "plan_created_at": datetime.now().isoformat()
                }
            )
        
        # 6. Set up task status callbacks
        await prometheus.register_task_callbacks(
            plan["plan_id"],
            callback_url=f"http://localhost:8008/api/callbacks/task-updates"
        )
        
        return {
            "plan_id": plan["plan_id"],
            "plan_name": plan["name"],
            "task_count": len(plan["tasks"]),
            "planning_readiness": analysis["planning_readiness"],
            "start_date": plan["start_date"],
            "end_date": plan["end_date"]
        }
    except Exception as e:
        logger.error(f"Prometheus integration error: {e}")
        raise IntegrationError(f"Failed to integrate with Prometheus: {str(e)}")
```

### Complete Rhetor Integration Example

```python
from telos.rhetor_adapter import RhetorAdapter

async def integrate_telos_with_rhetor(project_id, requirement_id):
    """Complete example of Rhetor integration."""
    rhetor = RhetorAdapter()
    
    try:
        # 1. Get the requirement with context
        requirement = await get_requirement_with_context(project_id, requirement_id)
        
        # 2. Validate the requirement
        validation = await rhetor.validate_requirement(
            requirement,
            validation_types=["completeness", "clarity", "testability", "consistency"]
        )
        
        # 3. Generate improvement suggestions if needed
        suggestions = []
        if not validation["passed"]:
            suggestions = await rhetor.generate_improvement_suggestions(
                requirement,
                validation_issues=validation["issues"]
            )
        
        # 4. Apply suggestions if auto-improve is enabled
        if auto_improve and suggestions:
            refined_requirement = await rhetor.refine_requirement(
                requirement,
                suggestions=suggestions
            )
            
            # 5. Update the requirement
            updated = await update_requirement(
                project_id,
                requirement_id,
                description=refined_requirement["description"],
                metadata={
                    **requirement["metadata"],
                    "last_refined": datetime.now().isoformat(),
                    "refinement_source": "rhetor_auto",
                    "original_description": requirement["description"]
                }
            )
            
            # 6. Store the refinement history
            await store_refinement_history(
                project_id,
                requirement_id,
                original=requirement,
                refined=refined_requirement,
                suggestions=suggestions,
                validation=validation
            )
            
            return {
                "requirement_id": requirement_id,
                "validation": validation,
                "suggestions": suggestions,
                "refinement_applied": True,
                "updated": updated
            }
        
        # Just return validation and suggestions if no auto-improve
        return {
            "requirement_id": requirement_id,
            "validation": validation,
            "suggestions": suggestions,
            "refinement_applied": False
        }
    except Exception as e:
        logger.error(f"Rhetor integration error: {e}")
        raise IntegrationError(f"Failed to integrate with Rhetor: {str(e)}")
```

## Environment Variables

Telos integration can be configured using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `TELOS_PORT` | HTTP server port | 8008 |
| `TELOS_HOST` | HTTP server host | 0.0.0.0 |
| `TELOS_STORAGE_DIR` | Directory for file storage | ./data/telos |
| `TELOS_LOG_LEVEL` | Logging level | INFO |
| `HERMES_URL` | URL for Hermes service | http://localhost:8000/api |
| `PROMETHEUS_URL` | URL for Prometheus service | http://localhost:8006/api |
| `RHETOR_URL` | URL for Rhetor service | http://localhost:8003/api |
| `ENGRAM_URL` | URL for Engram service | http://localhost:8001/api |
| `TELOS_WEBHOOK_SECRET` | Secret for signing webhooks | random generated |
| `TELOS_INTEGRATION_TIMEOUT` | Timeout for integration calls | 30s |
| `TELOS_AUTH_ENABLED` | Enable authentication | false |
| `TELOS_JWT_SECRET` | Secret for JWT tokens | null |
| `TELOS_CORS_ORIGINS` | Allowed CORS origins | * |

## Troubleshooting

### Common Integration Issues

1. **Connection Issues**:
   - Check that the target component is running
   - Verify that the URL is correct
   - Check network connectivity between components

2. **Authentication Issues**:
   - Ensure authentication tokens are valid
   - Check that the correct tokens are being sent
   - Verify permissions for the authenticated user

3. **Data Format Issues**:
   - Ensure data sent matches the expected format
   - Check for missing required fields
   - Verify that IDs are in the correct format

4. **Performance Issues**:
   - Consider batch operations for multiple items
   - Use pagination for large result sets
   - Implement caching for frequently accessed data

### Logging and Debugging

Enable detailed logging for troubleshooting:

```bash
# Enable debug logging
export TELOS_LOG_LEVEL=DEBUG

# Run with detailed logging
telos-api --debug
```

Programmatic logging control:

```python
import logging

# Configure logger
logger = logging.getLogger("telos.integration")
logger.setLevel(logging.DEBUG)

# Add file handler
handler = logging.FileHandler("telos_integration.log")
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
logger.addHandler(handler)

# Log integration events
logger.debug(f"Integration request: {request_data}")
logger.info(f"Integration successful: {result}")
logger.error(f"Integration error: {error}", exc_info=True)
```

## Conclusion

Telos is designed to integrate seamlessly with the Tekton ecosystem and external systems. By following the patterns and examples in this guide, you can effectively incorporate requirements management and tracing into your development workflow, ensuring requirements are properly tracked, validated, and linked to planning and execution processes.