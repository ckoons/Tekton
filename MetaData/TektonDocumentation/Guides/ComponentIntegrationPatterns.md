# Component Integration Patterns Guide

## Overview

This guide documents the standard patterns for integrating components within the Tekton ecosystem. Following these patterns ensures consistent, reliable, and maintainable integrations across all components.

## Core Integration Principles

### 1. Single Port Architecture

Each component operates on a single port with path-based routing:

```python
# Component configuration
COMPONENT_PORT = 8005  # Unique per component
AI_PORT = 45005       # CI specialist port (45000 + (COMPONENT_PORT - 8000))

# Path routing
/api/v1/*     # REST API endpoints
/ws           # WebSocket connections
/events       # Server-sent events
/health       # Health check endpoint
```

### 2. Service Discovery via Hermes

All components register with Hermes for automatic discovery:

```python
from hermes.api.client import HermesClient

async def register_component():
    hermes = HermesClient(host="localhost", port=8000)
    
    registration = {
        "component": "my_component",
        "version": "1.0.0",
        "description": "Component description",
        "host": "localhost",
        "port": 8005,
        "health_check": "/health",
        "capabilities": ["feature1", "feature2"],
        "dependencies": ["hermes", "engram"],
        "endpoints": [
            {
                "path": "/api/v1/process",
                "methods": ["POST"],
                "description": "Process data"
            }
        ]
    }
    
    response = await hermes.register_component(registration)
    return response
```

### 3. Standardized Communication

Use consistent patterns for inter-component communication:

```python
# Client pattern
class ComponentClient:
    def __init__(self, host="localhost", port=None):
        self.host = host
        self.port = port or self._discover_port()
        self.base_url = f"http://{self.host}:{self.port}"
    
    def _discover_port(self):
        # Discover via Hermes
        hermes = HermesClient()
        component = hermes.discover_component(self.__class__.__name__)
        return component["port"]
    
    async def call_api(self, endpoint, method="GET", data=None):
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                f"{self.base_url}/api/v1/{endpoint}",
                json=data
            )
            return response.json()
```

## Integration Patterns

### Pattern 1: Request-Response Integration

For synchronous operations between components:

```python
from typing import Dict, Any
import httpx

class SyncIntegration:
    def __init__(self, target_component: str):
        self.target = target_component
        self.client = httpx.Client(timeout=30.0)
        self._discover_endpoint()
    
    def _discover_endpoint(self):
        hermes = HermesClient()
        info = hermes.discover_component(self.target)
        self.base_url = f"http://{info['host']}:{info['port']}"
    
    def request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = self.client.post(
                f"{self.base_url}/api/v1/{endpoint}",
                json=data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            # Handle errors appropriately
            return {"error": str(e)}

# Usage
integration = SyncIntegration("rhetor")
result = integration.request("generate", {
    "prompt": "Explain quantum computing",
    "max_tokens": 500
})
```

### Pattern 2: Event-Driven Integration

For asynchronous, event-based communication:

```python
import asyncio
from typing import Callable
import websockets

class EventIntegration:
    def __init__(self, component: str):
        self.component = component
        self.handlers = {}
        self._discover_websocket()
    
    def _discover_websocket(self):
        hermes = HermesClient()
        info = hermes.discover_component(self.component)
        self.ws_url = f"ws://{info['host']}:{info['port']}/ws"
    
    def on_event(self, event_type: str):
        def decorator(func: Callable):
            self.handlers[event_type] = func
            return func
        return decorator
    
    async def connect(self):
        async with websockets.connect(self.ws_url) as websocket:
            # Send subscription message
            await websocket.send(json.dumps({
                "type": "subscribe",
                "events": list(self.handlers.keys())
            }))
            
            # Handle incoming events
            async for message in websocket:
                event = json.loads(message)
                if event["type"] in self.handlers:
                    await self.handlers[event["type"]](event["data"])

# Usage
events = EventIntegration("harmonia")

@events.on_event("workflow.completed")
async def handle_completion(data):
    print(f"Workflow {data['workflow_id']} completed")

# Run event loop
asyncio.run(events.connect())
```

### Pattern 3: Streaming Integration

