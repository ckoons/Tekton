# Sophia User Guide

## Introduction

Sophia is the intelligence analysis and measurement system for the Tekton ecosystem. It provides tools for evaluating LLM capabilities, detecting patterns in AI behavior, conducting experiments, and generating insights to improve AI systems. This guide will help you get started with Sophia and leverage its capabilities for your AI research and optimization needs.

## Getting Started

### Installation

1. Ensure you have Python 3.9+ installed
2. Clone the Sophia repository:
   ```bash
   git clone git@github.com:yourusername/Tekton.git
   cd Tekton/Sophia
   ```

3. Install dependencies:
   ```bash
   pip install -e .
   ```
   or use the setup script:
   ```bash
   ./setup.sh
   ```

4. Start the Sophia server:
   ```bash
   python -m sophia.api.app
   ```

By default, Sophia runs on port 8005. You can change this by setting the `SOPHIA_PORT` environment variable.

### Basic Configuration

Create a configuration file named `sophia_config.json`:

```json
{
  "server": {
    "host": "localhost",
    "port": 8005
  },
  "llm": {
    "default_provider": "openai",
    "providers": {
      "openai": {
        "api_key": "your-openai-api-key",
        "models": ["gpt-4", "gpt-3.5-turbo"]
      },
      "anthropic": {
        "api_key": "your-anthropic-api-key",
        "models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
      }
    }
  },
  "metrics": {
    "enabled": true,
    "storage_path": "./metrics_data"
  }
}
```

## Using the Client Library

Sophia provides a Python client for easy integration:

```python
from sophia.client import SophiaClient

# Initialize client
client = SophiaClient("http://localhost:8005")

# Get available measurement dimensions
dimensions = client.get_intelligence_dimensions()
print(f"Available dimensions: {', '.join(dim['name'] for dim in dimensions)}")

# Create a new experiment
experiment = client.create_experiment(
    name="Model Comparison Experiment",
    description="Comparing different models on reasoning tasks",
    models=["gpt-4", "claude-3-opus"],
    dimensions=["reasoning", "knowledge", "problem_solving"]
)

print(f"Created experiment: {experiment['id']}")
```

## Understanding Intelligence Dimensions

Sophia measures AI capabilities across 10 key dimensions:

1. **Language Understanding**: Comprehension, contextual understanding, and semantic parsing
2. **Reasoning**: Logical inference, deduction, problem-solving
3. **Knowledge**: Breadth and depth of factual information and domain expertise
4. **Learning**: Ability to acquire and apply new information
5. **Creativity**: Generation of novel and valuable outputs
6. **Social Intelligence**: Understanding human behavior, emotions, and intentions
7. **Adaptability**: Flexibility in responding to new situations or requirements
8. **Integration**: Combining information across domains and modalities
9. **Self-Regulation**: Awareness of capabilities and limitations
10. **Efficacy**: Practical effectiveness in achieving goals

### Viewing Dimension Details

```python
# Get details of a specific dimension
reasoning_dimension = client.get_intelligence_dimension("reasoning")

print(f"Dimension: {reasoning_dimension['name']}")
print(f"Description: {reasoning_dimension['description']}")

print("Metrics:")
for metric in reasoning_dimension['metrics']:
    print(f"- {metric['name']}: {metric['description']}")
```

## Conducting Intelligence Measurements

### Creating and Running Experiments

