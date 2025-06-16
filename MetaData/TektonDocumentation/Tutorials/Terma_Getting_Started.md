# Getting Started with Terma

This guide will help you get started with Terma, the terminal integration system for Tekton. It covers installation, basic usage, and common tasks for both users and developers.

## Quick Start

### Installation

```bash
# Clone the Tekton repository
git clone https://github.com/yourusername/Tekton.git
cd Tekton/Terma

# Run the setup script
./setup.sh

# Start the Terma server
python -m terma.cli.main
```

### Verify Installation

Check if Terma is running correctly:

```bash
curl http://localhost:8765/health
```

You should receive a JSON response with status "healthy".

### Create a Terminal Session

Using curl:

```bash
curl -X POST http://localhost:8765/api/sessions \
  -H "Content-Type: application/json" \
  -d '{}'
```

You should receive a JSON response with a session ID:

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": 1617184632.54
}
```

### Access the Terminal

Open the following URL in your browser:

```
http://localhost:8765/terminal/launch?session_id=550e8400-e29b-41d4-a716-446655440000
```

Replace the session ID with the one you received from the previous step.

## Basic Usage

### Terminal Interface

The Terma terminal interface provides:

1. **Terminal Window**: The main area where terminal input and output are displayed
2. **Control Bar**: Buttons and dropdowns for managing the terminal
3. **LLM Assistant Panel**: AI-powered help for terminal commands

### Common Terminal Operations

- **Execute Commands**: Type commands in the terminal and press Enter
- **Terminal Scrolling**: Use the mouse wheel or scroll bar to navigate output
- **Copy/Paste**: Select text to copy, Ctrl+V or right-click to paste
- **Resize**: The terminal automatically resizes to fit its container

### Session Management

Terma supports multiple terminal sessions:

1. **Create a New Session**: Select "New Session" from the session dropdown
2. **Switch Sessions**: Select an existing session from the session dropdown
3. **Terminal Types**: Choose different shell types (Bash, Python, Node.js) from the terminal type dropdown

### LLM Assistance

Terma provides AI-powered assistance for terminal commands:

1. **Command Explanation**: Type a command followed by `?` (e.g., `ls -la?`)
2. **Output Analysis**: Run a command, then type `?` to analyze the output
3. **Assistance Panel**: View AI explanations in the assistance panel
4. **Toggle Panel**: Click the AI Assistant header to expand/collapse the panel

## Integration with Hephaestus UI

### Install in Hephaestus

To integrate Terma with the Hephaestus UI:

```bash
cd Terma
./install_in_hephaestus.sh
```

### Access in Hephaestus

1. Open the Hephaestus UI in your browser
2. Select the Terma terminal component from the component selector
3. The terminal will initialize automatically and create a new session

## Development Workflow

### Setup Development Environment

```bash
# Clone the Tekton repository
git clone https://github.com/yourusername/Tekton.git
cd Tekton/Terma

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
pip install -r requirements.txt
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_terminal.py

# Run with coverage
pytest --cov=terma
```

### Making Changes

1. Make changes to the code
2. Run tests to ensure functionality
3. Start the server to test manually
4. Update documentation if necessary

## Common Tasks

### Creating and Managing Sessions

#### Create a Session

```bash
curl -X POST http://localhost:8765/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"shell_command": "/bin/bash"}'
```

#### List Sessions

```bash
curl http://localhost:8765/api/sessions
```

#### Close a Session

```bash
curl -X DELETE http://localhost:8765/api/sessions/550e8400-e29b-41d4-a716-446655440000
```

### Interactive Communication

Using the Python client:

```python
import asyncio
from examples.terminal_client import TermaClient

async def main():
    # Create a client
    client = TermaClient()
    
    # Create a session
    session = await client.create_session()
    session_id = session["session_id"]
    
    # Connect WebSocket with output handler
    websocket = await client.connect_websocket(
        session_id,
        on_output=lambda data: print(data, end=""),
        on_error=lambda msg: print(f"\nError: {msg}")
    )
    
    # Send a command
    await client.send_input(websocket, "echo 'Hello, Terma!'\n")
    
    # Wait for output
    await asyncio.sleep(1)
    
    # Close connection
    await websocket.close()
    await client.close_session(session_id)

# Run the example
asyncio.run(main())
```

### Working with LLM Integration

#### Get Available LLM Providers

```bash
curl http://localhost:8765/api/llm/providers
```

#### Set LLM Provider and Model

```bash
curl -X POST http://localhost:8765/api/llm/set \
  -H "Content-Type: application/json" \
  -d '{"provider": "claude", "model": "claude-3-sonnet-20240229"}'
```

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TERMA_PORT` | HTTP API port | 8765 |
| `TERMA_WS_PORT` | WebSocket server port | 8767 |
| `TERMA_HOST` | Host interface to bind to | 0.0.0.0 |
| `REGISTER_WITH_HERMES` | Register with Hermes on startup | false |
| `HERMES_API_URL` | Hermes API URL | http://localhost:8000 |
| `TERMA_LOG_LEVEL` | Logging level | INFO |

