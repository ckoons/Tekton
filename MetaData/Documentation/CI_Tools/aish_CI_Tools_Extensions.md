# aish Extensions for CI Tools Integration

## Overview

This document details the specific extensions to aish (CI Shell) required to support CI Tools as first-class citizens in the Tekton ecosystem. These extensions maintain backward compatibility while adding powerful new capabilities for integrating tools like Claude Code, Cursor, and Continue.

## Core Extensions

### 1. CI Registry Updates

#### New CI Type Definition

In `shared/aish/src/registry/ci_registry.py`:

```python
# Extend CI_TYPES enum
CI_TYPES = ['greek', 'terminal', 'project', 'tool']

# Add CI tools configuration
CI_TOOLS_CONFIG = {
    'claude-code': {
        'display_name': 'Claude Code',
        'executable': 'claude-code',
        'launch_args': ['--no-sandbox'],
        'health_check': 'version',
        'capabilities': {
            'code_analysis': True,
            'code_generation': True,
            'refactoring': True,
            'multi_file': True,
            'project_context': True
        }
    },
    'cursor': {
        'display_name': 'Cursor',
        'executable': 'cursor',
        'launch_args': ['--cli-mode'],
        'health_check': 'status',
        'capabilities': {
            'code_editing': True,
            'ai_completion': True,
            'chat_interface': True,
            'terminal_integration': True
        }
    },
    'continue': {
        'display_name': 'Continue',
        'executable': 'continue',
        'launch_args': ['--headless'],
        'health_check': 'ping',
        'capabilities': {
            'code_assistance': True,
            'context_aware': True,
            'multi_model': True
        }
    }
}
```

### 2. Unified Sender Extensions

#### Tool-Specific Message Routing

In `shared/aish/src/core/unified_sender.py`:

```python
def send_to_tool(tool_name: str, message: str, port: int) -> Optional[str]:
    """Send message to a CI tool via socket bridge."""
    try:
        # Check if tool is running
        if not is_tool_running(tool_name):
            launch_tool(tool_name)
        
        # Format message for tool protocol
        tool_message = {
            'type': 'command',
            'content': message,
            'context': get_current_context(),
            'session_id': get_or_create_session(tool_name)
        }
        
        # Send via socket
        response = send_socket_message(port, tool_message)
        
        # Store in registry for Apollo/Rhetor
        store_tool_exchange(tool_name, message, response)
        
        return response
        
    except Exception as e:
        return f"Error communicating with {tool_name}: {str(e)}"
```

### 3. New aish Commands

#### CI Terminal and Tool Commands

```bash
# Launch terminal programs with PTY
aish ci-terminal -n <name> [-d <delimiter>] -- <command>
aish ci-terminal --name claude-ci --delimiter "\n" -- claude

# Launch non-terminal programs with stdin control
aish ci-tool -n <name> [-d <delimiter>] -- <command>
aish ci-tool --name processor --delimiter "\n\n" -- python script.py

# Send messages with execution
aish <ci-name> "message" -x [delimiter]
aish <ci-name> "message" --execute [delimiter]
```

**Options:**
- `-n`, `--name`: CI name for socket communication
- `-d`, `--delimiter`: Default delimiter for auto-execution
- `-x`, `--execute`: Append delimiter when sending message

#### Tool Management Commands

```bash
# List all CI tools
aish tools list

# Show tool status
aish tools status [tool-name]

# Launch a tool manually
aish tools launch <tool-name> [--session <name>]

# Terminate a tool
aish tools terminate <tool-name>

# Show tool capabilities
aish tools capabilities <tool-name>

# Attach tool to current terminal
aish tools attach <tool-name>
```

#### Session Management

```bash
# List tool sessions
aish sessions list [--tool <name>]

# Create named session
aish session create <name> --tool <tool-name>

# Resume session
aish session resume <name>

# Save session state
aish session save <name>

# Delete session
aish session delete <name>
```

### 4. Message Protocol Extensions

#### Execute Flag Support

The message protocol is extended to support automatic command execution:

```python
# Standard message
message = {
    'from': 'sender_name',
    'content': 'message content',
    'type': 'message'
}

# Message with execution
message = {
    'from': 'sender_name',
    'content': 'message content',
    'type': 'message',
    'execute': True,           # Add delimiter
    'delimiter': '\n'          # Optional override
}
```

#### Wrapper Behavior

1. **CI Terminal (PTY wrapper)**:
   - Stores default delimiter from `-d` flag
   - Checks incoming messages for `execute` flag
   - Appends delimiter: `os.write(master_fd, (content + delimiter).encode())`

2. **CI Tool (Simple wrapper)**:
   - Stores default delimiter from `-d` flag  
   - Checks incoming messages for `execute` flag
   - Appends delimiter: `process.stdin.write((content + delimiter).encode())`

3. **Delimiter Priority**:
   - Message `delimiter` field (highest priority)
   - CI's configured delimiter (from `-d` flag)
   - Default: `\n` (if `-x` used without delimiter)

### 5. Enhanced List Command

Update `shared/aish/src/commands/list.py`:

```python
def list_cis(ci_type=None, format='text'):
    """List CIs with enhanced tool support."""
    
    if ci_type == 'tool' or ci_type is None:
        # Include CI tools in listing
        tools = get_ci_tools()
        for tool_name, tool_info in tools.items():
            status = get_tool_status(tool_name)
            port = tool_info['port']
            
            if format == 'text':
                print(f"  {tool_name:<15} {tool_info['description']:<40} "
                      f"port:{port} status:{status}")
            else:  # json
                # Include full tool metadata
                tool_data = {
                    'name': tool_name,
                    'type': 'tool',
                    'status': status,
                    'port': port,
                    'capabilities': tool_info.get('capabilities', {}),
                    'sessions': get_tool_sessions(tool_name)
                }
```

