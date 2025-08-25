# Ollama Configuration for Tekton AI Platform

## Overview
Ollama is the LLM backend for Tekton's Greek Chorus AIs. Proper configuration is essential for handling multiple concurrent AI connections.

## Key Configuration Parameters

### 1. Parallel Connections (CRITICAL)
```bash
# Default: 2 (too low for Tekton)
# Recommended: 4-8 depending on system resources
export OLLAMA_NUM_PARALLEL=4
```

**Why this matters**: With 18 AIs in Tekton, the default of 2 parallel connections creates a severe bottleneck. AIs will timeout waiting for their turn.

### 2. Maximum Loaded Models
```bash
# Controls how many models can be loaded in memory simultaneously
export OLLAMA_MAX_LOADED_MODELS=2
```

**Note**: Loading multiple models requires significant RAM. Monitor memory usage.

### 3. Keep Alive Duration
```bash
# How long to keep models loaded after last use
export OLLAMA_KEEP_ALIVE=30m  # 30 minutes
```

**Trade-off**: Longer = faster responses, but more memory usage.

## Recommended Configurations

### For Development (Limited Resources)
```bash
export OLLAMA_NUM_PARALLEL=4
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_KEEP_ALIVE=5m

ollama serve
```

### For Production (Ample Resources)
```bash
export OLLAMA_NUM_PARALLEL=8
export OLLAMA_MAX_LOADED_MODELS=3
export OLLAMA_KEEP_ALIVE=60m
export OLLAMA_HOST=0.0.0.0:11434  # If serving remotely

ollama serve
```

### For Testing All AIs
```bash
# Maximum parallelism for team-chat scenarios
export OLLAMA_NUM_PARALLEL=10
export OLLAMA_MAX_LOADED_MODELS=2

ollama serve
```

## Monitoring and Troubleshooting

### Check Current Connections
```bash
# See active models and connections
curl http://localhost:11434/api/ps | jq

# Count current connections
ps aux | grep ollama | grep runner | wc -l
```

### Common Issues

1. **"Connection refused" errors**
   - Ollama not running: `ollama serve`
   - Port conflict: Check if 11434 is in use

2. **Timeouts with team-chat**
   - Increase OLLAMA_NUM_PARALLEL
   - Check system resources (RAM/CPU)

3. **Memory errors**
   - Reduce OLLAMA_MAX_LOADED_MODELS
   - Use smaller models (e.g., 7B instead of 70B)
   - Decrease OLLAMA_KEEP_ALIVE

## Restarting Ollama

```bash
# Full restart with new configuration
killall ollama  # or pkill ollama

# Start with new settings
OLLAMA_NUM_PARALLEL=6 ollama serve
```

## Integration with Tekton's Message Queue

The new AI service architecture (one queue per AI) helps manage Ollama's limitations:
- Requests are naturally serialized per AI
- Prevents connection storms
- Allows graceful queueing when Ollama is busy

## Best Practices

1. **Start conservative**: Begin with OLLAMA_NUM_PARALLEL=4 and increase as needed
2. **Monitor resources**: Use `htop` or Activity Monitor while running team-chat
3. **Model selection**: Use appropriate model sizes for your hardware
4. **Restart periodically**: Ollama can accumulate memory over time

## Quick Reference

```bash
# Check if Ollama is healthy
curl http://localhost:11434/api/tags

# See current configuration (in process list)
ps aux | grep ollama | grep serve

# Test with single AI
echo "test" | nc localhost 45012  # Apollo's port

# Restart with optimal settings for Tekton
killall ollama
OLLAMA_NUM_PARALLEL=6 OLLAMA_KEEP_ALIVE=15m ollama serve
```

---

*Note: These recommendations are based on running 18 concurrent AIs in the Tekton platform. Adjust based on your specific hardware and usage patterns.*