#\!/usr/bin/env python3
"""
Terma Terminal Client Example

This example demonstrates how to use the Terma terminal system
from Python code, including session management, terminal I/O,
and LLM assistance.
"""

import argparse
import asyncio
import json
import sys
import os
import aiohttp


class TermaClient:
    """Client for interacting with Terma terminal services"""
    
    def __init__(self, base_url="http://localhost:8765"):
        """Initialize the client
        
        Args:
            base_url: Base URL of the Terma API
        """
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.ws_url = f"{base_url.replace('http', 'ws')}/ws"
        self.session = None
    
    async def initialize(self):
        """Initialize the HTTP session"""
        self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
    
    async def create_session(self, shell_command=None):
        """Create a new terminal session
        
        Args:
            shell_command: Optional shell command to run
            
        Returns:
            dict: Session information
        """
        if not self.session:
            await self.initialize()
            
        payload = {}
        if shell_command:
            payload["shell_command"] = shell_command
            
        async with self.session.post(f"{self.api_url}/sessions", json=payload) as response:
            response.raise_for_status()
            return await response.json()
    
    async def list_sessions(self):
        """List all active terminal sessions
        
        Returns:
            dict: List of sessions
        """
        if not self.session:
            await self.initialize()
            
        async with self.session.get(f"{self.api_url}/sessions") as response:
            response.raise_for_status()
            return await response.json()
    
    async def get_session(self, session_id):
        """Get information about a specific session
        
        Args:
            session_id: ID of the session
            
        Returns:
            dict: Session information
        """
        if not self.session:
            await self.initialize()
            
        async with self.session.get(f"{self.api_url}/sessions/{session_id}") as response:
            response.raise_for_status()
            return await response.json()
    
    async def close_session(self, session_id):
        """Close a terminal session
        
        Args:
            session_id: ID of the session to close
            
        Returns:
            dict: Status response
        """
        if not self.session:
            await self.initialize()
            
        async with self.session.delete(f"{self.api_url}/sessions/{session_id}") as response:
            response.raise_for_status()
            return await response.json()
    
    async def write_to_session(self, session_id, data):
        """Write data to a terminal session
        
        Args:
            session_id: ID of the session
            data: Data to write
            
        Returns:
            dict: Write result
        """
        if not self.session:
            await self.initialize()
            
        async with self.session.post(
            f"{self.api_url}/sessions/{session_id}/write",
            json={"data": data}
        ) as response:
            response.raise_for_status()
            return await response.json()
    
    async def read_from_session(self, session_id, size=1024):
        """Read data from a terminal session
        
        Args:
            session_id: ID of the session
            size: Maximum bytes to read
            
        Returns:
            dict: Read result with data
        """
        if not self.session:
            await self.initialize()
            
        async with self.session.get(
            f"{self.api_url}/sessions/{session_id}/read",
            params={"size": size}
        ) as response:
            response.raise_for_status()
            return await response.json()
    
    async def connect_websocket(self, session_id, on_output, on_error=None, on_llm_response=None):
        """Connect to terminal WebSocket and handle messages
        
        Args:
            session_id: ID of the session
            on_output: Callback for terminal output
            on_error: Optional callback for errors
            on_llm_response: Optional callback for LLM responses
            
        Returns:
            WebSocketClientProtocol: WebSocket connection
        """
        if not self.session:
            await self.initialize()
        
        websocket = await aiohttp.ClientSession().ws_connect(f"{self.ws_url}/{session_id}")
        
        async def receiver():
            async for msg in websocket:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    
                    if data["type"] == "output":
                        if on_output:
                            on_output(data["data"])
                    elif data["type"] == "error":
                        if on_error:
                            on_error(data["message"])
                    elif data["type"] == "llm_response":
                        if on_llm_response:
                            on_llm_response(data["content"])
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    break
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break
        
        # Start receiver task
        asyncio.create_task(receiver())
        
        return websocket
    
    async def send_input(self, websocket, data):
        """Send input through WebSocket
        
        Args:
            websocket: WebSocket connection
            data: Data to send
        """
        await websocket.send_json({
            "type": "input",
            "data": data
        })
    
    async def resize_terminal(self, websocket, rows, cols):
        """Resize terminal through WebSocket
        
        Args:
            websocket: WebSocket connection
            rows: Number of rows
            cols: Number of columns
        """
        await websocket.send_json({
            "type": "resize",
            "rows": rows,
            "cols": cols
        })
    
    async def request_llm_assistance(self, websocket, command):
        """Request LLM assistance for a command
        
        Args:
            websocket: WebSocket connection
            command: Command to analyze
        """
        await websocket.send_json({
            "type": "llm_assist",
            "command": command
        })


async def interactive_session():
    """Run an interactive terminal session"""
    client = TermaClient()
    
    try:
        # Create session
        print("Creating terminal session...")
        session = await client.create_session()
        session_id = session["session_id"]
        print(f"Session created: {session_id}")
        
        # Define callbacks
        def on_output(data):
            sys.stdout.write(data)
            sys.stdout.flush()
        
        def on_error(message):
            print(f"\nError: {message}", file=sys.stderr)
        
        def on_llm_response(content):
            print(f"\n--- LLM Assistance ---\n{content}\n-------------------")
        
        # Connect WebSocket
        print("Connecting to terminal...")
        websocket = await client.connect_websocket(
            session_id,
            on_output=on_output,
            on_error=on_error,
            on_llm_response=on_llm_response
        )
        
        print("Terminal connected. Type commands and press Enter.")
        print("Type 'exit' to quit, or 'help?' to get LLM assistance.")
        
        # Main input loop
        while True:
            try:
                command = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: input()
                )
                
                if command.lower() == "exit":
                    break
                
                # Check for LLM assistance
                if command.endswith("?"):
                    # Remove the question mark
                    pure_command = command[:-1].strip()
                    
                    # Only request assistance if there's an actual command
                    if pure_command:
                        await client.request_llm_assistance(websocket, pure_command)
                
                # Send the command to the terminal (with newline)
                await client.send_input(websocket, command + "\n")
                
            except (KeyboardInterrupt, EOFError):
                break
        
        # Close the WebSocket and session
        await websocket.close()
        await client.close_session(session_id)
        print(f"\nSession {session_id} closed.")
    
    finally:
        # Clean up
        await client.close()


async def run_command(command):
    """Run a single command and return output
    
    Args:
        command: Command to run
        
    Returns:
        str: Command output
    """
    client = TermaClient()
    
    try:
        # Create session
        session = await client.create_session()
        session_id = session["session_id"]
        
        # Write command to session
        await client.write_to_session(session_id, command + "\n")
        
        # Wait a bit for command to complete
        await asyncio.sleep(1)
        
        # Read output
        response = await client.read_from_session(session_id)
        output = response["data"]
        
        # Close session
        await client.close_session(session_id)
        
        return output
    
    finally:
        # Clean up
        await client.close()


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Terma Terminal Client Example")
    
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    
    parser.add_argument(
        "--command",
        type=str,
        help="Command to run (non-interactive mode)"
    )
    
    parser.add_argument(
        "--server",
        type=str,
        default="http://localhost:8765",
        help="Terma server URL"
    )
    
    return parser.parse_args()


async def main():
    """Main entry point"""
    args = parse_args()
    
    if args.interactive:
        await interactive_session()
    elif args.command:
        output = await run_command(args.command)
        print(output)
    else:
        print("Please specify either --interactive or --command")


if __name__ == "__main__":
    asyncio.run(main())
EOF < /dev/null