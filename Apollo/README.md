# Apollo

## Overview

Apollo is the executive coordinator and predictive planning system for the Tekton ecosystem. It monitors operational health, manages token budgets, and ensures behavioral reliability of all LLM components through predictive analytics and intelligent resource allocation.

## Key Features

- **Context Monitoring**: Track and analyze context usage metrics from Rhetor
- **Token Budgeting**: Allocate and manage token budgets for different LLM operations
- **Predictive Planning**: Anticipate context issues before they occur
- **Protocol Enforcement**: Define and enforce standards for component interactions
- **Bidirectional Messaging**: Enable flexible communication between components
- **CLI Management**: Command-line tools for system monitoring and control
- **CI Registry Integration**: Monitor all CI exchanges for performance and stress indicators
- **Context Staging**: Prepare optimized contexts for Rhetor to inject

## Quick Start

```bash
# Install Apollo
cd Apollo
pip install -e .

# Start the Apollo server
python -m apollo.api.app
# Or use the launch script
./scripts/tekton-launch --components apollo

# Use the CLI
apollo status
apollo contexts
apollo metrics all
```

## Configuration

### Environment Variables

```bash
# Apollo-specific settings
APOLLO_PORT=8012              # API port
APOLLO_AI_PORT=45012          # AI specialist port
APOLLO_PREDICTION_INTERVAL=60 # Prediction cycle (seconds)
APOLLO_ACTION_INTERVAL=10     # Action planning cycle (seconds)

# Token budget defaults
APOLLO_DEFAULT_BUDGET_PERIOD=DAILY
APOLLO_DEFAULT_BUDGET_POLICY=WARN
```

### Configuration File

Create `.env.apollo` for persistent settings:

```bash
# Model tier budgets (tokens)
LOCAL_LIGHTWEIGHT_BUDGET=100000
LOCAL_MIDWEIGHT_BUDGET=50000
REMOTE_HEAVYWEIGHT_BUDGET=10000
```

## API Reference

### REST API Endpoints

- `GET /api/contexts` - List all active contexts with metrics
- `GET /api/contexts/{context_id}` - Get detailed context information
- `GET /api/predictions` - Get context usage predictions
- `GET /api/actions` - Get recommended optimization actions
- `POST /api/budget/allocate` - Allocate token budget to operations
- `GET /api/protocols` - List enforced communication protocols
- `GET /api/status` - Get Apollo system status
- `GET /metrics/health` - Health check endpoint

### WebSocket Endpoints

- `/ws` - Real-time metric updates and alerts
- `/ws/events` - Event stream for context changes

For detailed API documentation, see [API Reference](docs/api_reference.md).

## Integration Points

Apollo seamlessly integrates with other Tekton components:

- **Rhetor**: Monitors LLM operations and context usage metrics
- **Hermes**: Distributes alerts and coordinates responses
- **Engram**: Stores historical metrics for trend analysis
- **Budget**: Coordinates token allocation across components
- **AI Specialists**: Apollo AI provides predictive insights

### Example Integration

```python
from apollo.client import ApolloClient

client = ApolloClient(host="localhost", port=8012)

# Monitor context usage
context = client.create_context("chat_session")
metrics = client.get_context_metrics(context.id)

# Get predictions
predictions = client.get_predictions(context.id)
if predictions.risk_level == "high":
    actions = client.get_recommended_actions(context.id)
```

## Troubleshooting

### Common Issues

#### 1. High Context Usage Warnings
**Symptoms**: Frequent warnings about context exhaustion

**Solutions**:
```bash
# Check current usage
apollo metrics context

# Adjust prediction sensitivity
export APOLLO_PREDICTION_THRESHOLD=0.8

# Increase budget temporarily
apollo budget increase --tier LOCAL_MIDWEIGHT --amount 10000
```

#### 2. Apollo Not Starting
**Symptoms**: Service fails to start or port conflicts

**Solutions**:
```bash
# Check port availability
lsof -i :8012

# Check logs
tail -f logs/apollo.log

# Start with debug mode
python -m apollo.api.app --debug
```

