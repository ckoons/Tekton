# Engram Data Streaming Integration

This document describes the integration between Noesis and Engram for real-time memory state analysis.

## Overview

Noesis now includes a comprehensive data streaming system that connects to Engram to observe memory state evolution in real-time. This enables theoretical analysis of collective intelligence patterns, memory dynamics, and cognitive state transitions.

## Architecture

### Core Components

1. **EngramDataStreamer**: Polls Engram for memory state updates
2. **NoesisMemoryAnalyzer**: Performs theoretical analysis on memory data
3. **TheoreticalStreamManager**: Coordinates streaming and analysis
4. **NoesisComponent**: Integrates streaming into the main component

### Data Flow

```
Engram Memory System
       ↓ (HTTP polling)
EngramDataStreamer
       ↓ (memory states & events)
NoesisMemoryAnalyzer
       ↓ (theoretical analysis)
TheoreticalStreamManager
       ↓ (insights & patterns)
API Endpoints
```

## Features

### Memory State Analysis

- **State Vectorization**: Converts memory states to numerical vectors for analysis
- **Event Detection**: Identifies thought creation, refinement, and state transitions
- **Pattern Recognition**: Detects multi-dimensional patterns in memory evolution
- **Dynamics Analysis**: Analyzes memory system stability and attractors
- **Catastrophe Detection**: Identifies phase transitions and bifurcations

### Theoretical Insights

The system generates insights about:
- Memory manifold dimensionality and curvature
- Dynamic stability and attractors
- Phase transitions and critical points
- Event patterns and cognitive rhythms
- Collective intelligence emergence

### Real-time Streaming

- **Configurable Polling**: Adjustable poll intervals (default: 5 seconds)
- **Event-driven Updates**: Immediate analysis of memory events
- **Historical Tracking**: Maintains history of memory states and analysis
- **Error Recovery**: Graceful handling of connection issues

## Configuration

### Stream Manager Configuration

```python
stream_config = {
    "engram": {
        "url": "http://localhost:8003",  # Engram URL
        "poll_interval": 5.0             # Seconds between polls
    }
}
```

### Auto-start Configuration

Set `auto_start_streaming: true` in Noesis configuration to automatically start streaming on component initialization.

## API Endpoints

### Streaming Control

- `GET /streaming/status` - Get streaming status
- `POST /streaming/start` - Start streaming
- `POST /streaming/stop` - Stop streaming
- `GET /streaming/health` - Health check

### Analysis Results

- `GET /streaming/insights` - Get theoretical insights
- `GET /streaming/memory/analysis` - Get memory analysis
- `GET /streaming/memory/history` - Get historical data
- `GET /streaming/memory/current` - Get current memory state
- `GET /streaming/statistics` - Get streaming statistics

### Force Operations

- `POST /streaming/memory/force-poll` - Force immediate poll
- `POST /streaming/analysis/update` - Force analysis update

## Memory State Format

### MemoryState Object

```python
@dataclass
class MemoryState:
    timestamp: datetime
    component_id: str
    latent_spaces: Dict[str, Any]        # Latent space structures
    thought_states: Dict[str, str]       # thought_id -> state
    memory_metrics: Dict[str, float]     # Numerical metrics
    attention_weights: List[float]       # Attention distribution
    activity_levels: Dict[str, float]    # Activity rates
    metadata: Dict[str, Any]             # Additional data
```

### Memory Events

- `thought_created` - New thought initialized
- `thought_refined` - Thought iteration added
- `state_transition` - Thought state changed
- `thought_removed` - Thought disappeared

## Theoretical Analysis

### Manifold Analysis

- **Intrinsic Dimensionality**: Estimates the true dimensionality of memory states
- **Curvature Analysis**: Measures manifold curvature to understand geometry
- **Topology Detection**: Identifies topological features of the memory space

### Dynamics Analysis

- **Stability Analysis**: Determines system stability and equilibrium points
- **Attractor Detection**: Identifies stable configurations
- **Flow Analysis**: Studies memory state evolution patterns

### Catastrophe Analysis

- **Phase Transitions**: Detects sudden changes in memory organization
- **Bifurcations**: Identifies points where behavior qualitatively changes
- **Critical Points**: Finds parameters where small changes have large effects

## Example Usage

### Programmatic Access

```python
from noesis.core.noesis_component import NoesisComponent

# Initialize component
component = NoesisComponent()
await component.init()

# Start streaming
await component.start_streaming()

# Get insights
insights = await component.get_theoretical_insights()
print(f"Found {len(insights['insights'])} insights")

# Get analysis
analysis = await component.get_memory_analysis()
print(f"Memory observations: {analysis['memory_statistics']['total_observations']}")

# Stop streaming
await component.stop_streaming()
```

### API Access

```bash
# Start streaming
curl -X POST http://localhost:8005/streaming/start

# Get insights
curl http://localhost:8005/streaming/insights

# Get current status
curl http://localhost:8005/streaming/status

# Stop streaming
curl -X POST http://localhost:8005/streaming/stop
```

## Testing

Run the integration test:

```bash
cd Noesis
python test_engram_streaming.py
```

This will test:
- Basic streaming components
- Memory analysis functionality
- Component integration
- API endpoint availability

## Dependencies

Required packages:
- `numpy` - Numerical computing
- `scipy` - Scientific computing
- `httpx` - HTTP client
- `scikit-learn` - Machine learning (optional, with fallbacks)

## Error Handling

The system includes comprehensive error handling:
- **Connection Failures**: Graceful degradation when Engram is unavailable
- **Analysis Errors**: Fallback to simpler analysis methods
- **Data Validation**: Input validation and sanitization
- **Recovery**: Automatic retry with exponential backoff

## Performance

- **Streaming Overhead**: Minimal impact on Engram (polling-based)
- **Memory Usage**: Bounded history with automatic cleanup
- **Analysis Speed**: Real-time analysis for typical memory states
- **Scalability**: Designed for continuous operation

## Future Enhancements

Planned improvements:
- WebSocket-based streaming for real-time updates
- Advanced pattern recognition algorithms
- Integration with other Tekton components
- Predictive modeling of memory evolution
- Visualization dashboard for memory dynamics

## Troubleshooting

### Common Issues

1. **Import Errors**: Install required dependencies
2. **Connection Failed**: Check Engram URL and availability
3. **No Data**: Verify Engram has active memory states
4. **Analysis Errors**: Check for valid numerical data

### Debug Mode

Enable debug logging:
```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

### Health Checks

Use the health endpoint to diagnose issues:
```bash
curl http://localhost:8005/streaming/health
```

This provides detailed status of all streaming components.