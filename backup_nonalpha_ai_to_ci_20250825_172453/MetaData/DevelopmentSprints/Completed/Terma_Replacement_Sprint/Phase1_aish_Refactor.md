# Phase 1: aish Shell Wrapper Refactor

## Objective

Transform aish from its current implementation into a true shell wrapper that can intercept CI commands while transparently passing through normal shell operations.

## Current State Analysis

### What aish Currently Does
- Acts as a command-line interface to query Tekton CIs
- Pipes input to CI specialists via HTTP/socket connections
- Returns CI responses to stdout
- Supports various flags for CI selection and output formatting

### What aish Needs to Become
- A full shell wrapper (like fish or zsh)
- Transparent passthrough for normal commands
- Smart detection of AI-intent commands
- Session state preservation (pwd, env, history)
- Integration point for Terma terminals

## Implementation Design

### 1. Shell Wrapper Architecture

```python
#!/usr/bin/env python3
"""
aish - AI-enhanced Shell
A transparent shell wrapper with CI capabilities
"""

import os
import sys
import subprocess
import readline
import json
import re
from pathlib import Path
from typing import Optional, Dict, List, Tuple

class AishShell:
    """AI-enhanced shell wrapper."""
    
    def __init__(self):
        self.base_shell = os.environ.get("AISH_BASE_SHELL", "/bin/bash")
        self.context = {
            "pwd": os.getcwd(),
            "env": os.environ.copy(),
            "history": [],
            "last_exit_code": 0
        }
        self.ai_patterns = self._load_ai_patterns()
        self.setup_readline()
    
    def _load_ai_patterns(self) -> List[re.Pattern]:
        """Load patterns that trigger CI interpretation."""
        patterns = [
            r"^(show me|tell me|what is|what are|find)",
            r"^(how do i|how to|help me)",
            r"^(explain|analyze|debug|fix)",
            r"(please|could you|can you)",
            r"\?$"  # Questions
        ]
        return [re.compile(p, re.IGNORECASE) for p in patterns]
    
    def setup_readline(self):
        """Configure readline for better UX."""
        # Load history
        history_file = Path.home() / ".aish_history"
        try:
            readline.read_history_file(history_file)
        except FileNotFoundError:
            pass
        
        # Save history on exit
        import atexit
        atexit.register(readline.write_history_file, history_file)
        
        # Tab completion
        readline.parse_and_bind("tab: complete")
```

### 2. Command Detection and Routing

```python
def is_ai_command(self, command: str) -> bool:
    """Detect if command should be routed to AI."""
    # Check explicit CI trigger
    if command.startswith("ai:") or command.startswith("@ai"):
        return True
    
    # Check pattern matching
    for pattern in self.ai_patterns:
        if pattern.search(command):
            return True
    
    # Check for complex natural language
    word_count = len(command.split())
    if word_count > 5 and not command.startswith("/"):
        return True
    
    return False

def process_command(self, command: str) -> int:
    """Process a single command."""
    if not command.strip():
        return 0
    
    # Add to history
    self.context["history"].append(command)
    
    # Check for built-in commands
    if command.strip() == "exit":
        return -1
    elif command.strip().startswith("cd "):
        return self.handle_cd(command)
    
    # Route to CI or shell
    if self.is_ai_command(command):
        return self.handle_ai_command(command)
    else:
        return self.handle_shell_command(command)
```

### 3. Shell Command Execution

```python
def handle_shell_command(self, command: str) -> int:
    """Execute command in base shell."""
    try:
        # Use base shell to handle all shell features
        process = subprocess.Popen(
            [self.base_shell, "-c", command],
            cwd=self.context["pwd"],
            env=self.context["env"],
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        
        # Wait for completion
        exit_code = process.wait()
        self.context["last_exit_code"] = exit_code
        
        # Update pwd if it might have changed
        self.sync_pwd()
        
        return exit_code
        
    except Exception as e:
        print(f"aish: error executing command: {e}", file=sys.stderr)
        return 1

def sync_pwd(self):
    """Sync working directory with base shell."""
    # Get actual pwd in case shell changed it
    result = subprocess.run(
        [self.base_shell, "-c", "pwd"],
        capture_output=True,
        text=True,
        cwd=self.context["pwd"]
    )
    if result.returncode == 0:
        new_pwd = result.stdout.strip()
        if new_pwd and new_pwd != self.context["pwd"]:
            self.context["pwd"] = new_pwd
            os.chdir(new_pwd)
```

### 4. CI Command Handling

