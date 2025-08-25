# aish Help System and Communication - Implementation Plan

## Overview

This document details the implementation steps for the expanded aish sprint including:
1. Unified command syntax
2. Message visibility for CIs
3. Help system with documentation paths

## Implementation Steps

### Phase 1: Fix aish Syntax

**File**: `/Users/cskoons/projects/github/Tekton/shared/aish/aish`

**Changes**:
1. Replace the current routing logic to implement unified syntax
2. Add direct CI messaging without synthetic pipelines
3. Create consistent command handling

```python
# After line 91 (args = parser.parse_args())

    # Handle help command
    if args.ai_or_script == "help":
        # General aish help
        print("Usage: aish [options] [component] [command/message]")
        print("CI Training: /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/AITraining/aish/")
        print("User Guides: /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/UserGuides/aish/")
        return
    
    # Known CI names and special components
    ai_names = ['numa', 'tekton', 'prometheus', 'telos', 'metis', 'harmonia',
                'synthesis', 'athena', 'sophia', 'noesis', 'engram', 'apollo',
                'rhetor', 'penia', 'hermes', 'ergon', 'terma', 'team-chat']
    
    # Check if first argument is a component
    if args.ai_or_script and args.ai_or_script.lower() in ai_names:
        component = args.ai_or_script.lower()
        
        # Special handling for terma
        if component == 'terma':
            from commands.terma import handle_terma_command
            return handle_terma_command(args.message)
        
        # Check for help command
        if args.message and args.message[0] == "help":
            print(f"Usage: aish {component} [message]")
            print(f"CI Training: /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/AITraining/{component}/")
            print(f"User Guides: /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/UserGuides/{component}/")
            return
        
        # Direct CI messaging
        if not sys.stdin.isatty():
            input_data = sys.stdin.read()
        elif args.message:
            input_data = ' '.join(args.message)
        else:
            print(f"[aish] Entering interactive mode with {component}")
            print("Type your message and press Ctrl+D when done:")
            input_data = sys.stdin.read()
        
        # Send directly to CI (no synthetic pipeline)
        if component == 'team-chat':
            shell.broadcast_message(input_data)
        else:
            shell.send_to_ai(component, input_data)
```

### Phase 2: Fix Message Display

**File**: `/Users/cskoons/projects/github/Tekton/shared/aish/aish-proxy`

**Changes**:
1. Update `display_terminal_message()` to write to /dev/tty
2. Add in-memory message storage

```python
# Add at top of file after imports
from collections import deque

# Global in-memory message storage
message_inbox = {
    'new': deque(maxlen=100),
    'keep': deque(maxlen=50)
}

def display_terminal_message(msg_info):
    """Display an inter-terminal message."""
    from_name = msg_info.get("from", "unknown")
    message = msg_info.get("message", "")
    routing = msg_info.get("routing", "direct")
    
    # Format based on routing type
    if routing == "broadcast":
        prefix = f"[TERMA: broadcast from {from_name}]"
    elif routing.startswith("@"):
        prefix = f"[TERMA: to {routing} from {from_name}]"
    else:
        prefix = f"[TERMA: from {from_name}]"
    
    # Write to terminal directly
    try:
        with open('/dev/tty', 'w') as tty:
            tty.write(f"\n{prefix} {message}\n")
            tty.flush()
    except:
        # Fallback to print if /dev/tty not available
        print(f"\n{prefix} {message}")
    
    # Add to in-memory inbox
    message_inbox['new'].append({
        'id': len(message_inbox['new']) + 1,
        'timestamp': datetime.now().isoformat(),
        'from': from_name,
        'message': message,
        'routing': routing
    })
```

### Phase 3: Implement Two-Inbox System

**File**: `/Users/cskoons/projects/github/Tekton/shared/aish/src/commands/terma.py`

**Changes**:
1. Add inbox command handling
2. Implement new/keep inbox operations

