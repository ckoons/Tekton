# Budget Component User Guide

The Budget component is a comprehensive solution for managing LLM token budgets and costs. It allows you to set budgets, track usage, and optimize LLM costs across components in the Tekton ecosystem.

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Setting Budgets](#setting-budgets)
4. [Token Allocations](#token-allocations)
5. [Usage Tracking](#usage-tracking)
6. [Budget LLM Assistant](#budget-llm-assistant)
7. [WebSocket Real-time Updates](#websocket-real-time-updates)
8. [CLI Interface](#cli-interface)
9. [API Reference](#api-reference)
10. [Common Workflows](#common-workflows)
11. [Troubleshooting](#troubleshooting)

## Overview

The Budget component provides the following key features:

- **Budget Management**: Create, track, and enforce budgets across different time periods
- **Token Allocation**: Allocate tokens to tasks based on LLM tier and priority
- **Cost Tracking**: Track and analyze costs by provider, model, and component
- **Budget Policies**: Set enforcement policies with flexible thresholds
- **Budget LLM Assistant**: Get AI-powered insights and optimization recommendations
- **Real-time Updates**: Receive WebSocket updates about budget status
- **Model Recommendations**: Get recommendations for the best model for a specific task

The component integrates with other Tekton components using the Single Port Architecture pattern, providing a centralized solution for budgeting and cost management.

## Getting Started

### Installation

The Budget component is installed as part of the Tekton ecosystem. To ensure it's properly set up, run:

```bash
cd /path/to/Tekton
./scripts/tekton-register /Budget
```

### Starting the Budget Service

Start the Budget service using the tekton-launch script:

```bash
./scripts/tekton-launch budget
```

Alternatively, use the CLI directly:

```bash
cd /path/to/Tekton/Budget
python -m budget.cli.main start
```

### Checking Status

Verify that the Budget component is running:

```bash
./scripts/tekton-status budget
```

Or use the Budget CLI:

```bash
python -m budget.cli.main status
```

## Setting Budgets

The Budget component allows you to set and manage budgets for different time periods and scopes.

### Creating a Budget

A budget is a top-level container that can have multiple policies attached to it. To create a budget:

```bash
# Using the CLI
python -m budget.cli.main set_limit daily 10.0 --provider openai --policy-type warn
```

This creates a budget with a $10.00 daily limit for OpenAI models with a "warn" policy.

### Budget Periods

Budget periods define the timeframe for which the budget applies:

- **Hourly**: Budget resets every hour
- **Daily**: Budget resets every day (default)
- **Weekly**: Budget resets every week (starting Monday)
- **Monthly**: Budget resets every calendar month
- **Per Session**: Budget applied to a specific session
- **Per Task**: Budget applied to a specific task

### Budget Policies

Budget policies define how budget limits are enforced:

- **Ignore**: Track usage but don't enforce limits
- **Warn**: Track usage and warn when limits are exceeded
- **Soft Limit**: Recommend cheaper alternatives when limits are approached
- **Hard Limit**: Strictly enforce limits, preventing further usage

Example of setting a hard limit:

```bash
python -m budget.cli.main set_limit daily 20.0 --policy-type hard_limit --provider anthropic
```

## Token Allocations

Token allocations are requests for tokens from a budget for a specific task.

### Creating Allocations

Allocations are typically created by other components through the API, but you can also create them manually using the CLI:

```bash
python -m budget.cli.main allocate create --context-id task-123 --component rhetor --tokens 10000 --tier remote_heavyweight
```

### Managing Allocations

List active allocations:

```bash
python -m budget.cli.main allocate list
```

Release an unused allocation:

```bash
python -m budget.cli.main allocate release ALLOCATION_ID
```

## Usage Tracking

The Budget component tracks token and cost usage across all components.

### Viewing Usage

View usage for a specific period:

```bash
python -m budget.cli.main get_usage daily --days 7
```

Filter by provider or component:

```bash
python -m budget.cli.main get_usage daily --provider openai --component codex
```

### Calculating Costs

Calculate the cost for a specific model and token count:

```bash
python -m budget.cli.main calc_cost --provider openai --model gpt-4 --input-tokens 1000 --output-tokens 500
```

### Viewing Prices

List current prices for models:

```bash
python -m budget.cli.main prices list
```

Update prices from sources:

```bash
python -m budget.cli.main prices update
```

## Budget LLM Assistant

The Budget LLM Assistant provides AI-powered insights and recommendations to help optimize your LLM costs.

### Budget Analysis

Get an analysis of your budget usage patterns:

```bash
curl -X POST http://localhost:8013/api/assistant/analyze \
  -H "Content-Type: application/json" \
  -d '{"period": "daily", "days": 30}'
```

### Cost Optimization

Get recommendations for optimizing costs:

```bash
curl -X POST http://localhost:8013/api/assistant/optimize \
  -H "Content-Type: application/json" \
  -d '{"period": "daily", "days": 30}'
```

### Model Recommendations

Get recommendations for the best model for a specific task:

```bash
curl -X POST http://localhost:8013/api/assistant/recommend-model \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Generate Python code for data processing",
    "input_length": 2000,
    "output_length": 1000,
    "usage_frequency": 25,
    "budget_limit": 10.0,
    "priority_areas": "Code accuracy, error handling"
  }'
```

## WebSocket Real-time Updates

The Budget component provides real-time updates through WebSocket connections.

### Available WebSocket Endpoints

- **/ws/budget/updates**: General budget updates
- **/ws/budget/alerts**: Budget alert notifications
- **/ws/budget/allocations**: Allocation updates
- **/ws/budget/prices**: Price update notifications

### Connecting to WebSocket Updates

Using JavaScript:

```javascript
const socket = new WebSocket('ws://localhost:8013/ws/budget/updates');

socket.onopen = function(event) {
  console.log('Connected to Budget WebSocket');
  
  // Subscribe to a specific topic
  socket.send(JSON.stringify({
    type: 'subscription',
    topic: 'subscription',
    payload: {
      topic: 'budget_events'
    }
  }));
};

socket.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Received update:', data);
};
```

Using Python (example in `/Budget/examples/websocket_client.py`):

```bash
python /path/to/Tekton/Budget/examples/websocket_client.py
```

## CLI Interface

The Budget CLI provides a command-line interface for managing budgets, allocations, and viewing usage.

### Available Commands

```
budget status                   # Show budget status
budget get_usage PERIOD         # Get usage data for a period
budget set_limit PERIOD LIMIT   # Set a budget limit
budget allocate create          # Create a budget allocation
budget allocate list            # List allocations
budget allocate release ID      # Release an allocation
budget prices list              # List model prices
budget prices update            # Update prices
budget recommend                # Get model recommendations
budget calc_cost                # Calculate cost for tokens
budget alerts list              # List budget alerts
budget alerts acknowledge ID    # Acknowledge an alert
```

### Examples

```bash
# Show daily budget status
python -m budget.cli.main status --period daily

# Get weekly usage for OpenAI models
python -m budget.cli.main get_usage weekly --provider openai

# Set a monthly budget limit for Claude models
python -m budget.cli.main set_limit monthly 100.0 --provider anthropic

# List active allocations for a component
python -m budget.cli.main allocate list --component codex

# Get model recommendations
python -m budget.cli.main recommend --task-type code_generation --context-size 2000 --output-size 1000
```

## API Reference

The Budget component provides a comprehensive API for integration with other components.

### Key Endpoints

- **/api/budgets**: Budget management
- **/api/policies**: Budget policies
- **/api/allocations**: Token allocations
- **/api/usage**: Usage tracking
- **/api/prices**: Model pricing
- **/api/alerts**: Budget alerts
- **/api/assistant**: Budget LLM Assistant

For complete API documentation, visit the Swagger UI at `/api/docs` when the Budget component is running.

## Common Workflows

### Setting Up a New Budget

1. Create a budget:
   ```bash
   python -m budget.cli.main set_limit daily 20.0 --policy-type warn
   ```

2. Add more specific policies:
   ```bash
   python -m budget.cli.main set_limit daily 10.0 --provider openai --policy-type hard_limit
   python -m budget.cli.main set_limit daily 5.0 --component codex --policy-type warn
   ```

3. Check the budget status:
   ```bash
   python -m budget.cli.main status
   ```

### Monitoring Usage

1. Check daily usage:
   ```bash
   python -m budget.cli.main get_usage daily
   ```

2. Get a budget analysis:
   ```bash
   curl -X POST http://localhost:8013/api/assistant/analyze \
     -H "Content-Type: application/json" \
     -d '{"period": "daily", "days": 7}'
   ```

3. View active allocations:
   ```bash
   python -m budget.cli.main allocate list
   ```

### Optimizing Costs

1. Get optimization recommendations:
   ```bash
   curl -X POST http://localhost:8013/api/assistant/optimize \
     -H "Content-Type: application/json" \
     -d '{"period": "weekly", "days": 30}'
   ```

2. Update model prices:
   ```bash
   python -m budget.cli.main prices update
   ```

3. Get model recommendations for a specific task:
   ```bash
   python -m budget.cli.main recommend --task-type text_generation --max-cost 5.0
   ```

## Troubleshooting

### Common Issues

#### Budget service not starting

Check if the port is already in use:
```bash
lsof -i :8013
```

Check if there's another instance running:
```bash
ps aux | grep budget
```

#### Unable to connect to the API

Verify the service is running:
```bash
./scripts/tekton-status budget
```

Check if the port is correct in the environment variables:
```bash
echo $BUDGET_PORT
```

#### Errors when setting budgets

Check if you have the correct parameters:
```bash
python -m budget.cli.main set_limit --help
```

#### Missing real-time updates

Ensure the WebSocket connection is established:
```bash
curl -I http://localhost:8013/api/health
```

Try the WebSocket example client:
```bash
python /path/to/Tekton/Budget/examples/websocket_client.py
```

### Getting Help

For more assistance, check the technical documentation or API reference, or file an issue in the Tekton repository.