# Terma Developer Guide

This guide provides detailed information for developers who want to understand, extend, or modify the Terma terminal system.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Code Organization](#code-organization)
- [Core Concepts](#core-concepts)
- [Development Environment Setup](#development-environment-setup)
- [Adding New Features](#adding-new-features)
- [Testing](#testing)
- [UI Development](#ui-development)
- [API Extensions](#api-extensions)
- [Contributing Guidelines](#contributing-guidelines)

## Architecture Overview

Terma follows a layered architecture pattern with clear separation of concerns:

```
┌───────────────────────────────────────────┐
│                   UI Layer                │
└───────────────────────────────────────────┘
                     ▲
                     │
                     ▼
┌───────────────────────────────────────────┐
│               API Layer                   │
└───────────────────────────────────────────┘
                     ▲
                     │
                     ▼
┌───────────────────────────────────────────┐
│               Core Layer                  │
└───────────────────────────────────────────┘
                     ▲
                     │
                     ▼
┌───────────────────────────────────────────┐
│           Integration Layer               │
└───────────────────────────────────────────┘
```

For a more detailed explanation of the architecture, see the [architecture.md](./architecture.md) document.

## Code Organization

The Terma codebase is organized as follows:

```
terma/
├── __init__.py            # Package initialization
├── api/                   # API endpoints
│   ├── __init__.py
│   ├── app.py             # FastAPI application
│   ├── ui_server.py       # UI serving functionality
│   └── websocket.py       # WebSocket server
├── cli/                   # Command-line interface
│   ├── __init__.py
│   ├── launch.py          # Launch functions
│   └── main.py            # CLI entry point
├── core/                  # Core functionality
│   ├── __init__.py
│   ├── llm_adapter.py     # LLM integration
│   ├── session_manager.py # Terminal session management
│   └── terminal.py        # Terminal session implementation
├── integrations/          # External integrations
│   ├── __init__.py
│   └── hermes_integration.py # Hermes integration
└── utils/                 # Utility functions
    ├── __init__.py
    ├── config.py          # Configuration management
    └── logging.py         # Logging utilities
```

## Core Concepts

### Terminal Sessions

A terminal session represents a single PTY (pseudoterminal) process running a shell or other command. Each session has:

- A unique identifier (UUID)
- An associated PTY process
- Input/output streams
- Activity tracking for idle detection

Terminal sessions are managed by the `TerminalSession` class in `terminal.py`.

### Session Manager

The session manager handles the lifecycle of terminal sessions, including:

- Creating new sessions
- Closing sessions
- Finding sessions by ID
- Cleaning up idle sessions
- Managing connections
- Resource allocation

The session manager is implemented in the `SessionManager` class in `session_manager.py`.

### LLM Adapter

The LLM adapter provides integration with language models for terminal assistance:

- Command explanations
- Output analysis
- Error resolution
- Context management
- Multiple provider support

The LLM adapter is implemented in the `LLMAdapter` class in `llm_adapter.py`.

### WebSocket Communication

Terma uses WebSockets for real-time communication between the client and server:

- Terminal input/output streaming
- Resize events
- LLM assistance requests
- Status updates

The WebSocket server is implemented in `websocket.py`.

## Development Environment Setup

### Setting Up a Development Environment

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/Tekton.git
   cd Tekton/Terma
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**:
   ```bash
   pip install -e .
   pip install -r requirements.txt
   ```

4. **Run Terma in development mode**:
   ```bash
   python -m terma.cli.main --dev
   ```

### Development Tools

- **Code Editor**: VS Code with Python extension is recommended
- **API Testing**: Postman or curl for testing REST API
- **WebSocket Testing**: Websocket.org debugger or custom script
- **UI Development**: Browser with Developer Tools

## Adding New Features

### Adding a New API Endpoint

1. Identify the appropriate module in the API layer
2. Add your endpoint function with FastAPI decorator
3. Implement the required functionality
4. Add appropriate type hints and models
5. Update documentation
6. Add tests

Example:

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..core.session_manager import SessionManager

router = APIRouter()

class SessionStatsModel(BaseModel):
    session_id: str
    commands_executed: int
    total_output_size: int

@router.get("/api/sessions/{session_id}/stats", response_model=SessionStatsModel)
async def get_session_stats(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Get statistics for a terminal session"""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
    # Implement statistics collection
    stats = {
        "session_id": session_id,
        "commands_executed": session.commands_executed,
        "total_output_size": session.total_output_size
    }
    
    return stats
```

### Adding a New Core Feature

1. Identify the appropriate module in the core layer
2. Implement your feature as a method or class
3. Add appropriate documentation
4. Update the API layer to expose the feature
5. Add tests

Example of adding command history to the terminal session:

```python
class TerminalSession:
    # ... existing code ...
    
    def __init__(self, session_id=None, shell_command=None):
        # ... existing code ...
        self.command_history = []
        
    def add_to_history(self, command):
        """Add a command to the session history
        
        Args:
            command: The command to add
        """
        # Don't add empty commands
        if not command.strip():
            return
            
        # Don't add duplicate consecutive commands
        if self.command_history and self.command_history[-1] == command:
            return
            
        self.command_history.append(command)
        # Limit history size
        if len(self.command_history) > 100:
            self.command_history.pop(0)
            
    def get_history(self):
        """Get the command history
        
        Returns:
            list: List of commands
        """
        return self.command_history
```

### Adding a New UI Component

1. Create or modify the HTML template
2. Add JavaScript functionality
3. Add CSS styles
4. Update the UI server to serve the component
5. Test in the browser

## Testing

### Running Tests

Terma uses pytest for testing. To run the tests:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_terminal.py

# Run tests with coverage
pytest --cov=terma
```

### Writing Tests

1. Create test files in the `tests` directory
2. Use pytest fixtures for setup/teardown
3. Test both success and failure cases
4. Mock external dependencies

Example test:

```python
import pytest
from terma.core.terminal import TerminalSession

def test_terminal_session_creation():
    # Create a terminal session
    session = TerminalSession(session_id="test-session")
    
    # Check basic properties
    assert session.session_id == "test-session"
    assert session.active is False
    assert session.pty is None
    
    # Start the session
    result = session.start()
    assert result is True
    assert session.active is True
    assert session.pty is not None
    
    # Clean up
    session.stop()
```

## UI Development

### Terminal UI Architecture

The terminal UI is built using:

- HTML templates with web component patterns
- JavaScript for terminal functionality
- CSS for styling
- xterm.js for terminal emulation

### Customizing the Terminal UI

To customize the terminal UI:

1. Modify the HTML template in `ui/hephaestus/terma-component.html`
2. Update the JavaScript in `ui/hephaestus/js/terma-component.js`
3. Add CSS styles in `ui/css/terma-terminal.css`

### UI Integration with Hephaestus

The Terma UI is designed to integrate with the Hephaestus UI framework:

- Uses Shadow DOM for encapsulation
- Follows Hephaestus component lifecycle
- Uses Hephaestus service registry
- Supports Hephaestus component communication

## API Extensions

### Adding WebSocket Message Types

To add a new WebSocket message type:

1. Add the message type handler in `websocket.py`
2. Update the client-side code to send and handle the message
3. Document the new message type

Example of adding a new "search" message type:

```python
async def handle_search_message(self, websocket, message, session_id):
    """Handle a search message
    
    Args:
        websocket: The WebSocket connection
        message: The message data
        session_id: The session ID
    """
    search_term = message.get('term')
    if not search_term:
        await websocket.send_json({
            'type': 'error',
            'message': 'Search term is required'
        })
        return
        
    session = self.session_manager.get_session(session_id)
    if not session:
        await websocket.send_json({
            'type': 'error',
            'message': f'Session {session_id} not found'
        })
        return
        
    # Implement search functionality
    results = session.search_output(search_term)
    
    # Send search results
    await websocket.send_json({
        'type': 'search_results',
        'results': results
    })
```

### Event System Extensions

To add new events to the Terma event system:

1. Identify the appropriate event trigger point
2. Define the event type and payload
3. Add the event emission code
4. Update the documentation

Example of adding a command execution event:

```python
async def handle_input_message(self, websocket, message, session_id):
    """Handle an input message
    
    Args:
        websocket: The WebSocket connection
        message: The message data
        session_id: The session ID
    """
    data = message.get('data')
    if not data:
        await websocket.send_json({
            'type': 'error',
            'message': 'Input data is required'
        })
        return
        
    # Write data to the session
    success = self.session_manager.write_to_session(session_id, data)
    if not success:
        await websocket.send_json({
            'type': 'error',
            'message': f'Failed to write to session {session_id}'
        })
        return
        
    # If this looks like a command (ends with newline), emit a command event
    if data.endswith('\n'):
        command = data.strip()
        if command:
            # Publish to Hermes if available
            if hasattr(self, 'hermes_integration') and self.hermes_integration.is_registered:
                payload = {
                    'session_id': session_id,
                    'command': command,
                    'timestamp': time.time()
                }
                asyncio.create_task(
                    self.hermes_integration.publish_event('terminal.command.executed', payload)
                )
```

## Contributing Guidelines

### Code Style

Terma follows these code style guidelines:

- PEP 8 for Python code
- Google-style docstrings
- Type hints for function signatures
- 4 spaces for indentation
- Line length limit of 100 characters

### Pull Request Process

1. Fork the repository
2. Create a new branch for your feature
3. Make your changes
4. Write tests for your changes
5. Run existing tests to ensure compatibility
6. Update documentation
7. Submit a pull request

### Commit Message Format

```
feat: Add command history feature

- Implement command history storage in TerminalSession
- Add API endpoint to retrieve command history
- Add WebSocket message type for history requests

This allows users to access their command history, enhancing the
terminal experience by providing access to previously run commands.
```

### Documentation Standards

All code should be documented according to these standards:

- Module-level docstrings explaining the purpose of the module
- Class-level docstrings explaining the class's purpose and usage
- Method/function docstrings with parameter and return type documentation
- Complex code sections should have inline comments

Example:

```python
"""Terminal session management and PTY interface"""

import os
import signal
import fcntl
import termios
import struct

class TerminalSession:
    """Manages a single terminal session with PTY interface
    
    A TerminalSession represents a single terminal session with a PTY
    interface. It handles starting, stopping, reading from, and writing
    to the terminal process.
    """
    
    def __init__(self, session_id=None, shell_command=None):
        """Initialize a new terminal session
        
        Args:
            session_id: Optional identifier for the session
            shell_command: Shell command to run (defaults to user's default shell)
        """
        # Implementation here
```

### Security Considerations

When contributing code, keep these security considerations in mind:

1. **Input Validation**: Validate all user input before processing
2. **Output Sanitization**: Sanitize output to prevent XSS attacks
3. **Access Control**: Implement proper access controls
4. **Error Handling**: Handle errors gracefully without exposing sensitive information
5. **Resource Protection**: Prevent resource exhaustion attacks