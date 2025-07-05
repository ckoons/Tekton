#!/usr/bin/env python3
"""
Persistent Connection Pool for AI Specialists

Maintains long-lived socket connections to all AI specialists,
enabling instant communication without connection overhead.

Features:
- Connection reuse across all Tekton components
- Automatic reconnection on failure
- Connection health monitoring
- Multiplexing support for concurrent requests
"""

import asyncio
import json
import logging
import time
from typing import Dict, Optional, Tuple, Any, List
from asyncio import StreamReader, StreamWriter
from dataclasses import dataclass
from enum import Enum

from landmarks import (
    architecture_decision,
    performance_boundary,
    integration_point,
    state_checkpoint
)

logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    """Connection states"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    FAILED = "failed"


@dataclass
class Connection:
    """Represents a persistent connection to an AI"""
    ai_id: str
    host: str
    port: int
    reader: Optional[StreamReader] = None
    writer: Optional[StreamWriter] = None
    state: ConnectionState = ConnectionState.DISCONNECTED
    last_used: float = 0
    created_at: float = 0
    request_count: int = 0
    lock: asyncio.Lock = None
    
    def __post_init__(self):
        if self.lock is None:
            self.lock = asyncio.Lock()


@architecture_decision(
    title="Persistent Connection Pool Architecture",
    rationale="Reuse socket connections to eliminate connection overhead and enable instant AI responses",
    alternatives_considered=["New connection per request", "HTTP keep-alive", "WebSockets"],
    impacts=["performance", "resource_usage", "complexity"],
    decided_by="Casey"
)
class AIConnectionPool:
    """
    Singleton connection pool for all AI specialists.
    
    Maintains persistent connections and handles:
    - Connection lifecycle management
    - Automatic reconnection
    - Request multiplexing
    - Health monitoring
    """
    
    _instance = None
    _lock = asyncio.Lock()
    
    def __new__(cls):
        """Ensure singleton instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize connection pool"""
        if not hasattr(self, '_initialized'):
            self._connections: Dict[str, Connection] = {}
            self._health_check_task = None
            self._reconnect_delay = 5.0
            self._health_check_interval = 30.0
            self._connection_timeout = 2.0
            self._request_timeout = 30.0
            self._initialized = True
            logger.info("AI Connection Pool initialized")
    
    @performance_boundary(
        title="Get or Create Connection",
        sla="<100ms for existing connection",
        optimization_notes="Connections are pre-established and reused"
    )
    async def get_connection(self, ai_id: str, host: str, port: int) -> Connection:
        """Get or create a connection to an AI specialist"""
        conn_key = f"{ai_id}:{host}:{port}"
        
        # Check if we have an existing connection
        if conn_key in self._connections:
            conn = self._connections[conn_key]
            if conn.state == ConnectionState.CONNECTED:
                conn.last_used = time.time()
                return conn
        
        # Create new connection
        conn = Connection(
            ai_id=ai_id,
            host=host,
            port=port,
            created_at=time.time()
        )
        
        self._connections[conn_key] = conn
        
        # Connect asynchronously
        await self._connect(conn)
        
        return conn
    
    async def _connect(self, conn: Connection) -> bool:
        """Establish connection to AI specialist"""
        async with conn.lock:
            if conn.state == ConnectionState.CONNECTED:
                return True
            
            conn.state = ConnectionState.CONNECTING
            
            try:
                logger.info(f"Connecting to {conn.ai_id} at {conn.host}:{conn.port}")
                
                conn.reader, conn.writer = await asyncio.wait_for(
                    asyncio.open_connection(conn.host, conn.port),
                    timeout=self._connection_timeout
                )
                
                conn.state = ConnectionState.CONNECTED
                conn.last_used = time.time()
                
                logger.info(f"Connected to {conn.ai_id}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to connect to {conn.ai_id}: {e}")
                conn.state = ConnectionState.FAILED
                return False
    
    @integration_point(
        title="Multiplexed AI Communication",
        target_component="AI Specialists",
        protocol="Socket/NDJSON",
        data_flow="Request/Response with connection reuse"
    )
    async def send_message(self, ai_id: str, host: str, port: int, 
                          message: str, context: Optional[Dict[str, Any]] = None,
                          timeout: Optional[float] = None) -> Dict[str, Any]:
        """Send message using persistent connection"""
        conn = await self.get_connection(ai_id, host, port)
        
        if conn.state != ConnectionState.CONNECTED:
            # Try to reconnect once
            await self._connect(conn)
            if conn.state != ConnectionState.CONNECTED:
                return {
                    "success": False,
                    "error": f"Cannot connect to {ai_id}",
                    "ai_id": ai_id
                }
        
        # Use connection with lock to handle concurrent requests
        async with conn.lock:
            try:
                # Prepare request
                request = {
                    "type": "chat",
                    "content": message,
                    "request_id": f"{time.time()}"
                }
                
                if context:
                    request["context"] = context
                
                # Send request
                request_data = json.dumps(request).encode('utf-8') + b'\n'
                conn.writer.write(request_data)
                await conn.writer.drain()
                
                # Read response
                response_data = await asyncio.wait_for(
                    conn.reader.readline(),
                    timeout=timeout or self._request_timeout
                )
                
                if not response_data:
                    raise ConnectionError("No response received")
                
                response = json.loads(response_data.decode('utf-8').strip())
                
                # Update metrics
                conn.request_count += 1
                conn.last_used = time.time()
                
                return {
                    "success": True,
                    "response": response.get('content', response.get('response', '')),
                    "ai_id": ai_id,
                    "model": response.get('model', 'unknown'),
                    "connection_reused": True,
                    "request_count": conn.request_count
                }
                
            except Exception as e:
                logger.error(f"Error sending to {ai_id}: {e}")
                # Mark connection as failed for reconnection
                conn.state = ConnectionState.FAILED
                return {
                    "success": False,
                    "error": str(e),
                    "ai_id": ai_id
                }
    
    async def send_to_all(self, message: str, ai_ids: List[Tuple[str, str, int]],
                         timeout: float = 2.0) -> List[Dict[str, Any]]:
        """Send message to multiple AIs concurrently using persistent connections"""
        tasks = []
        
        for ai_id, host, port in ai_ids:
            task = asyncio.create_task(
                self.send_message(ai_id, host, port, message, timeout=timeout)
            )
            tasks.append((ai_id, task))
        
        # Wait for all with timeout
        results = []
        for ai_id, task in tasks:
            try:
                result = await asyncio.wait_for(task, timeout=timeout)
                results.append(result)
            except asyncio.TimeoutError:
                results.append({
                    "success": False,
                    "error": f"Timeout after {timeout}s",
                    "ai_id": ai_id
                })
        
        return results
    
    @state_checkpoint(
        title="Connection Pool Health Check",
        state_type="runtime",
        persistence=False,
        consistency_requirements="Monitor and reconnect failed connections"
    )
    async def health_check(self):
        """Periodic health check and reconnection for all connections"""
        while True:
            try:
                await asyncio.sleep(self._health_check_interval)
                
                for conn_key, conn in list(self._connections.items()):
                    if conn.state == ConnectionState.FAILED:
                        # Try to reconnect
                        logger.info(f"Attempting to reconnect {conn.ai_id}")
                        await self._connect(conn)
                    
                    elif conn.state == ConnectionState.CONNECTED:
                        # Send ping to check connection
                        try:
                            ping = json.dumps({"type": "ping"}).encode() + b'\n'
                            conn.writer.write(ping)
                            await conn.writer.drain()
                            
                            # Read pong with short timeout
                            await asyncio.wait_for(
                                conn.reader.readline(),
                                timeout=2.0
                            )
                        except:
                            logger.warning(f"Health check failed for {conn.ai_id}")
                            conn.state = ConnectionState.FAILED
                
            except Exception as e:
                logger.error(f"Health check error: {e}")
    
    def start_health_monitoring(self):
        """Start background health monitoring"""
        if not self._health_check_task:
            self._health_check_task = asyncio.create_task(self.health_check())
    
    async def close_all(self):
        """Close all connections gracefully"""
        for conn in self._connections.values():
            if conn.writer:
                conn.writer.close()
                await conn.writer.wait_closed()
        
        self._connections.clear()
        
        if self._health_check_task:
            self._health_check_task.cancel()


# Global singleton instance
_pool = AIConnectionPool()


async def get_connection_pool() -> AIConnectionPool:
    """Get the global connection pool instance"""
    return _pool


# Convenience function for direct use
async def send_to_ai(ai_id: str, host: str, port: int, message: str,
                    context: Optional[Dict[str, Any]] = None,
                    timeout: Optional[float] = None) -> Dict[str, Any]:
    """Send message to AI using connection pool"""
    pool = await get_connection_pool()
    return await pool.send_message(ai_id, host, port, message, context, timeout)