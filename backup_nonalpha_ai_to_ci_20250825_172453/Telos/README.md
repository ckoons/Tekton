# Telos

## Overview

Telos is the intelligent requirements management and goal-setting system for the Tekton ecosystem. It captures, organizes, validates, and traces project requirements while ensuring alignment with strategic objectives through advanced analysis and bidirectional tracing capabilities.

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

## Quick Start

```bash
# Install Telos
cd Telos
pip install -e .

# Start the Telos server
python -m telos.api.app
# Or use the launch script
./scripts/tekton-launch --components telos

# Use the CLI
telos project create "Q1 Product Release"
telos requirement add "User authentication system"
telos validate --project current
```

## Configuration

### Environment Variables

```bash
# Telos-specific settings
TELOS_PORT=8006                       # API port
TELOS_AI_PORT=45006                   # CI specialist port
TELOS_VALIDATION_LEVEL=strict         # Validation strictness
TELOS_TRACE_DEPTH=5                   # Max tracing depth

# Requirements settings
TELOS_MAX_REQUIREMENT_SIZE=10000      # Max characters
TELOS_AUTO_VALIDATE=true              # Auto-validate on save
TELOS_VERSIONING_ENABLED=true         # Track requirement versions
```

### Configuration File

Create `.env.telos` for persistent settings:

```bash
# Validation rules
REQUIRE_ACCEPTANCE_CRITERIA=true
REQUIRE_PRIORITY=true
REQUIRE_ESTIMATION=false

# Integration settings
AUTO_SYNC_TO_METIS=true
PROMETHEUS_PLANNING_ENABLED=true
```

## API Reference

### REST API Endpoints

#### Project Management
- `POST /api/projects` - Create new project
- `GET /api/projects` - List all projects
- `GET /api/projects/{id}` - Get project details
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project

#### Requirements Management
- `POST /api/projects/{id}/requirements` - Add requirement
- `GET /api/projects/{id}/requirements` - List requirements
- `GET /api/requirements/{id}` - Get requirement details
- `PUT /api/requirements/{id}` - Update requirement
- `DELETE /api/requirements/{id}` - Delete requirement
- `POST /api/requirements/{id}/validate` - Validate requirement

#### Tracing & Analysis
- `GET /api/requirements/{id}/traces` - Get requirement traces
- `POST /api/requirements/{id}/traces` - Add trace
- `GET /api/projects/{id}/impact` - Impact analysis
- `GET /api/projects/{id}/coverage` - Coverage analysis

#### Integration
- `POST /api/prometheus/analyze` - Prometheus planning analysis
- `POST /api/metis/export` - Export to Metis tasks
- `GET /api/validation/report` - Validation report

### WebSocket Endpoints

- `/ws` - Real-time requirement updates
- `/ws/projects/{id}` - Project-specific updates

For detailed API documentation, run the server and visit `/docs`.

## Integration Points

Telos seamlessly integrates with:

- **Prometheus**: Strategic planning based on requirements
- **Metis**: Automatic task generation from requirements
- **Hermes**: Service registration and event distribution
- **Engram**: Requirements history and traceability
- **AI Specialists**: Telos CI for requirement analysis

### Example Integration

```python
from telos.client import TelosClient

client = TelosClient(host="localhost", port=8006)

# Create project with requirements
project = client.create_project(
    name="E-commerce Platform",
    description="Next-gen shopping experience",
    goals=["Increase conversion by 25%", "Reduce cart abandonment"]
)

# Add structured requirement
requirement = client.add_requirement(
    project_id=project.id,
    title="Shopping Cart Persistence",
    description="Cart contents must persist across sessions",
    type="functional",
    priority="high",
    acceptance_criteria=[
        "Cart saved for logged-in users",
        "Cart restored on next login",
        "Cart expires after 30 days"
    ]
)

# Validate requirement
validation = client.validate_requirement(requirement.id)
if not validation.is_valid:
    print(f"Issues: {validation.issues}")

# Trace to another requirement
client.add_trace(
    from_req=requirement.id,
    to_req="req-456",  # User auth requirement
    trace_type="depends_on",
    rationale="Requires user identification"
)

# Export to Metis for implementation
tasks = client.export_to_metis(
    project_id=project.id,
    include_estimates=True
)
```

## Troubleshooting

### Common Issues

#### 1. Validation Failures
**Symptoms**: Requirements marked as invalid

**Solutions**:
```bash
# Check validation rules
telos validation rules --list

# Run detailed validation
telos requirement validate <req-id> --verbose

# Adjust validation level
export TELOS_VALIDATION_LEVEL=moderate
```

#### 2. Circular Dependencies
**Symptoms**: Error when adding requirement traces

**Solutions**:
```bash
# Detect circular dependencies
telos trace analyze --project <project-id>

# Visualize dependency graph
telos viz traces --project <project-id> --output traces.png

# Remove problematic trace
telos trace remove <trace-id>
```

#### 3. Integration Sync Issues
**Symptoms**: Requirements not appearing in Metis/Prometheus

**Solutions**:
```bash
# Check integration status
telos integration status

# Force sync
telos sync --component metis --force

# Verify component registration
curl http://localhost:8000/api/components
```

### Performance Tuning

- Enable caching for large requirement sets
- Use pagination for requirement lists
- Configure appropriate validation levels
- Optimize trace queries with depth limits

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

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=telos tests/

# Run specific test category
pytest tests/unit/
pytest tests/integration/
```

### Debug Mode

```bash
# Enable debug logging
export TELOS_DEBUG=true
export TELOS_LOG_LEVEL=DEBUG

# Run with verbose output
python -m telos.api.app --debug
```

### Requirements Best Practices

1. Use clear, unambiguous language
2. Include measurable acceptance criteria
3. Specify priority and estimation
4. Link related requirements
5. Keep requirements atomic
6. Version significant changes

## Related Documentation

- [Requirements Engineering Guide](/MetaData/ComponentDocumentation/Telos/REQUIREMENTS_GUIDE.md)
- [Tracing and Impact Analysis](/MetaData/ComponentDocumentation/Telos/TRACING_GUIDE.md)
- [Integration Guide](/MetaData/ComponentDocumentation/Telos/INTEGRATION_GUIDE.md)
- [API Reference](/Telos/docs/api_reference.md)
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