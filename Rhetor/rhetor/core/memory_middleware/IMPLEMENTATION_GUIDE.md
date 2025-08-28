# Memory Hooks Implementation Guide for All Tekton CIs

## Quick Start

### 1. Enable Memory for All CIs

```bash
# Enable memory for all CIs at once
python scripts/enable_ci_memory.py enable --all --save

# Or enable for specific CI
python scripts/enable_ci_memory.py enable --ci ergon
```

### 2. Check Status

```bash
python scripts/enable_ci_memory.py status --verbose
```

### 3. Test Memory

```bash
# Test with basic scenario
python tests/test_memory_integration.py --test basic --ci ergon

# Test specific CI
python scripts/enable_ci_memory.py test ergon
```

## System Architecture

### Components

1. **UniversalMemoryAdapter**: Works with any CI type (Claude, GPT, local models)
2. **TektonMemorySystem**: System-level integration for all CIs
3. **MemoryPhaseManager**: Orchestrates memory operations per CI
4. **HabitTrainer**: Progressive training system

### How It Works

```
[User Message] 
    → [Universal Adapter checks CI type]
    → [Memory Injection based on config]
    → [CI Processing] 
    → [Memory Extraction based on response]
    → [Response to User]
```

## Configuration

### Per-CI Configuration

Edit `~/.tekton/memory_config.yaml`:

```yaml
ci_configs:
  your_ci_name:
    injection_style: natural    # natural/structured/minimal
    training_stage: explicit    # explicit/shortened/minimal/occasional/autonomous
    memory_tiers: [short, medium, long, latent]
    focus: "what this CI should remember"
    auto_extract: true
```

### Configure via Command Line

```bash
python scripts/enable_ci_memory.py configure ergon \
    --injection-style natural \
    --training-stage minimal \
    --memory-tiers short,medium,long \
    --focus "solutions and patterns"
```

## Integration Points

### For New CI Types

```python
from Rhetor.rhetor.core.memory_middleware.universal_adapter import get_universal_adapter

# In your CI handler
adapter = get_universal_adapter()

# Initialize memory for your CI
adapter.initialize_ci_memory('my_ci', config)

# Wrap your handler
wrapped = await adapter.wrap_handler(your_handler, 'my_ci')
```

### For Streaming Models

```python
from Rhetor.rhetor.core.memory_middleware.universal_adapter import StreamingMemoryAdapter

streaming_adapter = StreamingMemoryAdapter(get_universal_adapter())

# Start stream with memory
enriched = await streaming_adapter.start_stream('ci_name', message)

# Process tokens
for token in stream:
    await streaming_adapter.process_token('ci_name', token)

# End stream and extract memories
await streaming_adapter.end_stream('ci_name')
```

## Memory Tiers

- **Short-term**: Last 5-10 messages (1 hour retention)
- **Medium-term**: Session context (24 hour retention)
- **Long-term**: Important knowledge (7 day retention)
- **Latent**: Vector similarity search (30 day retention)

## Training Stages

CIs progress through stages automatically:

1. **Explicit**: Full memory prompts
2. **Shortened**: Abbreviated prompts (/r)
3. **Minimal**: Single character (/)
4. **Occasional**: 50% prompted
5. **Autonomous**: Natural memory use

Track progress:
```bash
python scripts/enable_ci_memory.py status --verbose
```

## Privacy Levels

Memories can be:
- **Private**: Only for that CI
- **Team**: Shared with working group
- **Tribal**: Cultural knowledge for all CIs

## Automatic Startup

Add to Tekton's initialization:

```python
# In Tekton's main startup
from Rhetor.rhetor.core.memory_middleware.system_integration import initialize_tekton_memory

async def startup():
    # ... other initialization
    await initialize_tekton_memory()
```

## Monitoring

View metrics:
```python
from Rhetor.rhetor.core.memory_middleware.universal_adapter import get_universal_adapter

adapter = get_universal_adapter()
status = adapter.get_memory_status()
```

## Troubleshooting

### Memory Not Working

1. Check if enabled: `python scripts/enable_ci_memory.py status`
2. Check config: `cat ~/.tekton/memory_config.yaml`
3. Test directly: `python scripts/enable_ci_memory.py test <ci_name>`

### Too Much Memory Injection

Adjust injection style:
```bash
python scripts/enable_ci_memory.py configure <ci_name> --injection-style minimal
```

### CI Not Learning

Check training stage:
```bash
python scripts/enable_ci_memory.py status --verbose
```

Manually advance if needed:
```python
adapter.memory_managers[ci_name].habit_trainer.set_stage(ci_name, 'minimal')
```

## Best Practices

1. **Start with explicit training** - Let CIs learn gradually
2. **Use natural injection for conversational CIs** - Apollo, Ergon, Terma
3. **Use minimal injection for utility CIs** - Rhetor, Hermes
4. **Let Sophia remember everything** - She's the memory specialist
5. **Monitor metrics** - Track memory usage and effectiveness
6. **Share successful patterns** - Through tribal memory

## Testing Memory Integration

Run comprehensive tests:
```bash
# Basic functionality
python tests/test_memory_integration.py --test basic --ci ergon

# Scenario testing
python tests/test_memory_integration.py --test scenario --scenario context_persistence

# A/B comparison
python tests/test_memory_integration.py --test ab --scenario pattern_recognition

# Training progression
python tests/test_memory_integration.py --test training
```

## Future Enhancements

- Cross-CI memory sharing
- Automatic memory optimization
- Visual memory graph interface
- Memory search and query tools
- Cultural memory emergence tracking