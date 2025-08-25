# Prometheus User Guide

## Introduction

Prometheus is the project planning and management system for the Tekton ecosystem. It provides tools for task planning, resource allocation, timeline management, and project optimization. This guide will help you get started with Prometheus and leverage its capabilities for managing complex software projects.

## Getting Started

### Installation

1. Ensure you have Python 3.9+ installed
2. Clone the Prometheus repository:
   ```bash
   git clone git@github.com:yourusername/Tekton.git
   cd Tekton/Prometheus
   ```

3. Install dependencies:
   ```bash
   pip install -e .
   ```
   or use the setup script:
   ```bash
   ./setup.sh
   ```

4. Start the Prometheus server:
   ```bash
   python -m prometheus.api.app
   ```

By default, Prometheus runs on port 8006. The port is configured through Tekton's GlobalConfig system.

### Basic Configuration

Create a configuration file named `prometheus_config.json`:

```json
{
  "server": {
    "host": "localhost",
    "port": 8003
  },
  "database": {
    "type": "sqlite",
    "path": "prometheus.db"
  },
  "integrations": {
    "hermes": {
      "url": "http://localhost:8002"
    },
    "telos": {
      "url": "http://localhost:8006"
    },
    "engram": {
      "url": "http://localhost:8001"
    }
  }
}
```

## Web UI Interface

Prometheus includes a modern web interface with six main tabs:

### Navigation

The UI uses CSS-first navigation with radio buttons for optimal performance:

1. **Planning** - Create and manage project plans
2. **Timeline** - Visualize project timelines and milestones
3. **Resources** - Manage team resources and allocations
4. **Analysis** - View critical path analysis and metrics
5. **Planning Chat** - AI-assisted planning conversations
6. **Team Chat** - Collaborative team discussions

### Key Features

- **Real-time Updates**: All data is fetched from the backend API in real-time
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **CI Integration**: Chat tabs integrate with Tekton's CI system via aish MCP
- **Semantic Navigation**: UI elements include semantic tags for accessibility

### Using the Chat Features

The Planning Chat and Team Chat tabs provide AI-powered assistance:

```javascript
// Planning Chat - For project-specific CI assistance
window.AIChat.sendMessage('prometheus', 'Help me plan a sprint')

// Team Chat - For collaborative discussions
window.AIChat.teamChat('Team update on project status', 'prometheus')
```

Note: CI Chat features require the main Tekton UI environment to be running.

## Using the Client Library

Prometheus provides a Python client for easy integration:

```python
from prometheus.client import PrometheusClient

# Initialize client
client = PrometheusClient("http://localhost:8003")

# Create a new project
project = client.create_project(
    name="Tekton UI Redesign",
    description="Redesigning the UI components for better user experience",
    start_date="2025-05-15",
    target_end_date="2025-07-15"
)

project_id = project["id"]
print(f"Created project: {project_id}")
```

## Project Management

### Creating and Managing Projects

```python
# Create a more detailed project
project = client.create_project(
    name="CI Feature Integration",
    description="Integrating new CI features into the product",
    start_date="2025-05-01",
    target_end_date="2025-08-15",
    metadata={
        "priority": "high",
        "sponsor": "Product Team",
        "budget": 150000,
        "success_criteria": [
            "All features pass quality testing",
            "User satisfaction scores above 4.5/5",
            "Performance impact less than 10%"
        ]
    }
)

# Update project details
client.update_project(
    project_id=project["id"],
    name="Enhanced CI Feature Integration",
    target_end_date="2025-08-30"  # Extending deadline
)

# List all projects
projects = client.list_projects()
for proj in projects:
    print(f"{proj['name']} - Target completion: {proj['target_end_date']}")

# Get detailed project info
project_details = client.get_project(project["id"])
print(f"Project status: {project_details['status']}")
print(f"Progress: {project_details['progress']}%")
```

### Managing Tasks

```python
# Create a task
task = client.create_task(
    project_id=project["id"],
    name="Research Existing CI Solutions",
    description="Evaluate available CI solutions for integration",
    estimated_hours=20,
    priority="high",
    status="not_started",
    assignee="team_member_1"
)

# Create a subtask
subtask = client.create_task(
    project_id=project["id"],
    name="Document API Requirements",
    description="Document API requirements for CI integration",
    estimated_hours=8,
    priority="medium",
    status="not_started",
    assignee="team_member_2",
    parent_task_id=task["id"]  # This makes it a subtask
)

# Update task status
client.update_task(
    task_id=task["id"],
    status="in_progress",
    progress=25
)

# Add a comment to a task
client.add_task_comment(
    task_id=task["id"],
    comment="Found three promising solutions to evaluate further."
)

# List all tasks for a project
tasks = client.list_tasks(project_id=project["id"])
for task in tasks:
    print(f"{task['name']} - Status: {task['status']}")

# Get detailed task info
task_details = client.get_task(task["id"])
print(f"Task: {task_details['name']}")
print(f"Assignee: {task_details['assignee']}")
print(f"Progress: {task_details['progress']}%")
```

