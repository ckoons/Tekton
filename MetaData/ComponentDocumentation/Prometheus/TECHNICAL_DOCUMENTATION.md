# Prometheus Technical Documentation

## Overview

Prometheus is the planning and preparation component of the Tekton ecosystem. It analyzes requirements, designs execution plans, and coordinates with other components to ensure successful project outcomes. The system consists of two main components:

1. **Prometheus**: Forward-looking planning and execution tracking
2. **Epimethius**: Retrospective analysis and improvement suggestions

## Architecture

Prometheus follows the Single Port Architecture pattern of the Tekton ecosystem, with different functionalities accessible through path-based routing on a single HTTP port.

### System Components

```
Prometheus/
├── api/                  # API layer
│   ├── app.py            # Main FastAPI application
│   ├── endpoints/        # API endpoint modules
│   └── models/           # API data models
├── core/                 # Core engine
│   ├── planning_engine.py # Planning logic with latent reasoning
│   └── critical_path.py  # Critical path analysis
├── models/               # Domain models
│   ├── plan.py           # Plan data model
│   ├── task.py           # Task data model
│   ├── resource.py       # Resource data model
│   ├── timeline.py       # Timeline data model
│   ├── retrospective.py  # Retrospective data model
│   └── improvement.py    # Improvement data model
└── utils/                # Utilities
    ├── engram_connector.py # Integration with Engram
    ├── rhetor_adapter.py # Integration with Rhetor
    ├── telos_connector.py # Integration with Telos
    └── hermes_helper.py  # Hermes integration utilities
```

### Key Classes

1. **PlanningEngine** - Core class for plan generation and refinement using latent reasoning
2. **CriticalPathAnalyzer** - Implements critical path method for project scheduling
3. **PrometheusClient** - Client for interacting with the Prometheus/Epimethius API
4. **FastAPI Application** - RESTful API for accessing Prometheus functionality

## Core Functionality

### Planning Capabilities

1. **Plan Creation and Management**
   - Create, update, and delete project plans
   - Define plan timelines, objectives, and metadata

2. **Task Management**
   - Add, update, and remove tasks
   - Define task dependencies and constraints
   - Track task progress and status

3. **Resource Allocation**
   - Define and manage project resources (human, equipment, etc.)
   - Assign resources to tasks
   - Track resource utilization and availability

4. **Critical Path Analysis**
   - Calculate the critical path of a project plan
   - Identify bottlenecks and risks
   - Calculate earliest/latest start/finish times
   - Determine slack time for each task

5. **Timeline Generation**
   - Generate project timelines based on tasks and dependencies
   - Visualize the timeline in different formats

6. **LLM-Powered Plan Analysis**
   - Analyze plans for risks and optimization opportunities
   - Generate recommendations for plan improvement

### Retrospective Capabilities (Epimethius)

1. **Retrospective Creation**
   - Create and manage retrospectives for completed plans
   - Capture feedback, observations, and outcomes

2. **Variance Analysis**
   - Compare planned vs. actual task durations
   - Identify patterns in schedule variances

3. **Performance Metrics**
   - Calculate key performance indicators
   - Track on-time completion rates and delays

4. **Improvement Suggestions**
   - Generate actionable improvement suggestions
   - Provide rationale and expected impact

5. **Retrospective Summary**
   - Generate comprehensive summaries of project outcomes
   - Identify lessons learned and action items

## Integration Points

Prometheus integrates with several other Tekton components:

1. **Telos**: Retrieves requirements and project constraints from Telos to inform planning
2. **Rhetor**: Uses Rhetor for LLM-powered plan analysis and improvement suggestions
3. **Engram**: Stores and retrieves planning knowledge and historical project data
4. **Hermes**: Registers capabilities with the service registry for discovery by other components
5. **Synthesis**: Hands off plans for execution with real-time progress feedback

## API Reference

Prometheus exposes a RESTful API following the Single Port Architecture pattern.

### Base URL

```
http://localhost:8006/api
```

### Health Check

```
GET /health
```

Returns the health status of the Prometheus service.

### Planning Endpoints