### 5. Tool Launch Integration

#### Automatic Tool Discovery

In `shared/aish/src/core/tool_launcher.py`:

```python
class ToolLauncher:
    """Manages CI tool lifecycle."""
    
    def __init__(self):
        self.running_tools = {}
        self.socket_bridges = {}
        
    def launch_tool(self, tool_name: str, session_id: str = None) -> bool:
        """Launch a CI tool with socket bridge."""
        
        config = CI_TOOLS_CONFIG.get(tool_name)
        if not config:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        # Find tool executable
        tool_path = find_tool_executable(config['executable'])
        if not tool_path:
            raise FileNotFoundError(f"Tool not found: {config['executable']}")
        
        # Create socket bridge
        bridge = SocketBridge(tool_name, config['port'])
        
        # Launch tool process
        env = prepare_tool_environment(tool_name, session_id)
        args = [tool_path] + config.get('launch_args', [])
        
        process = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env
        )
        
        # Connect bridge to process
        bridge.connect_process(process)
        
        # Store references
        self.running_tools[tool_name] = process
        self.socket_bridges[tool_name] = bridge
        
        # Register in CI registry
        register_tool_launch(tool_name, process.pid, config['port'])
        
        return True
```

### 6. Context Integration

#### Tool Context Injection

Tools participate in Apollo-Rhetor coordination:

```python
def inject_tool_context(tool_name: str, context: dict):
    """Inject context into tool session."""
    
    # Get staged context from Apollo
    staged = registry.get_ci_staged_context_prompt(tool_name)
    
    if staged and should_inject_context(tool_name):
        # Move to next context
        registry.set_ci_next_from_staged(tool_name)
        
        # Send context to tool
        context_message = {
            'type': 'context_injection',
            'prompts': staged,
            'metadata': {
                'source': 'apollo-rhetor',
                'timestamp': time.time()
            }
        }
        
        send_to_tool(tool_name, json.dumps(context_message))
```

### 7. Forward Command Enhancement

Update `shared/aish/src/commands/forward.py`:

```python
def handle_forward(args):
    """Extended forward command with tool support."""
    
    if len(args) >= 2:
        source = args[0]
        target = args[1]
        json_mode = len(args) > 2 and args[2] == 'json'
        
        # Check if source is a CI tool
        if is_ci_tool(source):
            # Set up tool output forwarding
            setup_tool_forward(source, target, json_mode)
            print(f"Forwarding {source} output to {target} terminal")
            
            # Tool forwards include metadata
            if json_mode:
                print("  (with tool metadata)")
```

### 8. Capability Discovery

#### Dynamic Capability Queries

```python
def get_tool_capabilities(tool_name: str) -> dict:
    """Query tool for current capabilities."""
    
    # Static capabilities from config
    static_caps = CI_TOOLS_CONFIG[tool_name].get('capabilities', {})
    
    # Dynamic capability query
    response = send_to_tool(tool_name, json.dumps({
        'type': 'capability_query',
        'version': '1.0'
    }))
    
    if response:
        dynamic_caps = json.loads(response).get('capabilities', {})
        # Merge static and dynamic
        return {**static_caps, **dynamic_caps}
    
    return static_caps
```

## Usage Examples

### Basic Tool Interaction

```bash
# Send prompt to Claude Code
aish claude-code "analyze the authentication module for security issues"

# Use Cursor for refactoring
aish cursor "refactor the UserService class to use dependency injection"

# Get help from Continue
aish continue "explain this error: TypeError: cannot read property 'id' of undefined"
```

### Advanced Workflows

```bash
# Create a code review session
aish session create auth-review --tool claude-code
aish claude-code "review the changes in PR #123"

# Forward tool output to terminal for monitoring
aish forward claude-code alice json

# Chain tools together
echo "Design a caching system" | aish prometheus | aish claude-code

# Use tool with specific context
aish purpose "code-review"
aish claude-code "review this implementation against our standards"
```

### Session Management

```bash
# List active tool sessions
aish sessions list --tool claude-code

# Resume previous session
aish session resume auth-review

# Save session for later
aish session save auth-review

# Attach tool to current terminal
aish tools attach cursor
```

## Implementation Priority

1. **Phase 1**: Core registry extensions and basic send/receive
2. **Phase 2**: Tool launcher and process management
3. **Phase 3**: Session management and persistence
4. **Phase 4**: Advanced features (forwarding, context injection)

## Testing Strategy

1. **Unit Tests**: Each new function and class
2. **Integration Tests**: Tool launch, communication, shutdown
3. **End-to-End Tests**: Complete workflows with real tools
4. **Performance Tests**: Socket communication latency
5. **Stress Tests**: Multiple tools, high message volume

## Backward Compatibility

All extensions maintain full backward compatibility:
- Existing aish commands work unchanged
- New commands use consistent syntax
- Tools appear as regular CIs to existing infrastructure
- No changes required to existing Greek Chorus or Terminal CIs

## Conclusion

These aish extensions seamlessly integrate CI tools into the Tekton ecosystem while maintaining the elegant simplicity of "CIs are sockets". The implementation provides powerful new capabilities while preserving the existing user experience and architectural principles.