```python
# Create a focused experiment
experiment = client.create_experiment(
    name="Reasoning Depth Analysis",
    description="Analyzing depth of reasoning across multiple models",
    models=["gpt-4", "gpt-3.5-turbo", "claude-3-opus"],
    dimensions=["reasoning"],
    parameters={
        "test_cases": 20,
        "complexity_levels": ["basic", "intermediate", "advanced"],
        "timeout_seconds": 300
    }
)

# Run the experiment
experiment_run = client.run_experiment(experiment['id'])

print(f"Experiment run started: {experiment_run['id']}")
print(f"Status: {experiment_run['status']}")

# Check experiment status
status = client.get_experiment_run_status(experiment_run['id'])
print(f"Current status: {status['status']}")
print(f"Progress: {status['progress']['completed']}/{status['progress']['total']} tasks")

# Get experiment results when complete
if status['status'] == 'completed':
    results = client.get_experiment_results(experiment_run['id'])
    
    print("\nOverall Scores:")
    for model, scores in results['model_scores'].items():
        print(f"{model}: {scores['reasoning']['overall']}/100")
        
    print("\nDetailed Metrics:")
    for model, scores in results['model_scores'].items():
        print(f"\n{model}:")
        for metric, score in scores['reasoning']['metrics'].items():
            print(f"  {metric}: {score}/100")
```

### Measuring a Single Model

```python
# Measure a single model on specific dimensions
measurement = client.measure_model(
    model="claude-3-sonnet",
    dimensions=["knowledge", "creativity", "adaptability"],
    parameters={
        "test_cases": 10,
        "domains": ["science", "history", "arts"]
    }
)

print(f"Measurement ID: {measurement['id']}")

# Get measurement results
results = client.get_measurement_results(measurement['id'])

print("\nDimension Scores:")
for dimension, score in results['scores'].items():
    print(f"{dimension}: {score['overall']}/100")
    
    print("  Metrics:")
    for metric, metric_score in score['metrics'].items():
        print(f"    {metric}: {metric_score}/100")
```

## Pattern Detection and Analysis

Sophia can detect patterns in AI behavior and outputs:

```python
# Detect patterns in model responses
patterns = client.detect_patterns(
    model="gpt-4",
    data_source="experiment_run_123",  # ID of a previous experiment run
    analysis_type="response_patterns",
    parameters={
        "min_confidence": 0.7,
        "max_patterns": 10
    }
)

print("Detected Patterns:")
for pattern in patterns:
    print(f"\nPattern: {pattern['name']}")
    print(f"Confidence: {pattern['confidence']}")
    print(f"Description: {pattern['description']}")
    print(f"Examples: {len(pattern['examples'])} instances")
```

### Custom Pattern Analysis

```python
# Create custom analysis task
analysis = client.create_analysis(
    name="Error Pattern Analysis",
    description="Analyzing patterns in model errors on math problems",
    data_source="experiment_run_456",
    analysis_type="error_patterns",
    parameters={
        "error_threshold": 0.3,
        "categorize": True,
        "generate_fixes": True
    }
)

# Get analysis results
results = client.get_analysis_results(analysis['id'])

print("\nError Categories:")
for category in results['error_categories']:
    print(f"\n{category['name']} ({category['frequency']}%):")
    print(f"Description: {category['description']}")
    print("Examples:")
    for example in category['examples'][:3]:  # First 3 examples
        print(f"  - {example['problem']}")
        print(f"    Response: {example['response']}")
        print(f"    Issue: {example['issue']}")
    
    print("Recommended Fixes:")
    for fix in category['recommended_fixes']:
        print(f"  - {fix}")
```

## Intelligence Improvement Recommendations

Sophia can recommend improvements based on analysis:

```python
# Generate improvement recommendations
recommendations = client.generate_recommendations(
    model="gpt-3.5-turbo",
    based_on="measurement_789",  # ID of a previous measurement
    dimensions=["reasoning", "knowledge"],
    parameters={
        "detail_level": "comprehensive",
        "include_examples": True,
        "prioritize": True
    }
)

print("\nImprovement Recommendations:")
for dimension, recs in recommendations['dimensions'].items():
    print(f"\n{dimension.upper()} Recommendations:")
    
    for i, rec in enumerate(recs, 1):
        print(f"{i}. {rec['title']}")
        print(f"   Priority: {rec['priority']}/10")
        print(f"   Description: {rec['description']}")
        print(f"   Implementation: {rec['implementation']}")
        
        if rec['examples']:
            print("   Examples:")
            for example in rec['examples']:
                print(f"     - {example}")
```

