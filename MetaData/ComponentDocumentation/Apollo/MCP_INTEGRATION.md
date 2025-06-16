# Apollo FastMCP Integration

This document describes Apollo's comprehensive FastMCP (Model Context Protocol) integration, providing intelligent action planning, execution monitoring, context observation, and protocol management capabilities.

## Overview

Apollo implements FastMCP to provide external systems with programmatic access to intelligent orchestration functionality, AI-powered decision making, and adaptive system management capabilities. The implementation includes 33 specialized tools organized into 7 main capability areas.

## Architecture

### MCP Server Configuration

- **Service Name**: `apollo`
- **Version**: `0.1.0`
- **Base URL**: `http://localhost:8000/api/mcp/v2`
- **Protocol**: FastMCP over HTTP

### Capabilities

Apollo provides seven main MCP capabilities:

1. **Action Planning** - Intelligent planning and optimization of action sequences
2. **Action Execution** - Execute and monitor planned actions with adaptation
3. **Context Observation** - Observe and analyze environmental context and changes
4. **Message Handling** - Intelligent message processing and routing
5. **Predictive Analysis** - Predictive analysis and system behavior forecasting
6. **Protocol Enforcement** - Enforce protocols and maintain system integrity
7. **Token Budgeting** - Manage token budgets and optimize resource allocation

## Capabilities and Tools

### 1. Action Planning Capability

**Capability Name**: `action_planning`  
**Description**: Plan and optimize sequences of actions based on goals and context

#### Tools

##### `PlanActions`
Plan a sequence of actions based on a goal and context.

**Parameters**:
- `goal`: The objective to achieve
- `context`: Current environment state and constraints
- `constraints`: List of limitations and requirements
- `optimization_criteria` (optional): Criteria for action optimization

**Example**:
```json
{
  "tool_name": "PlanActions",
  "arguments": {
    "goal": "optimize system performance",
    "context": {
      "current_load": "high",
      "available_resources": "medium",
      "system_constraints": ["memory_limit", "cpu_threshold"]
    },
    "constraints": ["budget", "time", "risk_tolerance"],
    "optimization_criteria": ["efficiency", "reliability"]
  }
}
```

**Response**:
```json
{
  "success": true,
  "plan": {
    "plan_id": "plan-abc123",
    "goal": "optimize system performance",
    "actions": [
      {
        "action_id": "action-001",
        "type": "scale_resources",
        "priority": 1,
        "estimated_duration": 300,
        "resource_requirements": {"cpu": 2, "memory": "4GB"},
        "dependencies": [],
        "success_probability": 0.95
      },
      {
        "action_id": "action-002", 
        "type": "load_balance",
        "priority": 2,
        "estimated_duration": 180,
        "dependencies": ["action-001"],
        "success_probability": 0.88
      }
    ],
    "total_estimated_duration": 480,
    "overall_success_probability": 0.84,
    "optimization_score": 0.92
  },
  "message": "Action plan generated successfully with 2 optimized actions"
}
```

##### `OptimizeActionSequence`
Optimize an existing sequence of actions for better performance.

##### `EvaluateActionFeasibility`
Evaluate the feasibility of a proposed action given current state.

##### `GenerateActionAlternatives`
Generate alternative actions when primary actions are not feasible.

### 2. Action Execution Capability

**Capability Name**: `action_execution`  
**Description**: Execute planned actions with real-time monitoring and adaptation

#### Tools

##### `ExecuteActionSequence`
Execute a sequence of planned actions with monitoring.

**Parameters**:
- `actions`: List of actions to execute
- `execution_mode`: How to execute ("sequential", "parallel", "conditional")
- `rollback_enabled`: Whether to enable rollback on failure
- `monitoring_interval`: Frequency of progress monitoring

##### `MonitorActionProgress`
Monitor the progress of executing actions in real-time.

##### `AdaptExecutionStrategy`
Adapt execution strategy based on current performance and conditions.

##### `HandleExecutionErrors`
Handle errors during action execution with intelligent recovery.

### 3. Context Observation Capability

**Capability Name**: `context_observation`  
**Description**: Observe, analyze, and interpret environmental context and changes

#### Tools

##### `ObserveContextChanges`
Observe and track changes in the system context.

**Parameters**:
- `observation_scope`: Types of context to observe
- `monitoring_duration`: How long to monitor (seconds)
- `change_sensitivity`: Sensitivity level for detecting changes

##### `AnalyzeContextPatterns`
Analyze patterns in context data to identify trends and anomalies.

##### `PredictContextEvolution`
Predict how the context will evolve over time.

##### `ExtractContextInsights`
Extract actionable insights from context observations.

### 4. Message Handling Capability

**Capability Name**: `message_handling`  
**Description**: Process, analyze, and route messages with intelligent handling

#### Tools

