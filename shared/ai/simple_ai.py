#!/usr/bin/env python3
"""
Simple AI Communication Interface - One Queue, One Socket, One AI

Usage:
    # Async
    response = await ai_send("apollo-ci", "hello", host="localhost", port=45012)
    
    # Sync
    response = ai_send_sync("apollo-ci", "hello", host="localhost", port=45012)
    
    # If AI already registered
    response = await ai_send("apollo-ci", "hello")
"""

from typing import Optional
from .ai_service_simple import get_service

from landmarks import (
    architecture_decision,
    performance_boundary,
    integration_point
)

# For async code
@architecture_decision(
    title="Unified AI Communication Interface",
    rationale="Single entry point for all AI communication using 'One Queue, One Socket, One AI' principle",
    alternatives_considered=["Multiple socket clients", "Connection pooling", "Direct socket access"],
    impacts=["simplicity", "maintainability", "consistency"],
    decided_by="Casey"
)
@performance_boundary(
    title="AI Message Exchange",
    sla="<30s timeout per message",
    optimization_notes="Direct socket connection with UUID-based message tracking",
    metrics={"default_timeout": "30s", "max_retries": 3}
)
@integration_point(
    title="AI Service Integration",
    target_component="ai_service_simple",
    protocol="Socket/NDJSON",
    data_flow="Message queue → Direct socket → AI response"
)
async def ai_send(ai_id: str, message: str, host: Optional[str] = None, port: Optional[int] = None) -> str:
    """
    Send message to AI and get response. Simple async interface.
    
    Args:
        ai_id: The AI identifier (e.g., "apollo-ci" or "localhost:45012")
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
    
    # Always create a fresh connection to avoid reuse issues
    # First clean up any existing connection
    if ai_id in service.sockets:
        try:
            _, old_writer = service.sockets[ai_id]
            old_writer.close()
            await old_writer.wait_closed()
        except:
            pass
        del service.sockets[ai_id]
        if ai_id in service.queues:
            del service.queues[ai_id]
    
    # Create new connection
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
        ai_id: The AI identifier (e.g., "apollo-ci" or "localhost:45012")
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
    
    if not host or not port:
        raise ValueError(f"Host and port required for {ai_id}")
    
    # Always use async version with real connections - don't use service sync method
    try:
        loop = asyncio.get_running_loop()
        # We're in an async context, use thread pool
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, ai_send(ai_id, message, host, port))
            return future.result()
    except RuntimeError:
        # No event loop running, safe to use asyncio.run
        return asyncio.run(ai_send(ai_id, message, host, port))

# Helper to map ports to AI IDs
def _get_ai_id_from_port(port: int) -> Optional[str]:
    """Get AI ID from port number"""
    port_map = {
        45000: "engram-ci",
        45001: "hermes-ci",
        45002: "ergon-ci",
        45003: "rhetor-ci",
        45004: "terma-ci",
        45005: "athena-ci",
        45006: "prometheus-ci",
        45007: "harmonia-ci",
        45008: "telos-ci",
        45009: "synthesis-ci",
        45010: "tekton_core-ci",
        45011: "metis-ci",
        45012: "apollo-ci",
        45013: "penia-ci",
        45014: "sophia-ci",
        45015: "noesis-ci",
        45016: "numa-ci",
        45080: "hephaestus-ci",
    }
    return port_map.get(port)

# Pre-register all known AIs
def register_all_ais():
    """Pre-register all known Tekton AIs"""
    service = get_service()
    
    ais = [
        ("engram-ci", "localhost", 45000),
        ("hermes-ci", "localhost", 45001),
        ("ergon-ci", "localhost", 45002),
        ("rhetor-ci", "localhost", 45003),
        ("terma-ci", "localhost", 45004),
        ("athena-ci", "localhost", 45005),
        ("prometheus-ci", "localhost", 45006),
        ("harmonia-ci", "localhost", 45007),
        ("telos-ci", "localhost", 45008),
        ("synthesis-ci", "localhost", 45009),
        ("tekton_core-ci", "localhost", 45010),
        ("metis-ci", "localhost", 45011),
        ("apollo-ci", "localhost", 45012),
        ("penia-ci", "localhost", 45013),
        ("sophia-ci", "localhost", 45014),
        ("noesis-ci", "localhost", 45015),
        ("numa-ci", "localhost", 45016),
        ("hephaestus-ci", "localhost", 45080),
    ]
    
    for ai_id, host, port in ais:
        # Don't auto-connect - just make sure the queues exist
        if ai_id not in service.queues:
            service.queues[ai_id] = {}

# Auto-register on import
register_all_ais()
