"""
Tool Launcher - Manages CI tool lifecycle and socket bridges.
"""

import logging
from typing import Dict, Optional, Any

from .base_adapter import BaseCIToolAdapter
from .socket_bridge import SocketBridge
from .registry import get_registry
from .adapters import ClaudeCodeAdapter

try:
    from landmarks import architecture_decision, state_checkpoint
except ImportError:
    def architecture_decision(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def state_checkpoint(**kwargs):
        def decorator(func):
            return func
        return decorator


@architecture_decision(
    title="Singleton Tool Launcher",
    description="Singleton tool launcher manages all CI tool processes",
    rationale="Centralized lifecycle management prevents orphan processes",
    tags=["ci-tools", "lifecycle", "singleton"]
)
class ToolLauncher:
    """
    Manages CI tool processes and their socket bridges.
    
    Singleton class that handles launching, monitoring, and
    terminating CI tool processes.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the tool launcher."""
        if not hasattr(self, 'initialized'):
            self.logger = logging.getLogger("ci_tools.launcher")
            self.tools = {}  # tool_name -> dict with adapter, bridge
            self.registry = get_registry()
            self.initialized = True
    
    @classmethod
    def get_instance(cls) -> 'ToolLauncher':
        """Get the singleton instance."""
        return cls()
    
    @state_checkpoint(
        title="Launch Tool",
        description="Launch a CI tool with socket bridge",
        state_type="process",
        state_key="running_tools"
    )
    def launch_tool(self, tool_name: str, session_id: Optional[str] = None) -> bool:
        """
        Launch a CI tool with socket bridge.
        
        Args:
            tool_name: Name of the tool to launch
            session_id: Optional session identifier
            
        Returns:
            True if launched successfully
        """
        # Check if already running
        if tool_name in self.tools and self.tools[tool_name]['adapter'].running:
            self.logger.info(f"{tool_name} is already running")
            return True
        
        # Get tool configuration
        tool_config = self.registry.get_tool(tool_name)
        if not tool_config:
            self.logger.error(f"Unknown tool: {tool_name}")
            return False
        
        try:
            # Create adapter based on tool
            adapter = self._create_adapter(tool_name, tool_config)
            if not adapter:
                return False
            
            # Create socket bridge
            bridge = SocketBridge(tool_name, tool_config['port'])
            bridge.connect_adapter(adapter)
            
            # Set message handler
            def handle_message(msg):
                adapter.on_output(msg)
            
            bridge.set_message_handler(handle_message)
            
            # Start socket bridge
            if not bridge.start():
                self.logger.error(f"Failed to start socket bridge for {tool_name}")
                return False
            
            # Launch tool process
            if not adapter.launch(session_id):
                self.logger.error(f"Failed to launch {tool_name}")
                bridge.stop()
                return False
            
            # Store references
            self.tools[tool_name] = {
                'adapter': adapter,
                'bridge': bridge,
                'config': tool_config
            }
            
            # Mark as running in registry
            self.registry.mark_running(tool_name, adapter, adapter.process.pid)
            
            self.logger.info(f"Successfully launched {tool_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to launch {tool_name}: {e}")
            return False
    
    def terminate_tool(self, tool_name: str) -> bool:
        """
        Terminate a CI tool.
        
        Args:
            tool_name: Name of the tool to terminate
            
        Returns:
            True if terminated successfully
        """
        if tool_name not in self.tools:
            return True
        
        tool_info = self.tools[tool_name]
        
        try:
            # Terminate adapter (which terminates process)
            if tool_info['adapter']:
                tool_info['adapter'].terminate()
            
            # Stop socket bridge
            if tool_info['bridge']:
                tool_info['bridge'].stop()
            
            # Remove from tracking
            del self.tools[tool_name]
            
            # Mark as stopped in registry
            self.registry.mark_stopped(tool_name)
            
            self.logger.info(f"Terminated {tool_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to terminate {tool_name}: {e}")
            return False
    
    def terminate_all(self):
        """Terminate all running tools."""
        tool_names = list(self.tools.keys())
        for tool_name in tool_names:
            self.terminate_tool(tool_name)
    
    def get_adapter(self, tool_name: str) -> Optional[BaseCIToolAdapter]:
        """Get adapter for a tool."""
        tool_info = self.tools.get(tool_name)
        return tool_info['adapter'] if tool_info else None
    
    def get_bridge(self, tool_name: str) -> Optional[SocketBridge]:
        """Get socket bridge for a tool."""
        tool_info = self.tools.get(tool_name)
        return tool_info['bridge'] if tool_info else None
    
    def get_status(self, tool_name: str) -> Dict[str, Any]:
        """Get status for a tool."""
        if tool_name not in self.tools:
            return {'running': False}
        
        tool_info = self.tools[tool_name]
        status = {
            'running': True,
            'adapter_status': tool_info['adapter'].get_status(),
            'bridge_status': tool_info['bridge'].get_status()
        }
        
        return status
    
    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status for all tools."""
        return {
            tool_name: self.get_status(tool_name)
            for tool_name in self.registry.get_tools()
        }
    
    def _create_adapter(self, tool_name: str, config: Dict[str, Any]) -> Optional[BaseCIToolAdapter]:
        """Create adapter instance for a tool."""
        # Map tool names to adapter classes
        adapter_map = {
            'claude-code': ClaudeCodeAdapter,
            # Add more adapters as they're implemented
            # 'cursor': CursorAdapter,
            # 'continue': ContinueAdapter,
        }
        
        adapter_class = adapter_map.get(tool_name)
        if not adapter_class:
            self.logger.warning(f"No adapter implemented for {tool_name}, using base adapter")
            # Could implement a generic adapter here
            return None
        
        return adapter_class(port=config['port'])