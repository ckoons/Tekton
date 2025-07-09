# Sophia

## Overview

Sophia is the machine learning and continuous improvement component for the Tekton ecosystem. It provides scientific measurement of AI intelligence across multiple dimensions, conducts controlled experiments for system optimization, and enables continuous self-improvement through data-driven insights and recommendations.

## Key Features

- **Metrics Collection and Analysis**: Comprehensive collection, storage, and analysis of performance and behavioral metrics across all Tekton components
- **Experiment Framework**: Design, execution, and analysis of controlled experiments to validate improvement hypotheses
- **Intelligence Measurement**: Structured framework for measuring AI cognitive capabilities across multiple dimensions
- **Recommendation System**: Generation and tracking of improvement suggestions based on analysis and experiments
- **Component Analysis**: Performance analysis of individual components and their interactions
- **Research Capabilities**: Advanced research tools including Computational Spectral Analysis (CSA) and Catastrophe Theory (CT) for neural network analysis
- **MCP Integration**: Model Context Protocol integration with 16 specialized tools and advanced workflows

## Quick Start

```bash
# Install Sophia
cd Sophia
pip install -e .

# Start the Sophia server
python -m sophia.api.app
# Or use the launch script
./scripts/tekton-launch --components sophia

# Use the CLI
sophia metrics collect --all
sophia experiment create "LLM Response Time"
sophia intelligence measure --component rhetor
```

## Configuration

### Environment Variables

```bash
# Sophia-specific settings
SOPHIA_PORT=8009                      # API port
SOPHIA_AI_PORT=45009                  # AI specialist port
SOPHIA_METRICS_RETENTION_DAYS=90      # Metrics retention period
SOPHIA_EXPERIMENT_TIMEOUT=3600        # Experiment timeout (seconds)

# Analysis settings
SOPHIA_ANOMALY_THRESHOLD=3.0          # Standard deviations for anomaly
SOPHIA_TREND_WINDOW=7                 # Days for trend analysis
SOPHIA_CONFIDENCE_LEVEL=0.95          # Statistical confidence
```

### Configuration File

Create `.env.sophia` for persistent settings:

```bash
# Intelligence measurement
ENABLE_CONTINUOUS_PROFILING=true
PROFILE_UPDATE_INTERVAL=3600
INTELLIGENCE_BENCHMARK_VERSION=2.0

# Experiment settings
DEFAULT_EXPERIMENT_DURATION=86400
MIN_SAMPLE_SIZE=100
ENABLE_AUTO_EXPERIMENTS=true
```

## API Reference

### REST API Endpoints

#### Metrics
- `POST /api/metrics` - Record new metrics
- `GET /api/metrics/query` - Query metrics with filters
- `GET /api/metrics/analyze` - Analyze metrics patterns
- `GET /api/metrics/anomalies` - Detect anomalies

#### Experiments
- `POST /api/experiments` - Create new experiment
- `GET /api/experiments` - List experiments
- `POST /api/experiments/{id}/start` - Start experiment
- `POST /api/experiments/{id}/stop` - Stop experiment
- `GET /api/experiments/{id}/results` - Get results

#### Intelligence Measurement
- `POST /api/intelligence/measure` - Measure intelligence
- `GET /api/intelligence/profiles` - Get profiles
- `GET /api/intelligence/compare` - Compare components
- `GET /api/intelligence/trends` - Intelligence trends

#### Recommendations
- `GET /api/recommendations` - Get recommendations
- `POST /api/recommendations/{id}/implement` - Track implementation
- `GET /api/recommendations/impact` - Measure impact

### WebSocket Endpoints

- `/ws/metrics` - Real-time metrics stream
- `/ws/experiments` - Experiment updates
- `/ws/alerts` - Anomaly alerts

For detailed API documentation, run the server and visit `/docs`.

## Integration Points

Sophia seamlessly integrates with:

- **All Components**: Collects metrics from every Tekton component
- **Hermes**: Service registration and health monitoring
- **Engram**: Stores historical data and intelligence profiles
- **Prometheus**: Provides insights for strategic planning
- **AI Specialists**: Sophia AI analyzes patterns and suggests improvements

### Example Integration

```python
from sophia.client import SophiaClient
import asyncio

async def main():
    client = SophiaClient(host="localhost", port=8009)
    
    # Measure component intelligence
    profile = await client.measure_intelligence(
        component="rhetor",
        dimensions=["language_processing", "reasoning", "creativity"]
    )
    
    print(f"Rhetor Intelligence Profile:")
    for dim, score in profile.scores.items():
        print(f"  {dim}: {score:.2f}/10")
    
    # Create and run experiment
    experiment = await client.create_experiment(
        name="Prompt Optimization",
        type="ab_test",
        hypothesis="Structured prompts improve response quality",
        metrics=["response_quality", "token_efficiency"]
    )
    
    await client.start_experiment(experiment.id)
    
    # Record metrics
    await client.record_metric(
        name="response_quality",
        value=0.85,
        component="rhetor",
        tags={"variant": "structured", "experiment": experiment.id}
    )
    
    # Get recommendations
    recommendations = await client.get_recommendations(
        component="rhetor",
        category="performance"
    )
    
    for rec in recommendations:
        print(f"Recommendation: {rec.title}")
        print(f"  Impact: {rec.expected_impact}")
        print(f"  Effort: {rec.implementation_effort}")

asyncio.run(main())
```

