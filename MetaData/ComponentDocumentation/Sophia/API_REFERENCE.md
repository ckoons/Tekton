# Sophia API Reference

This document provides a detailed reference for the Sophia API, following the Single Port Architecture pattern on port 8006.

## Base URL

All API endpoints are accessible under the base URL:

```
http://<host>:8006/api/
```

## Authentication

All API endpoints require authentication using the Tekton authentication system. Include the authentication token in the `Authorization` header:

```
Authorization: Bearer <token>
```

## REST API Endpoints

### Metrics API

#### Submit Metric

```
POST /api/metrics
```

Submits a new metric data point.

**Request Body:**

```json
{
  "metric_id": "component.performance.latency",
  "value": 42.5,
  "source": "my_component",
  "tags": ["performance", "latency"],
  "timestamp": "2025-05-01T10:15:30Z",
  "metadata": {
    "environment": "production",
    "instance": "worker-1"
  }
}
```

**Response:**

```json
{
  "id": "m1e2t3r4-5i6c7-8i9d0",
  "metric_id": "component.performance.latency",
  "value": 42.5,
  "source": "my_component",
  "tags": ["performance", "latency"],
  "timestamp": "2025-05-01T10:15:30Z",
  "recorded_at": "2025-05-01T10:15:30.123Z"
}
```

#### Query Metrics

```
GET /api/metrics
```

Queries metrics data with optional filtering.

**Query Parameters:**

- `metric_id` - Filter by metric ID (e.g., "component.performance.latency")
- `source` - Filter by source (e.g., "my_component")
- `tag` - Filter by tag (can be specified multiple times)
- `from_date` - Filter by timestamp (from)
- `to_date` - Filter by timestamp (to)
- `limit` - Maximum number of results to return (default: 100)
- `offset` - Offset for pagination (default: 0)

**Response:**

```json
{
  "total": 42,
  "offset": 0,
  "limit": 100,
  "metrics": [
    {
      "id": "m1e2t3r4-5i6c7-8i9d0",
      "metric_id": "component.performance.latency",
      "value": 42.5,
      "source": "my_component",
      "tags": ["performance", "latency"],
      "timestamp": "2025-05-01T10:15:30Z",
      "recorded_at": "2025-05-01T10:15:30.123Z",
      "metadata": {
        "environment": "production",
        "instance": "worker-1"
      }
    }
  ]
}
```

#### Aggregate Metrics

```
POST /api/metrics/aggregate
```

Aggregates metrics data.

**Request Body:**

```json
{
  "metric_id": "component.performance.latency",
  "source": "my_component",
  "tags": ["performance"],
  "from_date": "2025-05-01T00:00:00Z",
  "to_date": "2025-05-02T00:00:00Z",
  "aggregation": "avg",
  "group_by": ["source", "hour"]
}
```

**Response:**

```json
{
  "aggregation": "avg",
  "metric_id": "component.performance.latency",
  "from_date": "2025-05-01T00:00:00Z",
  "to_date": "2025-05-02T00:00:00Z",
  "groups": [
    {
      "keys": {
        "source": "my_component",
        "hour": "2025-05-01T10:00:00Z"
      },
      "value": 42.5,
      "count": 10
    },
    {
      "keys": {
        "source": "my_component",
        "hour": "2025-05-01T11:00:00Z"
      },
      "value": 45.2,
      "count": 12
    }
  ]
}
```

#### Get Metric Definitions

```
GET /api/metrics/definitions
```

Gets all metric definitions.

**Response:**

```json
{
  "definitions": [
    {
      "metric_id": "component.performance.latency",
      "name": "Component Latency",
      "description": "Latency of a component operation in milliseconds",
      "unit": "ms",
      "type": "gauge",
      "tags": ["performance", "latency"]
    },
    {
      "metric_id": "component.performance.throughput",
      "name": "Component Throughput",
      "description": "Throughput of a component operation in requests per second",
      "unit": "rps",
      "type": "gauge",
      "tags": ["performance", "throughput"]
    }
  ]
}
```

### Experiments API

#### Create Experiment

```
POST /api/experiments
```

Creates a new experiment.

**Request Body:**

```json
{
  "name": "Latency Optimization",
  "description": "Testing a new algorithm to reduce latency",
  "experiment_type": "a_b_test",
  "target_components": ["my_component"],
  "hypothesis": "The new algorithm reduces latency by 20%",
  "metrics": ["component.performance.latency"],
  "parameters": {
    "control": {
      "algorithm": "current"
    },
    "treatment": {
      "algorithm": "new"
    }
  },
  "tags": ["optimization", "performance"]
}
```

**Response:**

```json
{
  "experiment_id": "e1x2p3-4e5r6i7m8e9n0t1",
  "name": "Latency Optimization",
  "description": "Testing a new algorithm to reduce latency",
  "experiment_type": "a_b_test",
  "target_components": ["my_component"],
  "hypothesis": "The new algorithm reduces latency by 20%",
  "metrics": ["component.performance.latency"],
  "parameters": {
    "control": {
      "algorithm": "current"
    },
    "treatment": {
      "algorithm": "new"
    }
  },
  "status": "created",
  "created_at": "2025-05-01T10:15:30Z",
  "tags": ["optimization", "performance"]
}
```

