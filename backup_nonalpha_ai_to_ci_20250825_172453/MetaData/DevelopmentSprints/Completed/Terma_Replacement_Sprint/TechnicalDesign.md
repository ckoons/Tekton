# Terma Technical Design

## Architecture Overview

Terma operates as a lightweight orchestration layer that bridges Tekton's UI with native terminal applications, providing AI-enhanced shell capabilities through aish.

## System Components

### 1. Terma Service (Python/FastAPI)

Located at: `Terma/terma_service.py`

**Core Responsibilities:**
- Terminal launcher with platform-specific commands
- PID registry and lifecycle management
- Configuration management
- API endpoints for UI and CI consumers

**Key APIs:**
```python
POST   /api/terminals/launch     # Launch new terminal with config
GET    /api/terminals            # List active terminals
GET    /api/terminals/{pid}      # Get terminal details
POST   /api/terminals/{pid}/show # Bring terminal to front
DELETE /api/terminals/{pid}      # Terminate terminal
POST   /api/terminals/templates  # Save configuration template
```

### 2. Terminal Launch Mechanism

#### macOS Implementation
```python
def launch_terminal_macos(config):
    """Launch native macOS terminal with aish."""
    terminal_app = config.get('app', 'Terminal.app')
    working_dir = config.get('working_dir', os.getcwd())
    env_vars = config.get('env', {})
    
    # Build environment string
    env_str = " ".join([f"export {k}={v};" for k, v in env_vars.items()])
    
    # Launch commands by terminal type
    if terminal_app == "Terminal.app":
        cmd = [
            "osascript", "-e",
            f'tell app "Terminal" to do script "cd {working_dir}; {env_str} aish"'
        ]
    elif terminal_app == "iTerm.app":
        cmd = [
            "osascript", "-e",
            f'tell app "iTerm" to create window with default profile command "cd {working_dir}; {env_str} aish"'
        ]
    elif terminal_app == "Warp.app":
        cmd = ["open", "-a", "Warp", "-n", "--args", "--new-window", "--execute", f"cd {working_dir}; {env_str} aish"]
    
    process = subprocess.Popen(cmd)
    return process.pid
```

#### Linux Implementation
```python
def launch_terminal_linux(config):
    """Launch Linux terminal with aish."""
    terminal_app = config.get('app', 'gnome-terminal')
    working_dir = config.get('working_dir', os.getcwd())
    
    if terminal_app == "gnome-terminal":
        cmd = ["gnome-terminal", "--", "bash", "-c", f"cd {working_dir}; aish; exec bash"]
    elif terminal_app == "konsole":
        cmd = ["konsole", "-e", "bash", "-c", f"cd {working_dir}; aish"]
    elif terminal_app == "xterm":
        cmd = ["xterm", "-e", f"cd {working_dir}; aish"]
    
    process = subprocess.Popen(cmd)
    return process.pid
```

### 3. PID Management

**Registry Structure:**
```json
{
  "terminals": {
    "12345": {
      "pid": 12345,
      "config": {
        "name": "Development Terminal",
        "app": "Terminal.app",
        "purpose": "React development",
        "launched_at": "2025-01-01T10:00:00Z"
      },
      "status": "running"
    }
  }
}
```

**Lifecycle Operations:**
```python
class TerminalManager:
    def __init__(self):
        self.registry = {}
    
    def track_terminal(self, pid, config):
        """Register a new terminal."""
        self.registry[pid] = {
            "pid": pid,
            "config": config,
            "launched_at": datetime.now().isoformat(),
            "status": "running"
        }
    
    def is_running(self, pid):
        """Check if terminal process still exists."""
        try:
            os.kill(pid, 0)
            return True
        except ProcessLookupError:
            return False
    
    def show_terminal(self, pid):
        """Bring terminal to foreground (macOS)."""
        # Use AppleScript to activate window with PID
        script = f'''
        tell application "System Events"
            set frontProcess to first process whose unix id is {pid}
            set frontmost of frontProcess to true
        end tell
        '''
        subprocess.run(["osascript", "-e", script])
```

### 4. aish Shell Wrapper Enhancement

Located at: `scripts/aish` (refactored)

**Key Requirements:**
1. **Transparent Passthrough**: All commands execute normally
2. **Pattern Interception**: Detect CI command patterns
3. **Context Preservation**: Maintain working directory, environment
4. **Tool Compatibility**: Work with git, npm, python, etc.

