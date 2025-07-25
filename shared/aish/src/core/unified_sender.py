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
            
        elif message_format == 'json_simple':
            # Simple JSON format for direct API calls
            msg_data = {"message": message}
            url = ci.get('endpoint') + message_endpoint
            data = json.dumps(msg_data).encode('utf-8')
            
        elif message_format == 'rhetor_socket':
            # Use Rhetor client for Greek Chorus AIs
            from core.rhetor_client import send_to_rhetor
            response = send_to_rhetor(ci_name, message)
            if response:
                print(response)
                return True
            return False
            
        else:
            print(f"Unknown message format: {message_format}")
            return False
        
        # Send the message (for non-Rhetor formats)
        if message_format != 'rhetor_socket':
            req = urllib.request.Request(
                url,
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read())
                
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