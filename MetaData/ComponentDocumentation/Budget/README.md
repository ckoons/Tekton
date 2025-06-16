# Budget Component

## Overview

The Budget component provides comprehensive token and cost management for LLM usage across the Tekton ecosystem. It enables users to set budgets, track usage patterns, analyze costs, and optimize their usage of LLM resources.

## Features

### Core Features

- **Budget Management**: Create and manage budgets with time-based periods and limits
- **Token Allocation**: Request and allocate tokens from available budgets
- **Usage Tracking**: Record and analyze token usage and costs
- **Price Monitoring**: Keep track of current LLM provider pricing
- **Budget Enforcement**: Enforce budget limits with configurable policies
- **Budget Analytics**: Generate insights and recommendations for optimization

### UI Features

- **Dashboard**: Visual overview of current budget status, spending patterns, and usage
- **Usage Details**: Detailed records of token usage and costs
- **Settings Management**: Configure budget limits, provider settings, and policies
- **Alert System**: View and manage budget alerts
- **CLI Interface**: Command-line style interface for budget operations
- **Budget Chat**: LLM-assisted budget analysis and optimization recommendations
- **Team Chat**: Collaboration on budget matters

## Architecture

The Budget component consists of two main parts:

1. **Backend Service**: Python-based REST API service providing the core budget functionality
2. **UI Component**: JavaScript-based UI component integrated with the Hephaestus framework

The components communicate via:
- REST API calls for data operations
- WebSocket connections for real-time updates
- MCP Protocol for multi-component communication

## Getting Started

### Starting the Component

```bash
# Start the Budget backend service
./scripts/tekton-launch budget

# The UI component is automatically loaded as part of the Hephaestus UI
./scripts/tekton-launch hephaestus
```

### Accessing the UI

1. Navigate to the Hephaestus UI (http://localhost:8080 by default)
2. Select the Budget component from the navigation menu
3. The Budget dashboard will be displayed showing current budget status

### Basic Usage

- **View Budget Status**: The Dashboard tab shows current spending and limits
- **Track Usage**: The Usage Details tab shows detailed records of token usage
- **Configure Budgets**: The Settings tab allows setting budget limits and policies
- **Manage Alerts**: The Alerts tab shows budget notifications and warnings
- **Get Assistance**: The Budget Chat tab provides AI-powered budget analysis

## Integration Points

- **Apollo**: Integration for token budget management
- **Rhetor**: Integration for prompt optimization
- **Engram**: Integration for context memory management
- **Hermes**: Service registration and discovery
- **LLM Adapter**: Provider and model integration

## Documentation

For more detailed information, see:

- [User Guide](./USER_GUIDE.md): Complete guide for Budget component users
- [Technical Documentation](./TECHNICAL_DOCUMENTATION.md): Architecture and technical details
- [API Reference](./API_REFERENCE.md): Comprehensive API documentation
- [Integration Guide](./INTEGRATION_GUIDE.md): Guide for integrating with other components

## Repository Structure

```
/Budget/
├── README.md                  # Component overview
├── budget/                    # Backend service implementation
│   ├── __init__.py
│   ├── api/                   # API endpoints and models
│   ├── core/                  # Core budget functionality
│   ├── data/                  # Data models and repositories
│   └── service/               # Additional services
└── ui/components/budget/      # UI component implementation
    ├── budget-component.html  # Component HTML template
    └── scripts/               # JavaScript implementation
        ├── budget-api-client.js      # API communication
        ├── budget-chart-utils.js     # Chart visualization
        ├── budget-cli-handler.js     # CLI command handling
        ├── budget-component.js       # Main component logic
        ├── budget-models.js          # Data models
        ├── budget-state-manager.js   # State management
        └── budget-ws-handler.js      # WebSocket handling
```