## Intelligence Dimensions

Sophia measures AI intelligence across 10 key dimensions:

1. **Language Processing** - Natural language understanding and generation
2. **Reasoning** - Logical inference and deduction capabilities
3. **Knowledge** - Factual information and domain expertise
4. **Learning** - Ability to acquire and apply new information
5. **Creativity** - Generation of novel and valuable outputs
6. **Planning** - Strategic thinking and goal formulation
7. **Problem Solving** - Challenge identification and resolution
8. **Adaptation** - Behavioral adjustment to new conditions
9. **Collaboration** - Effective teamwork with humans and AIs
10. **Metacognition** - Self-awareness and thought process control

## Troubleshooting

### Common Issues

#### 1. Metrics Storage Full
**Symptoms**: Cannot record new metrics

**Solutions**:
```bash
# Check storage usage
sophia metrics storage --status

# Clean old metrics
sophia metrics clean --older-than 90d

# Adjust retention policy
export SOPHIA_METRICS_RETENTION_DAYS=30
```

#### 2. Experiment Not Converging
**Symptoms**: Experiment runs indefinitely without results

**Solutions**:
```bash
# Check experiment status
sophia experiment status <experiment-id>

# Adjust sample size
sophia experiment update <experiment-id> --min-samples 50

# Force analysis
sophia experiment analyze <experiment-id> --force
```

#### 3. Intelligence Measurement Errors
**Symptoms**: Cannot measure component intelligence

**Solutions**:
```bash
# Verify component is running
sophia component check <component-name>

# Reset intelligence cache
sophia intelligence reset --component <name>

# Run diagnostic
sophia diagnose intelligence
```

### Performance Tuning

- Use appropriate metric sampling rates
- Enable metric aggregation for high-volume data
- Configure retention policies based on needs
- Use async operations for bulk metrics

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=sophia tests/

# Run specific test category
pytest tests/unit/
pytest tests/integration/
```

### Debug Mode

```bash
# Enable debug logging
export SOPHIA_DEBUG=true
export SOPHIA_LOG_LEVEL=DEBUG

# Run with verbose output
python -m sophia.api.app --debug
```

### Adding New Intelligence Dimensions

1. Define dimension in `sophia/intelligence/dimensions.py`
2. Create measurement methods in `sophia/intelligence/measures/`
3. Add validation rules
4. Create benchmark tests
5. Update documentation

## Related Documentation

- [Intelligence Measurement Guide](/MetaData/ComponentDocumentation/Sophia/INTELLIGENCE_GUIDE.md)
- [Experiment Framework](/MetaData/ComponentDocumentation/Sophia/EXPERIMENTS.md)
- [Metrics Analysis](/MetaData/ComponentDocumentation/Sophia/METRICS_GUIDE.md)
- [API Reference](/Sophia/docs/api_reference.md)

async def example():
    # Create client
    client = SophiaClient(base_url="http://localhost:8006")
    
    try:
        # Check availability
        if await client.is_available():
            # Submit a metric
            await client.submit_metric(
                metric_id="component.performance.latency",
                value=42.5,
                source="my_component",
                tags=["performance", "latency"]
            )
            
            # Query metrics
            metrics = await client.query_metrics(
                metric_id="component.performance.latency",
                source="my_component",
                limit=10
            )
            
            # Create an experiment
            experiment_id = await client.create_experiment(
                name="Latency Optimization",
                description="Testing a new algorithm to reduce latency",
                experiment_type="a_b_test",
                target_components=["my_component"],
                hypothesis="The new algorithm reduces latency by 20%",
                metrics=["component.performance.latency"],
                parameters={
                    "control": {"algorithm": "current"},
                    "treatment": {"algorithm": "new"}
                }
            )
            
            # Get intelligence profile
            profile = await client.get_component_intelligence_profile("my_component")
            
            # Compare components
            comparison = await client.compare_intelligence_profiles(
                component_ids=["component_a", "component_b"],
                dimensions=["language_processing", "reasoning"]
            )
    finally:
        # Close client
        await client.close()

# Run the example
asyncio.run(example())
```

## API Endpoints

Sophia provides a comprehensive API following the Single Port Architecture pattern:

### Metrics API

- `POST /api/metrics` - Submit a metric
- `GET /api/metrics` - Query metrics
- `POST /api/metrics/aggregate` - Aggregate metrics
- `GET /api/metrics/definitions` - Get metric definitions

### Experiments API

- `POST /api/experiments` - Create an experiment
- `GET /api/experiments` - Query experiments
- `GET /api/experiments/{id}` - Get experiment details
- `PUT /api/experiments/{id}` - Update an experiment
- `POST /api/experiments/{id}/start` - Start an experiment
- `POST /api/experiments/{id}/stop` - Stop an experiment
- `POST /api/experiments/{id}/analyze` - Analyze experiment results
- `GET /api/experiments/{id}/results` - Get experiment results