### Configuration File

You can create a configuration file to customize Terma:

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8765,
    "ws_port": 8767
  },
  "session": {
    "cleanup_interval": 3600,
    "idle_timeout": 86400,
    "default_shell": "/bin/bash"
  },
  "llm": {
    "adapter_url": "http://localhost:8300",
    "adapter_ws_url": "ws://localhost:8300/ws",
    "provider": "claude",
    "model": "claude-3-sonnet-20240229"
  },
  "logging": {
    "level": "INFO",
    "file": "terma_server.log"
  }
}
```

Save this file and set `TERMA_CONFIG_PATH` to its location:

```bash
export TERMA_CONFIG_PATH=/path/to/config.json
python -m terma.cli.main
```

## Troubleshooting

### Common Issues

1. **Port Conflicts**:
   ```
   [ERROR] Address already in use
   ```
   
   Solution: Change the port using environment variables:
   ```bash
   TERMA_PORT=9000 TERMA_WS_PORT=9001 python -m terma.cli.main
   ```

2. **PTY Errors**:
   ```
   [ERROR] Failed to create valid PTY
   ```
   
   Solution: Ensure your system supports PTY:
   - On Windows, use WSL
   - On Linux/macOS, check that you have the required PTY libraries

3. **WebSocket Connection Failures**:
   ```
   WebSocket connection to 'ws://localhost:8767/ws/...' failed
   ```
   
   Solution:
   - Check that the WebSocket server is running
   - Verify that the port is correct
   - Check for firewall/proxy issues

4. **LLM Adapter Connection Issues**:
   ```
   [WARNING] Error connecting to LLM Adapter service
   ```
   
   Solution:
   - Ensure the LLM Adapter is running
   - Check the adapter URL in the configuration
   - Set `TERMA_LOG_LEVEL=DEBUG` for more detailed error information

### Getting Help

If you encounter issues not covered here:

1. Check the logs:
   ```bash
   TERMA_LOG_LEVEL=DEBUG python -m terma.cli.main
   ```

2. Run the tests to verify functionality:
   ```bash
   pytest
   ```

3. Check for open issues in the GitHub repository
4. File a new issue with detailed information about the problem

## Next Steps

Now that you're familiar with the basics of Terma, here are some next steps:

- Read the [Architecture Guide](./architecture.md) to understand Terma's design
- Explore the [API Reference](./api_reference.md) for details on Terma's APIs
- Check the [Integration Guide](./integration.md) for connecting with other systems
- See the [Developer Guide](./developer_guide.md) for extending Terma

## Examples

### Basic Terminal Client

```python
import asyncio
from examples.terminal_client import TermaClient

async def main():
    client = TermaClient()
    
    try:
        # Create a session
        session = await client.create_session()
        session_id = session["session_id"]
        print(f"Session created: {session_id}")
        
        # Define callbacks
        def on_output(data):
            print(data, end="")
        
        def on_error(message):
            print(f"\nError: {message}")
        
        def on_llm_response(content):
            print(f"\n--- LLM Assistance ---\n{content}\n-------------------")
        
        # Connect WebSocket
        websocket = await client.connect_websocket(
            session_id,
            on_output=on_output,
            on_error=on_error,
            on_llm_response=on_llm_response
        )
        
        # Execute commands
        commands = [
            "echo 'Hello, Terma!'",
            "date",
            "uname -a"
        ]
        
        for cmd in commands:
            print(f"\nExecuting: {cmd}")
            await client.send_input(websocket, cmd + "\n")
            await asyncio.sleep(1)  # Wait for output
        
        # Request LLM assistance
        await client.request_llm_assistance(websocket, "ls -la")
        await asyncio.sleep(3)  # Wait for LLM response
        
        # Close the session
        await websocket.close()
        await client.close_session(session_id)
    
    finally:
        # Clean up
        await client.close()

# Run the example
asyncio.run(main())
```

### JavaScript WebSocket Example

```javascript
// Create a WebSocket connection
const sessionId = "550e8400-e29b-41d4-a716-446655440000";  // Replace with actual session ID
const socket = new WebSocket(`ws://localhost:8765/ws/${sessionId}`);

// Connection opened
socket.addEventListener("open", (event) => {
    console.log("WebSocket connected");
    
    // Send a command
    socket.send(JSON.stringify({
        type: "input",
        data: "echo 'Hello from WebSocket!'\n"
    }));
});

// Listen for messages
socket.addEventListener("message", (event) => {
    const message = JSON.parse(event.data);
    
    switch (message.type) {
        case "output":
            console.log("Terminal output:", message.data);
            break;
        case "error":
            console.error("Terminal error:", message.message);
            break;
        case "llm_response":
            console.log("LLM response:", message.content);
            break;
    }
});

// Connection closed
socket.addEventListener("close", (event) => {
    console.log("WebSocket disconnected");
});

// Handle errors
socket.addEventListener("error", (event) => {
    console.error("WebSocket error:", event);
});
```