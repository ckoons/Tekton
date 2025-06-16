# Metis - Task Management System for Tekton

![Metis](images/icon.jpg)

Metis is the task management system for the Tekton ecosystem, serving as an intermediary layer between requirements management (Telos) and planning (Prometheus). It provides structured task tracking, dependency management, and real-time updates through a RESTful API with WebSocket support.

## Overview

Metis offers a comprehensive task management solution for software projects within the Tekton ecosystem:

- **Task Management**: Create, update, delete, and track tasks with rich metadata
- **Dependency Tracking**: Define and manage task dependencies with validation
- **Complexity Analysis**: Score and evaluate task complexity to assist planning
- **Real-time Updates**: Subscribe to task changes via WebSocket
- **Integration**: Connect with Telos for requirements and Prometheus for planning
- **Validation**: Ensure data integrity with comprehensive validation

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

## Installation

### Using uv (Recommended)

```bash
cd /path/to/Tekton/Metis
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

### Using pip

```bash
cd /path/to/Tekton/Metis
pip install -e .
```

## Running Metis

```bash
# Run directly
python -m metis

# Or use the launch script
./run_metis.sh
```

## Using with Tekton Launcher

Metis is fully integrated with the Tekton launcher system:

```bash
# From Tekton root directory
./tekton-launch metis
```

## Configuration

Metis uses environment variables for configuration:

- `METIS_PORT`: Port for the Metis service (default: 8011)
- `HERMES_PORT`: Port for the Hermes service (default: 8001)
- `TELOS_PORT`: Port for the Telos service (default: 8008)
- `PROMETHEUS_PORT`: Port for the Prometheus service (default: 8006)
- `METIS_BACKUP_PATH`: Path to save backup data (default: metis_data.json)

## API Endpoints

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

### Telos Integration

- `GET /api/v1/telos/requirements`: Search Telos requirements
- `POST /api/v1/telos/requirements/{requirement_id}/import`: Import requirement as task
- `POST /api/v1/tasks/{task_id}/telos/requirements/{requirement_id}`: Add requirement reference

For a complete API reference, see the [API Reference](docs/api_reference.md) documentation.

## WebSocket Interface

Connect to the WebSocket endpoint at `/ws` to receive real-time task updates:

1. Connect to `ws://localhost:8011/ws`
2. Send a registration message with subscriptions
3. Receive real-time updates for task creation, modification, and deletion

See the [API Reference](docs/api_reference.md) for more details on the WebSocket interface.

## Integration with Tekton

Metis integrates with various Tekton components:

- **Telos**: Import requirements and maintain requirements traceability
- **Prometheus**: Provide task information for planning and scheduling
- **Hermes**: Register services and discover other components
- **Tekton Core**: Integrate with the core orchestration layer

For detailed integration information, see the [Integration Guide](docs/integration_guide.md).

## Development

### Setup Development Environment

```bash
cd /path/to/Tekton/Metis
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

### Project Structure

```
metis/
├── __init__.py
├── setup.py
├── requirements.txt
├── README.md
├── metis/
│   ├── __init__.py
│   ├── config.py             # Configuration management
│   ├── app.py                # Application entry point
│   ├── core/                 # Core functionality
│   │   ├── __init__.py
│   │   ├── models.py         # Data models
│   │   ├── task_manager.py   # Task management
│   │   ├── dependency.py     # Dependency management
│   │   └── complexity.py     # Complexity analysis
│   ├── api/                  # API layer
│   │   ├── __init__.py
│   │   ├── routes.py         # API routes
│   │   ├── schemas.py        # API schemas
│   │   └── controllers.py    # API controllers
│   └── utils/                # Utilities
│       ├── __init__.py
│       ├── validation.py     # Validation utilities
│       └── port_config.py    # Port configuration
└── tests/                    # Tests
    ├── __init__.py
    ├── unit/
    │   ├── test_models.py
    │   └── test_task_manager.py
    └── integration/
        └── test_api.py
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=metis

# Run specific test files
pytest tests/unit/test_models.py
```

### Documentation

- [API Reference](docs/api_reference.md): Detailed API documentation
- [Integration Guide](docs/integration_guide.md): Guide for integrating with Metis

## License

This project is licensed under the terms of the MIT license. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions to Metis are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Run the tests (`pytest`)
5. Commit your changes (`git commit -m 'Add my feature'`)
6. Push to the branch (`git push origin feature/my-feature`)
7. Create a Pull Request