For real-time data streams:

```python
import asyncio
from typing import AsyncIterator

class StreamIntegration:
    def __init__(self, component: str):
        self.component = component
        self._discover_endpoint()
    
    def _discover_endpoint(self):
        hermes = HermesClient()
        info = hermes.discover_component(self.component)
        self.base_url = f"http://{info['host']}:{info['port']}"
    
    async def stream(self, endpoint: str, params: dict) -> AsyncIterator[dict]:
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/v1/{endpoint}",
                json=params
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = json.loads(line[6:])
                        yield data

# Usage
stream = StreamIntegration("apollo")

async def monitor_metrics():
    async for metric in stream.stream("metrics/stream", {
        "components": ["rhetor", "engram"],
        "metrics": ["latency", "throughput"]
    }):
        print(f"Metric update: {metric}")

asyncio.run(monitor_metrics())
```

### Pattern 4: Batch Processing Integration

For efficient bulk operations:

```python
from typing import List, Dict
import asyncio

class BatchIntegration:
    def __init__(self, component: str, batch_size: int = 100):
        self.component = component
        self.batch_size = batch_size
        self.queue = asyncio.Queue()
        self._discover_endpoint()
    
    def _discover_endpoint(self):
        hermes = HermesClient()
        info = hermes.discover_component(self.component)
        self.base_url = f"http://{info['host']}:{info['port']}"
    
    async def add_item(self, item: dict):
        await self.queue.put(item)
    
    async def process_batch(self):
        batch = []
        
        # Collect items up to batch_size
        while len(batch) < self.batch_size:
            try:
                item = await asyncio.wait_for(
                    self.queue.get(), 
                    timeout=1.0
                )
                batch.append(item)
            except asyncio.TimeoutError:
                break
        
        if batch:
            # Process batch
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/batch",
                    json={"items": batch}
                )
                return response.json()
        
        return None
    
    async def run(self):
        while True:
            result = await self.process_batch()
            if result:
                print(f"Processed {len(result['processed'])} items")

# Usage
batch = BatchIntegration("metis")

async def main():
    # Start processor
    processor = asyncio.create_task(batch.run())
    
    # Add items
    for i in range(250):
        await batch.add_item({
            "task": f"Task {i}",
            "priority": "medium"
        })
    
    # Wait for processing
    await asyncio.sleep(5)

asyncio.run(main())
```

### Pattern 5: Circuit Breaker Integration

For resilient component communication:

```python
import time
from enum import Enum
from typing import Optional

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        return (
            self.last_failure_time and
            time.time() - self.last_failure_time >= self.recovery_timeout
        )
    
    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

# Usage with component integration
class ResilientIntegration:
    def __init__(self, component: str):
        self.component = component
        self.circuit_breaker = CircuitBreaker()
        self.client = ComponentClient(component)
    
    def request(self, endpoint: str, data: dict):
        return self.circuit_breaker.call(
            self.client.call_api,
            endpoint,
            "POST",
            data
        )
```

## State Management Patterns

### Pattern 6: Shared State via Engram

Using Engram for persistent state across components:

```python
from engram.client import EngramClient

class SharedStateIntegration:
    def __init__(self, namespace: str):
        self.namespace = namespace
        self.engram = EngramClient()
    
    async def save_state(self, key: str, state: dict):
        """Save component state to Engram."""
        await self.engram.store({
            "namespace": self.namespace,
            "key": key,
            "type": "state",
            "content": state,
            "metadata": {
                "timestamp": time.time(),
                "component": self.namespace
            }
        })
    
    async def load_state(self, key: str) -> Optional[dict]:
        """Load component state from Engram."""
        results = await self.engram.search({
            "namespace": self.namespace,
            "key": key,
            "type": "state"
        })
        
        if results:
            return results[0]["content"]
        return None
    
    async def sync_state(self, key: str, update_func):
        """Atomically update shared state."""
        current = await self.load_state(key)
        updated = update_func(current or {})
        await self.save_state(key, updated)
        return updated

# Usage
state = SharedStateIntegration("workflow_engine")

# Save state
await state.save_state("current_workflow", {
    "id": "wf-123",
    "status": "running",
    "progress": 0.5
})

# Update state atomically
await state.sync_state("current_workflow", 
    lambda s: {**s, "progress": 0.75}
)
```

