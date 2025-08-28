# Memory Middleware for CI Integration

Natural memory integration for CIs through transparent injection and extraction.

## Quick Start

Run memory tests:
```python
# Basic test
python tests/test_memory_integration.py --test basic --ci ergon

# Scenario test  
python tests/test_memory_integration.py --test scenario --scenario context_persistence

# A/B comparison
python tests/test_memory_integration.py --test ab --scenario pattern_recognition

# Test habit training
python tests/test_memory_integration.py --test training
```

## Architecture

### Components

1. **HookManager** - Orchestrates pre/post processing hooks
2. **MemoryInjector** - Enriches prompts with relevant memories
3. **MemoryExtractor** - Identifies significant memories in responses
4. **HabitTrainer** - Progressive training (explicit → autonomous)
5. **MemoryPhaseManager** - Coordinates all memory operations

### Memory Tiers

- **Short-term**: Last 5-10 messages (always available)
- **Medium-term**: Session/project context (hours)
- **Long-term**: Persistent knowledge (days+)
- **Latent-space**: Associated memories via similarity

### Integration Points

Memory hooks into Claude processing:
```
[User Message] → [Memory Injection] → [Claude] → [Memory Extraction] → [Response]
```

## Habit Training Stages

CIs progressively learn to use memory naturally:

1. **Explicit**: Full prompts "/recall relevant memories"
2. **Shortened**: Abbreviated "/r"
3. **Minimal**: Just "/"
4. **Occasional**: 50% prompted
5. **Autonomous**: Natural memory use

## Test Scenarios

- **context_persistence**: Memory across time gaps
- **pattern_recognition**: Learning from repetition
- **preference_learning**: Adapting to user style
- **deep_philosophy**: Complex conceptual memory

## Memory Privacy Levels

- **Private**: Individual CI memories
- **Team**: Shared within working group
- **Tribal**: Cultural knowledge for all CIs

## Usage in Code

```python
from Rhetor.rhetor.core.memory_middleware.integration import get_memory_integrated_handler

# Get handler with memory
handler = get_memory_integrated_handler()

# Process message with memory
response = await handler.handle_forwarded_message('ergon', 'Your message')

# Check metrics
metrics = handler.get_memory_metrics('ergon')
progress = handler.get_training_progress('ergon')
```

## Monitoring

View memory metrics:
- Injection/extraction times
- Memory usage rates
- Training progression
- Storage statistics

Test results saved to: `~/.engram/test_results/`

## Next Steps

1. Run basic tests to verify integration
2. Use scenario tests to evaluate memory persistence
3. Run A/B tests to measure improvement
4. Monitor habit formation progress
5. Test collaborative memory between CIs