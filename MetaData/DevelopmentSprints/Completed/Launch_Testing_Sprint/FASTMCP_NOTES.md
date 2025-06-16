# FastMCP Development Sprint Notes

## Temporary Workarounds Implemented

### 1. Database MCP Server

A minimal implementation of the Database MCP Server has been created at `/scripts/run_database_mcp.py`. This is a temporary workaround to allow Hermes to start properly. The current implementation:

- Provides a basic heartbeat function
- Handles SIGINT and SIGTERM signals for graceful shutdown
- Runs on port 8011 by default
- Does not implement actual database operations

This stub should be replaced with a proper implementation during the FastMCP sprint that fully implements:

1. Database operations interface
2. Proper channel creation and management
3. Integration with message bus for database events
4. Full implementation of async methods for database operations
5. Metrics collection for database operations

### 2. MessageBus Async Methods

The `MessageBus` class in `hermes/core/message_bus.py` was missing async methods required by other components. The following methods were added:

```python
async def create_channel(self, channel_name: str, description: str = "") -> bool:
    """
    Create a new channel for message exchange.
    
    Args:
        channel_name: Name of the channel to create
        description: Optional description of the channel
        
    Returns:
        True if channel creation successful
    """
    logger.info(f"Creating channel: {channel_name} - {description}")
    
    # For now, this is a stub implementation that just logs the request
    # and returns success. In a real implementation, this would create
    # the channel in the message broker.
    
    # Add a subscription entry for this channel if it doesn't exist
    if channel_name not in self.subscriptions:
        self.subscriptions[channel_name] = set()
        
    return True
```

```python
async def subscribe(self, topic: str, callback: Callable[[Dict[str, Any]], None]) -> bool:
    """
    Subscribe to a topic (async version).
    
    Args:
        topic: Topic to subscribe to
        callback: Function to call when a message is received
        
    Returns:
        True if subscription successful
    """
    # Avoid recursion by implementing directly
    if topic not in self.subscriptions:
        self.subscriptions[topic] = set()
    
    # Add callback
    self.subscriptions[topic].add(callback)
    
    logger.info(f"Subscribed to topic {topic} (async)")
    return True
```

```python
async def publish(self, topic: str, message: Any, headers: Optional[Dict[str, Any]] = None) -> bool:
    """
    Publish a message to a topic (async version).
    
    Args:
        topic: Topic to publish to
        message: Message to publish (will be serialized)
        headers: Optional message headers
        
    Returns:
        True if publication successful
    """
    # Create message envelope
    headers = headers or {}
    headers["timestamp"] = time.time()
    headers["topic"] = topic
    
    envelope = {
        "headers": headers,
        "payload": message
    }
    
    # Serialize to JSON
    try:
        message_json = json.dumps(envelope)
    except TypeError:
        logger.error(f"Cannot serialize message for topic {topic}")
        return False
    
    # TODO: Implement actual message publication
    logger.info(f"Publishing message to topic {topic} (async)")
    
    # Store in history if enabled
    if self.history_size > 0:
        if topic not in self.history:
            self.history[topic] = []
        
        self.history[topic].append(envelope)
        
        # Trim history if needed
        if len(self.history[topic]) > self.history_size:
            self.history[topic] = self.history[topic][-self.history_size:]
    
    # Deliver to local subscribers
    await self._deliver_to_subscribers_async(topic, envelope)
    
    return True
```

These implementations are functional but minimal. The FastMCP sprint should implement more robust versions with proper error handling, retry mechanisms, and integration with message brokers.

### 3. Bash Compatibility

The original code used Bash 4.x features (`${component,,}` for lowercase conversion) which don't work on macOS's default Bash 3.2. This was replaced with POSIX-compatible code:

```bash
# Create log file name - use lowercase component name, compatible with bash 3.2
local component_lower=$(echo "$component" | tr '[:upper:]' '[:lower:]')
local log_file="$log_dir/${component_lower}.log"
```

Consider standardizing on a minimum Bash version for the project or ensuring all scripts are compatible with Bash 3.2 for maximum portability.

## Recommendations for FastMCP Implementation

1. **Implement Proper Message Broker Integration**
   - Replace the stub implementations with actual message broker connections
   - Consider using RabbitMQ, Redis, or ZeroMQ for the message bus
   - Implement proper serialization/deserialization with schema validation

2. **Standardize Async Patterns**
   - Ensure consistency in async/await usage throughout the codebase
   - Add proper error handling for async operations
   - Implement timeouts for all async operations
   - Consider using a task queue for long-running operations

3. **Enhance Component Management**
   - Create a standardized component lifecycle management interface
   - Implement health checks for all components
   - Add automatic restart capability for failed components
   - Implement graceful degradation when components are unavailable

4. **Improve Port Management**
   - Enhance port conflict resolution
   - Add automatic port assignment for development environments
   - Implement proper port release on component shutdown
   - Consider using Unix domain sockets for inter-component communication on same host

5. **Centralize Configuration**
   - Implement a central configuration system for all components
   - Add configuration validation
   - Support environment-specific configuration
   - Add runtime configuration updates