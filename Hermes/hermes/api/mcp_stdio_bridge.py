#!/usr/bin/env python3
"""
MCP STDIO Bridge for Hermes

This script provides a stdio interface to Hermes' HTTP MCP API,
allowing Claude Desktop to communicate with Hermes using the MCP protocol.
"""

import asyncio
import json
import sys
import logging
import aiohttp
from typing import Dict, Any, Optional

# Add Tekton's shared directory to Python path
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
from shared.urls import tekton_url

# Configure logging to stderr so it doesn't interfere with stdio protocol
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)

HERMES_URL = tekton_url("hermes", "/api/mcp/v2")


class HermesMCPBridge:
    """Bridge between stdio MCP protocol and Hermes HTTP API."""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.request_id = 0
        
    async def start(self):
        """Start the bridge."""
        self.session = aiohttp.ClientSession()
        await self.run()
        
    async def stop(self):
        """Stop the bridge."""
        if self.session:
            await self.session.close()
            
    async def run(self):
        """Main loop to handle stdio communication."""
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)
        
        # Log startup
        logger.debug("Hermes MCP bridge started")
        
        while True:
            try:
                # Read a line from stdin
                line = await reader.readline()
                if not line:
                    break
                    
                # Parse JSON-RPC request
                try:
                    request = json.loads(line.decode())
                    logger.debug(f"Received request: {request.get('method', 'unknown')}")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON: {e}")
                    continue
                    
                # Handle the request
                response = await self.handle_request(request)
                
                # Send response
                if response:
                    sys.stdout.write(json.dumps(response) + '\n')
                    sys.stdout.flush()
                    logger.debug(f"Sent response for: {request.get('method', 'unknown')}")
                    
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a JSON-RPC request."""
        method = request.get("method", "")
        params = request.get("params", {})
        req_id = request.get("id")
        
        try:
            if method == "initialize":
                result = await self.initialize(params)
            elif method == "tools/list":
                result = await self.list_tools()
            elif method == "tools/call":
                result = await self.call_tool(params)
            elif method == "prompts/list":
                # Return empty prompts list
                result = {"prompts": []}
            elif method == "resources/list":
                # Return empty resources list
                result = {"resources": []}
            elif method == "ping":
                result = {"pong": True}
            else:
                # Unknown method
                return {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    },
                    "id": req_id
                }
                
            return {
                "jsonrpc": "2.0",
                "result": result,
                "id": req_id
            }
            
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": str(e)
                },
                "id": req_id
            }
            
    async def initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize request."""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "prompts": {},
                "resources": {},
                "sampling": {}
            },
            "serverInfo": {
                "name": "hermes-mcp-bridge",
                "version": "1.0.0"
            }
        }
        
    async def list_tools(self) -> Dict[str, Any]:
        """List available tools from Hermes."""
        try:
            async with self.session.get(f"{HERMES_URL}/tools") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    
                    # Handle both list and dict responses
                    if isinstance(data, list):
                        tools = data
                    else:
                        tools = data.get("tools", [])
                    
                    # Convert Hermes tool format to MCP format
                    mcp_tools = []
                    for tool in tools:
                        mcp_tool = {
                            "name": tool.get("name", ""),
                            "description": tool.get("description", ""),
                            "inputSchema": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            }
                        }
                        
                        # Convert schema if available
                        if isinstance(tool, dict) and "schema" in tool and isinstance(tool["schema"], dict) and "parameters" in tool["schema"]:
                            params = tool["schema"]["parameters"]
                            if isinstance(params, dict):
                                for param_name, param_info in params.items():
                                    # Skip internal parameters
                                    if param_name in ["service_registry", "database_manager", "message_bus"]:
                                        continue
                                        
                                    if isinstance(param_info, dict):
                                        mcp_tool["inputSchema"]["properties"][param_name] = {
                                            "type": "string",  # Simplified type mapping
                                            "description": param_info.get("description", "")
                                        }
                                        
                                        if param_info.get("required", False):
                                            mcp_tool["inputSchema"]["required"].append(param_name)
                                    
                        mcp_tools.append(mcp_tool)
                        
                    return {"tools": mcp_tools}
                else:
                    raise Exception(f"Failed to get tools: {resp.status}")
                    
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            raise
            
    async def call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool through Hermes."""
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        
        try:
            # First, get the tool ID for this tool name
            async with self.session.get(f"{HERMES_URL}/tools") as resp:
                if resp.status == 200:
                    tools = await resp.json()
                    tool_id = None
                    
                    for tool in tools:
                        if tool.get("name") == tool_name:
                            tool_id = tool.get("id")
                            break
                            
                    if not tool_id:
                        raise Exception(f"Tool not found: {tool_name}")
                        
            # Execute the tool
            async with self.session.post(
                f"{HERMES_URL}/tools/{tool_id}/execute",
                json={"parameters": arguments}
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    
                    # Return the result in MCP format
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result.get("result", result), indent=2)
                            }
                        ]
                    }
                else:
                    error_text = await resp.text()
                    raise Exception(f"Tool execution failed: {error_text}")
                    
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            raise


async def main():
    """Main entry point."""
    bridge = HermesMCPBridge()
    try:
        await bridge.start()
    finally:
        await bridge.stop()


if __name__ == "__main__":
    asyncio.run(main())