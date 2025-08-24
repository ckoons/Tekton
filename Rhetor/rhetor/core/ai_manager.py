"""
Simple CI Manager for Rhetor

Reads CI configuration from component_config (ports from environment) and manages CI interactions.
No complex discovery - just fixed ports and health checks.
"""
import asyncio
import json
import socket
import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime

from tekton.utils.component_config import get_component_config
from shared.utils.ai_port_utils import get_ai_port
from shared.ai.simple_ai import ai_send

logger = logging.getLogger(__name__)


class CIManager:
    """
    Simple CI manager for Rhetor.
    
    - Reads components from component_config (ports from environment)
    - Calculates CI ports using standard formula
    - Checks health by attempting connection
    - Manages roster of active CIs
    """
    
    def __init__(self):
        """Initialize CI manager with component config."""
        self.config = get_component_config()
        self.roster: Dict[str, Dict[str, Any]] = {}  # Active CIs Rhetor is using
        self._health_cache: Dict[str, tuple[bool, float]] = {}  # (is_healthy, timestamp)
        self._cache_ttl = 30  # Cache health checks for 30 seconds
        
    def get_all_ai_components(self) -> List[str]:
        """Get list of all components that have CI specialists."""
        # All components can have CI specialists
        all_components = self.config.get_all_components()
        return [comp_id for comp_id in all_components.keys() 
                if comp_id not in ['ui_devtools']]  # Exclude non-CI components
    
    def get_ai_info(self, component_id: str) -> Dict[str, Any]:
        """
        Get CI information for a component.
        
        Returns:
            Dict with ai_id, component, port, host
        """
        comp_info = self.config.get_component(component_id)
        if not comp_info:
            raise ValueError(f"Unknown component: {component_id}")
            
        ai_port = get_ai_port(comp_info.port)
        
        return {
            'ai_id': f"{component_id}-ci",
            'component': component_id,
            'name': comp_info.name,
            'port': ai_port,
            'host': 'localhost',
            'description': comp_info.description,
            'category': comp_info.category,
            'capabilities': comp_info.capabilities
        }
    
    async def check_ai_health(self, ai_id: str) -> bool:
        """
        Check if an CI is healthy by attempting to connect.
        
        Uses cache to avoid hammering CIs with health checks.
        """
        # Check cache first
        if ai_id in self._health_cache:
            is_healthy, timestamp = self._health_cache[ai_id]
            if (datetime.now().timestamp() - timestamp) < self._cache_ttl:
                return is_healthy
        
        # Extract component from ai_id
        component_id = ai_id.replace('-ci', '')
        
        try:
            ai_info = self.get_ai_info(component_id)
            
            # Try to connect and ping
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(ai_info['host'], ai_info['port']),
                timeout=2.0
            )
            
            # Send ping
            writer.write(json.dumps({'type': 'ping'}).encode() + b'\n')
            await writer.drain()
            
            # Wait for response
            response = await asyncio.wait_for(reader.readline(), timeout=2.0)
            
            writer.close()
            await writer.wait_closed()
            
            # Cache result
            self._health_cache[ai_id] = (True, datetime.now().timestamp())
            return True
            
        except Exception as e:
            logger.debug(f"CI {ai_id} health check failed: {e}")
            self._health_cache[ai_id] = (False, datetime.now().timestamp())
            return False
    
    async def list_available_ais(self, include_health: bool = True) -> List[Dict[str, Any]]:
        """
        List all available CI specialists.
        
        Args:
            include_health: Whether to check health status
            
        Returns:
            List of CI info dicts
        """
        ais = []
        
        for component_id in self.get_all_ai_components():
            try:
                ai_info = self.get_ai_info(component_id)
                ai_id = ai_info['ai_id']
                
                # Add health status if requested
                if include_health:
                    ai_info['healthy'] = await self.check_ai_health(ai_id)
                else:
                    ai_info['healthy'] = None
                
                # Add roster status
                ai_info['in_roster'] = ai_id in self.roster
                
                ais.append(ai_info)
                
            except Exception as e:
                logger.warning(f"Failed to get info for {component_id}: {e}")
                
        return ais
    
    def hire_ai(self, ai_id: str, role: Optional[str] = None) -> Dict[str, Any]:
        """
        Add an CI to Rhetor's active roster.
        
        Args:
            ai_id: CI specialist ID (e.g., 'apollo-ci')
            role: Optional role assignment
            
        Returns:
            Roster entry
        """
        if ai_id in self.roster:
            return self.roster[ai_id]
        
        component_id = ai_id.replace('-ci', '')
        ai_info = self.get_ai_info(component_id)
        
        roster_entry = {
            'ai_id': ai_id,
            'component': component_id,
            'role': role or ai_info['category'],
            'hired_at': datetime.now().isoformat(),
            'performance': {
                'requests': 0,
                'successes': 0,
                'failures': 0,
                'avg_response_time': 0
            }
        }
        
        self.roster[ai_id] = roster_entry
        logger.info(f"Hired CI specialist: {ai_id} for role: {roster_entry['role']}")
        
        return roster_entry
    
    def fire_ai(self, ai_id: str) -> bool:
        """
        Remove an CI from Rhetor's active roster.
        
        Returns:
            True if removed, False if not in roster
        """
        if ai_id in self.roster:
            del self.roster[ai_id]
            logger.info(f"Fired CI specialist: {ai_id}")
            return True
        return False
    
    def get_roster(self) -> Dict[str, Dict[str, Any]]:
        """Get current roster of hired CIs."""
        return self.roster.copy()
    
    async def send_to_ai(self, ai_id: str, message: str) -> Dict[str, Any]:
        """
        Send a message to an CI specialist.
        
        Args:
            ai_id: CI specialist ID
            message: Message to send
            
        Returns:
            Response dict with success status and response/error
        """
        try:
            component_id = ai_id.replace('-ci', '')
            ai_info = self.get_ai_info(component_id)
            
            # Use simple_ai for communication
            response = await ai_send(ai_id, message, ai_info['host'], ai_info['port'])
            
            # Update performance metrics if in roster
            if ai_id in self.roster:
                perf = self.roster[ai_id]['performance']
                perf['requests'] += 1
                perf['successes'] += 1
            
            return {
                'success': True,
                'response': response,
                'ai_id': ai_id
            }
            
        except Exception as e:
            logger.error(f"Failed to send message to {ai_id}: {e}")
            
            # Update failure metrics if in roster
            if ai_id in self.roster:
                perf = self.roster[ai_id]['performance']
                perf['requests'] += 1
                perf['failures'] += 1
            
            return {
                'success': False,
                'error': str(e),
                'ai_id': ai_id
            }
    
    async def find_ai_for_role(self, role: str) -> Optional[str]:
        """
        Find a healthy CI that can fulfill a role.
        
        Args:
            role: Role/category needed (e.g., 'ai', 'knowledge', 'planning')
            
        Returns:
            CI ID if found, None otherwise
        """
        # First check roster for assigned roles
        for ai_id, entry in self.roster.items():
            if entry['role'] == role and await self.check_ai_health(ai_id):
                return ai_id
        
        # Then check components by category
        for component_id in self.get_all_ai_components():
            comp_info = self.config.get_component(component_id)
            if comp_info.category == role:
                ai_id = f"{component_id}-ci"
                if await self.check_ai_health(ai_id):
                    return ai_id
        
        return None
    
    def clear_health_cache(self):
        """Clear the health check cache."""
        self._health_cache.clear()
