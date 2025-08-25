# Penia (Budget) Component Guide

## Overview

Penia is Tekton's budget management and cost tracking component, providing real-time visibility into LLM usage costs across all components. Named after the Greek personification of poverty (a reminder to manage resources wisely), Penia helps prevent cost overruns through proactive monitoring and alerts.

## Component Purpose

- **Cost Tracking**: Monitor LLM usage costs in real-time
- **Budget Management**: Set and enforce spending limits
- **Usage Analytics**: Analyze usage patterns and optimize costs
- **Alert System**: Proactive notifications for budget thresholds
- **Model Recommendations**: Suggest cost-effective models based on task requirements

## Architecture

### Backend Structure
```
Penia/
├── budget/
│   ├── __main__.py          # Entry point
│   ├── api/
│   │   ├── app.py           # FastAPI application
│   │   ├── endpoints.py     # API endpoints
│   │   ├── models.py        # Request/response models
│   │   └── assistant_endpoints.py  # LLM assistant integration
│   ├── core/
│   │   ├── budget_component.py    # Main component class
│   │   ├── engine.py             # Budget tracking engine
│   │   ├── allocation.py         # Budget allocation logic
│   │   ├── tracking.py           # Usage tracking
│   │   └── policy.py             # Budget policies
│   └── data/
│       ├── models.py             # Database models
│       └── repository.py         # Data access layer
```

### Frontend Structure
```
Hephaestus/ui/components/budget/
├── budget-component.html         # Main UI component
└── scripts/
    ├── budget-models.js          # Data models
    ├── budget-api-client.js      # API client
    ├── budget-state-manager.js   # State management
    └── budget-ui-manager.js      # UI updates
```

## Key Features

### 1. Real-time Dashboard
- Live spending metrics (daily, weekly, monthly)
- Token usage visualization
- Provider cost breakdown
- Interactive charts with Chart.js

### 2. Usage Tracking
- Detailed usage records by component
- Filter by date range with preset options
- Export capabilities for reporting

### 3. Budget Settings
- Configurable spending limits
- Enforcement policies (warn, block, approve)
- Provider-specific limits
- Free model allowances

### 4. Alert System
- Threshold-based alerts
- Email notifications
- Real-time WebSocket updates
- Alert history and management

### 5. Assistant Integration
- Budget-aware chat interface
- Cost optimization recommendations
- Usage pattern analysis

## API Endpoints

### Budget Management
- `GET /api/v1/budgets` - List budgets
- `POST /api/v1/budgets` - Create budget
- `GET /api/v1/budgets/{id}` - Get budget details
- `PUT /api/v1/budgets/{id}` - Update budget
- `GET /api/v1/budgets/{id}/summary` - Get spending summary

### Usage Tracking
- `POST /api/v1/usage/record` - Record usage
- `GET /api/v1/usage/records` - List usage records
- `POST /api/v1/usage/summary` - Get usage summary

### Alerts
- `GET /api/v1/alerts` - List alerts
- `PUT /api/v1/alerts/{id}/dismiss` - Dismiss alert

### Assistant
- `POST /api/v1/assistant` - Send message to budget assistant

## UI Implementation

### Design Patterns
1. **HTML Injection Pattern**: All UI updates use innerHTML, no DOM manipulation
2. **CSS-First Styling**: Minimal JavaScript, maximum CSS
3. **BEM Naming**: Consistent class naming (`.budget__element--modifier`)
4. **Semantic Tags**: Full data-tekton-* tagging for CI navigation

### Key UI Components

#### Dashboard
```html
<div class="budget__summary">
    <div class="budget__card">
        <div class="budget__card-title">Daily Spend</div>
        <div class="budget__card-amount">$2.47</div>
        <div class="budget__card-limit">/ $5.00</div>
    </div>
</div>
```

#### Date Filter
```html
<div class="budget__filter-group">
    <label class="budget__filter-label">Beginning:</label>
    <input type="date" id="start-date" data-tekton-filter="start-date">
</div>
```

#### Chat Integration
```javascript
async function budget_sendToAssistant(message, chatType, messagesContainer) {
    const response = await fetch(budgetUrl('/api/v1/assistant'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            message: message,
            context: chatType === 'team' ? 'team_collaboration' : 'budget_management'
        })
    });
}
```

## Integration with Other Components

### Hermes Integration
- Registers with Hermes on startup
- Provides MCP tools for budget queries
- Heartbeat monitoring

### WebSocket Support
- Real-time budget updates
- Alert notifications
- Usage tracking events

### CI Assistant
- Budget-specific context
- Cost optimization suggestions
- Usage pattern analysis

## Configuration

### Environment Variables
```bash
BUDGET_PORT=8113          # Component port
BUDGET_DB_PATH=.tekton/data/budget/budget.db
BUDGET_LOG_LEVEL=INFO
```

### Default Settings
- Daily limit: $5.00
- Weekly limit: $25.00
- Monthly limit: $100.00
- Warning threshold: 80%
- Enforcement: Warn mode

## Development Guidelines

### Adding New Features
1. Follow HTML injection pattern for UI updates
2. Use semantic tags for all new elements
3. Add appropriate landmarks to backend code
4. Update API documentation
5. Test with both live and mock data

### Testing
```bash
# Run backend tests
cd Penia
python -m pytest

# Test API endpoints
curl http://localhost:8113/api/v1/budgets
curl http://localhost:8113/api/v1/usage/records
```

### Common Issues
1. **No budgets configured**: Create default budget via API
2. **Charts not displaying**: Ensure Chart.js is loaded
3. **Assistant not responding**: Check API endpoint availability

## Best Practices

1. **Always use innerHTML for updates** - No createElement or appendChild
2. **Tag all UI elements** - Use data-tekton-* attributes
3. **Handle empty states** - Show meaningful messages when no data
4. **Async all API calls** - Use async/await pattern
5. **Error handling** - Graceful fallbacks for API failures

## Future Enhancements

1. **Advanced Analytics**
   - Cost predictions
   - Usage trends
   - Optimization suggestions

2. **Budget Templates**
   - Pre-configured budget profiles
   - Project-based budgets
   - Team allocations

3. **Integration Features**
   - Export to accounting systems
   - Slack/email notifications
   - Custom webhooks

4. **Enhanced Visualizations**
   - Historical comparisons
   - Cost breakdown by task type
   - Model efficiency metrics

---

*Component Version: 0.1.0*
*Last Updated: 2025-07-31*
*Maintainer: Tekton Team*