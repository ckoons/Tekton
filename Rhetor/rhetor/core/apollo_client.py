"""
Apollo Client for Rhetor

Provides access to Apollo's Context Brief preparation system via MCP.
Rhetor uses this to get context before processing LLM requests.
"""

import logging
import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

# Use shared URL builder
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from shared.urls import apollo_url

logger = logging.getLogger("rhetor.apollo_client")


class ApolloClient:
    """Client for interacting with Apollo's Preparation system via MCP"""
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize Apollo client.
        
        Args:
            base_url: Optional base URL override for Apollo service
        """
        # Use shared URL builder to get Apollo URL
        self.apollo_url = base_url if base_url else apollo_url()
        self.mcp_endpoint = apollo_url("/mcp/tools/invoke")
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            
    async def get_context_brief(
        self, 
        ci_name: str,
        message: str,
        max_tokens: int = 2000
    ) -> Optional[Dict[str, Any]]:
        """
        Get a Context Brief from Apollo for a CI.
        
        Args:
            ci_name: Name of the CI requesting context
            message: Current message for relevance scoring
            max_tokens: Maximum tokens for the brief
            
        Returns:
            Context Brief dict or None if unavailable
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            # Call Apollo's MCP tool
            payload = {
                "tool_name": "get_context_brief",
                "arguments": {
                    "ci_name": ci_name,
                    "message": message,
                    "max_tokens": max_tokens
                }
            }
            
            async with self.session.post(
                self.mcp_endpoint,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Retrieved Context Brief for {ci_name}")
                    return result.get("result", {})
                else:
                    logger.warning(f"Failed to get Context Brief: {response.status}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.warning("Apollo request timed out")
            return None
        except Exception as e:
            logger.error(f"Error getting Context Brief: {e}")
            return None
            
    async def store_memory(
        self,
        memory_data: Dict[str, Any]
    ) -> bool:
        """
        Store a memory in Apollo's catalog.
        
        Args:
            memory_data: Memory data to store
            
        Returns:
            True if successful
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            # Call Apollo's MCP tool
            payload = {
                "tool_name": "store_memory",
                "arguments": {
                    "memory": memory_data
                }
            }
            
            async with self.session.post(
                self.mcp_endpoint,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    logger.info(f"Stored memory in Apollo")
                    return True
                else:
                    logger.warning(f"Failed to store memory: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error storing memory: {e}")
            return False
            
    async def search_memories(
        self,
        query: str,
        ci_name: Optional[str] = None,
        memory_type: Optional[str] = None,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search memories in Apollo's catalog.
        
        Args:
            query: Search query
            ci_name: Filter by CI name
            memory_type: Filter by memory type
            max_results: Maximum results to return
            
        Returns:
            List of matching memories
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            # Call Apollo's MCP tool
            payload = {
                "tool_name": "search_memories",
                "arguments": {
                    "query": query,
                    "ci_name": ci_name,
                    "memory_type": memory_type,
                    "max_results": max_results
                }
            }
            
            async with self.session.post(
                self.mcp_endpoint,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("result", {}).get("memories", [])
                else:
                    logger.warning(f"Failed to search memories: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            return []
            
    async def extract_memories(
        self,
        exchange: Dict[str, Any]
    ) -> List[str]:
        """
        Extract memories from a CI exchange.
        
        Args:
            exchange: Exchange data to analyze
            
        Returns:
            List of memory IDs created
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            # Call Apollo's MCP tool
            payload = {
                "tool_name": "extract_memories",
                "arguments": {
                    "exchange": exchange
                }
            }
            
            async with self.session.post(
                self.mcp_endpoint,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    memory_ids = result.get("result", {}).get("memory_ids", [])
                    logger.info(f"Extracted {len(memory_ids)} memories")
                    return memory_ids
                else:
                    logger.warning(f"Failed to extract memories: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error extracting memories: {e}")
            return []
            
    async def get_memory_statistics(
        self,
        ci_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get memory statistics from Apollo.
        
        Args:
            ci_name: Optional CI name for filtered stats
            
        Returns:
            Statistics dictionary
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            # Call Apollo's MCP tool
            payload = {
                "tool_name": "get_memory_statistics",
                "arguments": {
                    "ci_name": ci_name
                }
            }
            
            async with self.session.post(
                self.mcp_endpoint,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("result", {})
                else:
                    logger.warning(f"Failed to get statistics: {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}


# Singleton instance
_apollo_client = None


def get_apollo_client() -> ApolloClient:
    """Get or create the Apollo client singleton"""
    global _apollo_client
    if _apollo_client is None:
        # Use shared URL builder - no hardcoded URLs
        _apollo_client = ApolloClient()
    return _apollo_client