## Workflow Integration Patterns

### Pattern 7: Multi-Component Workflow

Orchestrating operations across multiple components:

```python
from harmonia.client import HarmoniaClient

class WorkflowIntegration:
    def __init__(self):
        self.harmonia = HarmoniaClient()
    
    async def create_analysis_workflow(self, code: str):
        """Create a code analysis workflow using multiple components."""
        workflow = await self.harmonia.create_workflow({
            "name": "code_analysis_pipeline",
            "description": "Comprehensive code analysis",
            "tasks": [
                {
                    "id": "parse",
                    "component": "codex",
                    "action": "parse_code",
                    "input": {
                        "code": code,
                        "language": "python"
                    }
                },
                {
                    "id": "analyze_complexity",
                    "component": "sophia",
                    "action": "measure_complexity",
                    "input": {
                        "ast": "${tasks.parse.output.ast}"
                    },
                    "depends_on": ["parse"]
                },
                {
                    "id": "security_scan",
                    "component": "metis",
                    "action": "security_analysis",
                    "input": {
                        "code": code,
                        "ast": "${tasks.parse.output.ast}"
                    },
                    "depends_on": ["parse"]
                },
                {
                    "id": "generate_report",
                    "component": "rhetor",
                    "action": "create_report",
                    "input": {
                        "complexity": "${tasks.analyze_complexity.output}",
                        "security": "${tasks.security_scan.output}",
                        "template": "code_analysis"
                    },
                    "depends_on": ["analyze_complexity", "security_scan"]
                }
            ]
        })
        
        # Execute workflow
        execution = await self.harmonia.execute_workflow(workflow["id"])
        
        # Monitor execution
        return await self._monitor_execution(execution["id"])
    
    async def _monitor_execution(self, execution_id: str):
        """Monitor workflow execution until completion."""
        while True:
            status = await self.harmonia.get_execution_status(execution_id)
            
            if status["state"] in ["completed", "failed"]:
                return status
            
            await asyncio.sleep(1)

# Usage
workflow = WorkflowIntegration()
result = await workflow.create_analysis_workflow("""
def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
""")

print(f"Analysis complete: {result['output']['generate_report']}")
```

## Monitoring and Health Patterns

### Pattern 8: Component Health Monitoring

Implementing health checks and monitoring:

```python
from typing import Dict, List
import asyncio

class HealthMonitor:
    def __init__(self, components: List[str]):
        self.components = components
        self.health_status = {}
        self.hermes = HermesClient()
    
    async def check_component_health(self, component: str) -> dict:
        """Check health of a single component."""
        try:
            info = self.hermes.discover_component(component)
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"http://{info['host']}:{info['port']}/health"
                )
                
                if response.status_code == 200:
                    return {
                        "status": "healthy",
                        "component": component,
                        "details": response.json()
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "component": component,
                        "error": f"HTTP {response.status_code}"
                    }
        except Exception as e:
            return {
                "status": "unreachable",
                "component": component,
                "error": str(e)
            }
    
    async def monitor_all(self):
        """Continuously monitor all components."""
        while True:
            tasks = [
                self.check_component_health(comp) 
                for comp in self.components
            ]
            
            results = await asyncio.gather(*tasks)
            
            # Update status
            for result in results:
                self.health_status[result["component"]] = result
            
            # Check for issues
            unhealthy = [
                r for r in results 
                if r["status"] != "healthy"
            ]
            
            if unhealthy:
                await self._handle_unhealthy(unhealthy)
            
            await asyncio.sleep(30)  # Check every 30 seconds
    
    async def _handle_unhealthy(self, unhealthy: List[dict]):
        """Handle unhealthy components."""
        for component in unhealthy:
            print(f"ALERT: {component['component']} is {component['status']}")
            
            # Could trigger recovery actions here
            # await self.trigger_recovery(component)

# Usage
monitor = HealthMonitor([
    "hermes", "engram", "rhetor", "athena", "apollo"
])

asyncio.run(monitor.monitor_all())
```

