# Terma User Guide

This guide provides comprehensive information on using Terma, the advanced terminal system for the Tekton ecosystem.

## Introduction

Terma is a powerful terminal system that provides interactive terminal functionality with features such as:

- **Rich Terminal Experience**: Full terminal emulation with support for interactive applications
- **LLM Assistance**: AI-powered help with terminal commands and output analysis
- **Session Management**: Create, manage, and monitor terminal sessions with persistence
- **WebSocket Communication**: Real-time terminal interaction with reliable connections
- **Seamless UI Integration**: Integration with Hephaestus UI and other interfaces

This guide will help you get started with Terma and show you how to use its key features.

## Getting Started

### Installation

There are multiple ways to access Terma:

1. **As part of Tekton**: Terma is included in the Tekton ecosystem
   ```bash
   # Start with Tekton launcher
   ./scripts/tekton-launch --components terma
   ```

2. **Standalone Installation**:
   ```bash
   # Clone the repository
   git clone https://github.com/yourusername/Tekton.git
   cd Tekton/Terma
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Start the server
   python -m terma.cli.main
   ```

3. **Via Hephaestus UI**: Access Terma through the Hephaestus UI component

### Accessing Terma

Once Terma is running, you can access it through:

- **Web Interface**: `http://localhost:8767/terminal/launch`
- **REST API**: `http://localhost:8767/api`
- **WebSocket API**: `ws://localhost:8767/ws`
- **Hephaestus UI**: Through the Terma component in Hephaestus

## Terminal Sessions

### Creating Sessions

#### Via Web Interface

1. Navigate to `http://localhost:8767/terminal/launch`
2. The terminal will automatically create a new session
3. To create a new session, click the "New Session" button in the toolbar

#### Via Command Line

```bash
# Create a session with default shell
curl -X POST http://localhost:8767/api/sessions \
  -H "Content-Type: application/json" \
  -d '{}'

# Create a session with specific shell and working directory
curl -X POST http://localhost:8767/api/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "shell_command": "/bin/zsh",
    "cwd": "/home/user/projects",
    "cols": 120,
    "rows": 40
  }'
```

### Managing Sessions

#### Listing Sessions

To see all active sessions:

```bash
curl http://localhost:8767/api/sessions
```

Response:
```json
{
  "sessions": [
    {
      "session_id": "sess-abc123",
      "created_at": 1719875632.123456,
      "last_activity": 1719875732.123456,
      "shell_command": "/bin/bash",
      "cwd": "/home/user",
      "active": true,
      "idle_time": 100.0
    },
    {
      "session_id": "sess-def456",
      "created_at": 1719875732.123456,
      "last_activity": 1719875832.123456,
      "shell_command": "/bin/zsh",
      "cwd": "/home/user/projects",
      "active": true,
      "idle_time": 100.0
    }
  ],
  "count": 2
}
```

#### Getting Session Details

To get details about a specific session:

```bash
curl http://localhost:8767/api/sessions/sess-abc123
```

Response:
```json
{
  "session_id": "sess-abc123",
  "created_at": 1719875632.123456,
  "last_activity": 1719875732.123456,
  "shell_command": "/bin/bash",
  "cwd": "/home/user",
  "active": true,
  "idle_time": 100.0
}
```

#### Closing Sessions

To close a session:

```bash
curl -X DELETE http://localhost:8767/api/sessions/sess-abc123
```

Response:
```json
{
  "status": "closed",
  "session_id": "sess-abc123"
}
```

### Session Timeouts

Terma automatically closes idle sessions after a period of inactivity (default: 1 hour). You can configure this with the `TERMA_SESSION_TIMEOUT` environment variable:

```bash
# Set timeout to 30 minutes (1800 seconds)
export TERMA_SESSION_TIMEOUT=1800

# Start Terma
python -m terma.cli.main
```

## Terminal Interaction

### Basic Usage

When using the web interface, you can:

1. **Type Commands**: Type commands directly into the terminal
2. **Copy/Paste**: Use Ctrl+C to copy and Ctrl+V to paste (or right-click menu)
3. **Resize Terminal**: Drag the window edges to resize the terminal
4. **Scroll Output**: Use the scrollbar or mouse wheel to scroll through output
5. **Clear Screen**: Use the `clear` command or Ctrl+L to clear the screen

### Keyboard Shortcuts

The terminal supports standard terminal keyboard shortcuts:

