# Prometheus MCP Integration

This document describes the FastMCP (Model Context Protocol) integration for Prometheus, the planning and retrospective analysis system in the Tekton ecosystem.

## Overview

Prometheus integrates with FastMCP to provide external systems (like Claude Code and other AI tools) with programmatic access to planning, retrospective analysis, resource management, and improvement recommendation capabilities. This integration enables AI systems to create project plans, analyze performance, optimize resources, and generate actionable insights.

## Architecture

The MCP integration follows the established Tekton FastMCP pattern:

- **FastMCP Server**: Integrated into the Prometheus API server on startup
- **Tool Definitions**: Decorator-based tool definitions using `@mcp_tool`
- **Capability Organization**: Tools grouped into logical capabilities
- **Endpoint Integration**: Standard MCP endpoints under `/api/mcp/v2`
- **Workflow Support**: Predefined analysis workflows for complex operations

## Capabilities

### 1. Planning (`planning`)

Comprehensive project planning and timeline management:

- **create_project_plan**: Create detailed project plans with milestones
- **analyze_critical_path**: Analyze project critical path and dependencies
- **optimize_timeline**: Optimize project timelines for efficiency
- **create_milestone**: Add milestones to existing project plans

### 2. Resource Management (`resource_management`)

Resource allocation and capacity planning:

- **allocate_resources**: Assign resources to project tasks optimally
- **analyze_resource_capacity**: Identify capacity bottlenecks and utilization

### 3. Retrospective Analysis (`retrospective_analysis`)

Performance analysis and lessons learned:

- **conduct_retrospective**: Analyze completed project performance
- **analyze_performance_trends**: Identify trends across multiple projects

### 4. Improvement Recommendations (`improvement_recommendations`)

AI-driven process improvements:

- **generate_improvement_recommendations**: AI-generated improvement suggestions
- **prioritize_improvements**: Prioritize improvements by impact vs effort

## Tool Reference

### Planning Tools

#### create_project_plan

Creates a comprehensive project plan with automatic milestone generation.

**Parameters:**
- `project_name` (string, required): Project name
- `description` (string, required): Detailed project description
- `start_date` (string, required): Start date (YYYY-MM-DD format)
- `end_date` (string, required): End date (YYYY-MM-DD format)
- `objectives` (list[string], required): List of project objectives
- `constraints` (list[string], optional): Project constraints
- `stakeholders` (list[string], optional): Project stakeholders
- `budget` (float, optional): Project budget
- `priority` (string, optional): Priority level (low, medium, high, critical)

**Returns:**
- `success` (boolean): Operation success status
- `plan` (object): Created project plan with details
- `milestones_count` (integer): Number of generated milestones
- `message` (string): Operation result message

**Example:**
```json
{
  "tool_name": "create_project_plan",
  "arguments": {
    "project_name": "Mobile App Development",
    "description": "Develop a cross-platform mobile application",
    "start_date": "2024-07-01",
    "end_date": "2024-12-31",
    "objectives": [
      "Deliver iOS and Android applications",
      "Achieve 4.5+ app store rating",
      "Support 100,000+ concurrent users"
    ],
    "constraints": ["Limited budget", "Fixed launch date"],
    "budget": 250000.0,
    "priority": "high"
  }
}
```

#### analyze_critical_path

Analyzes the critical path of project tasks to identify bottlenecks.

**Parameters:**
- `plan_id` (string, required): Project plan identifier
- `tasks` (list[object], required): List of tasks with dependencies and durations

**Returns:**
- `success` (boolean): Operation success status
- `project_duration` (integer): Total project duration
- `critical_path` (list): Tasks on the critical path
- `critical_path_length` (integer): Number of critical path tasks

#### optimize_timeline

Optimizes project timelines for specified criteria.

**Parameters:**
- `plan_id` (string, required): Project plan identifier
- `constraints` (object, optional): Additional optimization constraints
- `optimization_criteria` (string, optional): Optimization focus (duration, cost, resources)

**Returns:**
- `success` (boolean): Operation success status
- `results` (object): Optimization results and strategies
- `message` (string): Optimization summary

### Resource Management Tools

#### allocate_resources

Optimally allocates resources to project tasks.

**Parameters:**
- `plan_id` (string, required): Project plan identifier
- `resources` (list[object], required): Available resources with skills and rates
- `tasks` (list[object], required): Tasks requiring resource allocation
- `optimization_strategy` (string, optional): Allocation strategy (balanced, speed, cost)