#### Query Experiments

```
GET /api/experiments
```

Queries experiments with optional filtering.

**Query Parameters:**

- `experiment_type` - Filter by experiment type (e.g., "a_b_test")
- `status` - Filter by status (e.g., "active", "completed")
- `target_component` - Filter by target component
- `tag` - Filter by tag (can be specified multiple times)
- `from_date` - Filter by creation date (from)
- `to_date` - Filter by creation date (to)
- `limit` - Maximum number of results to return (default: 50)
- `offset` - Offset for pagination (default: 0)

**Response:**

```json
{
  "total": 5,
  "offset": 0,
  "limit": 50,
  "experiments": [
    {
      "experiment_id": "e1x2p3-4e5r6i7m8e9n0t1",
      "name": "Latency Optimization",
      "description": "Testing a new algorithm to reduce latency",
      "experiment_type": "a_b_test",
      "target_components": ["my_component"],
      "status": "created",
      "created_at": "2025-05-01T10:15:30Z",
      "tags": ["optimization", "performance"]
    }
  ]
}
```

#### Get Experiment Details

```
GET /api/experiments/{id}
```

Gets detailed information about a specific experiment.

**Path Parameters:**

- `id` - The ID of the experiment to retrieve

**Response:**

```json
{
  "experiment_id": "e1x2p3-4e5r6i7m8e9n0t1",
  "name": "Latency Optimization",
  "description": "Testing a new algorithm to reduce latency",
  "experiment_type": "a_b_test",
  "target_components": ["my_component"],
  "hypothesis": "The new algorithm reduces latency by 20%",
  "metrics": ["component.performance.latency"],
  "parameters": {
    "control": {
      "algorithm": "current"
    },
    "treatment": {
      "algorithm": "new"
    }
  },
  "status": "active",
  "created_at": "2025-05-01T10:15:30Z",
  "started_at": "2025-05-01T10:20:00Z",
  "tags": ["optimization", "performance"]
}
```

#### Start Experiment

```
POST /api/experiments/{id}/start
```

Starts an experiment.

**Path Parameters:**

- `id` - The ID of the experiment to start

**Response:**

```json
{
  "experiment_id": "e1x2p3-4e5r6i7m8e9n0t1",
  "status": "active",
  "started_at": "2025-05-01T10:20:00Z"
}
```

#### Stop Experiment

```
POST /api/experiments/{id}/stop
```

Stops an experiment.

**Path Parameters:**

- `id` - The ID of the experiment to stop

**Response:**

```json
{
  "experiment_id": "e1x2p3-4e5r6i7m8e9n0t1",
  "status": "completed",
  "stopped_at": "2025-05-08T10:20:00Z",
  "duration_hours": 168
}
```

#### Analyze Experiment Results

```
POST /api/experiments/{id}/analyze
```

Analyzes the results of an experiment.

**Path Parameters:**

- `id` - The ID of the experiment to analyze

**Response:**

```json
{
  "experiment_id": "e1x2p3-4e5r6i7m8e9n0t1",
  "analysis_id": "a1n2a3-4l5y6s7i8s9",
  "status": "in_progress",
  "started_at": "2025-05-08T10:25:00Z"
}
```

#### Get Experiment Results

```
GET /api/experiments/{id}/results
```

Gets the results of an experiment.

**Path Parameters:**

- `id` - The ID of the experiment to get results for

**Response:**

```json
{
  "experiment_id": "e1x2p3-4e5r6i7m8e9n0t1",
  "status": "completed",
  "metrics": [
    {
      "metric_id": "component.performance.latency",
      "control": {
        "mean": 52.3,
        "median": 50.1,
        "p95": 75.2,
        "sample_size": 1000
      },
      "treatment": {
        "mean": 42.8,
        "median": 40.5,
        "p95": 65.3,
        "sample_size": 1000
      },
      "difference": {
        "absolute": -9.5,
        "relative": -18.16,
        "p_value": 0.0001,
        "significant": true
      }
    }
  ],
  "conclusion": "The treatment showed an 18.16% reduction in latency, which is statistically significant (p < 0.001).",
  "recommendation": "Implement the new algorithm in production.",
  "analyzed_at": "2025-05-08T10:30:00Z"
}
```

### Recommendations API

#### Create Recommendation

```
POST /api/recommendations
```

Creates a new recommendation.

**Request Body:**

```json
{
  "title": "Optimize Query Performance",
  "description": "Replace string concatenation with parameterized queries for better performance and security",
  "target_components": ["database_service"],
  "justification": "Analysis shows 30% of CPU time is spent on query parsing",
  "expected_impact": "20% reduction in query latency, improved security",
  "effort_estimate": "medium",
  "priority": "high",
  "source": "experiment_analysis",
  "source_id": "e1x2p3-4e5r6i7m8e9n0t1",
  "tags": ["performance", "security"]
}
```

**Response:**

```json
{
  "recommendation_id": "r1e2c3-4o5m6m7e8n9d0",
  "title": "Optimize Query Performance",
  "description": "Replace string concatenation with parameterized queries for better performance and security",
  "target_components": ["database_service"],
  "justification": "Analysis shows 30% of CPU time is spent on query parsing",
  "expected_impact": "20% reduction in query latency, improved security",
  "effort_estimate": "medium",
  "priority": "high",
  "status": "open",
  "source": "experiment_analysis",
  "source_id": "e1x2p3-4e5r6i7m8e9n0t1",
  "created_at": "2025-05-08T11:00:00Z",
  "tags": ["performance", "security"]
}
```

