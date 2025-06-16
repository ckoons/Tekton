# Hermes Technical Documentation

## Architecture Overview

Hermes serves as the central message bus and service discovery system for the Tekton ecosystem. It facilitates communication between components through standardized protocols and maintains a registry of available services and their capabilities.

### Core Components

1. **Message Bus**
   - Provides publish/subscribe messaging patterns
   - Handles message routing between components
   - Implements message delivery guarantees
   - Supports synchronous and asynchronous communication

2. **Service Registry**
   - Maintains a catalog of available services
   - Stores service metadata and capabilities
   - Handles service registration and deregistration
   - Provides service lookup and discovery

3. **A2A Service**
   - Implements Agent-to-Agent communication protocol
   - Manages agent messages and conversations
   - Routes tasks between specialized agents
   - Maintains conversation context and history

4. **MCP Service**
   - Implements the Message Communication Protocol
   - Standardizes message formats across components
   - Provides message validation and transformation
   - Ensures protocol compatibility

5. **Database Manager**
   - Manages persistence for messages and service information
   - Implements data access patterns
   - Handles data migration and versioning
   - Provides transaction support

## Internal System Design

### Message Flow Architecture

Messages in Hermes follow a defined flow:

1. **Receipt**: Messages are received through HTTP API or WebSocket
2. **Validation**: Message format and content are validated
3. **Transformation**: Messages are transformed to internal format
4. **Routing**: Destination is determined based on message metadata
5. **Delivery**: Message is delivered to recipients
6. **Acknowledgment**: Delivery confirmation is sent to sender
7. **Persistence**: Messages may be persisted for history or retry

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Receipt   │     │  Validation │     │Transformation│     │   Routing   │
│             ├────►│             ├────►│             ├────►│             │
└─────────────┘     └─────────────┘     └─────────────┘     └──────┬──────┘
                                                                   │
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌──────▼──────┐
│ Persistence │     │Acknowledgment│     │  Delivery   │     │             │
│             │◄────┤             │◄────┤             │◄────┤             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

### Service Registration Process

The service registration process follows these steps:

1. **Initial Contact**: Service connects to Hermes registration endpoint
2. **Metadata Submission**: Service provides capabilities and connection info
3. **Validation**: Hermes validates service information
4. **Registration**: Service is added to the registry
5. **Heartbeat Setup**: Periodic heartbeat is established
6. **Availability Notification**: Other components are notified of new service

```python
class ServiceRegistry:
    def __init__(self, db_client):
        self.db_client = db_client
        self.services = {}  # In-memory cache of registered services
        
    async def register_service(self, service_info):
        # Validate service information
        self._validate_service_info(service_info)
        
        # Generate service ID if not provided
        service_id = service_info.get('id') or str(uuid.uuid4())
        service_info['id'] = service_id
        
        # Add registration timestamp
        service_info['registered_at'] = datetime.now().isoformat()
        
        # Store in database
        await self.db_client.insert_service(service_info)
        
        # Update in-memory cache
        self.services[service_id] = service_info
        
        # Publish service availability event
        await self._publish_service_event(service_id, 'registered')
        
        return service_id
```

## A2A Protocol Implementation

The Agent-to-Agent (A2A) protocol enables complex interactions between specialized agents:

### Message Structure

```json
{
  "id": "msg_123456789",
  "conversation_id": "conv_987654321",
  "sender": {
    "id": "agent_111",
    "type": "browser_agent"
  },
  "recipient": {
    "id": "agent_222",
    "type": "code_agent"
  },
  "content": {
    "type": "task",
    "task_type": "code_analysis",
    "payload": {
      "code": "function example() { return 'Hello World'; }",
      "language": "javascript",
      "analysis_type": "security"
    }
  },
  "metadata": {
    "priority": "high",
    "ttl_seconds": 3600
  },
  "timestamp": "2025-04-28T14:25:30.123Z"
}
```

### Conversation Management

The A2A service maintains conversations between agents:

```python
class ConversationManager:
    def __init__(self, db_client):
        self.db_client = db_client
        
    async def create_conversation(self, initiator_id, participants=None):
        conversation = {
            "id": f"conv_{uuid.uuid4().hex}",
            "initiator_id": initiator_id,
            "participants": participants or [initiator_id],
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "metadata": {}
        }
        
        await self.db_client.insert_conversation(conversation)
        return conversation
        
    async def add_message(self, conversation_id, message):
        # Validate conversation exists
        conversation = await self.db_client.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
            
        # Add message to conversation
        message["conversation_id"] = conversation_id
        message["timestamp"] = message.get("timestamp") or datetime.now().isoformat()
        
        await self.db_client.insert_message(message)
        
        # Update conversation last activity
        await self.db_client.update_conversation(
            conversation_id,
            {"updated_at": datetime.now().isoformat()}
        )
        
        return message
```