**Returns:**
- `success` (boolean): Operation success status
- `allocations` (list): Resource allocation assignments
- `total_allocations` (integer): Number of allocations made
- `estimated_total_cost` (float): Total estimated cost

**Example:**
```json
{
  "tool_name": "allocate_resources",
  "arguments": {
    "plan_id": "mobile_app_project",
    "resources": [
      {
        "id": "dev1",
        "name": "Senior Mobile Developer",
        "skills": ["react_native", "ios", "android"],
        "hourly_rate": 150,
        "capacity": 100
      }
    ],
    "tasks": [
      {
        "id": "app_development",
        "name": "Core App Development",
        "required_skills": ["react_native"],
        "duration": 60,
        "effort_required": 80
      }
    ],
    "optimization_strategy": "balanced"
  }
}
```

#### analyze_resource_capacity

Analyzes resource capacity to identify bottlenecks and optimization opportunities.

**Parameters:**
- `resources` (list[object], required): Resources to analyze
- `time_period` (string, optional): Analysis period (weekly, monthly, quarterly)

**Returns:**
- `success` (boolean): Operation success status
- `analysis` (object): Detailed capacity analysis
- `message` (string): Analysis summary

### Retrospective Analysis Tools

#### conduct_retrospective

Conducts comprehensive retrospective analysis of completed projects.

**Parameters:**
- `project_id` (string, required): Completed project identifier
- `planned_metrics` (object, required): Originally planned metrics
- `actual_metrics` (object, required): Actual performance metrics
- `team_feedback` (list[string], optional): Team observations and feedback

**Returns:**
- `success` (boolean): Operation success status
- `retrospective` (object): Detailed retrospective analysis
- `message` (string): Analysis summary

**Example:**
```json
{
  "tool_name": "conduct_retrospective",
  "arguments": {
    "project_id": "mobile_app_v1",
    "planned_metrics": {
      "duration": 180,
      "budget": 250000,
      "quality_score": 95,
      "team_satisfaction": 85
    },
    "actual_metrics": {
      "duration": 195,
      "budget": 270000,
      "quality_score": 92,
      "team_satisfaction": 88
    },
    "team_feedback": [
      "Scope creep impacted timeline",
      "Technical challenges underestimated",
      "Good team collaboration throughout"
    ]
  }
}
```

#### analyze_performance_trends

Analyzes performance trends across multiple projects.

**Parameters:**
- `projects` (list[object], required): Historical project data
- `metrics` (list[string], required): Metrics to analyze for trends
- `time_period` (string, optional): Analysis time period

**Returns:**
- `success` (boolean): Operation success status
- `trends` (object): Trend analysis for each metric
- `message` (string): Analysis summary

### Improvement Recommendation Tools

#### generate_improvement_recommendations

Generates AI-driven improvement recommendations based on project data.

**Parameters:**
- `project_data` (object, required): Historical project performance data
- `focus_areas` (list[string], optional): Areas to focus on (planning, execution, quality)
- `constraint_types` (list[string], optional): Constraint types to consider

**Returns:**
- `success` (boolean): Operation success status
- `recommendations` (object): Categorized improvement recommendations
- `message` (string): Generation summary

#### prioritize_improvements

Prioritizes improvement initiatives based on impact and effort analysis.

**Parameters:**
- `improvements` (list[object], required): Improvement initiatives to prioritize
- `constraints` (object, optional): Resource and time constraints

**Returns:**
- `success` (boolean): Operation success status
- `prioritized_improvements` (object): Improvements grouped by priority tier
- `message` (string): Prioritization summary

## Workflow Execution

The MCP integration supports predefined analysis workflows that combine multiple operations:

### full_project_analysis

Comprehensive project analysis including planning, critical path analysis, retrospective, and improvement recommendations.

**Parameters:**
- `project_data` (object): Complete project information
- `focus_areas` (list[string], optional): Analysis focus areas

### resource_optimization

Resource optimization workflow including capacity analysis and allocation optimization.

**Parameters:**
- `resources` (list): Available resources
- `tasks` (list): Tasks requiring allocation
- `plan_id` (string): Project plan identifier
- `optimization_strategy` (string, optional): Optimization approach

### retrospective_with_improvements

Retrospective analysis combined with improvement recommendations and prioritization.

**Parameters:**
- `project_id` (string): Completed project identifier
- `planned_metrics` (object): Planned performance metrics
- `actual_metrics` (object): Actual performance metrics
- `historical_projects` (list, optional): Historical data for trends

