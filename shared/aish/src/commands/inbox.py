"""
Inbox command for aish - unified message management system
"""

import os
import json
import uuid
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from shared.env import TektonEnviron

# Simple print functions
def print_error(msg):
    print(f"Error: {msg}")

def print_success(msg):
    print(msg)

def print_info(msg):
    print(msg)

# Simple debug function
def debug_log(component, msg, level="INFO"):
    if os.environ.get('AISH_DEBUG'):
        print(f"[DEBUG:{component}] {msg}", file=sys.stderr)

def log_function(func):
    """Simple decorator for function logging"""
    return func

# Landmark: aish-inbox-implementation-2025-01-25
# The inbox system provides unified message management for all CIs,
# replacing the confusing terma-specific inbox commands with a clean,
# CI-friendly interface that supports batch JSON processing.

INBOX_TYPES = ['prompt', 'new', 'keep']

@log_function
def get_inbox_root() -> Path:
    """Get the root inbox directory"""
    tekton_root = TektonEnviron.get('TEKTON_ROOT')
    if not tekton_root:
        tekton_root = os.environ.get('TEKTON_ROOT', '/Users/cskoons/projects/github/Tekton')
    inbox_root = Path(tekton_root) / ".tekton" / "inboxes"
    return inbox_root

@log_function
def get_ci_inbox_dir(ci_name: str) -> Path:
    """Get the inbox directory for a specific CI"""
    inbox_root = get_inbox_root()
    ci_inbox = inbox_root / ci_name
    return ci_inbox

@log_function
def ensure_ci_inbox(ci_name: str) -> Path:
    """Ensure CI inbox directory and subdirectories exist"""
    ci_inbox = get_ci_inbox_dir(ci_name)
    
    # Create main CI inbox directory
    ci_inbox.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories for each inbox type
    for inbox_type in INBOX_TYPES:
        (ci_inbox / inbox_type).mkdir(exist_ok=True)
    
    debug_log("inbox", f"Ensured inbox directory: {ci_inbox}")
    return ci_inbox

@log_function
def create_message(from_ci: str, to_ci: str, message: str, purpose: str = "") -> Dict:
    """Create a message dict with metadata"""
    return {
        "id": str(uuid.uuid4())[:8],  # Short UUID for readability
        "from": from_ci,
        "to": to_ci,
        "timestamp": datetime.now().isoformat(),
        "purpose": purpose or "general",
        "message": message
    }

@log_function
def store_message(ci_name: str, inbox_type: str, message_data: Dict) -> str:
    """Store a message in the specified inbox and return message ID"""
    ensure_ci_inbox(ci_name)
    ci_inbox = get_ci_inbox_dir(ci_name)
    inbox_dir = ci_inbox / inbox_type
    
    # Use timestamp + message ID for filename to maintain order
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{timestamp}_{message_data['id']}.json"
    message_file = inbox_dir / filename
    
    try:
        with open(message_file, 'w') as f:
            json.dump(message_data, f, indent=2)
        debug_log("inbox", f"Stored message {message_data['id']} in {ci_name}/{inbox_type}")
        return message_data['id']
    except Exception as e:
        debug_log("inbox", f"Error storing message: {e}", level="ERROR")
        raise

@log_function
def load_messages(ci_name: str, inbox_type: str, from_filter: Optional[str] = None) -> List[Dict]:
    """Load all messages from an inbox, optionally filtered by sender"""
    ci_inbox = get_ci_inbox_dir(ci_name)
    inbox_dir = ci_inbox / inbox_type
    
    if not inbox_dir.exists():
        return []
    
    messages = []
    for message_file in sorted(inbox_dir.glob("*.json")):
        try:
            with open(message_file, 'r') as f:
                message_data = json.load(f)
                
            # Apply from filter if specified
            if from_filter and message_data.get('from') != from_filter:
                continue
                
            messages.append(message_data)
        except Exception as e:
            debug_log("inbox", f"Error loading message {message_file}: {e}", level="ERROR")
            continue
    
    return messages

@log_function
def remove_messages(ci_name: str, inbox_type: str, from_filter: Optional[str] = None) -> List[Dict]:
    """Remove and return messages from inbox"""
    ci_inbox = get_ci_inbox_dir(ci_name)
    inbox_dir = ci_inbox / inbox_type
    
    if not inbox_dir.exists():
        return []
    
    messages = []
    for message_file in sorted(inbox_dir.glob("*.json")):
        try:
            with open(message_file, 'r') as f:
                message_data = json.load(f)
                
            # Apply from filter if specified
            if from_filter and message_data.get('from') != from_filter:
                continue
                
            messages.append(message_data)
            message_file.unlink()  # Remove the file
            debug_log("inbox", f"Removed message {message_data.get('id')} from {ci_name}/{inbox_type}")
            
        except Exception as e:
            debug_log("inbox", f"Error removing message {message_file}: {e}", level="ERROR")
            continue
    
    return messages

