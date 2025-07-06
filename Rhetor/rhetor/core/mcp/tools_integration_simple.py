"""
Simplified MCP Tools Integration for Rhetor.

Uses the simple AI manager instead of complex discovery service.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from rhetor.core.ai_manager import AIManager
from shared.ai.simple_ai import ai_send

from landmarks import (
    architecture_decision,
    integration_point,
    performance_boundary
)

logger = logging.getLogger(__name__)


@architecture_decision(
    title="Simplified MCP Tools Integration",
    rationale="Direct integration with fixed-port AI specialists via tekton_components.yaml",
    impacts=["Removes complex discovery", "Faster startup", "Simpler code"]
)
class MCPToolsIntegrationSimple:
    """
    Simplified MCP tools integration.
    
    - Uses AIManager for all AI operations
    - No complex discovery or routing
    - Direct communication via simple_ai
    """
    
    def __init__(self, hermes_url: str = "http://localhost:8001"):
        """Initialize the simplified MCP tools integration.
        
        Args:
            hermes_url: URL of the Hermes message bus
        """
        self.hermes_url = hermes_url
        self.ai_manager = AIManager()
        logger.info("Initialized simplified MCP tools integration")
    
    async def list_specialists(self) -> List[Dict[str, Any]]:
        """List all AI specialists.
        
        Returns:
            List of specialist information
        """
        try:
            specialists = await self.ai_manager.list_available_ais(include_health=True)
            
            # Format for compatibility
            return [{
                'id': spec['ai_id'],
                'name': spec['name'],
                'component': spec['component'],
                'status': 'healthy' if spec.get('healthy', False) else 'unavailable',
                'roles': [spec['category']],
                'capabilities': spec.get('capabilities', []),
                'connection': {
                    'host': spec['host'],
                    'port': spec['port']
                }
            } for spec in specialists]
            
        except Exception as e:
            logger.error(f"Failed to list specialists: {e}")
            return []
    
    async def activate_specialist(self, specialist_id: str) -> Dict[str, Any]:
        """Activate an AI specialist (adds to roster).
        
        Args:
            specialist_id: ID of the specialist
            
        Returns:
            Activation result
        """
        try:
            # Check health first
            if not await self.ai_manager.check_ai_health(specialist_id):
                return {
                    "success": False,
                    "error": f"Specialist {specialist_id} is not healthy"
                }
            
            # Add to roster
            roster_entry = self.ai_manager.hire_ai(specialist_id)
            
            return {
                "success": True,
                "message": f"Specialist {specialist_id} activated",
                "roster_entry": roster_entry
            }
            
        except Exception as e:
            logger.error(f"Failed to activate specialist {specialist_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_message_to_specialist(self, specialist_id: str, message: str, 
                                       context: Optional[Dict[str, Any]] = None,
                                       timeout: float = 30.0) -> Dict[str, Any]:
        """Send a message to an AI specialist.
        
        Args:
            specialist_id: ID of the specialist (e.g., 'athena-ai', 'apollo-ai')
            message: Message content
            context: Optional context (stored but not used yet)
            timeout: Response timeout in seconds
            
        Returns:
            Response from specialist with success status
        """
        try:
            result = await self.ai_manager.send_to_ai(specialist_id, message)
            
            # Log context if provided (for future use)
            if context:
                logger.debug(f"Context provided for {specialist_id}: {context}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to send message to {specialist_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "ai_id": specialist_id
            }
    
    async def get_specialist_info(self, specialist_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specialist.
        
        Args:
            specialist_id: AI specialist ID
            
        Returns:
            Specialist info or None if not found
        """
        try:
            component_id = specialist_id.replace('-ai', '')
            ai_info = self.ai_manager.get_ai_info(component_id)
            
            # Add health status
            ai_info['healthy'] = await self.ai_manager.check_ai_health(specialist_id)
            ai_info['in_roster'] = specialist_id in self.ai_manager.roster
            
            return ai_info
            
        except Exception as e:
            logger.error(f"Failed to get info for {specialist_id}: {e}")
            return None
    
    async def orchestrate_team_chat(self, topic: str, specialists: List[str], 
                                   initial_prompt: str, max_rounds: int = 1,
                                   orchestration_style: str = "pass_through",
                                   timeout: float = 2.0) -> Dict[str, Any]:
        """Orchestrate team chat - simplified version that calls team_chat.
        
        Args:
            topic: Discussion topic
            specialists: List of specialist IDs (empty for all)
            initial_prompt: Initial message
            max_rounds: Number of rounds (ignored for now)
            orchestration_style: Style of orchestration
            timeout: Timeout for responses
            
        Returns:
            Orchestration results
        """
        # If no specialists specified, use all available
        if not specialists:
            all_specialists = await self.list_specialists()
            specialists = [s['id'] for s in all_specialists if s['status'] == 'healthy']
        
        # Call the simpler team_chat method
        result = await self.team_chat(specialists, initial_prompt)
        
        # Format response for compatibility
        return {
            "success": result['success'],
            "responses": result['responses'],
            "topic": topic,
            "orchestration_style": orchestration_style,
            "rounds": 1,
            "summary": result.get('summary')
        }
    
    async def team_chat(self, specialists: List[str], message: str,
                       coordinator: Optional[str] = None) -> Dict[str, Any]:
        """Send a message to multiple specialists for team collaboration.
        
        Args:
            specialists: List of specialist IDs
            message: Message to send
            coordinator: Optional coordinator AI (defaults to numa-ai)
            
        Returns:
            Team chat results
        """
        if not coordinator:
            coordinator = 'numa-ai'
            
        results = {
            'coordinator': coordinator,
            'specialists': specialists,
            'responses': {},
            'summary': None,
            'success': True
        }
        
        try:
            # Send to all specialists
            for specialist_id in specialists:
                response = await self.send_message_to_specialist(specialist_id, message)
                results['responses'][specialist_id] = response
                
                if not response['success']:
                    results['success'] = False
            
            # If we have responses, ask coordinator to summarize
            if results['success'] and coordinator not in specialists:
                successful_responses = {
                    sid: resp['response'] 
                    for sid, resp in results['responses'].items() 
                    if resp['success']
                }
                
                if successful_responses:
                    summary_prompt = f"""As the team coordinator, please synthesize these responses to: "{message}"

Responses:
{json.dumps(successful_responses, indent=2)}

Provide a unified response that combines the key insights."""
                    
                    summary_result = await self.send_message_to_specialist(
                        coordinator, summary_prompt
                    )
                    
                    if summary_result['success']:
                        results['summary'] = summary_result['response']
            
            return results
            
        except Exception as e:
            logger.error(f"Team chat failed: {e}")
            results['success'] = False
            results['error'] = str(e)
            return results
    
    def get_roster(self) -> Dict[str, Dict[str, Any]]:
        """Get current AI roster."""
        return self.ai_manager.get_roster()
    
    async def find_specialist_for_task(self, task_description: str) -> Optional[str]:
        """Find the best specialist for a given task.
        
        Args:
            task_description: Description of the task
            
        Returns:
            Specialist ID or None
        """
        # Simple keyword matching for now
        task_lower = task_description.lower()
        
        # Map keywords to categories
        category_keywords = {
            'ai': ['llm', 'prompt', 'generate', 'chat', 'model'],
            'knowledge': ['graph', 'relationship', 'semantic', 'ontology'],
            'memory': ['remember', 'store', 'recall', 'history'],
            'planning': ['plan', 'schedule', 'organize', 'project'],
            'workflow': ['process', 'automate', 'workflow', 'pipeline'],
            'analysis': ['analyze', 'discover', 'pattern', 'insight']
        }
        
        # Find matching category
        for category, keywords in category_keywords.items():
            if any(keyword in task_lower for keyword in keywords):
                ai_id = await self.ai_manager.find_ai_for_role(category)
                if ai_id:
                    return ai_id
        
        # Default to numa-ai as general coordinator
        if await self.ai_manager.check_ai_health('numa-ai'):
            return 'numa-ai'
            
        return None


# Global instance for easy access
_mcp_tools_integration = None


def get_mcp_tools_integration() -> MCPToolsIntegrationSimple:
    """Get the global MCP tools integration instance."""
    global _mcp_tools_integration
    if _mcp_tools_integration is None:
        _mcp_tools_integration = MCPToolsIntegrationSimple()
    return _mcp_tools_integration


def set_mcp_tools_integration(integration: MCPToolsIntegrationSimple):
    """Set the global MCP tools integration instance."""
    global _mcp_tools_integration
    _mcp_tools_integration = integration