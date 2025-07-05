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
from .ai_service import get_service

# For async code
async def ai_send(ai_id: str, message: str, host: Optional[str] = None, port: Optional[int] = None) -> str:
    """
    Send message to AI and get response. Simple async interface.
    
    Args:
        ai_id: The AI identifier (e.g., "apollo-ai")
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
    service = get_service()
    return await service.send_message(ai_id, message, host or "localhost", port)

# For sync code
def ai_send_sync(ai_id: str, message: str, host: Optional[str] = None, port: Optional[int] = None) -> str:
    """
    Send message to AI and get response. Simple sync interface.
    
    Args:
        ai_id: The AI identifier (e.g., "apollo-ai")
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
    service = get_service()
    return service.send_message_sync(ai_id, message, host or "localhost", port)

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