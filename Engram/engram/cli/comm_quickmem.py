#!/usr/bin/env python3
"""
Communication QuickMem Module - Quick shortcuts for Claude-to-Claude communication

This module provides single-letter shortcuts for Claude-to-Claude communication functions
to make it easier to use communication functions in the interactive Claude CLI.
"""

import os
import asyncio
import json
from typing import Dict, List, Optional, Any, Union

# Configure client ID
client_id = os.environ.get("ENGRAM_CLIENT_ID", "claude")

# Import core components
try:
    from engram.core.claude_comm import ClaudeCommunicator

    # Create instance with the configured client ID
    communicator = ClaudeCommunicator(client_id=client_id)
except Exception as e:
    print(f"\033[93m⚠️ Failed to initialize Claude communication: {e}\033[0m")
    communicator = None

# ----- ULTRA-SHORT COMMANDS -----
# Use two letters for maximum UI efficiency

# Import the dialog module (but make it optional)
try:
    from engram.cli.claude_dialog import start_dialog, stop_dialog, is_dialog_active
    DIALOG_AVAILABLE = True
except ImportError:
    DIALOG_AVAILABLE = False

# sm: Send Message - Send a message to another Claude
async def sm(recipient_id: str, message: str, metadata: Dict = None) -> Dict:
    """Send a message to another Claude instance."""
    if communicator is None:
        return {"error": "Claude communication not available"}
    
    try:
        result = await communicator.send_message(recipient_id, message, metadata)
        return result
    except Exception as e:
        print(f"\033[91m❌ Error sending message: {e}\033[0m")
        return {"error": str(e)}

# gm: Get Messages - Get messages from a specific Claude
async def gm(sender_id: str = None, limit: int = 10, include_read: bool = False) -> List[Dict]:
    """Get messages from a specific Claude or all unread messages."""
    if communicator is None:
        return [{"error": "Claude communication not available"}]
    
    try:
        if sender_id:
            result = await communicator.get_messages_from(sender_id, limit, include_read)
        else:
            result = await communicator.get_unread_messages(limit)
        return result
    except Exception as e:
        print(f"\033[91m❌ Error getting messages: {e}\033[0m")
        return [{"error": str(e)}]

# ho: Hail Other - Send a hail (ping) to another Claude
async def ho(recipient_id: str, note: str = None) -> Dict:
    """Send a hail (ping) to another Claude instance."""
    if communicator is None:
        return {"error": "Claude communication not available"}
    
    try:
        metadata = {"type": "hail", "note": note} if note else {"type": "hail"}
        result = await communicator.send_message(
            recipient_id, "Hail from Claude instance", metadata
        )
        return result
    except Exception as e:
        print(f"\033[91m❌ Error sending hail: {e}\033[0m")
        return {"error": str(e)}

# cc: Chat Conversation - Create or continue a conversation
async def cc(recipient_id: str, message: str) -> Dict:
    """Create or continue a chat conversation with another Claude."""
    if communicator is None:
        return {"error": "Claude communication not available"}
    
    try:
        metadata = {"type": "conversation", "conversation_id": f"conv-{recipient_id}-{client_id}"}
        result = await communicator.send_message(recipient_id, message, metadata)
        return result
    except Exception as e:
        print(f"\033[91m❌ Error in conversation: {e}\033[0m")
        return {"error": str(e)}

# lc: List Connections - List connected Claudes
async def lc() -> List[Dict]:
    """List all connected Claude instances."""
    if communicator is None:
        return [{"error": "Claude communication not available"}]
    
    try:
        result = await communicator.list_connections()
        return result
    except Exception as e:
        print(f"\033[91m❌ Error listing connections: {e}\033[0m")
        return [{"error": str(e)}]

# sc: Send Content - Send structured content
async def sc(recipient_id: str, content_type: str, content: Any) -> Dict:
    """Send structured content to another Claude instance."""
    if communicator is None:
        return {"error": "Claude communication not available"}
    
    try:
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except json.JSONDecodeError:
                # Keep as string if not valid JSON
                pass
                
        metadata = {"type": "structured", "content_type": content_type}
        message = f"Structured content of type: {content_type}"
        
        if isinstance(content, dict) or isinstance(content, list):
            message_with_content = {"message": message, "content": content}
            result = await communicator.send_message(
                recipient_id, json.dumps(message_with_content), metadata
            )
        else:
            result = await communicator.send_message(
                recipient_id, message, metadata, {"content": content}
            )
            
        return result
    except Exception as e:
        print(f"\033[91m❌ Error sending structured content: {e}\033[0m")
        return {"error": str(e)}

