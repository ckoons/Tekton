# AI Forwarding Feature

## Overview

Enable human terminals to receive AI messages by adding a simple forwarding table. This allows Claude (or any human) to act as an intelligent proxy for AI components without API charges.

## The Simple Concept

```
Message for apollo → Check forward table → If forwarded, send to human mailbox
                                       → If not forwarded, send to AI socket
```

## Implementation

### 1. Command Interface

```bash
# Set up forwarding
aish forward apollo jill        # Forward apollo's mail to jill's terminal
aish forward rhetor jill        # Forward rhetor's mail to jill's terminal

# Remove forwarding  
aish unforward apollo           # Stop forwarding, return to AI socket

# Check forwarding status
aish forward list               # Show all active forwards
```

### 2. Forwarding Table Storage

**Location**: `~/.tekton/aish/forwarding.json`

```json
{
  "version": "1.0",
  "forwards": {
    "apollo": "jill",
    "rhetor": "jill",
    "prometheus": "alice"
  },
  "last_updated": "2025-01-05T16:00:00Z"
}
```

### 3. Core Routing Logic

**File to Update**: `/Users/cskoons/projects/github/Tekton/shared/aish/src/registry/socket_registry.py`

**Add forwarding check to message delivery**:

```python
# Around line 50-80 in socket_registry.py (where messages are routed)

import json
import os
from pathlib import Path

class SocketRegistry:
    def __init__(self):
        # ... existing init code ...
        self.forwarding_table = self.load_forwarding_table()
    
    def load_forwarding_table(self):
        """Load AI forwarding configuration"""
        forwarding_file = Path.home() / '.tekton' / 'aish' / 'forwarding.json'
        
        if forwarding_file.exists():
            try:
                with open(forwarding_file, 'r') as f:
                    data = json.load(f)
                    return data.get('forwards', {})
            except Exception:
                return {}
        return {}
    
    def save_forwarding_table(self):
        """Save forwarding table to disk"""
        forwarding_file = Path.home() / '.tekton' / 'aish' / 'forwarding.json'
        forwarding_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'version': '1.0',
            'forwards': self.forwarding_table,
            'last_updated': datetime.now().isoformat()
        }
        
        with open(forwarding_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def set_forward(self, ai_name, terminal_name):
        """Forward AI messages to terminal"""
        self.forwarding_table[ai_name] = terminal_name
        self.save_forwarding_table()
    
    def remove_forward(self, ai_name):
        """Stop forwarding AI messages"""
        if ai_name in self.forwarding_table:
            del self.forwarding_table[ai_name]
            self.save_forwarding_table()
    
    def send_message_to_ai(self, ai_name, message):
        """Main message routing with forwarding support"""
        
        # Check if AI is forwarded to a human terminal
        if ai_name in self.forwarding_table:
            terminal_name = self.forwarding_table[ai_name]
            
            # Format message for human inbox
            formatted_message = f"[{ai_name}] {message['sender']}: {message['content']}"
            
            # Send to terminal inbox instead of AI socket
            self.send_to_terminal_inbox(terminal_name, {
                'for_ai': ai_name,
                'from': message['sender'],
                'content': message['content'],
                'timestamp': message.get('timestamp', datetime.now().isoformat()),
                'display': formatted_message
            })
            
            return True
        
        # Normal AI routing (existing code)
        return self.send_to_ai_socket(ai_name, message)
    
    def send_to_terminal_inbox(self, terminal_name, message):
        """Send message to terminal's inbox (integrate with terma)"""
        # This integrates with the existing terma inbox system
        # Use the same mechanism that handles inter-terminal messages
        
        try:
            # Use existing terma message routing
            from commands.terma import terma_send_message_to_terminal
            terma_send_message_to_terminal(terminal_name, message['display'])
            return True
        except Exception as e:
            print(f"Error forwarding to terminal {terminal_name}: {e}")
            return False
```

### 4. Command Implementation

**File to Update**: `/Users/cskoons/projects/github/Tekton/shared/aish/src/commands/forward.py` (new file)

