"""
Terma command handler for inter-terminal communication.

Handles commands like:
- aish terma list
- aish terma whoami
- aish terma bob "message"
- aish terma @planning "message"
- aish terma broadcast "message"
- aish terma training-for-ais
- aish terma error-report "message"
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error
from datetime import datetime

# Get endpoints from environment
TERMA_ENDPOINT = os.environ.get('TERMA_ENDPOINT', 'http://localhost:8004')

def handle_terma_command(args):
    """Handle terma inter-terminal communication commands."""
    if len(args) < 1:
        print_usage()
        return 1
    
    command = args[0]
    
    # Handle help command
    if command == "help":
        print("Usage: aish terma [command] [args]")
        print("\nBasic Commands:")
        print("  list - List active terminals")
        print("  whoami - Show your terminal info")
        print("  <name> 'msg' - Send to terminal")
        print("  @<purpose> 'msg' - Send by purpose")
        print("  broadcast 'msg' - Send to all others")
        print("\nInbox Commands:")
        print("  inbox - Show all inboxes (prompt, new, keep)")
        print("  inbox prompt - Show urgent prompt messages")
        print("  inbox prompt pop - Pop from prompt inbox")
        print("  inbox new pop - Pop from new inbox")
        print("  inbox keep push 'text' - Save to keep")
        print("  inbox keep read [remove] - Read from keep")
        print("\nDocumentation:")
        tekton_root = os.environ.get('TEKTON_ROOT', '/Users/cskoons/projects/github/Tekton')
        print(f"  AI Training: {tekton_root}/MetaData/TektonDocumentation/AITraining/terma/")
        print(f"  User Guides: {tekton_root}/MetaData/TektonDocumentation/UserGuides/terma/")
        return 0
    
    # Handle special commands
    if command == "list":
        return terma_list_terminals()
    elif command == "whoami":
        return terma_whoami()
    elif command == "training-for-ais":
        return terma_training_info()
    elif command == "inbox":
        # Handle inbox subcommands
        if len(args) == 1:
            # Default: show both inboxes
            return terma_inbox_both()
        
        subcommand = args[1]
        if subcommand == "keep":
            # Check for keep subcommands
            if len(args) == 2:
                return terma_inbox_keep()
            
            keep_cmd = args[2]
            if keep_cmd == "push" and len(args) > 3:
                return terma_inbox_keep_push(' '.join(args[3:]))
            elif keep_cmd == "write" and len(args) > 3:
                return terma_inbox_keep_write(' '.join(args[3:]))
            elif keep_cmd == "read":
                remove = len(args) > 3 and args[3] == "remove"
                return terma_inbox_keep_read(remove)
            else:
                print("Usage: aish terma inbox keep [push|write|read [remove]]")
                return 1
                
        elif subcommand == "new":
            if len(args) > 2 and args[2] == "pop":
                return terma_inbox_new_pop()
            else:
                print("Usage: aish terma inbox new pop")
                return 1
        elif subcommand == "prompt":
            if len(args) > 2 and args[2] == "pop":
                return terma_inbox_prompt_pop()
            else:
                # Just show prompt messages
                return terma_inbox_prompt()
        else:
            print("Usage: aish terma inbox [prompt|keep|new] [pop]")
            return 1
    elif command == "error-report":
        if len(args) < 2:
            print("Usage: aish terma error-report 'error message'")
            return 1
        return terma_error_report(' '.join(args[1:]))
    elif command == "broadcast":
        if len(args) < 2:
            print("Usage: aish terma broadcast 'message'")
            return 1
        return terma_send_message("broadcast", ' '.join(args[1:]))
    elif command.startswith("@"):
        # Purpose-based routing
        if len(args) < 2:
            print(f"Usage: aish terma {command} 'message'")
            return 1
        return terma_send_message(command, ' '.join(args[1:]))
    elif command == "*":
        # Broadcast to all including self
        if len(args) < 2:
            print("Usage: aish terma * 'message'")
            return 1
        return terma_send_message("*", ' '.join(args[1:]))
    else:
        # Direct message to named terminal(s)
        if len(args) < 2:
            # Show help for direct messaging
            print(f"Usage: aish terma {command} 'message'")
            print(f"To send a message to terminal '{command}', include the message")
            return 1
        return terma_send_message(command, ' '.join(args[1:]))

def print_usage():
    """Print usage information for terma commands."""
    print("Usage: aish terma <command> [args]")
    print("\nCommands:")
    print("  list                 - List active terminals")
    print("  inbox                - Show all inboxes (prompt, new, keep)")
    print("  inbox prompt         - Show urgent messages")
    print("  inbox prompt pop     - Pop from prompt inbox")
    print("  inbox keep           - Show keep inbox")
    print("  inbox new pop        - Pop message from new")
    print("  inbox keep push 'text' - Push to keep (front)")
    print("  inbox keep write 'text' - Write to keep (end)")
    print("  inbox keep read [remove] - Read from keep")
    print("  whoami               - Show current terminal info")
    print("  <name> 'message'     - Send to specific terminal")
    print("  @<purpose> 'message' - Send to terminals by purpose")
    print("  broadcast 'message'  - Send to all other terminals")
    print("  * 'message'          - Send to all including self")
    print("  training-for-ais     - Get AI training docs location")
    print("  error-report 'msg'   - Report an error or issue")
    print("\nExamples:")
    print("  aish terma list")
    print("  aish terma inbox")
    print("  aish terma inbox new pop")
    print("  aish terma bob 'need help with auth'")
    print("  aish terma @planning 'team sync at 3pm'")
    print("  aish terma broadcast 'anyone know WebSockets?'")

def terma_list_terminals():
    """List all active terminals."""
    try:
        url = f"{TERMA_ENDPOINT}/api/mcp/v2/terminals/list"
        req = urllib.request.Request(url)
        
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read())
            
        if not data.get("terminals"):
            print("No active terminals")
            return 0
        
        # Get current terminal info
        my_id = os.environ.get('TERMA_SESSION_ID', '')
        
        print("Active Terminals:")
        print("-" * 60)
        for term in data["terminals"]:
            # Mark current terminal
            marker = "(you)" if term.get("terma_id", "").startswith(my_id[:8]) else "     "
            
            name = term.get("name", "unnamed") or "unnamed"
            pid = term.get("pid", 0)
            purpose = term.get("purpose") or "none"
            status = term.get("status", "unknown") or "unknown"
            
            print(f"{name:<12} [{pid:>6}]  Purpose: {purpose:<15} Status: {status:<8} {marker}")
        
        return 0
        
    except Exception as e:
        print(f"Error listing terminals: {e}")
        print("Is Terma running on port 8004?")
        return 1

def terma_whoami():
    """Show current terminal information."""
    try:
        name = os.environ.get('TERMA_TERMINAL_NAME', 'unnamed')
        session_id = os.environ.get('TERMA_SESSION_ID', 'unknown')
        pid = os.getpid()
        
        # Try to get purpose from terminal info
        purpose = "unknown"
        try:
            url = f"{TERMA_ENDPOINT}/api/mcp/v2/terminals/list"
            req = urllib.request.Request(url)
            
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read())
                
            for term in data.get("terminals", []):
                if term.get("terma_id", "").startswith(session_id[:8]):
                    purpose = term.get("purpose") or "none"
                    break
        except:
            pass
        
        print(f"You are: {name} [{pid}] Purpose: {purpose}")
        print(f"Session: {session_id[:8]}...")
        
        return 0
        
    except Exception as e:
        print(f"Error getting terminal info: {e}")
        return 1

def terma_training_info():
    """Show AI training documentation location."""
    training_dir = os.environ.get('TEKTON_AI_TRAINING')
    
    if not training_dir:
        print("TEKTON_AI_TRAINING environment variable not set")
        print("This terminal may not be launched through Terma")
        return 1
    
    print(f"AI Training Documentation Directory: {training_dir}")
    print("\nTo explore available documentation:")
    print(f"  ls {training_dir}")
    print(f"  cat {training_dir}/README.md")
    print(f"  cat {training_dir}/TermaCommunication.md")
    
    # List files if directory exists
    if os.path.exists(training_dir):
        print("\nAvailable documents:")
        for file in sorted(os.listdir(training_dir)):
            if file.endswith('.md'):
                print(f"  - {file}")
    
    return 0

def terma_error_report(message):
    """Report an error or issue."""
    try:
        # For now, just print confirmation
        # In Phase 2, we'll send to Terma for logging
        print(f"Error report submitted: {message}")
        print("Thank you for the feedback!")
        
        # Log to local file for now
        log_dir = os.path.expanduser("~/.tekton/terma/error_reports")
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"error_{timestamp}.json")
        
        error_data = {
            "terma_id": os.environ.get('TERMA_SESSION_ID', 'unknown'),
            "terminal_name": os.environ.get('TERMA_TERMINAL_NAME', 'unnamed'),
            "timestamp": datetime.now().isoformat(),
            "error_message": message,
            "type": "user_report"
        }
        
        with open(log_file, 'w') as f:
            json.dump(error_data, f, indent=2)
        
        return 0
        
    except Exception as e:
        print(f"Failed to submit error report: {e}")
        return 1

def terma_send_message(target, message):
    """Send a message to terminal(s)."""
    try:
        # Get sender info
        sender_id = os.environ.get('TERMA_SESSION_ID', 'unknown')
        sender_name = os.environ.get('TERMA_TERMINAL_NAME', 'unnamed')
        
        if sender_id == 'unknown':
            print("This terminal was not launched through Terma")
            print("Inter-terminal communication requires Terma-launched terminals")
            return 1
        
        # Build message payload
        msg_data = {
            "from": {
                "terma_id": sender_id,
                "name": sender_name
            },
            "target": target,  # name, @purpose, broadcast, or *
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "type": "chat"
        }
        
        # Send to Terma router endpoint
        url = f"{TERMA_ENDPOINT}/api/mcp/v2/terminals/route-message"
        data = json.dumps(msg_data).encode('utf-8')
        req = urllib.request.Request(url, data=data, 
                                   headers={'Content-Type': 'application/json'})
        
        with urllib.request.urlopen(req, timeout=5) as response:
            result = json.loads(response.read())
        
        if result.get("success"):
            delivered = result.get("delivered_to", [])
            if delivered:
                if target == "broadcast":
                    print(f"Message broadcast to {len(delivered)} terminal(s)")
                elif target.startswith("@"):
                    print(f"Message sent to {len(delivered)} {target} terminal(s)")
                else:
                    print(f"Message sent to: {', '.join(delivered)}")
            else:
                print("No terminals matched the target")
        else:
            print(f"Failed to send message: {result.get('error', 'Unknown error')}")
            
        return 0
        
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("Terma message routing not available yet")
            print("This feature will be implemented in the next update")
        else:
            print(f"Error sending message: HTTP {e.code}")
        return 1
    except Exception as e:
        print(f"Error sending message: {e}")
        return 1


def terma_send_message_to_terminal(terminal_name, message):
    """Send message directly to specific terminal's inbox."""
    try:
        # Build message for specific terminal
        msg_data = {
            "from": {
                "terma_id": "aish-forwarding",
                "name": "AI Forwarding"
            },
            "target": terminal_name,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "type": "ai_forward"
        }
        
        url = f"{TERMA_ENDPOINT}/api/mcp/v2/terminals/route-message"
        data = json.dumps(msg_data).encode('utf-8')
        req = urllib.request.Request(url, data=data, 
                                   headers={'Content-Type': 'application/json'})
        
        with urllib.request.urlopen(req, timeout=5) as response:
            result = json.loads(response.read())
        
        return result.get("success", False)
        
    except Exception as e:
        print(f"Failed to send to terminal {terminal_name}: {e}")
        return False

