# MCP Server CLI Usage Examples

This document provides examples of how to use the MCP Server CLI commands once implemented.

## Searching for MCP Servers

Search for MCP servers by keyword:

```bash
ergon mcp search file
```

Search for MCP servers with specific capabilities:

```bash
ergon mcp search --capability=filesystem,read,write
```

Search for Python-based MCP servers:

```bash
ergon mcp search --type=python
```

Get detailed information about a specific server:

```bash
ergon mcp info @modelcontextprotocol/server-filesystem
```

List available versions:

```bash
ergon mcp versions @modelcontextprotocol/server-filesystem
```

## Installing MCP Servers

Install a specific MCP server:

```bash
ergon mcp install @modelcontextprotocol/server-filesystem
```

Install a specific version:

```bash
ergon mcp install @modelcontextprotocol/server-filesystem@0.6.2
```

Install with specific options:

```bash
ergon mcp install @modelcontextprotocol/server-filesystem --option directories=/path/to/allow
```

Verify an installation:

```bash
ergon mcp verify @modelcontextprotocol/server-filesystem
```

## Managing Installed Servers

List all installed MCP servers:

```bash
ergon mcp list
```

Get details about an installed server:

```bash
ergon mcp status @modelcontextprotocol/server-filesystem
```

Update a server to the latest version:

```bash
ergon mcp update @modelcontextprotocol/server-filesystem
```

Uninstall a server:

```bash
ergon mcp uninstall @modelcontextprotocol/server-filesystem
```

## Configuring MCP Servers

View current configuration:

```bash
ergon mcp config @modelcontextprotocol/server-filesystem
```

Set a configuration option:

```bash
ergon mcp config @modelcontextprotocol/server-filesystem --set directories=/path/to/allow
```

Reset configuration to defaults:

```bash
ergon mcp config @modelcontextprotocol/server-filesystem --reset
```

Apply a configuration file:

```bash
ergon mcp config @modelcontextprotocol/server-filesystem --apply /path/to/config.json
```

## Testing MCP Servers

Test if a server is working correctly:

```bash
ergon mcp test @modelcontextprotocol/server-filesystem
```

Benchmark a server:

```bash
ergon mcp benchmark @modelcontextprotocol/server-filesystem
```

## Integration with Ergon

Register an installed server with Ergon:

```bash
ergon mcp register @modelcontextprotocol/server-filesystem
```

View registered servers:

```bash
ergon mcp registered
```

Unregister a server:

```bash
ergon mcp unregister @modelcontextprotocol/server-filesystem
```

## Cache Management

View cached server information:

```bash
ergon mcp cache list
```

Clear the cache:

```bash
ergon mcp cache clear
```

Update the cache:

```bash
ergon mcp cache update
```

## Advanced Usage

Create a multi-server configuration:

```bash
ergon mcp compose create mcp-compose.yml
```

Apply a multi-server configuration:

```bash
ergon mcp compose apply mcp-compose.yml
```

Export server metadata:

```bash
ergon mcp export @modelcontextprotocol/server-filesystem > metadata.json
```

Import server metadata:

```bash
ergon mcp import metadata.json
```