```python
"""
AI forwarding command handler.
"""

import os
import sys
from registry.socket_registry import SocketRegistry

def handle_forward_command(args):
    """Handle 'aish forward' commands"""
    
    if len(args) == 0:
        print_forward_usage()
        return 1
    
    command = args[0]
    registry = SocketRegistry()
    
    if command == "list":
        return list_forwards(registry)
    
    elif len(args) == 2:
        ai_name, terminal_name = args
        return set_forward(registry, ai_name, terminal_name)
    
    else:
        print_forward_usage()
        return 1

def print_forward_usage():
    """Print usage information"""
    print("Usage: aish forward <ai-name> <terminal-name>")
    print("       aish forward list")
    print("")
    print("Examples:")
    print("  aish forward apollo jill      # Forward apollo messages to jill")
    print("  aish forward rhetor alice     # Forward rhetor messages to alice")
    print("  aish forward list             # Show active forwards")

def set_forward(registry, ai_name, terminal_name):
    """Set up forwarding"""
    # Validate AI name
    valid_ais = ['apollo', 'athena', 'rhetor', 'prometheus', 'synthesis', 
                 'metis', 'harmonia', 'numa', 'noesis', 'engram', 'penia',
                 'hermes', 'ergon', 'sophia', 'telos']
    
    if ai_name not in valid_ais:
        print(f"Unknown AI: {ai_name}")
        print(f"Valid AIs: {', '.join(valid_ais)}")
        return 1
    
    # Set forwarding
    registry.set_forward(ai_name, terminal_name)
    print(f"✓ Forwarding {ai_name} messages to {terminal_name}")
    return 0

def list_forwards(registry):
    """List active forwards"""
    forwards = registry.forwarding_table
    
    if not forwards:
        print("No AI forwarding active")
        return 0
    
    print("Active AI Forwards:")
    print("-" * 30)
    for ai_name, terminal_name in forwards.items():
        print(f"  {ai_name:<12} → {terminal_name}")
    
    return 0
```

### 5. Unforward Command

**File to Update**: `/Users/cskoons/projects/github/Tekton/shared/aish/src/commands/unforward.py` (new file)

```python
"""
Remove AI forwarding.
"""

from registry.socket_registry import SocketRegistry

def handle_unforward_command(args):
    """Handle 'aish unforward' commands"""
    
    if len(args) != 1:
        print("Usage: aish unforward <ai-name>")
        return 1
    
    ai_name = args[0]
    registry = SocketRegistry()
    
    if ai_name in registry.forwarding_table:
        terminal_name = registry.forwarding_table[ai_name]
        registry.remove_forward(ai_name)
        print(f"✓ Stopped forwarding {ai_name} (was going to {terminal_name})")
        return 0
    else:
        print(f"No forwarding active for {ai_name}")
        return 1
```

### 6. Integration with Main aish Command

**File to Update**: `/Users/cskoons/projects/github/Tekton/shared/aish/aish`

**Around line 125-135** (where component commands are handled):

```python
# Add to the component handling section

    # Handle forwarding commands
    if args.ai_or_script == 'forward':
        from commands.forward import handle_forward_command
        return handle_forward_command(args.message or [])
    
    if args.ai_or_script == 'unforward':
        from commands.unforward import handle_unforward_command
        return handle_unforward_command(args.message or [])
```

## Usage Examples

### Set Up Claude as AI Proxy

```bash
# Claude starts in terminal "jill"
aish forward apollo jill
aish forward rhetor jill

# Now all apollo and rhetor messages come to jill's inbox
aish terma inbox

# Shows:
# [apollo] synthesis: "Need architecture review"
# [rhetor] athena: "Help with prompt optimization"

# Claude responds as the AI:
aish synthesis "apollo: I'll review the architecture. Key areas to focus on..."
aish athena "rhetor: For better prompts, try this pattern..."
```

### Check Status

```bash
aish forward list

# Output:
# Active AI Forwards:
# apollo     → jill
# rhetor     → jill
# prometheus → alice
```

### Stop Forwarding

```bash
aish unforward apollo
# Output: ✓ Stopped forwarding apollo (was going to jill)
```

## Benefits

1. **Zero API Costs** - Use Claude terminal sessions instead of paid APIs
2. **Simple Implementation** - Just routing table changes
3. **Transparent** - Senders don't know messages are forwarded
4. **Flexible** - Forward any AI to any terminal
5. **Reversible** - Easy to turn forwarding on/off

## Technical Notes

- Forwarding table persists across aish restarts
- Multiple AIs can forward to same terminal
- Terminal must be active to receive forwarded messages
- Integrates with existing terma inbox system
- No changes to senders - they still use `aish apollo "message"`

---
*"The world's smartest mail forwarding service"*