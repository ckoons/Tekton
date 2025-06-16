"""
Requirement analysis module.

This module provides utilities for analyzing requirements and generating
quality metrics and improvement suggestions, with optional LLM-powered analysis
through the Rhetor component.
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union

from telos.core.requirement import Requirement

logger = logging.getLogger(__name__)


class RequirementAnalyzer:
    """Analyzes requirements and provides improvement suggestions."""
    
    def __init__(self, use_llm=True):
        """
        Initialize the requirement analyzer.
        
        Args:
            use_llm: Whether to use LLM-powered analysis through Rhetor (if available)
        """
        # Load requirement quality criteria
        self.quality_criteria = {
            "clarity": {
                "weight": 0.25,
                "description": "How clear and unambiguous the requirement is"
            },
            "completeness": {
                "weight": 0.25,
                "description": "Whether the requirement contains all necessary information"
            },
            "testability": {
                "weight": 0.20,
                "description": "Whether the requirement can be verified and tested"
            },
            "feasibility": {
                "weight": 0.15,
                "description": "Whether the requirement is technically feasible"
            },
            "consistency": {
                "weight": 0.15,
                "description": "Whether the requirement conflicts with others"
            }
        }
        
        # Quality indicator terms for each criterion
        self.quality_indicators = {
            "clarity": {
                "positive": ["specific", "clear", "precise", "defined", "exact", "explicit"],
                "negative": ["vague", "unclear", "ambiguous", "general", "subjective"]
            },
            "completeness": {
                "positive": ["complete", "comprehensive", "detailed", "thorough", "full"],
                "negative": ["missing", "incomplete", "partial", "lacks", "insufficient"]
            },
            "testability": {
                "positive": ["measurable", "verifiable", "testable", "quantifiable", "observable"],
                "negative": ["unmeasurable", "unverifiable", "subjective", "abstract"]
            },
            "feasibility": {
                "positive": ["achievable", "feasible", "practical", "realistic", "implementable"],
                "negative": ["impossible", "unrealistic", "impractical", "excessive"]
            }
        }
        
        # LLM configuration
        self.use_llm = use_llm
        self.rhetor_client = None
        self.llm_client = None
    
    async def analyze_requirement(self, requirement: Requirement) -> Dict[str, Any]:
        """
        Analyze a requirement's quality and provide improvement suggestions.
        Uses Rhetor LLM capabilities when available, falling back to rule-based analysis.
        
        Args:
            requirement: The requirement to analyze
            
        Returns:
            Analysis results including quality score and suggestions
        """
        # Try LLM-powered analysis if enabled
        if self.use_llm:
            try:
                llm_analysis = await self._analyze_with_llm(requirement)
                if llm_analysis:
                    # Format detailed feedback
                    from .formatters import format_detailed_feedback
                    detailed_feedback = format_detailed_feedback(
                        requirement, 
                        llm_analysis["metrics"], 
                        llm_analysis["score"], 
                        llm_analysis["suggestions"]
                    )
                    llm_analysis["detailed_feedback"] = detailed_feedback
                    return llm_analysis
            except Exception as e:
                logger.warning(f"LLM-powered analysis failed, falling back to rules: {e}")
        
        # Fall back to rule-based analysis
        return await self._analyze_with_rules(requirement)
    
    async def _analyze_with_llm(self, requirement: Requirement) -> Optional[Dict[str, Any]]:
        """
        Analyze a requirement using LLM capabilities through Rhetor.
        
        Args:
            requirement: The requirement to analyze
            
        Returns:
            Analysis results or None if analysis failed
        """
        # Try to import Rhetor
        try:
            # First try the LLM adapter integration
            try:
                from rhetor.core.llm_client import LLMClient
                if not self.llm_client:
                    self.llm_client = LLMClient()
                    await self.llm_client.initialize()
                
                # Use direct LLM client
                return await self._analyze_with_direct_llm(requirement)
            except ImportError:
                logger.debug("Direct LLM client not available, trying Rhetor client")
                
                # Try Rhetor client as fallback
                from rhetor.client import get_rhetor_prompt_client
                if not self.rhetor_client:
                    self.rhetor_client = await get_rhetor_prompt_client()
                
                # Use Rhetor prompt client
                return await self._analyze_with_rhetor(requirement)
        
        except Exception as e:
            logger.warning(f"Failed to initialize LLM analysis: {e}")
            return None
    
    async def _analyze_with_direct_llm(self, requirement: Requirement) -> Dict[str, Any]:
        """
        Analyze a requirement using the direct LLM client.
        
        Args:
            requirement: The requirement to analyze
            
        Returns:
            Analysis results
        """
        # Check if LLM client is available
        if not self.llm_client or not self.llm_client.providers:
            raise RuntimeError("LLM client not initialized")
        
        # Create prompt for analysis
        system_prompt = """You are an expert requirements analyzer with deep experience in requirements engineering. 
Your task is to analyze a software requirement and provide feedback on its quality.
Focus on clarity, completeness, testability, feasibility, and consistency.
Provide a quantitative assessment (0.0-1.0) for each criterion.
Be specific and actionable in your feedback."""

        prompt = f"""Please analyze the following requirement:

