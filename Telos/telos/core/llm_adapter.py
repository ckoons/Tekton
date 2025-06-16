#!/usr/bin/env python3
"""
LLM Adapter for Telos Requirements Management System

This module implements an adapter for interacting with the Tekton LLM service,
providing a unified interface for LLM capabilities across the system using
the enhanced tekton-llm-client features.
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, AsyncGenerator, Callable, Awaitable

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
logger = logging.getLogger("telos.llm_adapter")

class LLMAdapter:
    """
    Client for interacting with LLMs through the Tekton LLM Adapter.
    
    This class provides a unified interface for LLM operations, using the
    enhanced tekton-llm-client features for template management, streaming,
    and response handling.
    """
    
    def __init__(self, adapter_url: Optional[str] = None):
        """
        Initialize the LLM Adapter client.
        
        Args:
            adapter_url: URL for the LLM adapter service
        """
        # Load client settings from environment or config
        rhetor_port = get_env("RHETOR_PORT", "8003")
        default_adapter_url = f"http://localhost:{rhetor_port}"
        
        self.adapter_url = adapter_url or get_env("LLM_ADAPTER_URL", default_adapter_url)
        self.default_provider = get_env("LLM_PROVIDER", "anthropic")
        self.default_model = get_env("LLM_MODEL", "claude-3-haiku-20240307")
        
        # Initialize client settings
        self.client_settings = ClientSettings(
            component_id="telos.requirements",
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
            max_tokens=1500,
            top_p=0.95
        )
        
        # Create LLM client (will be initialized on first use)
        self.llm_client = None
        
        # Initialize template registry
        self.template_registry = PromptTemplateRegistry(load_defaults=False)
        
        # Load prompt templates
        self._load_templates()
        
        logger.info(f"LLM Adapter initialized with URL: {self.adapter_url}")
    
    def _load_templates(self):
        """Load prompt templates for Telos"""
        # First try to load from standard locations
        standard_dirs = [
            "./prompt_templates",
            "./templates",
            "./telos/prompt_templates",
            "./telos/templates"
        ]
        
        # Try to load templates from directories
        for template_dir in standard_dirs:
            if os.path.exists(template_dir):
                # Load templates from directory using load_template utility
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
        
        # Register core templates
        self._register_core_templates()
    
    def _register_core_templates(self):
        """Register core prompt templates for Telos"""
        # Requirement analysis template
        self.template_registry.register({
            "name": "requirement_analysis",
            "template": """
            Please analyze this requirement:

            {{ requirement_text }}
            
            {% if context %}
            Consider this additional project context:
            
            {{ context }}
            {% endif %}
            
            Analyze the requirement and evaluate it based on the following quality criteria:
            
            1. Clarity: Is the requirement clear and unambiguous?
            2. Completeness: Does the requirement include all necessary information?
            3. Testability: Can the requirement be verified or tested objectively?
            4. Feasibility: Is the requirement technically and practically achievable?
            5. Consistency: Is the requirement free from contradictions?
            
            Provide a score from 1-5 for each criterion, where 1 is poor and 5 is excellent.
            Also provide specific suggestions for improvement and potential issues to address.
            
            Format your response like this:
            
            Clarity: X/5
            Completeness: X/5
            Testability: X/5
            Feasibility: X/5
            Consistency: X/5
            
            Issues:
            - Issue 1
            - Issue 2
            - Issue 3
            
            Suggestions:
            - Suggestion 1
            - Suggestion 2
            - Suggestion 3
            """,
            "description": "Template for requirement analysis"
        })
        
        # Requirement refinement template
        self.template_registry.register({
            "name": "requirement_refinement",
            "template": """
            Here is the requirement to refine:

            {{ requirement_text }}
            
            Here is the feedback to incorporate:
            
            {{ feedback }}
            
            Please refine this requirement to address the feedback and improve its overall quality.
            
            Return the refined requirement in the same format it was provided, with improved content.
            
            Format your response like this:
            
            Title: [Refined title]
            
            Description: [Refined description]
            
            Type: [Refined type]
            
            Priority: [Refined priority]
            
            Acceptance Criteria:
            - [Refined criteria 1]
            - [Refined criteria 2]
            - [Add more criteria as needed]
            """,
            "description": "Template for requirement refinement"
        })
        
        # Requirement validation template
        self.template_registry.register({
            "name": "requirement_validation",
            "template": """
            Please validate the following requirement against the provided criteria:

            {{ requirement_text }}
            
            Validation Criteria:
            {{ validation_criteria }}
            
            For each criterion, provide a PASS or FAIL assessment with a brief explanation.
            If a criterion is not applicable, mark it as N/A.
            
            For failed criteria, provide specific recommendations to address the issues.
            """,
            "description": "Template for requirement validation"
        })
        
        # Requirements conflict detection template
        self.template_registry.register({
            "name": "conflict_detection",
            "template": """
            Analyze the following set of requirements and identify any potential conflicts, inconsistencies, or dependencies:

            {{ requirements_list }}
            
            For each pair of conflicting requirements, provide:
            1. The IDs of the conflicting requirements
            2. Description of the conflict
            3. Recommendation for resolving the conflict
            
            Format your response as a structured analysis of conflicts and dependencies.
            If no conflicts are found, explicitly state that no conflicts were detected.
            """,
            "description": "Template for requirements conflict detection"
        })
        
        # Acceptance criteria generation template
        self.template_registry.register({
            "name": "acceptance_criteria_generation",
            "template": """
            Generate comprehensive acceptance criteria for the following requirement:

            {{ requirement_text }}
            
            {% if context %}
            Additional project context:
            {{ context }}
            {% endif %}
            
            The acceptance criteria should:
            1. Be specific and measurable
            2. Cover all aspects of the requirement
            3. Be testable
            4. Use clear, consistent terminology
            
            Format your response as a bulleted list of acceptance criteria. Each criterion should start with a verb and describe a specific condition that must be met.
            """,
            "description": "Template for generating acceptance criteria"
        })
        
        # System prompts
        self.template_registry.register({
            "name": "system_requirement_analysis",
            "template": """
            You are an AI assistant specialized in requirements engineering. 
            Analyze requirements and evaluate them based on quality criteria including clarity, completeness, testability, feasibility, and consistency.
            Provide objective assessments and practical suggestions for improvement.
            Format your analysis following the structure requested in the prompt.
            """
        })
        
        self.template_registry.register({
            "name": "system_requirement_refinement",
            "template": """
            You are an AI assistant specialized in requirements engineering.
            Your task is to refine requirements based on feedback provided by the user.
            
            Ensure the refined requirement is:
            1. Clear and unambiguous
            2. Complete with all necessary information
            3. Testable and verifiable
            4. Feasible and realistic
            5. Consistent and non-contradictory
            
            Return the refined requirement in the same format it was provided, with improved content.
            Do not invent technical details that aren't at least implied by the original requirement or feedback.
            """
        })
        
        self.template_registry.register({
            "name": "system_requirement_validation",
            "template": """
            You are an AI assistant specialized in requirements validation.
            Your task is to systematically evaluate requirements against defined validation criteria.
            Provide objective PASS/FAIL assessments with brief explanations.
            For failed criteria, offer specific, actionable recommendations to address the issues.
            """
        })
        
        self.template_registry.register({
            "name": "system_conflict_detection",
            "template": """
            You are an AI assistant specialized in requirements engineering and conflict analysis.
            Your task is to identify conflicts, inconsistencies, and dependencies between requirements.
            Focus on logical contradictions, technical incompatibilities, resource conflicts, and timing issues.
            Provide specific, actionable recommendations for resolving any identified conflicts.
            """
        })
        
        self.template_registry.register({
            "name": "system_acceptance_criteria",
            "template": """
            You are an AI assistant specialized in requirements engineering.
            Your task is to generate comprehensive acceptance criteria for requirements.
            Each criterion should be specific, measurable, testable, and clearly stated.
            Use consistent terminology and follow best practices for acceptance criteria.
            """
        })
    
    async def _get_client(self) -> TektonLLMClient:
        """
        Get or initialize the LLM client
        
        Returns:
            Initialized TektonLLMClient
        """
        if self.llm_client is None:
            self.llm_client = TektonLLMClient(
                settings=self.client_settings,
                llm_settings=self.llm_settings
            )
            await self.llm_client.initialize()
        return self.llm_client
    
    async def chat(self, 
                 messages: List[Dict[str, str]],
                 model: Optional[str] = None,
                 temperature: float = 0.7,
                 max_tokens: Optional[int] = None,
                 stream: bool = False,
                 system_prompt: Optional[str] = None) -> Union[str, AsyncGenerator[str, None]]:
        """
        Send a chat request to the LLM adapter.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: LLM model to use (defaults to configured default)
            temperature: Temperature parameter for generation
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            system_prompt: Optional system prompt
            
        Returns:
            If stream=False, returns the complete response as a string
            If stream=True, returns an async generator yielding response chunks
        """
        try:
            # Get LLM client
            client = await self._get_client()
            
            # Update settings with provided parameters
            custom_settings = LLMSettings(
                temperature=temperature,
                max_tokens=max_tokens or self.llm_settings.max_tokens,
                model=model or self.default_model,
                provider=self.default_provider
            )
            
            # Extract the last user message
            user_message = None
            for message in reversed(messages):
                if message["role"] == "user":
                    user_message = message["content"]
                    break
            
            if not user_message:
                # Default to the last message if no user message is found
                user_message = messages[-1]["content"]
            
            # Determine system prompt to use
            chat_system_prompt = system_prompt
            if not chat_system_prompt:
                for message in messages:
                    if message["role"] == "system":
                        chat_system_prompt = message["content"]
                        break
            
            # If streaming is requested, use streaming approach
            if stream:
                return self._stream_chat(user_message, chat_system_prompt, custom_settings)
            
            # Regular chat request
            response = await client.generate_text(
                prompt=user_message,
                system_prompt=chat_system_prompt,
                settings=custom_settings
            )
            
            return response.content
            
        except Exception as e:
            logger.error(f"LLM request exception: {str(e)}")
            return self._get_fallback_response()
    
    async def _stream_chat(self, 
                         prompt: str,
                         system_prompt: Optional[str],
                         custom_settings: LLMSettings) -> AsyncGenerator[str, None]:
        """
        Stream a chat response from the LLM adapter.
        
        Args:
            prompt: The prompt to send
            system_prompt: Optional system prompt
            custom_settings: LLM settings to use
            
        Yields:
            Response chunks as they arrive
        """
        try:
            # Get LLM client
            client = await self._get_client()
            
            # Create the stream generator
            async def generate_stream():
                try:
                    # Start streaming
                    response_stream = await client.generate_text(
                        prompt=prompt,
                        system_prompt=system_prompt,
                        settings=custom_settings,
                        streaming=True
                    )
                    
                    # Process the stream manually
                    async for chunk in response_stream:
                        if hasattr(chunk, 'chunk') and chunk.chunk:
                            yield chunk.chunk
                        elif isinstance(chunk, str):
                            yield chunk
                            
                except Exception as e:
                    logger.error(f"Error in streaming: {str(e)}")
                    yield f"Error: {str(e)}"
            
            # Return the generator
            return generate_stream()
            
        except Exception as e:
            logger.error(f"Stream setup error: {str(e)}")
            async def error_generator():
                yield self._get_fallback_response()
            return error_generator()
    
    async def analyze_requirement(self, 
                              requirement: Dict[str, Any], 
                              context: Optional[str] = None, 
                              model: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a requirement using the LLM adapter to evaluate quality and suggest improvements.
        
        Args:
            requirement: The requirement dictionary with id, title, description, etc.
            context: Optional additional context about the project
            model: LLM model to use (defaults to configured default)
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Format requirement as text for the LLM
            req_text = f"Requirement ID: {requirement.get('id', 'N/A')}\n"
            req_text += f"Title: {requirement.get('title', 'N/A')}\n"
            req_text += f"Description: {requirement.get('description', 'N/A')}\n"
            req_text += f"Type: {requirement.get('type', 'N/A')}\n"
            req_text += f"Priority: {requirement.get('priority', 'N/A')}\n"
            
            if requirement.get('acceptance_criteria'):
                req_text += "Acceptance Criteria:\n"
                for idx, criteria in enumerate(requirement['acceptance_criteria']):
                    req_text += f"- {criteria}\n"
            
            # Get templates
            template = self.template_registry.get_template("requirement_analysis")
            system_template = self.template_registry.get_template("system_requirement_analysis")
            
            # Format template values
            template_values = {
                "requirement_text": req_text,
                "context": context
            }
            
            # Generate prompt and system prompt
            prompt = template.format(**template_values)
            system_prompt = system_template.format()
            
            # Get LLM client
            client = await self._get_client()
            
            # Create custom settings if model is provided
            settings = None
            if model:
                settings = LLMSettings(
                    model=model,
                    temperature=0.3,  # Lower temperature for analysis tasks
                    max_tokens=2000  # Higher token limit for detailed analysis
                )
            
            # Call LLM and get response
            response = await client.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                settings=settings
            )
            
            # Try to extract structured data from response
            analysis = self._parse_requirement_analysis(response.content)
            
            return {
                "success": True,
                "analysis": analysis,
                "raw_response": response.content,
                "model": response.model,
                "provider": response.provider
            }
        except Exception as e:
            logger.error(f"Requirement analysis error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "raw_response": ""
            }
    
    async def refine_requirement(self,
                             requirement: Dict[str, Any],
                             feedback: str,
                             model: Optional[str] = None) -> Dict[str, Any]:
        """
        Refine a requirement based on feedback using the LLM adapter.
        
        Args:
            requirement: The requirement dictionary with id, title, description, etc.
            feedback: User feedback to incorporate into the refinement
            model: LLM model to use (defaults to configured default)
            
        Returns:
            Dictionary with refined requirement
        """
        try:
            # Format requirement as text for the LLM
            req_text = f"Requirement ID: {requirement.get('id', 'N/A')}\n"
            req_text += f"Title: {requirement.get('title', 'N/A')}\n"
            req_text += f"Description: {requirement.get('description', 'N/A')}\n"
            req_text += f"Type: {requirement.get('type', 'N/A')}\n"
            req_text += f"Priority: {requirement.get('priority', 'N/A')}\n"
            
            if requirement.get('acceptance_criteria'):
                req_text += "Acceptance Criteria:\n"
                for idx, criteria in enumerate(requirement['acceptance_criteria']):
                    req_text += f"- {criteria}\n"
            
            # Get templates
            template = self.template_registry.get_template("requirement_refinement")
            system_template = self.template_registry.get_template("system_requirement_refinement")
            
            # Format template values
            template_values = {
                "requirement_text": req_text,
                "feedback": feedback
            }
            
            # Generate prompt and system prompt
            prompt = template.format(**template_values)
            system_prompt = system_template.format()
            
            # Get LLM client
            client = await self._get_client()
            
            # Create custom settings if model is provided
            settings = None
            if model:
                settings = LLMSettings(
                    model=model,
                    temperature=0.4,  # Moderate temperature for refinement
                    max_tokens=2000  # Higher token limit for detailed refinement
                )
            
            # Call LLM and get response
            response = await client.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                settings=settings
            )
            
            # Parse the response to extract refined requirement
            refined = self._parse_refined_requirement(response.content, requirement)
            
            return {
                "success": True,
                "refined_requirement": refined,
                "raw_response": response.content,
                "model": response.model,
                "provider": response.provider
            }
        except Exception as e:
            logger.error(f"Requirement refinement error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "raw_response": ""
            }
    
    async def validate_requirements(self,
                                 requirements: List[Dict[str, Any]],
                                 validation_criteria: List[str],
                                 model: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate a set of requirements against specified criteria using the LLM adapter.
        
        Args:
            requirements: List of requirement dictionaries
            validation_criteria: List of validation criteria to check against
            model: LLM model to use (defaults to configured default)
            
        Returns:
            Dictionary with validation results
        """
        results = []
        
        for requirement in requirements:
            # Format requirement as text for the LLM
            req_text = f"Requirement ID: {requirement.get('id', 'N/A')}\n"
            req_text += f"Title: {requirement.get('title', 'N/A')}\n"
            req_text += f"Description: {requirement.get('description', 'N/A')}\n"
            req_text += f"Type: {requirement.get('type', 'N/A')}\n"
            req_text += f"Priority: {requirement.get('priority', 'N/A')}\n"
            
            if requirement.get('acceptance_criteria'):
                req_text += "Acceptance Criteria:\n"
                for idx, criteria in enumerate(requirement['acceptance_criteria']):
                    req_text += f"- {criteria}\n"
            
            # Format validation criteria as text
            criteria_text = ""
            for idx, criterion in enumerate(validation_criteria):
                criteria_text += f"{idx+1}. {criterion}\n"
            
            try:
                # Get templates
                template = self.template_registry.get_template("requirement_validation")
                system_template = self.template_registry.get_template("system_requirement_validation")
                
                # Format template values
                template_values = {
                    "requirement_text": req_text,
                    "validation_criteria": criteria_text
                }
                
                # Generate prompt and system prompt
                prompt = template.format(**template_values)
                system_prompt = system_template.format()
                
                # Get LLM client
                client = await self._get_client()
                
                # Create custom settings if model is provided
                settings = None
                if model:
                    settings = LLMSettings(
                        model=model,
                        temperature=0.3,  # Lower temperature for validation
                        max_tokens=2000  # Higher token limit for detailed validation
                    )
                
                # Call LLM and get response
                response = await client.generate_text(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    settings=settings
                )
                
                # Process response to extract validation results
                validation_result = self._parse_validation_result(response.content, validation_criteria)
                
                results.append({
                    "requirement_id": requirement.get("id"),
                    "requirement_title": requirement.get("title"),
                    "validation_results": validation_result,
                    "raw_response": response.content,
                    "success": True,
                    "model": response.model,
                    "provider": response.provider
                })
                
            except Exception as e:
                logger.error(f"Requirement validation error for {requirement.get('id')}: {str(e)}")
                results.append({
                    "requirement_id": requirement.get("id"),
                    "requirement_title": requirement.get("title"),
                    "validation_results": {},
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "validation_results": results
        }
    
    async def detect_conflicts(self,
                            requirements: List[Dict[str, Any]],
                            model: Optional[str] = None) -> Dict[str, Any]:
        """
        Detect conflicts between requirements using the LLM adapter.
        
        Args:
            requirements: List of requirement dictionaries
            model: LLM model to use (defaults to configured default)
            
        Returns:
            Dictionary with conflict analysis results
        """
        try:
            # Format requirements as text for the LLM
            requirements_text = ""
            for idx, req in enumerate(requirements):
                requirements_text += f"Requirement {idx+1}:\n"
                requirements_text += f"ID: {req.get('id', 'N/A')}\n"
                requirements_text += f"Title: {req.get('title', 'N/A')}\n"
                requirements_text += f"Description: {req.get('description', 'N/A')}\n"
                requirements_text += f"Type: {req.get('type', 'N/A')}\n"
                requirements_text += f"Priority: {req.get('priority', 'N/A')}\n"
                
                if req.get('acceptance_criteria'):
                    requirements_text += "Acceptance Criteria:\n"
                    for criteria in req.get('acceptance_criteria', []):
                        requirements_text += f"- {criteria}\n"
                        
                requirements_text += "\n"
            
            # Get templates
            template = self.template_registry.get_template("conflict_detection")
            system_template = self.template_registry.get_template("system_conflict_detection")
            
            # Format template values
            template_values = {
                "requirements_list": requirements_text
            }
            
            # Generate prompt and system prompt
            prompt = template.format(**template_values)
            system_prompt = system_template.format()
            
            # Get LLM client
            client = await self._get_client()
            
            # Create custom settings if model is provided
            settings = None
            if model:
                settings = LLMSettings(
                    model=model,
                    temperature=0.3,  # Lower temperature for conflict detection
                    max_tokens=3000  # Higher token limit for detailed conflict analysis
                )
            
            # Call LLM and get response
            response = await client.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                settings=settings
            )
            
            # Extract conflict information from the response
            conflicts = []
            
            # Simple parsing - not sophisticated, but works for basic conflict detection
            # In a real implementation, you might want a more sophisticated parsing approach
            
            # Split the response into sections
            sections = response.content.split("\n\n")
            current_conflict = None
            
            for section in sections:
                if "conflict" in section.lower() and "between" in section.lower():
                    # This might be a conflict description
                    if current_conflict:
                        conflicts.append(current_conflict)
                    
                    # Extract requirement IDs if possible
                    import re
                    id_pattern = r'(?:conflict between|between).*?([a-zA-Z0-9\-_]+).*?and.*?([a-zA-Z0-9\-_]+)'
                    id_match = re.search(id_pattern, section, re.IGNORECASE)
                    
                    req_ids = []
                    if id_match:
                        req_ids = [id_match.group(1), id_match.group(2)]
                    
                    current_conflict = {
                        "requirement_ids": req_ids,
                        "description": section.strip(),
                        "recommendation": ""
                    }
                elif current_conflict and "recommend" in section.lower():
                    # This might be a recommendation for the current conflict
                    current_conflict["recommendation"] = section.strip()
            
            # Add the last conflict if exists
            if current_conflict:
                conflicts.append(current_conflict)
            
            return {
                "success": True,
                "conflicts": conflicts,
                "raw_response": response.content,
                "model": response.model,
                "provider": response.provider
            }
            
        except Exception as e:
            logger.error(f"Conflict detection error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "conflicts": []
            }
    
    async def generate_acceptance_criteria(self,
                                        requirement: Dict[str, Any],
                                        context: Optional[str] = None,
                                        model: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate acceptance criteria for a requirement using the LLM adapter.
        
        Args:
            requirement: The requirement dictionary
            context: Optional additional context about the project
            model: LLM model to use (defaults to configured default)
            
        Returns:
            Dictionary with generated acceptance criteria
        """
        try:
            # Format requirement as text for the LLM
            req_text = f"Requirement ID: {requirement.get('id', 'N/A')}\n"
            req_text += f"Title: {requirement.get('title', 'N/A')}\n"
            req_text += f"Description: {requirement.get('description', 'N/A')}\n"
            req_text += f"Type: {requirement.get('type', 'N/A')}\n"
            req_text += f"Priority: {requirement.get('priority', 'N/A')}\n"
            
            # Get templates
            template = self.template_registry.get_template("acceptance_criteria_generation")
            system_template = self.template_registry.get_template("system_acceptance_criteria")
            
            # Format template values
            template_values = {
                "requirement_text": req_text,
                "context": context
            }
            
            # Generate prompt and system prompt
            prompt = template.format(**template_values)
            system_prompt = system_template.format()
            
            # Get LLM client
            client = await self._get_client()
            
            # Create custom settings if model is provided
            settings = None
            if model:
                settings = LLMSettings(
                    model=model,
                    temperature=0.5,  # Moderate temperature for creativity in criteria
                    max_tokens=2000  # Higher token limit
                )
            
            # Call LLM and get response
            response = await client.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                settings=settings
            )
            
            # Extract acceptance criteria from the response
            criteria = []
            
            # Simple parsing - extract bullet points
            import re
            bullet_pattern = r'[-*•]\s*(.*?)(?:\n|$)'
            matches = re.findall(bullet_pattern, response.content)
            
            criteria = [match.strip() for match in matches if match.strip()]
            
            # If no bullet points found, try splitting by lines
            if not criteria:
                lines = response.content.split('\n')
                criteria = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
            
            return {
                "success": True,
                "acceptance_criteria": criteria,
                "raw_response": response.content,
                "model": response.model,
                "provider": response.provider
            }
            
        except Exception as e:
            logger.error(f"Acceptance criteria generation error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "acceptance_criteria": []
            }
    
    def _parse_requirement_analysis(self, response: str) -> Dict[str, Any]:
        """
        Parse the LLM's response to extract structured analysis data.
        
        Args:
            response: The raw response from the LLM
            
        Returns:
            Dictionary with structured analysis data
        """
        try:
            # Initialize default analysis structure
            analysis = {
                "scores": {
                    "clarity": 0,
                    "completeness": 0,
                    "testability": 0,
                    "feasibility": 0,
                    "consistency": 0
                },
                "suggestions": [],
                "issues": []
            }
            
            # Try to extract scores using regex patterns
            import re
            
            # Extract scores
            score_patterns = {
                "clarity": r"clarity:?\s*(\d+)[/\s]*5",
                "completeness": r"completeness:?\s*(\d+)[/\s]*5",
                "testability": r"testability:?\s*(\d+)[/\s]*5",
                "feasibility": r"feasibility:?\s*(\d+)[/\s]*5",
                "consistency": r"consistency:?\s*(\d+)[/\s]*5"
            }
            
            for category, pattern in score_patterns.items():
                match = re.search(pattern, response, re.IGNORECASE)
                if match:
                    analysis["scores"][category] = int(match.group(1))
            
            # Extract suggestions
            suggestions_pattern = r"suggestions?:(.*?)(?:issues:|$)"
            suggestions_match = re.search(suggestions_pattern, response, re.IGNORECASE | re.DOTALL)
            if suggestions_match:
                # Split by bullet points and clean up
                suggestions_text = suggestions_match.group(1).strip()
                suggestions = re.findall(r"[-*]\s*(.*?)(?:\n|$)", suggestions_text)
                analysis["suggestions"] = [s.strip() for s in suggestions if s.strip()]
            
            # Extract issues
            issues_pattern = r"issues?:(.*?)(?:suggestions?:|$)"
            issues_match = re.search(issues_pattern, response, re.IGNORECASE | re.DOTALL)
            if issues_match:
                # Split by bullet points and clean up
                issues_text = issues_match.group(1).strip()
                issues = re.findall(r"[-*]\s*(.*?)(?:\n|$)", issues_text)
                analysis["issues"] = [i.strip() for i in issues if i.strip()]
            
            # Calculate overall score
            scores = analysis["scores"].values()
            analysis["overall_score"] = sum(scores) / len(scores) if scores else 0
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error parsing requirement analysis: {str(e)}")
            return {
                "scores": {},
                "suggestions": [],
                "issues": [],
                "parsing_error": str(e)
            }
    
    def _parse_refined_requirement(self, response: str, original_requirement: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse the LLM's response to extract refined requirement data.
        
        Args:
            response: The raw response from the LLM
            original_requirement: The original requirement dictionary
            
        Returns:
            Dictionary with refined requirement data
        """
        try:
            # Create a copy of the original requirement
            refined = original_requirement.copy()
            
            # Extract title
            import re
            title_match = re.search(r"title:?\s*(.+?)(?:\n|$)", response, re.IGNORECASE)
            if title_match:
                refined["title"] = title_match.group(1).strip()
            
            # Extract description
            description_pattern = r"description:?\s*(.*?)(?:type:|priority:|acceptance criteria:|$)"
            description_match = re.search(description_pattern, response, re.IGNORECASE | re.DOTALL)
            if description_match:
                refined["description"] = description_match.group(1).strip()
            
            # Extract type
            type_match = re.search(r"type:?\s*(.+?)(?:\n|$)", response, re.IGNORECASE)
            if type_match:
                refined["type"] = type_match.group(1).strip()
            
            # Extract priority
            priority_match = re.search(r"priority:?\s*(.+?)(?:\n|$)", response, re.IGNORECASE)
            if priority_match:
                refined["priority"] = priority_match.group(1).strip()
            
            # Extract acceptance criteria
            criteria_pattern = r"acceptance criteria:?(.*?)(?:$)"
            criteria_match = re.search(criteria_pattern, response, re.IGNORECASE | re.DOTALL)
            if criteria_match:
                criteria_text = criteria_match.group(1).strip()
                criteria = re.findall(r"[-*]\s*(.*?)(?:\n|$)", criteria_text)
                if criteria:
                    refined["acceptance_criteria"] = [c.strip() for c in criteria if c.strip()]
            
            return refined
            
        except Exception as e:
            logger.error(f"Error parsing refined requirement: {str(e)}")
            return original_requirement
    
    def _parse_validation_result(self, response: str, validation_criteria: List[str]) -> Dict[str, Any]:
        """
        Parse the LLM's response to extract validation results.
        
        Args:
            response: The raw response from the LLM
            validation_criteria: The original validation criteria
            
        Returns:
            Dictionary with validation results by criterion
        """
        results = {}
        try:
            # Simple parsing - look for each criterion and determine if it passed
            lines = response.split("\n")
            current_criterion = None
            current_result = {"pass": False, "explanation": "", "recommendations": []}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if this line starts a new criterion entry
                is_criterion_line = False
                for criterion in validation_criteria:
                    # Extract just the key part of the criterion (before the first colon or similar)
                    criterion_key = criterion.split(":")[0].strip() if ":" in criterion else criterion
                    if criterion_key and criterion_key.lower() in line.lower():
                        # If we have a previous criterion, save it
                        if current_criterion:
                            results[current_criterion] = current_result
                        
                        # Start a new criterion
                        current_criterion = criterion
                        current_result = {
                            "pass": "pass" in line.lower() and not "fail" in line.lower(),
                            "explanation": "",
                            "recommendations": []
                        }
                        is_criterion_line = True
                        break
                
                if not is_criterion_line and current_criterion:
                    # This is a continuation of the current criterion
                    if "recommend" in line.lower() or "suggest" in line.lower():
                        # This is likely a recommendation
                        recommendation = line.split(":", 1)[1].strip() if ":" in line else line
                        current_result["recommendations"].append(recommendation)
                    else:
                        # This is likely an explanation
                        if current_result["explanation"]:
                            current_result["explanation"] += " " + line
                        else:
                            current_result["explanation"] = line
            
            # Add the last criterion if exists
            if current_criterion:
                results[current_criterion] = current_result
            
            return results
            
        except Exception as e:
            logger.error(f"Error parsing validation result: {str(e)}")
            return {}
    
    def _get_fallback_response(self) -> str:
        """
        Provide a fallback response when the LLM service is unavailable.
        
        Returns:
            A helpful error message
        """
        return (
            "I apologize, but I'm currently unable to connect to the LLM service. "
            "This could be due to network issues or the service being offline. "
            "Please try again later or contact your administrator if the problem persists."
        )
    
    async def get_available_models(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Get the list of available models from the LLM adapter.
        
        Returns:
            Dictionary mapping providers to their available models
        """
        try:
            # Get LLM client
            client = await self._get_client()
            
            # Get providers information using enhanced client
            providers_info = await client.get_providers()
            
            # Convert to the expected format
            result = {}
            if hasattr(providers_info, 'providers'):
                for provider_id, provider_info in providers_info.providers.items():
                    models = []
                    for model_id, model_info in provider_info.get("models", {}).items():
                        models.append({
                            "id": model_id,
                            "name": model_info.get("name", model_id),
                            "context_length": model_info.get("context_length", 8192),
                            "capabilities": model_info.get("capabilities", [])
                        })
                    result[provider_id] = models
            else:
                # Handle alternative response format
                for provider in providers_info:
                    provider_id = provider.get("id")
                    if provider_id:
                        models = []
                        for model in provider.get("models", []):
                            models.append({
                                "id": model.get("id", ""),
                                "name": model.get("name", model.get("id", "")),
                                "context_length": model.get("context_length", 8192),
                                "capabilities": model.get("capabilities", [])
                            })
                        result[provider_id] = models
                
            return result
        except Exception as e:
            logger.error(f"Error getting models: {str(e)}")
            # Return fallback models
            return {
                "anthropic": [
                    {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku", "context_length": 200000},
                    {"id": "claude-3-sonnet-20240229", "name": "Claude 3 Sonnet", "context_length": 200000}
                ],
                "openai": [
                    {"id": "gpt-4", "name": "GPT-4", "context_length": 8192},
                    {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "context_length": 16384}
                ]
            }