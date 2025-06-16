# Sophia Integration Guide

## Overview

This guide provides detailed instructions for integrating Sophia, the intelligence measurement and analysis system, with other components of the Tekton ecosystem and external applications. Sophia offers rich capabilities for evaluating LLM performance, conducting experiments, detecting patterns, and generating improvement recommendations.

## Integration Methods

Sophia provides multiple integration points:

1. **REST API**: HTTP endpoints for all Sophia features
2. **Client Library**: Python client for easy programmatic access
3. **WebSocket API**: Real-time notifications and updates
4. **Hermes Integration**: Service discovery and cross-component messaging
5. **CLI Interface**: Command-line tools for scripting and automation

## REST API Integration

### API Basics

The Sophia REST API is available at `http://localhost:8005/api` by default.

Base URL structure:
```
http://{host}:{port}/api/{resource}
```

All API requests that modify data should use appropriate HTTP methods:
- `GET`: Retrieve data
- `POST`: Create new resources
- `PUT`: Update existing resources
- `DELETE`: Remove resources

### Authentication

API requests require authentication:

```
Authorization: Bearer {api_key}
```

You can obtain an API key by registering with Sophia:

```bash
curl -X POST http://localhost:8005/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "MyApplication",
    "client_id": "app-123"
  }'
```

Response:
```json
{
  "api_key": "sk_sophia_12345abcdef",
  "expires_at": "2026-04-30T00:00:00Z"
}
```

### Core API Endpoints

#### Intelligence Dimensions

```
GET /api/dimensions
```

Response:
```json
{
  "dimensions": [
    {
      "id": "reasoning",
      "name": "Reasoning",
      "description": "Logical inference, deduction, and problem-solving capabilities",
      "metrics": [
        {
          "id": "logical_consistency",
          "name": "Logical Consistency",
          "description": "Consistency in applying logical rules and principles"
        },
        ...
      ]
    },
    ...
  ]
}
```

#### Measurements

Create a measurement:
```
POST /api/measurements
```

Request:
```json
{
  "model": "gpt-4",
  "dimensions": ["reasoning", "knowledge"],
  "parameters": {
    "test_cases": 10,
    "domains": ["general", "scientific"]
  }
}
```

Response:
```json
{
  "id": "measurement_12345",
  "status": "pending",
  "created_at": "2025-04-30T12:00:00Z",
  "estimated_completion": "2025-04-30T12:10:00Z"
}
```

Get measurement results:
```
GET /api/measurements/{id}/results
```

Response:
```json
{
  "id": "measurement_12345",
  "model": "gpt-4",
  "dimensions": {
    "reasoning": {
      "overall": 85,
      "metrics": {
        "logical_consistency": 88,
        "deductive_reasoning": 90,
        "inductive_reasoning": 82,
        "fallacy_avoidance": 80
      }
    },
    "knowledge": {
      "overall": 92,
      "metrics": {
        "factual_accuracy": 94,
        "breadth": 91,
        "depth": 90,
        "context_relevance": 93
      }
    }
  },
  "created_at": "2025-04-30T12:00:00Z",
  "completed_at": "2025-04-30T12:08:45Z"
}
```

#### Experiments

Create an experiment:
```
POST /api/experiments
```

Request:
```json
{
  "name": "Cross-Model Comparison",
  "description": "Comparing reasoning capabilities across models",
  "models": ["gpt-4", "claude-3-opus"],
  "dimensions": ["reasoning"],
  "parameters": {
    "test_cases": 20,
    "complexity_levels": ["basic", "intermediate", "advanced"]
  }
}
```

Response:
```json
{
  "id": "experiment_abcdef",
  "name": "Cross-Model Comparison",
  "status": "created",
  "created_at": "2025-04-30T13:00:00Z"
}
```

Run an experiment:
```
POST /api/experiments/{id}/run
```

Response:
```json
{
  "run_id": "experiment_run_123456",
  "status": "running",
  "started_at": "2025-04-30T13:01:00Z",
  "estimated_completion": "2025-04-30T13:30:00Z"
}
```