@log_function
def count_messages(ci_name: str, inbox_type: str, from_filter: Optional[str] = None) -> int:
    """Count messages in inbox"""
    messages = load_messages(ci_name, inbox_type, from_filter)
    return len(messages)

@log_function
def clear_inbox(ci_name: str, inbox_type: str, from_filter: Optional[str] = None) -> int:
    """Clear all messages from inbox and return count removed"""
    messages = remove_messages(ci_name, inbox_type, from_filter)
    return len(messages)

@log_function
def get_current_ci() -> str:
    """Get current CI name from environment"""
    # Try terma terminal name first
    ci_name = os.environ.get('TERMA_TERMINAL_NAME')
    if ci_name:
        return ci_name
    
    # Fall back to system user
    return os.environ.get('USER', 'unknown')

@log_function
def parse_from_filter(args: List[str]) -> Tuple[List[str], Optional[str]]:
    """Parse 'from <ci>' filter from end of args list"""
    if len(args) >= 2 and args[-2] == 'from':
        return args[:-2], args[-1]
    return args, None

@log_function
def handle_inbox_send(args: List[str]):
    """Handle 'aish inbox send <type> <ci> "message"' command"""
    if len(args) < 3:
        print_error("See 'aish inbox training'")
        return
    
    inbox_type = args[0]
    to_ci = args[1]
    message = args[2]
    
    if inbox_type not in INBOX_TYPES:
        print_error(f"Invalid inbox type '{inbox_type}'. Must be: {', '.join(INBOX_TYPES)}")
        return
    
    from_ci = get_current_ci()
    purpose = os.environ.get('TERMA_PURPOSE', 'general')
    
    message_data = create_message(from_ci, to_ci, message, purpose)
    
    try:
        message_id = store_message(to_ci, inbox_type, message_data)
        print(message_id)  # Just return the message ID
    except Exception as e:
        print_error(f"Failed to send message: {e}")

@log_function
def handle_inbox_show(args: List[str]):
    """Handle 'aish inbox show <type> [from <ci>]' command"""
    args, from_filter = parse_from_filter(args)
    
    if len(args) < 1:
        print_error("See 'aish inbox training'")
        return
    
    inbox_type = args[0]
    if inbox_type not in INBOX_TYPES:
        print_error(f"Invalid inbox type '{inbox_type}'. Must be: {', '.join(INBOX_TYPES)}")
        return
    
    ci_name = get_current_ci()
    messages = load_messages(ci_name, inbox_type, from_filter)
    
    if not messages:
        print_info(f"No messages in {inbox_type} inbox")
        return
    
    print(f"\n{inbox_type.upper()} inbox:")
    print("-" * 60)
    
    for msg in messages:
        timestamp = datetime.fromisoformat(msg['timestamp']).strftime('%m/%d %H:%M')
        print(f"[{msg['id']}] {timestamp} from {msg['from']}")
        if msg.get('purpose') and msg['purpose'] != 'general':
            print(f"    Purpose: {msg['purpose']}")
        print(f"    {msg['message']}")
        print()

@log_function
def handle_inbox_json(args: List[str]):
    """Handle 'aish inbox json <type> [from <ci>]' command"""
    args, from_filter = parse_from_filter(args)
    
    if len(args) < 1:
        print_error("See 'aish inbox training'")
        return
    
    inbox_type = args[0]
    if inbox_type not in INBOX_TYPES:
        print_error(f"Invalid inbox type '{inbox_type}'. Must be: {', '.join(INBOX_TYPES)}")
        return
    
    ci_name = get_current_ci()
    messages = load_messages(ci_name, inbox_type, from_filter)
    
    print(json.dumps(messages, indent=2))

@log_function
def handle_inbox_get(args: List[str]):
    """Handle 'aish inbox get <type> [from <ci>]' command"""
    args, from_filter = parse_from_filter(args)
    
    if len(args) < 1:
        print_error("See 'aish inbox training'")
        return
    
    inbox_type = args[0]
    if inbox_type not in INBOX_TYPES:
        print_error(f"Invalid inbox type '{inbox_type}'. Must be: {', '.join(INBOX_TYPES)}")
        return
    
    ci_name = get_current_ci()
    messages = remove_messages(ci_name, inbox_type, from_filter)
    
    print(json.dumps(messages, indent=2))

@log_function
def handle_inbox_count(args: List[str]):
    """Handle 'aish inbox count <type> [from <ci>]' command"""
    args, from_filter = parse_from_filter(args)
    
    if len(args) < 1:
        print_error("See 'aish inbox training'")
        return
    
    inbox_type = args[0]
    if inbox_type not in INBOX_TYPES:
        print_error(f"Invalid inbox type '{inbox_type}'. Must be: {', '.join(INBOX_TYPES)}")
        return
    
    ci_name = get_current_ci()
    count = count_messages(ci_name, inbox_type, from_filter)
    
    print(count)  # Just the number

