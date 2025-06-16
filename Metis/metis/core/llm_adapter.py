#!/usr/bin/env python3
"""
LLM Adapter for Metis Task Management System

This module implements an adapter for interacting with the Tekton LLM service,
providing AI-powered task decomposition and analysis capabilities.
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# Import enhanced tekton-llm-client features
from tekton_llm_client import (
    TektonLLMClient,
    PromptTemplateRegistry, PromptTemplate, load_template,
    JSONParser, parse_json, extract_json,
    StreamHandler, collect_stream, stream_to_string,
    StructuredOutputParser, OutputFormat,
    ClientSettings, LLMSettings, load_settings, get_env
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("metis.llm_adapter")

class MetisLLMAdapter:
    """
    LLM Adapter for Metis task management.
    
    This class provides AI-powered capabilities for task decomposition,
    complexity analysis, and intelligent task management.
    """
    
    def __init__(self, adapter_url: Optional[str] = None):
        """
        Initialize the Metis LLM Adapter.
        
        Args:
            adapter_url: URL for the LLM adapter service (defaults to Rhetor port)
        """
        # Load client settings from environment
        rhetor_port = get_env("RHETOR_PORT")
        default_adapter_url = f"http://localhost:{rhetor_port}"
        
        self.adapter_url = adapter_url or get_env("LLM_ADAPTER_URL", default_adapter_url)
        self.default_provider = get_env("LLM_PROVIDER", "anthropic")
        self.default_model = get_env("LLM_MODEL", "claude-3-haiku-20240307")
        
        # Initialize client settings
        self.client_settings = ClientSettings(
            component_id="metis.task_manager",
            base_url=self.adapter_url,
            provider_id=self.default_provider,
            model_id=self.default_model,
            timeout=120,
            max_retries=3,
            use_fallback=True
        )
        
        # Initialize LLM settings
        self.llm_settings = LLMSettings(
            temperature=0.7,
            max_tokens=2000,
            top_p=0.95
        )
        
        # Create LLM client (will be initialized on first use)
        self.llm_client = None
        
        # Initialize template registry
        self.template_registry = PromptTemplateRegistry(load_defaults=False)
        
        # Load prompt templates
        self._load_templates()
        
        logger.info(f"Metis LLM Adapter initialized with URL: {self.adapter_url}")
    
    def _load_templates(self):
        """Load prompt templates for Metis"""
        # First try to load from standard locations
        standard_dirs = [
            "./prompt_templates",
            "./metis/prompt_templates",
            "../prompt_templates",
            os.path.join(os.path.dirname(__file__), "../prompt_templates")
        ]
        
        # Try to load templates from directories
        for template_dir in standard_dirs:
            if os.path.exists(template_dir):
                try:
                    for filename in os.listdir(template_dir):
                        if filename.endswith(('.json', '.yaml', '.yml')) and not filename.startswith('README'):
                            template_path = os.path.join(template_dir, filename)
                            template_name = os.path.splitext(filename)[0]
                            try:
                                template = load_template(template_path)
                                if template:
                                    self.template_registry.register(template)
                                    logger.info(f"Loaded template '{template_name}' from {template_path}")
                            except Exception as e:
                                logger.warning(f"Failed to load template '{template_name}': {e}")
                    logger.info(f"Loaded templates from {template_dir}")
                except Exception as e:
                    logger.warning(f"Error loading templates from {template_dir}: {e}")
        
        # Add core templates programmatically
        self._register_core_templates()
    
    def _register_core_templates(self):
        """Register core templates for task management"""
        # Task decomposition template
        self.template_registry.register({
            "name": "task_decomposition",
            "version": "1.0.0",
            "description": "Decompose high-level tasks into actionable subtasks",
            "template": """Given the following task, decompose it into smaller, actionable subtasks.

Task Title: {{ task_title }}
Task Description: {{ task_description }}
Maximum Depth: {{ depth }}
Maximum Subtasks: {{ max_subtasks }}

Please break down this task into concrete, specific subtasks that:
1. Are actionable and measurable
2. Have clear deliverables
3. Can be estimated in hours
4. Follow a logical execution order

Provide the response in JSON format:
{
  "subtasks": [
    {
      "title": "Subtask title",
      "description": "Clear description of what needs to be done",
      "estimated_hours": 2,
      "complexity": "low|medium|high",
      "dependencies": ["other subtask titles if any"],
      "order": 1
    }
  ]
}""",
            "variables": ["task_title", "task_description", "depth", "max_subtasks"],
            "examples": []
        })
        
        # Complexity analysis template
        self.template_registry.register({
            "name": "task_complexity_analysis",
            "version": "1.0.0",
            "description": "Analyze task complexity with AI",
            "template": """Analyze the complexity of the following task:

Task Title: {{ task_title }}
Task Description: {{ task_description }}
Current Subtasks: {{ subtasks }}

Please evaluate the task complexity considering:
1. Technical difficulty
2. Time requirements
3. Dependencies and interdependencies
4. Required expertise
5. Risk factors

Provide a detailed complexity analysis in JSON format:
{
  "complexity_score": 1-10,
  "complexity_level": "low|medium|high|critical",
  "factors": {
    "technical_difficulty": 1-10,
    "time_complexity": 1-10,
    "dependency_complexity": 1-10,
    "expertise_required": 1-10,
    "risk_level": 1-10
  },
  "explanation": "Detailed explanation of the complexity assessment",
  "recommendations": ["List of recommendations to manage complexity"]
}""",
            "variables": ["task_title", "task_description", "subtasks"]
        })
        
        # Task ordering template
        self.template_registry.register({
            "name": "task_ordering",
            "version": "1.0.0",
            "description": "Suggest optimal task execution order",
            "template": """Given the following tasks with their dependencies, suggest an optimal execution order:

Tasks:
{{ tasks }}

Dependencies:
{{ dependencies }}

Consider:
1. Dependency constraints
2. Resource optimization
3. Risk mitigation
4. Parallel execution opportunities

Provide the optimal order in JSON format:
{
  "execution_order": [
    {
      "task_id": "task_id",
      "order": 1,
      "can_parallel_with": ["other_task_ids"],
      "reasoning": "Why this order"
    }
  ],
  "critical_path": ["task_ids in critical path"],
  "estimated_total_time": "hours"
}""",
            "variables": ["tasks", "dependencies"]
        })
    
    async def _get_client(self) -> TektonLLMClient:
        """
        Get or initialize the LLM client
        
        Returns:
            Initialized TektonLLMClient
        """
        if self.llm_client is None:
            self.llm_client = TektonLLMClient(
                component_id=self.client_settings.component_id,
                rhetor_url=self.adapter_url,
                provider_id=self.default_provider,
                model_id=self.default_model,
                timeout=self.client_settings.timeout,
                max_retries=self.client_settings.max_retries,
                use_fallback=self.client_settings.use_fallback
            )
        return self.llm_client
    
    async def decompose_task(self, 
                           task_title: str,
                           task_description: str,
                           depth: int = 2,
                           max_subtasks: int = 10,
                           model: Optional[str] = None) -> Dict[str, Any]:
        """
        Decompose a task into subtasks using AI.
        
        Args:
            task_title: Title of the task to decompose
            task_description: Detailed description of the task
            depth: Maximum decomposition depth
            max_subtasks: Maximum number of subtasks to generate
            model: LLM model to use (optional)
            
        Returns:
            Dictionary containing decomposed subtasks and metadata
        """
        try:
            # Render the prompt
            prompt = self.template_registry.render(
                "task_decomposition",
                task_title=task_title,
                task_description=task_description,
                depth=depth,
                max_subtasks=max_subtasks
            )
            
            # Get LLM client
            client = await self._get_client()
            
            # Create custom settings if model is provided
            settings = self.llm_settings
            if model:
                settings = LLMSettings(
                    model=model,
                    temperature=0.3,  # Lower temperature for structured output
                    max_tokens=3000,  # Higher limit for detailed decomposition
                    top_p=0.95
                )
            
            # Prepare options with model and temperature settings
            options = {
                "temperature": settings.temperature if model else 0.3,
                "max_tokens": settings.max_tokens if model else 3000,
                "top_p": settings.top_p if model else 0.95
            }
            if model:
                options["model"] = model
            
            # Call LLM
            response = await client.generate_text(
                prompt=prompt,
                system_prompt="You are an expert project manager skilled at breaking down complex tasks into manageable subtasks. Always respond with valid JSON.",
                options=options
            )
            
            # Parse JSON response
            result = parse_json(response.content)
            
            if result and "subtasks" in result:
                return {
                    "success": True,
                    "subtasks": result["subtasks"],
                    "model": response.model,
                    "provider": response.provider,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                logger.error("Invalid response format from LLM")
                return {
                    "success": False,
                    "error": "Invalid response format",
                    "raw_response": response.content
                }
                
        except Exception as e:
            logger.error(f"Task decomposition error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "subtasks": []
            }
    
    async def analyze_task_complexity(self,
                                    task_title: str,
                                    task_description: str,
                                    subtasks: Optional[List[Dict]] = None,
                                    model: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze task complexity using AI.
        
        Args:
            task_title: Title of the task
            task_description: Task description
            subtasks: List of subtasks (optional)
            model: LLM model to use (optional)
            
        Returns:
            Dictionary containing complexity analysis
        """
        try:
            # Format subtasks for the prompt
            subtasks_str = ""
            if subtasks:
                subtasks_str = json.dumps(subtasks, indent=2)
            
            # Render the prompt
            prompt = self.template_registry.render(
                "task_complexity_analysis",
                task_title=task_title,
                task_description=task_description,
                subtasks=subtasks_str
            )
            
            # Get LLM client
            client = await self._get_client()
            
            # Create custom settings
            settings = self.llm_settings
            if model:
                settings = LLMSettings(
                    model=model,
                    temperature=0.3,
                    max_tokens=2000,
                    top_p=0.95
                )
            
            # Prepare options
            options = {
                "temperature": settings.temperature if model else 0.3,
                "max_tokens": settings.max_tokens if model else 2000,
                "top_p": settings.top_p if model else 0.95
            }
            if model:
                options["model"] = model
            
            # Call LLM
            response = await client.generate_text(
                prompt=prompt,
                system_prompt="You are an expert at analyzing task complexity and providing actionable insights. Always respond with valid JSON.",
                options=options
            )
            
            # Parse JSON response
            result = parse_json(response.content)
            
            if result and "complexity_score" in result:
                return {
                    "success": True,
                    "analysis": result,
                    "model": response.model,
                    "provider": response.provider,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                logger.error("Invalid complexity analysis format")
                return {
                    "success": False,
                    "error": "Invalid response format",
                    "raw_response": response.content
                }
                
        except Exception as e:
            logger.error(f"Complexity analysis error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "analysis": {}
            }
    
    async def suggest_task_order(self,
                               tasks: List[Dict],
                               dependencies: List[Dict],
                               model: Optional[str] = None) -> Dict[str, Any]:
        """
        Suggest optimal task execution order.
        
        Args:
            tasks: List of tasks with their properties
            dependencies: List of task dependencies
            model: LLM model to use (optional)
            
        Returns:
            Dictionary containing execution order suggestions
        """
        try:
            # Render the prompt
            prompt = self.template_registry.render(
                "task_ordering",
                tasks=json.dumps(tasks, indent=2),
                dependencies=json.dumps(dependencies, indent=2)
            )
            
            # Get LLM client
            client = await self._get_client()
            
            # Create custom settings
            settings = self.llm_settings
            if model:
                settings = LLMSettings(
                    model=model,
                    temperature=0.3,
                    max_tokens=2000,
                    top_p=0.95
                )
            
            # Prepare options
            options = {
                "temperature": settings.temperature if model else 0.3,
                "max_tokens": settings.max_tokens if model else 2000,
                "top_p": settings.top_p if model else 0.95
            }
            if model:
                options["model"] = model
            
            # Call LLM
            response = await client.generate_text(
                prompt=prompt,
                system_prompt="You are an expert at project planning and task scheduling. Always respond with valid JSON.",
                options=options
            )
            
            # Parse JSON response
            result = parse_json(response.content)
            
            if result and "execution_order" in result:
                return {
                    "success": True,
                    "order": result,
                    "model": response.model,
                    "provider": response.provider,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                logger.error("Invalid task order format")
                return {
                    "success": False,
                    "error": "Invalid response format",
                    "raw_response": response.content
                }
                
        except Exception as e:
            logger.error(f"Task ordering error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "order": {}
            }
    
    async def test_connection(self) -> Dict[str, Any]:
        """
        Test the connection to the LLM service.
        
        Returns:
            Dictionary with connection status and available models
        """
        try:
            # Get LLM client
            client = await self._get_client()
            
            # Try a simple request
            response = await client.generate_text(
                prompt="Hello, this is a test message. Please respond with 'Connection successful!'",
                options={"max_tokens": 50, "temperature": 0.1}
            )
            
            return {
                "connected": True,
                "adapter_url": self.adapter_url,
                "response": response.content,
                "model": response.model,
                "provider": response.provider
            }
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return {
                "connected": False,
                "adapter_url": self.adapter_url,
                "error": str(e)
            }