## MCP Implementation

The Message Communication Protocol (MCP) standardizes how components communicate:

### Protocol Structure

```
+----------------+
| Message Header |
|                |
| - id           |
| - type         |
| - source       |
| - destination  |
| - timestamp    |
+----------------+
|                |
| Message Body   |
|                |
+----------------+
|                |
| Message Footer |
| - checksum     |
| - version      |
+----------------+
```

### Message Types

The MCP supports various message types:

1. **Request**: Component requests information or action
2. **Response**: Reply to a request with results
3. **Event**: Notification of system event
4. **Command**: Instruction to perform specific action
5. **Status**: Component status update

```python
class MCPMessage:
    def __init__(self, msg_type, source, destination=None, body=None, id=None):
        self.id = id or str(uuid.uuid4())
        self.type = msg_type
        self.source = source
        self.destination = destination
        self.body = body or {}
        self.timestamp = datetime.now().isoformat()
        self.version = "1.0"
        
    def to_dict(self):
        return {
            "header": {
                "id": self.id,
                "type": self.type,
                "source": self.source,
                "destination": self.destination,
                "timestamp": self.timestamp,
                "version": self.version
            },
            "body": self.body,
            "footer": {
                "checksum": self._calculate_checksum()
            }
        }
        
    def _calculate_checksum(self):
        # Implementation of checksum calculation
        serialized = json.dumps(self.body, sort_keys=True)
        return hashlib.md5(serialized.encode()).hexdigest()
```

## Database Integration

Hermes uses a flexible database architecture for persistence:

### Database Adapters

The system supports multiple database backends through adapters:

```python
class DatabaseAdapter:
    """Base class for database adapters"""
    
    async def connect(self):
        """Establish connection to the database"""
        raise NotImplementedError
        
    async def disconnect(self):
        """Close database connection"""
        raise NotImplementedError
        
    async def insert_service(self, service_info):
        """Insert service registration information"""
        raise NotImplementedError
        
    async def get_service(self, service_id):
        """Retrieve service by ID"""
        raise NotImplementedError
        
    async def list_services(self, filter_criteria=None):
        """List services matching criteria"""
        raise NotImplementedError
        
    async def update_service(self, service_id, updates):
        """Update service information"""
        raise NotImplementedError
        
    async def delete_service(self, service_id):
        """Remove service from registry"""
        raise NotImplementedError
```

Specific implementations exist for SQLite, PostgreSQL, and in-memory storage.

### Schema Design

The core database schema includes these primary tables:

1. **services**: Registered service information
2. **messages**: Message history and pending deliveries
3. **conversations**: A2A conversation tracking
4. **heartbeats**: Service health monitoring
5. **subscriptions**: Message topic subscriptions

## Vector Engine Integration

Hermes integrates with vector databases for semantic message routing:

```python
class VectorEngine:
    def __init__(self, vector_store_client):
        self.vector_store = vector_store_client
        
    async def initialize(self):
        await self.vector_store.connect()
        
    async def index_message(self, message):
        """Index message content for semantic search"""
        content = self._extract_content(message)
        embedding = await self._generate_embedding(content)
        
        metadata = {
            "message_id": message["id"],
            "timestamp": message["timestamp"],
            "source": message["source"],
            "type": message["type"]
        }
        
        return await self.vector_store.insert(embedding, metadata)
        
    async def find_similar_messages(self, query_text, limit=10):
        """Find semantically similar messages"""
        embedding = await self._generate_embedding(query_text)
        results = await self.vector_store.search(embedding, limit=limit)
        
        # Fetch full messages using IDs
        message_ids = [r["metadata"]["message_id"] for r in results]
        return await self._fetch_messages(message_ids)
```

## Error Handling and Recovery

Hermes implements robust error handling and recovery mechanisms:

### Message Delivery Guarantees

For critical messages, Hermes ensures at-least-once delivery:

1. **Persistence**: Messages are persisted before delivery attempt
2. **Acknowledgment**: Recipients must acknowledge receipt
3. **Retry**: Failed deliveries are retried with backoff
4. **Dead Letter**: Messages that can't be delivered are moved to dead letter queue
5. **Monitoring**: Failed deliveries trigger alerts

