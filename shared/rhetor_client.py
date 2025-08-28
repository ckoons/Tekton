#!/usr/bin/env python3
"""
Simple Rhetor Client for Component Integration
Provides a clean interface for all components to use Rhetor's LLM capabilities.
"""

import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class RhetorClient:
    """
    Simplified Rhetor client for component LLM operations.
    
    Usage:
        from shared.rhetor_client import RhetorClient
        
        rhetor = RhetorClient(component="metis")
        response = await rhetor.generate("Decompose this task: ...")
    """
    
    def __init__(self, component: str = "default", base_url: str = None):
        """
        Initialize Rhetor client.
        
        Args:
            component: Name of the component using this client
            base_url: Rhetor service URL (defaults to localhost:8103)
        """
        self.component = component
        self.base_url = base_url or "http://localhost:8103"
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
            
    async def _ensure_session(self):
        """Ensure we have an active session."""
        if not self.session:
            self.session = aiohttp.ClientSession()
            
    async def generate(self, 
                      prompt: str,
                      capability: str = "reasoning",
                      system_prompt: Optional[str] = None,
                      temperature: float = 0.7,
                      max_tokens: int = 2000) -> str:
        """
        Generate text using Rhetor's LLM.
        
        Args:
            prompt: The prompt to send
            capability: Type of task (code/planning/reasoning/chat)
            system_prompt: Optional system prompt
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        await self._ensure_session()
        
        # Get the right model for this component/capability
        model = await self._get_model_for_capability(capability)
        
        payload = {
            "prompt": prompt,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "component": self.component,
            "capability": capability
        }
        
        if system_prompt:
            payload["system_prompt"] = system_prompt
            
        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/generate",
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("response", "")
                else:
                    logger.error(f"Rhetor generate failed: {response.status}")
                    return f"Error: Rhetor returned status {response.status}"
        except Exception as e:
            logger.error(f"Rhetor generate error: {e}")
            return f"Error: {str(e)}"
            
    async def chat(self,
                  messages: List[Dict[str, str]],
                  capability: str = "chat",
                  temperature: float = 0.7,
                  max_tokens: int = 2000) -> str:
        """
        Chat conversation using Rhetor's LLM.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            capability: Type of task (usually 'chat')
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            
        Returns:
            Chat response
        """
        await self._ensure_session()
        
        model = await self._get_model_for_capability(capability)
        
        payload = {
            "messages": messages,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "component": self.component,
            "capability": capability
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/chat",
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("response", "")
                else:
                    logger.error(f"Rhetor chat failed: {response.status}")
                    return f"Error: Rhetor returned status {response.status}"
        except Exception as e:
            logger.error(f"Rhetor chat error: {e}")
            return f"Error: {str(e)}"
            
    async def _get_model_for_capability(self, capability: str) -> str:
        """
        Get the assigned model for this component/capability combo.
        
        Args:
            capability: The capability type (code/planning/reasoning/chat)
            
        Returns:
            Model ID to use
        """
        try:
            async with self.session.get(
                f"{self.base_url}/api/models/assignments"
            ) as response:
                if response.status == 200:
                    assignments = await response.json()
                    
                    # Check component-specific assignment
                    component_assignment = assignments.get("components", {}).get(self.component, {})
                    model = component_assignment.get("assignments", {}).get(capability)
                    
                    # Fall back to default if needed
                    if not model or model == "use_default":
                        model = assignments.get("defaults", {}).get(capability)
                        
                    if model:
                        return model
                        
        except Exception as e:
            logger.warning(f"Could not get model assignment: {e}")
            
        # Ultimate fallback
        return "claude-sonnet-4-20250827"
        
    async def analyze(self, 
                     data: Any,
                     analysis_type: str = "general",
                     **kwargs) -> Dict:
        """
        Analyze data using Rhetor's LLM.
        
        Args:
            data: Data to analyze
            analysis_type: Type of analysis
            **kwargs: Additional parameters
            
        Returns:
            Analysis results
        """
        prompt = f"Analyze this {analysis_type} data:\n{json.dumps(data, indent=2)}"
        response = await self.generate(
            prompt=prompt,
            capability="reasoning",
            **kwargs
        )
        
        # Try to parse as JSON, otherwise return as text
        try:
            return json.loads(response)
        except:
            return {"analysis": response}
            
    async def decompose_task(self, 
                            task_title: str,
                            task_description: str,
                            max_subtasks: int = 10) -> Dict:
        """
        Decompose a task into subtasks.
        
        Args:
            task_title: Title of the task
            task_description: Description of the task
            max_subtasks: Maximum number of subtasks
            
        Returns:
            Decomposition results
        """
        prompt = f"""Decompose this task into subtasks (max {max_subtasks}):
Title: {task_title}
Description: {task_description}

Return a JSON list of subtasks with title, description, and estimated_hours."""
        
        response = await self.generate(
            prompt=prompt,
            capability="planning",
            temperature=0.5
        )
        
        try:
            subtasks = json.loads(response)
            return {
                "success": True,
                "subtasks": subtasks
            }
        except:
            return {
                "success": False,
                "error": "Failed to parse subtasks",
                "raw": response
            }
            
    async def close(self):
        """Close the client session."""
        if self.session:
            await self.session.close()
            self.session = None


# Convenience function for one-off requests
async def rhetor_generate(prompt: str, component: str = "default", **kwargs) -> str:
    """
    Quick generation without managing a client.
    
    Usage:
        from shared.rhetor_client import rhetor_generate
        response = await rhetor_generate("Explain this code...", component="sophia")
    """
    async with RhetorClient(component=component) as client:
        return await client.generate(prompt, **kwargs)