"""
Predictive Engine Module for Apollo.

This module is responsible for analyzing context metrics history to predict
future context states, identify potential issues before they occur, and 
create prediction models to guide proactive interventions.
"""

import os
import json
import logging
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
import uuid
from collections import deque

from apollo.models.context import (
    ContextMetrics,
    ContextState,
    ContextHistoryRecord,
    ContextPrediction,
    ContextHealth
)
from apollo.core.context_observer import ContextObserver

# Configure logging
logger = logging.getLogger(__name__)


def linear_regression(x_values: List[float], y_values: List[float]) -> Tuple[float, float, float, float, float]:
    """
    Pure Python implementation of linear regression.
    
    Args:
        x_values: List of x coordinates
        y_values: List of y coordinates
        
    Returns:
        Tuple of (slope, intercept, r_value, p_value, std_err)
        Note: p_value and std_err are simplified approximations
    """
    if len(x_values) != len(y_values) or len(x_values) < 2:
        return 0.0, 0.0, 0.0, 1.0, 0.0
    
    n = len(x_values)
    
    # Calculate means
    x_mean = sum(x_values) / n
    y_mean = sum(y_values) / n
    
    # Calculate sums needed for regression
    sum_xy = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
    sum_xx = sum((x - x_mean) ** 2 for x in x_values)
    sum_yy = sum((y - y_mean) ** 2 for y in y_values)
    
    # Avoid division by zero
    if sum_xx == 0:
        return 0.0, y_mean, 0.0, 1.0, 0.0
    
    # Calculate slope and intercept
    slope = sum_xy / sum_xx
    intercept = y_mean - slope * x_mean
    
    # Calculate correlation coefficient (r_value)
    if sum_yy == 0:
        r_value = 1.0 if slope == 0 else 0.0
    else:
        r_value = sum_xy / (sum_xx * sum_yy) ** 0.5
    
    # Simplified p_value approximation (for small samples, assume high confidence)
    # In real stats, this would require t-distribution calculations
    p_value = 0.05 if abs(r_value) > 0.5 else 0.5
    
    # Simplified standard error approximation
    if n > 2:
        residual_sum_squares = sum_yy - (sum_xy ** 2 / sum_xx)
        std_err = (residual_sum_squares / ((n - 2) * sum_xx)) ** 0.5
    else:
        std_err = 0.0
        
    return slope, intercept, r_value, p_value, std_err


class PredictionRule:
    """Base class for prediction rules."""
    
    def __init__(self, name: str, description: str, weight: float = 1.0):
        """
        Initialize the prediction rule.
        
        Args:
            name: Rule name
            description: Rule description
            weight: Rule weight for combining predictions
        """
        self.name = name
        self.description = description
        self.weight = weight
    
    async def predict(
        self, 
        context_id: str, 
        current_state: ContextState,
        history: List[ContextHistoryRecord],
        horizon_seconds: float
    ) -> Optional[ContextPrediction]:
        """
        Make a prediction for a context based on current state and history.
        
        Args:
            context_id: Context identifier
            current_state: Current context state
            history: Historical context records
            horizon_seconds: Prediction horizon in seconds
            
        Returns:
            Prediction for future context state or None
        """
        raise NotImplementedError("Prediction rules must implement predict method")