## Timeline Management

### Creating and Managing Timelines

```python
# Create a project timeline
timeline = client.create_timeline(
    project_id=project["id"],
    name="CI Integration Timeline",
    description="Detailed timeline for CI feature integration"
)

# Add phases to the timeline
research_phase = client.add_timeline_phase(
    timeline_id=timeline["id"],
    name="Research",
    start_date="2025-05-01",
    end_date="2025-05-15",
    color="#4287f5"
)

planning_phase = client.add_timeline_phase(
    timeline_id=timeline["id"],
    name="Planning",
    start_date="2025-05-16",
    end_date="2025-05-31",
    color="#42f59e"
)

implementation_phase = client.add_timeline_phase(
    timeline_id=timeline["id"],
    name="Implementation",
    start_date="2025-06-01",
    end_date="2025-07-31",
    color="#f54242"
)

testing_phase = client.add_timeline_phase(
    timeline_id=timeline["id"],
    name="Testing",
    start_date="2025-08-01",
    end_date="2025-08-15",
    color="#f5d442"
)

# Add milestones
client.add_timeline_milestone(
    timeline_id=timeline["id"],
    name="Research Complete",
    date="2025-05-15",
    description="All research completed and documented"
)

client.add_timeline_milestone(
    timeline_id=timeline["id"],
    name="Implementation Complete",
    date="2025-07-31",
    description="All features implemented and ready for testing"
)

client.add_timeline_milestone(
    timeline_id=timeline["id"],
    name="Project Complete",
    date="2025-08-15",
    description="All features tested and deployed"
)

# Get timeline details
timeline_details = client.get_timeline(timeline["id"])
print(f"Timeline: {timeline_details['name']}")
print(f"Phases: {len(timeline_details['phases'])}")
print(f"Milestones: {len(timeline_details['milestones'])}")
```

### Timeline Visualization

```python
# Generate a Gantt chart for the timeline
chart_url = client.generate_timeline_chart(
    timeline_id=timeline["id"],
    chart_type="gantt",
    format="png"
)

print(f"Timeline chart available at: {chart_url}")

# Generate a milestone chart
milestone_chart_url = client.generate_milestone_chart(
    timeline_id=timeline["id"],
    format="svg"
)

print(f"Milestone chart available at: {milestone_chart_url}")
```

## Resource Management

### Managing Team Resources

```python
# Add team members
team_member_1 = client.add_team_member(
    project_id=project["id"],
    name="Alice Johnson",
    role="CI Engineer",
    email="alice@example.com",
    availability_hours_per_week=30
)

team_member_2 = client.add_team_member(
    project_id=project["id"],
    name="Bob Smith",
    role="UI Developer",
    email="bob@example.com",
    availability_hours_per_week=40
)

team_member_3 = client.add_team_member(
    project_id=project["id"],
    name="Charlie Chen",
    role="Project Manager",
    email="charlie@example.com",
    availability_hours_per_week=20
)

# Set team member availability exceptions
client.set_team_member_availability(
    team_member_id=team_member_1["id"],
    date="2025-05-20",
    available_hours=0,  # Unavailable this day
    reason="Holiday"
)

# Get resource allocation
allocation = client.get_resource_allocation(project_id=project["id"])
print("Resource Allocation:")
for member in allocation["team_members"]:
    print(f"{member['name']}: {member['allocated_hours']} / {member['available_hours']} hours")
    
# Check team member workload
workload = client.get_team_member_workload(team_member_id=team_member_1["id"])
print(f"Workload for {workload['name']}:")
for week in workload["weeks"]:
    print(f"Week of {week['date']}: {week['allocated_hours']} / {week['available_hours']} hours")
```

### Resource Optimization

```python
# Get resource optimization recommendations
recommendations = client.optimize_resources(
    project_id=project["id"],
    optimization_target="balanced"  # Options: time, cost, balanced
)

print("Resource Optimization Recommendations:")
for recommendation in recommendations["recommendations"]:
    print(f"- {recommendation['description']}")
    print(f"  Impact: {recommendation['impact']}")
    print(f"  Effort: {recommendation['effort']}")
```