**Implementation Approach:**
```bash
#!/usr/bin/env python3
"""aish - AI-enhanced shell wrapper"""

import os
import sys
import subprocess
import readline

class AishShell:
    def __init__(self):
        self.context = {
            "pwd": os.getcwd(),
            "env": os.environ.copy(),
            "history": []
        }
        self.base_shell = os.environ.get("SHELL", "/bin/bash")
    
    def run(self):
        """Main REPL loop."""
        while True:
            try:
                # Show prompt with context
                prompt = f"[aish:{os.path.basename(self.context['pwd'])}]$ "
                command = input(prompt)
                
                # Check for CI patterns
                if self.is_ai_command(command):
                    result = self.process_ai_command(command)
                    print(result)
                else:
                    # Passthrough to base shell
                    self.execute_command(command)
                
                self.context["history"].append(command)
                
            except (EOFError, KeyboardInterrupt):
                print("\nExiting aish...")
                break
    
    def is_ai_command(self, command):
        """Detect natural language patterns."""
        ai_triggers = ["show me", "what is", "how do", "find all", "help with"]
        return any(trigger in command.lower() for trigger in ai_triggers)
    
    def execute_command(self, command):
        """Execute command in base shell."""
        process = subprocess.Popen(
            [self.base_shell, "-c", command],
            cwd=self.context["pwd"],
            env=self.context["env"]
        )
        process.wait()
        
        # Update context if needed (cd command)
        if command.strip().startswith("cd "):
            new_dir = command.strip()[3:].strip()
            self.context["pwd"] = os.path.abspath(new_dir)
            os.chdir(self.context["pwd"])
```

### 5. Configuration Templates

**Default Templates:**
```python
DEFAULT_TEMPLATES = {
    "default": {
        "name": "Default Terminal",
        "app": "Terminal.app",
        "shell": "aish",
        "env": {
            "TEKTON_ENABLED": "true"
        }
    },
    "development": {
        "name": "Development Terminal",
        "app": "Warp.app",
        "working_dir": "$TEKTON_ROOT",
        "shell": "aish",
        "env": {
            "TEKTON_MODE": "development",
            "NODE_ENV": "development"
        }
    },
    "claude_code": {
        "name": "Claude Code Session",
        "app": "Claude Code",
        "shell": "aish",
        "context": "Full project context with CI assistance"
    },
    "data_science": {
        "name": "Data Science Terminal",
        "app": "iTerm.app",
        "shell": "aish",
        "env": {
            "JUPYTER_ENABLE": "true",
            "CONDA_PREFIX": "/opt/conda"
        }
    }
}
```

### 6. UI Integration Points

**Terma UI Component** (Following Numa/Noesis pattern):
```javascript
// Terminal management functions
window.Terma = {
    apiUrl: window.TERMA_URL || 'http://localhost:8004',
    
    async launchTerminal(config) {
        const response = await fetch(`${this.apiUrl}/api/terminals/launch`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(config)
        });
        return response.json();
    },
    
    async listTerminals() {
        const response = await fetch(`${this.apiUrl}/api/terminals`);
        return response.json();
    },
    
    async showTerminal(pid) {
        await fetch(`${this.apiUrl}/api/terminals/${pid}/show`, {
            method: 'POST'
        });
    },
    
    async terminateTerminal(pid) {
        await fetch(`${this.apiUrl}/api/terminals/${pid}`, {
            method: 'DELETE'
        });
    }
};
```

### 7. CI Terminal Request API

Enable other Tekton CIs to request terminals:
```python
@app.post("/api/terminals/ai-request")
async def ai_terminal_request(request: AITerminalRequest):
    """Handle terminal requests from CI components."""
    config = {
        "name": f"AI Terminal - {request.purpose}",
        "app": request.terminal_app or "Terminal.app",
        "shell": "aish",
        "working_dir": request.working_dir,
        "env": {
            "TEKTON_AI_CONTEXT": request.context,
            "TEKTON_AI_PURPOSE": request.purpose,
            "TEKTON_AI_REQUESTER": request.requester_id
        }
    }
    
    pid = launch_terminal(config)
    
    # Inject initial context into aish
    if request.initial_commands:
        inject_commands(pid, request.initial_commands)
    
    return {"pid": pid, "status": "launched"}
```

## Security Considerations

1. **PID Validation**: Always verify PID belongs to our launched terminals
2. **Command Injection**: Sanitize all shell commands and paths
3. **Permission Scope**: Terminal runs with user permissions only
4. **AI Boundaries**: aish should confirm destructive operations

## Performance Considerations

1. **Lightweight Service**: Minimal memory footprint
2. **Async Operations**: Non-blocking terminal launches
3. **PID Polling**: Efficient process existence checks
4. **Registry Cleanup**: Periodic removal of dead terminals

## Error Handling

1. **Terminal Launch Failures**: Graceful fallback to alternative terminals
2. **PID Tracking**: Handle race conditions and process death
3. **Platform Differences**: Detect and adapt to OS capabilities
4. **aish Failures**: Fallback to base shell if aish unavailable