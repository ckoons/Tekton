#!/usr/bin/env python3
"""
AI-to-AI Communication Messenger
This module provides functions for AI models to communicate with each other.
"""

import os
import sys
import re
from typing import List, Dict, Any, Tuple
from datetime import datetime

# Import MemoryHandler for accessing memory operations
from ..memory.handler import MemoryHandler, MEMORY_AVAILABLE, run

class Messenger:
    """Handles communication between AI models."""
    
    def __init__(self, sender_persona="Echo", client_id="ollama"):
        """Initialize messenger with sender information."""
        self.sender_persona = sender_persona
        self.client_id = client_id
    
    def send_message(self, recipient: str, message: str):
        """Send a message to another AI."""
        try:
            # Import AI communication functions
            script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            sys.path.insert(0, script_dir)
            
            try:
                from ai_communication import send_message, run as ai_run
            except ImportError:
                # Fallback implementation
                async def send_message(sender, recipient, message, thread_id=None):
                    """Send a message from one AI to another."""
                    if not MEMORY_AVAILABLE:
                        return {"error": "Memory functions not available"}
                        
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Determine the appropriate tag based on sender/recipient
                    if sender.lower() == "claude" and recipient.lower() == "echo":
                        tag = "CLAUDE_TO_ECHO"
                    elif sender.lower() == "echo" and recipient.lower() == "claude":
                        tag = "ECHO_TO_CLAUDE"
                    else:
                        tag = f"{sender.upper()}_TO_{recipient.upper()}"
                    
                    # Add thread_id if provided
                    thread_part = f" [Thread: {thread_id}]" if thread_id else ""
                    
                    # Include tag information in the message itself to make search easier
                    memory_text = f"{tag}: [{timestamp}]{thread_part} {tag}:{sender}:{recipient} {message}"
                    
                    await m(memory_text)
                    return {"status": "sent", "timestamp": timestamp, "thread_id": thread_id}
            
            # Standardize recipient name
            if recipient.lower() in ["claude", "claude-3", "anthropic", "claude3"]:
                recipient = "claude"
            
            # Send the message using AI communication
            result = run(send_message(self.sender_persona, recipient, message))
            return result
        except Exception as e:
            print(f"Error sending message to {recipient}: {e}")
            return {"error": str(e)}
    
    def check_messages(self, sender: str):
        """Check for messages from a specific sender."""
        try:
            # Import AI communication functions
            script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            sys.path.insert(0, script_dir)
            
            try:
                from ai_communication import get_messages, run as ai_run
            except ImportError:
                # Simple fallback using direct memory search
                async def get_messages(tag, limit=5, thread_id=None):
                    """Simple fallback to get messages with a tag."""
                    if not MEMORY_AVAILABLE:
                        return {"error": "Memory functions not available"}
                    return await k(tag)
            
            # Standardize sender name
            if sender.lower() in ["claude", "claude-3", "anthropic", "claude3"]:
                sender = "claude"
                tag = "CLAUDE_TO_ECHO"
            else:
                tag = f"{sender.upper()}_TO_{self.sender_persona.upper()}"
            
            # Get messages from the sender
            messages = run(get_messages(tag, limit=5))
            
            # Store message summary as a memory for the model to see
            memory_handler = MemoryHandler(client_id=self.client_id)
            if messages:
                summary = f"Received {len(messages)} messages from {sender}:\n"
                for i, msg in enumerate(messages[:3]):
                    content = msg.get("content", "")
                    if content:
                        # Try to extract just the message part
                        try:
                            parts = content.split("] ")
                            if len(parts) > 1:
                                # Get everything after the tag and timestamp
                                msg_text = parts[-1]
                                # Remove the TAG:SENDER:RECIPIENT prefix if present
                                if ":" in msg_text and len(msg_text.split(" ", 1)) > 1:
                                    msg_text = msg_text.split(" ", 1)[1]
                            else:
                                msg_text = content
                        except:
                            msg_text = content
                        
                        summary += f"{i+1}. {msg_text[:100]}...\n"
                
                # Store this summary for the model to see in its next response
                memory_handler.store_memory(summary)
            else:
                memory_handler.store_memory(f"No recent messages found from {sender}.")
            
            return {"count": len(messages) if messages else 0}
        except Exception as e:
            print(f"Error checking messages from {sender}: {e}")
            return {"error": str(e)}
    
    def reply_message(self, recipient: str, message: str):
        """Reply to a message from another AI."""
        # This is similar to sending a message but might include context of previous messages
        try:
            # First check for recent messages to establish context
            check_result = self.check_messages(recipient)
            
            # Then send the reply
            send_result = self.send_message(recipient, message)
            
            # Combine results
            return {
                "checked": check_result,
                "sent": send_result
            }
        except Exception as e:
            print(f"Error replying to {recipient}: {e}")
            return {"error": str(e)}
    
    def broadcast_message(self, message: str, available_models=None):
        """Broadcast a message to all available AIs."""
        try:
            # Default recipients
            recipients = ["claude"] if not available_models else available_models
            
            # Try to get available models from system
            try:
                from ..api.models import MODEL_CAPABILITIES
                if "MODEL_CAPABILITIES" in globals():
                    recipients = list(MODEL_CAPABILITIES.keys())
                    recipients = [r for r in recipients if r != "default" and r != self.client_id]
            except:
                pass
            
            # Send message to each recipient
            results = {}
            for recipient in recipients:
                result = self.send_message(recipient, message)
                results[recipient] = result
            
            return {
                "recipients": recipients,
                "results": results
            }
        except Exception as e:
            print(f"Error broadcasting message: {e}")
            return {"error": str(e)}

