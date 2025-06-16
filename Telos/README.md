# Telos

## Overview

Telos is the comprehensive requirements management and tracing system for the Tekton ecosystem. It provides a robust platform for documenting, organizing, tracking, and validating project requirements with support for hierarchical visualization and bidirectional tracing.

## Key Features

- **Requirements Management**: Create, update, organize, and track project requirements
- **Hierarchical Requirements**: Support for parent-child relationships and dependencies
- **Requirement Tracing**: Bidirectional tracing between requirements for impact analysis
- **Requirement Validation**: Automated quality checking for requirements (completeness, clarity, verifiability)
- **Prometheus Integration**: Advanced planning capabilities for requirements
- **Single Port Architecture**: Consolidated HTTP, WebSocket, and Event communication
- **Real-time Updates**: WebSocket-based updates for collaborative requirement editing
- **Shadow DOM Component**: Seamless UI integration with Hephaestus
- **CLI Interface**: Comprehensive command-line tools for requirement management
- **REST API**: Full-featured API for programmatic integration

## Architecture

Telos follows the Tekton Single Port Architecture pattern:

- **Port 8008**: All Telos communications (HTTP, WebSocket, Events)
- **Path-based Routing**:
  - `/api/*`: RESTful API endpoints
  - `/ws`: WebSocket endpoint for real-time updates
  - `/events`: Server-Sent Events for notifications

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/example/tekton.git
cd tekton/Telos

# Install Telos and its dependencies
pip install -e .
```

### With Tekton Installer

```bash
# Run the Tekton installer
./tekton-install.sh --components telos
```

## Quick Start

```bash
# Register with Hermes
python -m Telos/register_with_hermes.py

# Start the Telos API server
telos-api

# Start with Tekton (alternative)
./scripts/tekton-launch --components telos
```

## Usage Examples

### CLI Usage

```bash
# Create a new project
telos project create --name "My Project" --description "Project description"

# Add a requirement
telos requirement add --project-id my-project-id --title "User Authentication" --description "The system must authenticate users with username and password"

# List all requirements
telos requirement list --project-id my-project-id

# Visualize requirements
telos viz requirements --project-id my-project-id --output requirements.png

# Analyze for planning
telos refine analyze --project-id my-project-id
```

### API Usage

```python
import requests

# Base URL
base_url = "http://localhost:8008"

# Create a project
response = requests.post(f"{base_url}/api/projects", json={
    "name": "API Project",
    "description": "Created via API"
})
project_id = response.json()["project_id"]

# Add a requirement
response = requests.post(f"{base_url}/api/projects/{project_id}/requirements", json={
    "title": "API Feature",
    "description": "This requirement was created via the API",
    "requirement_type": "functional",
    "priority": "high"
})
```

### WebSocket Connection

```javascript
// Connect to WebSocket
const ws = new WebSocket("ws://localhost:8008/ws");

// Listen for messages
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log("Received:", data);
};

// Register client
ws.send(JSON.stringify({
    type: "REGISTER",
    source: "client",
    target: "server",
    timestamp: Date.now(),
    payload: {}
}));

// Subscribe to project updates
ws.send(JSON.stringify({
    type: "PROJECT_SUBSCRIBE",
    source: "client",
    target: "server",
    timestamp: Date.now(),
    payload: {
        project_id: "your-project-id"
    }
}));
```

## UI Integration

Telos provides a web component that can be integrated into any Tekton UI:

```html
<!-- Include the Telos component -->
<script src="telos-component.js"></script>

<!-- Use the component -->
<telos-requirements project-id="my-project"></telos-requirements>
```

## Component Integration

Telos integrates with other Tekton components:

- **Hermes**: Service registration and discovery
- **Prometheus**: Planning and task breakdown
- **Ergon**: Memory integration
- **Rhetor**: Natural language processing for requirements refinement

## Documentation

For detailed documentation, see the following resources:

- [API Reference](../docs/telos_api_reference.md) - Complete API documentation
- [Component Summaries](../MetaData/ComponentSummaries.md) - Overview of all Tekton components
- [Tekton Architecture](../MetaData/TektonArchitecture.md) - Overall system architecture
- [Component Integration](../MetaData/ComponentIntegration.md) - How components interact
- [CLI Operations](../MetaData/CLI_Operations.md) - Command-line operations