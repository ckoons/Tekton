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
from pathlib import Path

# Add parent to path for shared imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from shared.urls import tekton_url
from shared.env import TektonEnviron

# Try to import landmarks if available
try:
    from landmarks import architecture_decision, integration_point, api_contract, state_checkpoint
except ImportError:
    # Landmarks not available, create no-op decorators
    def architecture_decision(name, description, rationale=""):
        def decorator(func):
            return func
        return decorator
    
    def integration_point(name, description, rationale=""):
        def decorator(func):
            return func
        return decorator
    
    def api_contract(name, description, rationale=""):
        def decorator(func):
            return func
        return decorator
    
    def state_checkpoint(name, description, rationale=""):
        def decorator(func):
            return func
        return decorator

# Build endpoint using tekton_url
TERMA_ENDPOINT = tekton_url('terma', '')

@architecture_decision(
    title="Inter-Terminal Messaging",
    description="Enables human-to-human and AI-to-human communication via terminal inboxes",
    rationale="Terminal inboxes provide asynchronous communication between distributed team members",
    alternatives_considered=["Slack integration", "Email", "Direct terminal interrupts"],
    impacts=["collaboration", "workflow", "attention management"],
    decided_by="Casey",
    decision_date="2025-01-17"
)
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
        print("\nNote: Inbox commands moved to 'aish inbox' - see 'aish inbox help'")
        print("\nDocumentation:")
        tekton_root = TektonEnviron.get('TEKTON_ROOT', '/Users/cskoons/projects/github/Tekton')
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
        print("Inbox commands have moved to 'aish inbox'")
        print("See 'aish inbox help' for complete documentation")
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
    print("  whoami               - Show current terminal info")
    print("  <name> 'message'     - Send to specific terminal")
    print("  @<purpose> 'message' - Send to terminals by purpose")
    print("  broadcast 'message'  - Send to all other terminals")
    print("  * 'message'          - Send to all including self")
    print("  training-for-ais     - Get AI training docs location")
    print("  error-report 'msg'   - Report an error or issue")
    print("\nNote: Inbox commands moved to 'aish inbox' - see 'aish inbox help'")
    print("\nExamples:")
    print("  aish terma list")
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
        my_id = TektonEnviron.get('TERMA_SESSION_ID', '')
        
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
        print("Is Terma running?")
        return 1

def terma_whoami():
    """Show current terminal information."""
    try:
        name = TektonEnviron.get('TERMA_TERMINAL_NAME', 'unnamed')
        session_id = TektonEnviron.get('TERMA_SESSION_ID', 'unknown')
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
    training_dir = TektonEnviron.get('TEKTON_AI_TRAINING')
    
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
        tekton_root = TektonEnviron.get('TEKTON_ROOT', '/Users/cskoons/projects/github/Tekton')
        log_dir = os.path.join(tekton_root, ".tekton", "terma", "error_reports")
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"error_{timestamp}.json")
        
        error_data = {
            "terma_id": TektonEnviron.get('TERMA_SESSION_ID', 'unknown'),
            "terminal_name": TektonEnviron.get('TERMA_TERMINAL_NAME', 'unnamed'),
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
        sender_id = TektonEnviron.get('TERMA_SESSION_ID', 'unknown')
        sender_name = TektonEnviron.get('TERMA_TERMINAL_NAME', 'unnamed')
        
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

# Landmark: Message Delivery - integration point for forwarding to new unified inbox system
@integration_point(
    title="Terma to Inbox Integration",
    description="Bridges legacy terma forwarding to unified inbox system",
    target_component="inbox_storage_system",
    protocol="function_call",
    data_flow="terma forwarding → deliver_message_to_inbox → inbox.store_message",
    integration_date="2025-01-25"
)
def deliver_message_to_inbox(ci_name, message, sender="forwarding", purpose="general"):
    """Deliver a message to a CI's inbox using the new unified system."""
    try:
        # Import the inbox system
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent))
        from inbox import store_message, create_message
        
        # Create message with proper metadata
        message_data = create_message(sender, ci_name, message, purpose)
        
        # Store in 'new' inbox by default
        message_id = store_message(ci_name, 'new', message_data)
        return True
        
    except Exception as e:
        print(f"Failed to deliver message to {ci_name}: {e}")
        return False