def terma_inbox_both():
    """Show both new and keep inboxes to stdout."""
    try:
        inbox_file = os.path.expanduser("~/.tekton/terma/.inbox_snapshot")
        
        if os.path.exists(inbox_file):
            with open(inbox_file, 'r') as f:
                data = json.load(f)
            
            prompt_messages = data.get('prompt', [])
            new_messages = data.get('new', [])
            keep_messages = data.get('keep', [])
            
            # Show prompt messages first (high priority)
            if prompt_messages:
                print(f"[PROMPT: {len(prompt_messages)} urgent messages]")
                for i, msg in enumerate(prompt_messages[:10], 1):  # Show first 10
                    time_str = msg['timestamp'][11:19] if 'timestamp' in msg else "??:??:??"
                    from_name = msg.get('from', 'unknown')
                    message = msg.get('message', '')
                    if len(message) > 50:
                        message = message[:47] + "..."
                    print(f"{i}. [{time_str}] {from_name}: {message}")
                print()  # Extra line for clarity
            
            # Show new messages
            print(f"[NEW: {len(new_messages)} messages]")
            if new_messages:
                for i, msg in enumerate(new_messages[:20], 1):  # Show first 20
                    time_str = msg['timestamp'][11:19] if 'timestamp' in msg else "??:??:??"
                    from_name = msg.get('from', 'unknown')
                    message = msg.get('message', '')
                    if len(message) > 50:
                        message = message[:47] + "..."
                    print(f"{i}. [{time_str}] {from_name}: {message}")
            
            # Show keep messages
            print(f"\n[KEEP: {len(keep_messages)} messages]")
            if keep_messages:
                for i, msg in enumerate(keep_messages[:10], 1):  # Show first 10
                    time_str = msg['timestamp'][11:19] if 'timestamp' in msg else "??:??:??"
                    content = msg.get('message', msg) if isinstance(msg, dict) else msg
                    if len(content) > 60:
                        content = content[:57] + "..."
                    print(f"{i}. [{time_str}] {content}")
        else:
            print("[PROMPT: 0 urgent messages]")
            print("[NEW: 0 messages]")
            print("[KEEP: 0 messages]")
            print("\n(Check your inbox frequently with 'aish terma inbox')")
        
        return 0
    except Exception as e:
        print(f"Error accessing inbox: {e}")
        return 1