### Service Health Monitoring

Service health is continuously monitored:

1. **Heartbeats**: Services send periodic heartbeats
2. **Timeouts**: Missing heartbeats trigger health checks
3. **Circuit Breaking**: Failing services are temporarily excluded from routing
4. **Auto-Recovery**: Services automatically return to rotation when healthy
5. **Admin Alerts**: Persistent health issues trigger administrator alerts

## Performance Optimization

Hermes is optimized for high-throughput message processing:

### Message Batching

Messages are batched for efficient processing:

```python
class MessageBatcher:
    def __init__(self, max_batch_size=100, max_wait_ms=50):
        self.max_batch_size = max_batch_size
        self.max_wait_ms = max_wait_ms
        self.batches = defaultdict(list)
        self.timers = {}
        
    async def add_message(self, destination, message):
        """Add message to batch for destination"""
        self.batches[destination].append(message)
        
        # Start timer if this is first message in batch
        if len(self.batches[destination]) == 1:
            self.timers[destination] = asyncio.create_task(
                self._timer_elapsed(destination)
            )
            
        # Process immediately if batch is full
        if len(self.batches[destination]) >= self.max_batch_size:
            return await self._process_batch(destination)
            
    async def _timer_elapsed(self, destination):
        """Wait for max_wait_ms then process batch"""
        await asyncio.sleep(self.max_wait_ms / 1000)
        await self._process_batch(destination)
        
    async def _process_batch(self, destination):
        """Process all messages in batch for destination"""
        if destination not in self.batches:
            return []
            
        # Get messages and clear batch
        messages = self.batches[destination]
        del self.batches[destination]
        
        # Cancel timer if it exists
        if destination in self.timers:
            self.timers[destination].cancel()
            del self.timers[destination]
            
        # Actual delivery implementation
        # ...
        
        return messages
```

### Connection Pooling

Connections to services are pooled for efficiency:

```python
class ConnectionPool:
    def __init__(self, min_size=5, max_size=20):
        self.min_size = min_size
        self.max_size = max_size
        self.pools = {}  # Destination -> pool mapping
        
    async def initialize(self):
        """Initialize minimum connections in pool"""
        # Implementation
        
    async def get_connection(self, destination):
        """Get connection from pool, creating if necessary"""
        if destination not in self.pools:
            self.pools[destination] = []
            
        # Return existing connection if available
        if self.pools[destination]:
            return self.pools[destination].pop()
            
        # Create new connection if below max size
        if len(self.pools[destination]) < self.max_size:
            return await self._create_connection(destination)
            
        # Wait for connection to become available
        return await self._wait_for_connection(destination)
        
    async def release_connection(self, destination, connection):
        """Return connection to pool"""
        if destination not in self.pools:
            self.pools[destination] = []
            
        self.pools[destination].append(connection)
```

## Security Implementation

Hermes implements several security measures:

### Authentication

Components authenticate using API keys or JWT tokens:

```python
class SecurityManager:
    def __init__(self, secret_key):
        self.secret_key = secret_key
        
    def generate_api_key(self, service_id, permissions=None):
        """Generate API key for service"""
        payload = {
            "service_id": service_id,
            "permissions": permissions or [],
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=365)).isoformat()
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        return token
        
    def validate_api_key(self, api_key):
        """Validate API key and return service ID"""
        try:
            payload = jwt.decode(api_key, self.secret_key, algorithms=["HS256"])
            
            # Check expiration
            expires_at = datetime.fromisoformat(payload["expires_at"])
            if expires_at < datetime.now():
                return None
                
            return payload["service_id"]
        except:
            return None
```

### Authorization

Access to topics and services is controlled through permissions:

```python
class PermissionsManager:
    def __init__(self, db_client):
        self.db_client = db_client
        
    async def check_permission(self, service_id, action, resource):
        """Check if service has permission for action on resource"""
        service = await self.db_client.get_service(service_id)
        if not service:
            return False
            
        permissions = service.get("permissions", [])
        
        # Check for wildcard permission
        if f"{action}:*" in permissions:
            return True
            
        # Check for specific permission
        if f"{action}:{resource}" in permissions:
            return True
            
        return False
```

## Deployment Architecture

Hermes can be deployed in various configurations:

### Single Instance

For simple deployments, a single Hermes instance works well:

```
┌─────────────────────┐
│                     │
│  Hermes Instance    │
│                     │
│  - Message Bus      │
│  - Service Registry │
│  - A2A Service      │
│  - MCP Service      │
│                     │
└─────────────────────┘
        ▲     ▲
        │     │
┌───────┴─┐ ┌─┴───────┐
│         │ │         │
│ Service │ │ Service │
│    A    │ │    B    │
│         │ │         │
└─────────┘ └─────────┘
```

### Distributed Deployment

For high availability, Hermes can be deployed in a distributed configuration:

```
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│             │ │             │ │             │
│   Hermes    │ │   Hermes    │ │   Hermes    │
│  Instance 1 │ │  Instance 2 │ │  Instance 3 │
│             │ │             │ │             │
└──────┬──────┘ └──────┬──────┘ └──────┬──────┘
       │               │               │
       └───────────────┼───────────────┘
                       │
              ┌────────┴────────┐
              │                 │
              │ Shared Database │
              │                 │
              └─────────────────┘
```

## API Implementation Details

The API implementation follows RESTful principles with these key endpoints:

### Registration API

- `POST /api/register`: Register a new service
- `GET /api/services`: List registered services
- `GET /api/services/{id}`: Get service details
- `DELETE /api/services/{id}`: Deregister a service

### Messaging API

- `POST /api/messages`: Send a message
- `GET /api/messages/{id}`: Get message details
- `POST /api/subscriptions`: Subscribe to a topic
- `DELETE /api/subscriptions/{id}`: Unsubscribe from a topic

### A2A API

- `POST /api/a2a/conversations`: Create a conversation
- `POST /api/a2a/conversations/{id}/messages`: Send message in conversation
- `GET /api/a2a/conversations/{id}`: Get conversation details

### MCP API

- `POST /api/mcp/send`: Send MCP message
- `GET /api/mcp/status`: Get MCP service status

## WebSocket Implementation

Hermes provides WebSocket endpoints for real-time communication:

### Client Connection

```javascript
const socket = new WebSocket('ws://hermes-server/ws');

socket.onopen = function(event) {
  console.log('Connected to Hermes');
  
  // Subscribe to topics
  socket.send(JSON.stringify({
    type: 'subscribe',
    topics: ['service-updates', 'system-events']
  }));
};

socket.onmessage = function(event) {
  const message = JSON.parse(event.data);
  console.log('Received message:', message);
  
  // Handle message based on type
  switch(message.type) {
    case 'service-update':
      handleServiceUpdate(message);
      break;
    case 'system-event':
      handleSystemEvent(message);
      break;
    default:
      console.log('Unknown message type:', message.type);
  }
};
```

### Server Implementation

```python
class WebSocketHandler:
    def __init__(self, message_bus):
        self.message_bus = message_bus
        self.connections = {}  # client_id -> WebSocketConnection
        self.subscriptions = defaultdict(set)  # topic -> {client_id, ...}
        
    async def on_connect(self, client_id, connection):
        """Handle new WebSocket connection"""
        self.connections[client_id] = connection
        
    async def on_disconnect(self, client_id):
        """Handle WebSocket disconnection"""
        if client_id in self.connections:
            del self.connections[client_id]
            
        # Remove client subscriptions
        for topic in self.subscriptions:
            if client_id in self.subscriptions[topic]:
                self.subscriptions[topic].remove(client_id)
                
    async def on_message(self, client_id, message):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            
            if data.get('type') == 'subscribe':
                await self._handle_subscribe(client_id, data.get('topics', []))
            elif data.get('type') == 'unsubscribe':
                await self._handle_unsubscribe(client_id, data.get('topics', []))
            elif data.get('type') == 'publish':
                await self._handle_publish(client_id, data.get('topic'), data.get('message'))
            else:
                await self._send_error(client_id, f"Unknown message type: {data.get('type')}")
                
        except json.JSONDecodeError:
            await self._send_error(client_id, "Invalid JSON message")
            
    async def _handle_subscribe(self, client_id, topics):
        """Subscribe client to topics"""
        for topic in topics:
            self.subscriptions[topic].add(client_id)
            
        # Confirm subscription
        await self._send_to_client(client_id, {
            "type": "subscription_confirm",
            "topics": topics
        })
```

## Conclusion

This technical documentation provides a comprehensive overview of Hermes' architecture, implementation details, and design considerations. Developers working with Hermes should reference this document for a deep understanding of the system's internal operation.

For practical usage guidance, please refer to the [Integration Guide](./INTEGRATION_GUIDE.md) document, which focuses on how to integrate with Hermes rather than its internal implementation.