#### Query Recommendations

```
GET /api/recommendations
```

Queries recommendations with optional filtering.

**Query Parameters:**

- `status` - Filter by status (e.g., "open", "implementing", "implemented")
- `target_component` - Filter by target component
- `priority` - Filter by priority (e.g., "high", "medium", "low")
- `tag` - Filter by tag (can be specified multiple times)
- `source` - Filter by source
- `limit` - Maximum number of results to return (default: 50)
- `offset` - Offset for pagination (default: 0)

**Response:**

```json
{
  "total": 12,
  "offset": 0,
  "limit": 50,
  "recommendations": [
    {
      "recommendation_id": "r1e2c3-4o5m6m7e8n9d0",
      "title": "Optimize Query Performance",
      "target_components": ["database_service"],
      "priority": "high",
      "status": "open",
      "created_at": "2025-05-08T11:00:00Z",
      "tags": ["performance", "security"]
    }
  ]
}
```

#### Get Recommendation Details

```
GET /api/recommendations/{id}
```

Gets detailed information about a specific recommendation.

**Path Parameters:**

- `id` - The ID of the recommendation to retrieve

**Response:**

```json
{
  "recommendation_id": "r1e2c3-4o5m6m7e8n9d0",
  "title": "Optimize Query Performance",
  "description": "Replace string concatenation with parameterized queries for better performance and security",
  "target_components": ["database_service"],
  "justification": "Analysis shows 30% of CPU time is spent on query parsing",
  "expected_impact": "20% reduction in query latency, improved security",
  "effort_estimate": "medium",
  "priority": "high",
  "status": "open",
  "source": "experiment_analysis",
  "source_id": "e1x2p3-4e5r6i7m8e9n0t1",
  "created_at": "2025-05-08T11:00:00Z",
  "tags": ["performance", "security"],
  "history": [
    {
      "status": "open",
      "timestamp": "2025-05-08T11:00:00Z",
      "comment": "Initial recommendation created from experiment analysis"
    }
  ]
}
```

#### Update Recommendation Status

```
POST /api/recommendations/{id}/status/{status}
```

Updates the status of a recommendation.

**Path Parameters:**

- `id` - The ID of the recommendation to update
- `status` - The new status (e.g., "open", "implementing", "implemented", "rejected")

**Request Body:**

```json
{
  "comment": "Starting implementation in sprint 23",
  "metadata": {
    "assigned_to": "team-alpha",
    "sprint": "23",
    "estimated_completion": "2025-05-20T00:00:00Z"
  }
}
```

**Response:**

```json
{
  "recommendation_id": "r1e2c3-4o5m6m7e8n9d0",
  "status": "implementing",
  "updated_at": "2025-05-09T09:00:00Z",
  "history": [
    {
      "status": "open",
      "timestamp": "2025-05-08T11:00:00Z",
      "comment": "Initial recommendation created from experiment analysis"
    },
    {
      "status": "implementing",
      "timestamp": "2025-05-09T09:00:00Z",
      "comment": "Starting implementation in sprint 23",
      "metadata": {
        "assigned_to": "team-alpha",
        "sprint": "23",
        "estimated_completion": "2025-05-20T00:00:00Z"
      }
    }
  ]
}
```

#### Verify Recommendation Implementation

```
POST /api/recommendations/{id}/verify
```

Verifies the implementation of a recommendation.

**Path Parameters:**

- `id` - The ID of the recommendation to verify

**Request Body:**

```json
{
  "verification_metrics": ["component.performance.latency"],
  "verification_period": {
    "from_date": "2025-05-20T00:00:00Z",
    "to_date": "2025-05-27T00:00:00Z"
  },
  "baseline_period": {
    "from_date": "2025-05-01T00:00:00Z",
    "to_date": "2025-05-08T00:00:00Z"
  },
  "expected_improvement": {
    "component.performance.latency": -20
  }
}
```

**Response:**

```json
{
  "recommendation_id": "r1e2c3-4o5m6m7e8n9d0",
  "verification_id": "v1e2r3-4i5f6y7",
  "status": "in_progress",
  "started_at": "2025-05-27T10:00:00Z"
}
```

### Intelligence API

#### Record Intelligence Measurement

```
POST /api/intelligence/measurements
```

Records an intelligence measurement.

**Request Body:**

```json
{
  "component_id": "my_component",
  "dimension": "reasoning",
  "score": 85,
  "test_id": "logical_deduction_test",
  "metadata": {
    "model": "claude-3-opus-20240229",
    "test_version": "1.2.0",
    "task_complexity": "medium"
  },
  "timestamp": "2025-05-01T10:15:30Z"
}
```

**Response:**

```json
{
  "measurement_id": "m1e2a3s4-5u6r7e8",
  "component_id": "my_component",
  "dimension": "reasoning",
  "score": 85,
  "test_id": "logical_deduction_test",
  "recorded_at": "2025-05-01T10:15:30.123Z"
}
```

