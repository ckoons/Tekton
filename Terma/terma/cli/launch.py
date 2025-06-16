"""Terminal launcher for standalone terminals"""

import argparse
import sys
import os
import webbrowser
import subprocess
import json
import uuid
import requests
import tempfile
import signal
import time
from pathlib import Path
from typing import Optional, Dict, Any

from ..utils.logging import setup_logging
from ..utils.config import Config

logger = setup_logging()
config = Config()

def launch_tmux_terminal(session_id: str, shell_command: Optional[str] = None, 
                         server_url: str = "http://localhost:8765"):
    """Launch a terminal session in tmux
    
    Args:
        session_id: Session ID to connect to
        shell_command: Optional shell command to run
        server_url: URL of the Terma server
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Check if tmux is installed
    try:
        subprocess.run(["which", "tmux"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        logger.error("tmux is not installed")
        return False
        
    try:
        # Create a script to connect to the terminal
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.sh') as f:
            script_path = f.name
            
            f.write(f"""#!/bin/bash
# Terma terminal connector script
echo "Connecting to Terma terminal session {session_id}"
echo "Press Ctrl+B then D to detach without closing the session"
echo "Press Ctrl+C to exit and close the session"

# Function to handle exit
function cleanup() {{
    echo "Closing session..."
    curl -X DELETE "{server_url}/api/sessions/{session_id}" 2>/dev/null || true
    exit 0
}}

# Register signal handlers
trap cleanup SIGINT SIGTERM

# Helper function to read from the terminal
function read_terminal() {{
    curl -s "{server_url}/api/sessions/{session_id}/read"
}}

# Helper function to write to the terminal
function write_terminal() {{
    curl -s -X POST -H "Content-Type: application/json" \\
        -d "{{\\"data\\":\\"\$1\\"}}" \\
        "{server_url}/api/sessions/{session_id}/write" >/dev/null
}}

# Main loop
while read -r input; do
    # Send input to terminal
    write_terminal "$input\\n"
    
    # Read output
    response=$(read_terminal)
    data=$(echo "$response" | grep -o '"data":"[^"]*"' | sed 's/"data":"\\(.*\\)"/\\1/')
    echo -e "$data"