- **Ctrl+C**: Send SIGINT (interrupt current command)
- **Ctrl+D**: Send EOF (logout from shell)
- **Ctrl+L**: Clear screen
- **Tab**: Command/file completion
- **Up/Down Arrows**: Cycle through command history
- **Ctrl+R**: Reverse search command history
- **Ctrl+A**: Move cursor to beginning of line
- **Ctrl+E**: Move cursor to end of line
- **Ctrl+K**: Kill (delete) text from cursor to end of line
- **Ctrl+U**: Kill text from cursor to beginning of line
- **Ctrl+W**: Kill the word behind the cursor

### Command Examples

Terma supports all standard terminal commands:

```bash
# File operations
ls -la
cd /path/to/directory
mkdir new_directory
touch new_file.txt
cat file.txt
cp source.txt destination.txt
mv old_name.txt new_name.txt
rm file.txt

# System information
uname -a
df -h
top
ps aux
free -m

# Text processing
grep "pattern" file.txt
awk '{print $1}' file.txt
sed 's/old/new/g' file.txt
cut -d, -f1 file.csv
sort file.txt

# Network operations
ping google.com
curl https://example.com
wget https://example.com/file.zip
ssh user@host
```

### Interactive Applications

Terma supports interactive terminal applications:

- Text editors (vim, nano, emacs)
- Interactive shells (bash, zsh, fish)
- Terminal-based applications (htop, tmux, screen)
- CLI tools with interactive prompts

Example with vim:
```bash
# Open vim
vim file.txt

# Use vim commands
# Press i to enter insert mode
# Type text
# Press Esc to exit insert mode
# Type :wq to save and quit
```

## LLM Assistance

Terma provides AI-powered assistance for terminal commands and output analysis.

### Requesting Assistance

#### Via Web Interface

1. Click the "AI Assist" button in the toolbar
2. Enter your question in the dialog
3. Click "Ask" to submit your question
4. The assistant's response will appear in a panel alongside the terminal

#### Via Command Line

```bash
curl -X POST http://localhost:8767/api/sessions/sess-abc123/llm-assist \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I find all files larger than 10MB?",
    "model": "claude-3-sonnet-20240229"
  }'
```

#### Via WebSocket

```javascript
// Send LLM assistance request
socket.send(JSON.stringify({
    type: 'llm_assist',
    data: 'How do I find all files larger than 10MB?',
    options: {
        model: 'claude-3-sonnet-20240229'
    }
}));
```

### Example Assistance Scenarios

1. **Command Help**: Get help with command syntax and options
   - "How do I use the find command to search for specific file types?"
   - "What are the options for the grep command?"

2. **Output Explanation**: Understand terminal output
   - "What does this error message mean: 'permission denied'?"
   - "Can you explain the output of 'ps aux'?"

3. **Task Guidance**: Get help with specific tasks
   - "How do I extract all zip files in a directory at once?"
   - "What's the best way to monitor CPU usage in real-time?"

4. **Troubleshooting**: Get help with common issues
   - "Why does my bash script exit with 'command not found'?"
   - "How do I fix 'no such file or directory' errors?"

5. **Learning**: Learn more about terminal concepts
   - "What are environment variables and how do they work?"
   - "Can you explain the difference between bash and zsh?"

### Markdown Rendering

LLM responses are rendered as markdown with:

- **Syntax Highlighting**: Code blocks are highlighted for better readability
- **Rich Formatting**: Support for headings, lists, tables, and more
- **Code Examples**: Formatted code examples with copy functionality

## Web Interface Features

### Terminal Customization

The web interface provides several customization options:

#### Themes

Change the terminal theme:
- **Dark Theme**: Dark background with light text (default)
- **Light Theme**: Light background with dark text

To change the theme:
1. Click the theme selector in the toolbar
2. Select your preferred theme

Or use query parameters:
```
http://localhost:8767/terminal/launch?theme=light
```

#### Font Size

Change the terminal font size:
- Default: 14px
- Range: 8px to 32px

To change the font size:
1. Use the font size selector in the toolbar
2. Select your preferred size

Or use query parameters:
```
http://localhost:8767/terminal/launch?font_size=16
```

#### Shell Selection

Change the shell command:
- Default: System default shell
- Options: bash, zsh, fish, etc.

To change the shell:
1. Create a new session with the desired shell
2. Or use query parameters:
```
http://localhost:8767/terminal/launch?shell_command=/bin/zsh
```

### UI Controls

The terminal UI provides several controls:

1. **New Session**: Create a new terminal session
2. **AI Assist**: Request LLM assistance
3. **Clear Terminal**: Clear the terminal screen
4. **Theme Selector**: Change the terminal theme
5. **Font Size Selector**: Change the terminal font size

## Web Component Usage

Terma provides a web component that can be integrated into any web application or the Hephaestus UI.

### Basic Usage

