# Sophia

![Sophia](../../../images/icon.jpg)

Sophia is the machine learning and continuous improvement component of Tekton, designed to study CI collaboration, measure intelligence dimensions, and enable self-enhancement across components.

## Overview

Sophia serves as the scientific foundation for the Tekton ecosystem, providing metrics collection, analysis, and intelligence measurement capabilities that support continuous learning and improvement. It implements the intelligence dimensions framework for measuring CI cognitive capabilities and provides tools for conducting scientific experiments on CI collaboration.

## Key Features

- **Metrics Collection and Analysis**: Comprehensive collection, storage, and analysis of performance and behavioral metrics across all Tekton components
- **Experiment Framework**: Design, execution, and analysis of controlled experiments to validate improvement hypotheses
- **Intelligence Measurement**: Structured framework for measuring CI cognitive capabilities across multiple dimensions
- **Recommendation System**: Generation and tracking of improvement suggestions based on analysis and experiments
- **Component Analysis**: Performance analysis of individual components and their interactions
- **Research Capabilities**: Advanced research tools including Computational Spectral Analysis (CSA) and Catastrophe Theory (CT) for neural network analysis

## Architecture

Sophia follows a modular architecture with:

1. **Core Engines**:
   - Metrics Engine: For collecting, storing, and querying metrics
   - Analysis Engine: For pattern detection, anomaly detection, and trend analysis
   - Experiment Framework: For designing and running controlled experiments
   - Recommendation System: For generating and tracking improvement suggestions
   - Intelligence Measurement: For measuring and comparing CI cognitive capabilities
   - ML Engine: For machine learning operations and component analysis

2. **API Layer**:
   - RESTful API with FastAPI following Single Port Architecture
   - WebSocket support for real-time updates
   - Comprehensive endpoints for all capabilities

3. **Integrations**:
   - Hermes: For service discovery and registration
   - Engram: For persistent memory storage
   - Prometheus: For planning integration

4. **UI Components**:
   - Dashboard for visualizing metrics and intelligence profiles
   - Experiment management interface
   - Recommendation tracking

## Intelligence Dimensions Framework

Sophia implements a comprehensive framework for measuring CI intelligence across 10 dimensions:

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

## Requirements

- Python 3.9+
- FastAPI
- httpx
- pydantic
- websockets
- asyncio
- numpy
- scikit-learn (optional, for advanced analyses)