# Terma Implementation Plan

## Phase 1: Rhetor Wrapper & Terminal Launch

### 1.1 Rhetor Wrapper Script
```bash
# terma/bin/rhetor-wrap
#!/usr/bin/env python3
- Wraps any shell command with Rhetor intelligence
- Monitors stdin/stdout without interfering
- Provides suggestions and safety checks
- Logs patterns to Engram
```

### 1.2 Terminal Launcher
```python
# terma/core/terminal_launcher.py
class TerminalLauncher:
    - detect_available_terminals() -> List[str]
    - launch_terminal(shell='bash', terminal=None) -> Process
    - attach_rhetor(process: Process) -> RhetorWrapper
```

### 1.2 Process Management
```python
# terma/core/process_manager.py
class ProcessManager:
    - spawn_process(command: str) -> Process
    - monitor_process(pid: int) -> ProcessStatus
    - terminate_process(pid: int) -> bool
    - list_managed_processes() -> List[Process]
```

### 1.3 Basic API
```python
# terma/api/app.py
- POST /execute - Execute command
- GET /status - Get shell status
- POST /terminate - Stop a process
- WebSocket /stream - Stream output
```

## Phase 2: Rhetor Integration

### 2.1 Rhetor Wrapper
```python
# terma/integrations/rhetor_wrapper.py
class RhetorTerminalMind:
    - __init__(personality="terminal_whisperer")
    - translate_intent(natural_language: str) -> CommandIntent
    - analyze_safety(command: str) -> SafetyAssessment
    - interpret_output(output: str) -> StructuredResult
```

### 2.2 Command Translation
```python
# terma/core/command_translator.py
class CommandTranslator:
    - register_pattern(intent: str, pattern: str)
    - translate(intent: CommandIntent) -> str
    - get_alternatives(intent: CommandIntent) -> List[str]
```

### 2.3 Output Parser
```python
# terma/core/output_parser.py
class OutputParser:
    - parse_ls(output: str) -> List[FileInfo]
    - parse_ps(output: str) -> List[ProcessInfo]
    - parse_error(output: str) -> ErrorInfo
    - parse_generic(output: str) -> Dict[str, Any]
```

## Phase 3: Safety & Context

### 3.1 Safety Checker
```python
# terma/safety/checker.py
class SafetyChecker:
    DANGEROUS_PATTERNS = [
        r'rm\s+-rf',
        r'>\s*/dev/.*',
        r'dd\s+if=.*of=/dev/.*'
    ]
    - is_dangerous(command: str) -> bool
    - get_confirmation_message(command: str) -> str
    - suggest_safer_alternative(command: str) -> Optional[str]
```

### 3.2 Context Manager
```python
# terma/core/context_manager.py
class TerminalContext:
    - pwd: str
    - env: Dict[str, str]
    - history: List[CommandHistory]
    - aliases: Dict[str, str]
    
    - update_pwd(new_path: str)
    - set_env(key: str, value: str)
    - add_to_history(command: str, result: CommandResult)
    - expand_command(command: str) -> str
```

### 3.3 State Persistence
```python
# terma/core/state_manager.py
class StateManager:
    - save_context(context: TerminalContext)
    - load_context() -> TerminalContext
    - save_patterns(patterns: List[Pattern])
    - load_patterns() -> List[Pattern]
```

## Phase 4: Learning & Integration

### 4.1 Pattern Learner
```python
# terma/learning/pattern_learner.py
class PatternLearner:
    - observe_execution(intent: str, command: str, success: bool)
    - get_best_command(intent: str) -> Optional[str]
    - export_patterns() -> List[LearnedPattern]
    - import_patterns(patterns: List[LearnedPattern])
```

### 4.2 Engram Integration
```python
# terma/integrations/engram_integration.py
class EngramPatternStore:
    - store_successful_pattern(pattern: LearnedPattern)
    - retrieve_patterns(intent: str) -> List[LearnedPattern]
    - share_patterns(namespace: str = "terma_patterns")
```

### 4.3 Tekton Commands
```python
# terma/integrations/tekton_commands.py
class TektonCommands:
    - status() -> ComponentStatus
    - start_component(name: str) -> bool
    - stop_component(name: str) -> bool
    - logs(component: str, lines: int = 100) -> str
```

## Testing Strategy

### Unit Tests
- Test each core class in isolation
- Mock shell interactions
- Test safety patterns exhaustively

### Integration Tests
- Test Rhetor integration
- Test real shell commands (in sandbox)
- Test learning and pattern matching

### Safety Tests
- Verify all dangerous patterns caught
- Test confirmation workflows
- Ensure no execution without approval

## File Structure
```
terma/
├── __init__.py
├── api/
│   ├── app.py
│   ├── models.py
│   └── websocket.py
├── core/
│   ├── async_shell.py
│   ├── command_translator.py
│   ├── context_manager.py
│   ├── output_parser.py
│   ├── process_manager.py
│   └── state_manager.py
├── integrations/
│   ├── engram_integration.py
│   ├── rhetor_wrapper.py
│   └── tekton_commands.py
├── learning/
│   └── pattern_learner.py
├── safety/
│   └── checker.py
└── tests/
    ├── test_shell.py
    ├── test_safety.py
    └── test_learning.py
```