# Metis - Task Management System for Tekton

Metis is the comprehensive task management system for the Tekton ecosystem, serving as an intermediary layer between requirements management (Telos) and planning (Prometheus). It provides structured task tracking, dependency management, and real-time updates through a RESTful API with WebSocket support.

## Overview

Metis offers a comprehensive task management solution for software projects within the Tekton ecosystem:

- **Task Management**: Create, update, delete, and track tasks with rich metadata
- **Dependency Tracking**: Define and manage task dependencies with validation
- **Complexity Analysis**: Score and evaluate task complexity to assist planning
- **Real-time Updates**: Subscribe to task changes via WebSocket
- **Integration**: Connect with Telos for requirements and Prometheus for planning
- **Validation**: Ensure data integrity with comprehensive validation

Metis serves as the central task management hub for the Tekton ecosystem, bridging the gap between requirements and planning while providing a robust platform for tracking and managing work items throughout the development lifecycle.

## Key Features

- **Rich Task Model**: Track title, description, status, priority, dependencies, complexity, subtasks, and more
- **Dependency Management**: Define relationships between tasks with cycle detection and validation
- **Complexity Scoring**: Evaluate task complexity based on customizable factors
- **RESTful API**: Comprehensive API for task and dependency management
- **WebSocket Support**: Real-time updates for task changes
- **Telos Integration**: Import requirements and maintain requirements traceability
- **Hermes Integration**: Service registration and discovery
- **In-Memory and Persistent Storage**: Flexible storage options
- **Comprehensive Validation**: Data integrity enforcement
- **Type Hints and Documentation**: Well-documented code with type annotations

## Architecture

Metis follows Tekton's Single Port Architecture pattern, providing all functionality through a single port with path-based routing:

- **HTTP API**: RESTful endpoints at `/api/v1/...`
- **WebSocket**: Real-time updates at `/ws`
- **Health Check**: Service health information at `/health`

The architecture consists of several key components:

1. **Core Domain Model**: Task, Dependency, Subtask, and ComplexityScore models
2. **Task Manager**: Central business logic for task operations
3. **API Layer**: FastAPI-based RESTful API and WebSocket interface
4. **Storage Layer**: In-memory storage with persistence capabilities
5. **Integration Layer**: Connections to Hermes, Telos, and Prometheus

## Configuration

Metis uses environment variables for configuration:

- `METIS_PORT`: Port for the Metis service (default: 8011)
- `HERMES_PORT`: Port for the Hermes service (default: 8001)
- `TELOS_PORT`: Port for the Telos service (default: 8008)
- `PROMETHEUS_PORT`: Port for the Prometheus service (default: 8006)
- `METIS_BACKUP_PATH`: Path to save backup data (default: metis_data.json)

## API Overview

Metis provides a comprehensive API for task management. Here are some key endpoints:

### Task Management

- `GET /api/v1/tasks`: List tasks with filtering options
- `POST /api/v1/tasks`: Create a new task
- `GET /api/v1/tasks/{task_id}`: Get details of a specific task
- `PUT /api/v1/tasks/{task_id}`: Update a task
- `DELETE /api/v1/tasks/{task_id}`: Delete a task

### Subtask Management

- `POST /api/v1/tasks/{task_id}/subtasks`: Add a subtask
- `PUT /api/v1/tasks/{task_id}/subtasks/{subtask_id}`: Update a subtask
- `DELETE /api/v1/tasks/{task_id}/subtasks/{subtask_id}`: Remove a subtask

### Dependency Management

- `GET /api/v1/dependencies`: List dependencies
- `POST /api/v1/dependencies`: Create a dependency between tasks
- `GET /api/v1/tasks/{task_id}/dependencies`: List dependencies for a task
- `PUT /api/v1/dependencies/{dependency_id}`: Update a dependency
- `DELETE /api/v1/dependencies/{dependency_id}`: Delete a dependency

For a complete API reference, see the [API Reference](./API_REFERENCE.md) documentation.

## Integration with Tekton

Metis integrates with various Tekton components:

- **Telos**: Import requirements and maintain requirements traceability
- **Prometheus**: Provide task information for planning and scheduling
- **Hermes**: Register services and discover other components
- **Tekton Core**: Integrate with the core orchestration layer

For detailed integration information, see the [Integration Guide](./INTEGRATION_GUIDE.md).

## Getting Started

### Installation

Metis can be installed and run using various methods:

```bash
# Using uv (Recommended)
cd /path/to/Tekton/Metis
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# Using Tekton launcher
cd /path/to/Tekton
./tekton-launch metis
```

For detailed installation instructions, see the [Installation Guide](./INSTALLATION_GUIDE.md).

### Basic Usage

1. **Start Metis**: Run the service using the launcher or directly
2. **Create Tasks**: Use the API to create and manage tasks
3. **Track Dependencies**: Define relationships between tasks
4. **Import Requirements**: Import requirements from Telos
5. **Monitor Updates**: Subscribe to WebSocket for real-time updates

For detailed usage instructions, see the [User Guide](./USER_GUIDE.md).

## Documentation

- [INDEX.md](./INDEX.md): Documentation index and overview
- [TECHNICAL_DOCUMENTATION.md](./TECHNICAL_DOCUMENTATION.md): Detailed technical specifications
- [API_REFERENCE.md](./API_REFERENCE.md): Comprehensive API documentation
- [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md): Guide for integrating with Metis
- [USER_GUIDE.md](./USER_GUIDE.md): Guide for using Metis effectively
- [INSTALLATION_GUIDE.md](./INSTALLATION_GUIDE.md): Installation instructions