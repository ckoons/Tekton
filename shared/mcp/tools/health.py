"""Health check tool implementation."""

from typing import Dict, Any, Optional
import time

from ..base.tool import MCPTool


class HealthCheckTool(MCPTool):
    """Tool for checking component health status."""
    
    name = "health_check"
    description = "Check the health status of the component"
    tags = ["system", "monitoring", "health"]
    
    def __init__(self, component_name: str, health_check_func: Optional[callable] = None):
        """
        Initialize the health check tool.
        
        Args:
            component_name: Name of the component
            health_check_func: Optional custom health check function
        """
        self.component_name = component_name
        self.health_check_func = health_check_func
        self.start_time = time.time()
        super().__init__()
    
    async def execute(self, detailed: bool = False) -> Dict[str, Any]:
        """
        Execute health check.
        
        Args:
            detailed: Whether to include detailed health information
            
        Returns:
            Health status information
        """
        # Basic health info
        health_info = {
            "status": "healthy",
            "component": self.component_name,
            "timestamp": time.time(),
            "uptime": time.time() - self.start_time
        }
        
        # Run custom health check if provided
        if self.health_check_func:
            try:
                if asyncio.iscoroutinefunction(self.health_check_func):
                    custom_health = await self.health_check_func()
                else:
                    custom_health = self.health_check_func()
                
                if isinstance(custom_health, dict):
                    health_info.update(custom_health)
                elif isinstance(custom_health, bool):
                    health_info["status"] = "healthy" if custom_health else "unhealthy"
            except Exception as e:
                health_info["status"] = "unhealthy"
                health_info["error"] = str(e)
        
        # Add detailed info if requested
        if detailed:
            health_info["details"] = {
                "start_time": self.start_time,
                "current_time": time.time(),
                "uptime_readable": self._format_uptime(health_info["uptime"])
            }
        
        return health_info
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable format."""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        parts.append(f"{secs}s")
        
        return " ".join(parts)
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Get the input schema for the health check tool."""
        return {
            "type": "object",
            "properties": {
                "detailed": {
                    "type": "boolean",
                    "description": "Whether to include detailed health information",
                    "default": False
                }
            },
            "required": []
        }


# Import asyncio for async checks
import asyncio