```
POST /plans                        # Create a new plan
GET /plans                         # List plans
GET /plans/{plan_id}               # Get plan details
PUT /plans/{plan_id}               # Update plan
DELETE /plans/{plan_id}            # Delete plan

POST /plans/{plan_id}/tasks        # Add task to plan
GET /plans/{plan_id}/tasks         # List tasks in plan
GET /plans/{plan_id}/tasks/{task_id} # Get task details
PUT /plans/{plan_id}/tasks/{task_id} # Update task
DELETE /plans/{plan_id}/tasks/{task_id} # Delete task
PUT /plans/{plan_id}/tasks/{task_id}/progress # Update task progress

POST /plans/{plan_id}/resources    # Add resource to plan
GET /plans/{plan_id}/resources     # List resources in plan
GET /plans/{plan_id}/resources/{resource_id} # Get resource details
PUT /plans/{plan_id}/resources/{resource_id} # Update resource
DELETE /plans/{plan_id}/resources/{resource_id} # Delete resource

GET /plans/{plan_id}/critical-path # Calculate critical path
GET /plans/{plan_id}/timeline      # Generate timeline
GET /plans/{plan_id}/summary       # Get plan summary
GET /plans/{plan_id}/analysis      # Generate LLM plan analysis
```

### Retrospective Endpoints

```
POST /retrospectives               # Create a retrospective
GET /retrospectives                # List retrospectives
GET /retrospectives/{retrospective_id} # Get retrospective details

POST /retrospectives/{retrospective_id}/feedback # Add feedback
GET /retrospectives/{retrospective_id}/feedback  # List feedback
GET /retrospectives/{retrospective_id}/feedback/{feedback_id} # Get feedback details

GET /plans/{plan_id}/variance-analysis     # Generate variance analysis
GET /plans/{plan_id}/performance-metrics   # Generate performance metrics
GET /retrospectives/{retrospective_id}/improvement-suggestions # Generate improvement suggestions
GET /retrospectives/{retrospective_id}/summary # Generate retrospective summary
```

## Client Usage

Prometheus provides a client library for easy integration:

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

## Latent Reasoning

Prometheus uses Tekton's Latent Reasoning framework to enable sophisticated planning capabilities:

1. **Complexity Assessment**: Analyzes plan requirements to determine complexity
2. **Iterative Refinement**: Multi-step reasoning for complex plans
3. **Thought Sharing**: Persists planning insights across components
4. **Contextual Reasoning**: Incorporates project context into planning decisions

The `complexity_based_reasoning` approach tailors the planning process to the complexity of the objective:
- Simple objectives get processed directly
- Complex objectives undergo multiple iterations of refinement
- The system records its reasoning process for later reference

## Critical Path Analysis

The `CriticalPathAnalyzer` implements the Critical Path Method (CPM) for project scheduling:

1. Builds a directed graph of tasks and dependencies
2. Calculates earliest and latest start/finish times for each task
3. Identifies tasks with zero slack (the critical path)
4. Calculates the minimum project duration
5. Identifies potential bottlenecks

The analyzer also provides visualization capabilities to render the critical path as a network diagram.

## Performance Considerations

1. **Asynchronous Processing**: All API endpoints are async for scalability
2. **Client Resilience**: The client implements automatic retries for transient failures
3. **Resource Management**: Clean shutdown procedures prevent resource leaks
4. **Caching**: Future implementations will cache frequently accessed data

## Future Enhancements

1. **Resource Leveling**: Optimize resource allocation to prevent overallocation
2. **Risk Analysis**: Advanced risk modeling and mitigation planning
3. **Scenario Planning**: Compare multiple plan scenarios side-by-side
4. **ML-Powered Estimation**: Use historical data to improve duration estimates
5. **Real-time Collaboration**: WebSocket-based collaborative planning

## Security Considerations

1. **Authentication**: Future versions will integrate with Tekton's authentication system
2. **Authorization**: Role-based access control for plans and operations
3. **Data Validation**: Strict validation of all API inputs
4. **Audit Logging**: Record all plan modifications for compliance

## Integration Guide

### Registering with Hermes

Prometheus automatically registers with Hermes during startup:

```bash
python -m Prometheus/register_with_hermes.py
```

### Environment Variables

- `PROMETHEUS_PORT`: Port for the Prometheus API (default: 8006)
- `HERMES_URL`: URL of the Hermes API (default: http://localhost:8000/api)
- `STARTUP_INSTRUCTIONS_FILE`: Path to JSON file with startup instructions

### Adding to Tekton Launch

Prometheus is included in the Tekton launch script:

```bash
./scripts/tekton-launch --components prometheus
```

## UI Integration

Prometheus includes a web UI component for integration with Hephaestus:

```
Prometheus/ui/
├── prometheus-component.html  # Web component template
├── scripts/                   # JavaScript for the component
│   └── prometheus-ui.js       # UI logic
└── styles/                    # CSS styles
    └── prometheus.css         # Component styling
```