```python
def handle_ai_command(self, command: str) -> int:
    """Route command to CI for interpretation."""
    # Strip CI prefix if present
    if command.startswith("ai:"):
        command = command[3:].strip()
    elif command.startswith("@ai"):
        command = command[3:].strip()
    
    # Get CI response
    response = self.query_ai(command)
    
    if response.get("type") == "command":
        # CI suggested a command
        suggested = response.get("command")
        explanation = response.get("explanation", "")
        
        if explanation:
            print(f"\n{explanation}")
        
        print(f"\nSuggested command: {suggested}")
        
        # Ask for confirmation
        confirm = input("Execute? [Y/n] ").strip().lower()
        if confirm in ["", "y", "yes"]:
            return self.handle_shell_command(suggested)
        else:
            print("Command cancelled.")
            return 0
    else:
        # Direct response
        print(response.get("message", "No response from AI"))
        return 0

def query_ai(self, prompt: str) -> Dict:
    """Query Tekton CI for assistance."""
    # This will integrate with existing aish CI connection logic
    # For now, placeholder
    import requests
    
    try:
        # Add context to prompt
        enhanced_prompt = f"""
        Current directory: {self.context['pwd']}
        Last command exit code: {self.context['last_exit_code']}
        
        User request: {prompt}
        """
        
        # Query appropriate CI (Rhetor, local specialist, etc.)
        # This reuses existing aish connection logic
        response = self._send_to_ai(enhanced_prompt)
        return response
        
    except Exception as e:
        return {"type": "error", "message": str(e)}
```

### 5. Main REPL Loop

```python
def run(self):
    """Main read-eval-print loop."""
    # Print welcome
    print("aish - AI-enhanced Shell")
    print("Type 'help' for aish commands, 'exit' to quit")
    print()
    
    while True:
        try:
            # Build prompt
            prompt = self.build_prompt()
            
            # Read command
            command = input(prompt)
            
            # Process command
            exit_code = self.process_command(command)
            
            if exit_code == -1:  # Exit requested
                break
                
        except KeyboardInterrupt:
            print("^C")
            continue
        except EOFError:
            print("exit")
            break
        except Exception as e:
            print(f"aish: {e}", file=sys.stderr)

def build_prompt(self) -> str:
    """Build shell prompt."""
    # Simple prompt for now, can be enhanced
    pwd = self.context["pwd"]
    home = str(Path.home())
    if pwd.startswith(home):
        pwd = "~" + pwd[len(home):]
    
    basename = os.path.basename(pwd) or pwd
    
    # Include exit code if non-zero
    exit_indicator = ""
    if self.context["last_exit_code"] != 0:
        exit_indicator = f"[{self.context['last_exit_code']}] "
    
    return f"{exit_indicator}aish:{basename}$ "
```

### 6. Integration with Existing aish

The refactored aish will preserve existing functionality:

```python
def legacy_mode(args):
    """Run aish in legacy pipe mode for backward compatibility."""
    # This preserves the current aish behavior when called with arguments
    # e.g., echo "question" | aish --ai apollo
    from aish_legacy import main as legacy_main
    return legacy_main(args)

if __name__ == "__main__":
    import argparse
    
    # If called with arguments, use legacy mode
    if len(sys.argv) > 1:
        sys.exit(legacy_mode(sys.argv[1:]))
    
    # Otherwise, start shell mode
    shell = AishShell()
    try:
        shell.run()
    except Exception as e:
        print(f"aish: fatal error: {e}", file=sys.stderr)
        sys.exit(1)
```

## Testing Plan

### Unit Tests
1. Command detection (AI vs shell)
2. Shell command execution
3. Environment preservation
4. Directory tracking
5. History management

### Integration Tests
1. Common shell workflows
2. Pipe and redirection
3. Background processes
4. Signal handling
5. Tool compatibility (git, npm, etc.)

### CI Integration Tests
1. Natural language interpretation
2. Command suggestion accuracy
3. Context awareness
4. Error handling

## Migration Strategy

1. **Preserve Legacy**: Keep current aish behavior when called with arguments
2. **Gradual Rollout**: Add `--shell` flag to enable new mode
3. **Testing Period**: Run parallel with bash/zsh for validation
4. **Full Migration**: Make shell mode default once stable

## Success Criteria

- [ ] Transparent command execution (99%+ compatibility)
- [ ] Natural language detection accuracy > 90%
- [ ] No performance regression
- [ ] Preserves all current aish features
- [ ] Works as login shell
- [ ] Integrates cleanly with Terma