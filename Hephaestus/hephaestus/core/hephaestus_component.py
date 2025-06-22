"""Hephaestus component implementation using StandardComponentBase."""
import logging
import os
import asyncio
import subprocess
import threading
import time
from typing import Optional, Dict, Any
from pathlib import Path

from shared.utils.standard_component import StandardComponentBase
from landmarks import architecture_decision, integration_point, state_checkpoint

logger = logging.getLogger(__name__)

@architecture_decision(
    title="Unified UI server architecture",
    rationale="Single component managing both HTTP/WebSocket UI server and MCP DevTools for centralized UI operations",
    alternatives_considered=["Separate UI and DevTools components", "Client-side only UI", "Multiple UI servers"])
@integration_point(
    title="UI component bridge",
    target_component="All Tekton components",
    protocol="Internal API",
    data_flow="Components → WebSocket → UI → User interactions → MCP DevTools → Component state"
)
class HephaestusComponent(StandardComponentBase):
    """Hephaestus UI server component managing both HTTP/WebSocket and MCP servers."""
    
    def __init__(self):
        super().__init__(component_name="hephaestus", version="0.1.0")
        # Component-specific attributes
        self.initialized = False
        self.http_server_thread = None
        self.http_server = None
        self.mcp_process = None
        self.ui_directory = None
        self.http_port = None
        self.mcp_port = None
        self.websocket_server = None
        
    async def _component_specific_init(self):
        """Initialize Hephaestus-specific services."""
        # Get ports from configuration
        self.http_port = self.global_config.config.hephaestus.port
        self.mcp_port = self.global_config.config.hephaestus.mcp_port
        
        # Set up UI directory
        hephaestus_root = Path(__file__).parent.parent.parent
        self.ui_directory = hephaestus_root / "ui"
        
        if not self.ui_directory.exists():
            raise FileNotFoundError(f"UI directory not found: {self.ui_directory}")
        
        logger.info(f"UI directory: {self.ui_directory}")
        logger.info(f"HTTP/WebSocket port: {self.http_port}")
        logger.info(f"MCP DevTools port: {self.mcp_port}")
        
        # Start main HTTP/WebSocket server in background thread
        self.http_server_thread = self._start_http_server()
        
        # Start MCP DevTools server
        self.mcp_process = await self._start_mcp_server()
        
        self.initialized = True
        logger.info("Hephaestus component initialization completed")
    
    def _start_http_server(self):
        """Start the HTTP/WebSocket server in a background thread."""
        def run_server():
            try:
                # Import server module
                import sys
                sys.path.insert(0, str(self.ui_directory.parent))
                
                from ui.server.server import run_http_server, run_websocket_server
                
                # Initialize WebSocket server (doesn't actually run separately in single port mode)
                run_websocket_server(self.http_port)
                
                # Run HTTP server (this blocks)
                logger.info(f"Starting HTTP/WebSocket server on port {self.http_port}")
                run_http_server(str(self.ui_directory), self.http_port)
                
            except Exception as e:
                logger.error(f"Error in HTTP server thread: {e}")
                raise
        
        # Create and start thread
        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()
        
        # Wait a bit to ensure server starts
        time.sleep(2)
        
        # Verify server is running
        import urllib.request
        max_retries = 10
        for i in range(max_retries):
            try:
                response = urllib.request.urlopen(f"http://localhost:{self.http_port}/health")
                if response.status == 200:
                    logger.info("HTTP/WebSocket server started successfully")
                    break
            except Exception:
                if i == max_retries - 1:
                    raise RuntimeError("Failed to start HTTP/WebSocket server")
                time.sleep(1)
        
        return thread
    
    @state_checkpoint(
        title="MCP DevTools server state",
        state_type="subprocess",
        persistence=False,
        consistency_requirements="MCP server process must be tracked for cleanup",
        recovery_strategy="Restart MCP server on failure, non-critical service"
    )
    async def _start_mcp_server(self):
        """Start the MCP DevTools server as a subprocess."""
        try:
            # Path to MCP server script
            mcp_script = Path(__file__).parent.parent / "mcp" / "mcp_server.py"
            
            if not mcp_script.exists():
                logger.warning(f"MCP server script not found: {mcp_script}")
                return None
            
            # Set environment variables for MCP server
            env = os.environ.copy()
            env["MCP_PORT"] = str(self.mcp_port)
            env["PYTHONPATH"] = f"{Path(__file__).parent.parent.parent}:{os.environ.get('PYTHONPATH', '')}"
            
            # Start MCP server process
            logger.info(f"Starting MCP DevTools server on port {self.mcp_port}")
            process = subprocess.Popen(
                ["python3", str(mcp_script)],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait a bit and check if process is running
            await asyncio.sleep(2)
            
            if process.poll() is not None:
                # Process ended, check stderr
                stderr = process.stderr.read().decode() if process.stderr else ""
                raise RuntimeError(f"MCP server failed to start: {stderr}")
            
            # Verify MCP server is running
            import httpx
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(f"http://localhost:{self.mcp_port}/health")
                    if response.status_code == 200:
                        logger.info("MCP DevTools server started successfully")
                except Exception as e:
                    logger.warning(f"MCP server health check failed: {e}")
                    # Not critical if MCP server is not available
            
            return process
            
        except Exception as e:
            logger.error(f"Error starting MCP server: {e}")
            # MCP server is optional, so we don't fail the component
            return None
    
    async def _component_specific_cleanup(self):
        """Cleanup Hephaestus-specific resources."""
        # Stop MCP server process
        if self.mcp_process:
            try:
                logger.info("Stopping MCP DevTools server")
                self.mcp_process.terminate()
                
                # Wait for graceful shutdown
                try:
                    self.mcp_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning("MCP server did not stop gracefully, killing process")
                    self.mcp_process.kill()
                    
            except Exception as e:
                logger.error(f"Error stopping MCP server: {e}")
        
        # Stop HTTP server thread
        if self.http_server:
            try:
                logger.info("Stopping HTTP/WebSocket server")
                # The HTTP server should have a shutdown method
                # For now, the thread is daemon so it will stop with the process
            except Exception as e:
                logger.error(f"Error stopping HTTP server: {e}")
        
        logger.info("Hephaestus cleanup completed")
    
    def get_capabilities(self) -> list:
        """Get component capabilities."""
        capabilities = ["ui", "visualization", "websocket"]
        
        if self.mcp_process and self.mcp_process.poll() is None:
            capabilities.append("ui_devtools")
            capabilities.append("mcp")
        
        return capabilities
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get component metadata."""
        metadata = {
            "description": "UI and visualization component for Tekton ecosystem",
            "ui_directory": str(self.ui_directory) if self.ui_directory else None,
            "http_port": self.http_port,
            "mcp_port": self.mcp_port,
            "mcp_running": bool(self.mcp_process and self.mcp_process.poll() is None),
            "ui_components": [
                "apollo", "athena", "budget", "codex", "engram", "ergon",
                "harmonia", "hermes", "metis", "prometheus", "rhetor",
                "sophia", "synthesis", "tekton", "telos", "terma"
            ]
        }
        
        return metadata
    
    def get_component_status(self) -> Dict[str, Any]:
        """Get component status information."""
        return {
            "initialized": self.initialized,
            "http_server_running": bool(self.http_server_thread and self.http_server_thread.is_alive()),
            "mcp_server_running": bool(self.mcp_process and self.mcp_process.poll() is None),
            "ui_directory": str(self.ui_directory) if self.ui_directory else None,
            "http_port": self.http_port,
            "mcp_port": self.mcp_port
        }