```python
# Add to handle_terma_command() after existing commands

    elif command == "inbox":
        # Handle inbox subcommands
        if len(args) == 1:
            # Default: show new messages
            return terma_inbox_new()
        
        subcommand = args[1]
        if subcommand == "new":
            return terma_inbox_new()
        elif subcommand == "keep":
            return terma_inbox_keep()
        elif subcommand == "read" and len(args) > 2:
            return terma_inbox_read(int(args[2]))
        elif subcommand == "trash":
            return terma_inbox_trash()
        else:
            print("Usage: aish terma inbox [new|keep|read N|trash]")
            return 1

# Add new functions for inbox management

def terma_inbox_new():
    """Show new messages."""
    # Import from the running aish-proxy instance
    try:
        # This is a bit tricky - we need to access the proxy's memory
        # For now, we'll store in a shared file temporarily
        print("New Messages:")
        print("-" * 60)
        print("(Inbox feature coming soon)")
        return 0
    except Exception as e:
        print(f"Error accessing inbox: {e}")
        return 1

def terma_inbox_keep():
    """Show kept messages."""
    print("Kept Messages:")
    print("-" * 60)
    print("(No kept messages yet)")
    return 0

def terma_inbox_read(msg_id):
    """Move message to keep inbox."""
    print(f"Moving message {msg_id} to keep...")
    print("(Feature coming soon)")
    return 0

def terma_inbox_trash():
    """Clear new inbox."""
    print("Clearing new messages...")
    print("(Feature coming soon)")
    return 0
```

### Phase 4: Add send_to_ai Method

**File**: `/Users/cskoons/projects/github/Tekton/shared/aish/src/core/shell.py`

**Changes**:
1. Add method to send messages directly to AI

```python
def send_to_ai(self, ai_name, message):
    """Send message directly to CI via Rhetor."""
    try:
        # Use the socket registry to communicate
        import json
        import urllib.request
        
        rhetor_url = self.rhetor_endpoint
        
        # Create request to Rhetor
        data = {
            'ai': ai_name,
            'message': message,
            'context': {}
        }
        
        # Send to Rhetor's message endpoint
        url = f"{rhetor_url}/api/message"
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read())
            print(result.get('response', 'No response'))
            
    except Exception as e:
        print(f"Error communicating with {ai_name}: {e}")

def broadcast_message(self, message):
    """Broadcast message to all CIs."""
    # Special handling for team-chat
    self.send_to_ai('team-chat', message)
```

### Phase 5: Create Documentation Structure

Run the create_directories.sh script from the sprint directory:

```bash
#!/bin/bash
# Create documentation directories

TEKTON_ROOT="/Users/cskoons/projects/github/Tekton"
DOC_BASE="$TEKTON_ROOT/MetaData/TektonDocumentation"

# Create base directories
mkdir -p "$DOC_BASE/AITraining"
mkdir -p "$DOC_BASE/UserGuides"

# CI components
COMPONENTS="aish numa tekton prometheus telos metis harmonia synthesis athena sophia noesis engram apollo rhetor penia hermes ergon terma"

# Create directories for each component
for comp in $COMPONENTS; do
    mkdir -p "$DOC_BASE/AITraining/$comp"
    mkdir -p "$DOC_BASE/UserGuides/$comp"
    
    # Create placeholder READMEs
    echo "# $comp CI Training Documentation" > "$DOC_BASE/AITraining/$comp/README.md"
    echo "# $comp User Guide" > "$DOC_BASE/UserGuides/$comp/README.md"
done

echo "Documentation structure created!"
```

### Testing Plan

1. **Test unified syntax**:
   ```bash
   aish apollo "What is Tekton?"
   echo "test" | aish penia
   aish terma list
   aish help
   aish apollo help
   ```

2. **Test message display**:
   - Send messages between terminals
   - Verify they appear without disrupting prompts

3. **Test inbox system**:
   ```bash
   aish terma inbox
   aish terma inbox keep
   aish terma inbox read 1
   aish terma inbox trash
   ```

4. **Test help system**:
   - Verify all components show correct paths
   - Check that documentation directories exist

## Notes

- The in-memory inbox system requires some IPC mechanism between aish-proxy and terma commands
- For initial implementation, we may use a simple shared memory approach
- Future enhancement: Use Rhetor's message queue for persistence