##### `ProcessIncomingMessages`
Process incoming messages with intelligent categorization and prioritization.

##### `RouteMessagesIntelligently`
Route messages to appropriate handlers based on content and context.

##### `AnalyzeMessagePatterns`
Analyze message patterns to identify trends and optimize handling.

##### `OptimizeMessageFlow`
Optimize message flow for better throughput and reduced latency.

### 5. Predictive Analysis Capability

**Capability Name**: `predictive_analysis`  
**Description**: Perform predictive analysis and forecasting of system behavior

#### Tools

##### `PredictSystemBehavior`
Predict future system behavior based on current metrics and trends.

##### `ForecastResourceNeeds`
Forecast future resource requirements based on usage patterns.

##### `AnalyzePerformanceTrends`
Analyze performance trends to identify optimization opportunities.

##### `IdentifyOptimizationOpportunities`
Identify specific opportunities for system optimization.

### 6. Protocol Enforcement Capability

**Capability Name**: `protocol_enforcement`  
**Description**: Enforce protocols and maintain system integrity and compliance

#### Tools

##### `EnforceCommunicationProtocols`
Enforce communication protocols and standards.

##### `ValidateSystemCompliance`
Validate system compliance with established standards.

##### `MonitorProtocolAdherence`
Monitor adherence to protocols and detect violations.

##### `HandleProtocolViolations`
Handle protocol violations with appropriate corrective actions.

### 7. Token Budgeting Capability

**Capability Name**: `token_budgeting`  
**Description**: Manage token budgets and optimize resource allocation

#### Tools

##### `ManageTokenBudgets`
Manage token budgets across different components and services.

##### `OptimizeResourceAllocation`
Optimize allocation of resources based on priorities and demands.

##### `TrackUsagePatterns`
Track usage patterns to inform budget decisions.

##### `PredictBudgetNeeds`
Predict future budget needs based on usage trends.

## Predefined Workflows

Apollo provides 4 predefined workflows that combine multiple tools for common orchestration scenarios:

### 1. Intelligent Action Planning
**Workflow Name**: `intelligent_action_planning`

Comprehensive action planning with optimization and feasibility analysis.

**Parameters**:
- `goal`: Target objective
- `constraints`: System constraints and limitations
- `optimization_level`: "conservative", "moderate", "aggressive"

### 2. Context-Aware Resource Management
**Workflow Name**: `context_aware_resource_management`

Intelligent resource management based on context observation and prediction.

### 3. Protocol Enforcement and Compliance
**Workflow Name**: `protocol_enforcement_compliance`

Comprehensive protocol enforcement and compliance monitoring.

### 4. Predictive System Management
**Workflow Name**: `predictive_system_management`

Proactive system management based on predictive analysis.

## API Endpoints

### Standard MCP Endpoints

- `GET /api/mcp/v2/health` - MCP server health check
- `GET /api/mcp/v2/capabilities` - List all capabilities
- `GET /api/mcp/v2/tools` - List all available tools
- `POST /api/mcp/v2/tools/execute` - Execute a specific tool

### Apollo-Specific Endpoints

- `GET /api/mcp/v2/apollo-status` - Get Apollo system status
- `POST /api/mcp/v2/execute-apollo-workflow` - Execute predefined workflows

## Usage Examples

### Python Client Example

```python
import aiohttp
import asyncio

async def test_apollo_mcp():
    async with aiohttp.ClientSession() as session:
        # Plan actions for system optimization
        planning_payload = {
            "tool_name": "PlanActions",
            "arguments": {
                "goal": "optimize system performance",
                "context": {
                    "current_load": "high",
                    "available_resources": "medium"
                },
                "constraints": ["budget", "time"]
            }
        }
        
        async with session.post(
            "http://localhost:8000/api/mcp/v2/tools/execute",
            json=planning_payload
        ) as response:
            result = await response.json()
            plan_id = result["plan"]["plan_id"]
            print(f"Created plan: {plan_id}")
        
        # Execute the planned actions
        execution_payload = {
            "tool_name": "ExecuteActionSequence",
            "arguments": {
                "actions": result["plan"]["actions"],
                "execution_mode": "sequential",
                "rollback_enabled": True
            }
        }
        
        async with session.post(
            "http://localhost:8000/api/mcp/v2/tools/execute",
            json=execution_payload
        ) as response:
            result = await response.json()
            print(f"Execution started: {result['execution']['execution_id']}")

# Run the example
asyncio.run(test_apollo_mcp())
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000/api/mcp/v2';

async function testApolloMCP() {
    try {
        // Predict system behavior
        const predictionPayload = {
            tool_name: 'PredictSystemBehavior',
            arguments: {
                system_metrics: {
                    cpu_trend: 'increasing',
                    memory_usage: 'stable',
                    network_load: 'variable'
                },
                prediction_scope: ['performance', 'capacity', 'failures'],
                time_horizon: '4 hours'
            }
        };
        
        const response = await axios.post(`${BASE_URL}/tools/execute`, predictionPayload);
        console.log('System behavior prediction:', response.data);
        
        // Analyze context patterns
        const analysisPayload = {
            tool_name: 'AnalyzeContextPatterns',
            arguments: {
                context_data: {
                    time_series: [
                        {timestamp: '2024-01-01T10:00:00Z', cpu_usage: 0.75},
                        {timestamp: '2024-01-01T10:01:00Z', cpu_usage: 0.82}
                    ]
                },
                pattern_types: ['trends', 'cycles', 'anomalies']
            }
        };
        
        const analysisResponse = await axios.post(`${BASE_URL}/tools/execute`, analysisPayload);
        console.log('Context pattern analysis:', analysisResponse.data);
        
    } catch (error) {
        console.error('Error:', error.response?.data || error.message);
    }
}

testApolloMCP();
```