#### Query Intelligence Measurements

```
GET /api/intelligence/measurements
```

Queries intelligence measurements with optional filtering.

**Query Parameters:**

- `component_id` - Filter by component ID
- `dimension` - Filter by intelligence dimension
- `test_id` - Filter by test ID
- `min_score` - Filter by minimum score
- `max_score` - Filter by maximum score
- `from_date` - Filter by timestamp (from)
- `to_date` - Filter by timestamp (to)
- `limit` - Maximum number of results to return (default: 100)
- `offset` - Offset for pagination (default: 0)

**Response:**

```json
{
  "total": 25,
  "offset": 0,
  "limit": 100,
  "measurements": [
    {
      "measurement_id": "m1e2a3s4-5u6r7e8",
      "component_id": "my_component",
      "dimension": "reasoning",
      "score": 85,
      "test_id": "logical_deduction_test",
      "timestamp": "2025-05-01T10:15:30Z",
      "recorded_at": "2025-05-01T10:15:30.123Z",
      "metadata": {
        "model": "claude-3-opus-20240229",
        "test_version": "1.2.0",
        "task_complexity": "medium"
      }
    }
  ]
}
```

#### Get Component Intelligence Profile

```
GET /api/intelligence/components/{id}/profile
```

Gets the intelligence profile for a specific component.

**Path Parameters:**

- `id` - The ID of the component

**Response:**

```json
{
  "component_id": "my_component",
  "dimensions": {
    "language_processing": {
      "score": 90,
      "confidence_interval": [85, 95],
      "tests": 12,
      "last_measured": "2025-05-01T10:15:30Z"
    },
    "reasoning": {
      "score": 85,
      "confidence_interval": [80, 90],
      "tests": 8,
      "last_measured": "2025-05-01T10:15:30Z"
    },
    "knowledge": {
      "score": 75,
      "confidence_interval": [70, 80],
      "tests": 10,
      "last_measured": "2025-05-01T10:15:30Z"
    },
    "learning": {
      "score": 80,
      "confidence_interval": [75, 85],
      "tests": 6,
      "last_measured": "2025-05-01T10:15:30Z"
    },
    "creativity": {
      "score": 85,
      "confidence_interval": [80, 90],
      "tests": 8,
      "last_measured": "2025-05-01T10:15:30Z"
    },
    "planning": {
      "score": 70,
      "confidence_interval": [65, 75],
      "tests": 7,
      "last_measured": "2025-05-01T10:15:30Z"
    },
    "problem_solving": {
      "score": 80,
      "confidence_interval": [75, 85],
      "tests": 9,
      "last_measured": "2025-05-01T10:15:30Z"
    },
    "adaptation": {
      "score": 65,
      "confidence_interval": [60, 70],
      "tests": 5,
      "last_measured": "2025-05-01T10:15:30Z"
    },
    "collaboration": {
      "score": 95,
      "confidence_interval": [90, 100],
      "tests": 6,
      "last_measured": "2025-05-01T10:15:30Z"
    },
    "metacognition": {
      "score": 60,
      "confidence_interval": [55, 65],
      "tests": 4,
      "last_measured": "2025-05-01T10:15:30Z"
    }
  },
  "overall_score": 78.5,
  "strengths": ["collaboration", "language_processing", "creativity"],
  "weaknesses": ["metacognition", "adaptation", "planning"],
  "last_updated": "2025-05-01T10:15:30Z"
}
```

#### Compare Intelligence Profiles

```
POST /api/intelligence/components/compare
```

Compares intelligence profiles of multiple components.

**Request Body:**

```json
{
  "component_ids": ["component_a", "component_b"],
  "dimensions": ["language_processing", "reasoning", "problem_solving"]
}
```

**Response:**

```json
{
  "components": [
    {
      "component_id": "component_a",
      "dimensions": {
        "language_processing": {
          "score": 90,
          "confidence_interval": [85, 95]
        },
        "reasoning": {
          "score": 85,
          "confidence_interval": [80, 90]
        },
        "problem_solving": {
          "score": 80,
          "confidence_interval": [75, 85]
        }
      },
      "overall_score": 85
    },
    {
      "component_id": "component_b",
      "dimensions": {
        "language_processing": {
          "score": 85,
          "confidence_interval": [80, 90]
        },
        "reasoning": {
          "score": 90,
          "confidence_interval": [85, 95]
        },
        "problem_solving": {
          "score": 85,
          "confidence_interval": [80, 90]
        }
      },
      "overall_score": 86.7
    }
  ],
  "comparison": {
    "language_processing": {
      "leader": "component_a",
      "difference": 5,
      "significant": true
    },
    "reasoning": {
      "leader": "component_b",
      "difference": 5,
      "significant": true
    },
    "problem_solving": {
      "leader": "component_b",
      "difference": 5,
      "significant": true
    }
  },
  "overall_leader": {
    "component_id": "component_b",
    "difference": 1.7,
    "significant": false
  }
}
```

#### Get Intelligence Dimensions

```
GET /api/intelligence/dimensions
```

Gets all intelligence dimensions.

**Response:**

