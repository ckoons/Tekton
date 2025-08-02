"""
CI Tool Registry - Manages available CI tools and their configurations.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    from landmarks import api_contract, state_checkpoint
except ImportError:
    def api_contract(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def state_checkpoint(**kwargs):
        def decorator(func):
            return func
        return decorator


# CI Tools configuration
CI_TOOLS_CONFIG = {
    'claude-code': {
        'display_name': 'Claude Code',
        'type': 'tool',
        'port': 8400,
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
        'port': 8401,
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
        'port': 8402,
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
        self.tools = CI_TOOLS_CONFIG.copy()
        self.running_tools = {}
        self.adapters = {}
        
        # Load custom tools if available
        self._load_custom_tools()
    
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
        
        # Save to custom tools
        self._save_custom_tools()
        
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
        
        # Don't allow unregistering built-in tools
        if tool_name in CI_TOOLS_CONFIG:
            self.logger.error(f"Cannot unregister built-in tool: {tool_name}")
            return False
        
        del self.tools[tool_name]
        self._save_custom_tools()
        
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
        
        Args:
            start_port: Port to start searching from
            
        Returns:
            Available port number
        """
        used_ports = {config['port'] for config in self.tools.values()}
        
        port = start_port
        while port in used_ports:
            port += 1
        
        return port
    
    def _load_custom_tools(self):
        """Load custom tool configurations."""
        try:
            import os
            from shared.env import TektonEnviron
            
            tekton_root = TektonEnviron.get('TEKTON_ROOT')
            if not tekton_root:
                return
            
            custom_file = Path(tekton_root) / '.tekton' / 'ci_tools' / 'custom_tools.json'
            if custom_file.exists():
                with open(custom_file, 'r') as f:
                    custom_tools = json.load(f)
                    
                for tool_name, config in custom_tools.items():
                    if tool_name not in self.tools:
                        config['type'] = 'tool'  # Ensure correct type
                        self.tools[tool_name] = config
                        self.logger.info(f"Loaded custom tool: {tool_name}")
                        
        except Exception as e:
            self.logger.error(f"Failed to load custom tools: {e}")
    
    def _save_custom_tools(self):
        """Save custom tool configurations."""
        try:
            import os
            from shared.env import TektonEnviron
            
            tekton_root = TektonEnviron.get('TEKTON_ROOT')
            if not tekton_root:
                return
            
            # Get custom tools (not in default config)
            custom_tools = {
                name: config
                for name, config in self.tools.items()
                if name not in CI_TOOLS_CONFIG
            }
            
            if custom_tools:
                custom_dir = Path(tekton_root) / '.tekton' / 'ci_tools'
                custom_dir.mkdir(parents=True, exist_ok=True)
                
                custom_file = custom_dir / 'custom_tools.json'
                with open(custom_file, 'w') as f:
                    json.dump(custom_tools, f, indent=2)
                    
        except Exception as e:
            self.logger.error(f"Failed to save custom tools: {e}")


# Global registry instance
import time
_registry = None

def get_registry() -> CIToolRegistry:
    """Get the global CI tool registry instance."""
    global _registry
    if _registry is None:
        _registry = CIToolRegistry()
    return _registry