def terma_inbox_keep():
    """Show kept messages."""
    try:
        inbox_file = os.path.expanduser("~/.tekton/terma/.inbox_snapshot")
        
        if os.path.exists(inbox_file):
            with open(inbox_file, 'r') as f:
                messages = json.load(f).get('keep', [])
            
            if messages:
                print("\nKept Messages:")
                print("-" * 60)
                for msg in messages:
                    time_str = msg['timestamp'][11:19] if 'timestamp' in msg else "??:??:??"
                    from_name = msg.get('from', 'unknown')
                    message = msg.get('message', '')
                    print(f"[{time_str}] {from_name}: {message}")
            else:
                print("No kept messages")
        else:
            print("No kept messages yet")
        
        return 0
    except Exception as e:
        print(f"Error accessing kept messages: {e}")
        return 1

def terma_inbox_new_pop():
    """Pop first message from new inbox (FIFO)."""
    try:
        inbox_file = os.path.expanduser("~/.tekton/terma/.inbox_snapshot")
        
        if os.path.exists(inbox_file):
            with open(inbox_file, 'r') as f:
                data = json.load(f)
            
            new_messages = data.get('new', [])
            if new_messages:
                # Pop first message (FIFO)
                msg = new_messages[0]
                time_str = msg['timestamp'][11:19] if 'timestamp' in msg else "??:??:??"
                from_name = msg.get('from', 'unknown')
                message = msg.get('message', '')
                
                # Output the message to stdout
                print(f"[{time_str}] {from_name}: {message}")
                
                # Write command for proxy to remove it
                cmd_dir = os.path.expanduser("~/.tekton/terma/commands")
                os.makedirs(cmd_dir, exist_ok=True)
                cmd_file = os.path.join(cmd_dir, f"inbox_pop_{int(time.time()*1000)}.json")
                with open(cmd_file, 'w') as f:
                    json.dump({'action': 'pop', 'timestamp': datetime.now().isoformat()}, f)
                
                return 0
            else:
                print("No new messages")
                return 0
        else:
            print("No messages in inbox")
            return 0
            
    except Exception as e:
        print(f"Error popping message: {e}")
        return 1