## Security Patterns

### Pattern 9: Secure Inter-Component Communication

Implementing authentication and encryption:

```python
import jwt
import hashlib
from datetime import datetime, timedelta

class SecureIntegration:
    def __init__(self, component: str, secret_key: str):
        self.component = component
        self.secret_key = secret_key
        self.client = ComponentClient(component)
    
    def _generate_token(self) -> str:
        """Generate JWT token for authentication."""
        payload = {
            "iss": "my_component",
            "sub": self.component,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(minutes=5)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def _sign_request(self, data: dict) -> str:
        """Create signature for request integrity."""
        content = json.dumps(data, sort_keys=True)
        signature = hashlib.sha256(
            f"{content}{self.secret_key}".encode()
        ).hexdigest()
        
        return signature
    
    async def secure_request(self, endpoint: str, data: dict):
        """Make authenticated and signed request."""
        token = self._generate_token()
        signature = self._sign_request(data)
        
        headers = {
            "Authorization": f"Bearer {token}",
            "X-Signature": signature
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.client.base_url}/api/v1/{endpoint}",
                json=data,
                headers=headers
            )
            
            # Verify response signature
            response_sig = response.headers.get("X-Signature")
            expected_sig = self._sign_request(response.json())
            
            if response_sig != expected_sig:
                raise ValueError("Invalid response signature")
            
            return response.json()
```

## Testing Integration Patterns

### Pattern 10: Integration Testing

Testing component integrations:

```python
import pytest
from unittest.mock import Mock, patch

class IntegrationTest:
    @pytest.fixture
    def mock_hermes(self):
        """Mock Hermes for testing."""
        with patch('hermes.api.client.HermesClient') as mock:
            instance = mock.return_value
            instance.discover_component.return_value = {
                "host": "localhost",
                "port": 8005,
                "health_check": "/health"
            }
            yield instance
    
    @pytest.fixture
    def mock_component_response(self):
        """Mock component API responses."""
        with patch('httpx.AsyncClient') as mock:
            instance = mock.return_value.__aenter__.return_value
            instance.post.return_value.json.return_value = {
                "status": "success",
                "data": {"result": "test"}
            }
            yield instance
    
    @pytest.mark.asyncio
    async def test_component_integration(
        self, mock_hermes, mock_component_response
    ):
        """Test basic component integration."""
        integration = SyncIntegration("test_component")
        
        result = await integration.request("process", {"input": "test"})
        
        assert result["status"] == "success"
        assert result["data"]["result"] == "test"
        
        # Verify correct calls
        mock_hermes.discover_component.assert_called_with("test_component")
        mock_component_response.post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_circuit_breaker(self):
        """Test circuit breaker behavior."""
        breaker = CircuitBreaker(failure_threshold=3)
        
        # Simulate failures
        for _ in range(3):
            with pytest.raises(Exception):
                breaker.call(lambda: 1/0)
        
        # Circuit should be open
        assert breaker.state == CircuitState.OPEN
        
        # Should fail fast
        with pytest.raises(Exception, match="Circuit breaker is OPEN"):
            breaker.call(lambda: "success")
```

## Best Practices

### 1. Error Handling

Always implement comprehensive error handling:

```python
class RobustIntegration:
    async def safe_request(self, component: str, endpoint: str, data: dict):
        try:
            client = ComponentClient(component)
            return await client.call_api(endpoint, "POST", data)
        except httpx.TimeoutException:
            # Handle timeout
            logger.warning(f"Timeout calling {component}/{endpoint}")
            return {"error": "timeout", "component": component}
        except httpx.HTTPStatusError as e:
            # Handle HTTP errors
            logger.error(f"HTTP error {e.response.status_code}")
            return {"error": "http_error", "status": e.response.status_code}
        except Exception as e:
            # Handle unexpected errors
            logger.exception(f"Unexpected error calling {component}")
            return {"error": "internal_error", "message": str(e)}
```

### 2. Configuration Management