```html
<!-- Include the component -->
<script src="http://localhost:8767/terminal/static/js/terma-terminal.js"></script>
<link rel="stylesheet" href="http://localhost:8767/terminal/static/css/terma-terminal.css">

<!-- Use the component -->
<terma-terminal></terma-terminal>
```

### Advanced Configuration

```html
<!-- Advanced configuration -->
<terma-terminal
  id="myTerminal"
  theme="dark"
  font-size="14"
  font-family="Fira Code, monospace"
  shell-command="/bin/bash"
  cwd="/home/user/projects"
  cols="120"
  rows="40"
  auto-connect="true"
  show-assist-button="true"
  llm-model="claude-3-sonnet-20240229">
</terma-terminal>
```

### JavaScript Interaction

```javascript
// Get the terminal element
const terminal = document.getElementById('myTerminal');

// Lifecycle events
terminal.addEventListener('terminalReady', event => {
    console.log('Terminal ready:', event.detail);
});

terminal.addEventListener('terminalConnected', event => {
    console.log('Terminal connected:', event.detail);
});

terminal.addEventListener('terminalDisconnected', event => {
    console.log('Terminal disconnected:', event.detail);
});

terminal.addEventListener('terminalError', event => {
    console.error('Terminal error:', event.detail);
});

terminal.addEventListener('llmResponse', event => {
    console.log('LLM response:', event.detail);
});

// Control methods
terminal.createSession(); // Create a new session
terminal.clear();         // Clear the terminal
terminal.focus();         // Focus the terminal
terminal.setTheme('light'); // Change theme
terminal.setFontSize(16);   // Change font size

// Send input programmatically
terminal.write('echo "Hello from JavaScript"\n');

// Request LLM assistance
terminal.getLlmAssistance('How do I use the grep command?');
```

## WebSocket API Usage

For advanced integrations, you can use the WebSocket API directly:

```javascript
// Connect to a session
const socket = new WebSocket(`ws://localhost:8767/ws/sess-abc123`);

// Handle connection open
socket.onopen = () => {
    console.log('Connected to terminal session');
};

// Handle incoming messages
socket.onmessage = event => {
    const message = JSON.parse(event.data);
    
    switch (message.type) {
        case 'output':
            console.log('Terminal output:', message.data);
            break;
        
        case 'error':
            console.error('Terminal error:', message.data);
            break;
        
        case 'llm_response':
            console.log('LLM response:', message.data);
            break;
    }
};

// Send terminal input
function sendInput(text) {
    socket.send(JSON.stringify({
        type: 'input',
        data: text
    }));
}

// Resize terminal
function resizeTerminal(cols, rows) {
    socket.send(JSON.stringify({
        type: 'resize',
        cols: cols,
        rows: rows
    }));
}

// Request LLM assistance
function getLlmAssistance(query) {
    socket.send(JSON.stringify({
        type: 'llm_assist',
        data: query
    }));
}

// Close connection
function closeConnection() {
    socket.close();
}
```

## Advanced Features

### Custom Shell Commands

You can start the terminal with custom shell commands:

```bash
# Create a session with a custom shell command
curl -X POST http://localhost:8767/api/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "shell_command": "python -i",
    "cwd": "/home/user/projects"
  }'
```

This allows you to:
- Start with a Python interpreter
- Use a specific shell with custom options
- Run a specific application directly

For example, to start Node.js REPL:
```json
{
  "shell_command": "node",
  "cwd": "/home/user/projects/node-app"
}
```

### Custom Environment Variables

You can set environment variables for the terminal session:

```bash
# Create a session with custom environment variables
curl -X POST http://localhost:8767/api/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "shell_command": "/bin/bash",
    "env": {
      "NODE_ENV": "development",
      "DEBUG": "app:*",
      "PATH": "/usr/local/bin:/usr/bin:/bin"
    }
  }'
