# Budget

## Overview

Budget is the centralized cost and resource management component for the Tekton ecosystem. It tracks LLM token usage, manages allocations, enforces budget policies, and provides cost optimization insights across all components.

## Key Features

- **Token Tracking**: Real-time monitoring of token consumption across all LLM providers
- **Cost Management**: Automated price tracking and cost calculation
- **Budget Enforcement**: Flexible policies (IGNORE, WARN, SOFT_LIMIT, HARD_LIMIT)
- **Usage Analytics**: Detailed reporting with visualization support
- **CI Optimization**: Budget CI specialist for intelligent resource allocation
- **Multi-Provider Support**: Works with OpenAI, Anthropic, Ollama, and more
- **MCP Integration**: Standard protocol support for seamless component integration

## Quick Start

```bash
# Install Budget
cd Budget
pip install -e .

# Start the Budget server
python -m budget.api.app
# Or use the launch script
./scripts/tekton-launch --components budget

# Use the CLI
budget status
budget set-limit daily 10.0
budget get-usage --format json
```

## Configuration

### Environment Variables

```bash
# Budget-specific settings
BUDGET_PORT=8013                    # API port
BUDGET_AI_PORT=45013                # CI specialist port
BUDGET_DEFAULT_CURRENCY=USD         # Default currency
BUDGET_ENFORCEMENT_LEVEL=WARN       # Default enforcement

# Provider settings
BUDGET_UPDATE_PRICES_ON_START=true  # Auto-update pricing
BUDGET_PRICE_UPDATE_INTERVAL=3600   # Update interval (seconds)
```

### Configuration File

Create `.env.budget` for persistent settings:

```bash
# Budget limits (per period)
DAILY_BUDGET_LIMIT=50.0
WEEKLY_BUDGET_LIMIT=300.0
MONTHLY_BUDGET_LIMIT=1000.0

# Component allocations (percentage)
RHETOR_ALLOCATION=30
CODEX_ALLOCATION=25
ERGON_ALLOCATION=20
OTHER_ALLOCATION=25
```

## API Reference

### REST API Endpoints

- `POST /api/check` - Check if request is within budget
- `POST /api/record` - Record token usage
- `GET /api/usage/{period}` - Get usage for period
- `GET /api/reports/summary` - Get usage summary
- `POST /api/limits` - Set budget limits
- `GET /api/providers/prices` - Get current pricing
- `POST /api/optimize` - Get optimization suggestions
- `GET /api/status` - Get system status

### WebSocket Endpoints

- `/ws` - Real-time usage updates
- `/ws/alerts` - Budget alert notifications

For detailed API documentation, run the server and visit `/docs`.

## Integration Points

Budget integrates seamlessly with:

- **Rhetor**: Tracks LLM usage for all prompt operations
- **Apollo**: Provides token allocation for predictive planning
- **Ergon**: Monitors agent execution costs
- **Hermes**: Publishes budget events and alerts
- **CI Specialists**: Budget CI provides optimization insights

### Example Integration

```python
from budget.client import BudgetClient

client = BudgetClient(host="localhost", port=8013)

# Check budget before LLM call
allowed, info = client.check_budget(
    provider="anthropic",
    model="claude-3-sonnet",
    estimated_tokens=1000,
    component="rhetor"
)

if allowed:
    # Make LLM call
    response = llm.complete(prompt)
    
    # Record actual usage
    client.record_usage(
        provider="anthropic",
        model="claude-3-sonnet",
        input_tokens=response.input_tokens,
        output_tokens=response.output_tokens,
        component="rhetor"
    )
else:
    print(f"Budget exceeded: {info['reason']}")
```

## Troubleshooting

### Common Issues

#### 1. Budget Limits Not Enforcing
**Symptoms**: Requests continue despite exceeding limits

**Solutions**:
```bash
# Check enforcement level
budget config get enforcement_level

# Set to strict enforcement
budget config set enforcement_level HARD_LIMIT

# Verify limits are set
budget limits list
```

#### 2. Missing Usage Data
**Symptoms**: Reports show zero usage despite activity

**Solutions**:
```bash
# Check component integration
budget debug integrations

# Verify database connection
budget db check

# Force usage recalculation
budget recalculate --period daily
```

#### 3. Incorrect Pricing
**Symptoms**: Cost calculations don't match provider pricing

**Solutions**:
```bash
# Update provider prices
budget prices update --all

# View current prices
budget prices list

# Set custom pricing
budget prices set anthropic claude-3-opus --input 0.015 --output 0.075
```

### Performance Tuning

- Enable caching for frequent budget checks
- Use batch recording for high-volume operations  
- Configure appropriate aggregation intervals
- Set up database indexing for large datasets

### CLI Usage

```bash
# Set a budget limit
budget set-limit daily 10.0

# Check current usage
budget get-usage daily

# View budget status
budget status
```

### API Usage

```python
from budget.client import BudgetClient

# Create client
client = BudgetClient()

# Check if a request is within budget
allowed, info = client.check_budget(
    provider="anthropic",
    model="claude-3-opus",
    input_text="Hello, world!",
    component="my-component"
)

# Record usage
client.record_completion(
    provider="anthropic",
    model="claude-3-opus",
    input_text="Hello, world!",
    output_text="Hi there! How can I assist you today?",
    component="my-component"
)
```

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=budget tests/

# Run specific test category
pytest tests/unit/
pytest tests/integration/
```

### Debug Mode

```bash
# Enable debug logging
export BUDGET_DEBUG=true
export BUDGET_LOG_LEVEL=DEBUG

# Run with verbose output
python -m budget.api.app --debug
```

### Adding New Providers

1. Create provider adapter in `budget/providers/`
2. Implement `BaseProvider` interface
3. Add pricing configuration
4. Register in provider factory
5. Add tests

## Related Documentation

- [Budget Integration Guide](/MetaData/ComponentDocumentation/Budget/INTEGRATION_GUIDE.md)
- [API Reference](/Budget/docs/api_reference.md)
- [Provider Configuration](/Budget/docs/providers.md)
- [Budget Policies](/Budget/docs/policies.md)
