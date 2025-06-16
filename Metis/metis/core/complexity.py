"""
Complexity analysis for Metis

This module provides functionality for analyzing and scoring task complexity.
It helps evaluate the difficulty and effort required for tasks.
"""

from typing import Dict, List, Optional, Any, Tuple
from metis.models.complexity import ComplexityFactor, ComplexityScore, ComplexityTemplate


# Standard complexity factors
STANDARD_COMPLEXITY_FACTORS = {
    "technical_difficulty": {
        "name": "Technical Difficulty",
        "description": "Technical complexity or difficulty of implementation",
        "weight": 1.5
    },
    "scope_size": {
        "name": "Scope Size",
        "description": "Size or breadth of the task",
        "weight": 1.2
    },
    "dependencies": {
        "name": "Dependencies",
        "description": "Number and complexity of dependencies",
        "weight": 1.0
    },
    "risk": {
        "name": "Risk",
        "description": "Risk level or impact of failure",
        "weight": 1.3
    },
    "knowledge_required": {
        "name": "Knowledge Required",
        "description": "Specialized knowledge or expertise required",
        "weight": 1.0
    }
}


# Standard complexity templates
STANDARD_COMPLEXITY_TEMPLATES = {
    "feature": {
        "name": "Feature Implementation",
        "description": "Template for evaluating new feature implementation",
        "factors": [
            {"name": "Technical Difficulty", "description": "Technical complexity of the feature", "weight": 1.5},
            {"name": "Scope Size", "description": "Size or breadth of the feature", "weight": 1.2},
            {"name": "Integration Complexity", "description": "Complexity of integrating with existing systems", "weight": 1.3},
            {"name": "User Experience", "description": "Complexity of user experience implementation", "weight": 1.1},
            {"name": "Testing Difficulty", "description": "Difficulty of testing the feature", "weight": 1.0}
        ]
    },
    "bug_fix": {
        "name": "Bug Fix",
        "description": "Template for evaluating bug fix complexity",
        "factors": [
            {"name": "Reproduction Difficulty", "description": "Difficulty of reproducing the bug", "weight": 1.2},
            {"name": "Root Cause Analysis", "description": "Complexity of identifying the root cause", "weight": 1.5},
            {"name": "Fix Implementation", "description": "Complexity of implementing the fix", "weight": 1.3},
            {"name": "Regression Risk", "description": "Risk of introducing regressions", "weight": 1.4},
            {"name": "Verification Complexity", "description": "Complexity of verifying the fix", "weight": 1.0}
        ]
    },
    "refactoring": {
        "name": "Code Refactoring",
        "description": "Template for evaluating code refactoring complexity",
        "factors": [
            {"name": "Code Size", "description": "Size of code being refactored", "weight": 1.2},
            {"name": "Structural Complexity", "description": "Complexity of code structure", "weight": 1.5},
            {"name": "Dependency Impact", "description": "Impact on dependent components", "weight": 1.4},
            {"name": "Technical Debt", "description": "Amount of technical debt being addressed", "weight": 1.0},
            {"name": "Testing Coverage", "description": "Level of existing test coverage", "weight": 1.1}
        ]
    }
}


class ComplexityAnalyzer:
    """
    Analyzer for evaluating task complexity.
    
    This class provides tools for creating and managing complexity scores
    for tasks, making consistent complexity evaluations easier.
    """
    
    @staticmethod
    def create_standard_factor(factor_key: str, score: int = 3) -> ComplexityFactor:
        """
        Create a standard complexity factor.
        
        Args:
            factor_key: Key of standard factor to create
            score: Initial score for the factor (1-5)
            
        Returns:
            ComplexityFactor: Created factor
            
        Raises:
            ValueError: If factor_key is not a standard factor
        """
        if factor_key not in STANDARD_COMPLEXITY_FACTORS:
            raise ValueError(f"Unknown standard factor: {factor_key}")
        
        factor_data = STANDARD_COMPLEXITY_FACTORS[factor_key].copy()
        factor_data["score"] = score
        
        return ComplexityFactor(**factor_data)
    
    @staticmethod
    def create_template(template_key: str) -> ComplexityTemplate:
        """
        Create a complexity template from a standard template.
        
        Args:
            template_key: Key of standard template to create
            
        Returns:
            ComplexityTemplate: Created template
            
        Raises:
            ValueError: If template_key is not a standard template
        """
        if template_key not in STANDARD_COMPLEXITY_TEMPLATES:
            raise ValueError(f"Unknown standard template: {template_key}")
        
        template_data = STANDARD_COMPLEXITY_TEMPLATES[template_key].copy()
        
        # Convert factors to ComplexityFactor objects
        factors = []
        for factor_data in template_data["factors"]:
            factors.append(ComplexityFactor(**factor_data))
        
        # Create template
        template = ComplexityTemplate(
            name=template_data["name"],
            description=template_data["description"],
            factors=factors
        )
        
        return template
    
    @staticmethod
    def create_score_from_template(template_key: str) -> ComplexityScore:
        """
        Create a complexity score from a standard template.
        
        Args:
            template_key: Key of standard template to use
            
        Returns:
            ComplexityScore: Created score
            
        Raises:
            ValueError: If template_key is not a standard template
        """
        template = ComplexityAnalyzer.create_template(template_key)
        return template.create_score()
    
    @staticmethod
    def create_empty_score() -> ComplexityScore:
        """
        Create an empty complexity score.
        
        Returns:
            ComplexityScore: Empty score
        """
        return ComplexityScore()
    
    @staticmethod
    def estimate_from_requirements(
        num_requirements: int,
        requirement_complexity: float,
        dependencies: int
    ) -> Tuple[ComplexityScore, str]:
        """
        Estimate complexity based on number of requirements, their complexity,
        and number of dependencies.
        
        Args:
            num_requirements: Number of requirements
            requirement_complexity: Average complexity of requirements (1-5)
            dependencies: Number of dependencies
            
        Returns:
            Tuple[ComplexityScore, str]: Complexity score and explanation
        """
        # Create score
        score = ComplexityScore()
        
        # Add factors
        score.add_factor(ComplexityFactor(
            name="Requirements Quantity",
            description="Number of requirements to implement",
            weight=1.2,
            score=min(5, max(1, round(num_requirements / 2)))
        ))
        
        score.add_factor(ComplexityFactor(
            name="Requirements Complexity",
            description="Average complexity of requirements",
            weight=1.5,
            score=min(5, max(1, round(requirement_complexity)))
        ))
        
        score.add_factor(ComplexityFactor(
            name="Dependencies",
            description="Number of dependencies",
            weight=1.0,
            score=min(5, max(1, round(dependencies / 2)))
        ))
        
        # Create explanation
        explanation = (
            f"Complexity estimate based on {num_requirements} requirements "
            f"with average complexity {requirement_complexity:.1f} and "
            f"{dependencies} dependencies. Overall score: {score.overall_score:.1f} "
            f"({score.level})."
        )
        
        return score, explanation