done
""")
            
        # Make the script executable
        os.chmod(script_path, 0o755)
        
        # Launch the script in tmux
        tmux_command = [
            "tmux", "new-session", "-s", f"terma-{session_id}", 
            "-n", "Terma Terminal", script_path
        ]
        
        process = subprocess.Popen(tmux_command)
        logger.info(f"Launched tmux session for {session_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to launch tmux terminal: {e}")
        return False

def launch_screen_terminal(session_id: str, shell_command: Optional[str] = None,
                          server_url: str = "http://localhost:8765"):
    """Launch a terminal session in screen
    
    Args:
        session_id: Session ID to connect to
        shell_command: Optional shell command to run
        server_url: URL of the Terma server
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Check if screen is installed
    try:
        subprocess.run(["which", "screen"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        logger.error("screen is not installed")
        return False
        
    try:
        # Create a script to connect to the terminal (similar to tmux)
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.sh') as f:
            script_path = f.name
            
            # Similar script as for tmux but with screen-specific instructions
            f.write(f"""#!/bin/bash
# Terma terminal connector script
echo "Connecting to Terma terminal session {session_id}"
echo "Press Ctrl+A then D to detach without closing the session"
echo "Press Ctrl+C to exit and close the session"

# Function to handle exit
function cleanup() {{
    echo "Closing session..."
    curl -X DELETE "{server_url}/api/sessions/{session_id}" 2>/dev/null || true
    exit 0
}}

# Register signal handlers
trap cleanup SIGINT SIGTERM

# Helper function to read from the terminal
function read_terminal() {{
    curl -s "{server_url}/api/sessions/{session_id}/read"
}}

# Helper function to write to the terminal
function write_terminal() {{
    curl -s -X POST -H "Content-Type: application/json" \\
        -d "{{\\"data\\":\\"\$1\\"}}" \\
        "{server_url}/api/sessions/{session_id}/write" >/dev/null
}}

# Main loop
while read -r input; do
    # Send input to terminal
    write_terminal "$input\\n"
    
    # Read output
    response=$(read_terminal)
    data=$(echo "$response" | grep -o '"data":"[^"]*"' | sed 's/"data":"\\(.*\\)"/\\1/')
    echo -e "$data"
done
""")
            
        # Make the script executable
        os.chmod(script_path, 0o755)
        
        # Launch the script in screen
        screen_command = [
            "screen", "-S", f"terma-{session_id}", script_path
        ]
        
        process = subprocess.Popen(screen_command)
        logger.info(f"Launched screen session for {session_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to launch screen terminal: {e}")
        return False

def launch_native_terminal(session_id: str, shell_command: Optional[str] = None,
                          server_url: str = "http://localhost:8765"):
    """Launch a terminal session in the native terminal
    
    Args:
        session_id: Session ID to connect to
        shell_command: Optional shell command to run
        server_url: URL of the Terma server
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create a script to connect to the terminal
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.sh') as f:
            script_path = f.name
            
            f.write(f"""#!/bin/bash
# Terma terminal connector script
echo "Connecting to Terma terminal session {session_id}"
echo "Press Ctrl+C to exit and close the session"

# Function to handle exit
function cleanup() {{
    echo "Closing session..."
    curl -X DELETE "{server_url}/api/sessions/{session_id}" 2>/dev/null || true
    exit 0
}}

# Register signal handlers
trap cleanup SIGINT SIGTERM

# Helper function to read from the terminal
function read_terminal() {{
    curl -s "{server_url}/api/sessions/{session_id}/read"
}}

# Helper function to write to the terminal
function write_terminal() {{
    curl -s -X POST -H "Content-Type: application/json" \\
        -d "{{\\"data\\":\\"\$1\\"}}" \\
        "{server_url}/api/sessions/{session_id}/write" >/dev/null
}}

# Main loop
while read -r input; do
    # Send input to terminal
    write_terminal "$input\\n"
    
    # Read output
    response=$(read_terminal)
    data=$(echo "$response" | grep -o '"data":"[^"]*"' | sed 's/"data":"\\(.*\\)"/\\1/')
    echo -e "$data"
done
""")
            
        # Make the script executable
        os.chmod(script_path, 0o755)
        
        # Determine the terminal command based on platform
        terminal_command = []
        if sys.platform == "darwin":
            # macOS
            terminal_command = ["open", "-a", "Terminal", script_path]
        elif sys.platform == "linux":
            # Try common Linux terminals
            for term in ["gnome-terminal", "konsole", "xterm"]:
                try:
                    subprocess.run(["which", term], check=True, capture_output=True)
                    if term == "gnome-terminal":
                        terminal_command = [term, "--", script_path]
                    else:
                        terminal_command = [term, "-e", script_path]
                    break
                except subprocess.CalledProcessError:
                    continue
        elif sys.platform == "win32":
            # Windows
            terminal_command = ["start", "cmd", "/c", script_path]
            
        if not terminal_command:
            logger.error("Could not determine terminal command for this platform")
            return False
            
        # Launch the script in the terminal
        process = subprocess.Popen(terminal_command)
        logger.info(f"Launched native terminal for {session_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to launch native terminal: {e}")
        return False

def launch_browser_terminal(session_id: str = None, server_url: str = "http://localhost:8765"):
    """Launch a browser-based terminal
    
    Args:
        session_id: Optional session ID to connect to
        server_url: URL of the Terma server
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # If no session ID is provided, create a new session
        if not session_id:
            # Create a new session
            response = requests.post(
                f"{server_url}/api/sessions",
                json={}
            )
            
            if response.status_code == 200:
                data = response.json()
                session_id = data["session_id"]
                logger.info(f"Created new session: {session_id}")
            else:
                logger.error(f"Failed to create session: {response.text}")
                return False
                
        # Open the browser to the terminal URL
        url = f"{server_url}/terminal/{session_id}"
        webbrowser.open(url)
        logger.info(f"Opened browser terminal for session {session_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to launch browser terminal: {e}")
        return False

def create_or_get_session(server_url: str, session_id: Optional[str] = None, 
                         shell_command: Optional[str] = None) -> Optional[str]:
    """Create a new session or get an existing one
    
    Args:
        server_url: URL of the Terma server
        session_id: Optional session ID to connect to
        shell_command: Optional shell command to run
        
    Returns:
        str: The session ID, or None if failed
    """
    try:
        if session_id:
            # Check if the session exists
            response = requests.get(f"{server_url}/api/sessions/{session_id}")
            if response.status_code == 200:
                logger.info(f"Connected to existing session: {session_id}")
                return session_id
            else:
                logger.warning(f"Session {session_id} not found, creating new session")
                
        # Create a new session
        payload = {}
        if shell_command:
            payload["shell_command"] = shell_command
            
        response = requests.post(
            f"{server_url}/api/sessions",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            new_session_id = data["session_id"]
            logger.info(f"Created new session: {new_session_id}")
            return new_session_id
        else:
            logger.error(f"Failed to create session: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Connection error: {e}")
        logger.error(f"Is the Terma server running at {server_url}?")
        return None

def launch_terminal(session_id: Optional[str] = None, mode: str = "tmux", 
                   shell_command: Optional[str] = None, server_url: Optional[str] = None):
    """Launch a terminal session
    
    Args:
        session_id: Optional session ID to connect to
        mode: Terminal mode (tmux, screen, native, browser)
        shell_command: Optional shell command to run
        server_url: URL of the Terma server
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Get the server URL from config if not provided
    if not server_url:
        host = config.get("server.host", "localhost")
        port = config.get("server.port", 8765)
        server_url = f"http://{host}:{port}"
    
    # Create or get a session
    session_id = create_or_get_session(server_url, session_id, shell_command)
    if not session_id:
        return False
        
    # Launch the terminal based on mode
    if mode == "tmux":
        return launch_tmux_terminal(session_id, shell_command, server_url)
    elif mode == "screen":
        return launch_screen_terminal(session_id, shell_command, server_url)
    elif mode == "native":
        return launch_native_terminal(session_id, shell_command, server_url)
    elif mode == "browser":
        return launch_browser_terminal(session_id, server_url)
    else:
        logger.error(f"Unknown terminal mode: {mode}")
        return False

def main():
    """Main CLI entry point for terminal launcher"""
    parser = argparse.ArgumentParser(description="Terma Terminal Launcher")
    parser.add_argument("--session-id", help="Connect to an existing session")
    parser.add_argument("--mode", choices=["tmux", "screen", "native", "browser"], 
                       default="tmux", help="Terminal mode")
    parser.add_argument("--shell-command", help="Shell command to run")
    parser.add_argument("--server-url", help="URL of the Terma server")
    
    args = parser.parse_args()
    
    success = launch_terminal(
        session_id=args.session_id,
        mode=args.mode,
        shell_command=args.shell_command,
        server_url=args.server_url
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())