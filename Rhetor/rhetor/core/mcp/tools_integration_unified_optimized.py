#!/usr/bin/env python3
"""
Optimized Team Chat Implementation using Connection Pool

This is a simplified version of orchestrate_team_chat that:
1. Uses persistent socket connections via connection pool
2. Reduces timeout to 2 seconds for fast responses
3. Removes discovery overhead by caching specialists
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

from shared.ai.connection_pool import get_connection_pool, send_to_ai
from shared.ai.unified_registry import UnifiedAIRegistry, AIStatus

logger = logging.getLogger(__name__)


class TeamChatOptimized:
    """Optimized team chat using connection pool"""
    
    def __init__(self):
        self.registry = UnifiedAIRegistry()
        self.connection_pool = None
        self._specialist_cache = {}
        self._cache_timestamp = 0
        self._cache_ttl = 60  # 1 minute cache
    
    async def initialize(self):
        """Initialize connection pool and pre-connect to all AIs"""
        self.connection_pool = await get_connection_pool()
        
        # Start health monitoring
        self.connection_pool.start_health_monitoring()
        
        # Pre-connect to all Greek Chorus AIs
        specialists = await self._get_cached_specialists()
        logger.info(f"Pre-connecting to {len(specialists)} AI specialists")
        
        connect_tasks = []
        for spec in specialists:
            if 'connection' in spec and spec['connection'].get('port'):
                task = asyncio.create_task(
                    self.connection_pool.get_connection(
                        spec['id'],
                        spec['connection'].get('host', 'localhost'),
                        spec['connection']['port']
                    )
                )
                connect_tasks.append(task)
        
        # Wait for all connections (but don't block on failures)
        await asyncio.gather(*connect_tasks, return_exceptions=True)
        logger.info("Pre-connection complete")
    
    async def _get_cached_specialists(self) -> List[Dict[str, Any]]:
        """Get specialists with caching to reduce discovery overhead"""
        now = time.time()
        
        # Check cache validity
        if self._specialist_cache and (now - self._cache_timestamp) < self._cache_ttl:
            return self._specialist_cache
        
        # Refresh cache
        all_specialists = await self.registry.list_specialists()
        
        # Filter for Greek Chorus AIs (socket-based on ports 45000-50000)
        greek_chorus = []
        for spec in all_specialists:
            spec_dict = spec.to_dict() if hasattr(spec, 'to_dict') else spec
            if 'connection' in spec_dict and spec_dict['connection'].get('port'):
                port = spec_dict['connection']['port']
                if 45000 <= port <= 50000:
                    greek_chorus.append(spec_dict)
        
        # Update cache
        self._specialist_cache = greek_chorus
        self._cache_timestamp = now
        
        return greek_chorus
    
    async def send_team_chat(self, 
                           message: str,
                           target_specialists: Optional[List[str]] = None,
                           timeout: float = 2.0) -> Dict[str, Any]:
        """
        Send team chat message using persistent connections.
        
        Args:
            message: Message to send
            target_specialists: Specific AI IDs to target (None = all)
            timeout: Timeout per AI (default 2 seconds for fast responses)
            
        Returns:
            Dict with responses from all AIs
        """
        start_time = time.time()
        
        # Get specialists
        specialists = await self._get_cached_specialists()
        
        # Filter by targets if specified
        if target_specialists:
            specialists = [s for s in specialists if s['id'] in target_specialists]
        
        if not specialists:
            return {
                "success": False,
                "error": "No specialists available",
                "responses": []
            }
        
        # Prepare AI connection info
        ai_connections = []
        for spec in specialists:
            ai_connections.append((
                spec['id'],
                spec['connection'].get('host', 'localhost'),
                spec['connection']['port']
            ))
        
        logger.info(f"Sending team chat to {len(ai_connections)} AIs with {timeout}s timeout")
        
        # Send to all AIs concurrently using connection pool
        if self.connection_pool:
            results = await self.connection_pool.send_to_all(
                message,
                ai_connections,
                timeout=timeout
            )
        else:
            # Fallback to individual sends
            tasks = []
            for ai_id, host, port in ai_connections:
                task = asyncio.create_task(
                    send_to_ai(ai_id, host, port, message, timeout=timeout)
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        responses = []
        success_count = 0
        
        for i, result in enumerate(results):
            if isinstance(result, dict) and result.get('success'):
                responses.append({
                    "socket_id": result['ai_id'],
                    "content": result['response'],
                    "model": result.get('model', 'unknown'),
                    "connection_reused": result.get('connection_reused', False),
                    "timestamp": datetime.utcnow().isoformat()
                })
                success_count += 1
            elif isinstance(result, dict):
                # Include error in response
                responses.append({
                    "socket_id": result.get('ai_id', ai_connections[i][0]),
                    "content": f"Error: {result.get('error', 'Unknown error')}",
                    "error": True,
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                # Exception case
                responses.append({
                    "socket_id": ai_connections[i][0] if i < len(ai_connections) else 'unknown',
                    "content": f"Error: {str(result)}",
                    "error": True,
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        elapsed_time = time.time() - start_time
        
        return {
            "success": success_count > 0,
            "responses": responses,
            "total_specialists": len(specialists),
            "success_count": success_count,
            "elapsed_time": elapsed_time,
            "average_response_time": elapsed_time / len(specialists) if specialists else 0,
            "connection_pool_used": self.connection_pool is not None
        }


# Global instance
_team_chat = None


async def get_team_chat() -> TeamChatOptimized:
    """Get or create team chat instance"""
    global _team_chat
    if _team_chat is None:
        _team_chat = TeamChatOptimized()
        await _team_chat.initialize()
    return _team_chat


# Convenience function
async def send_team_message(message: str, 
                          target_specialists: Optional[List[str]] = None,
                          timeout: float = 2.0) -> Dict[str, Any]:
    """Send team chat message using optimized connection pool"""
    team_chat = await get_team_chat()
    return await team_chat.send_team_chat(message, target_specialists, timeout)