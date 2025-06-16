# Budget Component Technical Documentation

## Architecture Overview

The Budget component is designed as a full-fledged Tekton component for managing token and cost budgets for LLM usage. It follows a layered architecture that separates core budget concerns from specialized functionality.

### Layered Architecture

The Budget component is structured in layers:

1. **Core Layer**: Foundational budget tracking and enforcement
2. **Data Layer**: Data models, repositories, and storage
3. **Service Layer**: API endpoints, services, and messaging
4. **Integration Layer**: Adapters for different components and providers
5. **UI Layer**: Dashboard and visualization components

### Component Diagram

```
┌─────────────────────────────────────────────────────┐
│                  Budget Component                    │
│                                                     │
│  ┌─────────┐  ┌─────────────┐  ┌────────────────┐   │
│  │   API   │  │ WebSocket   │  │  MCP Protocol  │   │
│  │ Server  │  │   Server    │  │     Server     │   │
│  └────┬────┘  └──────┬──────┘  └────────┬───────┘   │
│       │              │                  │           │
│  ┌────┴──────────────┴──────────────────┴────────┐  │
│  │                Service Layer                  │  │
│  │                                              │  │
│  │  ┌──────────┐ ┌─────────┐ ┌───────────────┐  │  │
│  │  │ Reporting│ │ Pricing │ │ Notification  │  │  │
│  │  │ Service  │ │ Service │ │   Service     │  │  │
│  │  └──────────┘ └─────────┘ └───────────────┘  │  │
│  └───────────────────────┬───────────────────────┘  │
│                          │                          │
│  ┌────────────────────────────────────────────────┐ │
│  │                 Core Layer                     │ │
│  │                                                │ │
│  │  ┌──────────┐ ┌─────────┐ ┌────────┐ ┌──────┐ │ │
│  │  │  Budget  │ │   Policy│ │Tracking│ │Engine│ │ │
│  │  │ Manager  │ │ Manager │ │ Manager│ │      │ │ │
│  │  └──────────┘ └─────────┘ └────────┘ └──────┘ │ │
│  └────────────────────────┬───────────────────────┘ │
│                           │                         │
│  ┌─────────────────────────────────────────────────┐│
│  │                  Data Layer                     ││
│  │                                                 ││
│  │  ┌──────────┐ ┌──────────┐ ┌─────────────────┐ ││
│  │  │ Entities │ │Repository│ │ Database Access │ ││
│  │  │          │ │  Pattern │ │                 │ ││
│  │  └──────────┘ └──────────┘ └─────────────────┘ ││
│  └─────────────────────────────────────────────────┘│
│                                                     │
│  ┌─────────────────────────────────────────────────┐│
│  │             Integration Layer                   ││
│  │                                                 ││
│  │  ┌──────────┐ ┌──────────┐ ┌─────────────────┐ ││
│  │  │  Apollo  │ │  Rhetor  │ │ Price Source    │ ││
│  │  │ Adapter  │ │ Adapter  │ │   Adapters      │ ││
│  │  └──────────┘ └──────────┘ └─────────────────┘ ││
│  └─────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────┘
```

## Core Components

### Budget Engine

The Budget engine is the central component responsible for budget management, allocation, and enforcement. It provides these key functions:

- Budget creation and management
- Token allocation based on policies
- Cost calculation and tracking
- Budget enforcement
- Usage recording and analysis

Key files:
- `/Budget/budget/core/engine.py`
- `/Budget/budget/core/allocation.py`
- `/Budget/budget/core/policy.py`
- `/Budget/budget/core/tracking.py`

### Data Model

The Budget component uses a domain-driven data model with these key entities:

#### Budget

Represents a budget with limits, periods, and metadata.

```python
class Budget:
    budget_id: str
    name: str
    description: str
    owner: str
    is_active: bool
    creation_time: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
```

#### BudgetPolicy

Defines a policy for budget enforcement.

```python
class BudgetPolicy:
    policy_id: str
    budget_id: str
    type: BudgetPolicyType  # WARN, ENFORCE, LOG
    period: BudgetPeriod  # HOURLY, DAILY, WEEKLY, MONTHLY
    tier: Optional[BudgetTier]  # LOCAL_LIGHTWEIGHT, LOCAL_MIDWEIGHT, REMOTE_HEAVYWEIGHT
    provider: Optional[str]
    component: Optional[str]
    task_type: Optional[str]
    token_limit: Optional[int]
    cost_limit: Optional[float]
    warning_threshold: float
    action_threshold: float
    enabled: bool
    created_at: datetime
    updated_at: datetime
```

#### BudgetAllocation

Represents a token allocation for a specific context or operation.

```python
class BudgetAllocation:
    allocation_id: str
    budget_id: str
    context_id: str
    component: str
    tokens_allocated: int
    tokens_used: int
    remaining_tokens: int
    tier: Optional[BudgetTier]
    provider: Optional[str]
    model: Optional[str]
    task_type: Optional[str]
    priority: int
    is_active: bool
    creation_time: datetime
    expiration_time: Optional[datetime]
    metadata: Dict[str, Any]
```

