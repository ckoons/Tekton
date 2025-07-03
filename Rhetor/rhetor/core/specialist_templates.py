"""
DEPRECATED: This module represents the old dynamic specialist system.
Use generic_specialist.py and COMPONENT_EXPERTISE instead.

This file is kept for reference but should not be used for new code.
The complex template-based personality system has been replaced with
a simpler approach using COMPONENT_EXPERTISE in generic_specialist.py.

Original description:
Specialist Templates for Dynamic AI Creation.

This module provides pre-defined templates for creating specialized AI agents
dynamically at runtime. Each template defines personality traits, capabilities,
and model preferences for different types of tasks.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class SpecialistTemplate:
    """Template for creating a specialized AI agent."""
    template_id: str
    name: str
    description: str
    base_type: str  # technical, analytical, creative, administrative, research
    model_preferences: List[str] = field(default_factory=list)
    personality_traits: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    system_prompt_template: str = ""
    focus_areas: List[str] = field(default_factory=list)
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    default_temperature: float = 0.7
    default_max_tokens: int = 2000
    
    def to_specialist_config(self, specialist_id: str, customization: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Convert template to a specialist configuration.
        
        Args:
            specialist_id: Unique ID for the new specialist
            customization: Optional customization overrides
            
        Returns:
            Complete specialist configuration
        """
        # Start with base configuration
        config = {
            "specialist_id": specialist_id,
            "specialist_type": f"dynamic-{self.base_type}",
            "component_id": "rhetor",  # Dynamic specialists belong to Rhetor
            "template_id": self.template_id,
            "created_from_template": True,
            "creation_time": datetime.now().isoformat(),
            "model_config": {
                "provider": "auto",  # Will be selected based on preferences
                "model": self.model_preferences[0] if self.model_preferences else "claude-3-haiku-20240307",
                "options": {
                    "temperature": self.default_temperature,
                    "max_tokens": self.default_max_tokens
                }
            },
            "personality": {
                "role": self.name,
                "traits": self.personality_traits.copy(),
                "system_prompt": self._generate_system_prompt(customization),
                "communication_style": self._determine_communication_style(),
                "focus_areas": self.focus_areas.copy()
            },
            "capabilities": self.capabilities.copy(),
            "resource_requirements": self.resource_requirements.copy()
        }
        
        # Apply customizations if provided
        if customization:
            config = self._apply_customization(config, customization)
            
        return config
    
    def _generate_system_prompt(self, customization: Optional[Dict[str, Any]] = None) -> str:
        """Generate system prompt from template."""
        prompt = self.system_prompt_template or f"You are {self.name}, a specialized AI assistant focused on {', '.join(self.focus_areas)}."
        
        if customization and "additional_context" in customization:
            prompt += f"\n\nAdditional context: {customization['additional_context']}"
            
        return prompt
    
    def _determine_communication_style(self) -> str:
        """Determine communication style based on traits."""
        style_parts = []
        
        trait_to_style = {
            "analytical": "precise",
            "creative": "imaginative",
            "technical": "detailed",
            "friendly": "approachable",
            "formal": "professional",
            "casual": "conversational"
        }
        
        for trait in self.personality_traits:
            if trait in trait_to_style:
                style_parts.append(trait_to_style[trait])
                
        return ", ".join(style_parts) if style_parts else "clear, helpful"
    
    def _apply_customization(self, config: Dict[str, Any], customization: Dict[str, Any]) -> Dict[str, Any]:
        """Apply customization overrides to configuration."""
        # Model customization
        if "model" in customization:
            config["model_config"]["model"] = customization["model"]
        
        if "temperature" in customization:
            config["model_config"]["options"]["temperature"] = customization["temperature"]
            
        if "max_tokens" in customization:
            config["model_config"]["options"]["max_tokens"] = customization["max_tokens"]
        
        # Personality customization
        if "additional_traits" in customization:
            config["personality"]["traits"].extend(customization["additional_traits"])
            
        if "additional_capabilities" in customization:
            config["capabilities"].extend(customization["additional_capabilities"])
            
        if "focus_override" in customization:
            config["personality"]["focus_areas"] = customization["focus_override"]
            
        return config


