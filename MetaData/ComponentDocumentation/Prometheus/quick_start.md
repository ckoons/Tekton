# Prometheus Quick Start Guide

This guide will help you quickly get started with Prometheus, the planning and retrospective analysis component of the Tekton ecosystem.

## Installation

Prometheus is installed as part of the Tekton ecosystem. If you haven't already set up Tekton, follow these steps:

1. Clone the Tekton repository:
   ```bash
   git clone https://github.com/yourusername/Tekton.git
   cd Tekton
   ```

2. Run the full setup script (optional):
   ```bash
   ./setup-all.sh
   ```

3. Alternatively, set up only Prometheus:
   ```bash
   cd Prometheus
   ./setup.sh
   ```

## Starting Prometheus

### Option 1: Using Tekton Launch

The simplest way to start Prometheus is using the Tekton launch script:

```bash
./scripts/tekton-launch --components prometheus
```

This will:
- Check for dependencies
- Start Prometheus on port 8006
- Register Prometheus with Hermes service registry

### Option 2: Starting Manually

Alternatively, you can start Prometheus manually:

1. Register with Hermes (optional but recommended):
   ```bash
   python -m Prometheus/register_with_hermes.py
   ```

2. Start the API server:
   ```bash
   cd Prometheus
   python -m prometheus.api.app
   ```

## Verifying the Setup

1. Check if the API is running:
   ```bash
   curl http://localhost:8006/health
   ```

   You should see a response like:
   ```json
   {
     "status": "healthy",
     "version": "0.1.0",
     "port": 8006
   }
   ```

2. Check Hermes registration:
   ```bash
   curl http://localhost:8000/api/components?id=prometheus.planning
   ```

## Basic Usage Examples

### Using the Client Library

```python
import asyncio
from prometheus.client import PrometheusClient

async def example():
    # Create client
    client = PrometheusClient(base_url="http://localhost:8006/api")
    
    try:
        # Check health
        health = await client.health_check()
        print(f"Service health: {health['status']}")
        
        # Create a plan
        plan_id = await client.create_plan(
            name="Example Project",
            description="A demonstration project",
            start_date="2025-05-01T00:00:00Z",
            end_date="2025-06-30T00:00:00Z"
        )
        print(f"Created plan: {plan_id}")
        
        # Add a resource
        resource_id = await client.add_resource(
            plan_id=plan_id,
            name="Developer",
            type="human",
            skills=["python", "javascript"],
            availability=1.0
        )
        print(f"Added resource: {resource_id}")
        
        # Add a task
        task_id = await client.add_task(
            plan_id=plan_id,
            name="Design System Architecture",
            description="Create the high-level system design",
            duration=5,
            duration_unit="days",
            assigned_to=resource_id
        )
        print(f"Added task: {task_id}")
        
        # Generate timeline
        timeline = await client.generate_timeline(plan_id)
        print(f"Timeline: {timeline['start_date']} to {timeline['end_date']}")
        
    finally:
        # Close the client
        await client.close()

if __name__ == "__main__":
    asyncio.run(example())
```

### Using the REST API Directly

#### Create a Plan

```bash
curl -X POST http://localhost:8006/api/plans \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Example Project",
    "description": "A demonstration project",
    "start_date": "2025-05-01T00:00:00Z",
    "end_date": "2025-06-30T00:00:00Z"
  }'
```

#### Add a Resource

```bash
curl -X POST http://localhost:8006/api/plans/PLAN_ID/resources \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Developer",
    "type": "human",
    "skills": ["python", "javascript"],
    "availability": 1.0
  }'
```

#### Add a Task

```bash
curl -X POST http://localhost:8006/api/plans/PLAN_ID/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Design System Architecture",
    "description": "Create the high-level system design",
    "duration": 5,
    "duration_unit": "days",
    "assigned_to": "RESOURCE_ID",
    "dependencies": []
  }'
```

#### Calculate Critical Path

