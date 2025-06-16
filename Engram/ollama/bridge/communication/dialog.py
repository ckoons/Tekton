#!/usr/bin/env python3
"""
Dialog Mode for AI-to-AI Communication
This module provides functionality for entering dialog mode with other AI models.
"""

import re
import time
import select
import sys
from typing import Dict, Any, List, Optional, Tuple

from ..memory.handler import MemoryHandler, MEMORY_AVAILABLE
from ..api.client import call_ollama_api
from .messenger import Messenger

class DialogManager:
    """Manages dialog mode with other AI models."""
    
    def __init__(self, client_id="ollama"):
        """Initialize dialog manager."""
        self.client_id = client_id
        self.dialog_mode = False
        self.dialog_target = None
        self.dialog_type = None
        self.last_check_time = 0
        self.messenger = Messenger(client_id=client_id)
    
    def enter_dialog_mode(self, recipient: str) -> Dict[str, Any]:
        """
        Handle entering dialog mode with a specific AI or with all AIs (*).
        
        Args:
            recipient: The client ID to dialog with, or '*' for all
        
        Returns:
            Dict with dialog mode status
        """
        try:
            dialog_target = recipient
            
            # Check if using wildcard
            if dialog_target == "*":
                dialog_message = "Entering dialog mode with ALL available AI models"
                dialog_type = "all"
            else:
                dialog_message = f"Entering dialog mode with {dialog_target}"
                dialog_type = "specific"
            
            # Store the dialog target for the main loop to use
            self.dialog_mode = True
            self.dialog_target = dialog_target
            self.dialog_type = dialog_type
            
            # Return message to display to user
            return {
                "status": "active",
                "dialog_with": dialog_target,
                "type": dialog_type,
                "message": dialog_message
            }
            
        except Exception as e:
            print(f"Error entering dialog mode: {e}")
            return {"error": str(e)}
    
    def exit_dialog_mode(self) -> Dict[str, Any]:
        """Exit dialog mode."""
        self.dialog_mode = False
        self.dialog_target = None
        self.dialog_type = None
        return {
            "status": "inactive",
            "message": "Dialog mode deactivated"
        }
    
    def check_for_messages(self, model: str, system: str, chat_history: List[Dict[str, str]], 
                          temperature: float, top_p: float, max_tokens: int) -> Optional[Dict[str, Any]]:
        """
        Check for messages in dialog mode and optionally auto-reply.
        
        Args:
            model: The model to use for auto-replies
            system: The system prompt
            chat_history: Current chat history
            temperature: Temperature for generation
            top_p: Top-p sampling parameter
            max_tokens: Maximum tokens to generate
            
        Returns:
            Optional dict with new messages and auto-replies
        """
        if not self.dialog_mode:
            return None
            
        current_time = time.time()
        # Only check messages every 2 seconds to avoid spamming
        if current_time - self.last_check_time < 2:
            return None
            
        self.last_check_time = current_time
        
        # Results structure to return
        results = {
            "new_messages": False,
            "auto_replies": [],
            "messages": []
        }
        
        # Check for new messages based on dialog mode type
        if self.dialog_type == "all":
            print("\n[Dialog] Checking for messages from all models...")
            # Try to list all connections and check each one
            try:
                if not MEMORY_AVAILABLE:
                    return None
                    
                from engram.cli.comm_quickmem import lc, gm, run
                connections = run(lc())
                
                for conn in connections:
                    conn_id = conn.get("id", "")
                    if conn_id and conn_id != self.client_id:
                        messages = run(gm(conn_id, 3, False))
                        if messages and not isinstance(messages, dict):
                            results["new_messages"] = True
                            
                            for msg in messages:
                                content = msg.get('message', '')
                                print(f"\n[Dialog] From {conn_id}: {content}")
                                results["messages"].append({
                                    "from": conn_id,
                                    "content": content
                                })
                                
                                # Auto-reply if the message contains a question
                                if '?' in content:
                                    # Process the message through Ollama
                                    chat_history.append({"role": "user", "content": f"Message from {conn_id}: {content}"})
                                    # Call Ollama API
                                    response = call_ollama_api(
                                        model=model,
                                        messages=chat_history,
                                        system=system,
                                        temperature=temperature,
                                        top_p=top_p,
                                        max_tokens=max_tokens
                                    )
                                    
                                    if "message" in response:
                                        ai_reply = response["message"]["content"]
                                        print(f"\n[Dialog] Auto-replying to {conn_id}...")
                                        self.messenger.reply_message(conn_id, ai_reply)
                                        chat_history.append({"role": "assistant", "content": ai_reply})
                                        results["auto_replies"].append({
                                            "to": conn_id,
                                            "content": ai_reply
                                        })
                
                if not results["new_messages"]:
                    # Don't spam "no messages" - only show occasionally
                    if int(current_time) % 10 == 0:  # Show every ~10 seconds
                        print("\n[Dialog] No new messages")
            except Exception as e:
                print(f"\n[Dialog] Error checking messages: {e}")
        else:
            # Check from specific target
            target = self.dialog_target
            if target:
                try:
                    if not MEMORY_AVAILABLE:
                        return None
                        
                    from engram.cli.comm_quickmem import gm, run
                    messages = run(gm(target, 3, False))
                    if messages and not isinstance(messages, dict):
                        results["new_messages"] = True
                        
                        for msg in messages:
                            content = msg.get('message', '')
                            print(f"\n[Dialog] From {target}: {content}")
                            results["messages"].append({
                                "from": target,
                                "content": content
                            })
                            
                            # Auto-reply if the message contains a question
                            if '?' in content:
                                # Process the message through Ollama
                                chat_history.append({"role": "user", "content": f"Message from {target}: {content}"})
                                # Call Ollama API
                                response = call_ollama_api(
                                    model=model,
                                    messages=chat_history,
                                    system=system,
                                    temperature=temperature,
                                    top_p=top_p,
                                    max_tokens=max_tokens
                                )
                                
                                if "message" in response:
                                    ai_reply = response["message"]["content"]
                                    print(f"\n[Dialog] Auto-replying to {target}...")
                                    self.messenger.reply_message(target, ai_reply)
                                    chat_history.append({"role": "assistant", "content": ai_reply})
                                    results["auto_replies"].append({
                                        "to": target,
                                        "content": ai_reply
                                    })
                    else:
                        # Don't spam "no messages" - only show occasionally
                        if int(current_time) % 10 == 0:  # Show every ~10 seconds
                            print(f"\n[Dialog] No new messages from {target}")
                except Exception as e:
                    print(f"\n[Dialog] Error checking messages from {target}: {e}")
        
        return results
    
    def get_user_input_with_timeout(self, timeout=1) -> Optional[str]:
        """
        Get user input with a timeout to support dialog mode.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            User input string or None if timeout
        """
        if not self.dialog_mode:
            # In normal mode, just wait for input without timeout
            return input("\nYou: ")
            
        # In dialog mode, use select to implement timeout
        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        if ready:
            return input("\nYou: ")
        
        # If timeout, return None
        return None

