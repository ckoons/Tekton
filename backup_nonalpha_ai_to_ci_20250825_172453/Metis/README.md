# Metis

## Overview

Metis is the intelligent task management system for the Tekton ecosystem. It bridges requirements (Telos) and strategic planning (Prometheus) by providing structured task tracking, dependency management, complexity analysis, and real-time updates for effective project execution.

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

## Quick Start

```bash
# Install Metis
cd Metis
pip install -e .

# Start the Metis server
python -m metis
# Or use the launch script
./scripts/tekton-launch --components metis

# Use the CLI (if available)
metis task list
metis task create "Implement authentication"
metis dependency add task-1 task-2
```

## Configuration

### Environment Variables

```bash
# Metis-specific settings
METIS_PORT=8010                      # API port
METIS_AI_PORT=45010                  # CI specialist port
METIS_BACKUP_PATH=metis_data.json    # Backup file path
METIS_STORAGE_TYPE=memory            # Storage type (memory/persistent)

# Task settings
METIS_MAX_TASK_DEPTH=5               # Maximum subtask nesting
METIS_DEFAULT_PRIORITY=medium        # Default task priority
METIS_COMPLEXITY_THRESHOLD=high      # Auto-flag complexity threshold
```

### Configuration File

Create `.env.metis` for persistent settings:

```bash
# Task defaults
DEFAULT_TASK_STATUS=pending
ENABLE_AUTO_COMPLEXITY_SCORING=true
ENABLE_DEPENDENCY_VALIDATION=true

# Integration settings
AUTO_SYNC_WITH_TELOS=true
AUTO_UPDATE_PROMETHEUS=true
```

## API Reference

### REST API Endpoints

#### Task Management
- `GET /api/v1/tasks` - List all tasks with filtering
- `POST /api/v1/tasks` - Create a new task
- `GET /api/v1/tasks/{id}` - Get task details
- `PUT /api/v1/tasks/{id}` - Update a task
- `DELETE /api/v1/tasks/{id}` - Delete a task
- `POST /api/v1/tasks/{id}/subtasks` - Add subtask
- `GET /api/v1/tasks/{id}/dependencies` - Get dependencies

#### Dependency Management
- `POST /api/v1/dependencies` - Create dependency
- `DELETE /api/v1/dependencies/{id}` - Remove dependency
- `GET /api/v1/dependencies/validate` - Validate dependencies

#### Analysis & Reports
- `GET /api/v1/tasks/{id}/complexity` - Get complexity score
- `GET /api/v1/reports/progress` - Progress report
- `GET /api/v1/reports/dependencies` - Dependency graph

### WebSocket Endpoints

- `/ws` - Real-time task updates
- `/ws/tasks/{id}` - Updates for specific task

For detailed API documentation, run the server and visit `/docs`.

## Integration Points

Metis seamlessly integrates with:

- **Telos**: Imports requirements and maintains traceability
- **Prometheus**: Provides task data for strategic planning
- **Hermes**: Service registration and event distribution
- **Harmonia**: Task execution in workflows
- **AI Specialists**: Metis CI for intelligent task analysis

### Example Integration

```python
from metis.client import MetisClient

client = MetisClient(host="localhost", port=8010)

# Create task from requirement
task = client.create_task(
    title="Implement OAuth2 authentication",
    description="Add OAuth2 support for Google and GitHub",
    priority="high",
    complexity="medium",
    telos_requirement_id="req-123",
    estimated_hours=16
)

# Add dependencies
client.add_dependency(
    from_task=task.id,
    to_task="task-456",  # Depends on API framework task
    dependency_type="blocks"
)

# Get complexity analysis
complexity = client.analyze_complexity(task.id)
print(f"Complexity score: {complexity.score}")
print(f"Risk factors: {complexity.risk_factors}")
```

## Troubleshooting

### Common Issues

#### 1. Task Dependency Cycles
**Symptoms**: Error when adding dependencies

**Solutions**:
```bash
# Validate dependency graph
curl http://localhost:8010/api/v1/dependencies/validate

# Visualize dependencies
metis dependency graph --output graph.png

# Remove problematic dependency
metis dependency remove <dependency-id>
```

#### 2. Sync Issues with Telos
**Symptoms**: Requirements not appearing as tasks

**Solutions**:
```bash
# Check Telos connection
metis integration test telos

# Force sync
metis sync telos --force

# Check sync status
metis sync status
```

#### 3. Performance with Large Task Lists
**Symptoms**: Slow response times

**Solutions**:
```bash
# Enable pagination
export METIS_DEFAULT_PAGE_SIZE=50

# Switch to persistent storage
export METIS_STORAGE_TYPE=persistent

# Optimize queries
metis optimize
```

### Performance Tuning

- Use persistent storage for large projects
- Enable caching for complex dependency graphs
- Configure appropriate page sizes
- Use task filters to reduce data transfer

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=metis tests/

# Run specific test category
pytest tests/unit/
pytest tests/integration/
```

### Debug Mode

```bash
# Enable debug logging
export METIS_DEBUG=true
export METIS_LOG_LEVEL=DEBUG

# Run with verbose output
python -m metis --debug
```

### Task Management Best Practices

1. Break down large tasks into subtasks
2. Set realistic complexity estimates
3. Define clear dependencies upfront
4. Use consistent priority levels
5. Keep task descriptions detailed

## Related Documentation

- [Task Management Guide](/MetaData/ComponentDocumentation/Metis/TASK_GUIDE.md)
- [Dependency Management](/MetaData/ComponentDocumentation/Metis/DEPENDENCIES.md)
- [Integration Guide](/MetaData/ComponentDocumentation/Metis/INTEGRATION_GUIDE.md)
- [API Reference](/Metis/docs/api_reference.md)