# Tekton Script Argument Parsing Summary

## enhanced_tekton_launcher.py (start/launch command)

### Positional Arguments:
None

### Optional Arguments:
- `--components`, `-c`: Components to launch (comma-separated) or 'all'. Default: None
- `--launch-all`, `-a`: Launch all available components (boolean flag)
- `--monitor`, `-m`: Enable continuous health monitoring (boolean flag)
- `--health-retries`, `-r`: Number of health check retries. Default: 3
- `--verbose`, `-v`: Verbose output (boolean flag)
- `--save-logs`, `-s`: Preserve existing log files. Default: delete logs on startup (boolean flag)
- `--full`, `-f`: Launch with full development environment, includes UI DevTools MCP (boolean flag)
- `--ai`: Launch only AI specialists for components. Can optionally specify which components. Default: None

### Usage Examples:
```bash
tekton-launch                     # Launch all components
tekton-launch -c hermes,engram    # Launch specific components
tekton-launch -a                  # Launch all components
tekton-launch -f                  # Launch all + UI DevTools
tekton-launch --ai                # Launch AI specialists only
tekton-launch --ai hermes         # Launch AI for specific component
tekton-launch -v -m              # Verbose with monitoring
```

## enhanced_tekton_killer.py (stop/kill command)

### Positional Arguments:
None

### Optional Arguments:
- `--components`, `-c`: Components to kill (comma-separated) or 'all'. Default: None
- `--nuclear`, `-n`: ☢️ NUCLEAR OPTION: Kill everything on all Tekton ports (boolean flag)
- `--parallel`, `-p`: Kill components in parallel - faster but potentially unstable (boolean flag)
- `--dry-run`, `-d`: Dry run mode - show what would be killed without doing it (boolean flag)
- `--force`, `-f`: Skip safety confirmations (boolean flag)
- `--skip-graceful`, `-sg`: Skip HTTP graceful shutdown, go straight to SIGTERM (boolean flag)
- `--yes`, `-y`: Automatically answer yes to all prompts (boolean flag)
- `--verbose`, `-v`: Verbose output (boolean flag)
- `--ui-dev-tools`, `-u`: Kill UI DevTools MCP server only (boolean flag)
- `--ai`: Kill only AI specialists for components. Can optionally specify which. Default: None
- `--no-ai`: Don't kill AI specialists when killing components (boolean flag)

### Usage Examples:
```bash
tekton-kill                       # Kill all running components
tekton-kill -c hermes,engram      # Kill specific components
tekton-kill -n                    # Nuclear option (kills everything)
tekton-kill -y                    # Auto-confirm
tekton-kill -f                    # Force kill without confirmation
tekton-kill --ai                  # Kill all AI specialists
tekton-kill --ai hermes           # Kill AI for specific component
tekton-kill --no-ai               # Kill components but not their AIs
tekton-kill -u                    # Kill UI DevTools only
```

## enhanced_tekton_status.py (status command)

### Positional Arguments:
None

### Optional Arguments:
- `--json`, `-j`: Output in JSON format (boolean flag)
- `--component`, `-c`: Check specific component(s) - single or comma-separated list
- `--full`, `-f`: Full output with enhanced table and capabilities (boolean flag)
- `--log`, `-l`: Show recent log lines for each component. Optional arg: number of lines. Default: 5
- `--verbose`, `-v`: Verbose output - equivalent to --full --log (boolean flag)
- `--trends`, `-t`: Show trend information (boolean flag)
- `--no-storage`, `-n`: Disable metrics storage (boolean flag)
- `--watch`, `-w`: Watch mode - refresh every N seconds. Requires integer argument
- `--timeout`: HTTP request timeout in seconds. Default: 2.0
- `--quick`, `-q`: Quick mode - skip detailed checks for faster results (boolean flag)

### Usage Examples:
```bash
tekton-status                     # Show status of all components
tekton-status -c hermes           # Check specific component
tekton-status -c hermes,engram    # Check multiple components
tekton-status -j                  # JSON output
tekton-status -f                  # Full detailed output
tekton-status -l                  # Show last 5 log lines
tekton-status -l 10               # Show last 10 log lines
tekton-status -v                  # Verbose (full + logs)
tekton-status -w 5                # Watch mode, refresh every 5s
tekton-status -q                  # Quick mode for faster results
```

## Key Notes for C Parser Implementation:

1. **Component Names**: All scripts accept component names that can be:
   - Lowercase with underscores: `tekton_core`
   - Lowercase with hyphens: `tekton-core`
   - These are normalized internally to underscores

2. **Special Values**:
   - Component lists can be `"all"` to select all components
   - AI arguments can be empty (all AIs) or specific component names

3. **Boolean Flags**: Many arguments are simple boolean flags that don't take values

4. **Optional Arguments with Optional Values**:
   - `--log` can be used alone (defaults to 5) or with a number
   - `--ai` can be used alone (all AIs) or with specific component names

5. **Mutual Exclusions**:
   - Some flags like `--nuclear` in killer change the behavior completely
   - `--ai` and `--no-ai` in killer are mutually exclusive

6. **Default Behaviors**:
   - launcher: Without args, launches all components
   - killer: Without args, kills all running components
   - status: Without args, shows status of all components
