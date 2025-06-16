"""Metis component implementation using StandardComponentBase."""
import logging
from typing import List, Dict, Any
from pathlib import Path

from shared.utils.standard_component import StandardComponentBase
from metis.core.task_manager import TaskManager
from metis.core.connection_manager import ConnectionManager
import metis.core.mcp.tools as mcp_tools

logger = logging.getLogger(__name__)

class MetisComponent(StandardComponentBase):
    """Metis task management component with WebSocket and MCP support."""
    
    def __init__(self):
        super().__init__(component_name="metis", version="0.1.0")
        # Component-specific attributes
        self.task_manager = None
        self.connection_manager = None
        self.mcp_tools = {}
        self.fastmcp_server = None
        self.db_path = None
        
    async def _component_specific_init(self):
        """Initialize Metis-specific services."""
        # Critical components - fail if these don't work
        from pathlib import Path
        self.db_path = Path(self.global_config.get_data_dir("metis")) / "tasks.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize task manager (uses InMemoryStorage by default)
        self.task_manager = TaskManager()
        
        # Initialize connection manager for WebSocket
        self.connection_manager = ConnectionManager()
        
        # Register event handlers
        self._register_event_handlers()
        
        # Optional components - warn but continue
        try:
            # Initialize MCP tools - Metis uses a different pattern
            # The tools module has functions like decompose_task, analyze_task_complexity, etc.
            # Rather than individual CRUD tools
            self.mcp_tools = {
                "decompose_task": mcp_tools.decompose_task,
                "analyze_task_complexity": mcp_tools.analyze_task_complexity,
                "suggest_task_order": mcp_tools.suggest_task_order,
                "generate_subtasks": mcp_tools.generate_subtasks,
                "detect_dependencies": mcp_tools.detect_dependencies
            }
            
            # Update the global task manager reference in mcp_tools
            # This is a temporary workaround until we refactor mcp_tools
            mcp_tools._task_manager = self.task_manager
                    
            logger.info("MCP tools initialized successfully")
        except Exception as e:
            logger.warning(f"MCP tools initialization failed: {e}")
            self.mcp_tools = {}
        
        # Note: FastMCP server is initialized and managed in fastmcp_endpoints.py
        # We don't need to duplicate that initialization here
        self.fastmcp_server = None  # Will be set by app.py if needed
    
    def _register_event_handlers(self):
        """Register event handlers for task manager."""
        if self.task_manager:
            # Register handlers for task events
            self.task_manager.on_task_created = self._handle_task_created
            self.task_manager.on_task_updated = self._handle_task_updated
            self.task_manager.on_task_deleted = self._handle_task_deleted
            self.task_manager.on_task_completed = self._handle_task_completed
    
    async def _handle_task_created(self, task):
        """Handle task created event."""
        if self.connection_manager:
            await self.connection_manager.broadcast({
                "event": "task_created",
                "task": task.dict()
            })
    
    async def _handle_task_updated(self, task):
        """Handle task updated event."""
        if self.connection_manager:
            await self.connection_manager.broadcast({
                "event": "task_updated", 
                "task": task.dict()
            })
    
    async def _handle_task_deleted(self, task_id):
        """Handle task deleted event."""
        if self.connection_manager:
            await self.connection_manager.broadcast({
                "event": "task_deleted",
                "task_id": task_id
            })
    
    async def _handle_task_completed(self, task):
        """Handle task completed event."""
        if self.connection_manager:
            await self.connection_manager.broadcast({
                "event": "task_completed",
                "task": task.dict()
            })
    
    async def _component_specific_cleanup(self):
        """Cleanup Metis-specific resources."""
        # Disconnect all WebSocket clients
        if self.connection_manager:
            await self.connection_manager.disconnect_all()
            logger.info("Disconnected all WebSocket clients")
        
        # Stop FastMCP server
        if self.fastmcp_server:
            try:
                # FastMCP doesn't have async stop, handle gracefully
                logger.info("FastMCP server cleanup completed")
            except Exception as e:
                logger.warning(f"Error during FastMCP cleanup: {e}")
        
        # Task manager doesn't have a close method - it uses InMemoryStorage
        if self.task_manager:
            logger.info("Task manager cleanup completed")
        
        # Cleanup MCP tools if needed
        for tool_name, tool in self.mcp_tools.items():
            if hasattr(tool, 'cleanup'):
                try:
                    await tool.cleanup()
                except Exception as e:
                    logger.warning(f"Error cleaning up MCP tool {tool_name}: {e}")
    
    def get_capabilities(self) -> List[str]:
        """Get component capabilities."""
        capabilities = [
            "task_management",
            "task_decomposition", 
            "event_streaming",
            "websocket_support"
        ]
        
        if self.mcp_tools:
            capabilities.append("mcp_tools")
        
        if self.fastmcp_server:
            capabilities.append("fastmcp_server")
            
        return capabilities
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get component metadata."""
        metadata = {
            "description": "Task management and decomposition system",
            "websocket_endpoint": "/ws",
            "mcp_enabled": bool(self.mcp_tools),
            "fastmcp_enabled": bool(self.fastmcp_server),
            "database": str(self.db_path) if self.db_path else None
        }
        
        # Task manager doesn't have get_task_count method
            
        return metadata