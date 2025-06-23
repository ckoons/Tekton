# Terma Usage Guide

This guide provides detailed instructions for using Terma in different modes and integrating it with other Tekton components.

## Table of Contents

- [Standalone Mode](#standalone-mode)
- [Embedded Mode in Hephaestus UI](#embedded-mode-in-hephaestus-ui)
- [API Client Usage](#api-client-usage)
- [LLM Assistance Features](#llm-assistance-features)
- [Terminal Customization](#terminal-customization)
- [Advanced Usage Patterns](#advanced-usage-patterns)

## Standalone Mode

Terma can be run as a standalone terminal service, accessible through a web browser.

### Starting the Terma Server

To start the Terma server in standalone mode:

```bash
# Navigate to the Terma directory
cd Terma

# Start the server
python -m terma.cli.main
```

By default, the server will run on port 8765. You can customize this using environment variables:

```bash
# Set custom HTTP and WebSocket ports
export TERMA_PORT=9000
export TERMA_WS_PORT=9001
python -m terma.cli.main
```

### Accessing the Terminal

Once the server is running, you can create a terminal session and access it through your browser:

1. Create a session using the REST API:
   ```bash
   curl -X POST http://localhost:8765/api/sessions \
     -H "Content-Type: application/json" \
     -d '{"shell_command": "/bin/bash"}'
   ```

2. Note the session ID returned in the response:
   ```json
   {"session_id": "550e8400-e29b-41d4-a716-446655440000", "created_at": 1617184632.54}
   ```

3. Access the terminal in your browser:
   ```
   http://localhost:8765/terminal/launch?session_id=550e8400-e29b-41d4-a716-446655440000
   ```

### Using the Standalone Terminal

The standalone terminal interface provides:

- Full terminal emulation with support for most terminal applications
- Terminal settings (font size, theme, etc.)
- LLM assistance panel
- Session management
- Keyboard shortcuts

## Embedded Mode in Hephaestus UI

Terma is designed to integrate seamlessly with the Hephaestus UI framework.

### Installing Terma in Hephaestus

To install Terma in Hephaestus:

```bash
cd Terma
./install_in_hephaestus.sh
```

This script copies the necessary files to the Hephaestus UI components directory.

### Using Terma in Hephaestus

1. Open the Hephaestus UI in your browser
2. Select the Terma terminal component from the component selector
3. The terminal will initialize automatically and create a new session

### Component Communication

When embedded in Hephaestus, Terma can communicate with other components through:

1. **Direct service communication**: Using registered Tekton UI services
2. **Hermes messaging**: For asynchronous communication with other Tekton components

Example of accessing the Terma service from another component:

```javascript
// From another Hephaestus component
const termaService = window.tektonUI.services.termaService;

// Create a new terminal session
termaService.createSession().then(sessionId => {
  console.log(`Created terminal session: ${sessionId}`);
  
  // Connect to the session
  termaService.connectToSession(sessionId);
});

// Send a command to the current terminal session
termaService.sendInput('echo "Hello from another component"\n');
```

## API Client Usage

Terma provides a Python client for programmatic interaction with the terminal service.

### Python Client Example

```python
from examples.terminal_client import TermaClient
import asyncio

async def main():
    # Create a client
    client = TermaClient(base_url="http://localhost:8765")
    
    try:
        # Create a session
        session = await client.create_session()
        session_id = session["session_id"]
        print(f"Session created: {session_id}")
        
        # Write a command to the session
        await client.write_to_session(session_id, "echo 'Hello, Terma!'\n")
        
        # Wait a bit for command to execute
        await asyncio.sleep(1)
        
        # Read the output
        response = await client.read_from_session(session_id)
        print(f"Output: {response['data']}")
        
        # Close the session
        await client.close_session(session_id)
        print(f"Session closed: {session_id}")
    
    finally:
        # Clean up
        await client.close()

asyncio.run(main())
```

### Interactive Terminal Session

For interactive terminal sessions, use the WebSocket interface:

```python
async def run_interactive_session():
    client = TermaClient()
    
    # Create session
    session = await client.create_session()
    session_id = session["session_id"]
    
    # Connect WebSocket
    websocket = await client.connect_websocket(
        session_id,
        on_output=lambda data: print(data, end=""),
        on_error=lambda msg: print(f"\nError: {msg}")
    )
    
    # Main input loop
    while True:
        command = input()
        
        if command.lower() == "exit":
            break
            
        # Send command to terminal
        await client.send_input(websocket, command + "\n")
    
    # Close connection
    await websocket.close()
    await client.close_session(session_id)
```

## LLM Assistance Features

Terma's LLM assistance features provide AI-powered help with terminal commands and output analysis.

### Command Explanation

To get an explanation for a command, type the command followed by `?`:

```
find . -name "*.py" -type f | xargs grep "def " | wc -l?
```

This will send the command to the LLM adapter, which will explain what the command does. The explanation will appear in the LLM assistance panel.

### Output Analysis

To analyze the output of a command, append `?` after running the command:

```
# Run the command first
ping -c 4 google.com

# Then type ? to analyze the output
?
```

### Using Different LLM Providers

Terma supports multiple LLM providers through the LLM adapter:

1. Select a provider from the dropdown menu in the terminal UI
2. The selected provider/model combination will be used for all subsequent LLM requests

Advanced configuration can be done through the API:

```bash
# Set LLM provider and model
curl -X POST http://localhost:8765/api/llm/set \
  -H "Content-Type: application/json" \
  -d '{"provider": "openai", "model": "gpt-4"}'
```

## Terminal Customization

Terma offers various customization options for the terminal interface.

### Terminal Settings

The terminal settings dialog allows you to customize:

- Font size and family
- Terminal theme (color scheme)
- Cursor style and blink rate
- Scrollback buffer size

Settings are stored in local storage and applied across sessions.

### Terminal Modes

Terma supports two terminal modes:

1. **Advanced Mode**: Full terminal emulation using xterm.js with support for complex applications
2. **Simple Mode**: Simplified terminal for basic command execution

Toggle between modes using the mode switch button in the UI.

### Session Management

Multiple terminal sessions can be managed through the session selector dropdown:

- Create new sessions with different shell types (Bash, Python, Node.js)
- Switch between existing sessions
- Close sessions when no longer needed

## Advanced Usage Patterns

### Detached Terminals

You can detach a terminal to a separate window while keeping the session active:

1. Start a terminal session in the main UI
2. Click the "Detach" button
3. The terminal will open in a new browser window
4. The session remains active and can be rejoined from the main UI

### Programmatic Terminal Control

For automated testing or workflow automation, you can control Terma programmatically:

```python
async def automate_terminal():
    client = TermaClient()
    
    # Create a session
    session = await client.create_session()
    session_id = session["session_id"]
    
    # Execute a series of commands
    commands = [
        "cd /tmp",
        "mkdir -p test_dir",
        "cd test_dir",
        "echo 'Hello, world!' > test.txt",
        "cat test.txt",
        "cd ..",
        "rm -rf test_dir"
    ]
    
    for cmd in commands:
        # Send command
        await client.write_to_session(session_id, cmd + "\n")
        
        # Wait for execution
        await asyncio.sleep(0.5)
        
        # Read output
        response = await client.read_from_session(session_id)
        print(f"Command: {cmd}")
        print(f"Output: {response['data']}")
    
    # Close session
    await client.close_session(session_id)
```

### Integration with Hermes

To enable Hermes integration, set the `REGISTER_WITH_HERMES` environment variable:

```bash
export REGISTER_WITH_HERMES=true
export HERMES_API_URL=http://localhost:8000
python -m terma.cli.main
```

This allows Terma to:
- Register its capabilities with Hermes
- Receive messages from other components
- Publish events (session creation, terminal output, etc.)

### WebSocket Reconnection

The Terma client handles WebSocket reconnection automatically:

- If the connection is lost, it will attempt to reconnect
- The session state is preserved during reconnection
- Configurable retry logic with exponential backoff

### Multi-user Support

While Terma doesn't have built-in authentication, you can:

1. Set up a reverse proxy (e.g., Nginx) with authentication
2. Use session tokens to identify users
3. Implement custom session management to isolate user sessions