def detect_communication_operations(model_output: str, messenger=None) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Detect and execute communication operations in model output.
    
    Args:
        model_output: The output text from the model
        messenger: Optional messenger to use (creates one if not provided)
        
    Returns:
        tuple: (cleaned_output, operation_results)
    """
    if messenger is None:
        messenger = Messenger()
        
    operation_results = []
    cleaned_output = model_output
    
    # Define patterns for communication operations
    comm_patterns = [
        (r"(?:SEND TO\s+(\w+):|(?:\*\*)?SEND TO\s+(\w+)(?:\*\*)?:?)\s*(.+?)(?=\n|$)", "send"),
        (r"(?:CHECK MESSAGES FROM\s+(\w+)|(?:\*\*)?CHECK MESSAGES FROM\s+(\w+)(?:\*\*)?)", "check"),
        (r"(?:REPLY TO\s+(\w+):|(?:\*\*)?REPLY TO\s+(\w+)(?:\*\*)?:?)\s*(.+?)(?=\n|$)", "reply"),
        (r"(?:BROADCAST:|(?:\*\*)?BROADCAST(?:\*\*)?:?)\s*(.+?)(?=\n|$)", "broadcast"),
    ]
    
    # Check for patterns and execute corresponding functions
    for pattern, op_type in comm_patterns:
        try:
            if op_type == "send":
                # Pattern: SEND TO recipient: message
                matches = re.finditer(pattern, model_output)
                for match in matches:
                    groups = match.groups()
                    recipient = groups[0] or groups[1]  # Either first or second group will have the recipient
                    message = groups[2] if len(groups) > 2 else ""
                    try:
                        result = messenger.send_message(recipient, message)
                        operation_results.append({
                            "type": op_type,
                            "input": f"to {recipient}: {message}",
                            "result": result
                        })
                        # Remove the operation from the output
                        cleaned_output = cleaned_output.replace(match.group(0), "", 1)
                    except Exception as e:
                        print(f"Error executing communication operation: {e}")
            
            elif op_type == "reply":
                # Pattern: REPLY TO recipient: message
                matches = re.finditer(pattern, model_output)
                for match in matches:
                    groups = match.groups()
                    recipient = groups[0] or groups[1]
                    message = groups[2] if len(groups) > 2 else ""
                    try:
                        result = messenger.reply_message(recipient, message)
                        operation_results.append({
                            "type": op_type,
                            "input": f"to {recipient}: {message}",
                            "result": result
                        })
                        # Remove the operation from the output
                        cleaned_output = cleaned_output.replace(match.group(0), "", 1)
                    except Exception as e:
                        print(f"Error executing communication operation: {e}")
            
            elif op_type == "broadcast":
                # Pattern: BROADCAST: message
                matches = re.findall(pattern, model_output)
                for match in matches:
                    try:
                        result = messenger.broadcast_message(match)
                        operation_results.append({
                            "type": op_type,
                            "input": match,
                            "result": result
                        })
                        # Remove the operation from the output
                        cleaned_output = re.sub(pattern, "", cleaned_output, count=1)
                    except Exception as e:
                        print(f"Error executing communication operation: {e}")
        
            elif op_type == "check":
                # Pattern: CHECK MESSAGES FROM recipient
                matches = re.finditer(pattern, model_output)
                for match in matches:
                    groups = match.groups()
                    recipient = groups[0] or groups[1]
                    try:
                        result = messenger.check_messages(recipient)
                        operation_results.append({
                            "type": op_type,
                            "input": f"from {recipient}",
                            "result": result
                        })
                        # Remove the operation from the output
                        cleaned_output = cleaned_output.replace(match.group(0), "", 1)
                    except Exception as e:
                        print(f"Error executing communication operation: {e}")
                
        except Exception as e:
            print(f"Error processing pattern {pattern}: {e}")
    
    # Clean up extra newlines caused by removal
    cleaned_output = re.sub(r'\n{3,}', '\n\n', cleaned_output)
    return cleaned_output.strip(), operation_results


def format_communication_operations_report(operations: List[Dict[str, Any]]) -> str:
    """
    Format communication operations into a readable report.
    
    Args:
        operations: List of communication operations and their results
        
    Returns:
        String with formatted report
    """
    if not operations:
        return ""
        
    report = "\n[Communication system: Detected communication operations]\n"
    
    for op in operations:
        op_type = op.get("type", "")
        op_input = op.get("input", "")
        
        if op_type == "send":
            report += f"[Communication system: Sent message {op_input}]\n"
        elif op_type == "check":
            count = op.get("result", {}).get("count", 0)
            report += f"[Communication system: Checked messages {op_input} (found {count})]\n"
        elif op_type == "reply":
            report += f"[Communication system: Replied {op_input}]\n"
        elif op_type == "broadcast":
            recipients = op.get("result", {}).get("recipients", [])
            count = len(recipients)
            report += f"[Communication system: Broadcasted message to {count} recipients]\n"
    
    return report