Get experiment results:
```
GET /api/experiments/runs/{run_id}/results
```

### API Reference

For complete API details, refer to the [Sophia API Reference](./API_REFERENCE.md).

## Client Library Integration

The Python client library provides a convenient way to integrate with Sophia.

### Installation

```bash
pip install sophia-client
```

Or install from source:

```bash
cd /path/to/Tekton/Sophia
pip install -e .
```

### Basic Usage

```python
from sophia.client import SophiaClient

# Initialize client
client = SophiaClient(
    base_url="http://localhost:8005",
    api_key="sk_sophia_12345abcdef"
)

# Create and run a simple experiment
experiment = client.create_experiment(
    name="Client Library Test",
    models=["gpt-4", "claude-3-sonnet"],
    dimensions=["reasoning", "knowledge"]
)

run = client.run_experiment(experiment['id'])

# Poll for results
import time
while True:
    status = client.get_experiment_run_status(run['id'])
    if status['status'] == 'completed':
        results = client.get_experiment_results(run['id'])
        break
    time.sleep(10)
```

### Error Handling

```python
from sophia.client import SophiaClient, SophiaError

client = SophiaClient("http://localhost:8005", "sk_sophia_12345abcdef")

try:
    # Attempt to get a non-existent experiment
    experiment = client.get_experiment("non_existent_id")
except SophiaError as e:
    print(f"Error: {e.message}")
    print(f"Status code: {e.status_code}")
    print(f"Error code: {e.error_code}")
```

### Asynchronous Client

```python
from sophia.client import AsyncSophiaClient
import asyncio

async def run_measurement():
    client = AsyncSophiaClient("http://localhost:8005", "sk_sophia_12345abcdef")
    
    # Create measurement
    measurement = await client.measure_model(
        model="gpt-4",
        dimensions=["reasoning"]
    )
    
    # Poll for completion
    while True:
        status = await client.get_measurement_status(measurement['id'])
        if status['status'] == 'completed':
            results = await client.get_measurement_results(measurement['id'])
            return results
        await asyncio.sleep(5)

# Run the async function
results = asyncio.run(run_measurement())
```

## WebSocket Integration

Sophia provides WebSocket endpoints for real-time notifications.

### Connecting to WebSocket

```javascript
// JavaScript example
const socket = new WebSocket('ws://localhost:8005/ws');

socket.onopen = function(event) {
  console.log('Connected to Sophia WebSocket');
  
  // Authenticate
  socket.send(JSON.stringify({
    type: 'authenticate',
    api_key: 'sk_sophia_12345abcdef'
  }));
  
  // Subscribe to events
  socket.send(JSON.stringify({
    type: 'subscribe',
    events: ['experiment.completed', 'measurement.completed']
  }));
};

socket.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Received event:', data);
  
  if (data.type === 'experiment.completed') {
    console.log(`Experiment ${data.experiment_id} completed!`);
    // Fetch results using REST API
  }
};

socket.onclose = function(event) {
  console.log('Disconnected from Sophia WebSocket');
};
```

Python example:

```python
import websocket
import json
import threading

def on_message(ws, message):
    data = json.loads(message)
    print(f"Received: {data}")
    
    if data.get('type') == 'experiment.completed':
        print(f"Experiment {data['experiment_id']} completed!")

def on_open(ws):
    print("Connection opened")
    
    # Authenticate
    ws.send(json.stringify({
        "type": "authenticate",
        "api_key": "sk_sophia_12345abcdef"
    }))
    
    # Subscribe to events
    ws.send(json.stringify({
        "type": "subscribe",
        "events": ["experiment.completed", "measurement.completed"]
    }))

websocket.enableTrace(True)
ws = websocket.WebSocketApp("ws://localhost:8005/ws",
                          on_message=on_message,
                          on_open=on_open)

# Start WebSocket connection in background thread
wst = threading.Thread(target=ws.run_forever)
wst.daemon = True
wst.start()
```

### WebSocket Event Types