class SpecialistTemplateRegistry:
    """Registry for managing specialist templates."""
    
    def __init__(self):
        self.templates: Dict[str, SpecialistTemplate] = {}
        self._load_default_templates()
        
    def _load_default_templates(self):
        """Load default specialist templates."""
        default_templates = [
            SpecialistTemplate(
                template_id="code-reviewer",
                name="Code Review Specialist",
                description="Specialized in code review, best practices, and quality analysis",
                base_type="technical",
                model_preferences=["gpt-4", "claude-3-opus-20240229"],
                personality_traits=["analytical", "detail-oriented", "constructive", "technical"],
                capabilities=[
                    "code_review",
                    "best_practices_analysis", 
                    "security_assessment",
                    "performance_optimization",
                    "refactoring_suggestions"
                ],
                system_prompt_template="You are a senior code review specialist with expertise in multiple programming languages and frameworks. Your role is to provide constructive, detailed code reviews focusing on quality, security, and maintainability.",
                focus_areas=["code quality", "security", "performance", "maintainability"],
                resource_requirements={"priority": "high", "memory": "medium"},
                default_temperature=0.3
            ),
            
            SpecialistTemplate(
                template_id="data-analyst",
                name="Data Analysis Specialist",
                description="Expert in data analysis, visualization, and insights extraction",
                base_type="analytical",
                model_preferences=["claude-3-sonnet-20240229", "gpt-4"],
                personality_traits=["analytical", "quantitative", "precise", "insightful"],
                capabilities=[
                    "data_analysis",
                    "statistical_modeling",
                    "visualization_recommendations",
                    "trend_identification",
                    "insight_extraction"
                ],
                system_prompt_template="You are a data analysis specialist skilled in statistical analysis, data visualization, and extracting meaningful insights from complex datasets. Focus on clarity and actionable recommendations.",
                focus_areas=["data patterns", "statistical analysis", "visualization", "insights"],
                resource_requirements={"priority": "medium", "memory": "high"},
                default_temperature=0.5
            ),
            
            SpecialistTemplate(
                template_id="documentation-writer",
                name="Documentation Specialist", 
                description="Creates clear, comprehensive technical documentation",
                base_type="technical",
                model_preferences=["claude-3-sonnet-20240229", "gpt-3.5-turbo"],
                personality_traits=["clear", "organized", "thorough", "user-focused"],
                capabilities=[
                    "technical_writing",
                    "api_documentation",
                    "user_guides",
                    "code_commenting",
                    "readme_creation"
                ],
                system_prompt_template="You are a technical documentation specialist who creates clear, well-organized documentation. Focus on user needs, provide examples, and ensure completeness.",
                focus_areas=["clarity", "completeness", "user experience", "examples"],
                resource_requirements={"priority": "low", "memory": "low"},
                default_temperature=0.7
            ),
            
            SpecialistTemplate(
                template_id="bug-hunter",
                name="Bug Detection Specialist",
                description="Identifies and analyzes software bugs and edge cases",
                base_type="technical",
                model_preferences=["gpt-4", "claude-3-opus-20240229"],
                personality_traits=["meticulous", "systematic", "critical", "thorough"],
                capabilities=[
                    "bug_detection",
                    "edge_case_analysis",
                    "error_pattern_recognition",
                    "debugging_assistance",
                    "test_case_generation"
                ],
                system_prompt_template="You are a bug detection specialist focused on finding potential issues, edge cases, and error conditions in code. Think critically about failure modes and provide detailed analysis.",
                focus_areas=["bug detection", "edge cases", "error handling", "test coverage"],
                resource_requirements={"priority": "high", "memory": "medium"},
                default_temperature=0.4
            ),
            
            SpecialistTemplate(
                template_id="architecture-advisor",
                name="Architecture Design Specialist",
                description="Provides architectural guidance and system design expertise",
                base_type="technical",
                model_preferences=["claude-3-opus-20240229", "gpt-4"],
                personality_traits=["strategic", "systematic", "forward-thinking", "pragmatic"],
                capabilities=[
                    "system_design",
                    "architecture_review",
                    "scalability_planning",
                    "technology_selection",
                    "design_patterns"
                ],
                system_prompt_template="You are a senior architecture specialist with deep experience in system design, scalability, and architectural patterns. Provide strategic guidance balancing ideal solutions with practical constraints.",
                focus_areas=["system architecture", "scalability", "design patterns", "best practices"],
                resource_requirements={"priority": "high", "memory": "high"},
                default_temperature=0.6
            ),
            
            SpecialistTemplate(
                template_id="api-designer", 
                name="API Design Specialist",
                description="Designs RESTful and GraphQL APIs with best practices",
                base_type="technical",
                model_preferences=["claude-3-sonnet-20240229", "gpt-4"],
                personality_traits=["systematic", "user-centric", "consistent", "pragmatic"],
                capabilities=[
                    "api_design",
                    "endpoint_planning",
                    "schema_design", 
                    "versioning_strategy",
                    "documentation_structure"
                ],
                system_prompt_template="You are an API design specialist focused on creating intuitive, well-structured APIs. Emphasize consistency, usability, and following RESTful principles.",
                focus_areas=["API design", "REST principles", "usability", "consistency"],
                resource_requirements={"priority": "medium", "memory": "low"},
                default_temperature=0.5
            ),
            
            SpecialistTemplate(
                template_id="performance-optimizer",
                name="Performance Optimization Specialist",
                description="Optimizes code and systems for maximum performance",
                base_type="technical",
                model_preferences=["gpt-4", "claude-3-opus-20240229"],
                personality_traits=["analytical", "detail-oriented", "pragmatic", "results-focused"],
                capabilities=[
                    "performance_analysis",
                    "bottleneck_identification",
                    "optimization_strategies",
                    "caching_recommendations",
                    "algorithm_optimization"
                ],
                system_prompt_template="You are a performance optimization specialist skilled in identifying bottlenecks and implementing optimizations. Balance performance gains with code maintainability.",
                focus_areas=["performance", "optimization", "efficiency", "scalability"],
                resource_requirements={"priority": "high", "memory": "medium"},
                default_temperature=0.4
            ),
            
            SpecialistTemplate(
                template_id="security-auditor",
                name="Security Audit Specialist",
                description="Performs security analysis and vulnerability assessment",
                base_type="technical",
                model_preferences=["gpt-4", "claude-3-opus-20240229"],
                personality_traits=["vigilant", "thorough", "cautious", "knowledgeable"],
                capabilities=[
                    "security_analysis",
                    "vulnerability_detection",
                    "threat_modeling",
                    "security_best_practices",
                    "compliance_checking"
                ],
                system_prompt_template="You are a security audit specialist focused on identifying vulnerabilities and security risks. Provide actionable recommendations following security best practices.",
                focus_areas=["security", "vulnerabilities", "threat modeling", "compliance"],
                resource_requirements={"priority": "critical", "memory": "medium"},
                default_temperature=0.2
            )
        ]
        
        for template in default_templates:
            self.register_template(template)
            
    def register_template(self, template: SpecialistTemplate):
        """Register a new specialist template."""
        self.templates[template.template_id] = template
        logger.info(f"Registered specialist template: {template.template_id}")
        
    def get_template(self, template_id: str) -> Optional[SpecialistTemplate]:
        """Get a template by ID."""
        return self.templates.get(template_id)
        
    def list_templates(self) -> List[Dict[str, Any]]:
        """List all available templates."""
        return [
            {
                "template_id": template.template_id,
                "name": template.name,
                "description": template.description,
                "base_type": template.base_type,
                "capabilities": template.capabilities,
                "model_preferences": template.model_preferences
            }
            for template in self.templates.values()
        ]
    
    def create_specialist_from_template(
        self, 
        template_id: str, 
        specialist_id: str,
        customization: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a specialist configuration from a template.
        
        Args:
            template_id: ID of the template to use
            specialist_id: Unique ID for the new specialist
            customization: Optional customization parameters
            
        Returns:
            Specialist configuration or None if template not found
        """
        template = self.get_template(template_id)
        if not template:
            logger.error(f"Template not found: {template_id}")
            return None
            
        config = template.to_specialist_config(specialist_id, customization)
        logger.info(f"Created specialist config from template: {template_id} -> {specialist_id}")
        
        return config


# Global registry instance
specialist_template_registry = SpecialistTemplateRegistry()


# Convenience functions
def get_template(template_id: str) -> Optional[SpecialistTemplate]:
    """Get a specialist template by ID."""
    return specialist_template_registry.get_template(template_id)


def list_templates() -> List[Dict[str, Any]]:
    """List all available specialist templates."""
    return specialist_template_registry.list_templates()


def create_from_template(
    template_id: str,
    specialist_id: str, 
    customization: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """Create a specialist configuration from a template."""
    return specialist_template_registry.create_specialist_from_template(
        template_id, specialist_id, customization
    )