class TokenUtilizationRule(PredictionRule):
    """Predicts future token utilization based on recent trends."""
    
    def __init__(self, weight: float = 1.0):
        """Initialize the token utilization rule."""
        super().__init__(
            name="token_utilization",
            description="Predicts future token utilization based on recent trends",
            weight=weight
        )
    
    async def predict(
        self, 
        context_id: str, 
        current_state: ContextState,
        history: List[ContextHistoryRecord],
        horizon_seconds: float
    ) -> Optional[ContextPrediction]:
        """Make a prediction based on token utilization trend."""
        # Need at least 3 history points for trend analysis
        if len(history) < 3:
            return None
        
        # Extract timestamps and utilization rates
        timestamps = [
            (h.timestamp - history[0].timestamp).total_seconds() 
            for h in history
        ]
        utilization_rates = [h.metrics.token_utilization for h in history]
        
        # Simple linear regression
        if len(timestamps) >= 2:
            slope, intercept, r_value, p_value, std_err = linear_regression(
                timestamps, utilization_rates
            )
            
            # Predict future utilization
            future_time = timestamps[-1] + horizon_seconds
            predicted_utilization = slope * future_time + intercept
            
            # Clamp to valid range
            predicted_utilization = max(0.0, min(1.0, predicted_utilization))
            
            # Calculate confidence based on r-squared value
            confidence = min(0.95, max(0.5, abs(r_value)))
            
            # Create predicted metrics based on current with adjusted utilization
            predicted_metrics = ContextMetrics(
                **current_state.metrics.model_dump()
            )
            predicted_metrics.token_utilization = predicted_utilization
            predicted_metrics.total_tokens = int(predicted_metrics.max_tokens * predicted_utilization)
            predicted_metrics.timestamp = current_state.metrics.timestamp + timedelta(seconds=horizon_seconds)
            
            # Estimate health based on predicted metrics
            health_score = self._estimate_health_score(predicted_metrics)
            health_status = self._determine_health_status(health_score)
            
            return ContextPrediction(
                context_id=context_id,
                predicted_metrics=predicted_metrics,
                predicted_health=health_status,
                predicted_health_score=health_score,
                confidence=confidence,
                prediction_timestamp=datetime.now(),
                prediction_horizon=horizon_seconds,
                basis="statistical"
            )
        
        return None
    
    def _estimate_health_score(self, metrics: ContextMetrics) -> float:
        """
        Estimate a health score for the context based on metrics.
        
        This is a simplified version of the context observer's calculation.
        
        Args:
            metrics: Context metrics
            
        Returns:
            Health score between 0.0 and 1.0 (higher is better)
        """
        # Base score starts at 1.0 (perfect health)
        score = 1.0
        
        # Factor 1: Token utilization (penalize high utilization)
        if metrics.token_utilization > 0.85:
            # Exponential penalty as we approach max tokens
            penalty = ((metrics.token_utilization - 0.85) / 0.15) ** 2 * 0.4
            score -= penalty
            
        # Ensure score is between 0.0 and 1.0
        return max(0.0, min(1.0, score))
    
    def _determine_health_status(self, health_score: float) -> ContextHealth:
        """
        Determine the health status category based on the health score.
        
        Args:
            health_score: Numerical health score between 0.0 and 1.0
            
        Returns:
            ContextHealth enum value
        """
        if health_score >= 0.9:
            return ContextHealth.EXCELLENT
        elif health_score >= 0.75:
            return ContextHealth.GOOD
        elif health_score >= 0.6:
            return ContextHealth.FAIR
        elif health_score >= 0.4:
            return ContextHealth.POOR
        else:
            return ContextHealth.CRITICAL