### capacity_planning

Forward-looking capacity planning for future projects.

**Parameters:**
- `current_resources` (list): Current resource inventory
- `future_projects` (list): Planned future projects
- `time_period` (string, optional): Planning horizon

## API Endpoints

### Standard MCP Endpoints

- `GET /api/mcp/v2/health` - MCP server health check
- `GET /api/mcp/v2/capabilities` - List available capabilities
- `GET /api/mcp/v2/tools` - List available tools
- `POST /api/mcp/v2/process` - Execute MCP tools

### Prometheus-Specific Endpoints

- `GET /api/mcp/v2/planning-status` - Get planning system status
- `POST /api/mcp/v2/execute-analysis-workflow` - Execute predefined workflows

## Usage Examples

### Basic Project Planning

```python
import aiohttp
import asyncio

async def create_project_and_analyze():
    async with aiohttp.ClientSession() as session:
        # Create a project plan
        create_request = {
            "tool_name": "create_project_plan",
            "arguments": {
                "project_name": "E-commerce Platform",
                "description": "Build a modern e-commerce platform",
                "start_date": "2024-08-01",
                "end_date": "2025-03-31",
                "objectives": [
                    "Launch MVP with core shopping features",
                    "Support 10,000 products",
                    "Handle 1,000 concurrent users"
                ],
                "budget": 500000.0,
                "priority": "high"
            }
        }
        
        async with session.post(
            "http://localhost:8006/api/mcp/v2/process",
            json=create_request
        ) as response:
            result = await response.json()
            plan_id = result["result"]["plan"]["plan_id"]
            print("Project plan created:", plan_id)

asyncio.run(create_project_and_analyze())
```

### Resource Optimization Workflow

```python
async def optimize_resources():
    async with aiohttp.ClientSession() as session:
        workflow_request = {
            "workflow_name": "resource_optimization",
            "parameters": {
                "resources": [
                    {
                        "id": "team_a",
                        "name": "Frontend Team",
                        "capacity": 100,
                        "current_utilization": 85,
                        "skills": ["react", "typescript", "ui_design"]
                    },
                    {
                        "id": "team_b",
                        "name": "Backend Team",
                        "capacity": 100,
                        "current_utilization": 90,
                        "skills": ["python", "databases", "api_design"]
                    }
                ],
                "tasks": [
                    {
                        "id": "frontend_dev",
                        "name": "Frontend Development",
                        "required_skills": ["react"],
                        "duration": 30
                    }
                ],
                "optimization_strategy": "balanced"
            }
        }
        
        async with session.post(
            "http://localhost:8006/api/mcp/v2/execute-analysis-workflow",
            json=workflow_request
        ) as response:
            result = await response.json()
            print("Resource optimization completed")
            print("Bottlenecks:", len(result["result"]["capacity_analysis"]["analysis"]["bottlenecks"]))

asyncio.run(optimize_resources())
```

### Comprehensive Retrospective Analysis

```python
async def conduct_project_retrospective():
    async with aiohttp.ClientSession() as session:
        workflow_request = {
            "workflow_name": "retrospective_with_improvements",
            "parameters": {
                "project_id": "ecommerce_v1",
                "planned_metrics": {
                    "duration": 240,  # 8 months
                    "budget": 500000,
                    "quality_score": 90,
                    "user_satisfaction": 85
                },
                "actual_metrics": {
                    "duration": 270,  # 9 months (3 weeks over)
                    "budget": 520000,  # 4% over budget
                    "quality_score": 88,  # slightly under
                    "user_satisfaction": 92  # exceeded expectations
                },
                "team_feedback": [
                    "Integration testing took longer than expected",
                    "Third-party API changes caused delays",
                    "Team worked well under pressure"
                ]
            }
        }
        
        async with session.post(
            "http://localhost:8006/api/mcp/v2/execute-analysis-workflow",
            json=workflow_request
        ) as response:
            result = await response.json()
            
            retrospective = result["result"]["retrospective"]["retrospective"]
            improvements = result["result"]["improvement_recommendations"]
            
            print("Retrospective completed")
            print("Overall rating:", retrospective["overall_rating"])
            print("Improvements identified:", improvements["recommendations"]["total_count"])

asyncio.run(conduct_project_retrospective())
```

## Testing

The Prometheus MCP integration includes comprehensive testing:

### Run Tests

```bash
# Run the test suite
cd /path/to/Tekton/Prometheus
./examples/run_fastmcp_test.sh
```

