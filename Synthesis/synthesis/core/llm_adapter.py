"""
LLM Adapter for Synthesis

This module provides integration with Tekton's LLM capabilities using the tekton-llm-client library.
It enables Synthesis to use LLM capabilities for dynamic execution, plan enhancement, and result interpretation.
"""

import os
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Callable, AsyncIterator

from tekton_llm_client import TektonLLMClient
from tekton_llm_client.models import Message, CompletionOptions, MessageRole
from tekton_llm_client.adapters import LocalFallbackAdapter
from tekton_llm_client.exceptions import TektonLLMError

logger = logging.getLogger(__name__)

class LLMAdapter:
    """
    Adapter for integrating with Tekton LLM capabilities using the standardized client.
    Provides methods for enhancing execution plans, validating execution results, and
    generating dynamic content during execution.
    """
    
    def __init__(self, component_id: str = "synthesis"):
        """
        Initialize the LLM adapter.
        
        Args:
            component_id: The component identifier for client registration
        """
        self.component_id = component_id
        self.client = None
        self.initialized = False
        self.fallback_enabled = True
        
        # LLM-related configuration
        self.base_url = os.getenv("TEKTON_LLM_URL", "http://localhost:8001")
        self.default_model = os.getenv("TEKTON_LLM_MODEL", "default")
        self.timeout = int(os.getenv("TEKTON_LLM_TIMEOUT", "60"))
        
        # Fallback settings
        self.fallback_models = [
            "claude-3-haiku-20240307",
            "local-small-model"
        ]
        
    async def initialize(self) -> bool:
        """
        Initialize the LLM client connection.
        
        Returns:
            True if initialization was successful
        """
        try:
            adapter = None
            if self.fallback_enabled:
                adapter = LocalFallbackAdapter(
                    fallback_models=self.fallback_models,
                    max_retries=2,
                    timeout=self.timeout
                )
            
            self.client = TektonLLMClient(
                base_url=self.base_url,
                default_model=self.default_model,
                timeout=self.timeout,
                adapter=adapter
            )
            
            logger.info(f"LLM adapter initialized with base URL: {self.base_url}")
            self.initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM adapter: {e}")
            self.initialized = False
            return False
    
    async def ensure_initialized(self) -> bool:
        """
        Ensure the client is initialized before use.
        
        Returns:
            True if client is initialized
        """
        if not self.initialized:
            return await self.initialize()
        return True
    
    async def shutdown(self) -> None:
        """Shutdown the LLM client."""
        if self.client:
            self.initialized = False
            logger.info("LLM adapter shutdown")
    
    async def enhance_execution_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance an execution plan using LLM capabilities.
        
        Args:
            plan: The original execution plan
            
        Returns:
            Enhanced execution plan
        """
        if not await self.ensure_initialized():
            logger.warning("LLM adapter not initialized, returning original plan")
            return plan
        
        try:
            messages = [
                Message(
                    role=MessageRole.SYSTEM,
                    content=(
                        "You are an AI assistant that enhances execution plans for Synthesis, "
                        "Tekton's execution and integration engine. Your task is to analyze "
                        "the provided execution plan and make improvements by:\n"
                        "1. Adding error handling and retry logic where appropriate\n"
                        "2. Optimizing parallel execution opportunities\n"
                        "3. Adding validation steps for critical operations\n"
                        "4. Enhancing variable usage for better context preservation\n\n"
                        "Return the enhanced plan as valid JSON that can be parsed directly."
                    )
                ),
                Message(
                    role=MessageRole.USER,
                    content=f"Enhance the following execution plan:\n\n```json\n{plan}\n```"
                )
            ]
            
            options = CompletionOptions(
                temperature=0.2,
                max_tokens=4000
            )
            
            response = await self.client.chat_completion(
                messages=messages, 
                options=options
            )
            
            # Extract JSON response
            response_text = response.choices[0].message.content
            
            # Simple JSON extraction from markdown
            import json
            import re
            
            json_match = re.search(r"```(?:json)?\s*\n([\s\S]*?)\n```", response_text)
            if json_match:
                json_str = json_match.group(1)
                enhanced_plan = json.loads(json_str)
                logger.info("Successfully enhanced execution plan with LLM")
                return enhanced_plan
            
            # Fallback if no markdown code block is found
            try:
                enhanced_plan = json.loads(response_text)
                return enhanced_plan
            except json.JSONDecodeError:
                logger.warning("Could not parse enhanced plan as JSON, returning original")
                return plan
                
        except TektonLLMError as e:
            logger.error(f"LLM error enhancing plan: {e}")
            return plan
        except Exception as e:
            logger.error(f"Unexpected error enhancing plan: {e}")
            return plan
    
    async def analyze_execution_result(self, 
                                     execution_id: str, 
                                     result: Dict[str, Any], 
                                     plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze execution results using LLM capabilities.
        
        Args:
            execution_id: The execution identifier
            result: The execution result
            plan: The original execution plan
            
        Returns:
            Analysis of the execution result
        """
        if not await self.ensure_initialized():
            logger.warning("LLM adapter not initialized, returning basic analysis")
            return {"success": result.get("success", False), "analysis": "LLM unavailable"}
        
        try:
            messages = [
                Message(
                    role=MessageRole.SYSTEM,
                    content=(
                        "You are an AI assistant that analyzes execution results for Synthesis, "
                        "Tekton's execution and integration engine. Your task is to analyze "
                        "the provided execution result against the original plan and provide insights by:\n"
                        "1. Identifying successful and failed steps\n"
                        "2. Analyzing error patterns and suggesting improvements\n"
                        "3. Recommending optimizations for future executions\n"
                        "4. Highlighting any unexpected behavior or outcomes\n\n"
                        "Provide your analysis in a structured JSON format with the following keys:\n"
                        "- success: boolean indicating overall success\n"
                        "- summary: brief text summary of the execution\n"
                        "- issues: array of identified issues\n"
                        "- recommendations: array of recommendations for improvement"
                    )
                ),
                Message(
                    role=MessageRole.USER,
                    content=(
                        f"Analyze the following execution result for execution {execution_id}:\n\n"
                        f"Original plan:\n```json\n{plan}\n```\n\n"
                        f"Execution result:\n```json\n{result}\n```"
                    )
                )
            ]
            
            options = CompletionOptions(
                temperature=0.2,
                max_tokens=2000
            )
            
            response = await self.client.chat_completion(
                messages=messages, 
                options=options
            )
            
            # Extract JSON response
            response_text = response.choices[0].message.content
            
            # Process the response to extract JSON
            import json
            import re
            
            json_match = re.search(r"```(?:json)?\s*\n([\s\S]*?)\n```", response_text)
            if json_match:
                json_str = json_match.group(1)
                analysis = json.loads(json_str)
                logger.info("Successfully analyzed execution result with LLM")
                return analysis
            
            # Fallback if no markdown code block is found
            try:
                analysis = json.loads(response_text)
                return analysis
            except json.JSONDecodeError:
                logger.warning("Could not parse analysis as JSON, returning text analysis")
                return {
                    "success": result.get("success", False),
                    "summary": response_text,
                    "issues": [],
                    "recommendations": []
                }
                
        except TektonLLMError as e:
            logger.error(f"LLM error analyzing result: {e}")
            return {"success": result.get("success", False), "analysis": f"Error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error analyzing result: {e}")
            return {"success": result.get("success", False), "analysis": f"Error: {str(e)}"}
    
    async def generate_dynamic_command(self, 
                                    context: Dict[str, Any], 
                                    instruction: str) -> str:
        """
        Generate a dynamic command based on context and instruction.
        
        Args:
            context: The execution context
            instruction: The instruction for command generation
            
        Returns:
            Generated command string
        """
        if not await self.ensure_initialized():
            logger.warning("LLM adapter not initialized, returning placeholder command")
            return "echo 'LLM unavailable for dynamic command generation'"
        
        try:
            messages = [
                Message(
                    role=MessageRole.SYSTEM,
                    content=(
                        "You are an AI assistant that generates shell commands for Synthesis, "
                        "Tekton's execution and integration engine. Your task is to generate "
                        "a valid shell command based on the provided context and instruction. "
                        "Generate only the command itself without explanation or markdown formatting. "
                        "Ensure the command is properly escaped and secure."
                    )
                ),
                Message(
                    role=MessageRole.USER,
                    content=(
                        f"Context:\n```json\n{context}\n```\n\n"
                        f"Instruction: {instruction}\n\n"
                        f"Generate a shell command that accomplishes this instruction based on the context."
                    )
                )
            ]
            
            options = CompletionOptions(
                temperature=0.2,
                max_tokens=500
            )
            
            response = await self.client.chat_completion(
                messages=messages, 
                options=options
            )
            
            command = response.choices[0].message.content.strip()
            
            # Remove markdown code block formatting if present
            if command.startswith("```") and command.endswith("```"):
                command = command[3:-3].strip()
                
            # Remove language identifier if present
            import re
            command = re.sub(r"^(bash|sh)\n", "", command)
            
            logger.info(f"Generated dynamic command with LLM: {command}")
            return command
                
        except TektonLLMError as e:
            logger.error(f"LLM error generating command: {e}")
            return f"echo 'Error generating dynamic command: {str(e)}'"
        except Exception as e:
            logger.error(f"Unexpected error generating command: {e}")
            return f"echo 'Error generating dynamic command: {str(e)}'"
    
    async def stream_execution_analysis(self, 
                                     execution_data: Dict[str, Any],
                                     callback: Callable[[str, bool], None]) -> None:
        """
        Stream execution analysis in real-time.
        
        Args:
            execution_data: The execution data to analyze
            callback: Function to call with each chunk of analysis and done flag
        """
        if not await self.ensure_initialized():
            callback("LLM streaming unavailable. Analysis cannot be provided.", True)
            return
        
        try:
            messages = [
                Message(
                    role=MessageRole.SYSTEM,
                    content=(
                        "You are an AI assistant that provides real-time analysis of execution data "
                        "for Synthesis, Tekton's execution and integration engine. Your task is to "
                        "analyze the provided execution data and provide insights in a conversational "
                        "manner. Focus on explaining what's happening, highlighting important details, "
                        "and providing context that would be helpful to a user monitoring this execution."
                    )
                ),
                Message(
                    role=MessageRole.USER,
                    content=f"Provide a real-time analysis of this execution data:\n\n```json\n{execution_data}\n```"
                )
            ]
            
            options = CompletionOptions(
                temperature=0.3,
                max_tokens=1500,
                stream=True
            )
            
            async for chunk in self.client.stream_chat_completion(
                messages=messages, 
                options=options
            ):
                content = chunk.choices[0].delta.content
                done = chunk.choices[0].finish_reason is not None
                
                if content:
                    callback(content, done)
                
                if done:
                    callback("", True)
                    
        except TektonLLMError as e:
            logger.error(f"LLM streaming error: {e}")
            callback(f"Error in LLM analysis: {str(e)}", True)
        except Exception as e:
            logger.error(f"Unexpected streaming error: {e}")
            callback(f"Unexpected error in analysis: {str(e)}", True)

# Global singleton instance
_llm_adapter = LLMAdapter()

async def get_llm_adapter() -> LLMAdapter:
    """
    Get the global LLM adapter instance.
    
    Returns:
        The initialized LLM adapter
    """
    if not _llm_adapter.initialized:
        await _llm_adapter.initialize()
    return _llm_adapter