#!/usr/bin/env python3
"""
Claude Dialog Mode - Background message checking for Claude

This module provides the DIALOG functionality for Claude, enabling continuous
communication with other AI models.
"""

import os
import sys
import time
import threading
import asyncio
from typing import Dict, List, Optional, Any, Callable

# Import the communication functions
try:
    from engram.cli.comm_quickmem import lc, gm, sm, run, cs
except ImportError:
    print("\033[93m⚠️ Claude communication functions not available\033[0m")
    sys.exit(1)

class ClaudeDialog:
    """
    Handles the dialog mode for Claude, enabling continuous communication
    with other AI models.
    """
    
    def __init__(self, client_id: str = "claude"):
        """Initialize the dialog handler"""
        self.client_id = client_id
        self.dialog_mode = False
        self.dialog_target = None
        self.dialog_type = None
        self.last_check_time = 0
        self.message_handler = None
        self.stop_event = threading.Event()
        self.dialog_thread = None
        self.message_history = {}
        self.seen_message_ids = set()
        
    def start_dialog(self, target: str, message_handler: Callable = None) -> Dict:
        """
        Start dialog mode with a specific target or all models (*)
        
        Args:
            target: The client ID to dialog with, or '*' for all
            message_handler: Optional callback to handle incoming messages
            
        Returns:
            Dict with dialog mode status
        """
        # Set dialog mode parameters
        self.dialog_mode = True
        self.dialog_target = target
        self.dialog_type = "all" if target == "*" else "specific"
        self.message_handler = message_handler
        
        # Reset the stop event
        self.stop_event.clear()
        
        # Check if thread is already running
        if self.dialog_thread and self.dialog_thread.is_alive():
            return {
                "status": "already_active",
                "dialog_with": self.dialog_target,
                "type": self.dialog_type,
                "message": f"Dialog mode already active with {self.dialog_target}"
            }
        
        # Start the background thread
        self.dialog_thread = threading.Thread(
            target=self._dialog_loop,
            daemon=True  # Make it a daemon thread so it doesn't block program exit
        )
        self.dialog_thread.start()
        
        # Return status
        if self.dialog_type == "all":
            dialog_message = "Entering dialog mode with ALL available AI models"
        else:
            dialog_message = f"Entering dialog mode with {self.dialog_target}"
            
        return {
            "status": "active",
            "dialog_with": self.dialog_target,
            "type": self.dialog_type,
            "message": dialog_message
        }
    
    def stop_dialog(self) -> Dict:
        """Stop the dialog mode"""
        if not self.dialog_mode:
            return {
                "status": "not_active",
                "message": "Dialog mode is not active"
            }
        
        # Signal the thread to stop
        self.stop_event.set()
        
        # Wait for thread to finish (with timeout)
        if self.dialog_thread and self.dialog_thread.is_alive():
            self.dialog_thread.join(timeout=2)
        
        # Reset dialog mode
        self.dialog_mode = False
        old_target = self.dialog_target
        self.dialog_target = None
        self.dialog_type = None
        
        return {
            "status": "stopped",
            "previous_dialog": old_target,
            "message": f"Dialog mode with {old_target} has been stopped"
        }
    
    def _dialog_loop(self):
        """Background thread that checks for messages"""
        while not self.stop_event.is_set():
            try:
                # Only check every 2 seconds to avoid API spam
                current_time = time.time()
                if current_time - self.last_check_time < 2:
                    time.sleep(0.5)  # Sleep for a bit
                    continue
                
                self.last_check_time = current_time
                
                # Check messages based on dialog type
                if self.dialog_type == "all":
                    self._check_all_models()
                else:
                    self._check_specific_target()
                    
                # Brief sleep to prevent high CPU usage
                time.sleep(0.5)
                
            except Exception as e:
                print(f"\n\033[91m[Dialog] Error in dialog loop: {e}\033[0m")
                time.sleep(2)  # Sleep longer on error
    
    def _check_all_models(self):
        """Check for messages from all models"""
        try:
            # Get all connections
            connections = run(lc())
            new_messages_found = False
            
            for conn in connections:
                conn_id = conn.get("id", "")
                if conn_id and conn_id != self.client_id:
                    # Skip connections that aren't active
                    status = conn.get("status", "")
                    if status != "online":
                        continue
                        
                    self._check_messages_from(conn_id)
        except Exception as e:
            print(f"\n\033[91m[Dialog] Error checking all models: {e}\033[0m")
    
    def _check_specific_target(self):
        """Check for messages from specific target"""
        if self.dialog_target:
            self._check_messages_from(self.dialog_target)
    
    def _check_messages_from(self, sender_id: str):
        """Check for messages from a specific sender"""
        try:
            # Get messages from the sender
            messages = run(gm(sender_id, 5, False))
            
            # Process messages if we have any
            if messages and not isinstance(messages, dict) and len(messages) > 0:
                # Process in reverse order (oldest first) for conversation flow
                for msg in reversed(messages):
                    msg_id = msg.get("id", "")
                    
                    # Skip if we've already seen this message
                    if msg_id in self.seen_message_ids:
                        continue
                        
                    # Add to seen messages
                    self.seen_message_ids.add(msg_id)
                    
                    # Extract message content
                    content = msg.get("message", "")
                    timestamp = msg.get("timestamp", 0)
                    
                    # Display the message
                    formatted_time = time.strftime("%H:%M:%S", time.localtime(timestamp))
                    print(f"\n\033[94m[Dialog {formatted_time}] From {sender_id}:\033[0m {content}")
                    
                    # Call message handler if provided
                    if self.message_handler:
                        self.message_handler(sender_id, content, msg)
        except Exception as e:
            print(f"\n\033[91m[Dialog] Error checking messages from {sender_id}: {e}\033[0m")

# Create global dialog instance
dialog_handler = None

def init_dialog(client_id: str = "claude", message_handler: Callable = None):
    """Initialize the dialog handler"""
    global dialog_handler
    dialog_handler = ClaudeDialog(client_id)
    return dialog_handler

def start_dialog(target: str = "*", message_handler: Callable = None) -> Dict:
    """Start dialog mode with a target"""
    global dialog_handler
    if not dialog_handler:
        dialog_handler = ClaudeDialog()
    return dialog_handler.start_dialog(target, message_handler)

def stop_dialog() -> Dict:
    """Stop dialog mode"""
    global dialog_handler
    if not dialog_handler:
        return {"status": "not_initialized", "message": "Dialog handler not initialized"}
    return dialog_handler.stop_dialog()

def is_dialog_active() -> bool:
    """Check if dialog mode is active"""
    global dialog_handler
    if not dialog_handler:
        return False
    return dialog_handler.dialog_mode

# Example usage
if __name__ == "__main__":
    # Handle message with callback
    def handle_message(sender, content, msg):
        print(f"Handling message from {sender}: {content[:30]}...")
        
    # Initialize dialog
    dialog = init_dialog("claude-test", handle_message)
    
    # Start dialog with all models
    result = start_dialog("*")
    print(f"Dialog started: {result}")
    
    # Keep running for testing
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping dialog...")
        stop_dialog()