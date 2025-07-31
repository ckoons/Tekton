# Penia (Budget) Component Architecture

## Overview

Penia implements a real-time budget tracking and cost management system for Tekton's LLM usage. The architecture follows Tekton's Single Port Architecture pattern and integrates seamlessly with the platform's AI orchestration capabilities.

## Architectural Principles

1. **Real-time Visibility**: Immediate cost feedback through WebSocket updates
2. **Proactive Management**: Alert before limits are exceeded, not after
3. **Component Isolation**: Each component tracks its own usage independently
4. **Centralized Aggregation**: Penia aggregates all usage for unified view
5. **Policy Enforcement**: Configurable actions when limits are approached

## System Architecture

### Component Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                        Hephaestus UI                         │
│  ┌─────────────────┐  ┌─────────────┐  ┌────────────────┐  │
│  │ Budget Dashboard│  │Usage Details│  │    Settings    │  │
│  └────────┬────────┘  └──────┬──────┘  └───────┬────────┘  │
└───────────┼──────────────────┼──────────────────┼───────────┘
            │                  │                  │
            └──────────────────┴──────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   Penia API       │
                    │   Port: 8113      │
                    └─────────┬─────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐  ┌────────▼────────┐  ┌────────▼────────┐
│ Budget Engine  │  │ Usage Tracker   │  │ Alert Manager   │
└───────┬────────┘  └────────┬────────┘  └────────┬────────┘
        │                     │                     │
        └─────────────────────┴─────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   SQLite DB       │
                    │ budget.db         │
                    └───────────────────┘
```

### Data Flow

1. **Usage Recording**
   ```
   Component → Usage API → Tracking Manager → Database
                           ↓
                        WebSocket → UI Update
   ```

2. **Budget Checking**
   ```
   Component → Check API → Budget Engine → Policy Evaluation
                                        ↓
                                    Allow/Warn/Block
   ```

3. **Alert Generation**
   ```
   Usage Threshold → Alert Manager → WebSocket Notification
                                  → Email (if configured)
                                  → UI Alert Display
   ```

## Core Components

### Budget Engine (`budget/core/engine.py`)
- Manages budget lifecycle
- Enforces spending policies
- Calculates remaining budgets
- Provides cost projections

### Usage Tracker (`budget/core/tracking.py`)
- Records all LLM usage
- Aggregates by component/model/time
- Maintains usage history
- Generates analytics

### Alert Manager
- Monitors thresholds
- Sends notifications
- Manages alert state
- Provides alert history

### WebSocket Manager
- Real-time updates to UI
- Budget status broadcasts
- Alert notifications
- Usage event streaming

## Database Schema

### Core Tables

```sql
-- Budget definitions
CREATE TABLE budgets (
    budget_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    daily_limit REAL,
    weekly_limit REAL,
    monthly_limit REAL,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Usage records
CREATE TABLE usage_records (
    record_id TEXT PRIMARY KEY,
    budget_id TEXT,
    component TEXT NOT NULL,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    total_tokens INTEGER,
    cost REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (budget_id) REFERENCES budgets(budget_id)
);

-- Alerts
CREATE TABLE alerts (
    alert_id TEXT PRIMARY KEY,
    budget_id TEXT,
    alert_type TEXT,
    threshold_percent INTEGER,
    message TEXT,
    is_dismissed BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (budget_id) REFERENCES budgets(budget_id)
);
```

## API Design

### RESTful Endpoints

#### Budget Management
```
GET    /api/v1/budgets              # List all budgets
POST   /api/v1/budgets              # Create new budget
GET    /api/v1/budgets/{id}         # Get budget details
PUT    /api/v1/budgets/{id}         # Update budget
DELETE /api/v1/budgets/{id}         # Delete budget
GET    /api/v1/budgets/{id}/summary # Get spending summary
```

#### Usage Tracking
```
POST   /api/v1/usage/record         # Record new usage
GET    /api/v1/usage/records        # List usage records
POST   /api/v1/usage/summary        # Get usage summary
```

#### Model Recommendations
```
POST   /api/v1/prices/recommend     # Get model recommendations
```

### WebSocket Events

```javascript
// Client → Server
{
    "type": "subscribe",
    "channels": ["budget_updates", "alerts"]
}

// Server → Client
{
    "type": "budget_update",
    "data": {
        "daily": { "spent": 2.47, "limit": 5.00 },
        "weekly": { "spent": 12.89, "limit": 25.00 }
    }
}

{
    "type": "alert",
    "data": {
        "alert_id": "...",
        "message": "Daily budget 90% consumed",
        "severity": "warning"
    }
}
```

## Integration Points

### Hermes Registration
```python
await self.hermes_client.register_component({
    "name": "budget",
    "port": 8113,
    "endpoints": [...],
    "capabilities": ["budget_management", "usage_tracking"]
})
```

### MCP Tools
```python
@mcp_tool
async def check_budget(component: str, estimated_cost: float) -> dict:
    """Check if component has budget for operation"""
    return await budget_engine.check_budget(component, estimated_cost)
```

### Assistant Context
```python
{
    "context": "budget_management",
    "system_prompt": "You are a budget optimization assistant...",
    "tools": ["get_usage_summary", "recommend_models", "set_alerts"]
}
```

## Performance Considerations

### Caching Strategy
- In-memory cache for active budgets
- 5-minute TTL for usage summaries
- Immediate cache invalidation on updates

### Database Optimization
- Indexes on timestamp, component, model
- Partitioning by month for usage records
- Vacuum scheduling for SQLite

### WebSocket Management
- Connection pooling
- Heartbeat monitoring
- Automatic reconnection
- Message batching for updates

## Security Considerations

1. **Authentication**: Component-level API keys
2. **Authorization**: Role-based budget access
3. **Data Privacy**: No PII in usage records
4. **Rate Limiting**: API request throttling
5. **Audit Trail**: All budget changes logged

## Monitoring and Observability

### Metrics
- Usage rate (requests/minute)
- Cost accumulation rate
- Alert frequency
- API response times
- WebSocket connection count

### Logging
```python
logger.info(f"Budget check: component={component}, cost={cost}, allowed={allowed}")
logger.warning(f"Budget threshold reached: {percent}% of {period} limit")
logger.error(f"Failed to record usage: {error}")
```

### Health Checks
```json
GET /health
{
    "status": "healthy",
    "database": "connected",
    "websocket_clients": 5,
    "active_budgets": 3,
    "uptime_seconds": 3600
}
```

## Future Architecture Enhancements

1. **Distributed Tracking**
   - Redis for cross-instance state
   - Event sourcing for usage records
   - CQRS for read/write separation

2. **Advanced Analytics**
   - Time-series database integration
   - Machine learning for cost prediction
   - Anomaly detection for usage spikes

3. **External Integrations**
   - Webhook support for alerts
   - Export to billing systems
   - Multi-tenant budget isolation

---

*Architecture Version: 1.0*
*Last Updated: 2025-07-31*
*Architect: Tekton Team*