def terma_inbox_prompt():
    """Show only prompt messages."""
    try:
        inbox_file = os.path.expanduser("~/.tekton/terma/.inbox_snapshot")
        
        if os.path.exists(inbox_file):
            with open(inbox_file, 'r') as f:
                data = json.load(f)
            
            prompt_messages = data.get('prompt', [])
            
            print(f"[PROMPT: {len(prompt_messages)} urgent messages]")
            if prompt_messages:
                for i, msg in enumerate(prompt_messages[:20], 1):  # Show first 20
                    time_str = msg['timestamp'][11:19] if 'timestamp' in msg else "??:??:??"
                    from_name = msg.get('from', 'unknown')
                    message = msg.get('message', '')
                    if len(message) > 60:
                        message = message[:57] + "..."
                    print(f"{i}. [{time_str}] {from_name}: {message}")
        else:
            print("[PROMPT: 0 urgent messages]")
        
        return 0
    except Exception as e:
        print(f"Error accessing prompt inbox: {e}")
        return 1

def terma_inbox_prompt_pop():
    """Pop first message from prompt inbox (FIFO)."""
    try:
        inbox_file = os.path.expanduser("~/.tekton/terma/.inbox_snapshot")
        
        if os.path.exists(inbox_file):
            with open(inbox_file, 'r') as f:
                data = json.load(f)
            
            prompt_messages = data.get('prompt', [])
            if prompt_messages:
                # Pop first message (FIFO)
                msg = prompt_messages[0]
                time_str = msg['timestamp'][11:19] if 'timestamp' in msg else "??:??:??"
                from_name = msg.get('from', 'unknown')
                message = msg.get('message', '')
                
                # Output the message to stdout
                print(f"[{time_str}] {from_name}: {message}")
                
                # Write command for proxy to remove it
                cmd_dir = os.path.expanduser("~/.tekton/terma/commands")
                os.makedirs(cmd_dir, exist_ok=True)
                cmd_file = os.path.join(cmd_dir, f"prompt_pop_{int(time.time()*1000)}.json")
                with open(cmd_file, 'w') as f:
                    json.dump({'action': 'prompt_pop', 'timestamp': datetime.now().isoformat()}, f)
                
                return 0
            else:
                print("No prompt messages")
                return 0
        else:
            print("No messages in prompt inbox")
            return 0
            
    except Exception as e:
        print(f"Error popping prompt message: {e}")
        return 1

