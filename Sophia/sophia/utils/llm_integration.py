"""
Tekton LLM Client Integration for Sophia

This module provides integration with the tekton-llm-client for standardized
access to LLM capabilities following the Tekton shared architecture patterns.
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Callable, AsyncIterator

# Import enhanced tekton-llm-client features
from tekton_llm_client import (
    TektonLLMClient,
    PromptTemplateRegistry, PromptTemplate, load_template,
    JSONParser, parse_json, extract_json,
    StreamHandler, collect_stream, stream_to_string,
    StructuredOutputParser, OutputFormat,
    ClientSettings, LLMSettings, load_settings, get_env
)
from tekton_llm_client.models import (
    ChatMessage, 
    ChatCompletionOptions,
    StreamingChunk
)

# Import Sophia utilities
from sophia.utils.tekton_utils import get_config, get_logger
from shared.urls import rhetor_url as get_rhetor_url

# Set up logging
logger = get_logger("sophia.utils.llm_integration")

# System prompts for different task types
SYSTEM_PROMPTS = {
    "default": "You are Sophia, Tekton's machine learning and continuous improvement component. "
              "You analyze metrics, patterns, and performance data to provide insights and recommendations.",
              
    "analysis": "You are Sophia's Analysis Engine. Examine the following metrics and identify patterns, "
                "trends, anomalies, and potential optimization opportunities. Format your analysis "
                "in a structured, factual manner.",
                
    "recommendation": "You are Sophia's Recommendation System. Generate specific, actionable recommendations "
                      "based on the provided analysis. Focus on concrete improvements with clear impact "
                      "and implementation steps.",
                     
    "experiment": "You are Sophia's Experiment Design System. Design experiments to test hypotheses "
                 "about component performance and optimization. Focus on clear methodology, measurable "
                 "outcomes, and controlled variables.",
                 
    "explanation": "You are Sophia's Explanation System. Translate technical metrics and analysis "
                  "into clear, concise explanations accessible to users with varying technical backgrounds.",
                  
    "intelligence": "You are Sophia's Intelligence Measurement System. Analyze component capabilities "
                   "across multiple intelligence dimensions and provide objective assessments."
}

# Model configuration for different tasks
MODEL_CONFIGURATION = {
    "analysis": {
        "preferred_model": "claude-3-opus-20240229",
        "fallback_model": "claude-3-haiku-20240307",
        "local_fallback": "mistral-7b-instruct",
        "temperature": 0.2,
        "max_tokens": 2000
    },
    "recommendation": {
        "preferred_model": "claude-3-sonnet-20240229",
        "fallback_model": "claude-3-haiku-20240307",
        "local_fallback": "llama-3-8b",
        "temperature": 0.4,
        "max_tokens": 1000
    },
    "experiment": {
        "preferred_model": "claude-3-sonnet-20240229",
        "fallback_model": "claude-3-haiku-20240307",
        "local_fallback": "mistral-7b-instruct",
        "temperature": 0.3,
        "max_tokens": 1500
    },
    "explanation": {
        "preferred_model": "claude-3-sonnet-20240229",
        "fallback_model": "gpt-3.5-turbo",
        "local_fallback": "phi-2",
        "temperature": 0.7,
        "max_tokens": 1500
    },
    "intelligence": {
        "preferred_model": "claude-3-opus-20240229",
        "fallback_model": "claude-3-sonnet-20240229",
        "local_fallback": "mistral-7b-instruct",
        "temperature": 0.3,
        "max_tokens": 2000
    }
}

class SophiaLLMIntegration:
    """
    LLM integration for Sophia using the enhanced tekton-llm-client.
    
    This class provides methods for all LLM-related tasks in Sophia,
    ensuring standardized access to LLM capabilities with proper
    error handling, prompt templates, and response parsing.
    """
    
    def __init__(self, component_id: str = "sophia"):
        """
        Initialize the Sophia LLM integration.
        
        Args:
            component_id: Component ID for tracking
        """
        self.component_id = component_id
        self.is_initialized = False
        self.clients = {}  # Task-specific clients
        
        # Initialize prompt template registry
        self.template_registry = PromptTemplateRegistry()
        
        # Load client settings from environment or config
        self.settings = load_settings("sophia")
        
        # Get default URL and provider from settings or config
        self.base_url = get_env("RHETOR_URL") or get_rhetor_url()  # Use Rhetor
        self.default_provider = get_env("TEKTON_LLM_PROVIDER", "anthropic")
        # Let Rhetor handle model selection based on component and capability
        
        logger.info(f"Initialized Sophia LLM Integration with URL {self.base_url}")
        
    async def initialize(self) -> bool:
        """
        Initialize the LLM clients and load prompt templates.
        
        Returns:
            True if initialization was successful
        """
        if self.is_initialized:
            return True
            
        logger.info("Initializing Sophia LLM Integration...")
        
        # Load prompt templates from standard locations
        self._load_templates()
        
        try:
            # Initialize task-specific clients
            for task_type, config in MODEL_CONFIGURATION.items():
                # Create client settings
                client_settings = ClientSettings(
                    component_id=f"{self.component_id}-{task_type}",
                    base_url=self.base_url,
                    provider_id=self.default_provider,
                    model_id=config["preferred_model"],
                    timeout=60,
                    max_retries=3,
                    use_fallback=True
                )
                
                # Create LLM settings
                llm_settings = LLMSettings(
                    temperature=config["temperature"],
                    max_tokens=config["max_tokens"],
                    top_p=0.95
                )
                
                # Create client
                client = TektonLLMClient(
                    settings=client_settings,
                    llm_settings=llm_settings
                )
                
                # Initialize the client to verify connection
                await client.initialize()
                
                self.clients[task_type] = client
                logger.info(f"Initialized LLM client for {task_type}")
                
            self.is_initialized = True
            logger.info("Sophia LLM Integration initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Sophia LLM Integration: {e}")
            return False
            
    def _load_templates(self) -> None:
        """
        Load prompt templates from standard locations and register predefined templates.
        """
        # First try to load from standard locations
        standard_dirs = [
            "./prompt_templates",
            "./templates",
            "./sophia/templates",
            "./sophia/prompt_templates"
        ]
        
        for template_dir in standard_dirs:
            if os.path.exists(template_dir):
                self.template_registry.load_templates_from_directory(template_dir)
                logger.info(f"Loaded templates from {template_dir}")
        
        # Add core templates
        self.template_registry.register_template(
            "metrics_analysis",
            PromptTemplate(
                template="Analyze the following metrics data from {component_id}:\n\n{metrics_json}\n\n"
                        "Identify patterns, anomalies, and potential optimization opportunities.",
                output_format=OutputFormat.JSON
            )
        )
        
        self.template_registry.register_template(
            "experiment_design",
            PromptTemplate(
                template="Design an experiment to test the hypothesis: {hypothesis}\n\n"
                        "Available components: {components_list}\n"
                        "Recent metrics: {metrics_summary}",
                output_format=OutputFormat.JSON
            )
        )
        
        self.template_registry.register_template(
            "recommendation_generation",
            PromptTemplate(
                template="Based on the following analysis:\n\n{analysis_summary}\n\n"
                        "Generate {count} specific recommendations to improve {target}.",
                output_format=OutputFormat.JSON_ARRAY
            )
        )
        
        self.template_registry.register_template(
            "natural_language_query",
            PromptTemplate(
                template="Context information:\n{context_json}\n\nUser query: {query}",
                output_format=OutputFormat.TEXT
            )
        )
        
        self.template_registry.register_template(
            "intelligence_assessment",
            PromptTemplate(
                template="Assess the intelligence capabilities of {component_id} "
                        "based on the following data:\n\n{data_json}\n\n"
                        "Provide ratings for each intelligence dimension with justification.",
                output_format=OutputFormat.JSON
            )
        )
            
    async def shutdown(self) -> None:
        """
        Shut down all LLM clients.
        """
        for task_type, client in self.clients.items():
            try:
                await client.shutdown()
                logger.info(f"Shut down LLM client for {task_type}")
            except Exception as e:
                logger.error(f"Error shutting down LLM client for {task_type}: {e}")
                
        self.is_initialized = False
        logger.info("Sophia LLM Integration shut down")
        
    async def get_client(self, task_type: Optional[str] = None) -> TektonLLMClient:
        """
        Get an LLM client for a specific task type.
        
        Args:
            task_type: Type of task (analysis, recommendation, etc.)
            
        Returns:
            TektonLLMClient for the task
        """
        if not self.is_initialized:
            await self.initialize()
            
        # Use the task-specific client if available, or default to analysis
        client = self.clients.get(task_type) if task_type in self.clients else self.clients.get("analysis")
        
        # If no clients are available, create one for the requested task
        if client is None:
            config = MODEL_CONFIGURATION.get(task_type, MODEL_CONFIGURATION["analysis"])
            
            # Create client settings
            client_settings = ClientSettings(
                component_id=f"{self.component_id}-{task_type or 'default'}",
                base_url=self.base_url,
                provider_id=self.default_provider,
                model_id=config["preferred_model"],
                timeout=60,
                max_retries=3,
                use_fallback=True
            )
            
            # Create LLM settings
            llm_settings = LLMSettings(
                temperature=config["temperature"],
                max_tokens=config["max_tokens"],
                top_p=0.95
            )
            
            # Create client
            client = TektonLLMClient(
                settings=client_settings,
                llm_settings=llm_settings
            )
            
            # Initialize the client
            await client.initialize()
            
            # Store the client for future use
            if task_type:
                self.clients[task_type] = client
                
        return client
        
    async def analyze_metrics(
        self, 
        metrics_data: Dict[str, Any], 
        component_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze metrics data using LLM.
        
        Args:
            metrics_data: Metrics data to analyze
            component_id: Optional component ID for context
            
        Returns:
            Analysis results
        """
        client = await self.get_client("analysis")
        
        try:
            # Get the metrics analysis template
            template = self.template_registry.get_template("metrics_analysis")
            
            # Format values for the template
            template_values = {
                "component_id": component_id or "all components",
                "metrics_json": json.dumps(metrics_data, indent=2)
            }
            
            # Create system prompt
            system_prompt = SYSTEM_PROMPTS["analysis"]
            
            # Generate response
            response = await client.generate_text(
                prompt=template.format(**template_values),
                system_prompt=system_prompt
            )
            
            # Parse JSON response using JSONParser
            parser = JSONParser()
            structured_analysis = parser.parse(response.content)
            
            # Return combined result
            return {
                "analysis": response.content,
                "structured": structured_analysis,
                "component_id": component_id,
                "model": response.model,
                "provider": response.provider
            }
            
        except Exception as e:
            logger.error(f"Error analyzing metrics with LLM: {e}")
            return {
                "error": str(e),
                "component_id": component_id,
                "fallback": "Unable to analyze metrics due to LLM service error"
            }
            
    async def generate_recommendations(
        self, 
        analysis_results: Dict[str, Any], 
        target_component: Optional[str] = None,
        count: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on analysis results.
        
        Args:
            analysis_results: Analysis data to base recommendations on
            target_component: Optional target component for recommendations
            count: Number of recommendations to generate
            
        Returns:
            List of recommendation objects
        """
        client = await self.get_client("recommendation")
        
        try:
            # Get the recommendation template
            template = self.template_registry.get_template("recommendation_generation")
            
            # Create summary of analysis results
            analysis_summary = (
                analysis_results["analysis"] 
                if "analysis" in analysis_results 
                else json.dumps(analysis_results, indent=2)
            )
            
            # Format values for the template
            template_values = {
                "analysis_summary": analysis_summary,
                "count": count,
                "target": target_component or "the Tekton ecosystem"
            }
            
            # Create system prompt with formatting instructions
            system_prompt = (
                SYSTEM_PROMPTS["recommendation"] + "\n\n" + 
                "Format your response as a JSON array of recommendation objects with " +
                "'title', 'description', 'impact', 'effort', and 'implementation_steps' fields."
            )
            
            # Generate response
            response = await client.generate_text(
                prompt=template.format(**template_values),
                system_prompt=system_prompt
            )
            
            # Parse JSON array using JSONParser
            parser = JSONParser()
            return parser.parse_array(response.content)
            
        except Exception as e:
            logger.error(f"Error generating recommendations with LLM: {e}")
            return [{
                "error": str(e),
                "title": "Recommendation Error",
                "description": "Unable to generate recommendations due to LLM service error"
            }]
            
    async def design_experiment(
        self, 
        hypothesis: str, 
        available_components: Optional[List[str]] = None,
        metrics_summary: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Design an experiment to test a hypothesis.
        
        Args:
            hypothesis: The hypothesis to test
            available_components: List of components available for the experiment
            metrics_summary: Summary of recent metrics
            
        Returns:
            Experiment design
        """
        client = await self.get_client("experiment")
        
        try:
            # Get the experiment design template
            template = self.template_registry.get_template("experiment_design")
            
            # Format components list
            components_list = (
                ", ".join(available_components) 
                if available_components 
                else "all available components"
            )
            
            # Format metrics summary
            metrics_json = (
                json.dumps(metrics_summary, indent=2)
                if metrics_summary
                else "No metrics summary provided"
            )
            
            # Format values for the template
            template_values = {
                "hypothesis": hypothesis,
                "components_list": components_list,
                "metrics_summary": metrics_json
            }
            
            # Create system prompt with formatting instructions
            system_prompt = (
                SYSTEM_PROMPTS["experiment"] + "\n\n" + 
                "Format your response as a JSON object with 'title', 'hypothesis', " +
                "'methodology', 'components', 'metrics', 'variables', 'control_condition', " +
                "'test_condition', and 'success_criteria' fields."
            )
            
            # Generate response with structured output parser
            response = await client.generate_text(
                prompt=template.format(**template_values),
                system_prompt=system_prompt
            )
            
            # Parse JSON using JSONParser
            parser = JSONParser()
            return parser.parse(response.content)
            
        except Exception as e:
            logger.error(f"Error designing experiment with LLM: {e}")
            return {
                "error": str(e),
                "title": "Experiment Design Error",
                "hypothesis": hypothesis,
                "message": "Unable to design experiment due to LLM service error"
            }
            
    async def explain_analysis(
        self, 
        analysis_data: Dict[str, Any],
        audience: str = "technical"
    ) -> str:
        """
        Explain analysis results in human-readable form.
        
        Args:
            analysis_data: Analysis data to explain
            audience: Target audience ("technical", "executive", "general")
            
        Returns:
            Human-readable explanation
        """
        client = await self.get_client("explanation")
        
        try:
            # Create system prompt with audience targeting
            system_prompt = SYSTEM_PROMPTS["explanation"] + f"\n\nTarget audience: {audience}"
            
            # Create prompt with analysis data
            prompt = (f"Explain the following analysis results in a way appropriate for a {audience} "
                      f"audience:\n\n{json.dumps(analysis_data, indent=2)}")
            
            # Generate response
            response = await client.generate_text(
                prompt=prompt,
                system_prompt=system_prompt
            )
            
            return response.content
            
        except Exception as e:
            logger.error(f"Error explaining analysis with LLM: {e}")
            return f"Unable to generate explanation due to service error: {str(e)}"
            
    async def process_natural_language_query(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a natural language query about metrics or analysis.
        
        Args:
            query: The natural language query
            context: Optional context information
            
        Returns:
            Response to the query
        """
        client = await self.get_client()
        
        try:
            # Get the natural language query template
            template = self.template_registry.get_template("natural_language_query")
            
            # Create context if not provided
            if context is None:
                context = {"query_time": "current time", "system_state": "normal"}
                
            # Format values for the template
            template_values = {
                "context_json": json.dumps(context, indent=2),
                "query": query
            }
            
            # Generate response
            response = await client.generate_text(
                prompt=template.format(**template_values),
                system_prompt=SYSTEM_PROMPTS["default"]
            )
            
            return {
                "query": query,
                "response": response.content,
                "type": "natural_language"
            }
            
        except Exception as e:
            logger.error(f"Error processing natural language query with LLM: {e}")
            return {
                "query": query,
                "response": f"I'm sorry, I couldn't process your query due to a service error: {str(e)}",
                "type": "error"
            }
            
    async def assess_intelligence(
        self,
        component_id: str,
        component_data: Dict[str, Any],
        dimensions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Assess the intelligence of a component across dimensions.
        
        Args:
            component_id: ID of the component to assess
            component_data: Data about the component's capabilities
            dimensions: Specific dimensions to assess (all if None)
            
        Returns:
            Intelligence assessment with scores and justifications
        """
        client = await self.get_client("intelligence")
        
        try:
            # Get the intelligence assessment template
            template = self.template_registry.get_template("intelligence_assessment")
            
            # Add dimensions to the component data if provided
            if dimensions:
                component_data["dimensions_to_assess"] = dimensions
                
            # Format values for the template
            template_values = {
                "component_id": component_id,
                "data_json": json.dumps(component_data, indent=2)
            }
            
            # Create system prompt with instructions
            system_prompt = (
                SYSTEM_PROMPTS["intelligence"] + "\n\n" +
                "Format your response as a JSON object with a 'dimensions' field containing " +
                "ratings and justifications for each intelligence dimension."
            )
            
            # Generate structured response
            response = await client.generate_text(
                prompt=template.format(**template_values),
                system_prompt=system_prompt
            )
            
            # Parse JSON using JSONParser
            parser = JSONParser()
            return parser.parse(response.content)
            
        except Exception as e:
            logger.error(f"Error assessing intelligence with LLM: {e}")
            return {
                "error": str(e),
                "component_id": component_id,
                "message": "Unable to assess intelligence due to LLM service error"
            }
            
    async def stream_explanation(
        self, 
        analysis_id: str,
        callback: Callable[[str], None]
    ) -> None:
        """
        Stream an explanation of the analysis, delivering chunks via callback.
        
        Args:
            analysis_id: ID of the analysis to explain
            callback: Function to call with each content chunk
        """
        client = await self.get_client("explanation")
        
        try:
            # Create system prompt
            system_prompt = SYSTEM_PROMPTS["explanation"]
            
            # Create prompt
            prompt = (f"Explain analysis {analysis_id} in detail, covering the methods used, "
                      f"findings, and recommendations.")
            
            # Create StreamHandler with the callback
            stream_handler = StreamHandler(callback_fn=callback)
            
            # Start streaming with the handler
            response_stream = await client.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                streaming=True
            )
            
            # Process the stream with the handler
            await stream_handler.process_stream(response_stream)
                
        except Exception as e:
            logger.error(f"Error streaming explanation with LLM: {e}")
            callback(f"\nError: Unable to complete explanation due to service error: {str(e)}")
            
# Global singleton instance
_llm_integration = SophiaLLMIntegration()

async def get_llm_integration() -> SophiaLLMIntegration:
    """
    Get the global LLM integration instance.
    
    Returns:
        SophiaLLMIntegration instance
    """
    if not _llm_integration.is_initialized:
        await _llm_integration.initialize()
    return _llm_integration