### Test Coverage

The test suite covers:

- Health check and MCP status verification
- Capability and tool discovery
- All planning operations (plans, critical path, optimization)
- Resource management (allocation, capacity analysis)
- Retrospective analysis and trend identification
- Improvement recommendations and prioritization
- Workflow execution and complex scenarios
- Error handling and edge cases

### Manual Testing

You can also test individual tools using curl:

```bash
# Test project plan creation
curl -X POST "http://localhost:8006/api/mcp/v2/process" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "create_project_plan",
    "arguments": {
      "project_name": "Test Project",
      "description": "A test project via MCP",
      "start_date": "2024-08-01",
      "end_date": "2024-12-31",
      "objectives": ["Test objective 1", "Test objective 2"]
    }
  }'

# Test workflow execution
curl -X POST "http://localhost:8006/api/mcp/v2/execute-analysis-workflow" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_name": "capacity_planning",
    "parameters": {
      "current_resources": [
        {
          "id": "dev_team",
          "name": "Development Team",
          "capacity": 100,
          "current_utilization": 75
        }
      ],
      "future_projects": []
    }
  }'
```

## Integration with Other Tekton Components

### Metis Task Management Integration

Prometheus can work with Metis to convert high-level project plans into detailed task breakdowns:

```python
# Create plan in Prometheus, then import tasks to Metis
plan_result = await create_project_plan(...)
# Use Metis MCP to create detailed tasks from plan
```

### Telos Requirements Integration

Import requirements from Telos for project planning:

```python
# Get requirements from Telos, use in Prometheus planning
requirements_result = await telos_get_requirements(...)
plan_result = await create_project_plan(
    objectives=[req["description"] for req in requirements_result["requirements"]]
)
```

### Engram Memory Integration

Store and retrieve planning insights using Engram:

```python
# Store retrospective insights in Engram for future planning
retrospective_result = await conduct_retrospective(...)
await engram_store_memory(
    content=retrospective_result["retrospective"]["insights"],
    category="planning_insights"
)
```

## Error Handling

All MCP tools include comprehensive error handling:

- **Planning Errors**: Invalid dates, insufficient project data
- **Resource Errors**: Capacity conflicts, skill mismatches
- **Analysis Errors**: Missing metrics, insufficient historical data
- **Workflow Errors**: Invalid parameters, dependency failures

Example error response:
```json
{
  "success": false,
  "error": "Invalid date format. Expected YYYY-MM-DD, got '2024-13-01'",
  "tool_name": "create_project_plan"
}
```

## Performance Optimization

- **Parallel Processing**: Resource allocation and analysis operations run concurrently
- **Intelligent Caching**: Planning calculations cached for repeated use
- **Batch Operations**: Multiple project analyses can be batched
- **Lazy Evaluation**: Complex calculations only performed when needed

## Security Considerations

- MCP endpoints are currently unauthenticated - implement authentication for production
- Input validation on all planning parameters
- Resource allocation respects capacity constraints
- Sensitive project data should be encrypted in transit

## Best Practices

### Planning Guidelines

1. **Detailed Objectives**: Provide specific, measurable objectives
2. **Realistic Constraints**: Include all known project constraints
3. **Historical Data**: Use past project data for better estimates
4. **Regular Updates**: Update plans based on actual progress

### Resource Management

1. **Skill Matching**: Ensure resource skills align with task requirements
2. **Capacity Planning**: Monitor utilization to prevent overallocation
3. **Cross-Training**: Identify skill bottlenecks and plan training
4. **Flexible Allocation**: Build in capacity for unexpected requirements

### Retrospective Analysis

1. **Comprehensive Metrics**: Track both quantitative and qualitative metrics
2. **Team Feedback**: Include diverse perspectives in retrospectives
3. **Trend Analysis**: Look for patterns across multiple projects
4. **Action Items**: Convert insights into actionable improvements

## Conclusion

The Prometheus MCP integration provides a comprehensive and powerful interface for project planning, resource management, retrospective analysis, and continuous improvement. It enables seamless integration with AI tools and external systems while maintaining the robustness and sophistication of advanced project management capabilities.

For more information, see:
- [Prometheus API Reference](docs/api_reference.md)
- [Tekton FastMCP Documentation](../tekton-core/tekton/mcp/fastmcp/README.md)
- [MCP Unified Integration Sprint Progress](../MetaData/DevelopmentSprints/MCP_Unified_Integration_Sprint/ProgressSummary.md)