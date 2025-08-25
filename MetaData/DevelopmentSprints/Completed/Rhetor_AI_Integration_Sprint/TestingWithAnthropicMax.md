# Testing with Anthropic Max Account

## Overview

This document describes how to configure the Rhetor CI Integration Sprint to use your Anthropic Max account for testing, avoiding API charges while developing and testing the component CI features.

## Anthropic Max Benefits for Testing

1. **No API Charges**: Use Claude models without per-token costs
2. **Higher Rate Limits**: Better for testing multiple component CIs
3. **All Claude Models**: Access to Haiku, Sonnet, and Opus
4. **Ideal for Development**: Perfect for iterative testing

## Configuration Steps

### Step 1: Configure Anthropic Max in Rhetor

Update your local `.env.local` file (this file is gitignored):

```bash
# Anthropic Max Configuration
ANTHROPIC_API_KEY=your_anthropic_max_api_key_here
ANTHROPIC_MAX_ACCOUNT=true
ANTHROPIC_BASE_URL=https://api.anthropic.com  # May differ for Max accounts

# Default to Anthropic for testing
RHETOR_DEFAULT_PROVIDER=anthropic
RHETOR_DEFAULT_MODEL=claude-3-sonnet-20240229
```

### Step 2: Update Component Model Configuration

Create a test configuration file `rhetor/config/component_models_test.json`:

```json
{
  "_test_mode": true,
  "_description": "Test configuration using Anthropic Max account",
  
  "budget": {
    "primary_model": "claude-3-haiku-20240307",
    "provider": "anthropic",
    "fallback_models": [],
    "notes": "Using Max account - no fallback needed"
  },
  "athena": {
    "primary_model": "claude-3-sonnet-20240229",
    "provider": "anthropic",
    "fallback_models": []
  },
  "sophia": {
    "primary_model": "claude-3-opus-20240229",
    "provider": "anthropic",
    "fallback_models": []
  },
  "ergon": {
    "primary_model": "claude-3-sonnet-20240229",
    "provider": "anthropic",
    "fallback_models": [],
    "notes": "Using Sonnet instead of GPT-4 for Max testing"
  },
  "synthesis": {
    "primary_model": "claude-3-sonnet-20240229",
    "provider": "anthropic",
    "fallback_models": []
  },
  "prometheus": {
    "primary_model": "claude-3-sonnet-20240229",
    "provider": "anthropic",
    "fallback_models": []
  },
  "engram": {
    "primary_model": "claude-3-haiku-20240307",
    "provider": "anthropic",
    "fallback_models": []
  },
  "hermes": {
    "primary_model": "claude-3-haiku-20240307",
    "provider": "anthropic",
    "fallback_models": []
  },
  "metis": {
    "primary_model": "claude-3-sonnet-20240229",
    "provider": "anthropic",
    "fallback_models": []
  },
  "harmonia": {
    "primary_model": "claude-3-sonnet-20240229",
    "provider": "anthropic",
    "fallback_models": []
  },
  "telos": {
    "primary_model": "claude-3-haiku-20240307",
    "provider": "anthropic",
    "fallback_models": []
  },
  "apollo": {
    "primary_model": "claude-3-sonnet-20240229",
    "provider": "anthropic",
    "fallback_models": []
  },
  "terma": {
    "primary_model": "claude-3-haiku-20240307",
    "provider": "anthropic",
    "fallback_models": []
  },
  "rhetor": {
    "primary_model": "claude-3-opus-20240229",
    "provider": "anthropic",
    "fallback_models": []
  },
  "hephaestus": {
    "primary_model": "claude-3-haiku-20240307",
    "provider": "anthropic",
    "fallback_models": []
  }
}
```

### Step 3: Update ComponentAIManager for Test Mode

Add test mode support to `rhetor/core/component_ai_manager.py`:

```python
class ComponentAIManager:
    def __init__(self, llm_client, model_router, context_manager, prompt_engine, test_mode=False):
        self.test_mode = test_mode or os.environ.get('ANTHROPIC_MAX_ACCOUNT', '').lower() == 'true'
        
        if self.test_mode:
            debug_log("rhetor", "ComponentAIManager initialized in TEST MODE using Anthropic Max", level="info")
            self.config_file = "component_models_test.json"
        else:
            self.config_file = "component_models.json"
            
        # Load appropriate configuration
        self._load_model_configurations()
```

### Step 4: Disable Budget Enforcement for Testing

In `rhetor/core/budget_manager.py`, add Max account detection:

```python
def __init__(self, db_path: Optional[str] = None, period: BudgetPeriod = BudgetPeriod.DAILY):
    self.is_max_account = os.environ.get('ANTHROPIC_MAX_ACCOUNT', '').lower() == 'true'
    
    if self.is_max_account:
        logger.info("Anthropic Max account detected - budget enforcement disabled")
        self.enforcement_policy = BudgetPolicy.IGNORE
    else:
        self.enforcement_policy = BudgetPolicy.WARN
```

## Testing Strategy

### Phase 1: Individual Component Testing

Test each component CI individually:

```bash
# Set test environment
export ANTHROPIC_MAX_ACCOUNT=true

# Launch Rhetor in test mode
cd Rhetor
python -m rhetor --test-mode

# In another terminal, test each component
python scripts/test_component_ai.py --component budget
python scripts/test_component_ai.py --component athena
# ... etc
```

### Phase 2: Concurrent CI Testing

Test multiple CIs simultaneously:

```python
# scripts/test_concurrent_ais.py
async def test_concurrent_ais():
    """Test multiple component CIs concurrently"""
    components = ['budget', 'athena', 'ergon', 'prometheus', 'sophia']
    
    tasks = []
    for component in components:
        task = test_component_ai(component)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    print(f"Tested {len(results)} component CIs concurrently")
```

### Phase 3: Team Chat Testing

Test the team chat with multiple CIs:

```python
# scripts/test_team_chat.py
async def test_team_chat():
    """Test team chat with multiple CIs"""
    # Initialize team chat
    team_chat = await create_team_chat_session()
    
    # Add component CIs
    await team_chat.add_participant('budget')
    await team_chat.add_participant('athena')
    await team_chat.add_participant('prometheus')
    
    # Send a collaborative request
    response = await team_chat.send_message(
        "Team, we need to plan the Q2 budget for CI services. "
        "@budget analyze current costs, @athena provide usage patterns, "
        "@prometheus suggest optimization strategies."
    )
```

## Monitoring During Testing

### 1. Usage Dashboard

Create a simple usage monitor:

```python
# scripts/monitor_usage.py
class AnthropicMaxMonitor:
    def track_request(self, component_id, model, tokens):
        """Track usage without billing concerns"""
        logger.info(f"Component: {component_id}, Model: {model}, Tokens: {tokens}")
        # Log to file for analysis
        with open("anthropic_max_usage.log", "a") as f:
            f.write(f"{datetime.now()},{component_id},{model},{tokens}\n")
```

### 2. Performance Metrics

Track performance without cost concerns:

```python
PERFORMANCE_METRICS = {
    'response_times': [],
    'tokens_per_second': [],
    'concurrent_requests': 0,
    'filter_overhead': []
}
```

## Best Practices for Max Account Testing

1. **Test All Models**: Since there's no cost, test Opus for complex tasks
2. **Stress Testing**: Run concurrent requests to find bottlenecks
3. **Long Conversations**: Test context window limits without budget concerns
4. **A/B Testing**: Compare different models for the same component
5. **Team Chat Load**: Test with all 15 CIs in team chat simultaneously

## Transitioning to Production

When ready for production:

1. **Switch Configuration**: Use `component_models.json` instead of test version
2. **Enable Budget Enforcement**: Set appropriate budget limits
3. **Add Fallback Models**: Include GPT models for redundancy
4. **Update Provider Mix**: Balance between providers
5. **Monitor Costs**: Enable full budget tracking

## Testing Checklist

- [ ] Anthropic Max API key configured
- [ ] Test mode enabled in environment
- [ ] Budget enforcement disabled
- [ ] All component CIs using Anthropic models
- [ ] Performance monitoring enabled
- [ ] Usage logging active
- [ ] Team chat tested with multiple CIs
- [ ] Stress testing completed
- [ ] Documentation updated with findings

## Example Test Session

```bash
# Terminal 1: Start Rhetor
export ANTHROPIC_MAX_ACCOUNT=true
cd Rhetor
python -m rhetor --debug

# Terminal 2: Start Hephaestus UI
cd Hephaestus
python ui/server/server.py

# Terminal 3: Run test suite
cd scripts
python run_all_tests.py --use-max-account

# Terminal 4: Monitor logs
tail -f ~/.tekton/logs/rhetor.log | grep "ComponentAI"
```

This configuration allows comprehensive testing of the Rhetor CI Integration Sprint using your Anthropic Max account without incurring API charges.