```bash
curl http://localhost:8006/api/plans/PLAN_ID/critical-path
```

## Working with Retrospectives

After a plan has been executed, you can create a retrospective to analyze its performance:

```python
import asyncio
from prometheus.client import PrometheusClient

async def retrospective_example(plan_id):
    client = PrometheusClient(base_url="http://localhost:8006/api")
    
    try:
        # Create a retrospective
        retrospective_id = await client.create_retrospective(
            plan_id=plan_id,
            name="Project Retrospective",
            description="Analysis of project execution",
            date="2025-07-01T00:00:00Z"
        )
        print(f"Created retrospective: {retrospective_id}")
        
        # Add feedback
        await client.add_retrospective_feedback(
            retrospective_id=retrospective_id,
            type="positive",
            description="Team collaboration was excellent",
            source="Project Manager"
        )
        
        await client.add_retrospective_feedback(
            retrospective_id=retrospective_id,
            type="negative",
            description="Timeline was too aggressive",
            source="Developer"
        )
        
        # Generate improvement suggestions
        suggestions = await client.generate_improvement_suggestions(retrospective_id)
        print("Improvement suggestions:")
        for suggestion in suggestions:
            print(f"- {suggestion['description']}")
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(retrospective_example("your-plan-id"))
```

## Integration with Other Tekton Components

### Telos Integration

Prometheus can import requirements from Telos:

```python
import asyncio
from prometheus.client import PrometheusClient
from telos.client import TelosClient

async def telos_integration():
    prometheus = PrometheusClient()
    telos = TelosClient()
    
    try:
        # Get requirements from Telos
        project = await telos.get_project("project-id")
        requirements = await telos.get_requirements(project.id)
        
        # Create a plan based on requirements
        plan_id = await prometheus.create_plan(
            name=f"Plan for {project.name}",
            description=f"Based on Telos requirements",
            start_date="2025-05-01T00:00:00Z",
            end_date="2025-06-30T00:00:00Z"
        )
        
        # Convert requirements to tasks
        for req in requirements:
            await prometheus.add_task(
                plan_id=plan_id,
                name=f"Implement {req.name}",
                description=req.description,
                duration=5,  # Estimate
                duration_unit="days"
            )
            
    finally:
        await prometheus.close()
        await telos.close()
```

## UI Integration

Prometheus includes a web component for use with Hephaestus:

1. Include the component in your HTML:
   ```html
   <script src="scripts/prometheus-ui.js"></script>
   <link rel="stylesheet" href="styles/prometheus.css">
   
   <prometheus-planner project-id="your-project-id"></prometheus-planner>
   ```

2. The component provides a full planning interface with:
   - Timeline visualization
   - Task management
   - Resource allocation
   - Critical path highlighting
   - Performance metrics

## Troubleshooting

### Common Issues

1. **API Not Responding**:
   - Ensure Prometheus is running: `ps aux | grep prometheus`
   - Check port availability: `netstat -an | grep 8006`
   - Verify no port conflicts with other components

2. **Hermes Registration Failing**:
   - Ensure Hermes is running: `curl http://localhost:8000/health`
   - Check Hermes logs: `cat Hermes/logs/hermes.log`
   - Try manual registration: `python -m Prometheus/register_with_hermes.py --hermes-url http://localhost:8000/api`

3. **Client Connection Issues**:
   - Verify base URL: `http://localhost:8006/api` (note the `/api` suffix)
   - Check for CORS issues if connecting from browser
   - Ensure port forwarding is set up correctly if using containers

### Getting Help

If you encounter issues:

1. Check the logs in `Prometheus/logs/`
2. Review the [technical documentation](./TECHNICAL_DOCUMENTATION.md)
3. File an issue on the Tekton repository

## Next Steps

- Set up the [UI integration](./ui_integration.md) with Hephaestus
- Learn about [advanced planning features](./advanced_planning.md)
- Explore [retrospective analysis](./retrospective_analysis.md) capabilities