def detect_dialog_operations(model_output: str, dialog_manager=None) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Detect dialog mode operations in model output.
    
    Args:
        model_output: The output text from the model
        dialog_manager: Optional dialog manager to use (creates one if not provided)
        
    Returns:
        tuple: (cleaned_output, operation_results)
    """
    if dialog_manager is None:
        dialog_manager = DialogManager()
        
    operation_results = []
    cleaned_output = model_output
    
    # Dialog pattern
    dialog_pattern = r"(?:DIALOG\s+(\w+|\*)|(?:\*\*)?DIALOG\s+(\w+|\*)(?:\*\*)?)"
    
    # Check for dialog operations
    matches = re.finditer(dialog_pattern, model_output)
    for match in matches:
        groups = match.groups()
        target = groups[0] or groups[1]  # Either first or second group will have the target
        try:
            result = dialog_manager.enter_dialog_mode(target)
            operation_results.append({
                "type": "dialog",
                "input": f"with {target}",
                "result": result
            })
            # Remove the operation from the output
            cleaned_output = cleaned_output.replace(match.group(0), "", 1)
        except Exception as e:
            print(f"Error executing dialog operation: {e}")
    
    # Clean up extra newlines caused by removal
    cleaned_output = re.sub(r'\n{3,}', '\n\n', cleaned_output)
    return cleaned_output.strip(), operation_results