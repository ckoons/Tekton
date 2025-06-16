"""
Pattern Detection Engine for Sophia

This module provides advanced pattern detection capabilities for metrics, 
behaviors, and intelligence characteristics across the Tekton ecosystem.
"""

import os
import json
import math
import asyncio
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple, Set
from datetime import datetime, timedelta
from enum import Enum

# Import other engines
from .metrics_engine import get_metrics_engine
from .analysis_engine import get_analysis_engine

logger = logging.getLogger("sophia.pattern_detection")

class PatternType(str, Enum):
    """Pattern types enumeration."""
    TREND = "trend"
    SEASONAL = "seasonal"
    CYCLIC = "cyclic"
    OUTLIER = "outlier"
    THRESHOLD = "threshold"
    CORRELATION = "correlation"
    SEQUENCE = "sequence"
    CLUSTER = "cluster"
    ANOMALY = "anomaly"
    STEADY_STATE = "steady_state"

class PatternConfidence(str, Enum):
    """Pattern confidence levels."""
    VERY_HIGH = "very_high"  # >90% confidence
    HIGH = "high"            # 75-90% confidence
    MEDIUM = "medium"        # 50-75% confidence
    LOW = "low"              # 25-50% confidence
    VERY_LOW = "very_low"    # <25% confidence

class PatternDirection(str, Enum):
    """Pattern direction enumeration."""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    OSCILLATING = "oscillating"
    UNKNOWN = "unknown"