## Creating and Managing Experiments

### Experiment Framework

Sophia provides a comprehensive experiment framework:

```python
# Define a complex experiment
experiment = client.create_experiment(
    name="Multi-Model Comparison",
    description="Comprehensive comparison across all dimensions",
    models=["gpt-4", "gpt-3.5-turbo", "claude-3-opus", "claude-3-sonnet"],
    dimensions=["language_understanding", "reasoning", "knowledge", 
                "creativity", "problem_solving", "adaptability"],
    parameters={
        "test_cases_per_dimension": 15,
        "complexity_levels": ["basic", "intermediate", "advanced"],
        "domains": ["general", "scientific", "creative", "practical"],
        "randomize_order": True,
        "blind_evaluation": True
    }
)

# Run experiment with custom settings
run = client.run_experiment(
    experiment_id=experiment['id'],
    settings={
        "parallel_tasks": 4,
        "timeout_minutes": 120,
        "retry_failed": True,
        "save_responses": True
    }
)

# Monitor progress
while True:
    status = client.get_experiment_run_status(run['id'])
    print(f"Status: {status['status']}")
    print(f"Progress: {status['progress']['completed']}/{status['progress']['total']} tasks")
    
    if status['status'] in ['completed', 'failed']:
        break
        
    time.sleep(30)  # Check every 30 seconds
```

### Managing Experiment Templates

```python
# Save experiment as template
template = client.save_experiment_template(
    experiment_id=experiment['id'],
    name="Comprehensive Model Evaluation",
    description="Template for thorough model evaluation across dimensions",
    is_public=True
)

print(f"Created template: {template['id']}")

# List available templates
templates = client.list_experiment_templates()
for template in templates:
    print(f"{template['name']} - {template['description']}")

# Create experiment from template
new_experiment = client.create_experiment_from_template(
    template_id=template['id'],
    name="New Model Evaluation",
    models=["new-model-1", "new-model-2"],
    parameters={
        "test_cases_per_dimension": 20  # Override template parameter
    }
)
```

## Metrics and Visualizations

### Retrieving Metrics

```python
# Get detailed metrics for a model
metrics = client.get_model_metrics(
    model="gpt-4",
    dimensions=["reasoning", "knowledge"],
    time_range={
        "start": "2025-01-01",
        "end": "2025-04-30"
    }
)

print("Model Metrics Over Time:")
for dimension, dim_metrics in metrics.items():
    print(f"\n{dimension.upper()}:")
    for timestamp, score in dim_metrics['timeline'].items():
        print(f"{timestamp}: {score}")
        
    print(f"Average: {dim_metrics['average']}")
    print(f"Trend: {dim_metrics['trend']}")
```

### Generating Visualizations

```python
# Generate visualization for experiment results
visualization = client.generate_visualization(
    data_source="experiment_run_123",
    visualization_type="dimension_comparison",
    parameters={
        "models": ["gpt-4", "claude-3-opus"],
        "dimensions": ["reasoning", "knowledge", "creativity"],
        "chart_type": "radar",
        "include_metrics": True
    }
)

# The visualization is returned as a base64-encoded image
print(f"Visualization URL: {visualization['url']}")

# Alternatively, save it to a file
import base64

with open("dimension_comparison.png", "wb") as f:
    f.write(base64.b64decode(visualization['data']))
```

### Comparing Models