```

This is useful for:
- Setting up development environments
- Configuring application behavior
- Setting language or locale preferences

### Multiple Sessions

You can work with multiple terminal sessions:

```bash
# Create two sessions
SESSION1=$(curl -s -X POST http://localhost:8767/api/sessions | jq -r '.session_id')
SESSION2=$(curl -s -X POST http://localhost:8767/api/sessions | jq -r '.session_id')

# Send different commands to each session
curl -X POST http://localhost:8767/api/sessions/$SESSION1/input \
  -H "Content-Type: application/json" \
  -d '{"data": "echo \"Session 1\"\n"}'

curl -X POST http://localhost:8767/api/sessions/$SESSION2/input \
  -H "Content-Type: application/json" \
  -d '{"data": "echo \"Session 2\"\n"}'
```

This allows you to:
- Run multiple tasks in parallel
- Keep separate environments for different projects
- Use different shells for different purposes

## Troubleshooting

### Common Issues

#### Terminal Not Working

**Symptoms:**
- Terminal doesn't load
- Commands don't execute
- No response from the terminal

**Solutions:**
1. Check that the Terma service is running
   ```bash
   curl http://localhost:8767/api/health
   ```
2. Verify your connection to the server
3. Try creating a new session
4. Check browser console for errors (in web interface)
5. Restart the Terma service

#### Session Disconnection

**Symptoms:**
- Terminal session disconnects unexpectedly
- "Session closed" or "Connection lost" messages

**Solutions:**
1. Check network connectivity
2. Check server logs for timeout or error messages
3. Create a new session
4. Ensure the server is still running
5. Check if the session timed out due to inactivity

#### LLM Assistance Issues

**Symptoms:**
- LLM assistance doesn't work
- "Failed to get LLM assistance" error
- No response from LLM

**Solutions:**
1. Check that the LLM service is available
2. Verify your LLM provider configuration
3. Try a different LLM model
4. Check server logs for LLM-related errors
5. Ensure your query is clear and well-formed

### Error Messages

| Error Message | Possible Cause | Solution |
|---------------|----------------|----------|
| "Session not found" | Session ID is invalid or session has expired | Create a new session |
| "Failed to create session" | Server issue or resource constraints | Check server logs, restart service |
| "Session closed" | Session was closed manually or timed out | Create a new session |
| "Connection lost" | Network issue or server restarted | Check connectivity, reconnect |
| "Failed to send input" | Session is closed or server issue | Check session status, create new session |
| "Failed to get LLM assistance" | LLM service unavailable or error | Check LLM service, try again later |

### Getting Help

If you encounter issues not covered in this guide:

1. **Check Logs**: Look at the Terma server logs for more information
   ```bash
   # View logs (if running with systemd)
   journalctl -u terma
   
   # View logs (if running directly)
   cat logs/terma.log
   ```

2. **Enable Debug Mode**: Start Terma with debug logging
   ```bash
   TERMA_LOG_LEVEL=debug python -m terma.cli.main
   ```

3. **Contact Support**: Reach out to the Tekton team for help

## Configuration

### Environment Variables

Terma can be configured through environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `TERMA_PORT` | HTTP server port | 8767 |
| `TERMA_HOST` | HTTP server host | 0.0.0.0 |
| `TERMA_LOG_LEVEL` | Logging level (debug, info, warning, error) | info |
| `TERMA_SESSION_TIMEOUT` | Idle session timeout in seconds | 3600 |
| `TERMA_CLEANUP_INTERVAL` | Cleanup interval in seconds | 300 |
| `TERMA_MAX_SESSIONS` | Maximum number of sessions | 100 |
| `TERMA_DEFAULT_SHELL` | Default shell command | system shell |
| `TERMA_LLM_PROVIDER` | Default LLM provider | rhetor |
| `TERMA_LLM_MODEL` | Default LLM model | depends on provider |
| `TERMA_UI_THEME` | Default UI theme (dark, light) | dark |
| `TERMA_UI_FONT_SIZE` | Default font size | 14 |

Example usage:
```bash
# Configure Terma
export TERMA_PORT=9000
export TERMA_SESSION_TIMEOUT=1800
export TERMA_LLM_PROVIDER=claude
export TERMA_UI_THEME=light

# Start Terma
python -m terma.cli.main
```

### Configuration File

*Note: Configuration file support is planned for future releases.*

## Best Practices

### Security

1. **Access Control**: Restrict access to the Terma service
2. **Avoid Sensitive Commands**: Don't run sensitive commands that could expose credentials
3. **Session Management**: Close sessions when finished to free resources
4. **Use Controlled Environments**: Run commands in controlled directories

### Performance

1. **Limit Concurrent Sessions**: Don't create too many sessions
2. **Clean Up**: Close sessions when done to free resources
3. **Optimize Output**: Avoid commands that produce excessive output
4. **Use Pagination**: For commands with long output, use pagination (`less`, `more`)

### Effective LLM Use

1. **Be Specific**: Ask clear, specific questions
2. **Provide Context**: Include relevant context in your questions
3. **Follow Up**: Ask follow-up questions for clarification
4. **Use for Learning**: Ask for explanations, not just solutions
5. **Verify Suggestions**: Always verify command suggestions before running them

## Conclusion

Terma provides a powerful terminal experience with LLM assistance, making it an essential tool for developers in the Tekton ecosystem. By following this guide, you should be able to effectively use Terma for your terminal needs.

For more detailed information, refer to the [Technical Documentation](./TECHNICAL_DOCUMENTATION.md), [API Reference](./API_REFERENCE.md), and [Integration Guide](./INTEGRATION_GUIDE.md).