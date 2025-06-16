# Apollo User Guide

This guide provides practical instructions for using Apollo's context monitoring, predictive planning, and token budgeting features. It focuses on day-to-day usage rather than technical implementation.

## Table of Contents

- [Introduction](#introduction)
- [Getting Started](#getting-started)
- [Context Monitoring](#context-monitoring)
- [Prediction Analysis](#prediction-analysis)
- [Action Management](#action-management)
- [Token Budgeting](#token-budgeting)
- [Protocol Management](#protocol-management)
- [Dashboard Usage](#dashboard-usage)
- [CLI Usage](#cli-usage)
- [Advanced Features](#advanced-features)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Introduction

Apollo is the executive coordinator and predictive planning system for Tekton, designed to monitor LLM context health, manage token budgets, and optimize performance through intelligent action recommendations. It serves as the guardian-advisor for your LLM operations, helping prevent issues before they occur and maintaining optimal system health.

## Getting Started

### Installation

Apollo is typically installed as part of the Tekton ecosystem:

```bash
# Clone the Tekton repository
git clone https://github.com/yourusername/Tekton.git
cd Tekton

# Install Apollo dependencies
cd Apollo
./setup.sh
```

### Running Apollo

Start Apollo using the provided script:

```bash
./run_apollo.sh
```

### Verifying Installation

Confirm Apollo is running by checking its status:

```bash
# Using curl
curl http://localhost:8001/api/status

# Using the Apollo CLI
./apollo/cli/apollo status
```

### Accessing the Web Interface

Apollo's web interface is accessible through the Hephaestus UI:

1. Ensure Hephaestus is running: `./scripts/tekton-launch --components hephaestus`
2. Open a web browser and navigate to `http://localhost:8080`
3. Select the Apollo component from the sidebar

## Context Monitoring

Apollo continuously monitors LLM contexts to assess their health and performance.

### Viewing Active Contexts

#### Using the Web Interface:

1. Navigate to the Apollo component in Hephaestus
2. Select the "Sessions" tab to view all active contexts
3. Contexts are color-coded by health status:
   - 🟢 Green: Excellent health
   - 🟡 Yellow: Good health
   - 🟠 Orange: Fair health
   - 🔴 Red: Poor health
   - ⚫ Black: Critical health

#### Using the CLI:

```bash
# List all contexts
./apollo/cli/apollo contexts

# List contexts with specific health status
./apollo/cli/apollo contexts --health poor
```

#### Using the API:

```bash
# Get all contexts
curl http://localhost:8001/api/contexts

# Filter by health status
curl http://localhost:8001/api/contexts?health=poor
```

### Context Details

To view detailed information about a specific context:

#### Using the Web Interface:

1. Navigate to the "Sessions" tab
2. Click on a specific context ID to view its details
3. You'll see:
   - Context metrics (token count, utilization, etc.)
   - Health status and history
   - Associated predictions
   - Recommended actions

#### Using the CLI:

```bash
# Get details for a specific context
./apollo/cli/apollo context ctx_123456

# Display the context dashboard
./apollo/cli/apollo context ctx_123456 --dashboard
```

#### Using the API:

```bash
# Get context details
curl http://localhost:8001/api/contexts/ctx_123456

# Get comprehensive dashboard data
curl http://localhost:8001/api/contexts/ctx_123456/dashboard
```

### Context Metrics

Apollo tracks several key metrics for each LLM context:

- **Token Count**: Total tokens in the context
- **Token Utilization**: Percentage of maximum token capacity used
- **Repetition Score**: Measure of redundant content
- **Coherence Score**: Measure of semantic coherence
- **Self-Reference Score**: Measure of model self-references
- **Token Growth Rate**: Rate of token accumulation

These metrics are used to calculate an overall health score, which determines the context's health status.

## Prediction Analysis

Apollo predicts future context states to help you anticipate potential issues.

### Viewing Predictions

#### Using the Web Interface:

1. Navigate to the "Forecasting" tab
2. View all current predictions, sorted by prediction time horizon
3. Predictions are color-coded by predicted health status
4. Each prediction shows:
   - Current health status
   - Predicted health status
   - Time horizon (e.g., +30min, +60min)
   - Confidence score
   - Key factors influencing the prediction

#### Using the CLI:

```bash
# Get all predictions
./apollo/cli/apollo predictions

# Get predictions for a specific context
./apollo/cli/apollo predictions ctx_123456

# Get critical predictions only
./apollo/cli/apollo predictions --critical
```

#### Using the API:

```bash
# Get all predictions
curl http://localhost:8001/api/predictions

# Get predictions for a specific context
curl http://localhost:8001/api/predictions/ctx_123456

# Get predictions with specific predicted health
curl http://localhost:8001/api/predictions?health=critical
```

### Understanding Predictions

Each prediction includes:

1. **Current Health**: The context's current health status
2. **Predicted Health**: The projected future health status
3. **Time Horizon**: When the prediction is for (e.g., 30 minutes in the future)
4. **Confidence**: Confidence level in the prediction (0.0-1.0)
5. **Factors**: Key metrics contributing to the prediction
6. **Basis**: Analytical method used for the prediction

Higher confidence predictions (>0.8) are generally more reliable. Pay special attention to predictions with high confidence and poor/critical predicted health.

### Using Predictions Effectively

- **Early Intervention**: Apply recommended actions for contexts with declining predicted health
- **Resource Planning**: Allocate resources based on future context needs
- **Session Management**: Plan LLM session refreshes based on prediction horizons
- **Trend Analysis**: Identify patterns in prediction data to optimize system configuration

## Action Management

Apollo recommends actions to maintain or improve context health.

### Viewing Recommended Actions

#### Using the Web Interface:

1. Navigate to the "Actions" tab
2. View all recommended actions, sorted by priority
3. Each action shows:
   - Priority level
   - Associated context
   - Action type
   - Description
   - Expected impact

#### Using the CLI:

```bash
# Get all actions
./apollo/cli/apollo actions

# Get actions for a specific context
./apollo/cli/apollo actions ctx_123456

# Get only critical actions
./apollo/cli/apollo actions --priority critical
```

#### Using the API:

```bash
# Get all actions
curl http://localhost:8001/api/actions

# Get actions for a specific context
curl http://localhost:8001/api/actions/ctx_123456

# Get only actionable-now actions
curl http://localhost:8001/api/actions?actionable_now=true
```

### Action Types

Apollo recommends several types of actions:

1. **Context Reduction**: Remove redundant or less relevant information
2. **Context Restructuring**: Reorganize context for better coherence
3. **Token Management**: Apply token optimization strategies
4. **Model Switching**: Switch to a different LLM for better handling
5. **Session Refresh**: Start a new LLM session with optimized context
6. **Parameter Adjustment**: Modify LLM parameters (temperature, etc.)

### Applying Actions

#### Using the Web Interface:

1. Navigate to the "Actions" tab
2. Select an action you want to apply
3. Click "Apply Action"
4. Confirm the action application
5. View the results after application

#### Using the CLI:

```bash
# Apply a specific action
./apollo/cli/apollo action apply act_789012

# Apply all critical actions
./apollo/cli/apollo actions apply-all --priority critical
```

#### Using the API:

```bash
# Mark an action as applied
curl -X POST http://localhost:8001/api/actions/act_789012/applied \
  -H "Content-Type: application/json" \
  -d '{
    "result": "success",
    "notes": "Applied context reduction, removed 500 tokens"
  }'
```

### Action Results

After applying an action, Apollo tracks its effectiveness by:

1. Comparing pre-action and post-action context health
2. Measuring the impact on specific metrics (token count, etc.)
3. Recording the actual versus expected impact
4. Updating its action recommendation system based on results

## Token Budgeting

Apollo manages token budgets for different LLM operations and model tiers.

### Viewing Token Budgets

#### Using the Web Interface:

1. Navigate to the "Token Budgets" tab
2. View current budget allocations by:
   - Model tier (Lightweight, Midweight, Heavyweight)
   - Component (Rhetor, Codex, etc.)
   - Time period (Hourly, Daily, Weekly, Monthly)

#### Using the CLI:

```bash
# View all budget policies
./apollo/cli/apollo budgets policies

# View current budget usage
./apollo/cli/apollo budgets usage

# View budget by component
./apollo/cli/apollo budgets usage --component rhetor
```

#### Using the API:

```bash
# Get budget policies
curl http://localhost:8001/api/budget/policies

# Get budget usage summary
curl http://localhost:8001/api/budget/usage

# Get usage for a specific tier
curl http://localhost:8001/api/budget/usage?tier=remote_heavyweight
```

### Budget Allocation

When you need tokens for an LLM operation:

#### Using the API:

```bash
# Request a token allocation
curl -X POST http://localhost:8001/api/budget/allocate \
  -H "Content-Type: application/json" \
  -d '{
    "context_id": "ctx_123456",
    "component": "rhetor",
    "tier": "remote_heavyweight",
    "provider": "anthropic",
    "model": "claude-3-7-sonnet",
    "task_type": "completion",
    "priority": 8,
    "tokens_requested": 10000
  }'
```

The response will include:

```json
{
  "allocation_id": "alloc_789def",
  "context_id": "ctx_123456",
  "component": "rhetor",
  "tier": "remote_heavyweight",
  "provider": "anthropic",
  "model": "claude-3-7-sonnet",
  "task_type": "completion",
  "priority": 8,
  "tokens_allocated": 10000,
  "tokens_used": 0,
  "creation_time": "2025-04-15T11:40:33Z",
  "expiration_time": "2025-04-16T11:40:33Z",
  "is_active": true
}
```

### Recording Token Usage

After using tokens from an allocation:

#### Using the API:

```bash
# Record token usage
curl -X POST http://localhost:8001/api/budget/usage \
  -H "Content-Type: application/json" \
  -d '{
    "allocation_id": "alloc_789def",
    "tokens_used": 4280,
    "usage_type": "total",
    "operation_id": "op_012xyz"
  }'
```

### Budget Policies

Apollo supports different budget policy types:

1. **IGNORE**: Track usage but don't enforce limits
2. **WARN**: Warn when limits are exceeded but allow operations
3. **SOFT_LIMIT**: Scale token allocation based on priority when near limits
4. **HARD_LIMIT**: Strictly enforce token limits

## Protocol Management

Apollo defines and enforces communication protocols between components.

### Viewing Protocols

#### Using the Web Interface:

1. Navigate to the "Protocols" tab
2. View all defined protocols
3. Each protocol shows:
   - Protocol name and description
   - Enforcement mode
   - Applicable components
   - Version and status

#### Using the CLI:

```bash
# List all protocols
./apollo/cli/apollo protocols

# Get details for a specific protocol
./apollo/cli/apollo protocol proto_123
```

#### Using the API:

```bash
# Get all protocols
curl http://localhost:8001/api/protocols

# Get a specific protocol
curl http://localhost:8001/api/protocols/proto_123

# Get protocol violations
curl http://localhost:8001/api/protocols/violations
```

### Protocol Types

Apollo manages several types of protocols:

1. **Message Format**: Standards for message structure
2. **Request Flow**: Proper sequencing for operations
3. **Response Format**: Standards for response data
4. **Event Sequencing**: Proper ordering of events
5. **Error Handling**: Standards for error responses

### Protocol Validation

To validate a message against a protocol:

#### Using the API:

```bash
# Validate a message against a protocol
curl -X POST http://localhost:8001/api/protocols/validate \
  -H "Content-Type: application/json" \
  -d '{
    "protocol_id": "proto_123",
    "message": {
      "message_id": "msg_123456",
      "source": "rhetor",
      "destination": "engram",
      "content": {
        "type": "memory_store",
        "data": {
          "memory_id": "mem_789012",
          "content": "Example memory content"
        }
      }
    }
  }'
```

## Dashboard Usage

Apollo's dashboard provides a comprehensive view of system health and operations.

### System Dashboard

#### Using the Web Interface:

1. Navigate to the "Dashboard" tab
2. View the system overview, including:
   - Active context count and health distribution
   - Token usage by tier and component
   - Critical contexts and predictions
   - Pending actions
   - Component status

#### Using the CLI:

```bash
# Display system dashboard
./apollo/cli/apollo dashboard

# Get system status
./apollo/cli/apollo status
```

#### Using the API:

```bash
# Get system status
curl http://localhost:8001/api/status
```

### Context Dashboard

For a comprehensive view of a specific context:

#### Using the Web Interface:

1. Navigate to the "Sessions" tab
2. Click on a context ID
3. View the context dashboard, including:
   - Context metrics and health
   - Historical trends
   - Predictions at different time horizons
   - Recommended actions
   - Token usage

#### Using the CLI:

```bash
# Display context dashboard
./apollo/cli/apollo context ctx_123456 --dashboard
```

#### Using the API:

```bash
# Get context dashboard
curl http://localhost:8001/api/contexts/ctx_123456/dashboard
```

## CLI Usage

Apollo's command-line interface provides quick access to common operations.

### Basic Commands

```bash
# Show Apollo status
./apollo/cli/apollo status

# List active contexts
./apollo/cli/apollo contexts

# Show context details
./apollo/cli/apollo context <context_id>

# List predictions
./apollo/cli/apollo predictions

# List recommended actions
./apollo/cli/apollo actions

# Apply an action
./apollo/cli/apollo action apply <action_id>

# Show system metrics
./apollo/cli/apollo metrics all
```

### Advanced Commands

```bash
# Watch context health in real-time
./apollo/cli/apollo watch context <context_id>

# Export context history to CSV
./apollo/cli/apollo context <context_id> --export csv

# Generate a system health report
./apollo/cli/apollo report

# Configure Apollo settings
./apollo/cli/apollo config set metrics_collection_interval 15

# Run a system test
./apollo/cli/apollo test connection rhetor
```

## Advanced Features

### Real-Time Monitoring

Apollo supports real-time monitoring through WebSockets:

```javascript
// Connect to the WebSocket
const socket = new WebSocket('ws://localhost:8001/ws');

// Subscribe to updates
socket.onopen = function() {
  socket.send(JSON.stringify({
    type: 'subscribe',
    channels: ['contexts', 'predictions', 'actions'],
    filters: {
      component: 'rhetor',
      priority: ['high', 'critical']
    }
  }));
};

// Handle messages
socket.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Received update:', data);
};
```

### Automated Actions

Configure Apollo to automatically apply certain actions:

#### Using the CLI:

```bash
# Enable auto-application for critical actions
./apollo/cli/apollo config set auto_apply_critical true

# Configure auto-application threshold
./apollo/cli/apollo config set auto_apply_threshold 8
```

### Custom Health Metrics

Define custom health metrics for Apollo to monitor:

#### Using the API:

```bash
# Define a custom metric
curl -X POST http://localhost:8001/api/metrics/custom \
  -H "Content-Type: application/json" \
  -d '{
    "name": "semantic_drift",
    "description": "Measures drift from original topic",
    "component": "rhetor",
    "calculation": "external",
    "callback_url": "http://localhost:8005/api/metrics/semantic_drift",
    "health_impact_weight": 0.3
  }'
```

### Action Templates

Create reusable action templates for common situations:

#### Using the API:

```bash
# Create an action template
curl -X POST http://localhost:8001/api/templates/actions \
  -H "Content-Type: application/json" \
  -d '{
    "name": "standard_context_cleanup",
    "description": "Standard context cleanup for high token utilization",
    "action_type": "context_reduction",
    "conditions": {
      "token_utilization": {
        "operator": "gt",
        "value": 0.85
      }
    },
    "parameters": {
      "target_reduction": 0.3,
      "strategy": "summarize_older_content"
    },
    "priority_calculator": "token_utilization * 10"
  }'
```

## Troubleshooting

### Common Issues

#### Apollo not starting

**Symptoms:**
- The `run_apollo.sh` script returns an error
- Apollo is not accessible at `http://localhost:8001`

**Solutions:**
1. Check if another process is using port 8001:
   ```bash
   lsof -i :8001
   ```
2. Verify Python dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```
3. Check log files for errors:
   ```bash
   cat /path/to/logs/apollo.log
   ```

#### Context not showing up

**Symptoms:**
- A context created in Rhetor doesn't appear in Apollo

**Solutions:**
1. Verify Rhetor is correctly configured to report to Apollo
2. Check the connection between Apollo and Rhetor:
   ```bash
   ./apollo/cli/apollo test connection rhetor
   ```
3. Restart the Rhetor metrics subscription:
   ```bash
   ./apollo/cli/apollo restart subscription metrics
   ```

#### Predictions not generating

**Symptoms:**
- No predictions are visible for contexts

**Solutions:**
1. Check if the predictive engine is enabled:
   ```bash
   ./apollo/cli/apollo status
   ```
2. Verify there's enough context history for predictions:
   ```bash
   ./apollo/cli/apollo context <context_id> --history
   ```
3. Manually trigger prediction generation:
   ```bash
   ./apollo/cli/apollo predict <context_id>
   ```

#### Actions not being recommended

**Symptoms:**
- No actions are being generated for problematic contexts

**Solutions:**
1. Check if the action planner is enabled:
   ```bash
   ./apollo/cli/apollo status
   ```
2. Verify action rules are properly configured:
   ```bash
   ./apollo/cli/apollo config get action_rules
   ```
3. Manually trigger action planning:
   ```bash
   ./apollo/cli/apollo plan-actions <context_id>
   ```

#### WebSocket connection issues

**Symptoms:**
- Unable to establish WebSocket connection
- WebSocket disconnects frequently

**Solutions:**
1. Verify Apollo is running and accessible
2. Check network settings and firewall rules
3. Increase WebSocket ping interval:
   ```bash
   ./apollo/cli/apollo config set ws_ping_interval 30
   ```

### Accessing Logs

Apollo logs can be accessed in several ways:

```bash
# View Apollo logs
tail -f /path/to/logs/apollo.log

# Filter logs by component
grep "ContextObserver" /path/to/logs/apollo.log

# Filter logs by severity
grep "ERROR" /path/to/logs/apollo.log
```

### Resetting Apollo

In extreme cases, you may need to reset Apollo:

```bash
# Stop Apollo
./scripts/tekton-kill apollo

# Clear Apollo data (use with caution)
rm -rf ~/.tekton/apollo/*

# Restart Apollo
./run_apollo.sh
```

## Best Practices

### Context Management

1. **Regular Monitoring**: Check context health regularly, especially for long-running sessions
2. **Proactive Action**: Apply recommended actions before context health becomes critical
3. **Context Rotation**: Regularly rotate LLM contexts for long-running operations
4. **Context Optimization**: Structure initial contexts for optimal token usage

### Token Budgeting

1. **Tier Allocation**: Use the appropriate model tier for each task
2. **Priority Assignment**: Assign higher priorities to critical operations
3. **Budget Reviews**: Regularly review token usage and adjust budgets as needed
4. **Pre-allocation**: Allocate tokens before starting resource-intensive operations

### Predictions

1. **Confidence Assessment**: Pay more attention to high-confidence predictions
2. **Trend Analysis**: Look for patterns in predictions over time
3. **Early Intervention**: Act on declining health predictions early
4. **Validation**: Compare predictions with actual outcomes to gauge accuracy

### Actions

1. **Priority Focus**: Focus on high-priority actions first
2. **Context-Specific Actions**: Consider the specific context when applying actions
3. **Action Verification**: Verify the effect of actions after application
4. **Customization**: Create custom action templates for your specific use cases

### General Tips

1. **Regular Updates**: Keep Apollo updated to the latest version
2. **Custom Metrics**: Define custom metrics relevant to your specific use cases
3. **Integration**: Integrate Apollo with your workflow and monitoring systems
4. **Documentation**: Document your Apollo configuration and customizations