Title: {requirement.title}
Type: {requirement.requirement_type}
Priority: {requirement.priority or 'Not specified'}
Description: {requirement.description}

Analyze this requirement for:
1. Clarity (0.0-1.0): Is it clear and unambiguous?
2. Completeness (0.0-1.0): Does it contain all necessary information?
3. Testability (0.0-1.0): Can it be verified and tested?
4. Feasibility (0.0-1.0): Is it technically feasible?
5. Consistency (0.0-1.0): Does it likely conflict with other requirements?

Provide specific suggestions for improvement.
Return your analysis in JSON format with the following structure:
{{
  "score": [overall_score],
  "metrics": {{
    "clarity": {{ "score": [score], "feedback": [list_of_feedback] }},
    "completeness": {{ "score": [score], "feedback": [list_of_feedback] }},
    "testability": {{ "score": [score], "feedback": [list_of_feedback] }},
    "feasibility": {{ "score": [score], "feedback": [list_of_feedback] }},
    "consistency": {{ "score": [score], "feedback": [list_of_feedback] }}
  }},
  "suggestions": [list_of_all_suggestions],
  "improvement_areas": [list_of_areas_needing_improvement]
}}"""

        # Get response from LLM
        context_id = f"req_analysis_{requirement.requirement_id}"
        response = await self.llm_client.complete(
            message=prompt,
            context_id=context_id,
            system_prompt=system_prompt,
            options={"fallback_provider": "simulated"}
        )
        
        # Parse the response
        if "error" in response:
            raise RuntimeError(f"LLM error: {response['error']}")
        
        try:
            # Extract JSON from the response
            text = response.get("content", "")
            # Find JSON part using markers
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_part = text[json_start:json_end]
                analysis = json.loads(json_part)
                
                # Add requirement ID
                analysis["requirement_id"] = requirement.requirement_id
                
                return analysis
            else:
                raise ValueError("No JSON found in the response")
        
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            logger.debug(f"Raw response: {response}")
            raise RuntimeError("Failed to parse LLM analysis")
    
    async def _analyze_with_rhetor(self, requirement: Requirement) -> Dict[str, Any]:
        """
        Analyze a requirement using the Rhetor prompt client.
        
        Args:
            requirement: The requirement to analyze
            
        Returns:
            Analysis results
        """
        # Check if Rhetor client is available
        if not self.rhetor_client:
            raise RuntimeError("Rhetor client not initialized")
        
        # Generate a prompt for analysis
        analysis_prompt = await self.rhetor_client.generate_prompt(
            task="analyze requirement quality",
            context={
                "requirement": {
                    "title": requirement.title,
                    "type": requirement.requirement_type,
                    "priority": requirement.priority or "Not specified",
                    "description": requirement.description
                },
                "criteria": list(self.quality_criteria.keys()),
                "format": "json"
            }
        )
        
        # Get results from Rhetor
        result = await self.rhetor_client.invoke_capability(
            "analyze_text",
            {
                "text": f"Title: {requirement.title}\nDescription: {requirement.description}",
                "analysis_type": "requirement_quality",
                "format": "json"
            }
        )
        
        # Parse the response
        if isinstance(result, dict) and "analysis" in result:
            analysis = result["analysis"]
            
            # Add requirement ID
            analysis["requirement_id"] = requirement.requirement_id
            
            return analysis
        else:
            raise RuntimeError("Unexpected response format from Rhetor")
    
    async def _analyze_with_rules(self, requirement: Requirement) -> Dict[str, Any]:
        """
        Analyze a requirement's quality using rule-based analysis.
        
        Args:
            requirement: The requirement to analyze
            
        Returns:
            Analysis results
        """
        # Initialize quality metrics
        quality_metrics = await self._initialize_metrics()
        
        # Analyze title
        quality_metrics = await self._analyze_title(requirement, quality_metrics)
        
        # Analyze description
        quality_metrics = await self._analyze_description(requirement, quality_metrics)
        
        # Analyze testability
        quality_metrics = await self._analyze_testability(requirement, quality_metrics)
        
        # Analyze feasibility
        quality_metrics = await self._analyze_feasibility(requirement, quality_metrics)
        
        # Analyze metadata
        quality_metrics = await self._analyze_metadata(requirement, quality_metrics)
        
        # Calculate overall score
        overall_score = await self._calculate_overall_score(quality_metrics)
        
        # Compile suggestions and improvement areas
        suggestions, improvement_areas = await self._compile_suggestions(requirement, quality_metrics)
        
        # Format detailed feedback
        from .formatters import format_detailed_feedback
        detailed_feedback = format_detailed_feedback(requirement, quality_metrics, overall_score, suggestions)
        
        return {
            "score": overall_score,
            "metrics": quality_metrics,
            "suggestions": suggestions,
            "improvement_areas": improvement_areas,
            "detailed_feedback": detailed_feedback,
            "requirement_id": requirement.requirement_id
        }
    
    async def _initialize_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Initialize quality metrics for each criterion."""
        quality_metrics = {}
        for criterion, info in self.quality_criteria.items():
            quality_metrics[criterion] = {
                "score": 0.0,
                "description": info["description"],
                "feedback": []
            }
        return quality_metrics
    
    async def _analyze_title(self, requirement: Requirement, metrics: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Analyze the requirement title."""
        if len(requirement.title) < 10:
            metrics["clarity"]["feedback"].append(
                "Title is too short. A good title should briefly summarize what needs to be achieved."
            )
            metrics["clarity"]["score"] = 0.3
        elif len(requirement.title) > 100:
            metrics["clarity"]["feedback"].append(
                "Title is very long. Consider simplifying it for better clarity."
            )
            metrics["clarity"]["score"] = 0.6
        else:
            metrics["clarity"]["score"] = 0.8
        return metrics
    
    async def _analyze_description(self, requirement: Requirement, metrics: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Analyze the requirement description."""
        if len(requirement.description) < 30:
            metrics["completeness"]["feedback"].append(
                "Description is too brief. Provide more details about what, why, and how."
            )
            metrics["completeness"]["score"] = 0.3
        else:
            # Check for completeness indicators
            has_what = "what" in requirement.description.lower()
            has_why = "why" in requirement.description.lower() or "because" in requirement.description.lower()
            has_how = "how" in requirement.description.lower()
            
            completeness_score = 0.4
            if has_what:
                completeness_score += 0.2
            else:
                metrics["completeness"]["feedback"].append(
                    "Add details about WHAT needs to be accomplished"
                )
                
            if has_why:
                completeness_score += 0.2
            else:
                metrics["completeness"]["feedback"].append(
                    "Add context about WHY this requirement matters (business value)"
                )
                
            if has_how:
                completeness_score += 0.2
            else:
                metrics["completeness"]["feedback"].append(
                    "Consider adding guidance on HOW this might be implemented or verified"
                )
                
            metrics["completeness"]["score"] = completeness_score
        return metrics
    
    async def _analyze_testability(self, requirement: Requirement, metrics: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Analyze the requirement testability."""
        testability_words = ["measure", "verify", "test", "validate", "check", "confirm", "demonstrate"]
        testability_count = sum(1 for word in testability_words if word in requirement.description.lower())
        
        if testability_count == 0:
            metrics["testability"]["feedback"].append(
                "Add specific, measurable criteria for verification"
            )
            metrics["testability"]["score"] = 0.3
        else:
            metrics["testability"]["score"] = min(0.3 + (testability_count * 0.15), 1.0)
        return metrics
    
    async def _analyze_feasibility(self, requirement: Requirement, metrics: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Analyze the requirement feasibility."""
        complexity_words = ["complex", "difficult", "challenging", "integrate", "multiple", "all", "every", "always", "never"]
        complexity_count = sum(1 for word in complexity_words if word in requirement.description.lower())
        
        if complexity_count > 3:
            metrics["feasibility"]["feedback"].append(
                "Consider breaking this down into smaller, more manageable requirements"
            )
            metrics["feasibility"]["score"] = 0.5
        else:
            metrics["feasibility"]["score"] = 0.8
            
        # Consistency can't be fully checked without other requirements
        metrics["consistency"]["score"] = 0.7  # Default assumption
        
        return metrics
    
    async def _analyze_metadata(self, requirement: Requirement, metrics: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Analyze requirement metadata (priority, tags, etc.)."""
        if not requirement.priority:
            metrics["completeness"]["feedback"].append(
                "Add a priority level to help with planning"
            )
        
        if not requirement.tags:
            metrics["completeness"]["feedback"].append(
                "Add tags to categorize this requirement"
            )
        
        return metrics
    
    async def _calculate_overall_score(self, metrics: Dict[str, Dict[str, Any]]) -> float:
        """Calculate the overall quality score as a weighted average."""
        overall_score = 0.0
        for criterion, criterion_metrics in metrics.items():
            weight = self.quality_criteria[criterion]["weight"]
            overall_score += criterion_metrics["score"] * weight
        return overall_score
    
    async def _compile_suggestions(self, requirement: Requirement, metrics: Dict[str, Dict[str, Any]]) -> tuple:
        """Compile improvement suggestions and areas from metrics."""
        suggestions = []
        improvement_areas = []
        
        # Extract suggestions from metrics
        for criterion, criterion_metrics in metrics.items():
            if criterion_metrics["score"] < 0.7:
                improvement_areas.append(criterion)
                for feedback in criterion_metrics["feedback"]:
                    suggestions.append(feedback)
        
        # Add best practice suggestions
        if requirement.requirement_type == "functional" and "shall" not in requirement.description.lower():
            suggestions.append(
                "Consider using 'shall' statements for functional requirements (e.g., 'The system shall...')"
            )
        
        # Check for weak words
        weak_words = ["may", "might", "could", "should", "would", "can", "optionally"]
        found_weak_words = [word for word in weak_words if word in requirement.description.lower()]
        if found_weak_words:
            suggestions.append(
                f"Replace weak words ({', '.join(found_weak_words)}) with more definitive terms"
            )
        
        return suggestions, improvement_areas