class RepetitionDetectionRule(PredictionRule):
    """Predicts future repetition based on trend analysis."""
    
    def __init__(self, weight: float = 0.8):
        """Initialize the repetition detection rule."""
        super().__init__(
            name="repetition_detection",
            description="Predicts future repetition issues based on trend analysis",
            weight=weight
        )
    
    async def predict(
        self, 
        context_id: str, 
        current_state: ContextState,
        history: List[ContextHistoryRecord],
        horizon_seconds: float
    ) -> Optional[ContextPrediction]:
        """Make a prediction based on repetition score trend."""
        # Need at least 3 history points for trend analysis
        if len(history) < 3:
            return None
        
        # Extract timestamps and repetition scores
        timestamps = [
            (h.timestamp - history[0].timestamp).total_seconds() 
            for h in history
        ]
        repetition_scores = [h.metrics.repetition_score for h in history]
        
        # Check if repetition is increasing
        if repetition_scores[-1] > 0.1 and repetition_scores[-1] > repetition_scores[0]:
            # Simple linear regression
            slope, intercept, r_value, p_value, std_err = linear_regression(
                timestamps, repetition_scores
            )
            
            # Only predict if slope is positive (repetition increasing)
            if slope > 0:
                # Predict future repetition
                future_time = timestamps[-1] + horizon_seconds
                predicted_repetition = slope * future_time + intercept
                
                # Clamp to valid range
                predicted_repetition = max(0.0, min(1.0, predicted_repetition))
                
                # Calculate confidence based on r-squared value and trend consistency
                trend_consistency = sum(1 for i in range(1, len(repetition_scores)) 
                                       if repetition_scores[i] > repetition_scores[i-1]) / (len(repetition_scores) - 1)
                confidence = min(0.9, max(0.6, abs(r_value) * trend_consistency))
                
                # Create predicted metrics based on current with adjusted repetition
                predicted_metrics = ContextMetrics(
                    **current_state.metrics.model_dump()
                )
                predicted_metrics.repetition_score = predicted_repetition
                predicted_metrics.timestamp = current_state.metrics.timestamp + timedelta(seconds=horizon_seconds)
                
                # Estimate health based on predicted metrics
                health_score = self._estimate_health_score(predicted_metrics)
                health_status = self._determine_health_status(health_score)
                
                return ContextPrediction(
                    context_id=context_id,
                    predicted_metrics=predicted_metrics,
                    predicted_health=health_status,
                    predicted_health_score=health_score,
                    confidence=confidence,
                    prediction_timestamp=datetime.now(),
                    prediction_horizon=horizon_seconds,
                    basis="statistical"
                )
        
        return None
    
    def _estimate_health_score(self, metrics: ContextMetrics) -> float:
        """
        Estimate a health score for the context based on repetition metrics.
        
        Args:
            metrics: Context metrics
            
        Returns:
            Health score between 0.0 and 1.0 (higher is better)
        """
        # Base score starts at 1.0 (perfect health)
        score = 1.0
        
        # Factor: Repetition (penalize high repetition)
        if metrics.repetition_score > 0.2:
            # Linear penalty based on repetition
            penalty = metrics.repetition_score * 0.5
            score -= penalty
            
        # Ensure score is between 0.0 and 1.0
        return max(0.0, min(1.0, score))
    
    def _determine_health_status(self, health_score: float) -> ContextHealth:
        """Determine health status from score."""
        if health_score >= 0.9:
            return ContextHealth.EXCELLENT
        elif health_score >= 0.75:
            return ContextHealth.GOOD
        elif health_score >= 0.6:
            return ContextHealth.FAIR
        elif health_score >= 0.4:
            return ContextHealth.POOR
        else:
            return ContextHealth.CRITICAL


