"""
Tool Launcher - Manages CI tool lifecycle and socket bridges.
"""

import logging
import threading
from typing import Dict, Optional, Any

from .base_adapter import BaseCIToolAdapter
from .socket_bridge import SocketBridge
from .registry import get_registry
from .adapters import ClaudeCodeAdapter, GenericAdapter

try:
    from landmarks import (
        architecture_decision, 
        state_checkpoint,
        integration_point,
        danger_zone
    )
except ImportError:
    def architecture_decision(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def state_checkpoint(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def danger_zone(**kwargs):
        def decorator(func):
            return func
        return decorator


@architecture_decision(
    title="Singleton Tool Launcher",
    description="Singleton tool launcher manages all CI tool processes",
    rationale="Centralized lifecycle management prevents orphan processes and port conflicts",
    alternatives_considered=["Per-tool launchers", "Process manager integration", "Systemd services"],
    impacts=["process_management", "resource_allocation", "multi_instance_support"],
    decided_by="Casey",
    decision_date="2025-08-02"
)
class ToolLauncher:
    """
    Manages CI tool processes and their socket bridges.
    
    Singleton class that handles launching, monitoring, and
    terminating CI tool processes.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                # Double-check locking pattern
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
            self.logger.info(f"ToolLauncher initialized, id: {id(self)}")
    
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
    def launch_tool(self, tool_name: str, session_id: Optional[str] = None, instance_name: Optional[str] = None) -> bool:
        """
        Launch a CI tool with socket bridge.
        
        Args:
            tool_name: Name of the tool to launch
            session_id: Optional session identifier
            instance_name: Optional instance name (allows multiple instances)
            
        Returns:
            True if launched successfully
        """
        # Use instance name if provided, otherwise use tool name
        launch_key = instance_name or tool_name
        
        # Check if already running
        if launch_key in self.tools and self.tools[launch_key]['adapter'].running:
            self.logger.info(f"{launch_key} is already running")
            return True
        
        # Get tool configuration
        tool_config = self.registry.get_tool(tool_name)
        if not tool_config:
            self.logger.error(f"Unknown tool: {tool_name}")
            return False
        
        try:
            # Allocate port dynamically if needed
            port = tool_config.get('port')
            if port == 'auto' or port is None:
                port = self.registry.find_available_port()
                self.logger.info(f"Allocated dynamic port {port} for {tool_name}")
            
            # Create a copy of config with actual port
            runtime_config = tool_config.copy()
            runtime_config['port'] = port
            
            # Create adapter based on tool
            adapter = self._create_adapter(tool_name, runtime_config)
            if not adapter:
                return False
            
            # Create socket bridge with allocated port
            bridge = SocketBridge(tool_name, port)
            bridge.connect_adapter(adapter)
            
            # Set message handler to send messages TO the tool
            def handle_message(msg):
                adapter.send_message(msg)
            
            bridge.set_message_handler(handle_message)
            
            # Set adapter output handler to send messages FROM the tool
            adapter.on_output = lambda msg: bridge.send_message(msg)
            
            # Start socket bridge
            if not bridge.start():
                self.logger.error(f"Failed to start socket bridge for {tool_name}")
                return False
            
            # Launch tool process
            if not adapter.launch(session_id):
                self.logger.error(f"Failed to launch {tool_name}")
                bridge.stop()
                return False
            
            # Store references using launch key
            self.tools[launch_key] = {
                'adapter': adapter,
                'bridge': bridge,
                'config': runtime_config,  # Use runtime_config with actual port
                'tool_name': tool_name,
                'instance_name': instance_name
            }
            
            # Mark as running in registry
            self.registry.mark_running(launch_key, adapter, adapter.process.pid)
            
            self.logger.info(f"Successfully launched {tool_name}")
            self.logger.info(f"Tools tracking: {list(self.tools.keys())}")
            print(f"DEBUG: Added {launch_key} to tools dict, now have: {list(self.tools.keys())}")
            print(f"DEBUG: launcher id after adding: {id(self)}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to launch {tool_name}: {e}")
            return False
    
    def terminate_tool(self, tool_key: str) -> bool:
        """
        Terminate a CI tool.
        
        Args:
            tool_key: Name or instance key of the tool to terminate
            
        Returns:
            True if terminated successfully
        """
        if tool_key not in self.tools:
            return True
        
        tool_info = self.tools[tool_key]
        
        try:
            # Terminate adapter (which terminates process)
            if tool_info['adapter']:
                tool_info['adapter'].terminate()
            
            # Stop socket bridge
            if tool_info['bridge']:
                tool_info['bridge'].stop()
            
            # Remove from tracking
            del self.tools[tool_key]
            
            # Mark as stopped in registry
            self.registry.mark_stopped(tool_key)
            
            self.logger.info(f"Terminated {tool_key}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to terminate {tool_key}: {e}")
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
        # Check for base_type first (for user-defined tools)
        base_type = config.get('base_type', tool_name)
        
        # Map tool types to adapter classes
        adapter_map = {
            'claude-code': ClaudeCodeAdapter,
            'generic': GenericAdapter,
            # Add more adapters as they're implemented
            # 'cursor': CursorAdapter,
            # 'continue': ContinueAdapter,
        }
        
        # Try base_type first, then tool_name
        adapter_class = adapter_map.get(base_type) or adapter_map.get(tool_name)
        
        if not adapter_class:
            self.logger.warning(f"No adapter for {tool_name} (base_type: {base_type}), using generic adapter")
            adapter_class = GenericAdapter
        
        # Pass full config to adapter
        return adapter_class(tool_name, config)


# Global singleton instance
_launcher_instance = None
_launcher_lock = threading.Lock()

def get_tool_launcher() -> ToolLauncher:
    """Get the global tool launcher instance."""
    global _launcher_instance
    if _launcher_instance is None:
        with _launcher_lock:
            if _launcher_instance is None:
                _launcher_instance = ToolLauncher()
    return _launcher_instance