"""
CI Tool Registry - Manages available CI tools and their configurations.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    from landmarks import (
        architecture_decision,
        api_contract, 
        state_checkpoint,
        integration_point,
        performance_boundary
    )
except ImportError:
    def architecture_decision(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def api_contract(**kwargs):
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
    
    def performance_boundary(**kwargs):
        def decorator(func):
            return func
        return decorator


# Default CI Tools configuration
# These will be written to config file on first run
DEFAULT_TOOLS_CONFIG = {
    'claude-code': {
        'display_name': 'Claude Code',
        'type': 'tool',
        'port': 'auto',
        'description': 'Claude AI coding assistant',
        'executable': 'claude-code',
        'launch_args': ['--no-sandbox', '--enable-stdio-bridge'],
        'health_check': 'version',
        'capabilities': {
            'code_analysis': True,
            'code_generation': True,
            'refactoring': True,
            'multi_file': True,
            'project_context': True,
            'debugging': True,
            'testing': True
        },
        'environment': {
            'CLAUDE_CODE_MODE': 'socket'
        }
    },
    'cursor': {
        'display_name': 'Cursor',
        'type': 'tool',
        'port': 'auto',
        'description': 'AI-powered code editor',
        'executable': 'cursor',
        'launch_args': ['--cli-mode', '--socket-bridge'],
        'health_check': 'status',
        'capabilities': {
            'code_editing': True,
            'ai_completion': True,
            'chat_interface': True,
            'terminal_integration': True,
            'file_management': True
        },
        'environment': {
            'CURSOR_HEADLESS': 'true'
        }
    },
    'continue': {
        'display_name': 'Continue',
        'type': 'tool',
        'port': 'auto',
        'description': 'Open-source AI code assistant',
        'executable': 'continue',
        'launch_args': ['--headless', '--socket-mode'],
        'health_check': 'ping',
        'capabilities': {
            'code_assistance': True,
            'context_aware': True,
            'multi_model': True,
            'custom_models': True,
            'embeddings': True
        },
        'environment': {
            'CONTINUE_HEADLESS': 'true'
        }
    }
}


@architecture_decision(
    title="CI Tool Registry Pattern",
    description="Centralized registry for all CI tool configurations and lifecycle",
    rationale="Single source of truth for tool discovery, configuration, and state persistence",
    alternatives_considered=["Individual tool configs", "Database storage", "Service discovery"],
    impacts=["tool_management", "persistence", "multi_instance_support"],
    decided_by="Casey",
    decision_date="2025-08-02"
)
@state_checkpoint(
    title="CI Tool Registry State",
    description="Persistent registry of tool configurations and custom definitions",
    state_type="persistent",
    persistence=True,
    consistency_requirements="Thread-safe access, atomic updates",
    recovery_strategy="Reload from disk on startup, merge with built-ins"
)
@api_contract(
    title="CI Tool Registry API",
    endpoint="/api/tools",
    methods=["GET", "POST"],
    description="Registry for CI tool configurations and status"
)
class CIToolRegistry:
    """
    Central registry for CI tools.
    
    Manages tool configurations, tracks running instances,
    and provides discovery services.
    """
    
    def __init__(self):
        """Initialize the registry."""
        self.logger = logging.getLogger("ci_tools.registry")
        self.tools = {}
        self.running_tools = {}
        self.adapters = {}
        
        # Initialize with defaults if needed, then load from file
        self._initialize_tools()
    
    @state_checkpoint(
        title="Get Tools",
        description="Get all registered CI tools",
        state_type="registry",
        state_key="tools"
    )
    def get_tools(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all registered CI tools.
        
        Returns:
            Dictionary of tool configurations
        """
        return self.tools.copy()
    
    def get_tool(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool configuration or None
        """
        return self.tools.get(tool_name)
    
    def register_tool(self, tool_name: str, config: Dict[str, Any]) -> bool:
        """
        Register a new CI tool.
        
        Args:
            tool_name: Unique tool identifier
            config: Tool configuration
            
        Returns:
            True if registered successfully
        """
        if tool_name in self.tools:
            self.logger.warning(f"Tool {tool_name} already registered")
            return False
        
        # Validate configuration
        required_fields = ['display_name', 'type', 'port', 'description', 'executable']
        for field in required_fields:
            if field not in config:
                self.logger.error(f"Missing required field: {field}")
                return False
        
        # Ensure type is 'tool'
        config['type'] = 'tool'
        
        # Register
        self.tools[tool_name] = config
        self.logger.info(f"Registered tool: {tool_name}")
        
        # Save all tools
        self._save_tools()
        
        return True
    
    def unregister_tool(self, tool_name: str) -> bool:
        """
        Unregister a CI tool.
        
        Args:
            tool_name: Tool to unregister
            
        Returns:
            True if unregistered successfully
        """
        if tool_name not in self.tools:
            return False
        
        # All tools can now be unregistered since they're all in config
        del self.tools[tool_name]
        self._save_tools()
        
        return True
    
    def mark_running(self, tool_name: str, adapter: Any, pid: int):
        """
        Mark a tool as running.
        
        Args:
            tool_name: Tool name
            adapter: Tool adapter instance
            pid: Process ID
        """
        self.running_tools[tool_name] = {
            'adapter': adapter,
            'pid': pid,
            'start_time': time.time()
        }
        self.adapters[tool_name] = adapter
    
    def mark_stopped(self, tool_name: str):
        """Mark a tool as stopped."""
        self.running_tools.pop(tool_name, None)
        self.adapters.pop(tool_name, None)
    
    def get_running_tools(self) -> List[str]:
        """Get list of running tools."""
        return list(self.running_tools.keys())
    
    def get_adapter(self, tool_name: str) -> Optional[Any]:
        """Get adapter for a running tool."""
        return self.adapters.get(tool_name)
    
    def get_tool_status(self, tool_name: str) -> Dict[str, Any]:
        """
        Get detailed status for a tool.
        
        Args:
            tool_name: Tool to check
            
        Returns:
            Status information
        """
        if tool_name not in self.tools:
            return {'error': 'Unknown tool'}
        
        status = {
            'name': tool_name,
            'config': self.tools[tool_name],
            'running': tool_name in self.running_tools
        }
        
        if status['running']:
            running_info = self.running_tools[tool_name]
            status['pid'] = running_info['pid']
            status['uptime'] = time.time() - running_info['start_time']
            
            # Get adapter status if available
            adapter = running_info.get('adapter')
            if adapter:
                status['adapter_status'] = adapter.get_status()
        
        return status
    
    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status for all tools."""
        return {
            tool_name: self.get_tool_status(tool_name)
            for tool_name in self.tools
        }
    
    def find_available_port(self, start_port: int = 8400) -> int:
        """
        Find an available port for a new tool.
        
        Always uses dynamic allocation.
        
        Args:
            start_port: Port to start searching from (ignored for dynamic)
            
        Returns:
            Available port number
        """
        # Always use dynamic allocation
        return self._allocate_dynamic_port()
    
    def _allocate_dynamic_port(self) -> int:
        """Allocate a dynamic port."""
        import socket
        from shared.env import TektonEnviron
        
        # Get port range from config
        port_range = TektonEnviron.get('CI_TOOLS_PORT_RANGE', '50000-60000')
        try:
            min_port, max_port = map(int, port_range.split('-'))
        except:
            min_port, max_port = 50000, 60000
        
        # Try to find an available port in the range
        for _ in range(100):  # Try up to 100 times
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', 0))
                port = s.getsockname()[1]
                
                # Check if in desired range
                if min_port <= port <= max_port:
                    return port
        
        # Fallback: use any available port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]
    
    def _initialize_tools(self):
        """Initialize tools from config file, creating defaults if needed."""
        try:
            import os
            from shared.env import TektonEnviron
            
            tekton_root = TektonEnviron.get('TEKTON_ROOT')
            if not tekton_root:
                return
            
            tools_dir = Path(tekton_root) / '.tekton' / 'ci_tools'
            tools_dir.mkdir(parents=True, exist_ok=True)
            
            tools_file = tools_dir / 'tools.json'
            
            if tools_file.exists():
                # Load existing tools
                with open(tools_file, 'r') as f:
                    self.tools = json.load(f)
                    self.logger.info(f"Loaded {len(self.tools)} tools from config")
            else:
                # First run - write defaults to file
                self.tools = DEFAULT_TOOLS_CONFIG.copy()
                with open(tools_file, 'w') as f:
                    json.dump(self.tools, f, indent=2)
                    self.logger.info(f"Created tools config with {len(self.tools)} default tools")
                    
        except Exception as e:
            self.logger.error(f"Failed to initialize tools: {e}")
            # Fall back to defaults in memory
            self.tools = DEFAULT_TOOLS_CONFIG.copy()
    
    def _save_tools(self):
        """Save all tool configurations."""
        try:
            import os
            from shared.env import TektonEnviron
            
            tekton_root = TektonEnviron.get('TEKTON_ROOT')
            if not tekton_root:
                return
            
            tools_dir = Path(tekton_root) / '.tekton' / 'ci_tools'
            tools_dir.mkdir(parents=True, exist_ok=True)
            
            tools_file = tools_dir / 'tools.json'
            with open(tools_file, 'w') as f:
                json.dump(self.tools, f, indent=2)
                self.logger.info(f"Saved {len(self.tools)} tools to config")
                    
        except Exception as e:
            self.logger.error(f"Failed to save tools: {e}")


# Global registry instance
import time
_registry = None

def get_registry() -> CIToolRegistry:
    """Get the global CI tool registry instance."""
    global _registry
    if _registry is None:
        _registry = CIToolRegistry()
    return _registry