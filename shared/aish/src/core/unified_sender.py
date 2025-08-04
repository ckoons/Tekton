"""
Unified message sender for all CI types.
Handles Greek Chorus, Terminals, and Project CIs through their endpoints.
"""

import json
import urllib.request
import urllib.error
import urllib.parse
from typing import Optional

from registry.ci_registry import get_registry

# Import landmarks with fallback
try:
    from landmarks import (
        architecture_decision,
        api_contract,
        integration_point,
        performance_boundary
    )
except ImportError:
    # Define no-op decorators when landmarks not available
    def architecture_decision(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def api_contract(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def performance_boundary(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator


@architecture_decision(
    title="Unified CI Message Routing",
    description="Single function routes messages to any CI type based on configuration",
    rationale="Eliminates duplicate send code, enables federation, simplifies debugging",
    alternatives_considered=["Type-specific send methods", "Hard-coded routing logic"],
    impacts=["simplicity", "maintainability", "federation_readiness"],
    decided_by="Casey",
    decision_date="2025-01-25"
)
@integration_point(
    title="Universal CI Message Gateway",
    description="Routes messages to CIs based on their configured message_format",
    target_component="Multiple (Rhetor, Terma, Project CIs)",
    protocol="Configuration-driven",
    data_flow="send_to_ci → registry lookup → format-specific routing → target CI",
    integration_date="2025-01-25"
)
@performance_boundary(
    title="CI Message Routing",
    description="Routes messages with minimal overhead",
    sla="<10ms routing decision",
    optimization_notes="Registry cached in memory, format check is O(1)",
    measured_impact="Adds negligible latency to message delivery"
)
def send_to_ci(ci_name: str, message: str) -> bool:
    """
    Send a message to any CI using the unified registry.
    
    Args:
        ci_name: Name of the CI to send to
        message: Message to send
        
    Returns:
        bool: True if message was sent successfully
    """
    # Get CI info from registry
    registry = get_registry()
    ci = registry.get_by_name(ci_name)
    
    if not ci:
        print(f"CI '{ci_name}' not found in registry")
        return False
    
    # Get messaging configuration from registry
    message_format = ci.get('message_format')
    message_endpoint = ci.get('message_endpoint')
    
    # Build message payload based on format
    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
        
        if message_format == 'terma_route':
            # Terma terminal routing format
            from shared.urls import tekton_url
            from shared.env import TektonEnviron
            from datetime import datetime
            
            msg_data = {
                "from": {
                    "terma_id": TektonEnviron.get('TERMA_SESSION_ID', 'aish-direct'),
                    "name": TektonEnviron.get('TERMA_TERMINAL_NAME', 'aish')
                },
                "target": ci_name,
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "type": "chat"
            }
            
            # Use terma's endpoint
            url = tekton_url('terma', message_endpoint)
            data = json.dumps(msg_data).encode('utf-8')
            
        elif message_format == 'json_simple' and ci.get('type') == 'ai_specialist':
            # Direct AI specialist communication
            from shared.ai.simple_ai import ai_send_sync
            
            # Extract port from CI data or endpoint
            port = ci.get('port')
            if not port and 'endpoint' in ci:
                port = int(ci['endpoint'].split(':')[-1])
            
            # Use the name with -ai suffix for AI communication
            ai_name = f"{ci.get('base_name', ci_name)}-ai"
            
            try:
                response = ai_send_sync(ai_name, message, "localhost", port)
                # Print response for MCP server to capture
                print(response)
                # Update last output for coordination
                registry.update_ci_last_output(ci_name, response)
                return True
            except Exception as e:
                # Print error message as response so MCP can return it
                error_msg = f"Failed to connect to {ai_name} on port {port}: {str(e)}"
                print(error_msg)
                # Also log to stderr for debugging
                import sys
                print(f"Error sending to AI specialist {ai_name} on port {port}: {e}", file=sys.stderr)
                # Still return True so MCP captures the error message
                return True
                
        elif message_format == 'json_simple':
            # Simple JSON format for direct API calls
            msg_data = {"message": message}
            url = ci.get('endpoint') + message_endpoint
            data = json.dumps(msg_data).encode('utf-8')
            
        elif message_format == 'mcp':
            # MCP format for Apollo and similar services
            msg_data = {
                "content": {"message": message},
                "context": {}
            }
            url = ci.get('endpoint') + message_endpoint
            data = json.dumps(msg_data).encode('utf-8')
            
        elif message_format == 'json' and ci.get('type') == 'tool':
            # Socket-based CI tools
            return _send_to_tool(ci_name, message, ci)
            
        else:
            print(f"Unknown message format: {message_format}")
            return False
        
        # Send the message
        req = urllib.request.Request(
            url,
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            response_text = response.read()
            result = json.loads(response_text)
            
        # Capture output for Apollo-Rhetor coordination
        registry.update_ci_last_output(ci_name, response_text.decode('utf-8'))
            
        # Handle response based on format
        if message_format == 'terma_route':
            if result.get("success"):
                delivered = result.get("delivered_to", [])
                if delivered:
                    print(f"Message sent to: {', '.join(delivered)}")
                    return True
                else:
                    print("No terminals matched the target")
                    return False
            else:
                print(f"Failed: {result.get('error', 'Unknown error')}")
                return False
        elif message_format == 'mcp':
            # For MCP format
            if 'content' in result:
                content = result['content']
                if isinstance(content, dict):
                    if 'error' in content:
                        print(f"Error: {content['error']}")
                        return False
                    elif 'message' in content:
                        print(content['message'])
                    else:
                        print(json.dumps(content, indent=2))
                else:
                    print(content)
            else:
                print(json.dumps(result, indent=2))
            return True
        else:
            # For json_simple format
            if 'response' in result:
                print(result['response'])
            elif 'message' in result:
                print(result['message'])
            else:
                print(json.dumps(result, indent=2))
            return True
                
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Endpoint not found for {ci_name}")
        else:
            print(f"Error sending to {ci_name}: HTTP {e.code}")
        return False
    except Exception as e:
        print(f"Error sending to {ci_name}: {e}")
        return False


@integration_point(
    title="CI Tool Message Handler",
    description="Sends messages to socket-based CI tools",
    target_component="CI Tools",
    protocol="Socket Bridge",
    data_flow="aish → tool launcher → socket bridge → CI tool process",
    integration_date="2025-08-02"
)
def _send_to_tool(tool_name: str, message: str, ci_info: dict) -> bool:
    """
    Send a message to a CI tool via socket bridge.
    
    Args:
        tool_name: Name of the CI tool
        message: Message to send
        ci_info: CI registry information
        
    Returns:
        bool: True if message was sent successfully
    """
    try:
        # Import CI tools support
        from shared.ci_tools import get_registry as get_tool_registry
        from shared.ci_tools.tool_launcher import ToolLauncher
        
        # Get tool registry and launcher
        tool_registry = get_tool_registry()
        launcher = ToolLauncher.get_instance()
        
        # Check if tool is running
        if not ci_info.get('running', False):
            print(f"Starting {tool_name}...")
            if not launcher.launch_tool(tool_name):
                print(f"Failed to start {tool_name}")
                return False
        
        # Get adapter for the tool
        adapter = tool_registry.get_adapter(tool_name)
        if not adapter:
            print(f"No adapter found for {tool_name}")
            return False
        
        # Send message through adapter
        message_data = {
            'type': 'message',
            'content': message,
            'session_id': ci_info.get('current_session')
        }
        
        if adapter.send_message(message_data):
            # Wait for response (with timeout)
            import time
            timeout = 30
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                # Check for response from socket bridge
                bridge = launcher.get_bridge(tool_name)
                if bridge:
                    response = bridge.get_message(timeout=0.1)
                    if response:
                        # Print response
                        content = response.get('content', '')
                        if content:
                            print(content)
                        
                        # Store in registry for Apollo-Rhetor
                        registry = get_registry()
                        registry.update_ci_last_output(tool_name, json.dumps(response))
                        
                        return True
                time.sleep(0.1)
            
            print(f"Timeout waiting for response from {tool_name}")
            return False
        else:
            print(f"Failed to send message to {tool_name}")
            return False
            
    except ImportError:
        print(f"CI tools support not available")
        return False
    except Exception as e:
        print(f"Error communicating with {tool_name}: {e}")
        return False