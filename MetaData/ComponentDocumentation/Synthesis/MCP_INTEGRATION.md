# Synthesis MCP Integration

This document describes the FastMCP integration for the Synthesis component, providing data synthesis, integration orchestration, and workflow composition capabilities through the Model Context Protocol (MCP).

## Overview

The Synthesis component implements 16 MCP tools across 3 capability categories:

- **Data Synthesis Capability**: 6 tools for synthesizing and unifying data
- **Integration Orchestration Capability**: 6 tools for orchestrating component integrations
- **Workflow Composition Capability**: 4 tools for composing and executing workflows

## Quick Start

### 1. Start Synthesis

```bash
# Start Synthesis on port 8011
./run_synthesis.sh
```

### 2. Test MCP Integration

```bash
# Run comprehensive test suite
./examples/run_fastmcp_test.sh

# Run Python test client
python examples/test_fastmcp.py
```

### 3. Basic Usage

```bash
# Check MCP capabilities
curl http://localhost:8011/api/mcp/v2/capabilities

# List available tools
curl http://localhost:8011/api/mcp/v2/tools

# Execute a tool
curl -X POST http://localhost:8011/api/mcp/v2/tools/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "synthesize_component_data",
    "arguments": {
      "component_ids": ["athena", "engram"],
      "synthesis_type": "contextual"
    }
  }'
```

## MCP Capabilities

### Data Synthesis Capability

Synthesize and unify data from multiple components and sources.

**Tools:**
- `synthesize_component_data` - Synthesize data from multiple Tekton components
- `create_unified_report` - Create comprehensive reports from multiple data sources
- `merge_data_streams` - Merge multiple data streams with conflict resolution
- `detect_data_conflicts` - Detect and analyze conflicts between data sources
- `optimize_data_flow` - Optimize data flow for better performance
- `validate_synthesis_quality` - Validate the quality of synthesized data

### Integration Orchestration Capability

Orchestrate complex integrations between multiple components.

**Tools:**
- `orchestrate_component_integration` - Orchestrate integration between components
- `design_integration_workflow` - Design integration workflows with patterns
- `monitor_integration_health` - Monitor the health of active integrations
- `resolve_integration_conflicts` - Resolve conflicts in component integrations
- `optimize_integration_performance` - Optimize integration performance
- `validate_integration_completeness` - Validate integration completeness

### Workflow Composition Capability

Compose and execute complex multi-component workflows.

**Tools:**
- `compose_multi_component_workflow` - Compose workflows with multiple components
- `execute_composed_workflow` - Execute previously composed workflows
- `analyze_workflow_performance` - Analyze workflow execution performance
- `optimize_workflow_execution` - Optimize workflow execution strategies

## MCP Endpoints

### Core Endpoints

- `GET /api/mcp/v2/capabilities` - List MCP capabilities
- `GET /api/mcp/v2/tools` - List available tools
- `GET /api/mcp/v2/server/info` - Get server information
- `POST /api/mcp/v2/tools/execute` - Execute a tool

### Synthesis-Specific Endpoints

- `GET /api/mcp/v2/synthesis-status` - Get synthesis system status
- `POST /api/mcp/v2/execute-synthesis-workflow` - Execute predefined workflows

## Synthesis Workflows

Predefined workflows that combine multiple tools for common use cases.

### Data Unification Workflow

Combines data synthesis, conflict detection, and quality validation.

```bash
curl -X POST http://localhost:8011/api/mcp/v2/execute-synthesis-workflow \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_name": "data_unification",
    "parameters": {
      "component_ids": ["athena", "engram"],
      "unification_strategy": "merge_with_conflict_resolution",
      "quality_threshold": 0.8
    }
  }'
```

### Component Integration Workflow

Orchestrates complete component integration including health monitoring.

```bash
curl -X POST http://localhost:8011/api/mcp/v2/execute-synthesis-workflow \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_name": "component_integration",
    "parameters": {
      "primary_component": "athena",
      "target_components": ["engram"],
      "integration_type": "bidirectional"
    }
  }'
```

### Workflow Orchestration Workflow

Composition and optimization of multi-component workflows.

```bash
curl -X POST http://localhost:8011/api/mcp/v2/execute-synthesis-workflow \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_name": "workflow_orchestration",
    "parameters": {
      "workflow_components": [
        {"component_id": "athena", "role": "knowledge_provider"}
      ],
      "workflow_type": "sequential",
      "optimization_goals": ["performance"]
    }
  }'
```

### End-to-End Synthesis Workflow

Complete synthesis pipeline from data collection to execution.

```bash
curl -X POST http://localhost:8011/api/mcp/v2/execute-synthesis-workflow \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_name": "end_to_end_synthesis",
    "parameters": {
      "source_components": ["athena", "engram"],
      "synthesis_objectives": ["unify_knowledge", "optimize_performance"],
      "integration_requirements": {
        "athena": {"mode": "query"},
        "engram": {"mode": "memory"}
      }
    }
  }'
```