class LatencyTrendRule(PredictionRule):
    """Predicts future performance issues based on latency trends."""
    
    def __init__(self, weight: float = 0.7):
        """Initialize the latency trend rule."""
        super().__init__(
            name="latency_trend",
            description="Predicts future performance issues based on latency trends",
            weight=weight
        )
    
    async def predict(
        self, 
        context_id: str, 
        current_state: ContextState,
        history: List[ContextHistoryRecord],
        horizon_seconds: float
    ) -> Optional[ContextPrediction]:
        """Make a prediction based on latency trend."""
        # Need at least 4 history points for this analysis
        if len(history) < 4:
            return None
        
        # Extract timestamps and latency values
        timestamps = [
            (h.timestamp - history[0].timestamp).total_seconds() 
            for h in history
        ]
        latency_values = [h.metrics.latency for h in history]
        token_rates = [h.metrics.output_token_rate for h in history if h.metrics.output_token_rate > 0]
        
        # Check if we have token rate data
        if not token_rates:
            return None
            
        # Check for significant decrease in token rate
        latest_rates = token_rates[-min(3, len(token_rates)):]
        if len(latest_rates) < 2:
            return None
            
        token_rate_trend = sum(1 for i in range(1, len(latest_rates)) 
                              if latest_rates[i] < latest_rates[i-1]) / (len(latest_rates) - 1)
        
        # If token rate is not decreasing, no prediction needed
        if token_rate_trend < 0.5:
            return None
            
        # Calculate latency trend
        latency_deltas = [latency_values[i] - latency_values[i-1] for i in range(1, len(latency_values))]
        avg_latency_delta = sum(latency_deltas) / len(latency_deltas)
        
        # Predict future latency
        predicted_latency = latency_values[-1] + (avg_latency_delta * (horizon_seconds / 5))  # Assuming 5 sec intervals
        
        # Predict future token rate (simplified)
        latest_token_rate = token_rates[-1]
        rate_of_decline = (token_rates[0] - latest_token_rate) / (timestamps[-1] - timestamps[0]) if timestamps[-1] != timestamps[0] else 0
        predicted_token_rate = max(0.1, latest_token_rate - (rate_of_decline * horizon_seconds))
        
        # Create predicted metrics
        predicted_metrics = ContextMetrics(
            **current_state.metrics.model_dump()
        )
        predicted_metrics.latency = predicted_latency
        predicted_metrics.output_token_rate = predicted_token_rate
        predicted_metrics.timestamp = current_state.metrics.timestamp + timedelta(seconds=horizon_seconds)
        
        # Calculate confidence based on consistency of trend
        confidence = min(0.85, max(0.6, token_rate_trend))
        
        # Estimate health based on predicted metrics
        health_score = self._estimate_health_score(predicted_metrics)
        health_status = self._determine_health_status(health_score)
        
        return ContextPrediction(
            context_id=context_id,
            predicted_metrics=predicted_metrics,
            predicted_health=health_status,
            predicted_health_score=health_score,
            confidence=confidence,
            prediction_timestamp=datetime.now(),
            prediction_horizon=horizon_seconds,
            basis="statistical"
        )
    
    def _estimate_health_score(self, metrics: ContextMetrics) -> float:
        """
        Estimate a health score based on latency and token rate.
        
        Args:
            metrics: Context metrics
            
        Returns:
            Health score between 0.0 and 1.0 (higher is better)
        """
        # Base score starts at 1.0 (perfect health)
        score = 1.0
        
        # Penalize high latency
        if metrics.latency > 2.0:
            penalty = min(0.3, (metrics.latency - 2.0) / 10.0)
            score -= penalty
        
        # Penalize low token rate
        if metrics.output_token_rate < 5.0 and metrics.output_token_rate > 0:
            penalty = min(0.4, (5.0 - metrics.output_token_rate) / 5.0)
            score -= penalty
            
        # Ensure score is between 0.0 and 1.0
        return max(0.0, min(1.0, score))
    
    def _determine_health_status(self, health_score: float) -> ContextHealth:
        """Determine health status from score."""
        if health_score >= 0.9:
            return ContextHealth.EXCELLENT
        elif health_score >= 0.75:
            return ContextHealth.GOOD
        elif health_score >= 0.6:
            return ContextHealth.FAIR
        elif health_score >= 0.4:
            return ContextHealth.POOR
        else:
            return ContextHealth.CRITICAL


