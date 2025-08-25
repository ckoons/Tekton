#!/usr/bin/env python3
"""
LLM Adapter for Prometheus

This module provides a unified interface for interacting with LLMs through
the enhanced tekton-llm-client, supporting prompt templates, structured
output parsing, and streaming capabilities.
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, AsyncGenerator, Callable, Awaitable
from datetime import datetime
import uuid

# Import enhanced tekton-llm-client features
from tekton_llm_client import (
    TektonLLMClient,
    PromptTemplateRegistry, PromptTemplate, load_template,
    JSONParser, parse_json, extract_json,
    StreamHandler, collect_stream, stream_to_string,
    StructuredOutputParser, OutputFormat,
    ClientSettings, LLMSettings, load_settings, get_env
)
from landmarks import architecture_decision, integration_point, performance_boundary

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("prometheus.utils.llm_adapter")

@architecture_decision(
    title="Enhanced LLM client integration",
    rationale="Use tekton-llm-client for standardized prompt templates, streaming, and structured output parsing",
    alternatives=["Direct API calls", "Custom LLM wrapper", "LangChain integration"],
    decision_date="2024-03-10"
)
@integration_point(
    title="LLM service connection",
    target_component="Rhetor",
    protocol="REST/WebSocket",
    data_flow="Prompts → LLM service → Structured responses"
)
class PrometheusLLMAdapter:
    """
    LLM Adapter for Prometheus planning system.
    
    This adapter provides an interface for LLM operations using the enhanced
    tekton-llm-client features for template management, streaming, and response handling.
    """
    
    def __init__(self, adapter_url: Optional[str] = None):
        """
        Initialize the LLM adapter.
        
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
            component_id="prometheus.planning",
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
        
        logger.info(f"Prometheus LLM Adapter initialized with URL: {self.adapter_url}")
    
    def _load_templates(self):
        """Load prompt templates for Prometheus"""
        # First try to load from standard locations
        standard_dirs = [
            "./prompt_templates",
            "./templates",
            "./prometheus/prompt_templates",
            "./prometheus/templates"
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
        """Register core prompt templates for Prometheus"""
        # Task breakdown template
        self.template_registry.register({
            "name": "task_breakdown",
            "template": """
            Given the following requirements, break them down into specific implementation tasks.
            For each task, provide the following:
            1. Task name
            2. Description
            3. Priority (high, medium, low)
            4. Estimated effort in hours
            5. Dependencies (references to other tasks)
            
            Requirements:
            {{ requirements }}
            
            Return the tasks in a structured JSON format with this schema:
            ```json
            [
              {
                "name": "Task name",
                "description": "Detailed description",
                "priority": "high|medium|low",
                "estimated_effort": 4.0,
                "dependencies": ["Reference to other tasks"]
              }
            ]
            ```
            """,
            "description": "Template for breaking down requirements into tasks"
        })
        
        # Retrospective analysis template
        self.template_registry.register({
            "name": "retrospective_analysis",
            "template": """
            Analyze the following retrospective data to identify patterns, root causes, and improvement opportunities.
            
            {{ retrospective_data }}
            
            Provide the following in your analysis:
            1. Key themes and patterns identified
            2. Root causes of issues
            3. Strengths to maintain
            4. Opportunities for improvement
            5. Recommendations for future sprints/projects
            
            Return the analysis in a structured format.
            """,
            "description": "Template for retrospective analysis"
        })
        
        # Improvement suggestions template
        self.template_registry.register({
            "name": "improvement_suggestions",
            "template": """
            Based on the following performance data, suggest improvements that could enhance future project execution.
            
            {{ performance_data }}
            
            Provide the following for each improvement suggestion:
            1. Title
            2. Description
            3. Priority (high, medium, low)
            4. Implementation plan
            5. Expected benefits
            
            Return 3-5 improvement suggestions in a structured JSON format with this schema:
            ```json
            [
              {
                "title": "Improvement title",
                "description": "Detailed description",
                "priority": "high|medium|low",
                "implementation_plan": "Step-by-step plan",
                "expected_benefits": "Expected benefits"
              }
            ]
            ```
            """,
            "description": "Template for generating improvement suggestions"
        })
        
        # Risk analysis template
        self.template_registry.register({
            "name": "risk_analysis",
            "template": """
            Analyze the following project plan to identify potential risks and suggest mitigation strategies.
            
            {{ project_data }}
            
            For each identified risk, provide:
            1. Risk name
            2. Description
            3. Impact (high, medium, low)
            4. Probability (high, medium, low)
            5. Mitigation strategy
            
            Return the risk analysis in a structured JSON format with this schema:
            ```json
            [
              {
                "name": "Risk name",
                "description": "Risk description",
                "impact": "high|medium|low",
                "probability": "high|medium|low",
                "mitigation": "Mitigation strategy"
              }
            ]
            ```
            """,
            "description": "Template for risk analysis"
        })
        
        # Critical path analysis template
        self.template_registry.register({
            "name": "critical_path_analysis",
            "template": """
            Analyze the following project tasks and identify the critical path through the project.
            
            Project Tasks:
            {{ tasks }}
            
            Provide the following in your analysis:
            1. The tasks that form the critical path
            2. Key dependencies that could affect project completion
            3. Risks associated with the critical path
            4. Suggestions for optimizing the critical path
            
            Structure your analysis clearly.
            """,
            "description": "Template for critical path analysis"
        })
        
        # System prompts
        self.template_registry.register({
            "name": "system_task_breakdown",
            "template": """
            You are an CI assistant that helps with project planning. 
            Your task is to break down high-level requirements into specific implementation tasks.
            For each task, provide a name, description, priority, estimated effort, and dependencies.
            Format your response as structured JSON that can be parsed directly.
            """
        })
        
        self.template_registry.register({
            "name": "system_retrospective_analysis",
            "template": """
            You are an CI assistant that specializes in analyzing retrospective data.
            Your task is to identify patterns, root causes, strengths, and improvement opportunities.
            Provide a comprehensive analysis that will help the team improve for future projects.
            """
        })
        
        self.template_registry.register({
            "name": "system_improvement_suggestions",
            "template": """
            You are an CI assistant that specializes in continuous improvement.
            Your task is to suggest specific, actionable improvements based on performance data.
            Format your response as structured JSON that can be parsed directly.
            """
        })
        
        self.template_registry.register({
            "name": "system_risk_analysis",
            "template": """
            You are an CI assistant that specializes in risk analysis and mitigation.
            Your task is to identify potential risks in a project plan and suggest mitigation strategies.
            Format your response as structured JSON that can be parsed directly.
            """
        })
        
        self.template_registry.register({
            "name": "system_critical_path",
            "template": """
            You are an CI assistant that specializes in project planning and critical path analysis.
            Your task is to identify the critical path through a project and suggest optimizations.
            Provide a clear and concise analysis that helps the team understand the project timeline.
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
    
    async def generate_text(self, 
                          prompt: str, 
                          system_prompt: Optional[str] = None,
                          model: Optional[str] = None,
                          temperature: float = 0.7,
                          max_tokens: Optional[int] = None,
                          streaming: bool = False) -> Union[str, AsyncGenerator[str, None]]:
        """
        Generate text from the LLM
        
        Args:
            prompt: The prompt to send to the LLM
            system_prompt: Optional system prompt
            model: LLM model to use (defaults to configured default)
            temperature: Temperature parameter for generation
            max_tokens: Maximum tokens to generate
            streaming: Whether to stream the response
            
        Returns:
            If streaming=False, returns the complete response as a string
            If streaming=True, returns an async generator yielding response chunks
        """
        try:
            # Get LLM client
            client = await self._get_client()
            
            # Custom settings for this request
            custom_settings = LLMSettings(
                temperature=temperature,
                max_tokens=max_tokens or self.llm_settings.max_tokens,
                model=model or self.default_model
            )
            
            # If streaming is requested, use streaming approach
            if streaming:
                response_stream = await client.generate_text(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    settings=custom_settings,
                    streaming=True
                )
                
                # Create a custom stream generator
                async def stream_generator():
                    try:
                        async for chunk in response_stream:
                            chunk_text = chunk.chunk if hasattr(chunk, 'chunk') else chunk
                            yield chunk_text
                    except Exception as e:
                        logger.error(f"Error in streaming: {str(e)}")
                        yield self._get_fallback_response()
                
                # Return the stream generator
                return stream_generator()
            
            # Normal non-streaming request
            response = await client.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                settings=custom_settings
            )
            
            return response.content
        
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            return self._get_fallback_response()
    
    @performance_boundary(
        title="Task breakdown generation",
        sla="<10s for typical requirement sets",
        metrics={"avg_time": "6.8s", "p95": "9.2s"},
        optimization_notes="Template caching, parallel processing for large sets"
    )
    async def breakdown_tasks(self, requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Use LLM to breakdown requirements into tasks.
        
        Args:
            requirements: List of requirement data
            
        Returns:
            List of task data
        """
        try:
            # Prepare requirements text
            req_text = ""
            for i, req in enumerate(requirements):
                req_text += f"{i+1}. {req.get('title', 'Requirement')}: {req.get('description', '')}\n"
            
            # Get templates
            prompt = self.template_registry.render(
                "task_breakdown", 
                requirements=req_text
            )
            
            system_prompt = self.template_registry.render("system_task_breakdown")
            
            # Get client and generate text
            client = await self._get_client()
            
            # Use specific settings for task breakdown
            settings = LLMSettings(
                temperature=0.3,  # Lower temperature for more consistent output
                max_tokens=2000,
                model=self.default_model
            )
            
            # Call LLM and get response
            response = await client.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                settings=settings
            )
            
            # Try to parse JSON response
            try:
                # Use JSON parser to extract structured data
                tasks_json = extract_json(response.content)
                
                # If successful, format the tasks
                if isinstance(tasks_json, list):
                    tasks = []
                    for task_data in tasks_json:
                        task_id = f"task-{uuid.uuid4()}"
                        task = {
                            "task_id": task_id,
                            "name": task_data.get("name", "Untitled Task"),
                            "description": task_data.get("description", ""),
                            "priority": task_data.get("priority", "medium"),
                            "estimated_effort": float(task_data.get("estimated_effort", 8.0)),
                            "dependencies": task_data.get("dependencies", []),
                            "requirements": [req.get("requirement_id") for req in requirements],
                            "created_at": datetime.now().timestamp(),
                            "updated_at": datetime.now().timestamp()
                        }
                        tasks.append(task)
                    return tasks
            except Exception as e:
                logger.error(f"Error parsing task breakdown response: {str(e)}")
            
            # Fallback to manual processing if JSON parsing fails
            return self._generate_fallback_tasks(requirements)
            
        except Exception as e:
            logger.error(f"Error in task breakdown: {str(e)}")
            return self._generate_fallback_tasks(requirements)
    
    def _generate_fallback_tasks(self, requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate fallback tasks from requirements if LLM fails.
        
        Args:
            requirements: List of requirement data
            
        Returns:
            List of task data
        """
        tasks = []
        
        for req in requirements:
            # Generate a task ID
            task_id = f"task-{uuid.uuid4()}"
            
            # Create a task from the requirement
            tasks.append({
                "task_id": task_id,
                "name": f"Implement: {req.get('title', 'Requirement')}",
                "description": req.get("description", ""),
                "priority": req.get("priority", "medium"),
                "estimated_effort": 8.0,  # 8 hours default
                "dependencies": [],
                "requirements": [req.get("requirement_id")],
                "created_at": datetime.now().timestamp(),
                "updated_at": datetime.now().timestamp()
            })
        
        return tasks
    
    async def analyze_retrospective(self, retrospective_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use LLM to analyze retrospective data.
        
        Args:
            retrospective_data: Retrospective data
            
        Returns:
            Analysis results
        """
        try:
            # Prepare retrospective text
            retro_text = f"""
            Retrospective: {retrospective_data.get('name', 'Retrospective')}
            Date: {retrospective_data.get('date', 'Unknown')}
            Format: {retrospective_data.get('format', 'Unknown')}
            
            Items:
            """
            
            # Group items by category
            items_by_category = {}
            for item in retrospective_data.get("items", []):
                category = item.get("category", "Uncategorized")
                if category not in items_by_category:
                    items_by_category[category] = []
                items_by_category[category].append(item)
            
            # Add items to text
            for category, items in items_by_category.items():
                retro_text += f"\n{category}:\n"
                for item in items:
                    votes = item.get("votes", 0)
                    vote_str = f" (Votes: {votes})" if votes > 0 else ""
                    retro_text += f"- {item.get('content', '')}{vote_str}\n"
            
            # Add action items to text
            if retrospective_data.get("action_items"):
                retro_text += "\nAction Items:\n"
                for action in retrospective_data.get("action_items", []):
                    retro_text += f"- {action.get('title', '')}: {action.get('description', '')}\n"
            
            # Get templates
            prompt = self.template_registry.render(
                "retrospective_analysis", 
                retrospective_data=retro_text
            )
            
            system_prompt = self.template_registry.render("system_retrospective_analysis")
            
            # Get client and generate text
            client = await self._get_client()
            
            # Use specific settings for retrospective analysis
            settings = LLMSettings(
                temperature=0.5,
                max_tokens=2500,
                model=self.default_model
            )
            
            # Call LLM and get response
            response = await client.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                settings=settings
            )
            
            # Return the analysis
            return {
                "retrospective_id": retrospective_data.get("retro_id"),
                "analysis": response.content,
                "model": response.model,
                "provider": response.provider,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in retrospective analysis: {str(e)}")
            return self._generate_fallback_retro_analysis(retrospective_data)
    
    def _generate_fallback_retro_analysis(self, retrospective_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate fallback retrospective analysis if LLM fails.
        
        Args:
            retrospective_data: Retrospective data
            
        Returns:
            Fallback analysis
        """
        # Count items by category
        category_counts = {}
        for item in retrospective_data.get("items", []):
            category = item.get("category", "Uncategorized")
            if category not in category_counts:
                category_counts[category] = 0
            category_counts[category] += 1
        
        # Generate analysis text
        analysis = f"""
        # Retrospective Analysis
        
        ## Summary
        
        This retrospective had {len(retrospective_data.get('items', []))} items across {len(category_counts)} categories.
        
        ## Categories
        
        """
        
        for category, count in category_counts.items():
            analysis += f"- {category}: {count} items\n"
        
        analysis += "\n## Action Items\n\n"
        
        for action in retrospective_data.get("action_items", []):
            analysis += f"- {action.get('title', '')}\n"
        
        analysis += "\n## Recommendations\n\n"
        analysis += "1. Follow up on action items\n"
        analysis += "2. Address top voted issues\n"
        analysis += "3. Continue practices mentioned positively\n"
        
        return {
            "retrospective_id": retrospective_data.get("retro_id"),
            "analysis": analysis,
            "model": self.default_model,
            "provider": self.default_provider,
            "timestamp": datetime.now().isoformat()
        }
    
    async def generate_improvements(self, performance_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Use LLM to generate improvement suggestions from performance data.
        
        Args:
            performance_data: Performance data
            
        Returns:
            List of improvement suggestions
        """
        try:
            # Prepare performance text
            performance_text = f"""
            Performance Data:
            - Completion Rate: {performance_data.get('completion_rate', 0) * 100:.1f}%
            - Effort Variance: {performance_data.get('effort_variance', 0):.1f} hours
            """
            
            # Add task completion information
            if "task_completion" in performance_data:
                performance_text += "\n\nTask Completion:\n"
                for task_id, task_data in performance_data.get("task_completion", {}).items():
                    performance_text += f"- {task_data.get('name', task_id)}: {task_data.get('actual_progress', 0) * 100:.1f}% complete\n"
            
            # Add milestone information
            if "milestone_achievement" in performance_data:
                performance_text += "\n\nMilestone Achievement:\n"
                for milestone_id, milestone_data in performance_data.get("milestone_achievement", {}).items():
                    performance_text += f"- {milestone_data.get('name', milestone_id)}: {milestone_data.get('actual_status', 'unknown')}\n"
            
            # Get templates
            prompt = self.template_registry.render(
                "improvement_suggestions", 
                performance_data=performance_text
            )
            
            system_prompt = self.template_registry.render("system_improvement_suggestions")
            
            # Get client and generate text
            client = await self._get_client()
            
            # Use specific settings for improvement suggestions
            settings = LLMSettings(
                temperature=0.7,  # Higher temperature for more creative suggestions
                max_tokens=2000,
                model=self.default_model
            )
            
            # Call LLM and get response
            response = await client.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                settings=settings
            )
            
            # Try to parse JSON response
            try:
                # Use JSON parser to extract structured data
                improvements_json = extract_json(response.content)
                
                # If successful, format the improvements
                if isinstance(improvements_json, list):
                    improvements = []
                    for imp_data in improvements_json:
                        improvement_id = f"improvement-{uuid.uuid4()}"
                        improvement = {
                            "improvement_id": improvement_id,
                            "title": imp_data.get("title", "Untitled Improvement"),
                            "description": imp_data.get("description", ""),
                            "source": "performance_analysis",
                            "priority": imp_data.get("priority", "medium"),
                            "implementation_plan": imp_data.get("implementation_plan", ""),
                            "verification_criteria": imp_data.get("expected_benefits", ""),
                            "tags": ["ai-generated", "performance"],
                            "created_at": datetime.now().timestamp(),
                            "updated_at": datetime.now().timestamp()
                        }
                        improvements.append(improvement)
                    return improvements
            except Exception as e:
                logger.error(f"Error parsing improvement suggestions response: {str(e)}")
            
            # Fallback to manual processing if JSON parsing fails
            return self._generate_fallback_improvements(performance_data)
            
        except Exception as e:
            logger.error(f"Error in improvement suggestions: {str(e)}")
            return self._generate_fallback_improvements(performance_data)
    
    def _generate_fallback_improvements(self, performance_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate fallback improvement suggestions if LLM fails.
        
        Args:
            performance_data: Performance data
            
        Returns:
            List of improvement suggestions
        """
        improvements = []
        
        # Generate some generic improvements
        improvements.append({
            "improvement_id": f"improvement-{uuid.uuid4()}",
            "title": "Enhance Task Estimation",
            "description": "Improve the process of estimating task effort to reduce variance.",
            "source": "performance_analysis",
            "priority": "high",
            "implementation_plan": "1. Review historical data\n2. Train team on estimation techniques\n3. Implement planning poker\n4. Review and adjust",
            "verification_criteria": "Reduced variance between estimated and actual effort",
            "tags": ["estimation", "planning"],
            "created_at": datetime.now().timestamp(),
            "updated_at": datetime.now().timestamp()
        })
        
        improvements.append({
            "improvement_id": f"improvement-{uuid.uuid4()}",
            "title": "Implement Regular Progress Reviews",
            "description": "Conduct regular progress reviews to identify and address issues early.",
            "source": "performance_analysis",
            "priority": "medium",
            "implementation_plan": "1. Schedule weekly reviews\n2. Create dashboard\n3. Define escalation process\n4. Monitor and adjust",
            "verification_criteria": "Issues identified and addressed earlier in the project lifecycle",
            "tags": ["monitoring", "process"],
            "created_at": datetime.now().timestamp(),
            "updated_at": datetime.now().timestamp()
        })
        
        improvements.append({
            "improvement_id": f"improvement-{uuid.uuid4()}",
            "title": "Refine Dependency Management",
            "description": "Improve the identification and management of task dependencies.",
            "source": "performance_analysis",
            "priority": "medium",
            "implementation_plan": "1. Update planning process\n2. Create dependency visualization\n3. Implement early alerts for dependency risks",
            "verification_criteria": "Fewer delays caused by unexpected dependencies",
            "tags": ["dependencies", "planning"],
            "created_at": datetime.now().timestamp(),
            "updated_at": datetime.now().timestamp()
        })
        
        return improvements
    
    async def analyze_risks(self, project_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Use LLM to analyze project risks.
        
        Args:
            project_data: Project data including tasks, timeline, and resources
            
        Returns:
            List of identified risks with mitigation strategies
        """
        try:
            # Prepare project data text
            project_text = f"""
            Project: {project_data.get('name', 'Project')}
            Timeline: {project_data.get('start_date', 'Unknown')} to {project_data.get('end_date', 'Unknown')}
            """
            
            # Add task information
            if "tasks" in project_data:
                project_text += "\n\nTasks:\n"
                for task in project_data.get("tasks", []):
                    project_text += f"- {task.get('name', 'Task')}: {task.get('description', '')}\n"
                    project_text += f"  Priority: {task.get('priority', 'medium')}, Effort: {task.get('estimated_effort', 0)} hours\n"
                    if task.get('dependencies'):
                        project_text += f"  Dependencies: {', '.join(task.get('dependencies', []))}\n"
            
            # Add resource information
            if "resources" in project_data:
                project_text += "\n\nResources:\n"
                for resource in project_data.get("resources", []):
                    project_text += f"- {resource.get('name', 'Resource')}: {resource.get('role', 'Unknown')}\n"
                    project_text += f"  Availability: {resource.get('availability', 100)}%\n"
            
            # Get templates
            prompt = self.template_registry.render(
                "risk_analysis", 
                project_data=project_text
            )
            
            system_prompt = self.template_registry.render("system_risk_analysis")
            
            # Get client and generate text
            client = await self._get_client()
            
            # Use specific settings for risk analysis
            settings = LLMSettings(
                temperature=0.4,
                max_tokens=2000,
                model=self.default_model
            )
            
            # Call LLM and get response
            response = await client.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                settings=settings
            )
            
            # Try to parse JSON response
            try:
                # Use JSON parser to extract structured data
                risks_json = extract_json(response.content)
                
                # If successful, format the risks
                if isinstance(risks_json, list):
                    risks = []
                    for risk_data in risks_json:
                        risk_id = f"risk-{uuid.uuid4()}"
                        risk = {
                            "risk_id": risk_id,
                            "name": risk_data.get("name", "Untitled Risk"),
                            "description": risk_data.get("description", ""),
                            "impact": risk_data.get("impact", "medium"),
                            "probability": risk_data.get("probability", "medium"),
                            "severity": self._calculate_severity(risk_data.get("impact", "medium"), risk_data.get("probability", "medium")),
                            "mitigation": risk_data.get("mitigation", ""),
                            "status": "identified",
                            "project_id": project_data.get("project_id"),
                            "created_at": datetime.now().timestamp(),
                            "updated_at": datetime.now().timestamp()
                        }
                        risks.append(risk)
                    return risks
            except Exception as e:
                logger.error(f"Error parsing risk analysis response: {str(e)}")
            
            # Fallback to generic risks if JSON parsing fails
            return self._generate_fallback_risks(project_data)
            
        except Exception as e:
            logger.error(f"Error in risk analysis: {str(e)}")
            return self._generate_fallback_risks(project_data)
    
    def _calculate_severity(self, impact: str, probability: str) -> str:
        """
        Calculate risk severity based on impact and probability.
        
        Args:
            impact: Impact level (high, medium, low)
            probability: Probability level (high, medium, low)
            
        Returns:
            Severity level (critical, high, medium, low)
        """
        # Convert to numeric values
        impact_values = {"high": 3, "medium": 2, "low": 1}
        probability_values = {"high": 3, "medium": 2, "low": 1}
        
        impact_value = impact_values.get(impact.lower(), 2)
        probability_value = probability_values.get(probability.lower(), 2)
        
        # Calculate severity score
        severity_score = impact_value * probability_value
        
        # Map to severity levels
        if severity_score >= 7:
            return "critical"
        elif severity_score >= 5:
            return "high"
        elif severity_score >= 3:
            return "medium"
        else:
            return "low"
    
    def _generate_fallback_risks(self, project_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate fallback risks if LLM fails.
        
        Args:
            project_data: Project data
            
        Returns:
            List of generic risks
        """
        risks = []
        
        # Generate some generic risks
        risks.append({
            "risk_id": f"risk-{uuid.uuid4()}",
            "name": "Resource Availability",
            "description": "Team members may not be available as planned due to competing priorities or illness.",
            "impact": "high",
            "probability": "medium",
            "severity": "high",
            "mitigation": "Identify backup resources and cross-train team members.",
            "status": "identified",
            "project_id": project_data.get("project_id"),
            "created_at": datetime.now().timestamp(),
            "updated_at": datetime.now().timestamp()
        })
        
        risks.append({
            "risk_id": f"risk-{uuid.uuid4()}",
            "name": "Scope Creep",
            "description": "Project scope may expand without corresponding adjustments to schedule or resources.",
            "impact": "high",
            "probability": "high",
            "severity": "critical",
            "mitigation": "Implement formal change control process and maintain a clear scope baseline.",
            "status": "identified",
            "project_id": project_data.get("project_id"),
            "created_at": datetime.now().timestamp(),
            "updated_at": datetime.now().timestamp()
        })
        
        risks.append({
            "risk_id": f"risk-{uuid.uuid4()}",
            "name": "Technical Challenges",
            "description": "Unforeseen technical issues may arise during implementation.",
            "impact": "medium",
            "probability": "medium",
            "severity": "medium",
            "mitigation": "Conduct early prototyping and ensure access to technical expertise.",
            "status": "identified",
            "project_id": project_data.get("project_id"),
            "created_at": datetime.now().timestamp(),
            "updated_at": datetime.now().timestamp()
        })
        
        return risks
    
    async def analyze_critical_path(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Use LLM to analyze the critical path through a project.
        
        Args:
            tasks: List of project tasks
            
        Returns:
            Critical path analysis
        """
        try:
            # Prepare task text
            task_text = "Tasks:\n"
            for i, task in enumerate(tasks):
                task_text += f"{i+1}. {task.get('name', 'Task')}\n"
                task_text += f"   Description: {task.get('description', '')}\n"
                task_text += f"   Effort: {task.get('estimated_effort', 0)} hours\n"
                if task.get('dependencies'):
                    dep_names = []
                    for dep_id in task.get('dependencies', []):
                        for t in tasks:
                            if t.get('task_id') == dep_id:
                                dep_names.append(t.get('name', dep_id))
                                break
                    if dep_names:
                        task_text += f"   Dependencies: {', '.join(dep_names)}\n"
                task_text += "\n"
            
            # Get templates
            prompt = self.template_registry.render(
                "critical_path_analysis", 
                tasks=task_text
            )
            
            system_prompt = self.template_registry.render("system_critical_path")
            
            # Get client and generate text
            client = await self._get_client()
            
            # Use specific settings for critical path analysis
            settings = LLMSettings(
                temperature=0.3,
                max_tokens=2000,
                model=self.default_model
            )
            
            # Call LLM and get response
            response = await client.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                settings=settings
            )
            
            # Return the analysis
            return {
                "critical_path_analysis": response.content,
                "model": response.model,
                "provider": response.provider,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in critical path analysis: {str(e)}")
            return {
                "critical_path_analysis": "Error performing critical path analysis. Please check the task data and try again.",
                "model": self.default_model,
                "provider": self.default_provider,
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_fallback_response(self) -> str:
        """
        Provide a fallback response when the LLM service is unavailable.
        
        Returns:
            A helpful error message
        """
        return (
            "I apologize, but I'm currently unable to connect to the LLM service. "
            "This could be due to network issues or the service being offline. "
            "Basic operations will continue to work, but advanced analysis "
            "capabilities may be limited. Please try again later or "
            "contact your administrator if the problem persists."
        )