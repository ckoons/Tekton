"""
Complexity models for Metis

This module defines the complexity scoring models for tasks in the Metis system.
It provides structures for evaluating and representing task complexity.
"""

from datetime import datetime
from pydantic import Field
from uuid import uuid4
from typing import Optional, List, Dict, Any
from tekton.models.base import TektonBaseModel

from metis.models.enums import ComplexityLevel


class ComplexityFactor(TektonBaseModel):
    """
    A single factor contributing to task complexity.
    
    Each factor has a name, weight, and score that contributes to
    the overall complexity score of a task.
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    weight: float = 1.0  # Relative importance of this factor
    score: int = 3  # Score from 1-5
    notes: Optional[str] = None
    
    def calculate_weighted_score(self) -> float:
        """
        Calculate the weighted score for this factor.
        
        Returns:
            float: Weighted score (score * weight)
        """
        return self.score * self.weight


class ComplexityScore(TektonBaseModel):
    """
    Overall complexity score for a task.
    
    Combines multiple complexity factors to produce an overall
    score and complexity level.
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    factors: List[ComplexityFactor] = []
    overall_score: float = 3.0
    level: str = ComplexityLevel.MODERATE.value
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def add_factor(self, factor: ComplexityFactor) -> None:
        """
        Add a complexity factor and recalculate the overall score.
        
        Args:
            factor: Complexity factor to add
        """
        self.factors.append(factor)
        self.recalculate()
    
    def update_factor(self, factor_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a complexity factor by ID and recalculate the overall score.
        
        Args:
            factor_id: ID of the factor to update
            updates: Dictionary of field updates
            
        Returns:
            bool: True if factor was found and updated, False otherwise
        """
        for i, factor in enumerate(self.factors):
            if factor.id == factor_id:
                # Update factor fields
                for key, value in updates.items():
                    if hasattr(factor, key):
                        setattr(factor, key, value)
                
                self.factors[i] = factor
                self.recalculate()
                return True
                
        return False
    
    def remove_factor(self, factor_id: str) -> bool:
        """
        Remove a complexity factor by ID and recalculate the overall score.
        
        Args:
            factor_id: ID of the factor to remove
            
        Returns:
            bool: True if factor was found and removed, False otherwise
        """
        for i, factor in enumerate(self.factors):
            if factor.id == factor_id:
                self.factors.pop(i)
                self.recalculate()
                return True
                
        return False
    
    def recalculate(self) -> None:
        """
        Recalculate the overall complexity score and level.
        
        This method computes a weighted average of all factors
        and updates the overall score and complexity level.
        """
        if not self.factors:
            self.overall_score = 3.0  # Default to moderate
            self.level = ComplexityLevel.MODERATE.value
            return
            
        total_weight = sum(factor.weight for factor in self.factors)
        if total_weight == 0:
            self.overall_score = 3.0  # Default to moderate
            self.level = ComplexityLevel.MODERATE.value
            return
            
        weighted_sum = sum(factor.calculate_weighted_score() for factor in self.factors)
        self.overall_score = weighted_sum / total_weight
        
        # Round to nearest integer for level mapping
        rounded_score = round(self.overall_score)
        self.level = ComplexityLevel.from_score(rounded_score)
        
        # Update the timestamp
        self.updated_at = datetime.utcnow()


class ComplexityTemplate(TektonBaseModel):
    """
    Template for predefined complexity factors.
    
    Used to create consistent complexity scores for similar tasks.
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    factors: List[ComplexityFactor] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def create_score(self) -> ComplexityScore:
        """
        Create a ComplexityScore instance from this template.
        
        Returns:
            ComplexityScore: New complexity score with factors from this template
        """
        # Create a copy of the factors to avoid reference issues
        factor_copies = [ComplexityFactor(**factor.model_dump()) for factor in self.factors]
        
        # Create a new complexity score with these factors
        score = ComplexityScore(factors=factor_copies)
        score.recalculate()
        
        return score