## Tool Examples

### Data Synthesis Tools

#### Synthesize Component Data

```json
{
  "tool_name": "synthesize_component_data",
  "arguments": {
    "component_ids": ["athena", "engram"],
    "synthesis_type": "contextual",
    "include_metadata": true,
    "synthesis_scope": "full_context"
  }
}
```

#### Create Unified Report

```json
{
  "tool_name": "create_unified_report",
  "arguments": {
    "data_sources": ["athena", "engram"],
    "report_format": "comprehensive",
    "include_visualizations": true,
    "aggregation_level": "detailed"
  }
}
```

### Integration Orchestration Tools

#### Orchestrate Component Integration

```json
{
  "tool_name": "orchestrate_component_integration",
  "arguments": {
    "primary_component": "athena",
    "target_components": ["engram"],
    "integration_type": "bidirectional",
    "orchestration_strategy": "adaptive"
  }
}
```

#### Monitor Integration Health

```json
{
  "tool_name": "monitor_integration_health",
  "arguments": {
    "integration_id": "athena_engram_integration",
    "monitoring_metrics": ["connectivity", "performance", "data_consistency"],
    "monitoring_duration": 60
  }
}
```

### Workflow Composition Tools

#### Compose Multi-Component Workflow

```json
{
  "tool_name": "compose_multi_component_workflow",
  "arguments": {
    "component_definitions": [
      {
        "component_id": "athena",
        "role": "knowledge_provider",
        "dependencies": [],
        "configuration": {"mode": "query"}
      },
      {
        "component_id": "engram",
        "role": "memory_manager",
        "dependencies": ["athena"],
        "configuration": {"mode": "memory"}
      }
    ],
    "workflow_type": "sequential",
    "optimization_hints": ["performance", "reliability"]
  }
}
```

#### Execute Composed Workflow

```json
{
  "tool_name": "execute_composed_workflow",
  "arguments": {
    "workflow_id": "knowledge_synthesis_workflow",
    "execution_mode": "synchronous",
    "timeout_seconds": 300
  }
}
```

## Error Handling

All tools return structured responses with error information:

```json
{
  "success": false,
  "error": "Invalid component_id: 'nonexistent_component'",
  "error_code": "INVALID_COMPONENT",
  "details": {
    "available_components": ["athena", "engram", "ergon"]
  }
}
```

## Integration with Other Components

### Hermes Integration

Synthesis automatically registers with Hermes for service discovery:

```python
# Component registration happens automatically on startup
component = SynthesisComponent(
    component_id="synthesis",
    component_name="Synthesis",
    hermes_registration=True
)
```

### Port Configuration

Synthesis runs on port 8011 following the Single Port Architecture:

```python
from synthesis.utils.port_config import get_synthesis_port
port = get_synthesis_port()  # Returns 8011
```

## Testing

### Test Scripts

1. **Bash Test Script**: `examples/run_fastmcp_test.sh`
   - Comprehensive endpoint testing
   - 18 different test cases
   - Color-coded output
   - Error handling validation

2. **Python Test Client**: `examples/test_fastmcp.py`
   - Async HTTP client
   - Tool and workflow testing
   - Detailed result analysis
   - JSON response validation

### Running Tests

```bash
# Run all tests
./examples/run_fastmcp_test.sh

# Run Python client tests
python examples/test_fastmcp.py

# Run specific tool test
curl -X POST http://localhost:8011/api/mcp/v2/tools/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "synthesize_component_data", "arguments": {"component_ids": ["athena"]}}'
```

## Performance Considerations

- **Tool Execution**: Most tools complete in under 100ms
- **Workflow Execution**: Complex workflows may take 1-5 seconds
- **Data Synthesis**: Large datasets may require longer processing times
- **Integration Monitoring**: Continuous monitoring has minimal overhead

## Troubleshooting

### Common Issues

1. **Connection Refused**: Ensure Synthesis is running on port 8011
2. **Tool Not Found**: Check tool name spelling and availability
3. **Invalid Arguments**: Validate argument types and required fields
4. **Timeout Errors**: Increase timeout for complex operations

### Debug Commands

```bash
# Check if Synthesis is running
curl http://localhost:8011/health

# List available tools
curl http://localhost:8011/api/mcp/v2/tools

# Check server status
curl http://localhost:8011/api/mcp/v2/synthesis-status

# View server logs
tail -f synthesis.log
```

## Future Enhancements

- **Real-time Monitoring**: WebSocket-based tool execution monitoring
- **Batch Operations**: Execute multiple tools in a single request
- **Workflow Templates**: Pre-defined workflow templates for common patterns
- **Advanced Analytics**: Detailed performance and usage analytics
- **Plugin System**: Support for custom synthesis plugins

For more information, see the main [Synthesis documentation](README.md) and [Tekton architecture documentation](../docs/ARCHITECTURE.md).