## Integration with Tekton Components

### Hermes Integration
Apollo integrates with Hermes for:
- Service discovery and registration
- Inter-component messaging and coordination
- Event-driven orchestration triggers

### Budget Integration  
Integration with Budget provides:
- Token budget management and optimization
- Cost-aware action planning
- Resource allocation optimization

### Engram Integration
Connection to Engram enables:
- Persistent context memory and learning
- Historical pattern analysis
- Long-term behavior prediction

### LLM Adapter Integration
Apollo leverages the LLM Adapter for:
- Intelligent decision making
- Natural language action planning
- Context analysis and interpretation

## Testing

### Running Tests

Execute the comprehensive test suite:

```bash
# Bash test script
./examples/run_fastmcp_test.sh

# Python async test client  
python3 examples/test_fastmcp.py

# Save test results to JSON
python3 examples/test_fastmcp.py --save-results
```

### Test Coverage

The test suite covers:
- All 33 MCP tools across 7 capabilities
- 4 predefined workflows  
- Apollo-specific endpoints
- Error handling and edge cases
- Performance and response time validation

## Error Handling

### Common Error Responses

```json
{
  "success": false,
  "error": "Invalid action sequence: missing required dependencies"
}
```

```json
{
  "success": false,
  "error": "Insufficient resources for action execution: requires 8GB memory, only 4GB available"
}
```

### HTTP Status Codes

- `200 OK` - Successful tool execution
- `400 Bad Request` - Invalid parameters or tool name
- `404 Not Found` - Tool or resource not found
- `500 Internal Server Error` - Server-side execution error

## Configuration

### Environment Variables

- `APOLLO_PORT` - Port for Apollo server (default: 8000)
- `APOLLO_HOST` - Host binding (default: localhost)
- `MCP_DEBUG` - Enable MCP debug logging
- `ACTION_TIMEOUT` - Default action execution timeout
- `REGISTER_WITH_HERMES` - Auto-register with Hermes service

### MCP Server Settings

```python
# apollo/api/endpoints/mcp.py
fastmcp_server = FastMCPServer(
    name="apollo",
    version="0.1.0", 
    description="Apollo Intelligent Orchestration and Protocol Management MCP Server"
)
```

## Performance Considerations

- **Tool Execution**: Most tools complete within 100-800ms
- **Workflow Execution**: Workflows may take 2-30 seconds depending on complexity
- **Action Planning**: Complex planning operations may take 1-5 seconds
- **Prediction Analysis**: Predictive tools typically complete within 200-1000ms
- **Concurrent Operations**: Supports multiple concurrent orchestration tasks

## Security

### Access Control
- Token-based authentication for sensitive operations
- Role-based access control for different tool categories
- Audit logging for all orchestration activities

### Protocol Enforcement
- Real-time protocol compliance monitoring
- Automatic violation detection and correction
- Security policy enforcement across all operations

## Troubleshooting

### Common Issues

1. **Action Planning Failures**
   - Verify goal and context parameters are well-defined
   - Check that constraints are realistic and achievable

2. **Execution Timeouts**
   - Increase timeout values for complex operations
   - Monitor system resources during execution

3. **Context Observation Issues**
   - Ensure monitoring permissions are properly configured
   - Verify observation scope matches available metrics

### Debug Mode

Enable debug logging:
```bash
export MCP_DEBUG=true
python -m apollo.cli.main
```

## Version History

- **v0.1.0** - Initial FastMCP integration
  - 33 MCP tools across 7 capabilities
  - 4 predefined workflows for common orchestration scenarios
  - Comprehensive action planning and execution framework
  - Full Tekton ecosystem integration

## Future Enhancements

- Advanced machine learning integration for action optimization
- Multi-tenant orchestration support
- Enhanced predictive modeling capabilities
- Real-time collaboration features
- Extended workflow automation and templates