## Critical Path Analysis

### Analyzing Project Critical Path

```python
# Define task dependencies
client.add_task_dependency(
    task_id=task["id"],  # "Research Existing CI Solutions"
    depends_on_task_id=subtask["id"]  # "Document API Requirements"
)

# Create more tasks with dependencies
implementation_task = client.create_task(
    project_id=project["id"],
    name="Implement CI Integration",
    description="Integrate CI solution with existing system",
    estimated_hours=60,
    priority="high",
    status="not_started"
)

client.add_task_dependency(
    task_id=implementation_task["id"],
    depends_on_task_id=task["id"]  # Depends on research task
)

testing_task = client.create_task(
    project_id=project["id"],
    name="Test CI Integration",
    description="Comprehensive testing of CI integration",
    estimated_hours=40,
    priority="high",
    status="not_started"
)

client.add_task_dependency(
    task_id=testing_task["id"],
    depends_on_task_id=implementation_task["id"]
)

# Calculate critical path
critical_path = client.calculate_critical_path(project_id=project["id"])

print("Critical Path:")
for i, task in enumerate(critical_path["tasks"], 1):
    print(f"{i}. {task['name']} ({task['estimated_hours']} hours)")
    
print(f"Total critical path duration: {critical_path['total_hours']} hours")
print(f"Earliest completion date: {critical_path['completion_date']}")
```

### Optimizing the Critical Path

```python
# Get critical path optimization suggestions
optimizations = client.optimize_critical_path(
    project_id=project["id"],
    target_reduction_percent=15  # Try to reduce time by 15%
)

print("Critical Path Optimization Suggestions:")
for opt in optimizations["suggestions"]:
    print(f"- {opt['description']}")
    print(f"  Time savings: {opt['time_saved']} hours")
    print(f"  Risk level: {opt['risk_level']}")
```

## Risk Management

### Managing Project Risks

```python
# Add a risk to the project
risk = client.add_project_risk(
    project_id=project["id"],
    name="API Integration Complexity",
    description="The third-party CI API may be more complex than anticipated",
    probability="medium",  # low, medium, high
    impact="high",         # low, medium, high
    mitigation_strategy="Allocate additional time for integration. Plan for early prototype testing."
)

# Update risk status
client.update_risk(
    risk_id=risk["id"],
    status="mitigated",
    notes="Created detailed API integration plan with buffer time"
)

# List all project risks
risks = client.list_project_risks(project_id=project["id"])
print("Project Risks:")
for risk in risks:
    print(f"{risk['name']} - Probability: {risk['probability']}, Impact: {risk['impact']}")
    print(f"Status: {risk['status']}")
    print(f"Mitigation: {risk['mitigation_strategy']}")
```

### Risk Matrix Visualization

```python
# Generate risk matrix visualization
risk_matrix_url = client.generate_risk_matrix(
    project_id=project["id"],
    format="png"
)

print(f"Risk matrix available at: {risk_matrix_url}")
```

## Project Metrics and Reporting

### Tracking Metrics

```python
# Record project metrics
client.record_project_metric(
    project_id=project["id"],
    metric_name="tasks_completed",
    value=5,
    timestamp="2025-05-15T14:30:00Z"
)

client.record_project_metric(
    project_id=project["id"],
    metric_name="hours_spent",
    value=120,
    timestamp="2025-05-15T14:30:00Z"
)

# Get project metrics
metrics = client.get_project_metrics(
    project_id=project["id"],
    start_date="2025-05-01",
    end_date="2025-05-15"
)

print("Project Metrics:")
for metric_name, values in metrics.items():
    latest_value = values[-1]["value"] if values else "N/A"
    print(f"{metric_name}: {latest_value}")
```

### Generating Reports

```python
# Generate a project status report
report = client.generate_project_report(
    project_id=project["id"],
    report_type="status",
    format="pdf"
)

print(f"Status report available at: {report['url']}")

# Generate a detailed progress report
progress_report = client.generate_project_report(
    project_id=project["id"],
    report_type="progress",
    format="html",
    include_sections=["summary", "metrics", "tasks", "risks", "timeline"]
)

print(f"Progress report available at: {progress_report['url']}")
```

## Project Improvements

### Retrospectives and Lessons Learned

