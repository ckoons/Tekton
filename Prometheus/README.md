# Prometheus

## Overview

Prometheus is the strategic planning and resource optimization component for the Tekton ecosystem. It analyzes requirements, designs multi-phase execution strategies, allocates resources intelligently, and ensures successful project outcomes through predictive planning and continuous optimization.

## Key Features

- **Strategic Planning**: Creates comprehensive execution strategies from requirements
- **Resource Optimization**: Intelligent allocation of computational and human resources
- **Multi-Phase Execution**: Breaks complex projects into manageable phases
- **Predictive Analysis**: Forecasts potential bottlenecks and risks
- **Component Coordination**: Orchestrates work across Tekton components
- **Progress Monitoring**: Real-time tracking of plan execution
- **Adaptive Replanning**: Adjusts strategies based on actual progress
- **AI-Powered Insights**: Prometheus CI provides strategic recommendations

## Quick Start

```bash
# Install Prometheus
cd Prometheus
pip install -e .

# Start the Prometheus server
python -m prometheus.api.app
# Or use the launch script
./scripts/tekton-launch --components prometheus

# Use the CLI
prometheus plan create --from-requirements
prometheus plan status <plan-id>
prometheus resource allocate
```

## Configuration

### Environment Variables

```bash
# Prometheus-specific settings
PROMETHEUS_PORT=8007                  # API port
PROMETHEUS_AI_PORT=45007              # CI specialist port
PROMETHEUS_PLANNING_INTERVAL=300      # Replanning interval (seconds)
PROMETHEUS_LOOKAHEAD_DAYS=30         # Planning horizon

# Resource settings
PROMETHEUS_MAX_PARALLEL_TASKS=5       # Concurrent task limit
PROMETHEUS_RESOURCE_BUFFER=0.2        # Resource buffer (20%)
PROMETHEUS_OPTIMIZATION_LEVEL=high    # Optimization aggressiveness
```

### Configuration File

Create `.env.prometheus` for persistent settings:

```bash
# Planning strategies
ENABLE_PREDICTIVE_PLANNING=true
ENABLE_RISK_ANALYSIS=true
ENABLE_AUTO_REPLANNING=true

# Resource constraints
MAX_BUDGET_OVERRIDE=false
MAX_TIMELINE_EXTENSION=7  # days
```

## API Reference

### REST API Endpoints

- `POST /api/plans` - Create a new execution plan
- `GET /api/plans` - List all plans
- `GET /api/plans/{id}` - Get plan details
- `PUT /api/plans/{id}` - Update a plan
- `POST /api/plans/{id}/execute` - Begin plan execution
- `GET /api/plans/{id}/progress` - Get execution progress
- `POST /api/resources/allocate` - Allocate resources
- `GET /api/resources/availability` - Check resource availability
- `POST /api/analyze/requirements` - Analyze requirements
- `GET /api/predictions/risks` - Get risk predictions
- `GET /api/status` - Get system status

### WebSocket Endpoints

- `/ws/plans/{id}` - Real-time plan updates
- `/ws/resources` - Resource allocation changes

For detailed API documentation, run the server and visit `/docs`.

## Integration Points

Prometheus seamlessly integrates with:

- **Telos**: Receives requirements for planning
- **Metis**: Coordinates task breakdown and dependencies
- **Apollo**: Monitors execution health and metrics
- **Harmonia**: Orchestrates workflow execution
- **Budget**: Ensures resource constraints are met
- **CI Specialists**: Prometheus CI for strategic insights

### Example Integration

```python
from prometheus.client import PrometheusClient

client = PrometheusClient(host="localhost", port=8007)

# Create plan from requirements
plan = client.create_plan(
    name="Q1 Feature Release",
    requirements_ids=["req-123", "req-124", "req-125"],
    constraints={
        "deadline": "2024-03-31",
        "budget": 50000,
        "team_size": 5
    }
)

# Analyze risks
risks = client.analyze_risks(plan.id)
for risk in risks:
    print(f"Risk: {risk.description} (Impact: {risk.impact})")

# Allocate resources
allocation = client.allocate_resources(
    plan_id=plan.id,
    auto_optimize=True
)

# Monitor progress
progress = client.get_progress(plan.id)
print(f"Overall progress: {progress.percentage}%")
```

## Troubleshooting

### Common Issues

#### 1. Planning Takes Too Long
**Symptoms**: Plan generation exceeds timeout

**Solutions**:
```bash
# Reduce planning complexity
export PROMETHEUS_OPTIMIZATION_LEVEL=medium

# Increase timeout
export PROMETHEUS_PLANNING_TIMEOUT=600

# Check system resources
prometheus debug resources
```

#### 2. Resource Conflicts
**Symptoms**: Unable to allocate required resources

**Solutions**:
```bash
# View resource allocation
prometheus resource list --allocated

# Free up resources
prometheus resource release --plan <plan-id>

# Adjust resource buffer
export PROMETHEUS_RESOURCE_BUFFER=0.1
```

#### 3. Integration Failures
**Symptoms**: Cannot retrieve requirements or tasks

**Solutions**:
```bash
# Test component connections
prometheus integration test all

# Re-register with Hermes
prometheus register

# Check component health
curl http://localhost:8000/api/health
```

### Performance Tuning

- Adjust planning intervals based on project velocity
- Use caching for frequently accessed data
- Enable parallel processing for large plans
- Configure appropriate optimization levels

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=prometheus tests/

# Run specific test category
pytest tests/unit/
pytest tests/integration/
```

### Debug Mode

```bash
# Enable debug logging
export PROMETHEUS_DEBUG=true
export PROMETHEUS_LOG_LEVEL=DEBUG

# Run with verbose output
python -m prometheus.api.app --debug
```

### Planning Algorithm Development

1. Implement new strategies in `prometheus/strategies/`
2. Register strategy in strategy factory
3. Add configuration options
4. Write comprehensive tests
5. Document strategy behavior

## Related Documentation

- [Planning Strategies Guide](/MetaData/ComponentDocumentation/Prometheus/PLANNING_GUIDE.md)
- [Resource Optimization](/MetaData/ComponentDocumentation/Prometheus/RESOURCE_OPTIMIZATION.md)
- [Integration Guide](/MetaData/ComponentDocumentation/Prometheus/INTEGRATION_GUIDE.md)
- [API Reference](/Prometheus/docs/api_reference.md)