def terma_inbox_keep_push(message):
    """Push message to front of keep inbox."""
    try:
        # Write command for proxy to process
        cmd_dir = os.path.expanduser("~/.tekton/terma/commands")
        os.makedirs(cmd_dir, exist_ok=True)
        
        cmd_file = os.path.join(cmd_dir, f"keep_push_{int(time.time()*1000)}.json")
        command = {
            'action': 'keep_push',
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(cmd_file, 'w') as f:
            json.dump(command, f)
        
        print("[TERMA: Added to keep inbox]")
        return 0
        
    except Exception as e:
        print(f"Error pushing to keep: {e}")
        return 1

def terma_inbox_keep_write(message):
    """Write message to end of keep inbox."""
    try:
        # Write command for proxy to process
        cmd_dir = os.path.expanduser("~/.tekton/terma/commands")
        os.makedirs(cmd_dir, exist_ok=True)
        
        cmd_file = os.path.join(cmd_dir, f"keep_write_{int(time.time()*1000)}.json")
        command = {
            'action': 'keep_write',
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(cmd_file, 'w') as f:
            json.dump(command, f)
        
        print("[TERMA: Added to keep inbox]")
        return 0
        
    except Exception as e:
        print(f"Error writing to keep: {e}")
        return 1

def terma_inbox_keep_read(remove=False):
    """Read last message from keep inbox (LIFO)."""
    try:
        inbox_file = os.path.expanduser("~/.tekton/terma/.inbox_snapshot")
        
        if os.path.exists(inbox_file):
            with open(inbox_file, 'r') as f:
                data = json.load(f)
            
            keep_messages = data.get('keep', [])
            if keep_messages:
                # Read last message (LIFO)
                msg = keep_messages[-1]
                if isinstance(msg, dict):
                    time_str = msg['timestamp'][11:19] if 'timestamp' in msg else "??:??:??"
                    content = msg.get('message', '')
                else:
                    time_str = datetime.now().strftime("%H:%M:%S")
                    content = msg
                
                # Output the message to stdout
                print(content)
                
                if remove:
                    # Write command for proxy to remove it
                    cmd_dir = os.path.expanduser("~/.tekton/terma/commands")
                    os.makedirs(cmd_dir, exist_ok=True)
                    cmd_file = os.path.join(cmd_dir, f"keep_remove_{int(time.time()*1000)}.json")
                    with open(cmd_file, 'w') as f:
                        json.dump({'action': 'keep_remove_last', 'timestamp': datetime.now().isoformat()}, f)
                    print("[TERMA: Removed from keep inbox]")
                
                return 0
            else:
                print("No kept messages")
                return 0
        else:
            print("No messages in keep inbox")
            return 0
            
    except Exception as e:
        print(f"Error reading from keep: {e}")
        return 1