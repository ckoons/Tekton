"""
Intelligence Measurement Framework for Sophia.

This module implements a framework for measuring CI cognitive capabilities
across multiple intelligence dimensions.
"""

import os
import json
import logging
import asyncio
import uuid
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum

from .metrics_engine import get_metrics_engine
from .analysis_engine import get_analysis_engine
from .database import get_database
from sophia.models.intelligence import IntelligenceDimension, MeasurementMethod

# Configure logging
logger = logging.getLogger("sophia.intelligence_measurement")

class IntelligenceMeasurer:
    """Measures intelligence across various dimensions."""
    
    def __init__(self, metrics_engine, analysis_engine):
        """
        Initialize the intelligence measurer.
        
        Args:
            metrics_engine: Metrics engine instance
            analysis_engine: Analysis engine instance
        """
        self.metrics_engine = metrics_engine
        self.analysis_engine = analysis_engine
        
    async def measure_language_processing(self, component_id: str, time_window: str = "7d") -> Dict[str, Any]:
        """
        Measure language processing capabilities.
        
        Args:
            component_id: ID of the component to measure
            time_window: Time window for measurement (e.g., "7d" for 7 days)
            
        Returns:
            Measurement result
        """
        logger.info(f"Measuring language processing for component {component_id}")
        
        # Define metrics related to language processing
        metrics = [
            "ai.language.comprehension",
            "ai.language.generation",
            "ai.language.consistency",
            "ai.language.coherence",
            "ai.language.relevance"
        ]
        
        # Calculate start time
        start_time = self._calculate_start_time(time_window)
        end_time = datetime.utcnow().isoformat() + "Z"
        
        # Collect metrics
        metric_values = {}
        for metric_id in metrics:
            values = await self.metrics_engine.query_metrics(
                metric_id=metric_id,
                source=component_id,
                start_time=start_time,
                end_time=end_time
            )
            
            # Calculate average (if values exist)
            if values:
                avg_value = sum(v.get("value", 0) for v in values) / len(values)
                metric_values[metric_id] = avg_value
            else:
                metric_values[metric_id] = 0.0
                
        # Calculate dimension score (weighted average)
        weights = {
            "ai.language.comprehension": 0.25,
            "ai.language.generation": 0.25,
            "ai.language.consistency": 0.2,
            "ai.language.coherence": 0.15,
            "ai.language.relevance": 0.15
        }
        
        score = 0.0
        total_weight = 0.0
        
        for metric_id, weight in weights.items():
            if metric_id in metric_values:
                score += metric_values[metric_id] * weight
                total_weight += weight
                
        # Normalize score
        if total_weight > 0:
            score = score / total_weight
        else:
            score = 0.0
            
        # Calculate confidence
        confidence = min(1.0, sum(1 for v in metric_values.values() if v > 0) / len(metrics))
        
        # Return result
        return {
            "dimension": IntelligenceDimension.LANGUAGE_PROCESSING,
            "score": score,
            "confidence": confidence,
            "metrics": metric_values,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    async def measure_reasoning(self, component_id: str, time_window: str = "7d") -> Dict[str, Any]:
        """
        Measure reasoning capabilities.
        
        Args:
            component_id: ID of the component to measure
            time_window: Time window for measurement (e.g., "7d" for 7 days)
            
        Returns:
            Measurement result
        """
        logger.info(f"Measuring reasoning for component {component_id}")
        
        # Define metrics related to reasoning
        metrics = [
            "ai.reasoning.logical",
            "ai.reasoning.deductive",
            "ai.reasoning.inductive",
            "ai.reasoning.causal",
            "ai.reasoning.counterfactual"
        ]
        
        # Calculate start time
        start_time = self._calculate_start_time(time_window)
        end_time = datetime.utcnow().isoformat() + "Z"
        
        # Collect metrics
        metric_values = {}
        for metric_id in metrics:
            values = await self.metrics_engine.query_metrics(
                metric_id=metric_id,
                source=component_id,
                start_time=start_time,
                end_time=end_time
            )
            
            # Calculate average (if values exist)
            if values:
                avg_value = sum(v.get("value", 0) for v in values) / len(values)
                metric_values[metric_id] = avg_value
            else:
                metric_values[metric_id] = 0.0
                
        # Calculate dimension score (weighted average)
        weights = {
            "ai.reasoning.logical": 0.25,
            "ai.reasoning.deductive": 0.2,
            "ai.reasoning.inductive": 0.2,
            "ai.reasoning.causal": 0.2,
            "ai.reasoning.counterfactual": 0.15
        }
        
        score = 0.0
        total_weight = 0.0
        
        for metric_id, weight in weights.items():
            if metric_id in metric_values:
                score += metric_values[metric_id] * weight
                total_weight += weight
                
        # Normalize score
        if total_weight > 0:
            score = score / total_weight
        else:
            score = 0.0
            
        # Calculate confidence
        confidence = min(1.0, sum(1 for v in metric_values.values() if v > 0) / len(metrics))
        
        # Return result
        return {
            "dimension": IntelligenceDimension.REASONING,
            "score": score,
            "confidence": confidence,
            "metrics": metric_values,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    async def measure_knowledge(self, component_id: str, time_window: str = "7d") -> Dict[str, Any]:
        """
        Measure knowledge capabilities.
        
        Args:
            component_id: ID of the component to measure
            time_window: Time window for measurement (e.g., "7d" for 7 days)
            
        Returns:
            Measurement result
        """
        logger.info(f"Measuring knowledge for component {component_id}")
        
        # Define metrics related to knowledge
        metrics = [
            "ai.knowledge.factual",
            "ai.knowledge.domain",
            "ai.knowledge.procedural",
            "ai.knowledge.contextual",
            "ai.knowledge.retrieval"
        ]
        
        # Calculate start time
        start_time = self._calculate_start_time(time_window)
        end_time = datetime.utcnow().isoformat() + "Z"
        
        # Collect metrics
        metric_values = {}
        for metric_id in metrics:
            values = await self.metrics_engine.query_metrics(
                metric_id=metric_id,
                source=component_id,
                start_time=start_time,
                end_time=end_time
            )
            
            # Calculate average (if values exist)
            if values:
                avg_value = sum(v.get("value", 0) for v in values) / len(values)
                metric_values[metric_id] = avg_value
            else:
                metric_values[metric_id] = 0.0
                
        # Calculate dimension score (weighted average)
        weights = {
            "ai.knowledge.factual": 0.2,
            "ai.knowledge.domain": 0.25,
            "ai.knowledge.procedural": 0.2,
            "ai.knowledge.contextual": 0.2,
            "ai.knowledge.retrieval": 0.15
        }
        
        score = 0.0
        total_weight = 0.0
        
        for metric_id, weight in weights.items():
            if metric_id in metric_values:
                score += metric_values[metric_id] * weight
                total_weight += weight
                
        # Normalize score
        if total_weight > 0:
            score = score / total_weight
        else:
            score = 0.0
            
        # Calculate confidence
        confidence = min(1.0, sum(1 for v in metric_values.values() if v > 0) / len(metrics))
        
        # Return result
        return {
            "dimension": IntelligenceDimension.KNOWLEDGE,
            "score": score,
            "confidence": confidence,
            "metrics": metric_values,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    async def measure_learning(self, component_id: str, time_window: str = "7d") -> Dict[str, Any]:
        """
        Measure learning capabilities.
        
        Args:
            component_id: ID of the component to measure
            time_window: Time window for measurement (e.g., "7d" for 7 days)
            
        Returns:
            Measurement result
        """
        logger.info(f"Measuring learning for component {component_id}")
        
        # Define metrics related to learning
        metrics = [
            "ai.learning.rate",
            "ai.learning.transfer",
            "ai.learning.adaptation",
            "ai.learning.improvement",
            "ai.learning.retention"
        ]
        
        # Calculate start time
        start_time = self._calculate_start_time(time_window)
        end_time = datetime.utcnow().isoformat() + "Z"
        
        # Collect metrics
        metric_values = {}
        for metric_id in metrics:
            values = await self.metrics_engine.query_metrics(
                metric_id=metric_id,
                source=component_id,
                start_time=start_time,
                end_time=end_time
            )
            
            # Calculate average (if values exist)
            if values:
                avg_value = sum(v.get("value", 0) for v in values) / len(values)
                metric_values[metric_id] = avg_value
            else:
                metric_values[metric_id] = 0.0
                
        # Calculate dimension score (weighted average)
        weights = {
            "ai.learning.rate": 0.2,
            "ai.learning.transfer": 0.2,
            "ai.learning.adaptation": 0.25,
            "ai.learning.improvement": 0.2,
            "ai.learning.retention": 0.15
        }
        
        score = 0.0
        total_weight = 0.0
        
        for metric_id, weight in weights.items():
            if metric_id in metric_values:
                score += metric_values[metric_id] * weight
                total_weight += weight
                
        # Normalize score
        if total_weight > 0:
            score = score / total_weight
        else:
            score = 0.0
            
        # Calculate confidence
        confidence = min(1.0, sum(1 for v in metric_values.values() if v > 0) / len(metrics))
        
        # Return result
        return {
            "dimension": IntelligenceDimension.LEARNING,
            "score": score,
            "confidence": confidence,
            "metrics": metric_values,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    async def measure_creativity(self, component_id: str, time_window: str = "7d") -> Dict[str, Any]:
        """
        Measure creativity capabilities.
        
        Args:
            component_id: ID of the component to measure
            time_window: Time window for measurement (e.g., "7d" for 7 days)
            
        Returns:
            Measurement result
        """
        logger.info(f"Measuring creativity for component {component_id}")
        
        # Define metrics related to creativity
        metrics = [
            "ai.creativity.novelty",
            "ai.creativity.originality",
            "ai.creativity.flexibility",
            "ai.creativity.elaboration",
            "ai.creativity.usefulness"
        ]
        
        # Calculate start time
        start_time = self._calculate_start_time(time_window)
        end_time = datetime.utcnow().isoformat() + "Z"
        
        # Collect metrics
        metric_values = {}
        for metric_id in metrics:
            values = await self.metrics_engine.query_metrics(
                metric_id=metric_id,
                source=component_id,
                start_time=start_time,
                end_time=end_time
            )
            
            # Calculate average (if values exist)
            if values:
                avg_value = sum(v.get("value", 0) for v in values) / len(values)
                metric_values[metric_id] = avg_value
            else:
                metric_values[metric_id] = 0.0
                
        # Calculate dimension score (weighted average)
        weights = {
            "ai.creativity.novelty": 0.25,
            "ai.creativity.originality": 0.2,
            "ai.creativity.flexibility": 0.2,
            "ai.creativity.elaboration": 0.15,
            "ai.creativity.usefulness": 0.2
        }
        
        score = 0.0
        total_weight = 0.0
        
        for metric_id, weight in weights.items():
            if metric_id in metric_values:
                score += metric_values[metric_id] * weight
                total_weight += weight
                
        # Normalize score
        if total_weight > 0:
            score = score / total_weight
        else:
            score = 0.0
            
        # Calculate confidence
        confidence = min(1.0, sum(1 for v in metric_values.values() if v > 0) / len(metrics))
        
        # Return result
        return {
            "dimension": IntelligenceDimension.CREATIVITY,
            "score": score,
            "confidence": confidence,
            "metrics": metric_values,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    async def measure_planning(self, component_id: str, time_window: str = "7d") -> Dict[str, Any]:
        """
        Measure planning capabilities.
        
        Args:
            component_id: ID of the component to measure
            time_window: Time window for measurement (e.g., "7d" for 7 days)
            
        Returns:
            Measurement result
        """
        logger.info(f"Measuring planning for component {component_id}")
        
        # Define metrics related to planning
        metrics = [
            "ai.planning.goal_setting",
            "ai.planning.sequencing",
            "ai.planning.resource_allocation",
            "ai.planning.contingency",
            "ai.planning.optimization"
        ]
        
        # Calculate start time
        start_time = self._calculate_start_time(time_window)
        end_time = datetime.utcnow().isoformat() + "Z"
        
        # Collect metrics
        metric_values = {}
        for metric_id in metrics:
            values = await self.metrics_engine.query_metrics(
                metric_id=metric_id,
                source=component_id,
                start_time=start_time,
                end_time=end_time
            )
            
            # Calculate average (if values exist)
            if values:
                avg_value = sum(v.get("value", 0) for v in values) / len(values)
                metric_values[metric_id] = avg_value
            else:
                metric_values[metric_id] = 0.0
                
        # Calculate dimension score (weighted average)
        weights = {
            "ai.planning.goal_setting": 0.2,
            "ai.planning.sequencing": 0.2,
            "ai.planning.resource_allocation": 0.2,
            "ai.planning.contingency": 0.2,
            "ai.planning.optimization": 0.2
        }
        
        score = 0.0
        total_weight = 0.0
        
        for metric_id, weight in weights.items():
            if metric_id in metric_values:
                score += metric_values[metric_id] * weight
                total_weight += weight
                
        # Normalize score
        if total_weight > 0:
            score = score / total_weight
        else:
            score = 0.0
            
        # Calculate confidence
        confidence = min(1.0, sum(1 for v in metric_values.values() if v > 0) / len(metrics))
        
        # Return result
        return {
            "dimension": IntelligenceDimension.PLANNING,
            "score": score,
            "confidence": confidence,
            "metrics": metric_values,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    async def measure_problem_solving(self, component_id: str, time_window: str = "7d") -> Dict[str, Any]:
        """
        Measure problem solving capabilities.
        
        Args:
            component_id: ID of the component to measure
            time_window: Time window for measurement (e.g., "7d" for 7 days)
            
        Returns:
            Measurement result
        """
        logger.info(f"Measuring problem solving for component {component_id}")
        
        # Define metrics related to problem solving
        metrics = [
            "ai.problem_solving.identification",
            "ai.problem_solving.analysis",
            "ai.problem_solving.solution_generation",
            "ai.problem_solving.evaluation",
            "ai.problem_solving.implementation"
        ]
        
        # Calculate start time
        start_time = self._calculate_start_time(time_window)
        end_time = datetime.utcnow().isoformat() + "Z"
        
        # Collect metrics
        metric_values = {}
        for metric_id in metrics:
            values = await self.metrics_engine.query_metrics(
                metric_id=metric_id,
                source=component_id,
                start_time=start_time,
                end_time=end_time
            )
            
            # Calculate average (if values exist)
            if values:
                avg_value = sum(v.get("value", 0) for v in values) / len(values)
                metric_values[metric_id] = avg_value
            else:
                metric_values[metric_id] = 0.0
                
        # Calculate dimension score (weighted average)
        weights = {
            "ai.problem_solving.identification": 0.2,
            "ai.problem_solving.analysis": 0.2,
            "ai.problem_solving.solution_generation": 0.25,
            "ai.problem_solving.evaluation": 0.2,
            "ai.problem_solving.implementation": 0.15
        }
        
        score = 0.0
        total_weight = 0.0
        
        for metric_id, weight in weights.items():
            if metric_id in metric_values:
                score += metric_values[metric_id] * weight
                total_weight += weight
                
        # Normalize score
        if total_weight > 0:
            score = score / total_weight
        else:
            score = 0.0
            
        # Calculate confidence
        confidence = min(1.0, sum(1 for v in metric_values.values() if v > 0) / len(metrics))
        
        # Return result
        return {
            "dimension": IntelligenceDimension.PROBLEM_SOLVING,
            "score": score,
            "confidence": confidence,
            "metrics": metric_values,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    async def measure_adaptation(self, component_id: str, time_window: str = "7d") -> Dict[str, Any]:
        """
        Measure adaptation capabilities.
        
        Args:
            component_id: ID of the component to measure
            time_window: Time window for measurement (e.g., "7d" for 7 days)
            
        Returns:
            Measurement result
        """
        logger.info(f"Measuring adaptation for component {component_id}")
        
        # Define metrics related to adaptation
        metrics = [
            "ai.adaptation.environment",
            "ai.adaptation.requirement",
            "ai.adaptation.feedback",
            "ai.adaptation.error",
            "ai.adaptation.degradation"
        ]
        
        # Calculate start time
        start_time = self._calculate_start_time(time_window)
        end_time = datetime.utcnow().isoformat() + "Z"
        
        # Collect metrics
        metric_values = {}
        for metric_id in metrics:
            values = await self.metrics_engine.query_metrics(
                metric_id=metric_id,
                source=component_id,
                start_time=start_time,
                end_time=end_time
            )
            
            # Calculate average (if values exist)
            if values:
                avg_value = sum(v.get("value", 0) for v in values) / len(values)
                metric_values[metric_id] = avg_value
            else:
                metric_values[metric_id] = 0.0
                
        # Calculate dimension score (weighted average)
        weights = {
            "ai.adaptation.environment": 0.2,
            "ai.adaptation.requirement": 0.2,
            "ai.adaptation.feedback": 0.25,
            "ai.adaptation.error": 0.2,
            "ai.adaptation.degradation": 0.15
        }
        
        score = 0.0
        total_weight = 0.0
        
        for metric_id, weight in weights.items():
            if metric_id in metric_values:
                score += metric_values[metric_id] * weight
                total_weight += weight
                
        # Normalize score
        if total_weight > 0:
            score = score / total_weight
        else:
            score = 0.0
            
        # Calculate confidence
        confidence = min(1.0, sum(1 for v in metric_values.values() if v > 0) / len(metrics))
        
        # Return result
        return {
            "dimension": IntelligenceDimension.ADAPTATION,
            "score": score,
            "confidence": confidence,
            "metrics": metric_values,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    async def measure_collaboration(self, component_id: str, time_window: str = "7d") -> Dict[str, Any]:
        """
        Measure collaboration capabilities.
        
        Args:
            component_id: ID of the component to measure
            time_window: Time window for measurement (e.g., "7d" for 7 days)
            
        Returns:
            Measurement result
        """
        logger.info(f"Measuring collaboration for component {component_id}")
        
        # Define metrics related to collaboration
        metrics = [
            "ai.collaboration.communication",
            "ai.collaboration.coordination",
            "ai.collaboration.information_sharing",
            "ai.collaboration.task_division",
            "ai.collaboration.conflict_resolution"
        ]
        
        # Calculate start time
        start_time = self._calculate_start_time(time_window)
        end_time = datetime.utcnow().isoformat() + "Z"
        
        # Collect metrics
        metric_values = {}
        for metric_id in metrics:
            values = await self.metrics_engine.query_metrics(
                metric_id=metric_id,
                source=component_id,
                start_time=start_time,
                end_time=end_time
            )
            
            # Calculate average (if values exist)
            if values:
                avg_value = sum(v.get("value", 0) for v in values) / len(values)
                metric_values[metric_id] = avg_value
            else:
                metric_values[metric_id] = 0.0
                
        # Calculate dimension score (weighted average)
        weights = {
            "ai.collaboration.communication": 0.25,
            "ai.collaboration.coordination": 0.2,
            "ai.collaboration.information_sharing": 0.2,
            "ai.collaboration.task_division": 0.2,
            "ai.collaboration.conflict_resolution": 0.15
        }
        
        score = 0.0
        total_weight = 0.0
        
        for metric_id, weight in weights.items():
            if metric_id in metric_values:
                score += metric_values[metric_id] * weight
                total_weight += weight
                
        # Normalize score
        if total_weight > 0:
            score = score / total_weight
        else:
            score = 0.0
            
        # Calculate confidence
        confidence = min(1.0, sum(1 for v in metric_values.values() if v > 0) / len(metrics))
        
        # Return result
        return {
            "dimension": IntelligenceDimension.COLLABORATION,
            "score": score,
            "confidence": confidence,
            "metrics": metric_values,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    async def measure_metacognition(self, component_id: str, time_window: str = "7d") -> Dict[str, Any]:
        """
        Measure metacognition capabilities.
        
        Args:
            component_id: ID of the component to measure
            time_window: Time window for measurement (e.g., "7d" for 7 days)
            
        Returns:
            Measurement result
        """
        logger.info(f"Measuring metacognition for component {component_id}")
        
        # Define metrics related to metacognition
        metrics = [
            "ai.metacognition.self_awareness",
            "ai.metacognition.confidence_calibration",
            "ai.metacognition.task_monitor",
            "ai.metacognition.strategy_selection",
            "ai.metacognition.error_detection"
        ]
        
        # Calculate start time
        start_time = self._calculate_start_time(time_window)
        end_time = datetime.utcnow().isoformat() + "Z"
        
        # Collect metrics
        metric_values = {}
        for metric_id in metrics:
            values = await self.metrics_engine.query_metrics(
                metric_id=metric_id,
                source=component_id,
                start_time=start_time,
                end_time=end_time
            )
            
            # Calculate average (if values exist)
            if values:
                avg_value = sum(v.get("value", 0) for v in values) / len(values)
                metric_values[metric_id] = avg_value
            else:
                metric_values[metric_id] = 0.0
                
        # Calculate dimension score (weighted average)
        weights = {
            "ai.metacognition.self_awareness": 0.25,
            "ai.metacognition.confidence_calibration": 0.2,
            "ai.metacognition.task_monitor": 0.2,
            "ai.metacognition.strategy_selection": 0.2,
            "ai.metacognition.error_detection": 0.15
        }
        
        score = 0.0
        total_weight = 0.0
        
        for metric_id, weight in weights.items():
            if metric_id in metric_values:
                score += metric_values[metric_id] * weight
                total_weight += weight
                
        # Normalize score
        if total_weight > 0:
            score = score / total_weight
        else:
            score = 0.0
            
        # Calculate confidence
        confidence = min(1.0, sum(1 for v in metric_values.values() if v > 0) / len(metrics))
        
        # Return result
        return {
            "dimension": IntelligenceDimension.METACOGNITION,
            "score": score,
            "confidence": confidence,
            "metrics": metric_values,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    async def measure_all_dimensions(self, component_id: str, time_window: str = "7d") -> Dict[str, Dict[str, Any]]:
        """
        Measure all intelligence dimensions.
        
        Args:
            component_id: ID of the component to measure
            time_window: Time window for measurement (e.g., "7d" for 7 days)
            
        Returns:
            Dictionary of dimension measurements
        """
        logger.info(f"Measuring all intelligence dimensions for component {component_id}")
        
        # Define measurement functions for each dimension
        measurement_functions = {
            IntelligenceDimension.LANGUAGE_PROCESSING: self.measure_language_processing,
            IntelligenceDimension.REASONING: self.measure_reasoning,
            IntelligenceDimension.KNOWLEDGE: self.measure_knowledge,
            IntelligenceDimension.LEARNING: self.measure_learning,
            IntelligenceDimension.CREATIVITY: self.measure_creativity,
            IntelligenceDimension.PLANNING: self.measure_planning,
            IntelligenceDimension.PROBLEM_SOLVING: self.measure_problem_solving,
            IntelligenceDimension.ADAPTATION: self.measure_adaptation,
            IntelligenceDimension.COLLABORATION: self.measure_collaboration,
            IntelligenceDimension.METACOGNITION: self.measure_metacognition
        }
        
        # Measure all dimensions in parallel
        tasks = []
        for dimension, measure_func in measurement_functions.items():
            task = asyncio.create_task(measure_func(component_id, time_window))
            tasks.append((dimension, task))
            
        # Collect results
        measurements = {}
        for dimension, task in tasks:
            try:
                result = await task
                measurements[dimension] = result
            except Exception as e:
                logger.error(f"Error measuring {dimension} for component {component_id}: {e}")
                # Add placeholder for failed measurement
                measurements[dimension] = {
                    "dimension": dimension,
                    "score": 0.0,
                    "confidence": 0.0,
                    "metrics": {},
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "error": str(e)
                }
                
        return measurements
        
    def _calculate_start_time(self, time_window: str) -> str:
        """
        Calculate start time based on time window.
        
        Args:
            time_window: Time window (e.g., "7d" for 7 days)
            
        Returns:
            Start time in ISO format
        """
        now = datetime.utcnow()
        
        # Parse time window
        if time_window.endswith("d"):
            days = int(time_window[:-1])
            delta = days * 24 * 60 * 60  # Convert days to seconds
        elif time_window.endswith("h"):
            hours = int(time_window[:-1])
            delta = hours * 60 * 60  # Convert hours to seconds
        elif time_window.endswith("m"):
            minutes = int(time_window[:-1])
            delta = minutes * 60  # Convert minutes to seconds
        elif time_window.endswith("s"):
            delta = int(time_window[:-1])  # Already in seconds
        else:
            # Default to 7 days
            delta = 7 * 24 * 60 * 60
            
        # Calculate start time
        start_time = now.timestamp() - delta
        start_dt = datetime.fromtimestamp(start_time)
        
        return start_dt.isoformat() + "Z"

class IntelligenceMeasurement:
    """
    Intelligence Measurement Framework for Sophia.
    
    Provides a framework for measuring CI cognitive capabilities
    across multiple intelligence dimensions.
    """
    
    def __init__(self):
        """Initialize the intelligence measurement framework."""
        self.is_initialized = False
        self.metrics_engine = None
        self.analysis_engine = None
        self.database = None
        self.measurer = None
        self.measurements = {}
        self.profiles = {}
        
    async def initialize(self) -> bool:
        """
        Initialize the intelligence measurement framework.
        
        Returns:
            True if initialization was successful
        """
        logger.info("Initializing Sophia Intelligence Measurement Framework...")
        
        # Get required engines and database
        self.metrics_engine = await get_metrics_engine()
        self.analysis_engine = await get_analysis_engine()
        self.database = await get_database()
        
        # Create intelligence measurer
        self.measurer = IntelligenceMeasurer(
            metrics_engine=self.metrics_engine,
            analysis_engine=self.analysis_engine
        )
        
        # Load existing measurements and profiles
        await self._load_measurements()
        
        self.is_initialized = True
        logger.info("Sophia Intelligence Measurement Framework initialized successfully")
        return True
        
    async def start(self) -> bool:
        """
        Start the intelligence measurement framework.
        
        Returns:
            True if successful
        """
        if not self.is_initialized:
            success = await self.initialize()
            if not success:
                logger.error("Failed to initialize Intelligence Measurement Framework")
                return False
                
        logger.info("Starting Sophia Intelligence Measurement Framework...")
        logger.info("Sophia Intelligence Measurement Framework started successfully")
        return True
        
    async def stop(self) -> bool:
        """
        Stop the intelligence measurement framework and clean up resources.
        
        Returns:
            True if successful
        """
        logger.info("Stopping Sophia Intelligence Measurement Framework...")
        
        # Save measurements and profiles
        await self._save_measurements()
        
        logger.info("Sophia Intelligence Measurement Framework stopped successfully")
        return True
        
    async def record_measurement(
        self,
        component_id: str,
        dimension: Union[str, IntelligenceDimension],
        measurement_method: Union[str, MeasurementMethod],
        score: float,
        confidence: float,
        context: Dict[str, Any],
        evidence: Dict[str, Any],
        evaluator: Optional[str] = None,
        timestamp: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Record an intelligence measurement.
        
        Args:
            component_id: ID of the component being measured
            dimension: Intelligence dimension being measured
            measurement_method: Method used for measurement
            score: Measurement score (0.0-1.0)
            confidence: Confidence in the measurement (0.0-1.0)
            context: Context of the measurement
            evidence: Evidence supporting the measurement
            evaluator: Entity performing the evaluation
            timestamp: Timestamp of the measurement (ISO format)
            tags: Tags for categorizing the measurement
            
        Returns:
            Measurement ID
        """
        if not self.is_initialized:
            await self.initialize()
            
        # Validate inputs
        if not 0.0 <= score <= 1.0:
            score = max(0.0, min(score, 1.0))
            logger.warning(f"Score adjusted to range [0.0, 1.0]: {score}")
            
        if not 0.0 <= confidence <= 1.0:
            confidence = max(0.0, min(confidence, 1.0))
            logger.warning(f"Confidence adjusted to range [0.0, 1.0]: {confidence}")
            
        # Convert dimension to string if it's an enum
        if isinstance(dimension, IntelligenceDimension):
            dimension = dimension.value
            
        # Convert measurement_method to string if it's an enum
        if isinstance(measurement_method, MeasurementMethod):
            measurement_method = measurement_method.value
            
        # Create measurement ID
        measurement_id = str(uuid.uuid4())
        
        # Set timestamp if not provided
        if not timestamp:
            timestamp = datetime.utcnow().isoformat() + "Z"
            
        # Create measurement
        measurement = {
            "id": measurement_id,
            "component_id": component_id,
            "dimension": dimension,
            "measurement_method": measurement_method,
            "score": score,
            "confidence": confidence,
            "context": context,
            "evidence": evidence,
            "evaluator": evaluator,
            "timestamp": timestamp,
            "tags": tags or []
        }
        
        # Store measurement in memory and database
        self.measurements[measurement_id] = measurement
        
        # Save to database
        await self._save_measurement_to_database(measurement)
        
        # Update component profile
        await self._update_component_profile(component_id, measurement)
        
        # Save profiles to database
        await self._save_profile_to_database(component_id, self.profiles[component_id])
        
        logger.info(f"Recorded intelligence measurement {measurement_id} for component {component_id}")
        return measurement_id
        
    async def query_measurements(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Query intelligence measurements with filtering.
        
        Args:
            query: Query parameters
            
        Returns:
            List of matching measurements
        """
        if not self.is_initialized:
            await self.initialize()
            
        filtered_measurements = []
        
        # Extract query parameters
        component_id = query.get("component_id")
        dimensions = query.get("dimensions")
        measurement_method = query.get("measurement_method")
        min_score = query.get("min_score")
        max_score = query.get("max_score")
        min_confidence = query.get("min_confidence")
        evaluator = query.get("evaluator")
        measured_after = query.get("measured_after")
        measured_before = query.get("measured_before")
        tags = query.get("tags")
        limit = query.get("limit", 100)
        offset = query.get("offset", 0)
        
        # Convert to ISO format if needed
        if measured_after and not measured_after.endswith("Z"):
            measured_after = measured_after + "Z"
        if measured_before and not measured_before.endswith("Z"):
            measured_before = measured_before + "Z"
            
        # Filter measurements
        for measurement_id, measurement in self.measurements.items():
            # Check component ID
            if component_id and measurement.get("component_id") != component_id:
                continue
                
            # Check dimension
            if dimensions and measurement.get("dimension") not in dimensions:
                continue
                
            # Check measurement method
            if measurement_method and measurement.get("measurement_method") != measurement_method:
                continue
                
            # Check score
            score = measurement.get("score", 0)
            if min_score is not None and score < min_score:
                continue
            if max_score is not None and score > max_score:
                continue
                
            # Check confidence
            confidence = measurement.get("confidence", 0)
            if min_confidence is not None and confidence < min_confidence:
                continue
                
            # Check evaluator
            if evaluator and measurement.get("evaluator") != evaluator:
                continue
                
            # Check timestamp
            timestamp = measurement.get("timestamp", "")
            if measured_after and timestamp < measured_after:
                continue
            if measured_before and timestamp > measured_before:
                continue
                
            # Check tags
            if tags and not any(tag in measurement.get("tags", []) for tag in tags):
                continue
                
            # Add to filtered list
            filtered_measurements.append(measurement)
            
        # Sort by timestamp (newest first)
        filtered_measurements.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Apply pagination
        paginated_measurements = filtered_measurements[offset:offset + limit]
        
        return paginated_measurements
        
    async def get_component_profile(self, component_id: str, timestamp: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get the intelligence profile of a component.
        
        Args:
            component_id: ID of the component
            timestamp: Timestamp for historical profile (ISO format)
            
        Returns:
            Component intelligence profile or None if not found
        """
        if not self.is_initialized:
            await self.initialize()
            
        # Check if component exists
        if component_id not in self.profiles:
            logger.warning(f"No intelligence profile found for component {component_id}")
            return None
            
        # Get the latest profile if timestamp not provided
        if not timestamp:
            return self.profiles[component_id]
            
        # TODO: Implement historical profile retrieval
        logger.warning("Historical profile retrieval not implemented yet")
        return self.profiles[component_id]
        
    async def compare_components(
        self,
        component_ids: List[str],
        dimensions: Optional[List[Union[str, IntelligenceDimension]]] = None
    ) -> Dict[str, Any]:
        """
        Compare intelligence between components.
        
        Args:
            component_ids: List of component IDs to compare
            dimensions: Dimensions to compare (all if None)
            
        Returns:
            Comparison result
        """
        if not self.is_initialized:
            await self.initialize()
            
        # Validate inputs
        if len(component_ids) < 2:
            raise ValueError("At least two components must be provided for comparison")
            
        # Convert dimensions to strings if they're enums
        if dimensions:
            dimensions = [d.value if isinstance(d, IntelligenceDimension) else d for d in dimensions]
            
        # Get profiles for all components
        profiles = {}
        missing_components = []
        
        for component_id in component_ids:
            profile = await self.get_component_profile(component_id)
            if profile:
                profiles[component_id] = profile
            else:
                missing_components.append(component_id)
                
        if missing_components:
            logger.warning(f"No profiles found for components: {missing_components}")
            
        if not profiles:
            raise ValueError("No valid component profiles found for comparison")
            
        # Extract scores for each dimension
        all_dimensions = set()
        for profile in profiles.values():
            all_dimensions.update(profile.get("dimensions", {}).keys())
            
        # Filter dimensions if specified
        if dimensions:
            all_dimensions = [d for d in all_dimensions if d in dimensions]
            
        # Build comparison
        scores = {}
        for component_id, profile in profiles.items():
            component_scores = {}
            for dimension in all_dimensions:
                component_scores[dimension] = profile.get("dimensions", {}).get(dimension, 0)
            scores[component_id] = component_scores
            
        # Calculate relative strengths
        relative_strengths = {}
        for component_id in profiles.keys():
            component_strengths = []
            
            for dimension in all_dimensions:
                # Check if this component has the highest score for this dimension
                component_score = scores[component_id].get(dimension, 0)
                is_best = True
                
                for other_id in profiles.keys():
                    if other_id != component_id:
                        other_score = scores[other_id].get(dimension, 0)
                        if other_score > component_score:
                            is_best = False
                            break
                            
                if is_best and component_score > 0:
                    component_strengths.append(dimension)
                    
            relative_strengths[component_id] = component_strengths
            
        # Calculate collaboration potential
        collaboration_potential = {}
        
        for component_id in profiles.keys():
            component_collaboration = {}
            
            for other_id in profiles.keys():
                if other_id != component_id:
                    # Calculate complementarity score
                    complementarity = 0
                    dimension_count = 0
                    
                    for dimension in all_dimensions:
                        component_score = scores[component_id].get(dimension, 0)
                        other_score = scores[other_id].get(dimension, 0)
                        
                        # Components with different strengths have higher complementarity
                        if component_score > 0 and other_score > 0:
                            complementarity += 1 - abs(component_score - other_score)
                            dimension_count += 1
                            
                    # Normalize complementarity score
                    if dimension_count > 0:
                        complementarity = complementarity / dimension_count
                    else:
                        complementarity = 0
                        
                    component_collaboration[other_id] = complementarity
                    
            collaboration_potential[component_id] = component_collaboration
            
        # Create comparison result
        comparison = {
            "component_ids": list(profiles.keys()),
            "dimensions": list(all_dimensions),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "scores": scores,
            "relative_strengths": relative_strengths,
            "collaboration_potential": collaboration_potential
        }
        
        return comparison
        
    async def get_intelligence_dimensions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all intelligence dimensions.
        
        Returns:
            Dictionary of intelligence dimensions
        """
        # Load dimension information from file
        dimensions_file = os.path.join(os.path.dirname(__file__), "data", "intelligence_dimensions.json")
        
        try:
            if os.path.exists(dimensions_file):
                with open(dimensions_file, "r") as f:
                    dimensions = json.load(f)
            else:
                # Create default dimensions
                dimensions = self._create_default_dimensions()
                
                # Save to file
                os.makedirs(os.path.dirname(dimensions_file), exist_ok=True)
                with open(dimensions_file, "w") as f:
                    json.dump(dimensions, f, indent=2)
                    
            return dimensions
        except Exception as e:
            logger.error(f"Error loading intelligence dimensions: {e}")
            return self._create_default_dimensions()
            
    async def get_intelligence_dimension(self, dimension: Union[str, IntelligenceDimension]) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific intelligence dimension.
        
        Args:
            dimension: Intelligence dimension
            
        Returns:
            Dimension information or None if not found
        """
        # Convert dimension to string if it's an enum
        if isinstance(dimension, IntelligenceDimension):
            dimension = dimension.value
            
        # Get all dimensions
        dimensions = await self.get_intelligence_dimensions()
        
        # Return specific dimension
        return dimensions.get(dimension)
        
    async def get_ecosystem_profile(self) -> Dict[str, Any]:
        """
        Get an intelligence profile for the entire Tekton ecosystem.
        
        Returns:
            Ecosystem intelligence profile
        """
        if not self.is_initialized:
            await self.initialize()
            
        # Get profiles for all components
        all_profiles = list(self.profiles.values())
        
        if not all_profiles:
            logger.warning("No component profiles found for ecosystem profile")
            return {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "dimensions": {},
                "overall_score": 0.0,
                "confidence": 0.0,
                "strengths": [],
                "improvement_areas": []
            }
            
        # Calculate aggregate scores for each dimension
        all_dimensions = set()
        for profile in all_profiles:
            all_dimensions.update(profile.get("dimensions", {}).keys())
            
        dimension_scores = {}
        dimension_confidences = {}
        
        for dimension in all_dimensions:
            scores = []
            confidences = []
            
            for profile in all_profiles:
                if dimension in profile.get("dimensions", {}):
                    scores.append(profile["dimensions"][dimension])
                    confidences.append(profile.get("confidence", {}).get(dimension, 0.0))
                    
            if scores:
                # Calculate weighted average score
                total_weighted_score = 0.0
                total_weight = 0.0
                
                for score, confidence in zip(scores, confidences):
                    total_weighted_score += score * confidence
                    total_weight += confidence
                    
                if total_weight > 0:
                    dimension_scores[dimension] = total_weighted_score / total_weight
                else:
                    dimension_scores[dimension] = sum(scores) / len(scores)
                    
                # Calculate average confidence
                dimension_confidences[dimension] = sum(confidences) / len(confidences) if confidences else 0.0
                
        # Calculate overall score
        overall_score = sum(dimension_scores.values()) / len(dimension_scores) if dimension_scores else 0.0
        
        # Calculate overall confidence
        overall_confidence = sum(dimension_confidences.values()) / len(dimension_confidences) if dimension_confidences else 0.0
        
        # Identify strengths and improvement areas
        strengths = []
        improvement_areas = []
        
        for dimension, score in dimension_scores.items():
            if score >= 0.7:
                strengths.append(dimension)
            elif score <= 0.4:
                improvement_areas.append(dimension)
                
        # Create ecosystem profile
        ecosystem_profile = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "dimensions": dimension_scores,
            "overall_score": overall_score,
            "confidence": dimension_confidences,
            "strengths": strengths,
            "improvement_areas": improvement_areas
        }
        
        return ecosystem_profile
        
    async def measure_component(self, component_id: str, time_window: str = "7d") -> Dict[str, Any]:
        """
        Measure all intelligence dimensions for a component.
        
        Args:
            component_id: ID of the component to measure
            time_window: Time window for measurement (e.g., "7d" for 7 days)
            
        Returns:
            Measurement result
        """
        if not self.is_initialized:
            await self.initialize()
            
        # Measure all dimensions
        measurements = await self.measurer.measure_all_dimensions(component_id, time_window)
        
        # Record measurements
        for dimension, measurement in measurements.items():
            if "error" not in measurement:  # Skip failed measurements
                await self.record_measurement(
                    component_id=component_id,
                    dimension=dimension,
                    measurement_method=MeasurementMethod.METRICS_ANALYSIS,
                    score=measurement["score"],
                    confidence=measurement["confidence"],
                    context={"time_window": time_window},
                    evidence={"metrics": measurement["metrics"]},
                    evaluator="SophiaAutomatedMeasurement",
                    timestamp=measurement["timestamp"]
                )
                
        # Return the updated profile
        return await self.get_component_profile(component_id)
        
    async def _update_component_profile(self, component_id: str, measurement: Dict[str, Any]) -> None:
        """
        Update a component's intelligence profile with a new measurement.
        
        Args:
            component_id: ID of the component
            measurement: New measurement
        """
        # Get existing profile or create new one
        profile = self.profiles.get(component_id, {
            "component_id": component_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "dimensions": {},
            "confidence": {},
            "strengths": [],
            "improvement_areas": []
        })
        
        # Extract dimension and score
        dimension = measurement.get("dimension")
        score = measurement.get("score", 0)
        confidence = measurement.get("confidence", 0)
        
        # Update dimension score (weighted by confidence)
        if dimension:
            existing_score = profile["dimensions"].get(dimension, 0)
            existing_confidence = profile["confidence"].get(dimension, 0)
            
            # Calculate new score with confidence weighting
            if existing_confidence > 0 or confidence > 0:
                new_score = (existing_score * existing_confidence + score * confidence) / (existing_confidence + confidence)
                new_confidence = (existing_confidence + confidence) / 2
            else:
                new_score = score
                new_confidence = confidence
                
            # Update profile
            profile["dimensions"][dimension] = new_score
            profile["confidence"][dimension] = new_confidence
            
        # Update timestamp
        profile["timestamp"] = datetime.utcnow().isoformat() + "Z"
        
        # Recalculate strengths and improvement areas
        strengths = []
        improvement_areas = []
        
        for dim, dim_score in profile["dimensions"].items():
            if dim_score >= 0.7:
                strengths.append(dim)
            elif dim_score <= 0.4:
                improvement_areas.append(dim)
                
        profile["strengths"] = strengths
        profile["improvement_areas"] = improvement_areas
        
        # Calculate overall score
        if profile["dimensions"]:
            profile["overall_score"] = sum(profile["dimensions"].values()) / len(profile["dimensions"])
        else:
            profile["overall_score"] = 0.0
            
        # Store updated profile
        self.profiles[component_id] = profile
    
    async def _save_measurement_to_database(self, measurement: Dict[str, Any]) -> bool:
        """
        Save intelligence measurement to database.
        
        Args:
            measurement: Measurement to save
            
        Returns:
            True if successful
        """
        try:
            await self.database.connection.execute("""
                INSERT INTO intelligence_measurements 
                (component_name, dimension, value, context, measurement_type, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                measurement.get('component_id'),
                measurement.get('dimension'),
                measurement.get('score'),
                json.dumps({
                    'measurement_method': measurement.get('measurement_method'),
                    'confidence': measurement.get('confidence'),
                    'context': measurement.get('context'),
                    'evidence': measurement.get('evidence'),
                    'evaluator': measurement.get('evaluator'),
                    'tags': measurement.get('tags', [])
                }),
                measurement.get('measurement_method'),
                measurement.get('timestamp')
            ))
            await self.database.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving measurement to database: {str(e)}")
            return False
    
    async def _save_profile_to_database(self, component_id: str, profile: Dict[str, Any]) -> bool:
        """
        Save intelligence profile to database.
        
        Args:
            component_id: Component ID
            profile: Profile to save
            
        Returns:
            True if successful
        """
        try:
            # Use the database method we implemented earlier
            await self.database.save_intelligence_profile(component_id, profile)
            return True
        except Exception as e:
            logger.error(f"Error saving profile to database: {str(e)}")
            return False
        
    async def _load_measurements(self) -> bool:
        """
        Load measurements and profiles from database.
        
        Returns:
            True if successful
        """
        try:
            # Load intelligence measurements from database
            cursor = await self.database.connection.execute("""
                SELECT * FROM intelligence_measurements ORDER BY timestamp DESC
            """)
            measurement_rows = await cursor.fetchall()
            
            # Convert database rows to measurement objects
            self.measurements = {}
            for row in measurement_rows:
                measurement_id = str(uuid.uuid4())  # Generate ID for in-memory storage
                
                # Parse context JSON
                context_data = {}
                if row['context']:
                    try:
                        context_data = json.loads(row['context'])
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse context for measurement: {row['context']}")
                
                measurement = {
                    'id': measurement_id,
                    'component_id': row['component_name'],
                    'dimension': row['dimension'], 
                    'score': row['value'],
                    'timestamp': row['timestamp'],
                    'measurement_method': context_data.get('measurement_method', row['measurement_type']),
                    'confidence': context_data.get('confidence', 0.0),
                    'context': context_data.get('context', {}),
                    'evidence': context_data.get('evidence', {}),
                    'evaluator': context_data.get('evaluator'),
                    'tags': context_data.get('tags', [])
                }
                
                self.measurements[measurement_id] = measurement
            
            logger.info(f"Loaded {len(self.measurements)} measurements from database")
            
            # Load intelligence profiles from database
            cursor = await self.database.connection.execute("""
                SELECT * FROM intelligence_profiles
            """)
            profile_rows = await cursor.fetchall()
            
            self.profiles = {}
            for row in profile_rows:
                try:
                    profile_data = json.loads(row['profile_data'])
                    self.profiles[row['component_name']] = profile_data
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse profile data for component: {row['component_name']}")
            
            logger.info(f"Loaded {len(self.profiles)} profiles from database")
            
            # Fallback: also try to load from JSON files for backward compatibility
            await self._load_from_json_fallback()
            
            return True
        except Exception as e:
            logger.error(f"Error loading measurements from database: {e}")
            # Fallback to JSON file loading
            return await self._load_from_json_fallback()
    
    async def _load_from_json_fallback(self) -> bool:
        """
        Fallback method to load from JSON files for backward compatibility.
        
        Returns:
            True if successful
        """
        # Define the measurements file path
        measurements_file = os.path.join(os.path.dirname(__file__), "..", "..", "data", "intelligence", "measurements.json")
        profiles_file = os.path.join(os.path.dirname(__file__), "..", "..", "data", "intelligence", "profiles.json")
        
        try:
            # Load measurements from JSON if file exists
            if os.path.exists(measurements_file):
                with open(measurements_file, "r") as f:
                    json_measurements = json.load(f)
                
                # Merge with existing measurements (database takes precedence)
                for measurement_id, measurement in json_measurements.items():
                    if measurement_id not in self.measurements:
                        self.measurements[measurement_id] = measurement
                
                logger.info(f"Loaded additional {len(json_measurements)} measurements from JSON fallback")
                
            # Load profiles from JSON if file exists  
            if os.path.exists(profiles_file):
                with open(profiles_file, "r") as f:
                    json_profiles = json.load(f)
                
                # Merge with existing profiles (database takes precedence)
                for component_id, profile in json_profiles.items():
                    if component_id not in self.profiles:
                        self.profiles[component_id] = profile
                
                logger.info(f"Loaded additional {len(json_profiles)} profiles from JSON fallback")
                
            return True
        except Exception as e:
            logger.error(f"Error loading from JSON fallback: {e}")
            # Initialize with empty state if all loading fails
            if not hasattr(self, 'measurements') or not self.measurements:
                self.measurements = {}
            if not hasattr(self, 'profiles') or not self.profiles:
                self.profiles = {}
            return False
            
    async def _save_measurements(self) -> bool:
        """
        Save measurements and profiles to storage (database).
        
        Note: This method is now mostly for backward compatibility.
        Measurements and profiles are saved directly to database in real-time.
        
        Returns:
            True if successful
        """
        # Since we're now saving to database in real-time, this method
        # is primarily for backward compatibility and JSON backup
        
        try:
            # Optional: Save JSON backup files
            measurements_file = os.path.join(os.path.dirname(__file__), "..", "..", "data", "intelligence", "measurements.json")
            profiles_file = os.path.join(os.path.dirname(__file__), "..", "..", "data", "intelligence", "profiles.json")
            
            # Create directories if they don't exist
            os.makedirs(os.path.dirname(measurements_file), exist_ok=True)
            
            # Save JSON backups
            with open(measurements_file, "w") as f:
                json.dump(self.measurements, f, indent=2)
            
            with open(profiles_file, "w") as f:
                json.dump(self.profiles, f, indent=2)
            
            logger.info(f"Saved JSON backups: {len(self.measurements)} measurements, {len(self.profiles)} profiles")
            return True
            
        except Exception as e:
            logger.warning(f"Error saving JSON backups (non-critical): {e}")
            # Return True since database is the primary storage
            return True
            
    def _create_default_dimensions(self) -> Dict[str, Dict[str, Any]]:
        """
        Create default intelligence dimensions information.
        
        Returns:
            Dictionary of intelligence dimensions
        """
        return {
            IntelligenceDimension.LANGUAGE_PROCESSING.value: {
                "name": "Language Processing",
                "description": "Ability to understand, interpret, and generate human language",
                "metrics": [
                    "ai.language.comprehension",
                    "ai.language.generation",
                    "ai.language.consistency",
                    "ai.language.coherence",
                    "ai.language.relevance"
                ]
            },
            IntelligenceDimension.REASONING.value: {
                "name": "Reasoning",
                "description": "Ability to make inferences, deduce conclusions, and process logical arguments",
                "metrics": [
                    "ai.reasoning.logical",
                    "ai.reasoning.deductive",
                    "ai.reasoning.inductive",
                    "ai.reasoning.causal",
                    "ai.reasoning.counterfactual"
                ]
            },
            IntelligenceDimension.KNOWLEDGE.value: {
                "name": "Knowledge",
                "description": "Extent of factual information and domain expertise",
                "metrics": [
                    "ai.knowledge.factual",
                    "ai.knowledge.domain",
                    "ai.knowledge.procedural",
                    "ai.knowledge.contextual",
                    "ai.knowledge.retrieval"
                ]
            },
            IntelligenceDimension.LEARNING.value: {
                "name": "Learning",
                "description": "Ability to acquire new information and adapt based on experience",
                "metrics": [
                    "ai.learning.rate",
                    "ai.learning.transfer",
                    "ai.learning.adaptation",
                    "ai.learning.improvement",
                    "ai.learning.retention"
                ]
            },
            IntelligenceDimension.CREATIVITY.value: {
                "name": "Creativity",
                "description": "Ability to generate novel, valuable, and surprising outputs",
                "metrics": [
                    "ai.creativity.novelty",
                    "ai.creativity.originality",
                    "ai.creativity.flexibility",
                    "ai.creativity.elaboration",
                    "ai.creativity.usefulness"
                ]
            },
            IntelligenceDimension.PLANNING.value: {
                "name": "Planning",
                "description": "Ability to formulate goals and develop strategies to achieve them",
                "metrics": [
                    "ai.planning.goal_setting",
                    "ai.planning.sequencing",
                    "ai.planning.resource_allocation",
                    "ai.planning.contingency",
                    "ai.planning.optimization"
                ]
            },
            IntelligenceDimension.PROBLEM_SOLVING.value: {
                "name": "Problem Solving",
                "description": "Ability to identify, analyze, and resolve challenges",
                "metrics": [
                    "ai.problem_solving.identification",
                    "ai.problem_solving.analysis",
                    "ai.problem_solving.solution_generation",
                    "ai.problem_solving.evaluation",
                    "ai.problem_solving.implementation"
                ]
            },
            IntelligenceDimension.ADAPTATION.value: {
                "name": "Adaptation",
                "description": "Ability to adjust behavior based on changing environments or requirements",
                "metrics": [
                    "ai.adaptation.environment",
                    "ai.adaptation.requirement",
                    "ai.adaptation.feedback",
                    "ai.adaptation.error",
                    "ai.adaptation.degradation"
                ]
            },
            IntelligenceDimension.COLLABORATION.value: {
                "name": "Collaboration",
                "description": "Ability to work effectively with other agents or humans",
                "metrics": [
                    "ai.collaboration.communication",
                    "ai.collaboration.coordination",
                    "ai.collaboration.information_sharing",
                    "ai.collaboration.task_division",
                    "ai.collaboration.conflict_resolution"
                ]
            },
            IntelligenceDimension.METACOGNITION.value: {
                "name": "Metacognition",
                "description": "Awareness and control of one's own thought processes",
                "metrics": [
                    "ai.metacognition.self_awareness",
                    "ai.metacognition.confidence_calibration",
                    "ai.metacognition.task_monitor",
                    "ai.metacognition.strategy_selection",
                    "ai.metacognition.error_detection"
                ]
            }
        }

# Global singleton instance
_intelligence_measurement = IntelligenceMeasurement()

async def get_intelligence_measurement() -> IntelligenceMeasurement:
    """
    Get the global intelligence measurement instance.
    
    Returns:
        IntelligenceMeasurement instance
    """
    if not _intelligence_measurement.is_initialized:
        await _intelligence_measurement.initialize()
    return _intelligence_measurement