class HeuristicRule(PredictionRule):
    """Simple heuristic-based prediction for contexts with limited history."""
    
    def __init__(self, weight: float = 0.5):
        """Initialize the heuristic rule."""
        super().__init__(
            name="heuristic",
            description="Simple heuristic-based prediction for contexts with limited history",
            weight=weight
        )
    
    async def predict(
        self, 
        context_id: str, 
        current_state: ContextState,
        history: List[ContextHistoryRecord],
        horizon_seconds: float
    ) -> Optional[ContextPrediction]:
        """Make a prediction based on current state and simple heuristics."""
        # This rule works even with limited history
        
        # Create predicted metrics as a copy of current
        predicted_metrics = ContextMetrics(
            **current_state.metrics.model_dump()
        )
        predicted_metrics.timestamp = current_state.metrics.timestamp + timedelta(seconds=horizon_seconds)
        
        # Apply heuristics based on current state
        
        # Heuristic 1: Contexts with high token utilization will likely continue to grow
        if current_state.metrics.token_utilization > 0.7:
            # Estimate growth rate (simplified)
            growth_rate = 0.002 * horizon_seconds  # 0.2% per second
            predicted_metrics.token_utilization = min(
                1.0, current_state.metrics.token_utilization + growth_rate
            )
            predicted_metrics.total_tokens = int(predicted_metrics.max_tokens * predicted_metrics.token_utilization)
        
        # Heuristic 2: Contexts with repetition issues tend to get worse
        if current_state.metrics.repetition_score > 0.15:
            # Estimate growth rate for repetition (simplified)
            rep_growth_rate = 0.001 * horizon_seconds  # 0.1% per second
            predicted_metrics.repetition_score = min(
                1.0, current_state.metrics.repetition_score + rep_growth_rate
            )
        
        # Heuristic 3: Self-reference tends to increase as contexts get larger
        if current_state.metrics.token_utilization > 0.5 and current_state.metrics.self_reference_score > 0.1:
            ref_growth_rate = 0.0005 * horizon_seconds  # 0.05% per second
            predicted_metrics.self_reference_score = min(
                1.0, current_state.metrics.self_reference_score + ref_growth_rate
            )
        
        # Heuristic 4: Coherence tends to decrease as contexts get larger and more complex
        if current_state.metrics.token_utilization > 0.6:
            coherence_decay_rate = 0.0003 * horizon_seconds  # 0.03% per second
            predicted_metrics.coherence_score = max(
                0.4, current_state.metrics.coherence_score - coherence_decay_rate
            )
        
        # Estimate health based on predicted metrics
        health_score = self._estimate_health_score(predicted_metrics)
        health_status = self._determine_health_status(health_score)
        
        # Lower confidence due to heuristic nature
        confidence = 0.7
        
        return ContextPrediction(
            context_id=context_id,
            predicted_metrics=predicted_metrics,
            predicted_health=health_status,
            predicted_health_score=health_score,
            confidence=confidence,
            prediction_timestamp=datetime.now(),
            prediction_horizon=horizon_seconds,
            basis="heuristic"
        )
    
    def _estimate_health_score(self, metrics: ContextMetrics) -> float:
        """
        Estimate a health score based on all metrics.
        
        Args:
            metrics: Context metrics
            
        Returns:
            Health score between 0.0 and 1.0 (higher is better)
        """
        # Base score starts at 1.0 (perfect health)
        score = 1.0
        
        # Factor 1: Token utilization (penalize high utilization)
        if metrics.token_utilization > 0.85:
            # Exponential penalty as we approach max tokens
            penalty = ((metrics.token_utilization - 0.85) / 0.15) ** 2 * 0.4
            score -= penalty
        
        # Factor 2: Repetition (penalize high repetition)
        if metrics.repetition_score > 0.2:
            # Linear penalty based on repetition
            penalty = metrics.repetition_score * 0.5
            score -= penalty
        
        # Factor 3: Self-reference (penalize high self-reference)
        if metrics.self_reference_score > 0.15:
            # Linear penalty based on self-reference
            penalty = metrics.self_reference_score * 0.3
            score -= penalty
        
        # Factor 4: Coherence (penalize low coherence)
        if metrics.coherence_score < 0.8:
            # Linear penalty based on lack of coherence
            penalty = (0.8 - metrics.coherence_score) * 0.4
            score -= penalty
            
        # Ensure score is between 0.0 and 1.0
        return max(0.0, min(1.0, score))
    
    def _determine_health_status(self, health_score: float) -> ContextHealth:
        """Determine health status from score."""
        if health_score >= 0.9:
            return ContextHealth.EXCELLENT
        elif health_score >= 0.75:
            return ContextHealth.GOOD
        elif health_score >= 0.6:
            return ContextHealth.FAIR
        elif health_score >= 0.4:
            return ContextHealth.POOR
        else:
            return ContextHealth.CRITICAL