#### UsageRecord

Records token and cost usage for a specific operation.

```python
class UsageRecord:
    record_id: str
    allocation_id: str
    context_id: str
    component: str
    provider: str
    model: str
    task_type: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float
    timestamp: datetime
    metadata: Dict[str, Any]
```

#### ProviderPricing

Stores pricing information for a provider and model.

```python
class ProviderPricing:
    pricing_id: str
    provider: str
    model: str
    price_type: PriceType  # TOKEN, CHARACTER, IMAGE, TIME, FIXED
    input_cost_per_token: float
    output_cost_per_token: float
    input_cost_per_char: float
    output_cost_per_char: float
    cost_per_image: float
    cost_per_second: float
    fixed_cost_per_request: float
    effective_date: datetime
    end_date: Optional[datetime]
    source: str
    verified: bool
    created_at: datetime
```

### Repository Pattern

The Budget component uses the repository pattern to abstract data access:

```python
class BudgetRepository:
    def get_by_id(self, budget_id: str) -> Optional[Budget]: ...
    def get_all(self, limit: int = 100, offset: int = 0) -> List[Budget]: ...
    def create(self, budget: Budget) -> Budget: ...
    def update(self, budget: Budget) -> Budget: ...
    def delete(self, budget_id: str) -> bool: ...
    # Additional query methods...
```

Each entity has its own repository with specific query methods.

## Price Monitoring System

The Budget component includes an automated price monitoring system that fetches pricing information from multiple sources and verifies it for accuracy.

### Price Source Adapters

Price information is fetched from multiple sources using adapters:

1. **LiteLLM Adapter**: Primary source from LiteLLM's pricing database
2. **LLMPrices Adapter**: Scrapes LLMPrices.com for pricing data
3. **PretrainedAI Adapter**: Scrapes Pretrained.ai for pricing data

### Price Verification

Prices are verified across sources before being applied:

1. Prices are fetched from multiple sources
2. A trust scoring system is applied to each source
3. Prices are compared within a tolerance threshold
4. A verification status is assigned to each price update
5. Verified prices are applied, while unverified prices are flagged for review

### Price Update Process

The price update process follows these steps:

1. Scheduled triggers check for updates at configured intervals
2. Source adapters fetch current pricing data
3. Verification system compares prices across sources
4. If verified, the price is updated in the database
5. If not verified, a conflict alert is generated for manual review
6. Notifications are sent for significant price changes

## Integration Layer

The integration layer provides adapters for other Tekton components to interact with the Budget component.

### Component Adapters

#### Apollo Adapter

The Apollo adapter maps Apollo's token-focused budget system to the Budget component:

- Maps Apollo's tier system to Budget tiers
- Translates Apollo's token allocation to Budget allocations
- Provides migration utilities for existing Apollo budgets

#### Rhetor Adapter

The Rhetor adapter maps Rhetor's cost-focused budget system to the Budget component:

- Maps Rhetor's cost tracking to Budget cost limits
- Translates Rhetor's provider rates to Budget pricing
- Provides migration utilities for existing Rhetor budgets

### Client Libraries

The Budget component provides client libraries for easy integration:

- Python client library for Tekton components
- JavaScript client library for UI components
- CLI client for command-line operations

## API Layer

The Budget component exposes its functionality through multiple interfaces following the Single Port Architecture pattern:

### HTTP API

RESTful API endpoints for budget operations:

- `/api/budgets`: Budget management
- `/api/policies`: Policy management
- `/api/allocations`: Allocation management
- `/api/usage`: Usage recording and reporting
- `/api/prices`: Price management

### WebSocket API

Real-time updates for budget status and alerts:

- `/ws/budget/updates`: Budget updates
- `/ws/budget/alerts`: Budget alerts

### MCP Protocol

Multi-Component Protocol support for standardized communication:

- `/api/mcp`: MCP endpoint
- Message handlers for budget operations
- Event publishing for budget events

## Service Layer

The service layer provides core services for budget operations:

### Price Monitoring Service

Manages automated price updates from external sources:

- Schedule management for price checks
- Source adapter coordination
- Price verification and conflict resolution

### Reporting Service

Generates reports and analyses of budget usage:

- Aggregation and filtering
- Period-based reporting
- Provider and model breakdown
- Export functionality

### Notification Service

Manages alerts and notifications for budget events:

- Threshold monitoring
- Alert generation and delivery
- Subscription management
- Integration with notification channels

## Security Considerations

### Authentication and Authorization

The Budget component uses Tekton's standard authentication and authorization mechanisms:

- API key for service-to-service authentication
- Role-based access control for operations
- Permission validation for sensitive operations

### Data Protection

Sensitive financial data is protected through:

- Database encryption for cost and pricing data
- Access logs for audit purposes
- Validation and sanitization of inputs
- Security headers for API responses

## Performance Considerations

The Budget component is designed for high performance:

- Efficient database queries for budget operations
- Connection pooling for database access
- Caching for frequently accessed data
- Background processing for price updates
- Optimized aggregation for reporting

## Configuration

The Budget component can be configured through environment variables and configuration files:

### Environment Variables

- `BUDGET_PORT`: HTTP port (default: 8013)
- `BUDGET_HOST`: Hostname for endpoint URL (default: localhost)
- `BUDGET_DATABASE_URL`: Database connection URL
- `PRICE_UPDATE_INTERVAL`: Interval for price updates in minutes
- `BUDGET_LOG_LEVEL`: Logging level (default: INFO)

### Configuration File

The configuration file (`config.yaml`) can customize:

- Database settings
- Price source adapters
- Verification thresholds
- Reporting options
- Notification channels

## Debug Instrumentation

The Budget component follows Tekton's debug instrumentation guidelines:

### Logging Levels

- **ERROR**: Critical failures that prevent operation
- **WARNING**: Issues that might affect functionality
- **INFO**: Important operations and state changes
- **DEBUG**: Detailed information for troubleshooting

### Component Tags

Each log entry includes a component tag for filtering:

- `budget_engine`: Core budget engine
- `allocation`: Allocation management
- `policy`: Policy enforcement
- `tracking`: Usage tracking
- `price_manager`: Price monitoring
- `api`: API endpoints
- `rhetor_adapter`: Rhetor integration
- `apollo_adapter`: Apollo integration

### Debug Log Example

```python
debug_log.info("budget_engine", f"Creating budget: {budget.name}")
debug_log.debug("allocation", f"Allocating {tokens} tokens for context {context_id}")
debug_log.error("price_manager", f"Failed to update prices from {source.name}: {str(e)}")
```

## Testing Strategy

The Budget component uses a comprehensive testing approach:

### Unit Tests

Unit tests for individual components:

- Core budget functionality
- Data repositories
- Service implementations
- Adapter functionality

### Integration Tests

Integration tests for component interactions:

- API endpoints
- Database operations
- External service integrations
- Component adapters

### End-to-End Tests

End-to-end tests for critical workflows:

- Budget creation and enforcement
- Token allocation and usage
- Price monitoring and updates
- Reporting and alerts

### Performance Tests

Performance tests for key operations:

- High-volume allocation requests
- Concurrent budget operations
- Large-scale reporting queries
- Price update operations

## Dependency Management

The Budget component has these key dependencies:

- FastAPI: Web framework for API endpoints
- SQLAlchemy: ORM for database access
- Pydantic: Data validation and serialization
- aiohttp: Asynchronous HTTP client for external APIs
- websockets: WebSocket support for real-time updates
- Click: Command-line interface framework

## Deployment

The Budget component can be deployed in various environments:

### Development

```bash
# Start the Budget component with development settings
BUDGET_ENV=development ./run_budget.sh
```

### Production

```bash
# Start the Budget component with production settings
BUDGET_ENV=production ./run_budget.sh
```

### Docker

```bash
# Build and run the Budget component in Docker
docker build -t budget:latest .
docker run -p 8013:8013 budget:latest
```

## Future Enhancements

Planned future enhancements include:

1. **Advanced Budget Forecasting**: Predict future usage based on historical patterns
2. **Machine Learning for Optimization**: Use ML for optimal budget allocation
3. **Extended Visualization**: Enhanced dashboard with interactive charts
4. **Integration with Enterprise Billing**: Connect to enterprise billing systems
5. **Multi-Tenant Support**: Support for multiple organizations and teams
6. **Advanced Provider Management**: Support for custom provider pricing models

## Technical Debt and Limitations

Current technical limitations include:

1. **Limited Provider Coverage**: Not all LLM providers have complete pricing data
2. **No AI-Generated Content Detection**: No differentiation between AI and human-generated content
3. **Basic Migration Tools**: Migration tools need enhancement for complex scenarios
4. **Limited Historical Analysis**: Basic historical analysis capabilities
5. **No Real-time Monitoring**: Dashboard updates are not real-time in the initial version

## Troubleshooting

Common issues and solutions:

### Price Updates Failing

If price updates are failing:

1. Check network connectivity to external sources
2. Verify API keys and authentication
3. Check source adapter logs for specific errors
4. Try manual price updates through the API

### Budget Enforcement Issues

If budget enforcement isn't working:

1. Verify policy configuration (enabled, thresholds, etc.)
2. Check allocation status and remaining tokens
3. Verify component integration is using the correct budget
4. Review usage records for discrepancies

### Performance Problems

If experiencing performance issues:

1. Check database indexes and query performance
2. Review concurrent operations and potential bottlenecks
3. Check cache hit rates and optimize caching
4. Review logging levels and reduce debug logging in production

## References

- [Budget Component README](/Budget/README.md)
- [API Reference](/MetaData/ComponentDocumentation/Budget/API_REFERENCE.md)
- [Integration Guide](/MetaData/ComponentDocumentation/Budget/INTEGRATION_GUIDE.md)
- [User Guide](/MetaData/ComponentDocumentation/Budget/USER_GUIDE.md)
- [Apollo Token Budget](/Apollo/apollo/core/token_budget.py)
- [Rhetor Budget Manager](/Rhetor/rhetor/core/budget_manager.py)