```python
# Create a project retrospective
retrospective = client.create_retrospective(
    project_id=project["id"],
    name="Mid-project Retrospective",
    date="2025-06-15"
)

# Add retrospective items
client.add_retrospective_item(
    retrospective_id=retrospective["id"],
    type="went_well",
    description="Team collaboration on research phase was excellent"
)

client.add_retrospective_item(
    retrospective_id=retrospective["id"],
    type="needs_improvement",
    description="Documentation is falling behind implementation"
)

client.add_retrospective_item(
    retrospective_id=retrospective["id"],
    type="action_item",
    description="Schedule weekly documentation reviews",
    assignee="team_member_3"  # Charlie Chen (PM)
)

# Get retrospective details
retro_details = client.get_retrospective(retrospective["id"])
print(f"Retrospective: {retro_details['name']}")
print("What went well:")
for item in [i for i in retro_details["items"] if i["type"] == "went_well"]:
    print(f"- {item['description']}")
    
print("Needs improvement:")
for item in [i for i in retro_details["items"] if i["type"] == "needs_improvement"]:
    print(f"- {item['description']}")
    
print("Action items:")
for item in [i for i in retro_details["items"] if i["type"] == "action_item"]:
    print(f"- {item['description']} (Assigned to: {item['assignee']})")
```

### Continuous Improvement

```python
# Get project improvement suggestions
improvements = client.get_improvement_suggestions(
    project_id=project["id"],
    categories=["process", "communication", "technical"]
)

print("Improvement Suggestions:")
for category, suggestions in improvements.items():
    print(f"\n{category.upper()}:")
    for suggestion in suggestions:
        print(f"- {suggestion['description']}")
        print(f"  Impact: {suggestion['impact']}")
        print(f"  Effort: {suggestion['effort']}")
```

## Integration with Tekton Components

### Telos Integration

Integrate with Telos for requirements management:

```python
from prometheus.utils.telos_connector import TelosConnector

# Initialize Telos connector
telos = TelosConnector("http://localhost:8006")

# Get requirements from Telos
requirements = telos.get_project_requirements("telos_project_id")

# Create tasks based on requirements
for req in requirements:
    client.create_task(
        project_id=project["id"],
        name=f"Implement: {req['name']}",
        description=f"Implementation of requirement: {req['description']}",
        estimated_hours=req.get("estimated_hours", 20),
        priority=req.get("priority", "medium"),
        metadata={
            "requirement_id": req["id"],
            "requirement_type": req["type"]
        }
    )

# Link task completion back to Telos
def on_task_completed(task_id):
    task = client.get_task(task_id)
    if "requirement_id" in task.get("metadata", {}):
        req_id = task["metadata"]["requirement_id"]
        telos.update_requirement_status(req_id, "implemented")
```

### Engram Integration

Use Engram for project memory:

```python
from prometheus.utils.engram_connector import EngramConnector

# Initialize Engram connector
engram = EngramConnector("http://localhost:8001")

# Store project information in Engram
project_details = client.get_project(project["id"])
memory_id = engram.store_memory(
    text=f"Project {project_details['name']} created with target completion date of {project_details['target_end_date']}.",
    metadata={
        "type": "project_creation",
        "project_id": project["id"],
        "date": project_details["created_at"]
    }
)

# Retrieve relevant project memories
memories = engram.search_memory(
    query="CI integration project planning",
    limit=5
)

print("Relevant project memories:")
for memory in memories:
    print(f"- {memory['text']}")
```

## Command Line Interface

Prometheus includes a CLI for common operations:

### Basic Commands

```bash
# Create a project
prometheus project create \
  --name "CLI Test Project" \
  --description "Project created via CLI" \
  --start-date 2025-06-01 \
  --end-date 2025-07-31

# List projects
prometheus project list

# Create a task
prometheus task create \
  --project-id "project_123" \
  --name "CLI Test Task" \
  --description "Task created via CLI" \
  --hours 20 \
  --priority medium

# Update task status
prometheus task update \
  --id "task_456" \
  --status "in_progress" \
  --progress 50

# Calculate critical path
prometheus critical-path \
  --project-id "project_123"

# Generate project report
prometheus report \
  --project-id "project_123" \
  --type "status" \
  --format "pdf"
```

## Advanced Features

### Project Templates

Create and use project templates:

```python
# Create a project template
template = client.create_project_template(
    name="CI Integration Project",
    description="Template for CI integration projects",
    phases=[
        {
            "name": "Research",
            "duration_days": 14,
            "tasks": [
                {
                    "name": "Market Research",
                    "estimated_hours": 20,
                    "priority": "high"
                },
                {
                    "name": "Technical Evaluation",
                    "estimated_hours": 30,
                    "priority": "high"
                }
            ]
        },
        {
            "name": "Planning",
            "duration_days": 10,
            "tasks": [
                {
                    "name": "Project Plan Creation",
                    "estimated_hours": 16,
                    "priority": "high"
                },
                {
                    "name": "Resource Allocation",
                    "estimated_hours": 8,
                    "priority": "medium"
                }
            ]
        },
        {
            "name": "Implementation",
            "duration_days": 30,
            "tasks": [
                {
                    "name": "Core Integration",
                    "estimated_hours": 60,
                    "priority": "high"
                },
                {
                    "name": "UI Implementation",
                    "estimated_hours": 40,
                    "priority": "medium"
                }
            ]
        },
        {
            "name": "Testing",
            "duration_days": 14,
            "tasks": [
                {
                    "name": "Integration Testing",
                    "estimated_hours": 30,
                    "priority": "high"
                },
                {
                    "name": "Performance Testing",
                    "estimated_hours": 20,
                    "priority": "medium"
                }
            ]
        }
    ]
)

# Create project from template
new_project = client.create_project_from_template(
    template_id=template["id"],
    name="New CI Integration Project",
    start_date="2025-07-01"
)
```

### Project Forecasting

Use historical data to forecast project completion:

```python
# Generate a project forecast
forecast = client.generate_project_forecast(
    project_id=project["id"],
    forecast_type="completion_date",
    confidence_levels=[50, 80, 95]
)

print("Project Completion Forecast:")
print(f"Most likely (50%): {forecast['forecasts'][50]}")
print(f"Likely (80%): {forecast['forecasts'][80]}")
print(f"Safe bet (95%): {forecast['forecasts'][95]}")
```

### Resource Scenario Planning

Evaluate different resource scenarios:

```python
# Create a scenario
scenario = client.create_resource_scenario(
    project_id=project["id"],
    name="Additional Developer",
    description="Adding one more developer to the team"
)

# Add resource to scenario
client.add_scenario_resource(
    scenario_id=scenario["id"],
    name="Diana Wilson",
    role="Backend Developer",
    availability_hours_per_week=40,
    start_date="2025-06-01"
)

# Evaluate scenario impact
impact = client.evaluate_scenario(scenario["id"])

print("Scenario Impact:")
print(f"Original completion date: {impact['original']['completion_date']}")
print(f"New completion date: {impact['new']['completion_date']}")
print(f"Time saved: {impact['difference_days']} days")
print(f"Cost impact: ${impact['cost_impact']}")
```

## Troubleshooting

### Common Issues

1. **Connection Problems**
   - Check that the Prometheus server is running
   - Verify the server URL in your client configuration
   - Ensure network connectivity between client and server

2. **Data Validation Errors**
   - Check that all required fields are provided
   - Verify date formats (ISO 8601: YYYY-MM-DD)
   - Ensure dependencies are valid (e.g., task IDs exist)

3. **Integration Issues**
   - Verify that integrated services (Telos, Engram) are running
   - Check API keys and permissions
   - Confirm URL configurations are correct

4. **Chart Generation Failures**
   - Ensure required libraries are installed
   - Check file permissions for output directories
   - Verify data completeness for visualization

### Logging

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or configure logging in your application:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("prometheus.log"),
        logging.StreamHandler()
    ]
)

# Get logger
logger = logging.getLogger("prometheus")
```

## Best Practices

1. **Project Planning**
   - Break down large tasks into smaller, manageable tasks
   - Use realistic time estimates with appropriate buffers
   - Define clear dependencies between tasks
   - Set measurable milestones to track progress

2. **Resource Management**
   - Don't overallocate team members (stay under 80% allocation)
   - Account for meetings, administrative tasks, and unexpected issues
   - Update availability regularly to reflect changes
   - Consider skill sets when assigning tasks

3. **Timeline Management**
   - Use phases to group related tasks
   - Add buffer time for unexpected delays
   - Regularly update progress to keep timelines accurate
   - Monitor critical path tasks closely

4. **Risk Management**
   - Identify risks early in the project
   - Develop mitigation strategies for high-impact risks
   - Regularly review and update risk status
   - Add contingency time for high-probability risks

5. **Continuous Improvement**
   - Conduct retrospectives throughout the project
   - Document lessons learned for future projects
   - Implement improvement suggestions promptly
   - Use historical data to improve future estimates

## Conclusion

This guide covers the basics of using Prometheus for project planning and management. For more detailed information, check the [API Reference](./API_REFERENCE.md) and [Technical Documentation](./TECHNICAL_DOCUMENTATION.md).

If you encounter issues or need assistance, please refer to the [Tekton Documentation](../../README.md) for community support options.