### Recommendations API

- `POST /api/recommendations` - Create a recommendation
- `GET /api/recommendations` - Query recommendations
- `GET /api/recommendations/{id}` - Get recommendation details
- `PUT /api/recommendations/{id}` - Update a recommendation
- `POST /api/recommendations/{id}/status/{status}` - Update recommendation status
- `POST /api/recommendations/{id}/verify` - Verify recommendation implementation

### Intelligence API

- `POST /api/intelligence/measurements` - Record an intelligence measurement
- `GET /api/intelligence/measurements` - Query intelligence measurements
- `GET /api/intelligence/components/{id}/profile` - Get component intelligence profile
- `POST /api/intelligence/components/compare` - Compare component intelligence profiles
- `GET /api/intelligence/dimensions` - Get intelligence dimensions
- `GET /api/intelligence/dimensions/{dimension}` - Get intelligence dimension details
- `GET /api/intelligence/ecosystem/profile` - Get ecosystem intelligence profile

### Components API

- `POST /api/components/register` - Register a component
- `GET /api/components` - Query components
- `GET /api/components/{id}` - Get component details
- `PUT /api/components/{id}` - Update a component
- `GET /api/components/{id}/performance` - Analyze component performance
- `POST /api/components/interaction` - Analyze component interactions

### Research API

- `POST /api/research/projects` - Create a research project
- `GET /api/research/projects` - Query research projects
- `GET /api/research/projects/{id}` - Get project details
- `PUT /api/research/projects/{id}` - Update a research project

### MCP API

Sophia provides Model Context Protocol integration with 16 specialized tools:

#### ML/AI Analysis Tools (6 tools)
- `POST /mcp/tools/analyze_component_performance` - Analyze component performance using ML
- `POST /mcp/tools/extract_patterns` - Extract behavioral patterns from data
- `POST /mcp/tools/predict_optimization_impact` - Predict optimization impact
- `POST /mcp/tools/design_ml_experiment` - Design ML experiments
- `POST /mcp/tools/analyze_ecosystem_trends` - Analyze ecosystem-wide trends
- `POST /mcp/tools/forecast_system_evolution` - Forecast system evolution

#### Research Management Tools (6 tools)
- `POST /mcp/tools/create_research_project` - Create research projects
- `POST /mcp/tools/manage_experiment_lifecycle` - Manage experiment lifecycle
- `POST /mcp/tools/validate_optimization_results` - Validate optimization results
- `POST /mcp/tools/generate_research_recommendations` - Generate research recommendations
- `POST /mcp/tools/track_research_progress` - Track research progress
- `POST /mcp/tools/synthesize_research_findings` - Synthesize research findings

#### Intelligence Measurement Tools (4 tools)
- `POST /mcp/tools/measure_component_intelligence` - Measure component intelligence
- `POST /mcp/tools/compare_intelligence_profiles` - Compare intelligence profiles
- `POST /mcp/tools/track_intelligence_evolution` - Track intelligence evolution
- `POST /mcp/tools/generate_intelligence_insights` - Generate intelligence insights

#### Advanced Workflows
- `POST /mcp/workflows/complete_research_analysis` - Complete research analysis workflow
- `POST /mcp/workflows/intelligence_assessment` - Intelligence assessment workflow
- `POST /mcp/workflows/component_optimization` - Component optimization workflow
- `POST /mcp/workflows/trend_analysis` - Advanced trend analysis workflow

### WebSocket Connection

- `/ws` - WebSocket connection for real-time updates

## Integration with Hermes

Sophia registers with Hermes to participate in the Tekton ecosystem:

1. Component Registration:
   - Registers as "sophia" component
   - Provides capabilities including "metrics", "experiments", "intelligence", etc.
   - Specifies API endpoints for all services

2. Dependency Handling:
   - Depends on Hermes for service discovery
   - Optional dependencies on Engram for memory integration
   - Optional dependencies on Prometheus for planning integration

## Documentation

- [Implementation Status](./IMPLEMENTATION_STATUS.md): Current implementation status
- [MCP Integration](./MCP_INTEGRATION.md): Model Context Protocol integration with 16 tools and workflows
- [Sophia Architecture](../docs/SOPHIA_ARCHITECTURE.md): Detailed architecture design
- [Intelligence Dimensions](../docs/SOPHIA_INTELLIGENCE_DIMENSIONS.md): Framework for measuring AI intelligence
- [LLM Integration](../docs/SOPHIA_LLM_INTEGRATION.md): Integration with language models
- [Metrics Specification](../docs/SOPHIA_METRICS_SPECIFICATION.md): Metrics collection and analysis

## Development

Sophia is under active development. See [Implementation Status](./IMPLEMENTATION_STATUS.md) for current progress and next steps.

## Requirements

- Python 3.9+
- FastAPI
- httpx
- pydantic
- websockets
- asyncio
- numpy
- scikit-learn (optional, for advanced analyses)

## License

See the LICENSE file for details.