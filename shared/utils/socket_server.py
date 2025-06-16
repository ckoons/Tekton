"""
Socket reuse utility for uvicorn servers.

Provides a wrapper to enable SO_REUSEADDR for uvicorn servers,
fixing the port binding issues during rapid restarts.
"""
import os
import sys
import socket
import signal
import asyncio
import struct
import uvicorn
from uvicorn.config import Config
from uvicorn.server import Server


async def run_with_socket_reuse_async(app, host: str = "0.0.0.0", port: int = 8000, **kwargs):
    """
    Run uvicorn with socket reuse enabled (async version).
    
    This properly configures socket reuse for immediate port rebinding on macOS.
    
    Args:
        app: Either a string (e.g., "module:app") or an app instance
        host: Host to bind to
        port: Port to bind to
        **kwargs: Additional arguments for uvicorn Config
    """
    # Create socket with proper reuse options
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Enable reuse options BEFORE binding
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # REMOVED SO_REUSEPORT - we don't want multiple processes on same port
    
    # Set SO_LINGER to 2 seconds for graceful close
    linger_struct = struct.pack('ii', 1, 2)  # onoff=1, linger time=2 seconds
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, linger_struct)
    
    # Bind and listen
    sock.bind((host, port))
    sock.listen(128)
    
    # Configure uvicorn with our socket
    kwargs.pop('host', None)
    kwargs.pop('port', None)
    
    config = Config(
        app,
        fd=sock.fileno(),
        **kwargs
    )
    
    server = Server(config)
    
    # Handle signals properly
    def signal_handler(signum, frame):
        server.should_exit = True
    
    for sig in [signal.SIGTERM, signal.SIGINT]:
        signal.signal(sig, signal_handler)
    
    try:
        await server.serve()
    finally:
        sock.close()


def run_with_socket_reuse(app, host: str = "0.0.0.0", port: int = 8000, **kwargs):
    """
    Run uvicorn with socket reuse enabled.
    
    This fixes the "Address already in use" error during rapid restarts.
    
    Args:
        app: Either a string (e.g., "module:app") or an app instance
        host: Host to bind to
        port: Port to bind to
        **kwargs: Additional arguments for uvicorn Config
    """
    # Create socket with proper reuse options
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Enable reuse options BEFORE binding
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # REMOVED SO_REUSEPORT - we don't want multiple processes on same port
    
    # Set SO_LINGER to 2 seconds for graceful close
    linger_struct = struct.pack('ii', 1, 2)  # onoff=1, linger time=2 seconds
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, linger_struct)
    
    # Bind and listen
    sock.bind((host, port))
    sock.listen(128)
    
    # Configure uvicorn with our socket
    kwargs.pop('host', None)
    kwargs.pop('port', None)
    
    config = Config(
        app,
        fd=sock.fileno(),
        **kwargs
    )
    
    server = Server(config)
    
    # Create new event loop for the server
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Handle signals
    def signal_handler(signum, frame):
        server.should_exit = True
    
    for sig in [signal.SIGTERM, signal.SIGINT]:
        signal.signal(sig, signal_handler)
    
    try:
        loop.run_until_complete(server.serve())
    finally:
        sock.close()
        loop.close()


class ReuseAddressServer(Server):
    """Uvicorn server with SO_REUSEADDR enabled."""
    
    async def startup(self, sockets=None):
        """Override startup to set socket options."""
        await super().startup(sockets)
        
        # Set SO_REUSEADDR on all server sockets
        for server in self.servers:
            for sock in server.sockets:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                # On macOS, also set SO_REUSEPORT
                if hasattr(socket, 'SO_REUSEPORT'):
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)


def run_component_server(
    component_name: str,
    app_module,
    default_port: int,
    reload: bool = False
):
    """
    Run a Tekton component server with proper socket reuse.
    
    Args:
        component_name: Name of the component (e.g., "budget", "telos")
        app_module: Module path to the app (e.g., "budget.api.app") or app instance
        default_port: Default port if not in environment
        reload: Whether to enable auto-reload
    """
    # Get port from environment
    port_env = f"{component_name.upper()}_PORT"
    port = int(os.environ.get(port_env, str(default_port)))
    
    print(f"Starting {component_name.capitalize()} on port {port}...")
    
    # Run with socket reuse
    # If app_module is a string, append :app, otherwise use it directly
    app = f"{app_module}:app" if isinstance(app_module, str) else app_module
    run_with_socket_reuse(
        app,
        host="0.0.0.0",
        port=port,
        reload=reload,
        reload_dirs=[component_name] if reload else None,
        timeout_graceful_shutdown=5,
        server_header=False,
        access_log=False,
        use_colors=True
    )