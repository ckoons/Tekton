"""
MCP Tool Discovery for Ergon v2.

This module implements tool discovery through MCP (Model Context Protocol),
allowing Ergon to discover, catalog, and utilize tools from other Tekton
components and external MCP servers.
"""
import asyncio
import json
import logging
import os
from shared.env import TektonEnviron
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from dataclasses import dataclass, field

# Import landmarks with fallback
try:
    from landmarks import integration_point, state_checkpoint, performance_boundary
except ImportError:
    # Create no-op decorators if landmarks module is not available
    def state_checkpoint(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    def integration_point(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    def performance_boundary(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

logger = logging.getLogger(__name__)


@dataclass
class MCPTool:
    """Represents a discovered MCP tool."""
    name: str
    description: str
    provider: str  # Component/server providing the tool
    version: str
    capabilities: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    extra_metadata: Dict[str, Any] = field(default_factory=dict)
    discovered_at: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    available: bool = True


@dataclass
class MCPServer:
    """Represents an MCP server/provider."""
    name: str
    url: str
    component: str  # Tekton component name
    capabilities: List[str] = field(default_factory=list)
    tools: Dict[str, MCPTool] = field(default_factory=dict)
    extra_metadata: Dict[str, Any] = field(default_factory=dict)
    connected: bool = False
    last_ping: Optional[datetime] = None


@integration_point(
    title="MCP Tool Discovery",
    target_component="All MCP-enabled components",
    protocol="MCP protocol over HTTP/WebSocket",
    data_flow="Ergon -> MCP servers -> Tool catalog"
)
@state_checkpoint(
    title="Tool Discovery State",
    state_type="persistent",
    persistence=True,
    consistency_requirements="Tool catalog must be consistent across restarts",
    recovery_strategy="Re-discover tools on startup, merge with persisted catalog"
)
@performance_boundary(
    title="Tool Discovery Performance",
    sla="<2s per server discovery, 50 tools/s processing",
    metrics={"cache_ttl": "5m", "max_concurrent_discoveries": "10"},
    optimization_notes="Parallel discovery, caching, background refresh"
)
class MCPToolDiscovery:
    """
    Discovers and catalogs MCP tools from Tekton components.
    
    Features:
    - Auto-discovery of MCP servers
    - Tool capability analysis
    - Tool compatibility checking
    - Tool usage tracking
    - Tool recommendation
    """
    
    def __init__(self, ergon_component):
        self.ergon = ergon_component
        self.servers: Dict[str, MCPServer] = {}
        self.tools: Dict[str, MCPTool] = {}
        self.discovery_running = False
        self._discovery_task = None
        
        # Import shared URLs
        try:
            from shared.urls import (
                hermes_url, terma_url, athena_url, metis_url, 
                prometheus_url, harmonia_url, synthesis_url, 
                telos_url, rhetor_url, apollo_url, sophia_url
            )
            
            # Known Tekton MCP servers with dynamic URLs
            self.known_servers = {
                "hermes": {"url": hermes_url(""), "component": "hermes"},
                "terma": {"url": terma_url(""), "component": "terma"},
                "athena": {"url": athena_url(""), "component": "athena"},
                "metis": {"url": metis_url(""), "component": "metis"},
                "prometheus": {"url": prometheus_url(""), "component": "prometheus"},
                "harmonia": {"url": harmonia_url(""), "component": "harmonia"},
                "synthesis": {"url": synthesis_url(""), "component": "synthesis"},
                "telos": {"url": telos_url(""), "component": "telos"},
                "rhetor": {"url": rhetor_url(""), "component": "rhetor"},
                "apollo": {"url": apollo_url(""), "component": "apollo"},
                "sophia": {"url": sophia_url(""), "component": "sophia"},
            }
        except ImportError:
            # Fallback to environment-aware defaults if shared.urls not available
            self.known_servers = self._get_fallback_servers()
    
    def _get_fallback_servers(self) -> Dict[str, Dict[str, str]]:
        """Get fallback server URLs using environment variables."""
        # Determine base port range from environment
        base_port = 8000  # Default Tekton port range
        
        # Check for environment-specific ports
        hermes_port = TektonEnviron.get("HERMES_PORT")
        if hermes_port:
            # If we have a specific port, determine the base range
            port_num = int(hermes_port)
            base_port = (port_num // 100) * 100  # Get the base (8000 or 8100)
        
        # Define component port offsets
        port_offsets = {
            "hermes": 1,
            "terma": 15,  # Note: Terma actually uses port 15
            "athena": 5,
            "metis": 16,
            "prometheus": 6,
            "harmonia": 18,
            "synthesis": 19,
            "telos": 21,
            "rhetor": 3,
            "apollo": 23,
            "sophia": 26,
        }
        
        # Build server URLs
        servers = {}
        for component, offset in port_offsets.items():
            port = base_port + offset
            # Check for component-specific port override
            env_port = TektonEnviron.get(f"{component.upper()}_PORT")
            if env_port:
                port = int(env_port)
            
            servers[component] = {
                "url": f"http://localhost:{port}",
                "component": component
            }
        
        return servers
        
    async def start_discovery(self):
        """Start the tool discovery process."""
        if self.discovery_running:
            logger.warning("Tool discovery already running")
            return
            
        self.discovery_running = True
        self._discovery_task = asyncio.create_task(self._discovery_loop())
        logger.info("MCP tool discovery started")
        
    async def stop_discovery(self):
        """Stop the tool discovery process."""
        self.discovery_running = False
        if self._discovery_task:
            self._discovery_task.cancel()
            try:
                await self._discovery_task
            except asyncio.CancelledError:
                pass
        logger.info("MCP tool discovery stopped")
        
    async def _discovery_loop(self):
        """Main discovery loop."""
        while self.discovery_running:
            try:
                # Discover tools from all known servers
                await self._discover_all_servers()
                
                # Wait before next discovery round
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"Error in discovery loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
                
    async def _discover_all_servers(self):
        """Discover tools from all known servers."""
        tasks = []
        for server_name, server_info in self.known_servers.items():
            task = asyncio.create_task(
                self._discover_server(server_name, server_info)
            )
            tasks.append(task)
            
        # Wait for all discoveries to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Log results
        successful = sum(1 for r in results if not isinstance(r, Exception))
        logger.info(f"Discovered tools from {successful}/{len(tasks)} servers")
        
    async def _discover_server(self, server_name: str, server_info: Dict[str, Any]):
        """Discover tools from a specific MCP server."""
        try:
            # Create/update server record
            if server_name not in self.servers:
                self.servers[server_name] = MCPServer(
                    name=server_name,
                    url=server_info["url"],
                    component=server_info["component"]
                )
                
            server = self.servers[server_name]
            
            # Try to connect and get capabilities
            # TODO: Implement actual MCP protocol communication
            # For now, mock the discovery
            await self._mock_discover_tools(server)
            
            server.connected = True
            server.last_ping = datetime.now()
            
            # Update tool catalog
            for tool_name, tool in server.tools.items():
                full_name = f"{server_name}.{tool_name}"
                self.tools[full_name] = tool
                
            logger.info(f"Discovered {len(server.tools)} tools from {server_name}")
            
        except Exception as e:
            logger.error(f"Failed to discover tools from {server_name}: {e}")
            if server_name in self.servers:
                self.servers[server_name].connected = False
                
    async def _mock_discover_tools(self, server: MCPServer):
        """Mock tool discovery for development."""
        # Mock tools based on component
        mock_tools = {
            "hermes": [
                MCPTool(
                    name="send_message",
                    description="Send message through Hermes",
                    provider=server.name,
                    version="1.0",
                    capabilities=["messaging", "routing"],
                    parameters={"to": "string", "message": "string"}
                ),
                MCPTool(
                    name="register_component",
                    description="Register component with Hermes",
                    provider=server.name,
                    version="1.0",
                    capabilities=["registration"],
                    parameters={"component": "string", "capabilities": "array"}
                )
            ],
            "terma": [
                MCPTool(
                    name="execute_command",
                    description="Execute terminal command",
                    provider=server.name,
                    version="1.0",
                    capabilities=["terminal", "execution"],
                    parameters={"command": "string", "directory": "string"}
                ),
                MCPTool(
                    name="read_file",
                    description="Read file contents",
                    provider=server.name,
                    version="1.0",
                    capabilities=["filesystem", "read"],
                    parameters={"path": "string"}
                )
            ],
            "athena": [
                MCPTool(
                    name="query_knowledge",
                    description="Query knowledge graph",
                    provider=server.name,
                    version="1.0",
                    capabilities=["knowledge", "query"],
                    parameters={"query": "string", "context": "object"}
                ),
                MCPTool(
                    name="add_knowledge",
                    description="Add to knowledge graph",
                    provider=server.name,
                    version="1.0",
                    capabilities=["knowledge", "write"],
                    parameters={"entity": "object", "relationships": "array"}
                )
            ]
        }
        
        # Add mock tools to server
        tools = mock_tools.get(server.component, [])
        for tool in tools:
            server.tools[tool.name] = tool
            
    def get_tools_by_capability(self, capability: str) -> List[MCPTool]:
        """Get all tools with a specific capability."""
        matching_tools = []
        for tool in self.tools.values():
            if capability in tool.capabilities:
                matching_tools.append(tool)
        return matching_tools
        
    def get_tools_by_provider(self, provider: str) -> List[MCPTool]:
        """Get all tools from a specific provider."""
        return [t for t in self.tools.values() if t.provider == provider]
        
    def search_tools(self, query: str) -> List[MCPTool]:
        """Search tools by name or description."""
        query_lower = query.lower()
        matching_tools = []
        
        for tool in self.tools.values():
            if (query_lower in tool.name.lower() or 
                query_lower in tool.description.lower()):
                matching_tools.append(tool)
                
        return matching_tools
        
    def get_tool_recommendations(self, task_type: str) -> List[MCPTool]:
        """Get tool recommendations for a specific task type."""
        # Map task types to capabilities
        task_capability_map = {
            "file_operations": ["filesystem", "read", "write"],
            "code_execution": ["terminal", "execution"],
            "knowledge_query": ["knowledge", "query"],
            "messaging": ["messaging", "routing"],
            "data_analysis": ["analysis", "statistics"],
            "workflow": ["workflow", "orchestration"]
        }
        
        capabilities = task_capability_map.get(task_type, [])
        recommendations = []
        
        for capability in capabilities:
            recommendations.extend(self.get_tools_by_capability(capability))
            
        # Remove duplicates
        seen = set()
        unique_recommendations = []
        for tool in recommendations:
            tool_id = f"{tool.provider}.{tool.name}"
            if tool_id not in seen:
                seen.add(tool_id)
                unique_recommendations.append(tool)
                
        return unique_recommendations
        
    async def refresh_tool(self, tool_name: str):
        """Refresh a specific tool's information."""
        if tool_name not in self.tools:
            logger.warning(f"Tool {tool_name} not found")
            return
            
        tool = self.tools[tool_name]
        server_name = tool.provider
        
        if server_name in self.servers:
            await self._discover_server(
                server_name, 
                {"url": self.servers[server_name].url, 
                 "component": self.servers[server_name].component}
            )
            
    def refresh_server_urls(self):
        """Refresh server URLs from environment in case they changed."""
        try:
            from shared.urls import (
                hermes_url, terma_url, athena_url, metis_url, 
                prometheus_url, harmonia_url, synthesis_url, 
                telos_url, rhetor_url, apollo_url, sophia_url
            )
            
            # Update with fresh URLs
            self.known_servers = {
                "hermes": {"url": hermes_url(""), "component": "hermes"},
                "terma": {"url": terma_url(""), "component": "terma"},
                "athena": {"url": athena_url(""), "component": "athena"},
                "metis": {"url": metis_url(""), "component": "metis"},
                "prometheus": {"url": prometheus_url(""), "component": "prometheus"},
                "harmonia": {"url": harmonia_url(""), "component": "harmonia"},
                "synthesis": {"url": synthesis_url(""), "component": "synthesis"},
                "telos": {"url": telos_url(""), "component": "telos"},
                "rhetor": {"url": rhetor_url(""), "component": "rhetor"},
                "apollo": {"url": apollo_url(""), "component": "apollo"},
                "sophia": {"url": sophia_url(""), "component": "sophia"},
            }
        except ImportError:
            # Fallback to environment-aware defaults
            self.known_servers = self._get_fallback_servers()
            
        logger.info(f"Refreshed server URLs for {len(self.known_servers)} servers")
    
    def get_discovery_status(self) -> Dict[str, Any]:
        """Get current discovery status."""
        connected_servers = sum(1 for s in self.servers.values() if s.connected)
        total_tools = len(self.tools)
        available_tools = sum(1 for t in self.tools.values() if t.available)
        
        return {
            "discovery_running": self.discovery_running,
            "servers": {
                "total": len(self.servers),
                "connected": connected_servers
            },
            "tools": {
                "total": total_tools,
                "available": available_tools
            },
            "last_discovery": max(
                (s.last_ping for s in self.servers.values() if s.last_ping),
                default=None
            )
        }