Centralize configuration:

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class IntegrationConfig:
    timeout: float = 30.0
    retry_count: int = 3
    retry_delay: float = 1.0
    circuit_breaker_threshold: int = 5
    batch_size: int = 100
    
    @classmethod
    def from_env(cls):
        return cls(
            timeout=float(os.getenv("INTEGRATION_TIMEOUT", "30.0")),
            retry_count=int(os.getenv("INTEGRATION_RETRY_COUNT", "3")),
            retry_delay=float(os.getenv("INTEGRATION_RETRY_DELAY", "1.0")),
            circuit_breaker_threshold=int(os.getenv("CIRCUIT_BREAKER_THRESHOLD", "5")),
            batch_size=int(os.getenv("INTEGRATION_BATCH_SIZE", "100"))
        )
```

### 3. Observability

Add logging and metrics:

```python
import structlog
from prometheus_client import Counter, Histogram

logger = structlog.get_logger()

# Metrics
integration_requests = Counter(
    'integration_requests_total',
    'Total integration requests',
    ['source', 'target', 'endpoint']
)

integration_duration = Histogram(
    'integration_duration_seconds',
    'Integration request duration',
    ['source', 'target', 'endpoint']
)

class ObservableIntegration:
    def __init__(self, source: str, target: str):
        self.source = source
        self.target = target
        self.logger = logger.bind(
            source=source,
            target=target
        )
    
    async def request(self, endpoint: str, data: dict):
        with integration_duration.labels(
            self.source, self.target, endpoint
        ).time():
            
            integration_requests.labels(
                self.source, self.target, endpoint
            ).inc()
            
            self.logger.info(
                "Making integration request",
                endpoint=endpoint,
                data_size=len(str(data))
            )
            
            try:
                result = await self._make_request(endpoint, data)
                self.logger.info(
                    "Integration request successful",
                    endpoint=endpoint
                )
                return result
            except Exception as e:
                self.logger.error(
                    "Integration request failed",
                    endpoint=endpoint,
                    error=str(e)
                )
                raise
```

### 4. Versioning

Handle API versioning:

```python
class VersionedIntegration:
    def __init__(self, component: str, version: str = "v1"):
        self.component = component
        self.version = version
        self.client = ComponentClient(component)
    
    async def request(self, endpoint: str, data: dict):
        # Include version in request
        versioned_endpoint = f"{self.version}/{endpoint}"
        
        # Add version header
        headers = {"X-API-Version": self.version}
        
        return await self.client.call_api(
            versioned_endpoint,
            "POST",
            data,
            headers=headers
        )
```

## Troubleshooting

### Common Integration Issues

#### 1. Service Discovery Failures
```python
# Debug service discovery
hermes = HermesClient()
components = hermes.list_components()
print(f"Registered components: {[c['name'] for c in components]}")

# Check specific component
try:
    info = hermes.discover_component("target_component")
    print(f"Component info: {info}")
except Exception as e:
    print(f"Discovery failed: {e}")
```

#### 2. Connection Issues
```python
# Test connectivity
async def test_connection(host: str, port: int):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://{host}:{port}/health",
                timeout=5.0
            )
            print(f"Connection successful: {response.status_code}")
    except Exception as e:
        print(f"Connection failed: {e}")

# Run test
asyncio.run(test_connection("localhost", 8005))
```

#### 3. Performance Issues
```python
# Profile integration performance
import time

async def profile_integration():
    times = []
    
    for _ in range(100):
        start = time.time()
        await integration.request("endpoint", {"data": "test"})
        times.append(time.time() - start)
    
    print(f"Average: {sum(times)/len(times):.3f}s")
    print(f"Min: {min(times):.3f}s")
    print(f"Max: {max(times):.3f}s")
    print(f"P95: {sorted(times)[95]:.3f}s")
```

## Related Documentation

- [Hermes Integration Guide](/MetaData/ComponentDocumentation/Hermes/INTEGRATION_GUIDE.md)
- [API Development Standards](/MetaData/TektonDocumentation/Standards/APIDevelopment.md)
- [WebSocket Communication](/MetaData/TektonDocumentation/Guides/WebSocketGuide.md)
- [Security Best Practices](/MetaData/TektonDocumentation/Security/BestPractices.md)
- [Testing Guidelines](/MetaData/TektonDocumentation/Testing/IntegrationTesting.md)