```json
{
  "dimensions": [
    {
      "id": "language_processing",
      "name": "Language Processing",
      "description": "Understanding, interpreting, and generating human language",
      "scale": {
        "min": 0,
        "max": 100,
        "thresholds": {
          "low": 30,
          "medium": 60,
          "high": 80
        }
      },
      "tests": [
        "text_comprehension",
        "generation_coherence",
        "multilingual_capability"
      ]
    },
    {
      "id": "reasoning",
      "name": "Reasoning",
      "description": "Making inferences, deductions, and logical arguments",
      "scale": {
        "min": 0,
        "max": 100,
        "thresholds": {
          "low": 30,
          "medium": 60,
          "high": 80
        }
      },
      "tests": [
        "logical_deduction",
        "inductive_reasoning",
        "abductive_reasoning"
      ]
    }
  ]
}
```

#### Get Intelligence Dimension Details

```
GET /api/intelligence/dimensions/{dimension}
```

Gets detailed information about a specific intelligence dimension.

**Path Parameters:**

- `dimension` - The ID of the dimension (e.g., "reasoning")

**Response:**

```json
{
  "id": "reasoning",
  "name": "Reasoning",
  "description": "Making inferences, deductions, and logical arguments",
  "scale": {
    "min": 0,
    "max": 100,
    "thresholds": {
      "low": 30,
      "medium": 60,
      "high": 80
    }
  },
  "tests": [
    {
      "id": "logical_deduction",
      "name": "Logical Deduction",
      "description": "Ability to draw logical conclusions from a set of premises",
      "versions": ["1.0.0", "1.1.0", "1.2.0"],
      "complexity_levels": ["easy", "medium", "hard"]
    },
    {
      "id": "inductive_reasoning",
      "name": "Inductive Reasoning",
      "description": "Ability to recognize patterns and make generalizations",
      "versions": ["1.0.0", "1.1.0"],
      "complexity_levels": ["easy", "medium", "hard"]
    },
    {
      "id": "abductive_reasoning",
      "name": "Abductive Reasoning",
      "description": "Ability to form explanatory hypotheses",
      "versions": ["1.0.0"],
      "complexity_levels": ["medium", "hard"]
    }
  ],
  "related_dimensions": ["problem_solving", "metacognition"],
  "documentation_url": "/docs/intelligence/dimensions/reasoning"
}
```

#### Get Ecosystem Intelligence Profile

```
GET /api/intelligence/ecosystem/profile
```

Gets the intelligence profile for the entire Tekton ecosystem.

**Response:**

```json
{
  "dimensions": {
    "language_processing": {
      "score": 88,
      "confidence_interval": [85, 91],
      "components": [
        {"component_id": "component_a", "score": 90},
        {"component_id": "component_b", "score": 85}
      ]
    },
    "reasoning": {
      "score": 87,
      "confidence_interval": [84, 90],
      "components": [
        {"component_id": "component_a", "score": 85},
        {"component_id": "component_b", "score": 90}
      ]
    },
    "knowledge": {
      "score": 75,
      "confidence_interval": [72, 78],
      "components": [
        {"component_id": "component_a", "score": 75},
        {"component_id": "component_b", "score": 75}
      ]
    }
  },
  "overall_score": 80.2,
  "strengths": ["language_processing", "reasoning", "collaboration"],
  "weaknesses": ["metacognition", "adaptation"],
  "component_count": 10,
  "last_updated": "2025-05-01T10:15:30Z"
}
```

### Components API

#### Register Component

```
POST /api/components/register
```

Registers a component for intelligence measurement.

**Request Body:**

```json
{
  "component_id": "new_component",
  "name": "New Component",
  "description": "A new component for testing",
  "capabilities": ["text_processing", "data_analysis"],
  "models": [
    {
      "id": "claude-3-haiku-20240307",
      "provider": "anthropic"
    }
  ],
  "tags": ["experimental", "nlp"]
}
```

**Response:**

```json
{
  "component_id": "new_component",
  "name": "New Component",
  "description": "A new component for testing",
  "capabilities": ["text_processing", "data_analysis"],
  "models": [
    {
      "id": "claude-3-haiku-20240307",
      "provider": "anthropic"
    }
  ],
  "registration_time": "2025-05-01T10:15:30Z",
  "tags": ["experimental", "nlp"]
}
```

#### Query Components

```
GET /api/components
```

Queries registered components with optional filtering.

**Query Parameters:**

- `capability` - Filter by capability
- `model` - Filter by model ID
- `provider` - Filter by model provider
- `tag` - Filter by tag (can be specified multiple times)
- `limit` - Maximum number of results to return (default: 50)
- `offset` - Offset for pagination (default: 0)

**Response:**

```json
{
  "total": 10,
  "offset": 0,
  "limit": 50,
  "components": [
    {
      "component_id": "new_component",
      "name": "New Component",
      "description": "A new component for testing",
      "capabilities": ["text_processing", "data_analysis"],
      "registration_time": "2025-05-01T10:15:30Z",
      "tags": ["experimental", "nlp"]
    }
  ]
}
```

#### Get Component Details

```
GET /api/components/{id}
```

Gets detailed information about a specific component.

**Path Parameters:**

- `id` - The ID of the component to retrieve

**Response:**

