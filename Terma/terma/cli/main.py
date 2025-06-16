"""Command-line entry point for Terma"""

import argparse
import sys
import asyncio
import logging
import os
import signal
import time
import uvicorn
from typing import Optional

import logging

from ..utils.logging import setup_logging
from ..utils.config import Config
from ..core.session_manager import SessionManager
from ..api.app import app, start_server
from ..api.ui_server import start_ui_server

# Use DEBUG level for logging during troubleshooting
logger = setup_logging(level=logging.DEBUG)
config = Config()

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Terma Terminal Management")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Version command
    parser.add_argument("--version", action="store_true", help="Show version and exit")
    
    # Start server command
    server_parser = subparsers.add_parser("server", help="Start the Terma server")
    server_parser.add_argument("--host", default=config.get("server.host", "0.0.0.0"), 
                              help="Host to bind to")
    server_parser.add_argument("--port", type=int, default=config.get("server.port", 8765), 
                              help="Port to bind to")
    server_parser.add_argument("--ui-port", type=int, default=config.get("ui.port", 8766),
                              help="Port for the UI server")
    server_parser.add_argument("--no-ui", action="store_true", help="Don't start the UI server")
    
    # Create session command
    session_parser = subparsers.add_parser("create-session", help="Create a new terminal session")
    session_parser.add_argument("--shell-command", help="Shell command to run")
    
    # List sessions command
    list_parser = subparsers.add_parser("list-sessions", help="List active terminal sessions")
    
    # Close session command
    close_parser = subparsers.add_parser("close-session", help="Close a terminal session")
    close_parser.add_argument("session_id", help="ID of the session to close")
    
    # UI server command
    ui_parser = subparsers.add_parser("ui", help="Start the UI server")
    ui_parser.add_argument("--host", default=config.get("ui.host", "0.0.0.0"),
                          help="Host to bind to")
    ui_parser.add_argument("--port", type=int, default=config.get("ui.port", 8766),
                          help="Port to bind to")
    
    args = parser.parse_args()
    
    # Show version
    if args.version:
        from .. import __version__
        print(f"Terma Terminal version {__version__}")
        return 0
    
    # Handle commands
    if args.command == "server":
        # Save config
        config.set("server.host", args.host)
        config.set("server.port", args.port)
        
        if not args.no_ui:
            config.set("ui.host", args.host)
            config.set("ui.port", args.ui_port)
        
        try:
            # Set up asyncio event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Add debug logging for port availability before starting servers
            def check_port(host, port, name):
                import socket
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = s.connect_ex((host, port))
                if result == 0:
                    logger.debug(f"Port {port} for {name} is ALREADY IN USE")
                    # Check what process is using the port
                    import subprocess
                    try:
                        process_info = subprocess.run(['lsof', '-i', f':{port}'], 
                                                    capture_output=True, text=True)
                        logger.debug(f"lsof output for port {port}:\n{process_info.stdout}")
                    except Exception as e:
                        logger.debug(f"Failed to run lsof: {e}")
                else:
                    logger.debug(f"Port {port} for {name} is AVAILABLE")
                s.close()
                return result == 0
            
            # Check ports before starting servers
            api_port_used = check_port(args.host, args.port, "API Server")
            if api_port_used:
                logger.warning(f"API port {args.port} is already in use!")
            
            if not args.no_ui:
                ui_port_used = check_port(args.host, args.ui_port, "UI Server")
                if ui_port_used:
                    logger.warning(f"UI port {args.ui_port} is already in use!")
            
            # Start UI server in a separate process if requested
            ui_process = None
            if not args.no_ui:
                try:
                    import multiprocessing
                    logger.info(f"Starting UI server on {args.host}:{args.ui_port}")
                    ui_process = multiprocessing.Process(
                        target=start_ui_server,
                        args=(args.host, args.ui_port)
                    )
                    ui_process.start()
                    logger.debug(f"UI process started with PID {ui_process.pid}")
                except Exception as e:
                    logger.error(f"Failed to start UI server: {e}")
            
            # Start the API server with WebSocket server on a different port (+2 by default)
            # This allows both the API and WebSocket servers to run in the main process without port conflict
            ws_port = args.port + 2  # Use API port + 2 to avoid conflict with UI server
            logger.info(f"Starting API server on {args.host}:{args.port}")
            logger.info(f"Starting WebSocket server on {args.host}:{ws_port}")
            loop.run_until_complete(start_server(args.host, args.port, ws_port=ws_port))
            
        except KeyboardInterrupt:
            print("Server stopped")
            if ui_process:
                ui_process.terminate()
        except Exception as e:
            logger.error(f"Server error: {e}")
            if ui_process:
                ui_process.terminate()
            return 1
            
    elif args.command == "ui":
        # Save config
        config.set("ui.host", args.host)
        config.set("ui.port", args.port)
        
        # Start the UI server
        print(f"Starting UI server on {args.host}:{args.port}")
        
        try:
            start_ui_server(args.host, args.port)
        except KeyboardInterrupt:
            print("UI server stopped")
        except Exception as e:
            logger.error(f"UI server error: {e}")
            return 1
            
    elif args.command == "create-session":
        # Create a session
        session_manager = SessionManager()
        session_id = session_manager.create_session(shell_command=args.shell_command)
        if session_id:
            print(f"Created session: {session_id}")
            return 0
        else:
            print("Failed to create session")
            return 1
            
    elif args.command == "list-sessions":
        # List sessions
        session_manager = SessionManager()
        sessions = session_manager.list_sessions()
        if sessions:
            print("Active sessions:")
            for session in sessions:
                print(f"  {session['id']} - Active: {session['active']}, "
                      f"Shell: {session['shell_command']}, "
                      f"Idle: {session['idle_time']:.1f}s")
        else:
            print("No active sessions")
            
    elif args.command == "close-session":
        # Close a session
        session_manager = SessionManager()
        success = session_manager.close_session(args.session_id)
        if success:
            print(f"Closed session: {args.session_id}")
            return 0
        else:
            print(f"Failed to close session: {args.session_id}")
            return 1
            
    else:
        parser.print_help()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())