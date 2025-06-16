"""
Telos integration for Metis

This module provides functionality for integrating with Telos,
the requirements management system for Tekton.
"""

import aiohttp
from typing import Dict, List, Optional, Any, Tuple
import asyncio

from metis.utils.hermes_helper import hermes_client
from metis.config import config
from metis.models.requirement import RequirementRef


class TelosClient:
    """
    Client for interacting with the Telos requirements management system.
    
    This class provides methods for retrieving requirements from Telos
    and synchronizing them with tasks in Metis.
    """
    
    def __init__(self):
        """Initialize the Telos client."""
        self.telos_url = config["TELOS_URL"]
        self._session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session for HTTP requests."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def get_requirement(self, requirement_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a requirement from Telos by ID.
        
        Args:
            requirement_id: ID of the requirement to get
            
        Returns:
            Optional[Dict[str, Any]]: Requirement data if found, None otherwise
        """
        try:
            # Try to discover Telos URL through Hermes
            telos_url = await hermes_client.get_service_url("Telos")
            if telos_url:
                self.telos_url = telos_url
            
            session = await self._get_session()
            
            # Get requirement data from Telos
            async with session.get(
                f"{self.telos_url}/api/v1/requirements/{requirement_id}"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("requirement")
                else:
                    print(f"Failed to get requirement {requirement_id}: {response.status}")
                    return None
        
        except Exception as e:
            print(f"Error getting requirement {requirement_id}: {e}")
            return None
    
    async def search_requirements(
        self, 
        query: str = None, 
        status: str = None,
        category: str = None,
        page: int = 1, 
        page_size: int = 50
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Search for requirements in Telos.
        
        Args:
            query: Search query
            status: Filter by status
            category: Filter by category
            page: Page number
            page_size: Page size
            
        Returns:
            Tuple[List[Dict[str, Any]], int]: List of requirements and total count
        """
        try:
            # Try to discover Telos URL through Hermes
            telos_url = await hermes_client.get_service_url("Telos")
            if telos_url:
                self.telos_url = telos_url
            
            session = await self._get_session()
            
            # Set up query parameters
            params = {
                "page": page,
                "page_size": page_size
            }
            
            if query:
                params["query"] = query
            
            if status:
                params["status"] = status
            
            if category:
                params["category"] = category
            
            # Search requirements
            async with session.get(
                f"{self.telos_url}/api/v1/requirements",
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("requirements", []), data.get("total", 0)
                else:
                    print(f"Failed to search requirements: {response.status}")
                    return [], 0
        
        except Exception as e:
            print(f"Error searching requirements: {e}")
            return [], 0
    
    async def create_requirement_reference(
        self, requirement_id: str
    ) -> Optional[RequirementRef]:
        """
        Create a requirement reference from a Telos requirement.
        
        Args:
            requirement_id: ID of the requirement
            
        Returns:
            Optional[RequirementRef]: Requirement reference if created, None otherwise
        """
        # Get requirement data from Telos
        requirement = await self.get_requirement(requirement_id)
        if not requirement:
            return None
        
        # Create requirement reference
        return RequirementRef(
            requirement_id=requirement_id,
            source="telos",
            requirement_type=requirement.get("type", "unknown"),
            title=requirement.get("title", "Untitled Requirement"),
            relationship="implements",
            description=requirement.get("description")
        )
    
    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None


# Global Telos client instance
telos_client = TelosClient()