| Event Type | Description |
|------------|-------------|
| `experiment.created` | New experiment created |
| `experiment.started` | Experiment run started |
| `experiment.progress` | Experiment progress update |
| `experiment.completed` | Experiment run completed |
| `experiment.failed` | Experiment run failed |
| `measurement.created` | New measurement created |
| `measurement.started` | Measurement started |
| `measurement.completed` | Measurement completed |
| `recommendation.generated` | New recommendations generated |
| `analysis.completed` | Analysis task completed |

## Hermes Integration

Sophia integrates with Hermes for service discovery and cross-component communication.

### Registering with Hermes

```python
from sophia.utils.tekton_utils import register_with_hermes

# Register Sophia with Hermes
success, api_key = register_with_hermes(
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

if success:
    print(f"Successfully registered with Hermes: {api_key}")
else:
    print("Failed to register with Hermes")
```

### Discovering Sophia via Hermes

From another component:

```python
import requests

def discover_sophia():
    response = requests.get(
        "http://localhost:8002/api/services",
        params={"capability": "intelligence-measurement"}
    )
    
    services = response.json()
    for service in services:
        if service["name"] == "Sophia":
            return service["endpoints"]["http"]
    
    return None

sophia_endpoint = discover_sophia()
if sophia_endpoint:
    print(f"Found Sophia at: {sophia_endpoint}")
else:
    print("Sophia not found")
```

### Sending Messages to Sophia via Hermes

```python
import requests

def send_message_via_hermes(message):
    response = requests.post(
        "http://localhost:8002/api/messages",
        json={
            "destination": "Sophia",
            "message_type": "command",
            "payload": message
        }
    )
    
    return response.json()

# Request an intelligence measurement
result = send_message_via_hermes({
    "command": "measure_model",
    "parameters": {
        "model": "gpt-4",
        "dimensions": ["reasoning", "knowledge"]
    }
})

print(f"Message sent, tracking ID: {result['tracking_id']}")
```

## CLI Integration

The Sophia CLI can be integrated into scripts and workflows.

### Basic CLI Usage

```bash
# Create an experiment from a script
experiment_id=$(sophia experiment create \
  --name "Automated Test" \
  --models "gpt-4,gpt-3.5-turbo" \
  --dimensions "reasoning,knowledge" \
  --output json | jq -r '.id')

echo "Created experiment: $experiment_id"

# Run the experiment
run_id=$(sophia experiment run --id "$experiment_id" --output json | jq -r '.run_id')

echo "Started run: $run_id"

# Wait for completion
while true; do
  status=$(sophia experiment status --id "$run_id" --output json | jq -r '.status')
  echo "Status: $status"
  
  if [ "$status" = "completed" ] || [ "$status" = "failed" ]; then
    break
  fi
  
  sleep 30
done

# Get results
sophia experiment results --id "$run_id" --output json > results.json
```

### Scripting with Python Subprocess

```python
import subprocess
import json

def run_sophia_command(command, args=None):
    cmd = ["sophia"] + command.split() + (args or [])
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Command failed: {result.stderr}")
        
    return json.loads(result.stdout)

# Create measurement
measurement = run_sophia_command("measure --model gpt-4 --dimensions reasoning --output json")
measurement_id = measurement["id"]

# Get results when ready
import time
while True:
    status = run_sophia_command(f"measurement status --id {measurement_id} --output json")
    if status["status"] == "completed":
        results = run_sophia_command(f"measurement results --id {measurement_id} --output json")
        break
    time.sleep(10)

print(f"Reasoning score: {results['dimensions']['reasoning']['overall']}/100")
```

## Integration with Other Tekton Components

### Integrating with Rhetor

Use Sophia's intelligence measurements to guide Rhetor's prompt engineering:

```python
from sophia.client import SophiaClient
from rhetor.client import RhetorClient

# Initialize clients
sophia = SophiaClient("http://localhost:8005", "sk_sophia_api_key")
rhetor = RhetorClient("http://localhost:8007", "sk_rhetor_api_key")

# Analyze model strengths
measurement = sophia.measure_model(
    model="gpt-4",
    dimensions=["reasoning", "creativity", "knowledge"]
)

# Wait for measurement completion
# ...

results = sophia.get_measurement_results(measurement['id'])

# Create optimized templates based on strengths
if results['dimensions']['reasoning']['overall'] > 85:
    # Create template optimized for reasoning tasks
    rhetor.create_template(
        name="reasoning_optimized",
        content="Think through this step-by-step: {{problem}}",
        variables=[{"name": "problem", "type": "string", "required": True}]
    )

if results['dimensions']['creativity']['overall'] > 80:
    # Create template optimized for creative tasks
    rhetor.create_template(
        name="creativity_optimized",
        content="Explore multiple creative approaches to: {{task}}",
        variables=[{"name": "task", "type": "string", "required": True}]
    )
```

### Integrating with Prometheus for Planning

Use Sophia's recommendations to inform Prometheus project planning:

```python
from sophia.client import SophiaClient
from prometheus.client import PrometheusClient

# Initialize clients
sophia = SophiaClient("http://localhost:8005", "sk_sophia_api_key")
prometheus = PrometheusClient("http://localhost:8003", "sk_prometheus_api_key")

# Generate improvement recommendations
recommendations = sophia.generate_recommendations(
    model="gpt-4",
    based_on="measurement_123",
    dimensions=["reasoning", "problem_solving"]
)

# Create tasks in Prometheus for each high-priority recommendation
for dimension, recs in recommendations['dimensions'].items():
    for rec in recs:
        if rec['priority'] >= 8:  # High priority
            # Create task in Prometheus
            prometheus.create_task(
                title=f"Implement {rec['title']}",
                description=rec['description'],
                priority="high",
                estimated_hours=rec['estimated_effort_hours'],
                category="model-improvement"
            )
```

### Integrating with Engram for Memory

Store measurement results in Engram for long-term reference:

```python
from sophia.client import SophiaClient
import requests
import json

# Initialize Sophia client
sophia = SophiaClient("http://localhost:8005", "sk_sophia_api_key")

# Get measurement results
results = sophia.get_measurement_results("measurement_456")

# Store in Engram
engram_url = "http://localhost:8001/api/memory"
response = requests.post(
    engram_url,
    json={
        "text": json.dumps(results),
        "metadata": {
            "type": "sophia_measurement",
            "model": results["model"],
            "dimensions": list(results["dimensions"].keys()),
            "date": results["completed_at"]
        }
    }
)

if response.status_code == 200:
    memory_id = response.json()["id"]
    print(f"Stored in Engram with ID: {memory_id}")
```

## Integration Patterns

### Webhook Integration

Set up webhooks to notify external systems of Sophia events:

```python
# Register a webhook
response = requests.post(
    "http://localhost:8005/api/webhooks",
    headers={"Authorization": f"Bearer {api_key}"},
    json={
        "url": "https://your-application.com/webhooks/sophia",
        "events": ["experiment.completed", "measurement.completed"],
        "secret": "your_webhook_secret"  # Used for signature verification
    }
)

webhook_id = response.json()["id"]
```

Receiving webhook notifications:

```python
from flask import Flask, request, jsonify
import hmac
import hashlib

app = Flask(__name__)

@app.route("/webhooks/sophia", methods=["POST"])
def sophia_webhook():
    # Verify signature
    signature = request.headers.get("X-Sophia-Signature")
    payload = request.data
    secret = "your_webhook_secret"
    
    expected_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_signature):
        return jsonify({"error": "Invalid signature"}), 401
    
    # Process the webhook payload
    data = request.json
    event_type = data["type"]
    
    if event_type == "experiment.completed":
        # Handle completed experiment
        experiment_id = data["experiment_id"]
        run_id = data["run_id"]
        print(f"Experiment {experiment_id} completed with run {run_id}")
        
        # Fetch results and process them
        # ...
    
    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(port=5000)
```

### Scheduled Integration

Set up scheduled tasks to run periodic measurements:

```python
from sophia.client import SophiaClient
import schedule
import time

sophia = SophiaClient("http://localhost:8005", "sk_sophia_api_key")

def run_weekly_measurement():
    print("Running weekly measurement...")
    measurement = sophia.measure_model(
        model="gpt-4",
        dimensions=["reasoning", "knowledge", "problem_solving"],
        parameters={
            "test_cases": 20,
            "consistent_test_set": True  # Use same test cases each time
        }
    )
    print(f"Started measurement: {measurement['id']}")

# Schedule weekly measurement
schedule.every().monday.at("09:00").do(run_weekly_measurement)

# Run the scheduler
while True:
    schedule.run_pending()
    time.sleep(60)
```

### Database Integration

Store Sophia results in your own database:

```python
from sophia.client import SophiaClient
import sqlite3
import json

sophia = SophiaClient("http://localhost:8005", "sk_sophia_api_key")

# Create database connection
conn = sqlite3.connect("model_performance.db")
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS measurements (
    id TEXT PRIMARY KEY,
    model TEXT,
    date TEXT,
    dimensions TEXT,
    results TEXT
)
''')

# Get measurement results
results = sophia.get_measurement_results("measurement_789")

# Store in database
cursor.execute(
    "INSERT INTO measurements VALUES (?, ?, ?, ?, ?)",
    (
        results["id"],
        results["model"],
        results["completed_at"],
        json.dumps(list(results["dimensions"].keys())),
        json.dumps(results)
    )
)

conn.commit()
conn.close()
```

## Security Considerations

### API Key Management

- Store API keys securely (environment variables, secrets manager)
- Use different API keys for different integrations
- Rotate API keys periodically
- Set appropriate permissions for each API key

### Webhook Security

- Verify webhook signatures to prevent spoofing
- Use HTTPS for all webhook endpoints
- Implement IP allow-listing for webhook sources
- Set up rate limiting on webhook endpoints

### Data Protection

- Be aware of potential sensitive data in measurements
- Consider data retention policies for stored results
- Encrypt sensitive data in transit and at rest
- Implement access controls for Sophia integration points

## Best Practices

1. **Error Handling**: Implement robust error handling for all API calls
2. **Retry Logic**: Add retry logic for failed requests with exponential backoff
3. **Async Operations**: Use asynchronous APIs for long-running operations
4. **Resource Cleanup**: Close connections and release resources properly
5. **Versioned Integration**: Specify API version in your integrations
6. **Monitoring**: Set up monitoring for integration health
7. **Rate Limiting**: Respect API rate limits to prevent throttling
8. **Batch Operations**: Use batch endpoints for multiple operations
9. **Logging**: Implement comprehensive logging for debugging
10. **Documentation**: Keep integration documentation updated with changes

## Troubleshooting

### Common Integration Issues

1. **Connection Failures**
   - Check network connectivity
   - Verify Sophia is running and accessible
   - Check firewall or proxy configurations

2. **Authentication Errors**
   - Verify API key is valid and has not expired
   - Check API key permissions
   - Ensure correct authorization header format

3. **Timeout Errors**
   - Increase timeout settings for long-running operations
   - Consider using asynchronous endpoints
   - Check Sophia server load and performance

4. **Data Format Issues**
   - Validate request payload format
   - Check for correct Content-Type headers
   - Verify JSON structure matches API requirements

### Debugging Integration

Enable detailed logging in your integration:

```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("sophia_integration.log"),
        logging.StreamHandler()
    ]
)
```

Diagnose connectivity issues:

```bash
# Test basic connectivity
curl -v http://localhost:8005/api/status

# Test authentication
curl -v -H "Authorization: Bearer your_api_key" http://localhost:8005/api/auth/verify
```

## Conclusion

This guide covers the various ways to integrate with Sophia. For more detailed information about specific API endpoints, refer to the [API Reference](./API_REFERENCE.md).

If you encounter issues or need assistance with integration, please refer to the [Tekton Documentation](../../README.md) for community support options.