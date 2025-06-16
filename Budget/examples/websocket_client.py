"""
Budget WebSocket Client Example

This example demonstrates how to connect to the Budget WebSocket API
and receive real-time updates about budget status, allocations, and alerts.
"""

import os
import sys
import json
import asyncio
import argparse
import websockets
from datetime import datetime
from typing import Dict, Any, Optional

# Add the parent directory to sys.path to ensure package imports work correctly
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Function to create WebSocket messages
def create_message(type: str, topic: str, payload: Dict[str, Any]) -> str:
    """
    Create a WebSocket message.
    
    Args:
        type: The message type (e.g., 'subscription', 'authentication')
        topic: The message topic
        payload: The message payload
        
    Returns:
        str: The JSON-encoded message
    """
    message = {
        "type": type,
        "topic": topic,
        "payload": payload,
        "timestamp": datetime.now().isoformat()
    }
    return json.dumps(message)

# Function to handle budget updates
async def handle_budget_updates(uri: str, api_key: Optional[str] = None):
    """
    Connect to the Budget WebSocket API and handle updates.
    
    Args:
        uri: The WebSocket URI
        api_key: An optional API key for authentication
    """
    async with websockets.connect(uri) as websocket:
        print(f"Connected to {uri}")
        
        # Authenticate if API key is provided
        if api_key:
            auth_message = create_message(
                type="authentication",
                topic="authentication",
                payload={"api_key": api_key, "client_id": "example_client"}
            )
            await websocket.send(auth_message)
            response = await websocket.recv()
            print(f"Authentication response: {response}")
        
        # Subscribe to budget_events
        subscription_message = create_message(
            type="subscription",
            topic="subscription",
            payload={"topic": "budget_events"}
        )
        await websocket.send(subscription_message)
        response = await websocket.recv()
        print(f"Subscription response: {response}")
        
        # Start the heartbeat task
        heartbeat_task = asyncio.create_task(send_heartbeats(websocket))
        
        try:
            # Process incoming messages
            while True:
                message = await websocket.recv()
                
                # Parse and pretty-print the message
                try:
                    data = json.loads(message)
                    message_type = data.get("type", "unknown")
                    
                    # Handle different message types
                    if message_type == "budget_update":
                        print("\n=== Budget Update ===")
                        payload = data.get("payload", {})
                        
                        # Pretty print budget summary
                        if "summary" in payload:
                            summary = payload["summary"]
                            print(f"Budget ID: {payload.get('budget_id', 'N/A')}")
                            print(f"Period: {summary.get('period', 'N/A')}")
                            print(f"Total Cost: ${summary.get('total_cost', 0):.2f}")
                            print(f"Cost Limit: ${summary.get('cost_limit', 0):.2f}" if summary.get('cost_limit') else "Cost Limit: No limit")
                            print(f"Usage: {summary.get('cost_usage_percentage', 0) * 100:.1f}%" if summary.get('cost_usage_percentage') else "Usage: N/A")
                        else:
                            print(json.dumps(payload, indent=2))
                    
                    elif message_type == "alert":
                        print("\n=== Budget Alert ===")
                        payload = data.get("payload", {})
                        alerts = payload.get("alerts", [])
                        
                        for alert in alerts:
                            print(f"Severity: {alert.get('severity', 'unknown').upper()}")
                            print(f"Type: {alert.get('type', 'unknown')}")
                            print(f"Message: {alert.get('message', 'No message')}")
                            print(f"Time: {alert.get('timestamp', 'unknown')}")
                            print("-" * 30)
                    
                    elif message_type == "allocation_update":
                        print("\n=== Allocation Update ===")
                        payload = data.get("payload", {})
                        allocation = payload.get("allocation", {})
                        
                        print(f"Allocation ID: {payload.get('allocation_id', 'N/A')}")
                        print(f"Component: {allocation.get('component', 'N/A')}")
                        print(f"Tokens Allocated: {allocation.get('tokens_allocated', 0)}")
                        print(f"Tokens Used: {allocation.get('tokens_used', 0)}")
                        print(f"Estimated Cost: ${allocation.get('estimated_cost', 0):.4f}")
                        print(f"Active: {allocation.get('is_active', False)}")
                    
                    elif message_type == "price_update":
                        print("\n=== Price Update ===")
                        payload = data.get("payload", {})
                        update = payload.get("update", {})
                        
                        print(f"Provider: {payload.get('provider', 'N/A')}")
                        print(f"Model: {payload.get('model', 'N/A')}")
                        print(f"Input Cost: ${update.get('input_cost_per_token', 0) * 1000:.4f} per 1K tokens")
                        print(f"Output Cost: ${update.get('output_cost_per_token', 0) * 1000:.4f} per 1K tokens")
                        print(f"Source: {update.get('source', 'N/A')}")
                    
                    elif message_type == "heartbeat":
                        # Just print a dot to show we're still connected
                        print(".", end="", flush=True)
                    
                    else:
                        # For other message types, just print the raw data
                        print(f"\n=== {message_type.upper()} ===")
                        print(json.dumps(data, indent=2))
                    
                except json.JSONDecodeError:
                    print(f"Received non-JSON message: {message}")
                except Exception as e:
                    print(f"Error processing message: {str(e)}")
                    print(f"Raw message: {message}")
        
        finally:
            # Cancel the heartbeat task
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass

# Function to send periodic heartbeats
async def send_heartbeats(websocket, interval: int = 30):
    """
    Send periodic heartbeat messages to keep the connection alive.
    
    Args:
        websocket: The WebSocket connection
        interval: The interval in seconds between heartbeats
    """
    while True:
        try:
            heartbeat_message = create_message(
                type="heartbeat",
                topic="heartbeat",
                payload={"timestamp": datetime.now().isoformat()}
            )
            await websocket.send(heartbeat_message)
            await asyncio.sleep(interval)
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Error sending heartbeat: {str(e)}")
            break

# Entry point
async def main():
    """
    Main entry point for the WebSocket client.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Budget WebSocket Client Example")
    parser.add_argument("--host", default="localhost", help="WebSocket host")
    parser.add_argument("--port", type=int, default=8002, help="WebSocket port")
    parser.add_argument("--path", default="/ws/budget/updates", help="WebSocket path")
    parser.add_argument("--api-key", help="API key for authentication")
    args = parser.parse_args()
    
    # Construct the WebSocket URI
    uri = f"ws://{args.host}:{args.port}{args.path}"
    
    # Connect to the WebSocket and handle updates
    try:
        await handle_budget_updates(uri, args.api_key)
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())