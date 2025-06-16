# Metis Backend API Implementation - Claude Code Prompt

## Context

You are Working Claude, tasked with implementing the backend API for the Metis component for the Tekton ecosystem. Metis is a Python-based task management system inspired by Claude Task Master that serves as an intermediary layer between requirements management (Telos) and planning (Prometheus).

This implementation follows the updated implementation plan that builds upon the successful patterns from the Clean Slate Sprint methodology while adapting the task management capabilities of the Claude Task Master project to Python.

**Important Note**: This sprint focuses ONLY on the backend API implementation. The UI component will be developed in a separate sprint following the Clean Slate UI patterns.

## Sprint Documentation

Before beginning implementation, please review these documents:

1. [Updated Implementation Plan](./Updated_Implementation_Plan.md): Detailed implementation tasks, phasing, and requirements
2. [Architectural Decisions](./ArchitecturalDecisions.md): Key architectural decisions and their rationale
3. [Task Structure](../claude-task-master/docs/task-structure.md): Reference for task structure from Claude Task Master

## Environment Setup

For this implementation, we'll use the existing Clean Slate branch:

```bash
# Start by changing to the Tekton directory
cd Tekton

# Verify and checkout the Clean Slate branch
git checkout sprint/Clean_Slate_051125
git status
```

This approach ensures we're working with the stable Clean Slate implementation as our foundation. Since you'll be the only Claude Code session working on the Tekton project, using this existing branch simplifies the workflow and ensures consistency.

## Implementation Approach

### Phase 1: Core Implementation

1. **Project Structure Setup**
   - Create the initial project structure for Metis following Tekton standards
   - Implement `setup.py`, `requirements.txt`, and configuration management
   - Set up a clear README with component overview
   - Use the Tekton port configuration standard (port 8011)

2. **Core Data Models**
   - Implement task model with all required attributes (ID, title, description, status, priority, dependencies, complexity, etc.)
   - Create dependency model for representing task relationships
   - Implement complexity model for scoring task complexity
   - Ensure proper validation and serialization

3. **Task Management Service**
   - Implement CRUD operations for tasks
   - Create dependency management functions
   - Implement status transitions and validation
   - Add task querying and filtering capabilities

4. **API Layer**
   - Implement FastAPI-based Single Port Architecture
   - Create RESTful endpoints for task management
   - Implement WebSocket support for real-time updates
   - Add proper error handling and validation
   - Document API with OpenAPI

5. **Hermes Integration**
   - Implement service registration with Hermes
   - Add health reporting
   - Configure capability announcement

### Development Standards

- Follow Python best practices (PEP 8) for code style
- Write comprehensive docstrings for all classes and functions
- Create type hints for all function signatures
- Create unit tests for all functionality with pytest
- Validate all inputs to ensure data integrity
- Follow Tekton's Single Port Architecture pattern
- Use Tekton's standard logging patterns

### Code Organization

Follow this structure for organizing the codebase:

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

## Key Implementation Details

### Data Models

The Task model should include:

```python
class Task:
    id: str
    title: str
    description: str
    status: TaskStatus  # Enum: pending, in_progress, review, done
    priority: Priority  # Enum: high, medium, low
    dependencies: List[str]  # List of task IDs
    complexity: Optional[ComplexityScore]
    details: str  # Implementation details
    test_strategy: Optional[str]
    subtasks: List[Subtask]
    created_at: datetime
    updated_at: datetime
    requirement_refs: List[RequirementRef]  # References to Telos requirements
```

### API Implementation

Implement these API endpoints:

- `GET /api/v1/tasks`: List tasks with filtering options
- `POST /api/v1/tasks`: Create a new task
- `GET /api/v1/tasks/{task_id}`: Get details of a specific task
- `PUT /api/v1/tasks/{task_id}`: Update a task
- `DELETE /api/v1/tasks/{task_id}`: Delete a task
- `GET /api/v1/tasks/{task_id}/dependencies`: List dependencies of a task
- `POST /api/v1/tasks/{task_id}/dependencies`: Add a dependency to a task
- `DELETE /api/v1/tasks/{task_id}/dependencies/{dependency_id}`: Remove a dependency

### WebSocket Interface

Implement WebSocket support using FastAPI's WebSocket functionality:

- Connect to the WebSocket endpoint at `/ws`
- Subscribe to task updates with a registration message
- Receive real-time updates for task creation, modification, and deletion
- Send updates when task status changes

### Hermes Integration

Implement Hermes integration for service registration:

- Register the Metis component with Hermes at startup
- Provide health status reporting
- Announce capabilities for service discovery
- Discover other components (Telos, Prometheus) through Hermes

## Testing Strategy

Create comprehensive tests for all functionality:

- Unit tests for data models and validation
- Unit tests for task management functions
- Integration tests for API endpoints
- Integration tests for WebSocket functionality
- Tests for Hermes integration

Use pytest as the testing framework and aim for high test coverage.

## Deployment Considerations

Ensure the component can be deployed in the following ways:

- Standalone service with its own entry point
- Part of the Tekton ecosystem with the `tekton-launch` script
- Containerized deployment with Docker

## Documentation Requirements

Create comprehensive documentation:

- README.md with component overview and installation instructions
- API reference documentation with endpoint descriptions and examples
- Data model documentation with field descriptions
- Integration guide for other components

## Initial Implementation Tasks

Begin with these specific implementation tasks:

1. Set up the project structure and base dependencies
2. Implement the core data models for tasks and dependencies
3. Create the task management service with basic CRUD operations
4. Implement the API layer with FastAPI
5. Add Hermes integration for service registration

## Next Steps

After completing Phase 1, you'll move on to Phase 2, which focuses on Telos integration and PRD parsing capabilities. The detailed tasks for Phase 2 are outlined in the Updated Implementation Plan.

## Questions

If you have any questions or encounter any issues during implementation, please ask before proceeding. It's important to maintain alignment with Tekton's architecture and standards throughout the sprint.

## Let's Get Started

Using the information provided, please begin implementing the Metis component for Tekton, starting with Phase 1 as outlined in the Updated Implementation Plan.