# gc: Get Conversation - Get messages from a conversation
async def gc(conversation_id: str, limit: int = 20) -> List[Dict]:
    """Get messages from a specific conversation."""
    if communicator is None:
        return [{"error": "Claude communication not available"}]
    
    try:
        result = await communicator.get_conversation(conversation_id, limit)
        return result
    except Exception as e:
        print(f"\033[91m❌ Error getting conversation: {e}\033[0m")
        return [{"error": str(e)}]

# cs: Communication Status - Check communication status
def cs() -> Dict:
    """Check the status of Claude-to-Claude communication."""
    if communicator is None:
        print(f"\033[91m✗ Claude communication is not available\033[0m")
        return {"status": "unavailable", "client_id": client_id}
    
    try:
        status = communicator.status()
        if status.get("status") == "online":
            print(f"\033[92m✓ Claude communication is online (Client: {client_id})\033[0m")
        else:
            print(f"\033[91m✗ Claude communication is offline (Client: {client_id})\033[0m")
        return status
    except Exception as e:
        print(f"\033[91m❌ Error checking communication status: {e}\033[0m")
        return {"status": "error", "error": str(e), "client_id": client_id}

# wi: Who am I - Get current Claude identity
def wi() -> Dict:
    """Get the identity of the current Claude instance."""
    if communicator is None:
        print(f"\033[93m⚠️ Claude communication not available, using client ID only\033[0m")
        return {"id": client_id, "name": client_id}
    
    try:
        identity = communicator.get_identity()
        print(f"\033[92mYou are Claude instance: {identity.get('name', client_id)} ({identity.get('id', 'unknown')})\033[0m")
        return identity
    except Exception as e:
        print(f"\033[91m❌ Error getting identity: {e}\033[0m")
        return {"id": client_id, "name": client_id, "error": str(e)}

# dl: Dialog - Enter continuous dialog mode with another Claude
def dl(target_id: str = "*"):
    """Enter continuous dialog mode with another Claude or all Claudes."""
    if not DIALOG_AVAILABLE:
        print(f"\033[91m❌ Dialog mode not available. Missing claude_dialog.py module.\033[0m")
        return {"error": "Dialog mode not available"}
    
    try:
        # Define a message handler to auto-respond to questions
        async def message_handler(sender, content, msg):
            # Auto-respond to questions
            if '?' in content:
                print(f"\033[94m[Dialog] Auto-responding to question from {sender}...\033[0m")
                response = f"Thank you for your question. I'll analyze this and get back to you."
                await sm(sender, response)
        
        # Start dialog mode
        result = start_dialog(target_id, message_handler)
        if result["status"] == "active":
            print(f"\033[92m✓ {result['message']}\033[0m")
            print(f"\033[93mType '/dialog_off' to exit dialog mode\033[0m")
        return result
    except Exception as e:
        print(f"\033[91m❌ Error starting dialog: {e}\033[0m")
        return {"error": str(e)}

# do: Dialog Off - Exit dialog mode
def do():
    """Exit dialog mode."""
    if not DIALOG_AVAILABLE:
        print(f"\033[91m❌ Dialog mode not available. Missing claude_dialog.py module.\033[0m")
        return {"error": "Dialog mode not available"}
    
    try:
        result = stop_dialog()
        if result["status"] == "stopped":
            print(f"\033[92m✓ {result['message']}\033[0m")
        return result
    except Exception as e:
        print(f"\033[91m❌ Error stopping dialog: {e}\033[0m")
        return {"error": str(e)}

# di: Dialog Info - Check dialog mode status
def di():
    """Check dialog mode status."""
    if not DIALOG_AVAILABLE:
        print(f"\033[91m❌ Dialog mode not available. Missing claude_dialog.py module.\033[0m")
        return {"error": "Dialog mode not available"}
    
    try:
        active = is_dialog_active()
        if active:
            print(f"\033[92m✓ Dialog mode is active\033[0m")
            return {"status": "active"}
        else:
            print(f"\033[93m✗ Dialog mode is not active\033[0m")
            return {"status": "inactive"}
    except Exception as e:
        print(f"\033[91m❌ Error checking dialog status: {e}\033[0m")
        return {"error": str(e)}

# ----- LONGER ALIASES FOR BETTER READABILITY -----

# These provide more descriptive names for the same functions
send_message = sm
get_messages = gm
hail_other = ho
chat_conversation = cc
list_connections = lc
send_content = sc
get_conversation = gc
communication_status = cs
who_am_i = wi
dialog = dl
dialog_off = do
dialog_info = di

# Add run function for compatibility with sync environments
def run(coro):
    """Run a coroutine in the current event loop or create a new one."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)