class PatternEngine:
    """
    Core pattern detection engine for identifying and analyzing patterns
    in metrics, behavior, and intelligence characteristics.
    
    Provides various detection algorithms and analysis methods to identify
    meaningful patterns across the Tekton ecosystem.
    """
    
    def __init__(self):
        """Initialize the pattern detection engine."""
        self.is_initialized = False
        self.metrics_engine = None
        self.analysis_engine = None
        self.detection_tasks = {}
        self.pattern_cache = {}
        self.cache_expiry = {}
        
    async def initialize(self) -> bool:
        """
        Initialize the pattern detection engine.
        
        Returns:
            True if initialization was successful
        """
        logger.info("Initializing Sophia Pattern Detection Engine...")
        
        # Get required engines
        self.metrics_engine = await get_metrics_engine()
        self.analysis_engine = await get_analysis_engine()
        
        self.is_initialized = True
        logger.info("Sophia Pattern Detection Engine initialized successfully")
        return True
        
    async def start(self) -> bool:
        """
        Start the pattern detection engine and background tasks.
        
        Returns:
            True if successful
        """
        if not self.is_initialized:
            success = await self.initialize()
            if not success:
                logger.error("Failed to initialize Pattern Detection Engine")
                return False
                
        logger.info("Starting Sophia Pattern Detection Engine...")
        
        # Start periodic pattern detection tasks
        self.detection_tasks["persistent_patterns"] = asyncio.create_task(
            self._detect_persistent_patterns()
        )
        
        logger.info("Sophia Pattern Detection Engine started successfully")
        return True
        
    async def stop(self) -> bool:
        """
        Stop the pattern detection engine and clean up resources.
        
        Returns:
            True if successful
        """
        logger.info("Stopping Sophia Pattern Detection Engine...")
        
        # Cancel background tasks
        for task_name, task in self.detection_tasks.items():
            logger.info(f"Cancelling task: {task_name}")
            task.cancel()
            
        self.detection_tasks = {}
        
        logger.info("Sophia Pattern Detection Engine stopped successfully")
        return True
        
    async def detect_patterns(
        self,
        metric_id: str,
        time_window: str = "24h",
        source: Optional[str] = None,
        tags: Optional[List[str]] = None,
        pattern_types: Optional[List[Union[PatternType, str]]] = None,
        min_confidence: Union[PatternConfidence, str] = PatternConfidence.MEDIUM
    ) -> Dict[str, Any]:
        """
        Detect patterns in a specific metric.
        
        Args:
            metric_id: The metric ID to analyze
            time_window: Time window for analysis (e.g., "24h", "7d")
            source: Filter by source
            tags: Filter by tags
            pattern_types: Types of patterns to detect (defaults to all)
            min_confidence: Minimum confidence level for reported patterns
            
        Returns:
            Pattern detection results
        """
        # Convert enum values to strings if needed
        pattern_types_str = [
            p.value if isinstance(p, PatternType) else p
            for p in (pattern_types or list(PatternType))
        ]
        min_confidence_str = min_confidence.value if isinstance(min_confidence, PatternConfidence) else min_confidence
        
        # Create cache key
        cache_key = f"pattern:{metric_id}:{time_window}:{source}:{tags}:{','.join(pattern_types_str)}:{min_confidence_str}"
        
        # Check cache
        if cache_key in self.pattern_cache and cache_key in self.cache_expiry:
            if datetime.utcnow() < self.cache_expiry[cache_key]:
                return self.pattern_cache[cache_key]
        
        # Fetch metric data
        try:
            # Calculate time range
            end_time = datetime.utcnow()
            if time_window.endswith("h"):
                start_time = end_time - timedelta(hours=int(time_window[:-1]))
            elif time_window.endswith("d"):
                start_time = end_time - timedelta(days=int(time_window[:-1]))
            elif time_window.endswith("w"):
                start_time = end_time - timedelta(weeks=int(time_window[:-1]))
            else:
                # Default to hours
                start_time = end_time - timedelta(hours=int(time_window))
                
            # Format times for query
            start_str = start_time.isoformat() + "Z"
            end_str = end_time.isoformat() + "Z"
            
            # Get metric data with appropriate interval
            hours_diff = (end_time - start_time).total_seconds() / 3600
            if hours_diff < 6:
                interval = "15m"  # 15-minute intervals for short windows
            elif hours_diff < 24:
                interval = "1h"  # 1-hour intervals for medium windows
            elif hours_diff < 168:  # 7 days
                interval = "4h"  # 4-hour intervals for week-long windows
            else:
                interval = "1d"  # Daily intervals for longer windows
                
            # Get aggregated data
            aggregated = await self.metrics_engine.aggregate_metrics(
                metric_id=metric_id,
                aggregation="avg",
                interval=interval,
                source=source,
                tags=tags,
                start_time=start_str,
                end_time=end_str
            )
            
            # Extract values and timestamps
            values = []
            timestamps = []
            
            if "time_series" in aggregated:
                for point in aggregated["time_series"]:
                    if point["value"] is not None:
                        values.append(point["value"])
                        timestamps.append(point["start_time"])
                        
            # Check if we have enough data
            if len(values) < 3:
                result = {
                    "metric_id": metric_id,
                    "time_window": time_window,
                    "analysis_time": datetime.utcnow().isoformat() + "Z",
                    "patterns_detected": [],
                    "has_patterns": False,
                    "message": "Insufficient data for pattern detection"
                }
                
                self.pattern_cache[cache_key] = result
                self.cache_expiry[cache_key] = datetime.utcnow() + timedelta(minutes=30)
                return result
                
            # Detect patterns based on requested types
            detected_patterns = []
            
            # Trend pattern detection
            if PatternType.TREND.value in pattern_types_str:
                trend_pattern = await self._detect_trend_pattern(values, timestamps)
                if self._meets_confidence_threshold(trend_pattern, min_confidence_str):
                    detected_patterns.append(trend_pattern)
                    
            # Seasonal pattern detection
            if PatternType.SEASONAL.value in pattern_types_str and len(values) >= 12:
                seasonal_pattern = await self._detect_seasonal_pattern(values, timestamps)
                if seasonal_pattern and self._meets_confidence_threshold(seasonal_pattern, min_confidence_str):
                    detected_patterns.append(seasonal_pattern)
                    
            # Cyclic pattern detection
            if PatternType.CYCLIC.value in pattern_types_str and len(values) >= 12:
                cyclic_pattern = await self._detect_cyclic_pattern(values, timestamps)
                if cyclic_pattern and self._meets_confidence_threshold(cyclic_pattern, min_confidence_str):
                    detected_patterns.append(cyclic_pattern)
                    
            # Outlier pattern detection
            if PatternType.OUTLIER.value in pattern_types_str:
                outlier_pattern = await self._detect_outliers(values, timestamps)
                if outlier_pattern and self._meets_confidence_threshold(outlier_pattern, min_confidence_str):
                    detected_patterns.append(outlier_pattern)
                    
            # Threshold pattern detection
            if PatternType.THRESHOLD.value in pattern_types_str:
                threshold_pattern = await self._detect_threshold_breaches(values, timestamps, metric_id)
                if threshold_pattern and self._meets_confidence_threshold(threshold_pattern, min_confidence_str):
                    detected_patterns.append(threshold_pattern)
                    
            # Steady state pattern detection
            if PatternType.STEADY_STATE.value in pattern_types_str:
                steady_pattern = await self._detect_steady_state(values, timestamps)
                if steady_pattern and self._meets_confidence_threshold(steady_pattern, min_confidence_str):
                    detected_patterns.append(steady_pattern)
                    
            # Compile detection results
            result = {
                "metric_id": metric_id,
                "time_window": time_window,
                "analysis_time": datetime.utcnow().isoformat() + "Z",
                "data_points": len(values),
                "patterns_detected": detected_patterns,
                "has_patterns": len(detected_patterns) > 0,
                "dominant_pattern": self._determine_dominant_pattern(detected_patterns) if detected_patterns else None
            }
            
            # Cache results
            self.pattern_cache[cache_key] = result
            self.cache_expiry[cache_key] = datetime.utcnow() + timedelta(hours=2)
            
            return result
            
        except Exception as e:
            logger.error(f"Error detecting patterns for metric {metric_id}: {e}")
            return {
                "metric_id": metric_id,
                "time_window": time_window,
                "analysis_time": datetime.utcnow().isoformat() + "Z",
                "error": str(e),
                "patterns_detected": [],
                "has_patterns": False
            }
            
    async def detect_correlated_patterns(
        self,
        metric_ids: List[str],
        time_window: str = "24h",
        source: Optional[str] = None,
        min_correlation: float = 0.7
    ) -> Dict[str, Any]:
        """
        Detect correlated patterns across multiple metrics.
        
        Args:
            metric_ids: List of metric IDs to analyze
            time_window: Time window for analysis
            source: Filter by source
            min_correlation: Minimum correlation threshold
            
        Returns:
            Correlation pattern detection results
        """
        if len(metric_ids) < 2:
            return {
                "error": "At least 2 metrics are required for correlation pattern detection",
                "metric_ids": metric_ids
            }
            
        # Create cache key
        metrics_key = ",".join(sorted(metric_ids))
        cache_key = f"correlation_pattern:{metrics_key}:{time_window}:{source}:{min_correlation}"
        
        # Check cache
        if cache_key in self.pattern_cache and cache_key in self.cache_expiry:
            if datetime.utcnow() < self.cache_expiry[cache_key]:
                return self.pattern_cache[cache_key]
                
        try:
            # First, get correlation analysis from analysis engine
            correlation_analysis = await self.analysis_engine.analyze_multi_metric_correlations(
                metric_ids=metric_ids,
                time_window=time_window,
                source=source
            )
            
            # Extract strong correlations
            strong_correlations = correlation_analysis.get("strong_correlations", [])
            
            # Filter by minimum correlation threshold
            strong_correlations = [
                corr for corr in strong_correlations
                if abs(corr["correlation"]) >= min_correlation
            ]
            
            # Detect patterns in each correlated metric
            metric_patterns = {}
            for metric_id in metric_ids:
                patterns = await self.detect_patterns(
                    metric_id=metric_id,
                    time_window=time_window,
                    source=source
                )
                metric_patterns[metric_id] = patterns
                
            # Find common patterns across correlated metrics
            common_patterns = await self._find_common_patterns(
                metric_patterns, strong_correlations
            )
            
            # Compile results
            result = {
                "metric_ids": metric_ids,
                "time_window": time_window,
                "analysis_time": datetime.utcnow().isoformat() + "Z",
                "correlations": strong_correlations,
                "metric_patterns": metric_patterns,
                "common_patterns": common_patterns,
                "has_correlated_patterns": len(common_patterns) > 0
            }
            
            # Cache results
            self.pattern_cache[cache_key] = result
            self.cache_expiry[cache_key] = datetime.utcnow() + timedelta(hours=4)
            
            return result
            
        except Exception as e:
            logger.error(f"Error detecting correlated patterns: {e}")
            return {
                "metric_ids": metric_ids,
                "time_window": time_window,
                "analysis_time": datetime.utcnow().isoformat() + "Z",
                "error": str(e),
                "correlations": [],
                "common_patterns": [],
                "has_correlated_patterns": False
            }
            
    async def detect_sequence_patterns(
        self,
        event_series: List[Dict[str, Any]],
        max_sequence_length: int = 5,
        min_support: float = 0.1,
        time_field: str = "timestamp",
        event_field: str = "event"
    ) -> Dict[str, Any]:
        """
        Detect sequential patterns in a series of events.
        
        Args:
            event_series: List of event dictionaries
            max_sequence_length: Maximum sequence length to detect
            min_support: Minimum support (frequency) threshold
            time_field: Field containing timestamp
            event_field: Field containing event name/type
            
        Returns:
            Sequence pattern detection results
        """
        if not event_series or len(event_series) < 3:
            return {
                "sequences_detected": [],
                "has_patterns": False,
                "message": "Insufficient events for sequence detection"
            }
            
        try:
            # Sort events by timestamp
            sorted_events = sorted(event_series, key=lambda x: x.get(time_field, ""))
            
            # Extract event sequence
            event_sequence = [event.get(event_field, "unknown") for event in sorted_events]
            
            # Generate candidate sequences
            sequences = {}
            for length in range(2, min(max_sequence_length + 1, len(event_sequence))):
                for i in range(len(event_sequence) - length + 1):
                    sequence = tuple(event_sequence[i:i+length])
                    if sequence in sequences:
                        sequences[sequence] += 1
                    else:
                        sequences[sequence] = 1
            
            # Filter by minimum support
            min_count = len(event_sequence) * min_support
            frequent_sequences = {
                seq: count for seq, count in sequences.items()
                if count >= min_count
            }
            
            # Sort by frequency
            sorted_sequences = sorted(
                frequent_sequences.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Format detected sequences
            detected_sequences = []
            for sequence, count in sorted_sequences:
                support = count / len(event_sequence)
                confidence = self._calculate_sequence_confidence(
                    sequence, event_sequence
                )
                
                detected_sequences.append({
                    "sequence": list(sequence),
                    "length": len(sequence),
                    "count": count,
                    "support": support,
                    "confidence": confidence,
                    "confidence_level": self._confidence_to_level(confidence)
                })
                
            # Compile results
            result = {
                "analysis_time": datetime.utcnow().isoformat() + "Z",
                "total_events": len(event_sequence),
                "unique_events": len(set(event_sequence)),
                "sequences_detected": detected_sequences,
                "has_patterns": len(detected_sequences) > 0
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error detecting sequence patterns: {e}")
            return {
                "analysis_time": datetime.utcnow().isoformat() + "Z",
                "error": str(e),
                "sequences_detected": [],
                "has_patterns": False
            }
            
    async def detect_component_behavior_patterns(
        self,
        component_id: str,
        time_window: str = "7d"
    ) -> Dict[str, Any]:
        """
        Detect patterns in component behavior.
        
        Args:
            component_id: ID of the component
            time_window: Time window for analysis
            
        Returns:
            Component behavior pattern detection results
        """
        # Create cache key
        cache_key = f"component_pattern:{component_id}:{time_window}"
        
        # Check cache
        if cache_key in self.pattern_cache and cache_key in self.cache_expiry:
            if datetime.utcnow() < self.cache_expiry[cache_key]:
                return self.pattern_cache[cache_key]
                
        try:
            # Get component analysis from analysis engine
            component_analysis = await self.analysis_engine.analyze_component_performance(
                component_id=component_id,
                time_window=time_window
            )
            
            # Check which metrics are available
            key_metrics = component_analysis.get("metrics_analyzed", [])
            
            # Detect patterns for each metric
            metric_patterns = {}
            for metric_id in key_metrics:
                patterns = await self.detect_patterns(
                    metric_id=metric_id,
                    time_window=time_window,
                    source=component_id
                )
                metric_patterns[metric_id] = patterns
                
            # Analyze behavioral characteristics
            behavior_patterns = await self._analyze_behavior_patterns(
                component_id, metric_patterns, component_analysis
            )
            
            # Compile results
            result = {
                "component_id": component_id,
                "time_window": time_window,
                "analysis_time": datetime.utcnow().isoformat() + "Z",
                "metric_patterns": metric_patterns,
                "behavior_patterns": behavior_patterns,
                "has_patterns": any(patterns.get("has_patterns", False) for patterns in metric_patterns.values()) or len(behavior_patterns) > 0
            }
            
            # Cache results
            self.pattern_cache[cache_key] = result
            self.cache_expiry[cache_key] = datetime.utcnow() + timedelta(hours=6)
            
            return result
            
        except Exception as e:
            logger.error(f"Error detecting component behavior patterns for {component_id}: {e}")
            return {
                "component_id": component_id,
                "time_window": time_window,
                "analysis_time": datetime.utcnow().isoformat() + "Z",
                "error": str(e),
                "metric_patterns": {},
                "behavior_patterns": [],
                "has_patterns": False
            }
            
    async def _detect_trend_pattern(
        self,
        values: List[float],
        timestamps: List[str]
    ) -> Dict[str, Any]:
        """
        Detect trend patterns in time series data.
        
        Args:
            values: List of metric values
            timestamps: List of timestamps
            
        Returns:
            Trend pattern information
        """
        if not values or len(values) < 3:
            return None
            
        # Calculate linear regression
        n = len(values)
        x = list(range(n))
        
        # Calculate means
        mean_x = sum(x) / n
        mean_y = sum(values) / n
        
        # Calculate slope and intercept
        numerator = sum((x[i] - mean_x) * (values[i] - mean_y) for i in range(n))
        denominator = sum((x[i] - mean_x) ** 2 for i in range(n))
        
        if denominator == 0:
            return None
            
        slope = numerator / denominator
        intercept = mean_y - slope * mean_x
        
        # Calculate correlation coefficient (r-value)
        ss_xx = sum((x[i] - mean_x) ** 2 for i in range(n))
        ss_yy = sum((values[i] - mean_y) ** 2 for i in range(n))
        ss_xy = sum((x[i] - mean_x) * (values[i] - mean_y) for i in range(n))
        
        if ss_xx == 0 or ss_yy == 0:
            return None
            
        r_value = ss_xy / (math.sqrt(ss_xx * ss_yy))
        r_squared = r_value ** 2
        
        # Determine trend direction
        if abs(slope) < 0.00001:
            direction = PatternDirection.STABLE.value
        elif slope > 0:
            direction = PatternDirection.INCREASING.value
        else:
            direction = PatternDirection.DECREASING.value
            
        # Calculate trend strength and confidence
        trend_strength = abs(r_value)
        confidence = self._calculate_confidence(trend_strength)
        
        # Calculate percentage change
        if values[0] != 0:
            percent_change = ((values[-1] - values[0]) / abs(values[0])) * 100
        else:
            percent_change = 0
            
        # Create pattern if strength meets threshold
        if trend_strength >= 0.3:  # Minimum threshold for trend
            return {
                "type": PatternType.TREND.value,
                "direction": direction,
                "strength": trend_strength,
                "confidence": confidence,
                "confidence_level": self._confidence_to_level(confidence),
                "slope": slope,
                "r_squared": r_squared,
                "percent_change": percent_change,
                "description": f"{direction.capitalize()} trend with {self._confidence_to_level(confidence)} confidence",
                "start_value": values[0],
                "end_value": values[-1]
            }
            
        return None
        
    async def _detect_seasonal_pattern(
        self,
        values: List[float],
        timestamps: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Detect seasonal patterns in time series data.
        
        Args:
            values: List of metric values
            timestamps: List of timestamps
            
        Returns:
            Seasonal pattern information or None if not detected
        """
        if len(values) < 12:  # Need sufficient data points
            return None
            
        # Check common seasonality periods
        best_period = None
        best_autocorr = 0
        
        for period in [2, 3, 4, 6, 7, 12, 24]:
            if len(values) < period * 2:  # Need at least 2 full periods
                continue
                
            # Calculate autocorrelation at this lag
            autocorr = self._autocorrelation(values, period)
            
            if autocorr > 0.5 and autocorr > best_autocorr:  # Minimum threshold
                best_period = period
                best_autocorr = autocorr
                
        if not best_period:
            return None
            
        # Calculate confidence
        confidence = self._calculate_confidence(best_autocorr)
        
        return {
            "type": PatternType.SEASONAL.value,
            "period": best_period,
            "strength": best_autocorr,
            "confidence": confidence,
            "confidence_level": self._confidence_to_level(confidence),
            "description": f"Seasonal pattern with period {best_period} and {self._confidence_to_level(confidence)} confidence"
        }
        
    async def _detect_cyclic_pattern(
        self,
        values: List[float],
        timestamps: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Detect cyclic patterns in time series data.
        
        Args:
            values: List of metric values
            timestamps: List of timestamps
            
        Returns:
            Cyclic pattern information or None if not detected
        """
        if len(values) < 12:  # Need sufficient data points
            return None
            
        # Calculate autocorrelations for various lags
        autocorrs = []
        max_lag = min(len(values) // 3, 30)  # Up to 1/3 of series length or max 30
        
        for lag in range(1, max_lag + 1):
            autocorr = self._autocorrelation(values, lag)
            autocorrs.append((lag, autocorr))
            
        # Find peaks in autocorrelation
        peaks = []
        for i in range(1, len(autocorrs) - 1):
            if (autocorrs[i][1] > autocorrs[i-1][1] and 
                autocorrs[i][1] > autocorrs[i+1][1] and 
                autocorrs[i][1] > 0.3):  # Minimum peak height
                peaks.append(autocorrs[i])
                
        if not peaks:
            return None
            
        # Sort by strength
        peaks.sort(key=lambda x: x[1], reverse=True)
        
        # Best cycle is the strongest peak
        best_cycle = peaks[0][0]
        cycle_strength = peaks[0][1]
        
        # Calculate confidence
        confidence = self._calculate_confidence(cycle_strength)
        
        return {
            "type": PatternType.CYCLIC.value,
            "period": best_cycle,
            "strength": cycle_strength,
            "confidence": confidence,
            "confidence_level": self._confidence_to_level(confidence),
            "additional_cycles": [p[0] for p in peaks[1:3]] if len(peaks) > 1 else [],
            "description": f"Cyclic pattern with period {best_cycle} and {self._confidence_to_level(confidence)} confidence"
        }
        
    async def _detect_outliers(
        self,
        values: List[float],
        timestamps: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Detect outliers in time series data.
        
        Args:
            values: List of metric values
            timestamps: List of timestamps
            
        Returns:
            Outlier pattern information or None if not detected
        """
        if len(values) < 3:
            return None
            
        # Calculate mean and standard deviation
        mean = sum(values) / len(values)
        std_dev = math.sqrt(sum((x - mean) ** 2 for x in values) / len(values))
        
        # Define outlier threshold (3 standard deviations)
        threshold = 3.0
        
        # Find outliers
        outliers = []
        for i, value in enumerate(values):
            z_score = (value - mean) / std_dev if std_dev > 0 else 0
            if abs(z_score) > threshold:
                outliers.append({
                    "index": i,
                    "timestamp": timestamps[i],
                    "value": value,
                    "z_score": z_score,
                    "deviation": (value - mean) / std_dev if std_dev > 0 else 0
                })
                
        # Only report if we have outliers
        if not outliers:
            return None
            
        # Calculate confidence based on outlier strength
        if len(outliers) > 0:
            avg_z_score = sum(abs(o["z_score"]) for o in outliers) / len(outliers)
            confidence = min(1.0, avg_z_score / 5.0)  # Scale confidence (max at z=5)
        else:
            confidence = 0.0
            
        return {
            "type": PatternType.OUTLIER.value,
            "outlier_count": len(outliers),
            "outlier_percentage": (len(outliers) / len(values)) * 100,
            "outliers": outliers,
            "confidence": confidence,
            "confidence_level": self._confidence_to_level(confidence),
            "description": f"Detected {len(outliers)} outliers with {self._confidence_to_level(confidence)} confidence"
        }
        
    async def _detect_threshold_breaches(
        self,
        values: List[float],
        timestamps: List[str],
        metric_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Detect threshold breaches in time series data.
        
        Args:
            values: List of metric values
            timestamps: List of timestamps
            metric_id: Metric ID for determining thresholds
            
        Returns:
            Threshold pattern information or None if not detected
        """
        if len(values) < 3:
            return None
            
        # Define thresholds based on metric type
        thresholds = await self._get_metric_thresholds(metric_id)
        
        if not thresholds:
            return None
            
        # Find threshold breaches
        breaches = []
        for i, value in enumerate(values):
            for threshold_name, threshold_value in thresholds.items():
                if "upper" in threshold_name and value > threshold_value:
                    breaches.append({
                        "index": i,
                        "timestamp": timestamps[i],
                        "value": value,
                        "threshold": threshold_value,
                        "threshold_name": threshold_name,
                        "type": "upper_breach",
                        "severity": "high" if "critical" in threshold_name else "medium"
                    })
                elif "lower" in threshold_name and value < threshold_value:
                    breaches.append({
                        "index": i,
                        "timestamp": timestamps[i],
                        "value": value,
                        "threshold": threshold_value,
                        "threshold_name": threshold_name,
                        "type": "lower_breach",
                        "severity": "high" if "critical" in threshold_name else "medium"
                    })
                    
        # Only report if we have breaches
        if not breaches:
            return None
            
        # Calculate confidence based on breach severity and count
        high_severity_count = sum(1 for b in breaches if b["severity"] == "high")
        confidence = min(1.0, ((high_severity_count * 0.2) + (len(breaches) * 0.05)))
        
        return {
            "type": PatternType.THRESHOLD.value,
            "breach_count": len(breaches),
            "breach_percentage": (len(breaches) / len(values)) * 100,
            "breaches": breaches,
            "thresholds": thresholds,
            "high_severity_count": high_severity_count,
            "confidence": confidence,
            "confidence_level": self._confidence_to_level(confidence),
            "description": f"Detected {len(breaches)} threshold breaches with {self._confidence_to_level(confidence)} confidence"
        }
        
    async def _detect_steady_state(
        self,
        values: List[float],
        timestamps: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Detect steady state in time series data.
        
        Args:
            values: List of metric values
            timestamps: List of timestamps
            
        Returns:
            Steady state pattern information or None if not detected
        """
        if len(values) < 3:
            return None
            
        # Calculate mean and coefficient of variation
        mean = sum(values) / len(values)
        std_dev = math.sqrt(sum((x - mean) ** 2 for x in values) / len(values))
        
        # Calculate coefficient of variation
        cv = std_dev / abs(mean) if mean != 0 else float('inf')
        
        # Define threshold for steady state
        steady_threshold = 0.1  # 10% variation
        
        # Only report if CV is below threshold
        if cv >= steady_threshold:
            return None
            
        # Calculate steadiness (1 - CV)
        steadiness = 1.0 - cv
        
        # Calculate confidence
        confidence = steadiness * (1.0 - (1.0 / len(values)))  # Adjust by series length
        
        return {
            "type": PatternType.STEADY_STATE.value,
            "mean": mean,
            "std_dev": std_dev,
            "coefficient_of_variation": cv,
            "steadiness": steadiness,
            "confidence": confidence,
            "confidence_level": self._confidence_to_level(confidence),
            "description": f"Steady state pattern with {self._confidence_to_level(confidence)} confidence"
        }
        
    def _autocorrelation(self, values: List[float], lag: int) -> float:
        """
        Calculate autocorrelation at a specific lag.
        
        Args:
            values: Time series values
            lag: Lag value
            
        Returns:
            Autocorrelation coefficient
        """
        if len(values) <= lag:
            return 0
            
        # Mean and variance
        n = len(values)
        mean = sum(values) / n
        variance = sum((x - mean) ** 2 for x in values) / n
        
        if variance == 0:
            return 0
            
        # Calculate autocorrelation
        acf = 0
        for i in range(n - lag):
            acf += (values[i] - mean) * (values[i + lag] - mean)
            
        acf /= ((n - lag) * variance)
        
        return acf
        
    def _calculate_confidence(self, strength: float) -> float:
        """
        Calculate confidence level from pattern strength.
        
        Args:
            strength: Pattern strength value
            
        Returns:
            Confidence value (0.0 to 1.0)
        """
        # Simple linear scaling for now
        return min(1.0, max(0.0, strength))
        
    def _confidence_to_level(self, confidence: float) -> str:
        """
        Convert confidence value to confidence level string.
        
        Args:
            confidence: Confidence value (0.0 to 1.0)
            
        Returns:
            Confidence level string
        """
        if confidence >= 0.9:
            return PatternConfidence.VERY_HIGH.value
        elif confidence >= 0.75:
            return PatternConfidence.HIGH.value
        elif confidence >= 0.5:
            return PatternConfidence.MEDIUM.value
        elif confidence >= 0.25:
            return PatternConfidence.LOW.value
        else:
            return PatternConfidence.VERY_LOW.value
            
    def _calculate_sequence_confidence(
        self,
        sequence: Tuple[str, ...],
        event_sequence: List[str]
    ) -> float:
        """
        Calculate confidence for a sequence pattern.
        
        Args:
            sequence: The sequence pattern
            event_sequence: Full event sequence
            
        Returns:
            Confidence value (0.0 to 1.0)
        """
        if len(sequence) < 2:
            return 0.0
            
        # Count occurrences of prefix
        prefix = sequence[:-1]
        prefix_count = 0
        
        for i in range(len(event_sequence) - len(prefix) + 1):
            if tuple(event_sequence[i:i+len(prefix)]) == prefix:
                prefix_count += 1
                
        # Count occurrences of full sequence
        sequence_count = 0
        for i in range(len(event_sequence) - len(sequence) + 1):
            if tuple(event_sequence[i:i+len(sequence)]) == sequence:
                sequence_count += 1
                
        # Calculate confidence
        return sequence_count / prefix_count if prefix_count > 0 else 0.0
        
    def _meets_confidence_threshold(
        self,
        pattern: Optional[Dict[str, Any]],
        min_confidence: str
    ) -> bool:
        """
        Check if pattern meets minimum confidence threshold.
        
        Args:
            pattern: Pattern information
            min_confidence: Minimum confidence level
            
        Returns:
            True if pattern meets threshold
        """
        if not pattern:
            return False
            
        # Convert min_confidence to numeric value
        min_value = 0.0
        if min_confidence == PatternConfidence.VERY_HIGH.value:
            min_value = 0.9
        elif min_confidence == PatternConfidence.HIGH.value:
            min_value = 0.75
        elif min_confidence == PatternConfidence.MEDIUM.value:
            min_value = 0.5
        elif min_confidence == PatternConfidence.LOW.value:
            min_value = 0.25
        elif min_confidence == PatternConfidence.VERY_LOW.value:
            min_value = 0.0
            
        return pattern.get("confidence", 0.0) >= min_value
        
    def _determine_dominant_pattern(
        self,
        patterns: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Determine the dominant pattern from a list of detected patterns.
        
        Args:
            patterns: List of detected patterns
            
        Returns:
            Dominant pattern or None if no patterns
        """
        if not patterns:
            return None
            
        # Define pattern priorities
        pattern_priorities = {
            PatternType.TREND.value: 1,
            PatternType.SEASONAL.value: 2,
            PatternType.CYCLIC.value: 3,
            PatternType.THRESHOLD.value: 4,
            PatternType.OUTLIER.value: 5,
            PatternType.STEADY_STATE.value: 6
        }
        
        # Sort patterns by confidence and priority
        sorted_patterns = sorted(
            patterns,
            key=lambda p: (
                p.get("confidence", 0.0),
                -pattern_priorities.get(p.get("type", ""), 99)  # Negative for descending priority
            ),
            reverse=True
        )
        
        return sorted_patterns[0] if sorted_patterns else None
        
    async def _get_metric_thresholds(self, metric_id: str) -> Dict[str, float]:
        """
        Get thresholds for a specific metric type.
        
        Args:
            metric_id: Metric ID
            
        Returns:
            Dictionary of threshold types and values
        """
        # This would normally be loaded from configuration
        # For now, use some reasonable defaults based on metric type
        
        # Performance metrics
        if metric_id == "perf.response_time":
            return {
                "upper_warning": 1000.0,  # 1 second
                "upper_critical": 3000.0  # 3 seconds
            }
        elif metric_id == "perf.processing_time":
            return {
                "upper_warning": 500.0,  # 500 ms
                "upper_critical": 2000.0  # 2 seconds
            }
        elif metric_id == "perf.throughput":
            return {
                "lower_warning": 10.0,  # 10 ops/sec
                "lower_critical": 5.0  # 5 ops/sec
            }
            
        # Resource metrics
        elif metric_id == "res.cpu_usage":
            return {
                "upper_warning": 80.0,  # 80%
                "upper_critical": 95.0  # 95%
            }
        elif metric_id == "res.memory_usage":
            return {
                "upper_warning": 80.0,  # 80%
                "upper_critical": 90.0  # 90%
            }
            
        # Error metrics
        elif metric_id == "ops.error_count":
            return {
                "upper_warning": 10.0,
                "upper_critical": 50.0
            }
            
        # Default empty thresholds
        return {}
        
    async def _find_common_patterns(
        self,
        metric_patterns: Dict[str, Dict[str, Any]],
        correlations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Find common patterns across correlated metrics.
        
        Args:
            metric_patterns: Dictionary of metric patterns
            correlations: List of correlation information
            
        Returns:
            List of common pattern information
        """
        common_patterns = []
        
        for correlation in correlations:
            metric1 = correlation.get("metric1", "")
            metric2 = correlation.get("metric2", "")
            
            if not metric1 or not metric2:
                continue
                
            if metric1 not in metric_patterns or metric2 not in metric_patterns:
                continue
                
            patterns1 = metric_patterns[metric1].get("patterns_detected", [])
            patterns2 = metric_patterns[metric2].get("patterns_detected", [])
            
            # Check for common pattern types
            for pattern1 in patterns1:
                for pattern2 in patterns2:
                    if pattern1.get("type") == pattern2.get("type"):
                        common_pattern = {
                            "type": pattern1.get("type"),
                            "metrics": [metric1, metric2],
                            "correlation": correlation.get("correlation", 0),
                            "patterns": [pattern1, pattern2],
                            "description": f"Common {pattern1.get('type')} pattern between {metric1} and {metric2}"
                        }
                        
                        # Add more specific information based on pattern type
                        if pattern1.get("type") == PatternType.TREND.value:
                            if pattern1.get("direction") == pattern2.get("direction"):
                                common_pattern["direction"] = pattern1.get("direction")
                                common_pattern["description"] = f"Common {pattern1.get('direction')} trend between {metric1} and {metric2}"
                            else:
                                common_pattern["inverse_directions"] = True
                                common_pattern["description"] = f"Inverse trends between {metric1} and {metric2}"
                                
                        elif pattern1.get("type") == PatternType.SEASONAL.value:
                            if pattern1.get("period") == pattern2.get("period"):
                                common_pattern["period"] = pattern1.get("period")
                                common_pattern["description"] = f"Common seasonal pattern (period={pattern1.get('period')}) between {metric1} and {metric2}"
                                
                        common_patterns.append(common_pattern)
                        
        return common_patterns
        
    async def _analyze_behavior_patterns(
        self,
        component_id: str,
        metric_patterns: Dict[str, Dict[str, Any]],
        component_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Analyze behavior patterns for a component.
        
        Args:
            component_id: Component ID
            metric_patterns: Dictionary of metric patterns
            component_analysis: Component performance analysis
            
        Returns:
            List of behavior pattern information
        """
        behavior_patterns = []
        
        # Check for load-sensitive behavior
        if ("perf.response_time" in metric_patterns and 
            "perf.throughput" in metric_patterns):
            
            response_patterns = metric_patterns["perf.response_time"].get("patterns_detected", [])
            throughput_patterns = metric_patterns["perf.throughput"].get("patterns_detected", [])
            
            response_trend = next((p for p in response_patterns if p.get("type") == PatternType.TREND.value), None)
            throughput_trend = next((p for p in throughput_patterns if p.get("type") == PatternType.TREND.value), None)
            
            if (response_trend and throughput_trend and
                response_trend.get("direction") != throughput_trend.get("direction")):
                
                behavior_patterns.append({
                    "type": "load_sensitive",
                    "metrics": ["perf.response_time", "perf.throughput"],
                    "confidence": min(response_trend.get("confidence", 0), throughput_trend.get("confidence", 0)),
                    "confidence_level": self._confidence_to_level(
                        min(response_trend.get("confidence", 0), throughput_trend.get("confidence", 0))
                    ),
                    "description": f"Component {component_id} shows load-sensitive behavior"
                })
                
        # Check for resource constraint behavior
        if ("perf.response_time" in metric_patterns and 
            "res.cpu_usage" in metric_patterns):
            
            response_patterns = metric_patterns["perf.response_time"].get("patterns_detected", [])
            cpu_patterns = metric_patterns["res.cpu_usage"].get("patterns_detected", [])
            
            response_trend = next((p for p in response_patterns if p.get("type") == PatternType.TREND.value), None)
            cpu_trend = next((p for p in cpu_patterns if p.get("type") == PatternType.TREND.value), None)
            
            if (response_trend and cpu_trend and
                response_trend.get("direction") == "increasing" and
                cpu_trend.get("direction") == "increasing"):
                
                behavior_patterns.append({
                    "type": "resource_constrained",
                    "metrics": ["perf.response_time", "res.cpu_usage"],
                    "confidence": min(response_trend.get("confidence", 0), cpu_trend.get("confidence", 0)),
                    "confidence_level": self._confidence_to_level(
                        min(response_trend.get("confidence", 0), cpu_trend.get("confidence", 0))
                    ),
                    "description": f"Component {component_id} shows resource constraint behavior"
                })
                
        # Check for error-prone behavior
        if "ops.error_count" in metric_patterns:
            error_patterns = metric_patterns["ops.error_count"].get("patterns_detected", [])
            
            error_trend = next((p for p in error_patterns if p.get("type") == PatternType.TREND.value), None)
            error_threshold = next((p for p in error_patterns if p.get("type") == PatternType.THRESHOLD.value), None)
            
            if (error_trend and error_trend.get("direction") == "increasing" and
                error_trend.get("confidence", 0) > 0.6):
                
                behavior_patterns.append({
                    "type": "error_prone",
                    "metrics": ["ops.error_count"],
                    "confidence": error_trend.get("confidence", 0),
                    "confidence_level": self._confidence_to_level(error_trend.get("confidence", 0)),
                    "description": f"Component {component_id} shows increasing error rates"
                })
            elif error_threshold and error_threshold.get("confidence", 0) > 0.7:
                behavior_patterns.append({
                    "type": "error_prone",
                    "metrics": ["ops.error_count"],
                    "confidence": error_threshold.get("confidence", 0),
                    "confidence_level": self._confidence_to_level(error_threshold.get("confidence", 0)),
                    "description": f"Component {component_id} exceeds error rate thresholds"
                })
                
        # Check for stable behavior
        stable_count = 0
        total_metrics = 0
        
        for metric_id, patterns in metric_patterns.items():
            steady_pattern = next((p for p in patterns.get("patterns_detected", []) 
                             if p.get("type") == PatternType.STEADY_STATE.value), None)
            
            if steady_pattern and steady_pattern.get("confidence", 0) > 0.7:
                stable_count += 1
                
            total_metrics += 1
            
        if total_metrics > 0 and (stable_count / total_metrics) > 0.7:
            behavior_patterns.append({
                "type": "stable",
                "stable_metrics": stable_count,
                "total_metrics": total_metrics,
                "stability_ratio": stable_count / total_metrics,
                "confidence": stable_count / total_metrics,
                "confidence_level": self._confidence_to_level(stable_count / total_metrics),
                "description": f"Component {component_id} shows stable behavior across {stable_count}/{total_metrics} metrics"
            })
            
        return behavior_patterns
        
    async def _detect_persistent_patterns(self) -> None:
        """Run persistent pattern detection as a background task."""
        try:
            # Sleep to allow system startup
            await asyncio.sleep(300)  # 5 minutes
            
            while True:
                try:
                    logger.info("Running persistent pattern detection")
                    
                    # Get all component IDs
                    # This would normally come from Hermes registry
                    component_ids = ["rhetor", "engram", "terma", "athena"]
                    
                    # Detect patterns for each component
                    for component_id in component_ids:
                        try:
                            patterns = await self.detect_component_behavior_patterns(
                                component_id=component_id,
                                time_window="7d"
                            )
                            
                            logger.info(f"Detected behavior patterns for {component_id}: {patterns.get('has_patterns', False)}")
                            
                        except Exception as e:
                            logger.error(f"Error detecting patterns for {component_id}: {e}")
                            
                    # Sleep until next run (daily)
                    await asyncio.sleep(86400)  # 24 hours
                    
                except Exception as e:
                    logger.error(f"Error in persistent pattern detection: {e}")
                    await asyncio.sleep(3600)  # Retry after 1 hour
                    
        except asyncio.CancelledError:
            logger.info("Persistent pattern detection task cancelled")
        except Exception as e:
            logger.error(f"Unexpected error in pattern detection task: {e}")
            
# Global singleton instance
_pattern_engine = PatternEngine()

async def get_pattern_engine() -> PatternEngine:
    """
    Get the global pattern detection engine instance.
    
    Returns:
        PatternEngine instance
    """
    if not _pattern_engine.is_initialized:
        await _pattern_engine.initialize()
    return _pattern_engine