```json
{
  "component_id": "new_component",
  "name": "New Component",
  "description": "A new component for testing",
  "capabilities": ["text_processing", "data_analysis"],
  "models": [
    {
      "id": "claude-3-haiku-20240307",
      "provider": "anthropic"
    }
  ],
  "intelligence_profile": {
    "overall_score": 78.5,
    "dimensions": {
      "language_processing": 90,
      "reasoning": 85
    }
  },
  "metrics_summary": {
    "collected_metrics": 256,
    "last_activity": "2025-05-01T10:15:30Z",
    "top_metrics": [
      "component.performance.latency",
      "component.performance.throughput"
    ]
  },
  "experiments": {
    "total": 5,
    "active": 2,
    "completed": 3
  },
  "recommendations": {
    "total": 8,
    "open": 3,
    "implementing": 2,
    "implemented": 3
  },
  "registration_time": "2025-05-01T10:15:30Z",
  "last_updated": "2025-05-01T10:15:30Z",
  "tags": ["experimental", "nlp"]
}
```

#### Analyze Component Performance

```
GET /api/components/{id}/performance
```

Analyzes performance of a specific component.

**Path Parameters:**

- `id` - The ID of the component to analyze

**Query Parameters:**

- `from_date` - Start of analysis period (default: 7 days ago)
- `to_date` - End of analysis period (default: now)
- `metrics` - Comma-separated list of metrics to include (default: all)

**Response:**

```json
{
  "component_id": "new_component",
  "analysis_period": {
    "from_date": "2025-04-24T10:15:30Z",
    "to_date": "2025-05-01T10:15:30Z"
  },
  "metrics": {
    "component.performance.latency": {
      "current": {
        "mean": 42.5,
        "median": 40.2,
        "p95": 65.3,
        "min": 30.1,
        "max": 120.5
      },
      "trend": {
        "direction": "improving",
        "change_percent": -5.2,
        "significant": true
      },
      "anomalies": [
        {
          "timestamp": "2025-04-28T15:30:00Z",
          "value": 120.5,
          "deviation": 185.3,
          "description": "Significant latency spike"
        }
      ]
    },
    "component.performance.throughput": {
      "current": {
        "mean": 150.2,
        "median": 155.0,
        "p95": 180.5,
        "min": 100.0,
        "max": 200.0
      },
      "trend": {
        "direction": "stable",
        "change_percent": 0.8,
        "significant": false
      },
      "anomalies": []
    }
  },
  "intelligence": {
    "current_score": 78.5,
    "trend": {
      "direction": "improving",
      "change_points": [
        {
          "timestamp": "2025-04-26T00:00:00Z",
          "score_before": 75.0,
          "score_after": 78.5,
          "description": "Improvement after model update"
        }
      ]
    }
  },
  "recommendations": [
    {
      "recommendation_id": "r1e2c3-4o5m6m7e8n9d0",
      "title": "Optimize Query Performance",
      "priority": "high",
      "expected_impact": "20% reduction in query latency, improved security"
    }
  ]
}
```

#### Analyze Component Interactions

```
POST /api/components/interaction
```

Analyzes interactions between components.

**Request Body:**

```json
{
  "component_ids": ["component_a", "component_b", "component_c"],
  "metrics": ["api_calls", "data_transfer", "error_rate"],
  "period": {
    "from_date": "2025-04-24T10:15:30Z",
    "to_date": "2025-05-01T10:15:30Z"
  }
}
```

**Response:**

```json
{
  "period": {
    "from_date": "2025-04-24T10:15:30Z",
    "to_date": "2025-05-01T10:15:30Z"
  },
  "interactions": [
    {
      "source": "component_a",
      "target": "component_b",
      "metrics": {
        "api_calls": {
          "count": 1250,
          "trend": "increasing"
        },
        "data_transfer": {
          "bytes": 28500000,
          "trend": "increasing"
        },
        "error_rate": {
          "percentage": 0.5,
          "trend": "decreasing"
        }
      }
    },
    {
      "source": "component_a",
      "target": "component_c",
      "metrics": {
        "api_calls": {
          "count": 750,
          "trend": "stable"
        },
        "data_transfer": {
          "bytes": 15000000,
          "trend": "stable"
        },
        "error_rate": {
          "percentage": 1.2,
          "trend": "stable"
        }
      }
    },
    {
      "source": "component_b",
      "target": "component_c",
      "metrics": {
        "api_calls": {
          "count": 500,
          "trend": "increasing"
        },
        "data_transfer": {
          "bytes": 8500000,
          "trend": "increasing"
        },
        "error_rate": {
          "percentage": 0.8,
          "trend": "stable"
        }
      }
    }
  ],
  "insights": [
    "Component A is the main hub with the most outgoing connections",
    "Data transfer between Component A and Component B is growing fastest",
    "Error rates are generally low and stable or improving"
  ],
  "bottlenecks": [
    {
      "component": "component_b",
      "reason": "High incoming traffic from Component A",
      "recommendation": "Consider scaling Component B or implementing caching"
    }
  ]
}
```

### Research API

#### Create Research Project

```
POST /api/research/projects
```

Creates a new research project.

**Request Body:**

