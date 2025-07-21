"""
Engram Connector

This module provides a connector for interacting with the Engram memory component.
"""

import os
import sys
import logging
import json
from typing import Dict, List, Any, Optional
import asyncio

# Add Tekton root to path for shared imports
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if tekton_root not in sys.path:
    sys.path.append(tekton_root)

from shared.utils.global_config import GlobalConfig

# Configure logging
logger = logging.getLogger("prometheus.utils.engram_connector")


class EngramConnector:
    """
    Connector for interacting with the Engram memory component.
    """
    
    def __init__(self, engram_url: Optional[str] = None):
        """
        Initialize the Engram connector.
        
        Args:
            engram_url: URL of the Engram API (defaults to environment variable)
        """
        config = GlobalConfig()
        engram_port = config.get_port('engram')
        self.engram_url = engram_url or f"http://localhost:{engram_port}/api"
        self.initialized = False
        self.engram_client = None
    
    async def initialize(self) -> bool:
        """
        Initialize the connector.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        if self.initialized:
            return True
            
        try:
            # Try to import from tekton-core
            try:
                from tekton.utils.component_client import ComponentClient
                
                # Create client
                hermes_port = GlobalConfig().get_port('hermes')
                self.engram_client = ComponentClient(
                    component_id="engram.memory",
                    hermes_url=f"http://localhost:{hermes_port}/api"
                )
                await self.engram_client.initialize()
                self.initialized = True
                logger.info(f"Engram connector initialized with component client")
                return True
                
            except ImportError:
                logger.warning("Could not import component client from tekton-core.")
                
                # Fallback to HTTP client
                import aiohttp
                logger.info(f"Using direct HTTP connection to Engram at {self.engram_url}")
                self.initialized = True
                return True
                
        except Exception as e:
            logger.error(f"Error initializing Engram connector: {e}")
            return False
    
    async def store_execution_record(self, execution_record: Dict[str, Any]) -> bool:
        """
        Store an execution record in Engram.
        
        Args:
            execution_record: Execution record data
            
        Returns:
            True if storage was successful, False otherwise
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            # Create memory entry
            memory_entry = {
                "content": json.dumps(execution_record),
                "metadata": {
                    "type": "execution_record",
                    "plan_id": execution_record.get("plan_id"),
                    "record_id": execution_record.get("record_id"),
                    "record_date": execution_record.get("record_date")
                },
                "tags": ["execution_record", f"plan_{execution_record.get('plan_id')}"]
            }
            
            if self.engram_client:
                # Use the client
                result = await self.engram_client.invoke_capability("store_memory", memory_entry)
                
                if isinstance(result, dict) and "memory_id" in result:
                    logger.info(f"Stored execution record {execution_record.get('record_id')} in Engram")
                    return True
                else:
                    logger.error(f"Unexpected response format from Engram: {result}")
                    return False
            else:
                # Use direct HTTP request
                import aiohttp
                
                url = f"{self.engram_url}/memory"
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=memory_entry) as response:
                        if response.status == 200 or response.status == 201:
                            result = await response.json()
                            if "data" in result and "memory_id" in result["data"]:
                                logger.info(f"Stored execution record {execution_record.get('record_id')} in Engram")
                                return True
                            else:
                                logger.error(f"Unexpected response format from Engram: {result}")
                                return False
                        else:
                            logger.error(f"Error storing execution record in Engram: {response.status}")
                            return False
        except Exception as e:
            logger.error(f"Error storing execution record in Engram: {e}")
            return False
    
    async def store_retrospective(self, retrospective: Dict[str, Any]) -> bool:
        """
        Store a retrospective in Engram.
        
        Args:
            retrospective: Retrospective data
            
        Returns:
            True if storage was successful, False otherwise
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            # Create memory entry
            memory_entry = {
                "content": json.dumps(retrospective),
                "metadata": {
                    "type": "retrospective",
                    "plan_id": retrospective.get("plan_id"),
                    "retro_id": retrospective.get("retro_id"),
                    "date": retrospective.get("date"),
                    "format": retrospective.get("format")
                },
                "tags": ["retrospective", f"plan_{retrospective.get('plan_id')}"]
            }
            
            if self.engram_client:
                # Use the client
                result = await self.engram_client.invoke_capability("store_memory", memory_entry)
                
                if isinstance(result, dict) and "memory_id" in result:
                    logger.info(f"Stored retrospective {retrospective.get('retro_id')} in Engram")
                    return True
                else:
                    logger.error(f"Unexpected response format from Engram: {result}")
                    return False
            else:
                # Use direct HTTP request
                import aiohttp
                
                url = f"{self.engram_url}/memory"
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=memory_entry) as response:
                        if response.status == 200 or response.status == 201:
                            result = await response.json()
                            if "data" in result and "memory_id" in result["data"]:
                                logger.info(f"Stored retrospective {retrospective.get('retro_id')} in Engram")
                                return True
                            else:
                                logger.error(f"Unexpected response format from Engram: {result}")
                                return False
                        else:
                            logger.error(f"Error storing retrospective in Engram: {response.status}")
                            return False
        except Exception as e:
            logger.error(f"Error storing retrospective in Engram: {e}")
            return False
    
    async def get_historical_data(self, filters: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retrieve historical data from Engram.
        
        Args:
            filters: Filters to apply to the search
            
        Returns:
            Dictionary with historical data
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            # Build search query
            search_query = {
                "filters": filters
            }
            
            if "time_range" in filters:
                # Convert time range to proper filter
                time_range = filters.pop("time_range")
                if "start" in time_range:
                    search_query["after"] = time_range["start"]
                if "end" in time_range:
                    search_query["before"] = time_range["end"]
            
            if "team_id" in filters:
                # Add team tag
                search_query["tags"] = search_query.get("tags", []) + [f"team_{filters['team_id']}"]
                
            # Get execution records
            execution_records = await self._search_memories("execution_record", search_query)
            
            # Get retrospectives
            retrospectives = await self._search_memories("retrospective", search_query)
            
            return {
                "execution_records": execution_records,
                "retrospectives": retrospectives
            }
        except Exception as e:
            logger.error(f"Error getting historical data from Engram: {e}")
            return {
                "execution_records": [],
                "retrospectives": []
            }
    
    async def _search_memories(self, memory_type: str, search_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search for memories of a specific type.
        
        Args:
            memory_type: Type of memory to search for
            search_query: Search query
            
        Returns:
            List of matching memories
        """
        # Add type filter
        search_query["metadata"] = search_query.get("metadata", {})
        search_query["metadata"]["type"] = memory_type
        
        if self.engram_client:
            # Use the client
            result = await self.engram_client.invoke_capability("search_memory", search_query)
            
            if isinstance(result, dict) and "results" in result:
                # Parse the content of each result
                memories = []
                for item in result["results"]:
                    try:
                        content = json.loads(item["content"])
                        memories.append(content)
                    except (json.JSONDecodeError, KeyError):
                        logger.error(f"Error parsing memory content: {item}")
                return memories
            else:
                logger.error(f"Unexpected response format from Engram: {result}")
                return []
        else:
            # Use direct HTTP request
            import aiohttp
            
            url = f"{self.engram_url}/memory/search"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=search_query) as response:
                    if response.status == 200:
                        result = await response.json()
                        if "data" in result and "results" in result["data"]:
                            # Parse the content of each result
                            memories = []
                            for item in result["data"]["results"]:
                                try:
                                    content = json.loads(item["content"])
                                    memories.append(content)
                                except (json.JSONDecodeError, KeyError):
                                    logger.error(f"Error parsing memory content: {item}")
                            return memories
                        else:
                            logger.error(f"Unexpected response format from Engram: {result}")
                            return []
                    else:
                        logger.error(f"Error searching memories in Engram: {response.status}")
                        return []