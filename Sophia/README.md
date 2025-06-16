# Sophia

Sophia is the machine learning and continuous improvement component of Tekton, designed to study AI collaboration, measure intelligence dimensions, and enable self-enhancement across components.

## Overview

Sophia serves as the scientific foundation for the Tekton ecosystem, providing metrics collection, analysis, and intelligence measurement capabilities that support continuous learning and improvement. It implements the intelligence dimensions framework for measuring AI cognitive capabilities and provides tools for conducting scientific experiments on AI collaboration.

## Key Features

- **Metrics Collection and Analysis**: Comprehensive collection, storage, and analysis of performance and behavioral metrics across all Tekton components
- **Experiment Framework**: Design, execution, and analysis of controlled experiments to validate improvement hypotheses
- **Intelligence Measurement**: Structured framework for measuring AI cognitive capabilities across multiple dimensions
- **Recommendation System**: Generation and tracking of improvement suggestions based on analysis and experiments
- **Component Analysis**: Performance analysis of individual components and their interactions
- **Research Capabilities**: Advanced research tools including Computational Spectral Analysis (CSA) and Catastrophe Theory (CT) for neural network analysis
- **MCP Integration**: Model Context Protocol integration with 16 specialized tools and advanced workflows

## Architecture

Sophia follows a modular architecture with:

1. **Core Engines**:
   - Metrics Engine: For collecting, storing, and querying metrics
   - Analysis Engine: For pattern detection, anomaly detection, and trend analysis
   - Experiment Framework: For designing and running controlled experiments
   - Recommendation System: For generating and tracking improvement suggestions
   - Intelligence Measurement: For measuring and comparing AI cognitive capabilities
   - ML Engine: For machine learning operations and component analysis

2. **API Layer**:
   - RESTful API with FastAPI following Single Port Architecture
   - WebSocket support for real-time updates
   - Comprehensive endpoints for all capabilities

3. **Integrations**:
   - Hermes: For service discovery and registration
   - Engram: For persistent memory storage
   - Prometheus: For planning integration
   - FastMCP: For Model Context Protocol integration

4. **UI Components**:
   - Dashboard for visualizing metrics and intelligence profiles
   - Experiment management interface
   - Recommendation tracking

## Intelligence Dimensions Framework

Sophia implements a comprehensive framework for measuring AI intelligence across 10 dimensions:

1. **Language Processing**: Understanding, interpreting, and generating human language
2. **Reasoning**: Making inferences, deductions, and logical arguments
3. **Knowledge**: Factual information and domain expertise
4. **Learning**: Acquiring new information and adapting from experience
5. **Creativity**: Generating novel, valuable, and surprising outputs
6. **Planning**: Formulating goals and strategies to achieve them
7. **Problem Solving**: Identifying, analyzing, and resolving challenges
8. **Adaptation**: Adjusting behavior based on changing conditions
9. **Collaboration**: Working effectively with other agents or humans
10. **Metacognition**: Awareness and control of one's own thought processes

Each dimension is measured through multiple metrics and can be used to create intelligence profiles for components or the entire ecosystem.

## Experiment Framework

Sophia provides a comprehensive experiment framework supporting multiple experiment types:

- **A/B Testing**: Compare two variants to determine which performs better
- **Multivariate Testing**: Test multiple variables simultaneously
- **Canary Deployments**: Gradually roll out changes to a subset of users
- **Shadow Mode Testing**: Run a new implementation alongside the current one
- **Parameter Tuning**: Find optimal values for configurable parameters
- **Before/After Testing**: Compare metrics before and after a change
- **Baseline Comparisons**: Compare multiple candidates against a baseline

The framework handles experiment design, execution, data collection, and analysis, providing insights and recommendations based on results.

## Quick Start

```bash
# Install dependencies
./setup.sh

# Run the service with the unified launcher
./scripts/tekton-launch --components sophia

# Or run with custom port
SOPHIA_PORT=8006 ./scripts/tekton-launch --components sophia

# Register with Hermes
./register_with_hermes.py
```

## Client Usage

Sophia provides a Python client for easy interaction with the API:

```python
from sophia.client import SophiaClient
import asyncio

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