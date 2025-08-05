# Development Sprint: Improve aish status Command

**Sprint ID**: SPRINT-2025-08-05-001  
**Component**: aish  
**Developer**: Iris  
**Priority**: High  
**Estimated Effort**: 2-3 hours  

## Objective
Update the `aish status` command to provide comprehensive system information about all CI components, tools, terminals, and configurations in a clean, easy-to-read format.

## Current State
The current `aish status` command is missing many components and doesn't show complete system information. Output is incomplete and doesn't include CI tools, all Greek Chorus components, or configuration details.

## Target Output Format
```
aish Status Report
==================================================
Configuration:
  TEKTON_ROOT: /Users/cskoons/projects/github/Coder-C
  TEKTON_PORT_BASE: 8300
  TEKTON_AI_PORT_BASE: 42000
  aish MCP Server: Running on port 8318

Greek Chorus Components:
------------------------------
  Component      Port   AI Port
  ----------     ----   -------
  engram         8300   42000
  hermes         8301   42001
  [... all components ...]

CI Tools:
------------------------------
  Tool              Port/Socket
  ----              -----------
  echo_tool         8500
  message_bus       /tmp/ci_message_bus.sock
  [... all tools ...]

Active Terminals:
------------------------------
  Casey (apollo) - /dev/ttys001
  [... all active terminals ...]

Active Forwards:
------------------------------
  apollo → Casey
  [... all forwards ...]

Additional Status Commands:
------------------------------
  tekton -c c status --json

==================================================
```

## Implementation Guide

### 1. Main Command File
**Location**: `shared/aish/src/commands/status.py`

This is where the main status command is implemented. You'll need to update the display logic here.

### 2. Get Configuration Data
```python
# Environment variables
from shared.env import TektonEnviron

tekton_root = TektonEnviron.get('TEKTON_ROOT', 'Not set')
port_base = TektonEnviron.get('TEKTON_PORT_BASE', '8300')
ai_port_base = TektonEnviron.get('TEKTON_AI_PORT_BASE', '42000')

# MCP server port
mcp_port = TektonEnviron.get('AISH_MCP_PORT', '8318')
```

### 3. Get Greek Chorus Components
```python
from shared.aish.src.registry.ci_registry import CIRegistry

registry = CIRegistry()

# The complete list is in CIRegistry.GREEK_CHORUS
# Each component has its port calculated dynamically
for name in registry.GREEK_CHORUS:
    ci_info = registry.get_ci(name)
    if ci_info:
        # Extract port from endpoint URL
        endpoint = ci_info.get('endpoint', '')
        port = endpoint.split(':')[-1] if endpoint else 'Unknown'
        
        # Get AI port
        try:
            ai_port = registry.get_ai_port(name)
        except:
            ai_port = 'Unknown'
```

### 4. Get CI Tools
CI tools need to be added to the registry. For now, you can hardcode them:
```python
CI_TOOLS = {
    'echo_tool': {'type': 'port', 'value': '8500'},
    'message_bus': {'type': 'socket', 'value': '/tmp/ci_message_bus.sock'},
    'context_manager': {'type': 'port', 'value': '8501'},
    'launcher': {'type': 'binary', 'value': '(binary)'}
}
```

### 5. Get Active Terminals
This data comes from the existing terminal list functionality:
```python
# You can call the existing terminal list function
# Or parse the .aish_terminals file directly
terminals_file = os.path.expanduser('~/.aish_terminals')
if os.path.exists(terminals_file):
    with open(terminals_file, 'r') as f:
        terminals = json.load(f)
```

### 6. Get Active Forwards
```python
# Read from forwards file
forwards_file = os.path.expanduser('~/.aish_forwards')
if os.path.exists(forwards_file):
    with open(forwards_file, 'r') as f:
        forwards = json.load(f)
```

### 7. Format the Display
Use consistent column widths for clean output:
```python
# For Greek Chorus section
print("  Component      Port   AI Port")
print("  ----------     ----   -------")
for name, port, ai_port in components:
    print(f"  {name:<14} {port:<6} {ai_port}")

# For CI Tools section  
print("  Tool              Port/Socket")
print("  ----              -----------")
for tool, info in CI_TOOLS.items():
    if info['type'] == 'socket':
        value = info['value']
    else:
        value = info['value']
    print(f"  {tool:<18} {value}")
```

## Key Files to Modify

1. **Main file**: `shared/aish/src/commands/status.py`
   - This contains the status command implementation
   - Update the `execute()` method with new display logic

2. **Registry**: `shared/aish/src/registry/ci_registry.py`
   - Already contains Greek Chorus components
   - May need to add CI tools registration

3. **Test the output formatting**:
   - Ensure columns align properly
   - Test with different terminal widths
   - Verify all components are listed

## Testing
```bash
# After making changes, test with:
aish status

# Verify all sections display correctly
# Check that ports are accurate
# Ensure formatting is clean and readable
```

## Notes
- Keep the display simple and deterministic
- Don't try to check if services are running (they always are)
- Focus on providing complete information in a clean format
- The Additional Status Commands section should show the actual tekton command for the current TEKTON_ROOT

## Success Criteria
- [ ] All Greek Chorus components listed with correct ports
- [ ] CI tools section added with port/socket info
- [ ] Configuration section at top with env variables
- [ ] Active terminals and forwards displayed
- [ ] Clean, aligned column formatting
- [ ] Additional status commands section added