class PredictiveEngine:
    """
    Predictive engine for Apollo that forecasts future context states.
    
    This class analyzes context metrics history to predict future context states,
    identify potential issues before they occur, and provide recommendations for
    proactive interventions.
    """
    
    def __init__(
        self,
        context_observer: Optional[ContextObserver] = None,
        prediction_horizon: float = 60.0,
        prediction_interval: float = 15.0,
        min_history_points: int = 3,
        prediction_limit: int = 10,
        data_dir: Optional[str] = None
    ):
        """
        Initialize the Predictive Engine.
        
        Args:
            context_observer: Observer for context metrics
            prediction_horizon: Prediction horizon in seconds (default: 60 seconds)
            prediction_interval: Interval for making predictions in seconds
            min_history_points: Minimum history points required for prediction
            prediction_limit: Maximum predictions to keep per context
            data_dir: Directory for storing prediction data
        """
        self.context_observer = context_observer
        self.prediction_horizon = prediction_horizon
        self.prediction_interval = prediction_interval
        self.min_history_points = min_history_points
        self.prediction_limit = prediction_limit
        
        # Set up data directory
        if data_dir:
            self.data_dir = data_dir
        else:
            # Use $TEKTON_DATA_DIR/apollo/prediction_data by default
            default_data_dir = os.path.join(
                os.environ.get('TEKTON_DATA_DIR', 
                              os.path.join(os.environ.get('TEKTON_ROOT', os.path.expanduser('~')), '.tekton', 'data')),
                'apollo', 'prediction_data'
            )
            self.data_dir = default_data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize prediction rules
        self.prediction_rules: List[PredictionRule] = [
            TokenUtilizationRule(weight=1.0),
            RepetitionDetectionRule(weight=0.8),
            LatencyTrendRule(weight=0.7),
            HeuristicRule(weight=0.5)
        ]
        
        # Store predictions by context
        self.predictions: Dict[str, List[ContextPrediction]] = {}
        
        # For task management
        self.prediction_task = None
        self.is_running = False
        
        # For prediction quality tracking
        self.prediction_accuracy: Dict[str, deque] = {
            rule.name: deque(maxlen=100) for rule in self.prediction_rules
        }
    
    async def start(self):
        """Start the prediction engine."""
        if self.is_running:
            logger.warning("Prediction engine is already running")
            return
            
        self.is_running = True
        
        # Start the prediction task
        self.prediction_task = asyncio.create_task(self._prediction_loop())
        
        logger.info("Prediction engine started")
    
    async def stop(self):
        """Stop the prediction engine."""
        if not self.is_running:
            logger.warning("Prediction engine is not running")
            return
            
        self.is_running = False
        
        # Cancel the prediction task
        if self.prediction_task:
            self.prediction_task.cancel()
            try:
                await self.prediction_task
            except asyncio.CancelledError:
                pass
                
        logger.info("Prediction engine stopped")
    
    async def _prediction_loop(self):
        """Main loop for making predictions periodically."""
        try:
            while self.is_running:
                await self._make_predictions()
                await self._evaluate_predictions()
                await asyncio.sleep(self.prediction_interval)
        except asyncio.CancelledError:
            logger.info("Prediction loop cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in prediction loop: {e}")
            self.is_running = False
            raise
    
    async def _make_predictions(self):
        """Make predictions for all active contexts."""
        if not self.context_observer:
            logger.warning("No context observer available for predictions")
            return
            
        try:
            # Get all active contexts
            active_contexts = self.context_observer.get_all_context_states()
            
            for context in active_contexts:
                context_id = context.context_id
                
                # Get history for this context
                history = self.context_observer.get_context_history(context_id)
                
                # Skip if not enough history
                if len(history) < self.min_history_points:
                    continue
                    
                # Apply each prediction rule
                rule_predictions: List[ContextPrediction] = []
                
                for rule in self.prediction_rules:
                    try:
                        prediction = await rule.predict(
                            context_id,
                            context,
                            history,
                            self.prediction_horizon
                        )
                        
                        if prediction:
                            rule_predictions.append(prediction)
                    except Exception as e:
                        logger.error(f"Error applying prediction rule {rule.name}: {e}")
                
                # If no predictions were made, skip
                if not rule_predictions:
                    continue
                    
                # Combine predictions
                combined_prediction = await self._combine_predictions(rule_predictions)
                
                # Store the prediction
                if context_id not in self.predictions:
                    self.predictions[context_id] = []
                    
                self.predictions[context_id].append(combined_prediction)
                
                # Limit number of predictions per context
                if len(self.predictions[context_id]) > self.prediction_limit:
                    self.predictions[context_id] = self.predictions[context_id][-self.prediction_limit:]
        
        except Exception as e:
            logger.error(f"Error making predictions: {e}")
    
    async def _combine_predictions(self, predictions: List[ContextPrediction]) -> ContextPrediction:
        """
        Combine multiple predictions into a single consensus prediction.
        
        Args:
            predictions: List of predictions to combine
            
        Returns:
            Combined prediction
        """
        if not predictions:
            raise ValueError("No predictions to combine")
            
        # If only one prediction, return it
        if len(predictions) == 1:
            return predictions[0]
            
        # Get the context ID (should be the same for all)
        context_id = predictions[0].context_id
        
        # Get total weight
        total_weight = 0.0
        for pred in predictions:
            rule = next((r for r in self.prediction_rules if r.name == pred.basis), None)
            weight = rule.weight if rule else 1.0
            total_weight += weight * pred.confidence
            
        if total_weight == 0:
            # Fallback to equal weights
            total_weight = len(predictions)
            weights = [1.0 for _ in predictions]
        else:
            # Calculate normalized weights
            weights = []
            for p in predictions:
                rule = next((r for r in self.prediction_rules if r.name == p.basis), None)
                if rule and rule.weight is not None:
                    weight = (rule.weight * p.confidence) / total_weight
                else:
                    # Default weight if rule not found or weight is None
                    weight = p.confidence / total_weight
                weights.append(weight)
        
        # Combine metrics
        combined_metrics = ContextMetrics(
            # Use weighted average for most metrics
            input_tokens=int(sum(p.predicted_metrics.input_tokens * w for p, w in zip(predictions, weights))),
            output_tokens=int(sum(p.predicted_metrics.output_tokens * w for p, w in zip(predictions, weights))),
            total_tokens=int(sum(p.predicted_metrics.total_tokens * w for p, w in zip(predictions, weights))),
            max_tokens=predictions[0].predicted_metrics.max_tokens,  # This should be the same for all
            token_utilization=sum(p.predicted_metrics.token_utilization * w for p, w in zip(predictions, weights)),
            input_token_rate=sum(p.predicted_metrics.input_token_rate * w for p, w in zip(predictions, weights)),
            output_token_rate=sum(p.predicted_metrics.output_token_rate * w for p, w in zip(predictions, weights)),
            token_rate_change=sum(p.predicted_metrics.token_rate_change * w for p, w in zip(predictions, weights)),
            repetition_score=sum(p.predicted_metrics.repetition_score * w for p, w in zip(predictions, weights)),
            self_reference_score=sum(p.predicted_metrics.self_reference_score * w for p, w in zip(predictions, weights)),
            coherence_score=sum(p.predicted_metrics.coherence_score * w for p, w in zip(predictions, weights)),
            latency=sum(p.predicted_metrics.latency * w for p, w in zip(predictions, weights)),
            processing_time=sum(p.predicted_metrics.processing_time * w for p, w in zip(predictions, weights)),
            timestamp=predictions[0].predicted_metrics.timestamp  # Use timestamp from first prediction
        )
        
        # Combine health scores
        combined_health_score = sum(p.predicted_health_score * w for p, w in zip(predictions, weights))
        
        # Determine health status from combined score
        combined_health = self._determine_health_status(combined_health_score)
        
        # Average confidence (weighted by rule weight)
        combined_confidence = min(
            0.95,
            sum(p.confidence * w for p, w in zip(predictions, weights))
        )
        
        # Create combined prediction
        return ContextPrediction(
            context_id=context_id,
            predicted_metrics=combined_metrics,
            predicted_health=combined_health,
            predicted_health_score=combined_health_score,
            confidence=combined_confidence,
            prediction_timestamp=datetime.now(),
            prediction_horizon=predictions[0].prediction_horizon,
            basis="hybrid"
        )
    
    def _determine_health_status(self, health_score: float) -> ContextHealth:
        """
        Determine the health status category based on the health score.
        
        Args:
            health_score: Numerical health score between 0.0 and 1.0
            
        Returns:
            ContextHealth enum value
        """
        if health_score >= 0.9:
            return ContextHealth.EXCELLENT
        elif health_score >= 0.75:
            return ContextHealth.GOOD
        elif health_score >= 0.6:
            return ContextHealth.FAIR
        elif health_score >= 0.4:
            return ContextHealth.POOR
        else:
            return ContextHealth.CRITICAL
    
    async def _evaluate_predictions(self):
        """Evaluate the accuracy of past predictions against current reality."""
        if not self.context_observer:
            return
            
        try:
            # Get current time
            now = datetime.now()
            
            # Check for predictions that should have come true by now
            for context_id, context_predictions in list(self.predictions.items()):
                # Get current state
                current_state = self.context_observer.get_context_state(context_id)
                
                # If context no longer exists, remove predictions
                if not current_state:
                    del self.predictions[context_id]
                    continue
                    
                # Evaluate mature predictions
                for pred in context_predictions[:]:
                    # Calculate age of prediction
                    pred_age = (now - pred.prediction_timestamp).total_seconds()
                    
                    # If prediction has matured (reached its horizon)
                    if pred_age >= pred.prediction_horizon:
                        # Compare prediction with current reality
                        self._compare_prediction_with_reality(pred, current_state)
                        
                        # Remove this prediction
                        context_predictions.remove(pred)
        
        except Exception as e:
            logger.error(f"Error evaluating predictions: {e}")
    
    def _compare_prediction_with_reality(self, prediction: ContextPrediction, current_state: ContextState):
        """
        Compare a prediction with current reality to evaluate accuracy.
        
        Args:
            prediction: The prediction to evaluate
            current_state: Current context state
        """
        try:
            # Calculate error in key metrics
            token_utilization_error = abs(prediction.predicted_metrics.token_utilization - current_state.metrics.token_utilization)
            repetition_error = abs(prediction.predicted_metrics.repetition_score - current_state.metrics.repetition_score)
            health_score_error = abs(prediction.predicted_health_score - current_state.health_score)
            
            # Calculate overall accuracy (inverse of weighted error)
            total_error = (token_utilization_error * 0.4) + (repetition_error * 0.3) + (health_score_error * 0.3)
            accuracy = max(0.0, 1.0 - total_error)
            
            # Record accuracy for the prediction basis
            if prediction.basis in self.prediction_accuracy:
                self.prediction_accuracy[prediction.basis].append(accuracy)
            
            # Log evaluation
            if accuracy < 0.7:
                logger.warning(f"Low prediction accuracy ({accuracy:.2f}) for {prediction.basis} prediction on context {prediction.context_id}")
            else:
                logger.debug(f"Prediction accuracy: {accuracy:.2f} for {prediction.basis} prediction on context {prediction.context_id}")
                
        except Exception as e:
            logger.error(f"Error comparing prediction with reality: {e}")
    
    def get_prediction(self, context_id: str) -> Optional[ContextPrediction]:
        """
        Get the latest prediction for a specific context.
        
        Args:
            context_id: Context identifier
            
        Returns:
            Latest prediction or None if no predictions exist
        """
        if context_id not in self.predictions or not self.predictions[context_id]:
            return None
            
        return self.predictions[context_id][-1]
    
    def get_all_predictions(self) -> Dict[str, ContextPrediction]:
        """
        Get the latest prediction for all contexts.
        
        Returns:
            Dictionary mapping context IDs to their latest predictions
        """
        return {
            context_id: predictions[-1]
            for context_id, predictions in self.predictions.items()
            if predictions
        }
    
    def get_prediction_accuracy(self) -> Dict[str, float]:
        """
        Get average prediction accuracy for each rule.
        
        Returns:
            Dictionary mapping rule names to their average accuracy
        """
        return {
            rule: sum(accuracies) / len(accuracies) if accuracies else 0.0
            for rule, accuracies in self.prediction_accuracy.items()
        }
    
    def get_predictions_by_health(self, health: ContextHealth) -> List[ContextPrediction]:
        """
        Get all predictions with a specific predicted health status.
        
        Args:
            health: Health status to filter by
            
        Returns:
            List of predictions with the specified health status
        """
        result = []
        
        for predictions in self.predictions.values():
            if not predictions:
                continue
                
            latest = predictions[-1]
            if latest.predicted_health == health:
                result.append(latest)
                
        return result
    
    def get_critical_predictions(self) -> List[ContextPrediction]:
        """
        Get predictions that indicate critical future issues.
        
        Returns:
            List of predictions with critical health status
        """
        return self.get_predictions_by_health(ContextHealth.CRITICAL)