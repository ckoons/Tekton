# MCP Discovery Service

## Introduction

The MCP Discovery Service is a core component of the MCP Server Discovery and Integration capability. It provides a unified interface for searching and discovering Model Context Protocol (MCP) servers across multiple sources, including NPM, PyPI, GitHub, and potentially custom registries.

## Architecture

The Discovery Service uses a modular, extensible architecture with the following key components:

1. **Registry Sources**: Adapters for different package registries and repositories
2. **Metadata Schema**: Standardized representation of MCP server metadata
3. **Caching System**: Multi-level caching for improved performance
4. **Search Engine**: Unified search interface across all sources

```
┌──────────────────────────────────────────────────┐
│             MCP Discovery Service                │
└───────────────────┬──────────────────────────────┘
                    │
        ┌───────────┴──────────────┐
        │                          │
┌───────▼────────┐        ┌────────▼────────┐
│ Registry Layer │        │  Caching Layer  │
└───────┬────────┘        └─────────────────┘
        │
┌───────┴────────────────────────────────┐
│                                        │
┌────▼─────┐   ┌────▼─────┐   ┌──────▼───────┐
│   NPM    │   │   PyPI   │   │    GitHub    │
│ Registry │   │ Registry │   │   Registry   │
└──────────┘   └──────────┘   └──────────────┘
```

## Registry Sources

The Discovery Service supports the following registry sources:

### NPM Registry

The NPM Registry adapter searches for MCP servers in the NPM package registry. It identifies MCP servers by:

- Package name prefixes (`@modelcontextprotocol/server-*`)
- Keywords and tags in package metadata
- Presence of MCP-specific files and configurations

### PyPI Registry

The PyPI Registry adapter searches for MCP servers in the Python Package Index. It identifies MCP servers by:

- Package name prefixes (`mcp-server-*`)
- Keywords and classifiers in package metadata
- Presence of MCP-specific entry points

### GitHub Registry

The GitHub Registry adapter searches for MCP servers in GitHub repositories. It identifies MCP servers by:

- Repository topics and tags
- README content and metadata
- Presence of MCP-specific files and configurations

### Custom Registries

The Discovery Service also supports custom registries through a plugin architecture. Custom registry adapters must implement the `RegistrySource` interface.

## Metadata Schema

The Discovery Service uses a standardized metadata schema to represent MCP servers:

```python
class MCPServerMetadata:
    """Metadata for an MCP server."""
    
    name: str
    description: str
    package_name: str
    source: str
    latest_version: str
    versions: List[str]
    homepage: Optional[str]
    repository: Optional[str]
    license: Optional[str]
    author: Optional[str]
    installation_type: str  # "python", "node", "docker", etc.
    capabilities: List[str]
    tags: List[str]
    requirements: Dict[str, Any]
    configuration_schema: Optional[Dict[str, Any]]
    metadata: Dict[str, Any]  # Additional metadata
```

## Caching System

The Discovery Service uses a multi-level caching system to improve performance and reduce dependency on external APIs:

1. **Memory Cache**: In-memory cache for the current session
2. **Disk Cache**: Persistent cache between sessions
3. **Time-Based Invalidation**: Cache invalidation based on age
4. **Event-Based Invalidation**: Cache invalidation based on events (e.g., package updates)

## Search Capabilities

The Discovery Service provides several search methods:

### Text Search

Search for MCP servers by free-text query:

```python
servers = discovery_service.search("file")
```

### Capability Search

Search for MCP servers by capability:

```python
servers = discovery_service.search("", filters={"capability": "filesystem"})
```

### Tag Search

Search for MCP servers by tag:

```python
servers = discovery_service.search("", filters={"tag": "file"})
```

### Combined Search

Combine multiple search criteria:

```python
servers = discovery_service.search("file", filters={
    "capability": "filesystem",
    "installation_type": "node"
})
```

## Detailed Server Information

Get detailed metadata for a specific server:

```python
metadata = discovery_service.get_server_metadata("@modelcontextprotocol/server-filesystem")
```

## Version Information

Get available versions for a specific server:

```python
versions = discovery_service.get_server_versions("@modelcontextprotocol/server-filesystem")
```

## Configuration

The Discovery Service can be configured with the following options:

```python
discovery_service = MCPDiscoveryService(
    registry_sources=[
        NPMRegistrySource(),
        PyPIRegistrySource(),
        GitHubRegistrySource()
    ],
    cache_manager=CacheManager(
        memory_cache_size=100,
        disk_cache_path="/path/to/cache",
        cache_ttl=3600  # 1 hour
    ),
    search_limit=50,
    timeout=30  # seconds
)
```

## Error Handling

The Discovery Service provides robust error handling for registry API failures, network issues, and other errors:

```python
try:
    servers = discovery_service.search("file")
except RegistryConnectionError as e:
    print(f"Connection error: {e}")
except RegistryRateLimitError as e:
    print(f"Rate limit exceeded: {e}")
except DiscoveryError as e:
    print(f"Discovery error: {e}")
```

## Examples

### Basic Search

```python
from ergon.core.mcp_discovery import MCPDiscoveryService

# Create the discovery service
discovery_service = MCPDiscoveryService()

# Search for MCP servers by capability
servers = discovery_service.search("file", filters={"capability": "filesystem"})

# Print results
for server in servers:
    print(f"Server: {server.name}")
    print(f"  Description: {server.description}")
    print(f"  Source: {server.source}")
    print(f"  Version: {server.latest_version}")
    print(f"  Capabilities: {', '.join(server.capabilities)}")
```

### Get Server Metadata

```python
# Get detailed metadata for a specific server
metadata = discovery_service.get_server_metadata("@modelcontextprotocol/server-filesystem")

print(f"Server: {metadata.name}")
print(f"Package: {metadata.package_name}")
print(f"Description: {metadata.description}")
print(f"Latest version: {metadata.latest_version}")
print(f"All versions: {', '.join(metadata.versions)}")
print(f"Installation type: {metadata.installation_type}")
```

### Custom Registry Source

```python
from ergon.core.mcp_discovery.registry.base import RegistrySource

class CustomRegistrySource(RegistrySource):
    """Custom registry source for MCP servers."""
    
    def search(self, query, filters=None, limit=None):
        """Search for MCP servers matching the query and filters."""
        # Implementation
        
    def get_metadata(self, server_id):
        """Get detailed metadata for a specific MCP server."""
        # Implementation
        
    def get_versions(self, server_id):
        """Get available versions for a specific MCP server."""
        # Implementation

# Add custom registry to discovery service
discovery_service = MCPDiscoveryService(
    registry_sources=[
        NPMRegistrySource(),
        PyPIRegistrySource(),
        GitHubRegistrySource(),
        CustomRegistrySource()
    ]
)
```

## Best Practices

1. **Use Specific Searches**: When possible, use specific search criteria to narrow results
2. **Cache Results**: For performance-critical applications, consider additional caching
3. **Handle Registry Failures**: Be prepared for registry API failures and implement retries
4. **Validate Metadata**: Validate metadata before using it for installation or other operations
5. **Respect Rate Limits**: Be mindful of registry API rate limits

## Troubleshooting

### Common Issues

1. **Registry Connection Failures**
   - Check network connectivity
   - Verify registry API status
   - Check for rate limiting

2. **No Results Found**
   - Verify search terms
   - Try alternative search strategies
   - Check if server is available in supported registries

3. **Inconsistent Metadata**
   - Different registries may have different metadata
   - Consider using a preferred registry for certain servers
   - Report inconsistencies to server authors

### Logging

The Discovery Service provides detailed logging:

```python
import logging
logging.getLogger("ergon.core.mcp_discovery").setLevel(logging.DEBUG)
```

## Future Enhancements

1. **Additional Registry Sources**: Support for more package registries
2. **Enhanced Search**: More advanced search capabilities (semantic search, etc.)
3. **Federated Registry**: Support for a centralized MCP server registry
4. **Reputation System**: Community-driven ratings and reviews
5. **Automated Analysis**: Security and quality analysis of discovered servers