#### 3. Missing Metrics
**Symptoms**: No data from Rhetor or other components

**Solutions**:
```bash
# Verify Hermes connection
curl http://localhost:8000/api/health

# Check component registration
apollo status --verbose

# Re-register with Hermes
apollo register
```

### Performance Tuning

- Adjust prediction intervals based on load
- Configure appropriate budget policies
- Use caching for frequently accessed metrics
- Enable batch processing for actions

## Development

```
Apollo/
├── apollo/
│   ├── __init__.py
│   ├── api/
│   │   ├── app.py            # FastAPI application
│   │   ├── models.py         # API data models
│   │   └── routes.py         # API route definitions
│   ├── cli/
│   │   ├── __init__.py
│   │   └── main.py           # CLI implementation
│   ├── core/
│   │   ├── action_planner.py         # Action planning
│   │   ├── apollo_manager.py         # Component coordination
│   │   ├── context_observer.py       # Context monitoring
│   │   ├── interfaces/
│   │   │   └── rhetor.py             # Rhetor integration
│   │   ├── message_handler.py        # Message management
│   │   ├── predictive_engine.py      # Prediction system
│   │   ├── protocol_enforcer.py      # Protocol enforcement
│   │   └── token_budget.py           # Budget management
│   ├── models/
│   │   ├── budget.py         # Budget models
│   │   ├── context.py        # Context models
│   │   ├── message.py        # Message models
│   │   └── protocol.py       # Protocol models
│   └── utils/
│       └── port_config.py    # Port configuration utilities
├── docs/
│   └── api_reference.md      # API documentation
├── tests/
│   ├── conftest.py           # Test configuration
│   ├── integration/          # Integration tests
│   └── unit/                 # Unit tests
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── run_apollo.sh             # Startup script
└── setup.sh                  # Setup script
```

### Running Tests

Run the test suite with pytest:

```bash
cd Apollo
python -m pytest
```

## Monitoring and Management

Apollo provides several interfaces for monitoring and management:

1. **Web Dashboard**: Access the Swagger UI at `/docs` for API exploration
2. **CLI Tools**: Use the Apollo CLI for quick status checks and commands
3. **API Endpoints**: Programmatically interact with Apollo's functionality
4. **WebSocket**: Subscribe to real-time updates at `/ws`

## Protocol Definition

Apollo enforces several communication protocols, which can be extended or modified as needed:

1. **Message Format**: Defines required fields and structure for messages
2. **Request Flow**: Ensures proper request sequencing and validation
3. **Response Format**: Standardizes response structures
4. **Event Sequencing**: Enforces proper event ordering

Protocols can be managed through the `/api/protocols` endpoints.

## Token Budgeting

Apollo manages token budgets across three tiers of model capabilities:

1. **LOCAL_LIGHTWEIGHT**: For simple operations (e.g., CodeLlama, Deepseek Coder)
2. **LOCAL_MIDWEIGHT**: For moderate complexity (e.g., Claude Haiku, Qwen)
3. **REMOTE_HEAVYWEIGHT**: For complex reasoning (e.g., Claude 3.7 Sonnet, GPT-4)

Budget policies can be configured with different enforcement levels (IGNORE, WARN, SOFT_LIMIT, HARD_LIMIT) and periods (HOURLY, DAILY, WEEKLY, MONTHLY).

## Performance Considerations

- Apollo is designed to run continuously, monitoring all active contexts
- The prediction engine operates on a configurable interval (default: 60 seconds)
- Action planning occurs on a separate interval (default: 10 seconds)
- Message handling uses batching for efficiency
- Protocol enforcement has minimal performance impact by default

## Contributing

Contributions to Apollo follow the standard Tekton development process:

1. Follow the coding standards in `CLAUDE.md`
2. Add comprehensive docstrings to all new code
3. Write unit tests for all new functionality
4. Update documentation to reflect changes
5. Submit pull requests with clear descriptions

## License

Apollo is part of the Tekton project and is subject to the same licensing terms.

---

*Apollo: Foresight and coordination for intelligent systems.*