```json
{
  "name": "Intelligence Evolution Analysis",
  "description": "Analyzing how intelligence profiles evolve over time with model updates",
  "research_questions": [
    "How do intelligence profiles change after model updates?",
    "Which dimensions show the most consistent improvement?",
    "Are there trade-offs between different dimensions?"
  ],
  "components": ["component_a", "component_b"],
  "dimensions": ["language_processing", "reasoning", "knowledge"],
  "timeline": {
    "start_date": "2025-05-01T00:00:00Z",
    "end_date": "2025-08-01T00:00:00Z"
  },
  "tags": ["intelligence", "model_evolution", "longitudinal"]
}
```

**Response:**

```json
{
  "project_id": "p1r2o3j4-5e6c7t8",
  "name": "Intelligence Evolution Analysis",
  "description": "Analyzing how intelligence profiles evolve over time with model updates",
  "research_questions": [
    "How do intelligence profiles change after model updates?",
    "Which dimensions show the most consistent improvement?",
    "Are there trade-offs between different dimensions?"
  ],
  "components": ["component_a", "component_b"],
  "dimensions": ["language_processing", "reasoning", "knowledge"],
  "timeline": {
    "start_date": "2025-05-01T00:00:00Z",
    "end_date": "2025-08-01T00:00:00Z",
    "created_at": "2025-05-01T10:15:30Z"
  },
  "status": "created",
  "tags": ["intelligence", "model_evolution", "longitudinal"]
}
```

#### Query Research Projects

```
GET /api/research/projects
```

Queries research projects with optional filtering.

**Query Parameters:**

- `status` - Filter by status (e.g., "created", "active", "completed")
- `component` - Filter by component
- `dimension` - Filter by dimension
- `tag` - Filter by tag (can be specified multiple times)
- `limit` - Maximum number of results to return (default: 50)
- `offset` - Offset for pagination (default: 0)

**Response:**

```json
{
  "total": 3,
  "offset": 0,
  "limit": 50,
  "projects": [
    {
      "project_id": "p1r2o3j4-5e6c7t8",
      "name": "Intelligence Evolution Analysis",
      "description": "Analyzing how intelligence profiles evolve over time with model updates",
      "status": "created",
      "timeline": {
        "start_date": "2025-05-01T00:00:00Z",
        "end_date": "2025-08-01T00:00:00Z"
      },
      "tags": ["intelligence", "model_evolution", "longitudinal"]
    }
  ]
}
```

#### Get Research Project Details

```
GET /api/research/projects/{id}
```

Gets detailed information about a specific research project.

**Path Parameters:**

- `id` - The ID of the research project to retrieve

**Response:**

```json
{
  "project_id": "p1r2o3j4-5e6c7t8",
  "name": "Intelligence Evolution Analysis",
  "description": "Analyzing how intelligence profiles evolve over time with model updates",
  "research_questions": [
    "How do intelligence profiles change after model updates?",
    "Which dimensions show the most consistent improvement?",
    "Are there trade-offs between different dimensions?"
  ],
  "components": ["component_a", "component_b"],
  "dimensions": ["language_processing", "reasoning", "knowledge"],
  "timeline": {
    "start_date": "2025-05-01T00:00:00Z",
    "end_date": "2025-08-01T00:00:00Z",
    "created_at": "2025-05-01T10:15:30Z",
    "started_at": "2025-05-01T14:00:00Z"
  },
  "status": "active",
  "milestones": [
    {
      "name": "Initial Baseline Measurement",
      "due_date": "2025-05-15T00:00:00Z",
      "status": "in_progress"
    },
    {
      "name": "First Model Update",
      "due_date": "2025-06-01T00:00:00Z",
      "status": "pending"
    },
    {
      "name": "Midpoint Analysis",
      "due_date": "2025-07-01T00:00:00Z",
      "status": "pending"
    },
    {
      "name": "Final Analysis",
      "due_date": "2025-08-01T00:00:00Z",
      "status": "pending"
    }
  ],
  "findings": [],
  "tags": ["intelligence", "model_evolution", "longitudinal"]
}
```

### System API

#### Health Check

```
GET /health
```

Checks the health status of the Sophia component.

