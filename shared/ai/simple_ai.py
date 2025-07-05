#!/usr/bin/env python3
"""
Simple AI Communication Interface - One Queue, One Socket, One AI

Usage:
    # Async
    response = await ai_send("apollo-ai", "hello", host="localhost", port=45012)
    
    # Sync
    response = ai_send_sync("apollo-ai", "hello", host="localhost", port=45012)
    
    # If AI already registered
    response = await ai_send("apollo-ai", "hello")
"""

from typing import Optional
from .ai_service_simple import get_service

# For async code
async def ai_send(ai_id: str, message: str, host: Optional[str] = None, port: Optional[int] = None) -> str:
    """
    Send message to AI and get response. Simple async interface.
    
    Args:
        ai_id: The AI identifier (e.g., "apollo-ai" or "localhost:45012")
        message: The message to send
        host: Host if AI not registered (default: localhost)
        port: Port if AI not registered
        
    Returns:
        The AI's response as a string
        
    Raises:
        ValueError: If AI not registered and no host/port provided
        TimeoutError: If no response within timeout
        Exception: If AI returns an error
    """
    import asyncio
    
    service = get_service()
    
    # Handle port-based IDs from socket client
    if ":" in ai_id and not host and not port:
        parts = ai_id.split(":")
        if len(parts) == 2:
            host = parts[0]
            try:
                port = int(parts[1])
                # Try to find the actual AI name from port
                ai_id = _get_ai_id_from_port(port) or ai_id
            except:
                pass
    
    if not host or not port:
        raise ValueError(f"Host and port required for {ai_id}")
    
    # Register AI if not already registered
    if ai_id not in service.sockets:
        try:
            reader, writer = await asyncio.open_connection(host, port)
            service.register_ai(ai_id, reader, writer)
        except Exception as e:
            raise Exception(f"Could not connect to {ai_id}: {e}")
    
    # Send message async
    msg_id = service.send_message_async(ai_id, message)
    
    # Process the message
    await service.process_one_message(ai_id, msg_id)
    
    # Get response
    result = service.get_response(ai_id, msg_id)
    if result:
        if result['success']:
            return result['response']
        else:
            raise Exception(result['error'])
    else:
        raise Exception(f"No response from {ai_id}")

# For sync code
def ai_send_sync(ai_id: str, message: str, host: Optional[str] = None, port: Optional[int] = None) -> str:
    """
    Send message to AI and get response. Simple sync interface.
    
    Args:
        ai_id: The AI identifier (e.g., "apollo-ai" or "localhost:45012")
        message: The message to send
        host: Host if AI not registered (default: localhost)
        port: Port if AI not registered
        
    Returns:
        The AI's response as a string
        
    Raises:
        ValueError: If AI not registered and no host/port provided
        TimeoutError: If no response within timeout
        Exception: If AI returns an error
    """
    import asyncio
    
    # Handle port-based IDs from socket client
    if ":" in ai_id and not host and not port:
        parts = ai_id.split(":")
        if len(parts) == 2:
            host = parts[0]
            try:
                port = int(parts[1])
                # Try to find the actual AI name from port
                ai_id = _get_ai_id_from_port(port) or ai_id
            except:
                pass
    
    # Use the async version
    return asyncio.run(ai_send(ai_id, message, host, port))

# Helper to map ports to AI IDs
def _get_ai_id_from_port(port: int) -> Optional[str]:
    """Get AI ID from port number"""
    port_map = {
        45000: "engram-ai",
        45001: "hermes-ai",
        45002: "ergon-ai",
        45003: "rhetor-ai",
        45004: "terma-ai",
        45005: "athena-ai",
        45006: "prometheus-ai",
        45007: "harmonia-ai",
        45008: "telos-ai",
        45009: "synthesis-ai",
        45010: "tekton_core-ai",
        45011: "metis-ai",
        45012: "apollo-ai",
        45013: "penia-ai",
        45014: "sophia-ai",
        45015: "noesis-ai",
        45016: "numa-ai",
        45080: "hephaestus-ai",
    }
    return port_map.get(port)

# Pre-register all known AIs
def register_all_ais():
    """Pre-register all known Tekton AIs"""
    service = get_service()
    
    ais = [
        ("engram-ai", "localhost", 45000),
        ("hermes-ai", "localhost", 45001),
        ("ergon-ai", "localhost", 45002),
        ("rhetor-ai", "localhost", 45003),
        ("terma-ai", "localhost", 45004),
        ("athena-ai", "localhost", 45005),
        ("prometheus-ai", "localhost", 45006),
        ("harmonia-ai", "localhost", 45007),
        ("telos-ai", "localhost", 45008),
        ("synthesis-ai", "localhost", 45009),
        ("tekton_core-ai", "localhost", 45010),
        ("metis-ai", "localhost", 45011),
        ("apollo-ai", "localhost", 45012),
        ("penia-ai", "localhost", 45013),
        ("sophia-ai", "localhost", 45014),
        ("noesis-ai", "localhost", 45015),
        ("numa-ai", "localhost", 45016),
        ("hephaestus-ai", "localhost", 45080),
    ]
    
    for ai_id, host, port in ais:
        service.register_ai(ai_id, host, port)

# Auto-register on import
register_all_ais()