```python
# Generate model comparison
comparison = client.compare_models(
    models=["gpt-4", "gpt-3.5-turbo", "claude-3-opus"],
    dimensions=["reasoning", "knowledge", "problem_solving"],
    parameters={
        "test_cases": 15,
        "normalize_scores": True,
        "detailed_breakdown": True
    }
)

print("\nModel Comparison:")
for dimension in comparison['dimensions']:
    print(f"\n{dimension['name']} Dimension:")
    
    # Overall rankings
    print("Rankings:")
    for i, model_score in enumerate(dimension['rankings'], 1):
        print(f"{i}. {model_score['model']}: {model_score['score']}/100")
    
    # Metric breakdown
    print("\nMetric Breakdown:")
    for metric in dimension['metrics']:
        print(f"\n{metric['name']}:")
        for model, score in metric['scores'].items():
            print(f"  {model}: {score}/100")
```

## Integration with Tekton Components

### Hermes Integration

Register with Hermes for service discovery:

```python
from sophia.utils.tekton_utils import register_with_hermes

# Register with Hermes
success = register_with_hermes(
    hermes_url="http://localhost:8002",
    component_info={
        "name": "Sophia",
        "version": "1.0.0",
        "description": "Intelligence measurement and analysis system",
        "endpoints": {
            "http": "http://localhost:8005/api",
            "websocket": "ws://localhost:8005/ws"
        },
        "capabilities": ["intelligence-measurement", "pattern-analysis"]
    }
)

print(f"Registered with Hermes: {success}")
```

### LLM Integration

Use the Tekton LLM client for model interactions:

```python
from sophia.utils.llm_integration import get_llm_client

# Get LLM client
llm_client = get_llm_client()

# Use client for model queries
response = llm_client.query(
    model="gpt-4",
    prompt="Solve this problem step by step: If x² + 5x + 6 = 0, what are the values of x?",
    parameters={
        "temperature": 0.2,
        "max_tokens": 500
    }
)

print(f"Model response: {response}")
```

## Command Line Interface

Sophia includes a CLI for common operations:

### Basic Commands

```bash
# List available dimensions
python -m sophia.cli.main dimensions list

# Measure a model
python -m sophia.cli.main measure --model "gpt-4" --dimensions "reasoning,knowledge"

# Create an experiment
python -m sophia.cli.main experiment create \
  --name "CLI Test Experiment" \
  --models "gpt-4,claude-3-opus" \
  --dimensions "reasoning,knowledge,creativity"

# Run an experiment
python -m sophia.cli.main experiment run --id "experiment_123"

# Get experiment results
python -m sophia.cli.main experiment results --id "experiment_run_456"

# Generate recommendations
python -m sophia.cli.main recommendations --model "gpt-4" --based-on "measurement_789"
```

### Interactive Analysis Mode

```bash
# Start interactive analysis mode
python -m sophia.cli.main interactive

# In interactive mode, you can run commands and explore results interactively
```

## Advanced Use Cases

### Custom Metric Development

You can create custom metrics for specific evaluation needs:

```python
from sophia.core.metrics_engine import register_custom_metric

# Define custom metric
def coding_accuracy_evaluator(response, reference):
    """Evaluates coding accuracy by testing functionality against test cases"""
    # Metric implementation...
    return score, confidence, details

# Register custom metric
register_custom_metric(
    dimension="problem_solving",
    name="coding_accuracy",
    description="Measures ability to write functioning code that passes test cases",
    evaluator=coding_accuracy_evaluator,
    parameters={
        "test_cases_required": True,
        "score_range": [0, 100],
        "weight": 1.5  # Higher weight than standard metrics
    }
)

# Use custom metric in measurement
measurement = client.measure_model(
    model="gpt-4",
    dimensions=["problem_solving"],
    parameters={
        "include_metrics": ["coding_accuracy"],
        "test_cases": [
            {
                "prompt": "Write a function to find the nth Fibonacci number",
                "test_cases": [
                    {"input": 0, "expected": 0},
                    {"input": 1, "expected": 1},
                    {"input": 10, "expected": 55}
                ]
            }
        ]
    }
)
```

### Longitudinal Model Tracking

Track model performance over time:

