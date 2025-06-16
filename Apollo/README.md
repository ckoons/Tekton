# Apollo

Apollo is the executive coordinator and predictive planning system responsible for managing operational health, token flow, and behavioral reliability of all LLM components in Tekton. It serves as the guardian-advisor, orchestrating context management and protocol enforcement through active collaboration with **Rhetor**, **Engram**, and **Synthesis**.

![Apollo Icon](../images/icon.jpg)

## Key Features

- **Context Monitoring**: Track and analyze context usage metrics from Rhetor
- **Token Budgeting**: Allocate and manage token budgets for different LLM operations
- **Predictive Planning**: Anticipate context issues before they occur
- **Protocol Enforcement**: Define and enforce standards for component interactions
- **Bidirectional Messaging**: Enable flexible communication between components
- **CLI Management**: Command-line tools for system monitoring and control

## Quick Start

```bash
# Install dependencies and set up Apollo
./setup.sh

# Start the Apollo server
./run_apollo.sh

# Use the CLI for status monitoring
./apollo/cli/apollo status
```

## Architecture

Apollo follows the modular observer-controller architecture, with the following core components:

### Context Observer

Monitors LLM context usage metrics from Rhetor, tracking token consumption rates and identifying patterns that might indicate performance issues or context degradation.

### Predictive Engine

Analyzes context metrics history to predict future states and identify potential issues before they occur, using a combination of heuristic rules and statistical models.

### Action Planner

Determines appropriate corrective actions based on current states and predictions, generating prioritized action plans for component interventions.

### Protocol Enforcer

Enforces communication protocols between components, validating messages against defined standards and ensuring consistent interactions.

### Token Budget Manager

Manages token budget allocation and enforcement across different model capabilities, ensuring efficient resource utilization.

### Message Handler

Provides messaging functionality for Apollo, including sending and receiving messages, managing subscriptions, and integrating with Hermes.

### Apollo Manager

High-level manager that coordinates all Apollo components, providing a simplified interface for the API layer.

## Integration Points

Apollo integrates with the following Tekton components:

- **Rhetor**: For monitoring LLM operations and context metrics
- **Hermes**: For message distribution across components
- **Engram**: For persistent context memory and analysis
- **Synthesis**: For action execution coordination

## Using the Apollo CLI

Apollo includes a command-line interface for interacting with its functionality:

```bash
# Check Apollo status
./apollo/cli/apollo status

# List active contexts
./apollo/cli/apollo contexts

# Get details for a specific context
./apollo/cli/apollo context <context-id> --dashboard

# View recommended actions
./apollo/cli/apollo actions

# View system metrics
./apollo/cli/apollo metrics all
```

## API Reference

Apollo implements the Single Port Architecture pattern with path-based routing for all operations. See the [API Reference](docs/api_reference.md) for detailed documentation.

### Key Endpoints

- `GET /api/contexts`: Get all active contexts
- `GET /api/predictions`: Get context predictions
- `GET /api/actions`: Get recommended actions
- `POST /api/budget/allocate`: Allocate token budget
- `GET /api/protocols`: Get protocol definitions
- `GET /api/status`: Get system status
- `GET /metrics/health`: Get health metrics

## Development

### Project Structure

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