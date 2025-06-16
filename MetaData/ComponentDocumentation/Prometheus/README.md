# Prometheus

## Overview

Prometheus is the planning and preparation component of the Tekton ecosystem. It analyzes requirements, designs execution plans, and coordinates with other components to ensure successful project outcomes. As the forward-looking planning engine, Prometheus transforms requirements and constraints into actionable execution plans with critical path analysis and resource optimization.

## Key Features

- **Plan Creation and Management**: Create, update, and analyze project plans with timelines and objectives
- **Task Management**: Define tasks with dependencies, constraints, and resource allocations
- **Critical Path Analysis**: Calculate critical paths and identify bottlenecks in project execution
- **Resource Allocation**: Define, manage, and optimize resource assignments and utilization
- **LLM-Powered Plan Analysis**: Leverage AI for risk identification and optimization opportunities
- **Retrospective Analysis (Epimethius)**: Learn from completed projects through variance analysis and performance metrics
- **Timeline Generation**: Visualize project timelines and dependencies through multiple formats
- **Improvement Suggestions**: Generate data-driven recommendations for planning improvement
- **WebSocket Real-time Updates**: Get live updates on plan changes and progress
- **Single Port Architecture**: Unified access through HTTP, WebSocket, and events via path-based routing

## Architecture

Prometheus follows the Single Port Architecture pattern of the Tekton ecosystem:

```
Prometheus/
├── api/                  # API layer
│   ├── app.py            # Main FastAPI application
│   └── endpoints/        # API endpoint modules
├── core/                 # Core engine
│   ├── planning_engine.py # Planning logic with latent reasoning
│   └── critical_path.py  # Critical path analysis
├── models/               # Domain models
│   ├── plan.py           # Plan data model
│   ├── task.py           # Task data model
│   └── resource.py       # Resource data model
└── utils/                # Utilities
    ├── engram_connector.py # Integration with Engram
    ├── rhetor_adapter.py # Integration with Rhetor
    └── telos_connector.py # Integration with Telos
```

### Key Components:

1. **Planning Engine**: Core component for plan generation and refinement using latent reasoning
2. **Critical Path Analyzer**: Implements critical path method for project scheduling
3. **Retrospective Module (Epimethius)**: Provides retrospective analysis of completed projects
4. **FastAPI Application**: RESTful API and WebSocket interface for accessing Prometheus functionality

## Integration Points

Prometheus integrates with several other Tekton components:

1. **Telos**: Retrieves requirements and project constraints from Telos to inform planning
2. **Rhetor**: Uses Rhetor for LLM-powered plan analysis and improvement suggestions
3. **Engram**: Stores and retrieves planning knowledge and historical project data
4. **Synthesis**: Hands off plans for execution with real-time progress feedback
5. **Hermes**: Registers capabilities with the service registry for discovery by other components

## Quick Start

```bash
# Register with Hermes
python -m Prometheus/register_with_hermes.py

# Start with Tekton
./scripts/tekton-launch --components prometheus

# Use client
python -m Prometheus/examples/client_usage.py
```

## Client Usage

```python
from prometheus.client import PrometheusClient

async def main():
    # Connect to Prometheus
    client = PrometheusClient(base_url="http://localhost:8006/api")
    
    # Create a plan
    plan_id = await client.create_plan(
        name="Example Project",
        description="An example project plan",
        start_date="2025-05-01T00:00:00Z",
        end_date="2025-06-30T00:00:00Z"
    )
    
    # Add resources
    resource_id = await client.add_resource(
        plan_id=plan_id,
        name="Developer",
        type="human",
        skills=["python", "javascript"],
        availability=1.0
    )
    
    # Add tasks
    task_id = await client.add_task(
        plan_id=plan_id,
        name="Initial Planning",
        description="Define project requirements",
        duration=3,
        duration_unit="days",
        assigned_to=resource_id
    )
    
    # Calculate critical path
    critical_path = await client.calculate_critical_path(plan_id)
    
    # Generate retrospective
    retrospective_id = await client.create_retrospective(
        plan_id=plan_id,
        name="Project Retrospective",
        description="Analysis of project execution",
        date="2025-07-01T00:00:00Z"
    )
    
    # Get improvement suggestions
    suggestions = await client.generate_improvement_suggestions(retrospective_id)
    
    # Close the client
    await client.close()
```

## API Endpoints

### Base URL

```
http://localhost:8006/api
```

### Plan Endpoints

- `POST /plans` - Create a new plan
- `GET /plans` - List plans
- `GET /plans/{plan_id}` - Get plan details
- `PUT /plans/{plan_id}` - Update plan
- `DELETE /plans/{plan_id}` - Delete plan

### Task Endpoints

- `POST /plans/{plan_id}/tasks` - Add task to plan
- `GET /plans/{plan_id}/tasks` - List tasks in plan
- `GET /plans/{plan_id}/tasks/{task_id}` - Get task details
- `PUT /plans/{plan_id}/tasks/{task_id}` - Update task
- `DELETE /plans/{plan_id}/tasks/{task_id}` - Delete task
- `PUT /plans/{plan_id}/tasks/{task_id}/progress` - Update task progress

### Resource Endpoints

- `POST /plans/{plan_id}/resources` - Add resource to plan
- `GET /plans/{plan_id}/resources` - List resources in plan
- `GET /plans/{plan_id}/resources/{resource_id}` - Get resource details
- `PUT /plans/{plan_id}/resources/{resource_id}` - Update resource
- `DELETE /plans/{plan_id}/resources/{resource_id}` - Delete resource

### Analysis Endpoints

- `GET /plans/{plan_id}/critical-path` - Calculate critical path
- `GET /plans/{plan_id}/timeline` - Generate timeline
- `GET /plans/{plan_id}/summary` - Get plan summary
- `GET /plans/{plan_id}/analysis` - Generate LLM plan analysis

### Retrospective Endpoints

- `POST /retrospectives` - Create a retrospective
- `GET /retrospectives` - List retrospectives
- `GET /retrospectives/{retrospective_id}` - Get retrospective details
- `GET /retrospectives/{retrospective_id}/improvement-suggestions` - Generate improvement suggestions
- `GET /retrospectives/{retrospective_id}/summary` - Generate retrospective summary

## Documentation

For detailed documentation, see:

- [Technical Documentation](./TECHNICAL_DOCUMENTATION.md) - Detailed technical specifications
- [API Reference](./API_REFERENCE.md) - Complete API documentation
- [Integration Guide](./INTEGRATION_GUIDE.md) - Information on integrating with Prometheus