**Response:**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 3600,
  "components": {
    "api": "healthy",
    "metrics_engine": "healthy",
    "experiment_framework": "healthy",
    "intelligence_measurement": "healthy",
    "storage": "healthy"
  }
}
```

#### Metrics

```
GET /metrics
```

Retrieves metrics for the Sophia component.

**Response:**

```json
{
  "metrics_collected": 12500,
  "experiments": {
    "total": 25,
    "active": 5,
    "completed": 20
  },
  "intelligence_measurements": 1500,
  "recommendations": {
    "total": 120,
    "open": 30,
    "implementing": 20,
    "implemented": 60,
    "rejected": 10
  },
  "storage": {
    "metrics_size_mb": 250,
    "experiments_size_mb": 50,
    "intelligence_size_mb": 100
  },
  "performance": {
    "avg_request_time_ms": 45,
    "p95_request_time_ms": 120,
    "requests_per_minute": 60
  }
}
```

## WebSocket API

### Metrics Updates

```
WebSocket: ws://<host>:8006/ws/metrics
```

Provides real-time updates about metrics data.

**Connection URL Parameters:**

- None

**Messages:**

Metric Submitted:
```json
{
  "type": "metric_submitted",
  "timestamp": "2025-05-01T10:15:30Z",
  "data": {
    "metric_id": "component.performance.latency",
    "value": 42.5,
    "source": "my_component"
  }
}
```

### Experiment Updates

```
WebSocket: ws://<host>:8006/ws/experiments/{experiment_id}
```

Provides real-time updates about a specific experiment.

**Connection URL Parameters:**

- `experiment_id` - The ID of the experiment to monitor

**Messages:**

Experiment Started:
```json
{
  "type": "experiment_started",
  "timestamp": "2025-05-01T10:20:00Z",
  "data": {
    "experiment_id": "e1x2p3-4e5r6i7m8e9n0t1",
    "name": "Latency Optimization"
  }
}
```

Experiment Data Point:
```json
{
  "type": "experiment_data_point",
  "timestamp": "2025-05-01T10:30:00Z",
  "data": {
    "experiment_id": "e1x2p3-4e5r6i7m8e9n0t1",
    "variant": "treatment",
    "metric_id": "component.performance.latency",
    "value": 42.5
  }
}
```

Experiment Completed:
```json
{
  "type": "experiment_completed",
  "timestamp": "2025-05-08T10:20:00Z",
  "data": {
    "experiment_id": "e1x2p3-4e5r6i7m8e9n0t1",
    "status": "completed",
    "duration_hours": 168
  }
}
```

### Intelligence Updates

```
WebSocket: ws://<host>:8006/ws/intelligence
```

Provides real-time updates about intelligence measurements.

**Connection URL Parameters:**

- None

**Messages:**

Intelligence Measurement:
```json
{
  "type": "intelligence_measurement",
  "timestamp": "2025-05-01T10:15:30Z",
  "data": {
    "component_id": "my_component",
    "dimension": "reasoning",
    "score": 85
  }
}
```

Profile Update:
```json
{
  "type": "profile_update",
  "timestamp": "2025-05-01T10:15:30Z",
  "data": {
    "component_id": "my_component",
    "dimension": "reasoning",
    "previous_score": 80,
    "new_score": 85,
    "change": 5
  }
}
```

## API Clients

Sophia provides client libraries for easy integration:

### Python Client

```python
from sophia.client import SophiaClient
import asyncio

async def sophia_client_example():
    # Create client
    client = SophiaClient(base_url="http://localhost:8006")
    
    try:
        # Check health
        health = await client.is_available()
        print(f"Sophia available: {health}")
        
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
        print(f"Retrieved {len(metrics)} metrics")
        
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
        print(f"Created experiment: {experiment_id}")
        
        # Get intelligence profile
        profile = await client.get_component_intelligence_profile("my_component")
        print(f"Component overall score: {profile['overall_score']}")
        
        # Compare components
        comparison = await client.compare_intelligence_profiles(
            component_ids=["component_a", "component_b"],
            dimensions=["language_processing", "reasoning"]
        )
        print(f"Comparison leader: {comparison['overall_leader']['component_id']}")
        
    finally:
        # Close client
        await client.close()

# Run the example
asyncio.run(sophia_client_example())
```

### JavaScript Client

```javascript
import { SophiaClient } from 'sophia-client';

async function sophiaClientExample() {
  // Create client
  const client = new SophiaClient('http://localhost:8006');
  
  try {
    // Check health
    const health = await client.isAvailable();
    console.log(`Sophia available: ${health}`);
    
    // Submit a metric
    await client.submitMetric({
      metric_id: 'component.performance.latency',
      value: 42.5,
      source: 'my_component',
      tags: ['performance', 'latency']
    });
    
    // Query metrics
    const metrics = await client.queryMetrics({
      metric_id: 'component.performance.latency',
      source: 'my_component',
      limit: 10
    });
    console.log(`Retrieved ${metrics.length} metrics`);
    
    // Create an experiment
    const experimentId = await client.createExperiment({
      name: 'Latency Optimization',
      description: 'Testing a new algorithm to reduce latency',
      experiment_type: 'a_b_test',
      target_components: ['my_component'],
      hypothesis: 'The new algorithm reduces latency by 20%',
      metrics: ['component.performance.latency'],
      parameters: {
        control: { algorithm: 'current' },
        treatment: { algorithm: 'new' }
      }
    });
    console.log(`Created experiment: ${experimentId}`);
    
    // Get intelligence profile
    const profile = await client.getComponentIntelligenceProfile('my_component');
    console.log(`Component overall score: ${profile.overall_score}`);
    
    // Compare components
    const comparison = await client.compareIntelligenceProfiles({
      component_ids: ['component_a', 'component_b'],
      dimensions: ['language_processing', 'reasoning']
    });
    console.log(`Comparison leader: ${comparison.overall_leader.component_id}`);
    
  } finally {
    // Close client
    client.close();
  }
}

sophiaClientExample();
```

## Error Responses

All API endpoints return standard error responses in the following format:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Invalid request parameters",
    "details": [
      {
        "field": "value",
        "message": "Must be a number"
      }
    ]
  }
}
```

Common error codes:

- `validation_error`: Request validation failed
- `not_found`: Resource not found
- `already_exists`: Resource already exists
- `permission_denied`: Permission denied
- `invalid_operation`: Invalid operation for the current state
- `internal_error`: Internal server error