@log_function
def handle_inbox_clear(args: List[str]):
    """Handle 'aish inbox clear <type> [from <ci>]' command"""
    args, from_filter = parse_from_filter(args)
    
    if len(args) < 1:
        print_error("See 'aish inbox training'")
        return
    
    inbox_type = args[0]
    if inbox_type not in INBOX_TYPES:
        print_error(f"Invalid inbox type '{inbox_type}'. Must be: {', '.join(INBOX_TYPES)}")
        return
    
    ci_name = get_current_ci()
    count = clear_inbox(ci_name, inbox_type, from_filter)
    
    # Silent operation - no output unless error

@log_function
def handle_inbox_list(args: List[str]):
    """Handle 'aish inbox' (default) command - show counts"""
    ci_name = get_current_ci()
    
    counts = []
    for inbox_type in INBOX_TYPES:
        count = count_messages(ci_name, inbox_type)
        counts.append(f"{inbox_type}:{count}")
    
    print("  ".join(counts))

@log_function
def handle_inbox_help(args: List[str]):
    """Handle 'aish inbox help' command"""
    print("""
aish inbox commands:

Basic Usage:
  aish inbox                         Show message counts (prompt:1 new:3 keep:0)
  aish inbox send <type> <ci> "msg"  Send message to CI's inbox
  aish inbox show <type>             Display messages in text format
  aish inbox json <type>             Display messages in JSON format
  aish inbox get <type>              Get and remove all messages (JSON)
  aish inbox count <type>            Count messages (returns number only)
  aish inbox clear <type>            Remove all messages (silent)

Inbox Types:
  prompt - Urgent messages needing immediate attention
  new    - Regular incoming messages
  keep   - Saved/archived messages

Filtering:
  Add 'from <ci-name>' to any command to filter by sender:
  aish inbox json new from apollo
  aish inbox get prompt from numa
  aish inbox count keep from rhetor

Examples:
  aish inbox send prompt numa "Please review the PR"
  aish inbox get new | jq '.[] | .message'
  aish inbox count prompt
  aish inbox clear keep from apollo

For CI training: aish inbox training
""")

@log_function
def handle_inbox_training(args: List[str]):
    """Handle 'aish inbox training' command"""
    print("""
INBOX TRAINING FOR CIs

The inbox system provides structured message management with three types:
- prompt: Urgent messages requiring immediate attention
- new: Regular incoming messages  
- keep: Saved/archived messages

BATCH PROCESSING (Recommended):
# Process all urgent messages at once
messages=$(aish inbox get prompt)
echo "$messages" | jq -r '.[] | "From: \\(.from) - \\(.message)"'

# Count-based loops
while [ $(aish inbox count new) -gt 0 ]; do
    aish inbox get new | process_messages
done

# Filter by sender
apollo_messages=$(aish inbox get new from apollo)

MESSAGE STRUCTURE:
Each message is JSON with:
{
  "id": "msg-7f3a4b21",
  "from": "sender-ci-name", 
  "to": "recipient-ci-name",
  "timestamp": "2025-01-25T10:30:00.123456",
  "purpose": "code-review",
  "message": "The actual message content"
}

SENDING MESSAGES:
# Send to specific inbox type
msg_id=$(aish inbox send prompt numa "Urgent: build failed")
msg_id=$(aish inbox send new rhetor "Please optimize this prompt")

COMMON PATTERNS:
# Check for urgent messages first
if [ $(aish inbox count prompt) -gt 0 ]; then
    urgent=$(aish inbox get prompt)
    # Process urgent messages
fi

# Regular message processing
new_msgs=$(aish inbox get new)
if [ -n "$new_msgs" ]; then
    echo "$new_msgs" | jq -r '.[] | select(.purpose == "code-review") | .message'
fi

# Archive completed work
aish inbox send keep self "Completed: authentication module"

INTEGRATION WITH FORWARDING:
When AIs are forwarded to your terminal, messages appear in your 'new' inbox
with full JSON structure including purpose context.
""")

@log_function
def handle_inbox_command(args: List[str]):
    """Main entry point for inbox command"""
    if not args:
        # Default behavior: show list
        handle_inbox_list([])
        return
    
    subcommand = args[0]
    subargs = args[1:]
    
    if subcommand == "send":
        handle_inbox_send(subargs)
    elif subcommand == "show":
        handle_inbox_show(subargs)
    elif subcommand == "json":
        handle_inbox_json(subargs)
    elif subcommand == "get":
        handle_inbox_get(subargs)
    elif subcommand == "count":
        handle_inbox_count(subargs)
    elif subcommand == "clear":
        handle_inbox_clear(subargs)
    elif subcommand == "help":
        handle_inbox_help(subargs)
    elif subcommand == "training":
        handle_inbox_training(subargs)
    else:
        print_error(f"Unknown inbox command: {subcommand}")
        print_error("See 'aish inbox help'")