```python
# Start tracking a model
tracking = client.start_model_tracking(
    model="gpt-4",
    dimensions=["reasoning", "knowledge", "problem_solving"],
    schedule="weekly",
    parameters={
        "test_cases": 20,
        "consistent_test_set": True,
        "notification_threshold": 5  # Alert on 5% change
    }
)

print(f"Tracking started: {tracking['id']}")

# Get tracking history
history = client.get_tracking_history(tracking['id'])

print("\nPerformance History:")
for entry in history:
    print(f"\nDate: {entry['date']}")
    for dimension, score in entry['scores'].items():
        print(f"  {dimension}: {score}/100")
    
    if entry.get('changes'):
        print("  Significant Changes:")
        for change in entry['changes']:
            print(f"    {change['dimension']}: {change['change']}% ({change['direction']})")
```

### A/B Testing Models

Compare variations of models:

```python
# Create A/B test
ab_test = client.create_ab_test(
    name="Prompt Engineering Impact",
    description="Testing impact of different prompt engineering techniques",
    models=["gpt-4"],
    variations=[
        {
            "name": "Standard",
            "prompt_template": "{{question}}"
        },
        {
            "name": "Chain of Thought",
            "prompt_template": "{{question}}\n\nThink step by step to solve this problem."
        },
        {
            "name": "Few Shot",
            "prompt_template": "Here are some examples:\n{{examples}}\n\n{{question}}"
        }
    ],
    dimensions=["reasoning"],
    test_cases=10
)

# Run A/B test
test_run = client.run_ab_test(ab_test['id'])

# Get A/B test results
results = client.get_ab_test_results(test_run['id'])

print("\nA/B Test Results:")
for dimension, dim_results in results['dimensions'].items():
    print(f"\n{dimension.upper()}:")
    
    for variation, score in dim_results['scores'].items():
        print(f"  {variation}: {score}/100")
    
    winner = dim_results['winner']
    improvement = dim_results['improvement']
    print(f"  Winner: {winner}")
    print(f"  Improvement: {improvement}% over standard")
```

## Troubleshooting

### Common Issues

1. **Connection Problems**
   - Check that the Sophia server is running
   - Verify the server URL in your client configuration
   - Ensure network connectivity between client and server

2. **Authentication Errors**
   - Check that your API keys are correctly set in configuration
   - Verify the keys have the necessary permissions
   - Check for typos in API keys

3. **Experiment Failures**
   - Check detailed error logs for the experiment run
   - Ensure all required parameters are provided
   - Verify models are accessible and operational

4. **Performance Issues**
   - For large experiments, consider increasing timeouts
   - Reduce parallel tasks if experiencing rate limiting
   - Break large experiments into smaller batches

### Debugging

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or configure logging in your application:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("sophia.log"),
        logging.StreamHandler()
    ]
)

# Get logger
logger = logging.getLogger("sophia")
```

## Best Practices

1. **Start Simple**: Begin with focused experiments on a few dimensions
2. **Use Templates**: Create and reuse experiment templates for consistency
3. **Regular Tracking**: Set up automated tracking to monitor model performance
4. **Compare Models**: Always run comparative experiments rather than absolute measurements
5. **Custom Metrics**: Develop custom metrics for your specific needs
6. **Version Results**: Keep track of measurement versions and changes
7. **Combine Insights**: Use pattern detection and recommendations together
8. **Statistical Significance**: Run enough test cases for statistical significance
9. **Domain Diversity**: Include diverse domains in comprehensive evaluations
10. **Continuous Improvement**: Use recommendations to iteratively improve systems

## Conclusion

This guide covers the basics of using Sophia for intelligence measurement and analysis. For more detailed information, check the [API Reference](./API_REFERENCE.md) and [Technical Documentation](./TECHNICAL_DOCUMENTATION.md).

If you encounter issues or need assistance, please refer to the [Tekton Documentation](../../README.md) for community support options.