"""
Example code for using the MCP Discovery Service.

This file demonstrates how to use the MCP Discovery Service to search for and
interact with MCP servers across multiple registry sources.
"""

# First, create a discovery service with default configuration
from ergon.core.mcp_discovery import MCPDiscoveryService

# Create the discovery service
discovery_service = MCPDiscoveryService()

# Search for MCP servers by capability
print("Searching for MCP servers with 'file' capability...")
file_servers = discovery_service.search("file", 
                                      filters={"capability": "filesystem"})

for server in file_servers:
    print(f"Found server: {server.name}")
    print(f"  Description: {server.description}")
    print(f"  Source: {server.source}")
    print(f"  Version: {server.latest_version}")
    print(f"  Capabilities: {', '.join(server.capabilities)}")
    print("")

# Get detailed metadata for a specific server
print("Getting detailed metadata for filesystem server...")
filesystem_server = discovery_service.get_server_metadata("@modelcontextprotocol/server-filesystem")

print(f"Server: {filesystem_server.name}")
print(f"Package: {filesystem_server.package_name}")
print(f"Source: {filesystem_server.source}")
print(f"Description: {filesystem_server.description}")
print(f"Latest version: {filesystem_server.latest_version}")
print(f"All versions: {', '.join(filesystem_server.versions)}")
print(f"Homepage: {filesystem_server.homepage}")
print(f"Repository: {filesystem_server.repository}")
print(f"License: {filesystem_server.license}")
print(f"Installation type: {filesystem_server.installation_type}")
print("")

# Now create an installation service and install the server
from ergon.core.mcp_installation import MCPInstallationService

# Create the installation service with our discovery service
installation_service = MCPInstallationService(discovery_service)

# Check if the server meets installation requirements
print("Checking installation requirements...")
requirements_met = installation_service.check_requirements("@modelcontextprotocol/server-filesystem")

if requirements_met:
    print("Requirements met, proceeding with installation...")
    # Install the server
    install_result = installation_service.install_server(
        "@modelcontextprotocol/server-filesystem",
        options={"directories": ["/path/to/allow"]}
    )
    
    if install_result.success:
        print(f"Server installed successfully at {install_result.installation_path}")
        print(f"Command to run: {install_result.command}")
        print(f"Version: {install_result.version}")
    else:
        print(f"Installation failed: {install_result.error}")
else:
    print("Requirements not met, cannot install")

# List all installed servers
print("\nListing installed MCP servers...")
installed_servers = installation_service.get_installed_servers()

for server in installed_servers:
    print(f"Installed server: {server.name}")
    print(f"  Version: {server.installed_version}")
    print(f"  Installation path: {server.installation_path}")
    print(f"  Configuration: {server.configuration}")
    print("")

# Now, register the server with Ergon
from ergon.core.repository.mcp_server_integration import MCPServerIntegration
from ergon.core.repository.repository import RepositoryService

# Create the repository service
repo_service = RepositoryService()

# Create the integration service
integration_service = MCPServerIntegration(repo_service, installation_service)

# Register the installed server with Ergon
print("Registering server with Ergon...")
registration_result = integration_service.register_installed_server(
    "@modelcontextprotocol/server-filesystem"
)

if registration_result.success:
    print(f"Server registered with ID: {registration_result.component_id}")
    print(f"Registered capabilities: {', '.join(registration_result.capabilities)}")
else:
    print(f"Registration failed: {registration_result.error}")

# Now the MCP server is installed and registered with Ergon, making it available for use by CI models