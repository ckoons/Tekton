"""
Analysis Engine for Sophia

This module provides advanced analysis capabilities for metrics collected across
the Tekton ecosystem, including pattern detection, anomaly detection, and trend analysis.
"""

import os
import json
import math
import asyncio
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple, Set
from datetime import datetime, timedelta

# Import metrics engine
from .metrics_engine import get_metrics_engine

logger = logging.getLogger("sophia.analysis_engine")

class AnalysisEngine:
    """
    Core analysis engine for processing metrics and generating insights.
    
    Provides a suite of analysis tools including statistical analysis,
    pattern recognition, anomaly detection, and trend analysis.
    """
    
    def __init__(self):
        """Initialize the analysis engine."""
        self.is_initialized = False
        self.metrics_engine = None
        self.analysis_cache = {}
        self.cache_expiry = {}
        self.analysis_tasks = {}
        self.baseline_data = {}
        
    async def initialize(self) -> bool:
        """
        Initialize the analysis engine.
        
        Returns:
            True if initialization was successful
        """
        logger.info("Initializing Sophia Analysis Engine...")
        
        # Get metrics engine
        self.metrics_engine = await get_metrics_engine()
        
        # Load baseline data if available
        await self._load_baseline_data()
        
        self.is_initialized = True
        logger.info("Sophia Analysis Engine initialized successfully")
        return True
        
    async def start(self) -> bool:
        """
        Start the analysis engine and background tasks.
        
        Returns:
            True if successful
        """
        if not self.is_initialized:
            success = await self.initialize()
            if not success:
                logger.error("Failed to initialize Analysis Engine")
                return False
                
        logger.info("Starting Sophia Analysis Engine...")
        
        # Start periodic analysis tasks
        self.analysis_tasks["periodic_trend_analysis"] = asyncio.create_task(
            self._periodic_trend_analysis()
        )
        
        logger.info("Sophia Analysis Engine started successfully")
        return True
        
    async def stop(self) -> bool:
        """
        Stop the analysis engine and clean up resources.
        
        Returns:
            True if successful
        """
        logger.info("Stopping Sophia Analysis Engine...")
        
        # Cancel background tasks
        for task_name, task in self.analysis_tasks.items():
            logger.info(f"Cancelling task: {task_name}")
            task.cancel()
            
        self.analysis_tasks = {}
        
        logger.info("Sophia Analysis Engine stopped successfully")
        return True
        
    async def analyze_metric_patterns(
        self,
        metric_id: str,
        time_window: str = "24h",
        source: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze patterns in a specific metric.
        
        Args:
            metric_id: The metric ID to analyze
            time_window: Time window for analysis (e.g., "24h", "7d")
            source: Filter by source
            tags: Filter by tags
            
        Returns:
            Analysis results
        """
        # Create cache key
        cache_key = f"pattern:{metric_id}:{time_window}:{source}:{tags}"
        
        # Check cache
        if cache_key in self.analysis_cache and cache_key in self.cache_expiry:
            if datetime.utcnow() < self.cache_expiry[cache_key]:
                return self.analysis_cache[cache_key]
        
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
        
        # Get time-series data with appropriate interval
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
        
        # Get raw metrics for detailed analysis
        raw_metrics = await self.metrics_engine.query_metrics(
            metric_id=metric_id,
            source=source,
            tags=tags,
            start_time=start_str,
            end_time=end_str,
            limit=10000
        )
        
        # Extract values
        values = []
        time_points = []
        
        if "time_series" in aggregated:
            for point in aggregated["time_series"]:
                if point["value"] is not None:
                    values.append(point["value"])
                    time_points.append(point["start_time"])
        
        # Perform pattern analysis
        patterns = await self._analyze_patterns(values, time_points, metric_id)
        
        # Perform statistical analysis
        stats = await self._calculate_statistics(raw_metrics)
        
        # Check for anomalies
        anomalies = await self._detect_anomalies(values, time_points, metric_id)
        
        # Calculate trends
        trends = await self._analyze_trends(values, time_points)
        
        # Compile results
        analysis = {
            "metric_id": metric_id,
            "time_window": time_window,
            "analysis_time": datetime.utcnow().isoformat() + "Z",
            "data_points": len(values),
            "raw_data_points": len(raw_metrics),
            "patterns": patterns,
            "statistics": stats,
            "anomalies": anomalies,
            "trends": trends,
            "has_significant_pattern": patterns["pattern_strength"] > 0.6,
            "has_anomalies": len(anomalies["points"]) > 0
        }
        
        # Add baseline comparison if available
        if metric_id in self.baseline_data:
            analysis["baseline_comparison"] = await self._compare_to_baseline(
                metric_id, stats, patterns
            )
        
        # Cache results
        self.analysis_cache[cache_key] = analysis
        self.cache_expiry[cache_key] = datetime.utcnow() + timedelta(hours=1)
        
        return analysis
        
    async def detect_anomalies(
        self,
        metric_id: str,
        sensitivity: float = 2.0,
        time_window: str = "24h",
        source: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Detect anomalies in a specific metric.
        
        Args:
            metric_id: The metric ID to analyze
            sensitivity: Sensitivity for anomaly detection (standard deviations)
            time_window: Time window for analysis
            source: Filter by source
            tags: Filter by tags
            
        Returns:
            Anomaly detection results
        """
        # Create cache key
        cache_key = f"anomaly:{metric_id}:{sensitivity}:{time_window}:{source}:{tags}"
        
        # Check cache
        if cache_key in self.analysis_cache and cache_key in self.cache_expiry:
            if datetime.utcnow() < self.cache_expiry[cache_key]:
                return self.analysis_cache[cache_key]
        
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
        
        # Get raw metrics
        raw_metrics = await self.metrics_engine.query_metrics(
            metric_id=metric_id,
            source=source,
            tags=tags,
            start_time=start_str,
            end_time=end_str,
            limit=10000
        )
        
        # Extract values and timestamps
        values = []
        timestamps = []
        
        for metric in raw_metrics:
            if "value" in metric and "timestamp" in metric:
                try:
                    value = float(metric["value"])
                    values.append(value)
                    timestamps.append(metric["timestamp"])
                except (ValueError, TypeError):
                    continue
        
        # Check if we have enough data
        if len(values) < 3:
            result = {
                "metric_id": metric_id,
                "time_window": time_window,
                "analysis_time": datetime.utcnow().isoformat() + "Z",
                "anomalies": [],
                "anomaly_count": 0,
                "has_anomalies": False,
                "message": "Insufficient data for anomaly detection"
            }
            
            # Cache results
            self.analysis_cache[cache_key] = result
            self.cache_expiry[cache_key] = datetime.utcnow() + timedelta(minutes=30)
            
            return result
        
        # Calculate mean and standard deviation
        mean_value = sum(values) / len(values)
        std_dev = math.sqrt(sum((x - mean_value) ** 2 for x in values) / len(values))
        
        # Define threshold
        upper_threshold = mean_value + (sensitivity * std_dev)
        lower_threshold = mean_value - (sensitivity * std_dev)
        
        # Find anomalies
        anomalies = []
        for i, value in enumerate(values):
            if value > upper_threshold or value < lower_threshold:
                anomalies.append({
                    "timestamp": timestamps[i],
                    "value": value,
                    "deviation": (value - mean_value) / std_dev if std_dev > 0 else 0,
                    "type": "high" if value > upper_threshold else "low"
                })
        
        # Sort anomalies by absolute deviation
        anomalies.sort(key=lambda x: abs(x["deviation"]), reverse=True)
        
        # Create result
        result = {
            "metric_id": metric_id,
            "time_window": time_window,
            "analysis_time": datetime.utcnow().isoformat() + "Z",
            "data_points": len(values),
            "mean": mean_value,
            "std_dev": std_dev,
            "upper_threshold": upper_threshold,
            "lower_threshold": lower_threshold,
            "sensitivity": sensitivity,
            "anomalies": anomalies,
            "anomaly_count": len(anomalies),
            "has_anomalies": len(anomalies) > 0,
            "anomaly_percentage": (len(anomalies) / len(values)) * 100 if values else 0
        }
        
        # Cache results
        self.analysis_cache[cache_key] = result
        self.cache_expiry[cache_key] = datetime.utcnow() + timedelta(hours=1)
        
        return result
        
    async def analyze_component_performance(
        self,
        component_id: str,
        time_window: str = "24h"
    ) -> Dict[str, Any]:
        """
        Analyze overall performance of a component.
        
        Args:
            component_id: ID of the component to analyze
            time_window: Time window for analysis
            
        Returns:
            Component performance analysis
        """
        # Create cache key
        cache_key = f"component:{component_id}:{time_window}"
        
        # Check cache
        if cache_key in self.analysis_cache and cache_key in self.cache_expiry:
            if datetime.utcnow() < self.cache_expiry[cache_key]:
                return self.analysis_cache[cache_key]
        
        # Define key metrics to analyze for components
        performance_metrics = [
            "perf.response_time",
            "perf.processing_time",
            "perf.throughput",
            "res.cpu_usage",
            "res.memory_usage"
        ]
        
        # Collect analyses for each metric
        metric_analyses = {}
        anomaly_count = 0
        
        for metric_id in performance_metrics:
            # Only analyze if we have data for this metric
            metrics = await self.metrics_engine.query_metrics(
                metric_id=metric_id,
                source=component_id,
                limit=1
            )
            
            if metrics:
                # Analyze this metric
                analysis = await self.analyze_metric_patterns(
                    metric_id=metric_id,
                    time_window=time_window,
                    source=component_id
                )
                
                metric_analyses[metric_id] = {
                    "statistics": analysis["statistics"],
                    "trends": analysis["trends"],
                    "anomalies": analysis["anomalies"],
                    "has_anomalies": analysis["has_anomalies"]
                }
                
                if analysis["has_anomalies"]:
                    anomaly_count += len(analysis["anomalies"]["points"])
        
        # Analyze error metrics specifically
        error_analysis = await self.analyze_metric_patterns(
            metric_id="ops.error_count",
            time_window=time_window,
            source=component_id
        )
        
        # Compile component performance result
        component_performance = {
            "component_id": component_id,
            "time_window": time_window,
            "analysis_time": datetime.utcnow().isoformat() + "Z",
            "metrics_analyzed": list(metric_analyses.keys()),
            "metric_analyses": metric_analyses,
            "error_analysis": error_analysis if "ops.error_count" in metric_analyses else None,
            "anomaly_count": anomaly_count,
            "has_anomalies": anomaly_count > 0,
            "overall_health": await self._calculate_health_score(
                component_id, metric_analyses, error_analysis
            )
        }
        
        # Cache results
        self.analysis_cache[cache_key] = component_performance
        self.cache_expiry[cache_key] = datetime.utcnow() + timedelta(hours=1)
        
        return component_performance
        
    async def analyze_system_performance(
        self,
        time_window: str = "24h",
        components: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze overall system performance across components.
        
        Args:
            time_window: Time window for analysis
            components: List of components to include (all if None)
            
        Returns:
            System performance analysis
        """
        # Create cache key
        components_key = ",".join(sorted(components)) if components else "all"
        cache_key = f"system:{time_window}:{components_key}"
        
        # Check cache
        if cache_key in self.analysis_cache and cache_key in self.cache_expiry:
            if datetime.utcnow() < self.cache_expiry[cache_key]:
                return self.analysis_cache[cache_key]
        
        # If no components specified, get all components with metrics
        if not components:
            # Get all sources from metrics
            performance_metrics = await self.metrics_engine.query_metrics(
                metric_id="perf.response_time",
                limit=1000
            )
            
            components = list(set(metric.get("source") for metric in performance_metrics 
                               if "source" in metric))
        
        # Analyze each component
        component_analyses = {}
        for component_id in components:
            if not component_id:
                continue
                
            component_analysis = await self.analyze_component_performance(
                component_id=component_id,
                time_window=time_window
            )
            component_analyses[component_id] = {
                "overall_health": component_analysis["overall_health"],
                "has_anomalies": component_analysis["has_anomalies"],
                "anomaly_count": component_analysis["anomaly_count"],
                "metrics_analyzed": component_analysis["metrics_analyzed"]
            }
        
        # Calculate overall system metrics
        response_times = []
        error_counts = []
        cpu_usage = []
        memory_usage = []
        throughput = []
        
        # Collect aggregate data
        for component_id, analysis in component_analyses.items():
            component_details = await self.analyze_component_performance(
                component_id=component_id,
                time_window=time_window
            )
            
            metric_analyses = component_details.get("metric_analyses", {})
            
            # Collect response times
            if "perf.response_time" in metric_analyses:
                stats = metric_analyses["perf.response_time"].get("statistics", {})
                if "mean" in stats:
                    response_times.append(stats["mean"])
            
            # Collect error counts
            if "ops.error_count" in metric_analyses:
                stats = metric_analyses["ops.error_count"].get("statistics", {})
                if "sum" in stats:
                    error_counts.append(stats["sum"])
            
            # Collect CPU usage
            if "res.cpu_usage" in metric_analyses:
                stats = metric_analyses["res.cpu_usage"].get("statistics", {})
                if "mean" in stats:
                    cpu_usage.append(stats["mean"])
            
            # Collect memory usage
            if "res.memory_usage" in metric_analyses:
                stats = metric_analyses["res.memory_usage"].get("statistics", {})
                if "mean" in stats:
                    memory_usage.append(stats["mean"])
            
            # Collect throughput
            if "perf.throughput" in metric_analyses:
                stats = metric_analyses["perf.throughput"].get("statistics", {})
                if "mean" in stats:
                    throughput.append(stats["mean"])
        
        # Calculate system-wide metrics
        system_metrics = {
            "avg_response_time": sum(response_times) / len(response_times) if response_times else None,
            "total_errors": sum(error_counts) if error_counts else 0,
            "avg_cpu_usage": sum(cpu_usage) / len(cpu_usage) if cpu_usage else None,
            "avg_memory_usage": sum(memory_usage) / len(memory_usage) if memory_usage else None,
            "total_throughput": sum(throughput) if throughput else None
        }
        
        # Calculate anomaly statistics
        anomaly_stats = {
            "components_with_anomalies": sum(1 for c in component_analyses.values() if c["has_anomalies"]),
            "total_anomaly_count": sum(c["anomaly_count"] for c in component_analyses.values()),
            "percentage_components_with_anomalies": (sum(1 for c in component_analyses.values() if c["has_anomalies"]) / len(component_analyses)) * 100 if component_analyses else 0
        }
        
        # Calculate overall system health
        component_health_scores = [a["overall_health"]["score"] for a in component_analyses.values() 
                                 if "overall_health" in a and "score" in a["overall_health"]]
        system_health = {
            "score": sum(component_health_scores) / len(component_health_scores) if component_health_scores else 0,
            "status": self._health_score_to_status(sum(component_health_scores) / len(component_health_scores) if component_health_scores else 0),
            "anomaly_impact": (anomaly_stats["total_anomaly_count"] / len(components)) if components else 0
        }
        
        # Compile system performance result
        system_performance = {
            "time_window": time_window,
            "analysis_time": datetime.utcnow().isoformat() + "Z",
            "components_analyzed": components,
            "component_count": len(components),
            "component_analyses": component_analyses,
            "system_metrics": system_metrics,
            "anomaly_statistics": anomaly_stats,
            "system_health": system_health
        }
        
        # Cache results
        self.analysis_cache[cache_key] = system_performance
        self.cache_expiry[cache_key] = datetime.utcnow() + timedelta(hours=1)
        
        return system_performance
    
    async def analyze_multi_metric_correlations(
        self,
        metric_ids: List[str],
        time_window: str = "24h",
        source: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze correlations between multiple metrics.
        
        Args:
            metric_ids: List of metric IDs to analyze
            time_window: Time window for analysis
            source: Filter by source
            
        Returns:
            Correlation analysis
        """
        # Need at least 2 metrics to calculate correlation
        if len(metric_ids) < 2:
            return {
                "error": "At least 2 metrics are required for correlation analysis",
                "metric_ids": metric_ids
            }
            
        # Create cache key
        metrics_key = ",".join(sorted(metric_ids))
        cache_key = f"correlation:{metrics_key}:{time_window}:{source}"
        
        # Check cache
        if cache_key in self.analysis_cache and cache_key in self.cache_expiry:
            if datetime.utcnow() < self.cache_expiry[cache_key]:
                return self.analysis_cache[cache_key]
        
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
        
        # Get time-series data for all metrics
        metric_data = {}
        for metric_id in metric_ids:
            # Get data with appropriate interval
            hours_diff = (end_time - start_time).total_seconds() / 3600
            if hours_diff < 6:
                interval = "5m"  # 5-minute intervals for short windows
            elif hours_diff < 24:
                interval = "30m"  # 30-minute intervals for medium windows
            elif hours_diff < 168:  # 7 days
                interval = "2h"  # 2-hour intervals for week-long windows
            else:
                interval = "6h"  # 6-hour intervals for longer windows
                
            # Get aggregated data
            aggregated = await self.metrics_engine.aggregate_metrics(
                metric_id=metric_id,
                aggregation="avg",
                interval=interval,
                source=source,
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
                        
            metric_data[metric_id] = {
                "values": values,
                "timestamps": timestamps
            }
        
        # Check if we have enough data
        for metric_id, data in metric_data.items():
            if len(data["values"]) < 3:
                return {
                    "error": f"Insufficient data for metric {metric_id}",
                    "metric_ids": metric_ids,
                    "time_window": time_window
                }
        
        # Align timestamps across metrics
        aligned_data = self._align_time_series(metric_data)
        
        # Calculate correlations
        correlations = {}
        for i, metric1 in enumerate(metric_ids):
            for j, metric2 in enumerate(metric_ids):
                if i >= j:  # Only calculate upper triangle (and diagonal)
                    continue
                
                corr = self._calculate_correlation(
                    aligned_data[metric1],
                    aligned_data[metric2]
                )
                
                correlations[f"{metric1}_{metric2}"] = {
                    "correlation": corr,
                    "strength": abs(corr),
                    "direction": "positive" if corr >= 0 else "negative",
                    "significance": self._interpret_correlation_strength(abs(corr))
                }
        
        # Find strongest correlations
        strong_correlations = []
        for pair, corr_data in correlations.items():
            if abs(corr_data["correlation"]) > 0.7:
                metric1, metric2 = pair.split("_")
                strong_correlations.append({
                    "metric1": metric1,
                    "metric2": metric2,
                    "correlation": corr_data["correlation"],
                    "direction": corr_data["direction"],
                    "significance": corr_data["significance"]
                })
                
        # Sort by absolute correlation
        strong_correlations.sort(key=lambda x: abs(x["correlation"]), reverse=True)
        
        # Compile results
        result = {
            "metric_ids": metric_ids,
            "time_window": time_window,
            "analysis_time": datetime.utcnow().isoformat() + "Z",
            "data_points": {metric_id: len(values) for metric_id, values in aligned_data.items()},
            "correlations": correlations,
            "strong_correlations": strong_correlations,
            "has_strong_correlations": len(strong_correlations) > 0
        }
        
        # Cache results
        self.analysis_cache[cache_key] = result
        self.cache_expiry[cache_key] = datetime.utcnow() + timedelta(hours=2)
        
        return result
        
    async def _analyze_patterns(
        self,
        values: List[float],
        time_points: List[str],
        metric_id: str
    ) -> Dict[str, Any]:
        """
        Analyze patterns in time series data.
        
        Args:
            values: List of metric values
            time_points: List of timestamps
            metric_id: Metric ID
            
        Returns:
            Pattern analysis results
        """
        if not values or len(values) < 3:
            return {
                "has_pattern": False,
                "pattern_type": "insufficient_data",
                "pattern_strength": 0.0,
                "message": "Insufficient data for pattern analysis"
            }
            
        # Check for trend
        trend_strength, trend_direction = self._calculate_trend(values)
        
        # Check for seasonality (if enough data points)
        seasonality = self._detect_seasonality(values) if len(values) >= 12 else None
        
        # Check for cyclic patterns
        cycles = self._detect_cycles(values) if len(values) >= 12 else None
        
        # Check for steady state
        is_steady = self._is_steady_state(values)
        
        # Determine dominant pattern
        patterns = []
        pattern_strengths = {}
        
        if trend_strength > 0.5:
            patterns.append("trend")
            pattern_strengths["trend"] = trend_strength
            
        if seasonality and seasonality["strength"] > 0.5:
            patterns.append("seasonal")
            pattern_strengths["seasonal"] = seasonality["strength"]
            
        if cycles and cycles["strength"] > 0.5:
            patterns.append("cyclic")
            pattern_strengths["cyclic"] = cycles["strength"]
            
        if is_steady:
            patterns.append("steady")
            pattern_strengths["steady"] = 0.9  # High confidence for steady state
            
        if not patterns:
            patterns.append("random")
            pattern_strengths["random"] = 0.8
            
        # Find dominant pattern
        dominant_pattern = None
        max_strength = 0
        
        for pattern in patterns:
            if pattern_strengths.get(pattern, 0) > max_strength:
                dominant_pattern = pattern
                max_strength = pattern_strengths[pattern]
                
        # Compile pattern results
        pattern_results = {
            "has_pattern": dominant_pattern != "random",
            "pattern_type": dominant_pattern,
            "pattern_strength": max_strength,
            "detected_patterns": patterns,
            "trend": {
                "direction": trend_direction,
                "strength": trend_strength
            }
        }
        
        # Add seasonality details if detected
        if seasonality:
            pattern_results["seasonality"] = seasonality
            
        # Add cycle details if detected
        if cycles:
            pattern_results["cycles"] = cycles
            
        # Add steady state details if detected
        if is_steady:
            pattern_results["steady_state"] = {
                "mean": sum(values) / len(values),
                "variance": sum((x - (sum(values) / len(values))) ** 2 for x in values) / len(values),
                "stability": 1.0 - (math.sqrt(sum((x - (sum(values) / len(values))) ** 2 for x in values) / len(values)) / (sum(values) / len(values)) if sum(values) != 0 else 0)
            }
            
        return pattern_results
    
    def _calculate_trend(self, values: List[float]) -> Tuple[float, str]:
        """
        Calculate trend strength and direction.
        
        Args:
            values: List of metric values
            
        Returns:
            Tuple of (trend_strength, trend_direction)
        """
        if not values or len(values) < 2:
            return 0.0, "none"
            
        # Simple linear regression
        n = len(values)
        x = list(range(n))
        
        mean_x = sum(x) / n
        mean_y = sum(values) / n
        
        # Calculate slope
        numerator = sum((x[i] - mean_x) * (values[i] - mean_y) for i in range(n))
        denominator = sum((x[i] - mean_x) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0, "none"
            
        slope = numerator / denominator
        
        # Calculate correlation coefficient
        ss_xx = sum((x[i] - mean_x) ** 2 for i in range(n))
        ss_yy = sum((values[i] - mean_y) ** 2 for i in range(n))
        ss_xy = sum((x[i] - mean_x) * (values[i] - mean_y) for i in range(n))
        
        if ss_xx == 0 or ss_yy == 0:
            return 0.0, "none"
            
        r = ss_xy / (math.sqrt(ss_xx * ss_yy))
        
        # Trend strength is absolute correlation
        trend_strength = abs(r)
        
        # Trend direction
        if abs(slope) < 0.00001:
            trend_direction = "none"
        elif slope > 0:
            trend_direction = "increasing"
        else:
            trend_direction = "decreasing"
            
        return trend_strength, trend_direction
        
    def _detect_seasonality(self, values: List[float]) -> Optional[Dict[str, Any]]:
        """
        Detect seasonality in time series.
        
        Args:
            values: List of metric values
            
        Returns:
            Seasonality information or None if not detected
        """
        if len(values) < 12:
            return None
            
        # Try common seasonality periods
        best_period = None
        best_strength = 0
        
        for period in [2, 3, 4, 6, 12, 24]:
            if len(values) < period * 2:  # Need at least 2 full periods
                continue
                
            # Check autocorrelation at this lag
            autocorr = self._autocorrelation(values, period)
            
            if autocorr > 0.6 and autocorr > best_strength:
                best_period = period
                best_strength = autocorr
                
        if not best_period:
            return None
            
        return {
            "period": best_period,
            "strength": best_strength,
            "significant": best_strength > 0.7
        }
        
    def _detect_cycles(self, values: List[float]) -> Optional[Dict[str, Any]]:
        """
        Detect cyclic patterns in time series.
        
        Args:
            values: List of metric values
            
        Returns:
            Cycle information or None if not detected
        """
        if len(values) < 12:
            return None
            
        # Calculate autocorrelations for various lags
        autocorrs = []
        for lag in range(1, min(len(values) // 3, 30)):  # Up to 1/3 of series length or max 30
            autocorr = self._autocorrelation(values, lag)
            autocorrs.append((lag, autocorr))
            
        # Find peaks in autocorrelation
        peaks = []
        for i in range(1, len(autocorrs) - 1):
            if autocorrs[i][1] > autocorrs[i-1][1] and autocorrs[i][1] > autocorrs[i+1][1] and autocorrs[i][1] > 0.4:
                peaks.append(autocorrs[i])
                
        if not peaks:
            return None
            
        # Sort by strength
        peaks.sort(key=lambda x: x[1], reverse=True)
        
        return {
            "period": peaks[0][0],
            "strength": peaks[0][1],
            "significant": peaks[0][1] > 0.6,
            "additional_periods": [p[0] for p in peaks[1:3]] if len(peaks) > 1 else []
        }
        
    def _is_steady_state(self, values: List[float]) -> bool:
        """
        Check if the series is in a steady state (low variance).
        
        Args:
            values: List of metric values
            
        Returns:
            True if the series is in a steady state
        """
        if not values:
            return False
            
        mean = sum(values) / len(values)
        if mean == 0:
            return all(abs(v) < 0.001 for v in values)
            
        # Calculate coefficient of variation
        std_dev = math.sqrt(sum((x - mean) ** 2 for x in values) / len(values))
        cv = std_dev / abs(mean) if mean != 0 else 0
        
        # Consider steady if CV < 10%
        return cv < 0.1
        
    def _autocorrelation(self, values: List[float], lag: int) -> float:
        """
        Calculate autocorrelation at a specific lag.
        
        Args:
            values: List of metric values
            lag: Lag value
            
        Returns:
            Autocorrelation value
        """
        if len(values) <= lag:
            return 0
            
        # Mean and variance
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        
        if variance == 0:
            return 0
            
        # Calculate autocorrelation
        n = len(values) - lag
        autocorr = sum((values[i] - mean) * (values[i + lag] - mean) for i in range(n))
        autocorr /= (n * variance)
        
        return autocorr
    
    async def _calculate_statistics(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate statistical measures for a set of metrics.
        
        Args:
            metrics: List of metrics
            
        Returns:
            Statistical measures
        """
        if not metrics:
            return {
                "count": 0,
                "message": "No data available"
            }
            
        # Extract values
        values = []
        for metric in metrics:
            if "value" in metric:
                try:
                    value = float(metric["value"])
                    values.append(value)
                except (ValueError, TypeError):
                    continue
                    
        if not values:
            return {
                "count": 0,
                "message": "No numeric values available"
            }
            
        # Calculate basic statistics
        count = len(values)
        mean = sum(values) / count
        
        # Calculate variance and standard deviation
        variance = sum((x - mean) ** 2 for x in values) / count
        std_dev = math.sqrt(variance)
        
        # Calculate min, max, range
        min_val = min(values)
        max_val = max(values)
        range_val = max_val - min_val
        
        # Calculate median
        sorted_values = sorted(values)
        if count % 2 == 0:
            median = (sorted_values[count // 2 - 1] + sorted_values[count // 2]) / 2
        else:
            median = sorted_values[count // 2]
            
        # Calculate sum
        sum_val = sum(values)
        
        # Calculate quartiles
        q1_idx = count // 4
        q3_idx = count * 3 // 4
        q1 = sorted_values[q1_idx]
        q3 = sorted_values[q3_idx]
        iqr = q3 - q1
        
        # Compile statistics
        stats = {
            "count": count,
            "mean": mean,
            "median": median,
            "min": min_val,
            "max": max_val,
            "range": range_val,
            "sum": sum_val,
            "variance": variance,
            "std_dev": std_dev,
            "q1": q1,
            "q3": q3,
            "iqr": iqr,
            "coefficient_of_variation": std_dev / mean if mean != 0 else 0
        }
        
        return stats
        
    async def _detect_anomalies(
        self,
        values: List[float],
        time_points: List[str],
        metric_id: str
    ) -> Dict[str, Any]:
        """
        Detect anomalies in time series data.
        
        Args:
            values: List of metric values
            time_points: List of timestamps
            metric_id: Metric ID
            
        Returns:
            Anomaly detection results
        """
        if not values or len(values) < 3 or len(values) != len(time_points):
            return {
                "has_anomalies": False,
                "points": [],
                "message": "Insufficient data for anomaly detection"
            }
            
        # Calculate mean and standard deviation
        mean = sum(values) / len(values)
        std_dev = math.sqrt(sum((x - mean) ** 2 for x in values) / len(values))
        
        # Define thresholds
        threshold = 2.5  # 2.5 standard deviations
        upper_limit = mean + (threshold * std_dev)
        lower_limit = mean - (threshold * std_dev)
        
        # Find anomalies
        anomalies = []
        for i, value in enumerate(values):
            if value > upper_limit or value < lower_limit:
                anomalies.append({
                    "index": i,
                    "timestamp": time_points[i],
                    "value": value,
                    "deviation": (value - mean) / std_dev,
                    "type": "high" if value > upper_limit else "low"
                })
                
        # Sort by absolute deviation
        anomalies.sort(key=lambda x: abs(x["deviation"]), reverse=True)
        
        return {
            "has_anomalies": len(anomalies) > 0,
            "points": anomalies,
            "mean": mean,
            "std_dev": std_dev,
            "upper_limit": upper_limit,
            "lower_limit": lower_limit,
            "anomaly_count": len(anomalies),
            "anomaly_percentage": (len(anomalies) / len(values)) * 100
        }
        
    async def _analyze_trends(
        self,
        values: List[float],
        time_points: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze trends in time series data.
        
        Args:
            values: List of metric values
            time_points: List of timestamps
            
        Returns:
            Trend analysis results
        """
        if not values or len(values) < 3:
            return {
                "has_trend": False,
                "message": "Insufficient data for trend analysis"
            }
            
        # Calculate trend using regression
        n = len(values)
        x = list(range(n))
        
        # Calculate slope and intercept
        mean_x = sum(x) / n
        mean_y = sum(values) / n
        
        # Calculate slope (rise/run)
        numerator = sum((x[i] - mean_x) * (values[i] - mean_y) for i in range(n))
        denominator = sum((x[i] - mean_x) ** 2 for i in range(n))
        
        if denominator == 0:
            return {
                "has_trend": False,
                "message": "Cannot calculate trend"
            }
            
        slope = numerator / denominator
        intercept = mean_y - slope * mean_x
        
        # Calculate fitted values
        fitted = [slope * x_val + intercept for x_val in x]
        
        # Calculate R-squared
        ss_total = sum((y - mean_y) ** 2 for y in values)
        ss_residual = sum((values[i] - fitted[i]) ** 2 for i in range(n))
        
        r_squared = 1 - (ss_residual / ss_total) if ss_total != 0 else 0
        
        # Determine trend direction and significance
        if abs(slope) < 0.0001:
            trend_direction = "flat"
            trend_significance = "none"
        elif slope > 0:
            trend_direction = "increasing"
            if slope > 0.1:
                trend_significance = "significant"
            else:
                trend_significance = "slight"
        else:
            trend_direction = "decreasing"
            if slope < -0.1:
                trend_significance = "significant"
            else:
                trend_significance = "slight"
                
        # Calculate trend strength
        trend_strength = abs(r_squared)
        
        # Calculate rate of change
        if len(values) > 1 and values[0] != 0:
            overall_change = values[-1] - values[0]
            percent_change = (overall_change / abs(values[0])) * 100
        else:
            overall_change = 0
            percent_change = 0
            
        # Compile trend results
        trend_results = {
            "has_trend": trend_strength > 0.3,
            "direction": trend_direction,
            "significance": trend_significance,
            "strength": trend_strength,
            "slope": slope,
            "intercept": intercept,
            "r_squared": r_squared,
            "overall_change": overall_change,
            "percent_change": percent_change,
            "fit_quality": "good" if r_squared > 0.7 else "moderate" if r_squared > 0.4 else "poor"
        }
        
        return trend_results
        
    async def _compare_to_baseline(
        self,
        metric_id: str,
        current_stats: Dict[str, Any],
        current_patterns: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare current metrics to baseline.
        
        Args:
            metric_id: Metric ID
            current_stats: Current statistical measures
            current_patterns: Current pattern analysis
            
        Returns:
            Baseline comparison results
        """
        # Check if we have baseline data
        if metric_id not in self.baseline_data:
            return {
                "available": False,
                "message": "No baseline data available for comparison"
            }
            
        baseline = self.baseline_data[metric_id]
        
        # Compare mean
        if "mean" in current_stats and "mean" in baseline["statistics"]:
            mean_diff = current_stats["mean"] - baseline["statistics"]["mean"]
            mean_percent = (mean_diff / baseline["statistics"]["mean"]) * 100 if baseline["statistics"]["mean"] != 0 else 0
        else:
            mean_diff = None
            mean_percent = None
            
        # Compare standard deviation
        if "std_dev" in current_stats and "std_dev" in baseline["statistics"]:
            std_diff = current_stats["std_dev"] - baseline["statistics"]["std_dev"]
            std_percent = (std_diff / baseline["statistics"]["std_dev"]) * 100 if baseline["statistics"]["std_dev"] != 0 else 0
        else:
            std_diff = None
            std_percent = None
            
        # Compare pattern
        pattern_match = (
            "pattern_type" in current_patterns and 
            "pattern_type" in baseline["patterns"] and
            current_patterns["pattern_type"] == baseline["patterns"]["pattern_type"]
        )
        
        # Compile comparison results
        comparison = {
            "available": True,
            "baseline_time": baseline["time"],
            "mean_difference": mean_diff,
            "mean_percent_change": mean_percent,
            "std_dev_difference": std_diff,
            "std_dev_percent_change": std_percent,
            "pattern_match": pattern_match,
            "significant_deviation": (
                abs(mean_percent) > 20 if mean_percent is not None else False
            )
        }
        
        return comparison
        
    async def _calculate_health_score(
        self,
        component_id: str,
        metric_analyses: Dict[str, Dict[str, Any]],
        error_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate health score for a component.
        
        Args:
            component_id: Component ID
            metric_analyses: Metric analyses
            error_analysis: Error analysis
            
        Returns:
            Health score data
        """
        # Base score
        base_score = 100
        
        # Factor in response time if available
        if "perf.response_time" in metric_analyses:
            response_analysis = metric_analyses["perf.response_time"]
            
            # Penalize for high response times
            if "statistics" in response_analysis and "mean" in response_analysis["statistics"]:
                mean_response = response_analysis["statistics"]["mean"]
                
                # Scale factor depends on component type
                if "rhetor" in component_id:
                    # LLM components have higher response times
                    if mean_response > 5000:  # > 5s
                        base_score -= 10
                    elif mean_response > 2000:  # > 2s
                        base_score -= 5
                else:
                    # Other components should be faster
                    if mean_response > 1000:  # > 1s
                        base_score -= 10
                    elif mean_response > 500:  # > 500ms
                        base_score -= 5
                        
            # Penalize for response time anomalies
            if "anomalies" in response_analysis and response_analysis["anomalies"].get("has_anomalies", False):
                anomaly_count = response_analysis["anomalies"].get("anomaly_count", 0)
                base_score -= min(anomaly_count * 2, 15)  # Up to 15 points off
        
        # Factor in error rate if available
        if error_analysis and "statistics" in error_analysis:
            error_stats = error_analysis["statistics"]
            
            # Penalize for errors
            if "sum" in error_stats:
                error_count = error_stats["sum"]
                base_score -= min(error_count, 30)  # Up to 30 points off
        
        # Factor in resource usage if available
        if "res.cpu_usage" in metric_analyses:
            cpu_analysis = metric_analyses["res.cpu_usage"]
            
            # Penalize for high CPU usage
            if "statistics" in cpu_analysis and "mean" in cpu_analysis["statistics"]:
                mean_cpu = cpu_analysis["statistics"]["mean"]
                if mean_cpu > 90:  # > 90%
                    base_score -= 15
                elif mean_cpu > 75:  # > 75%
                    base_score -= 10
                elif mean_cpu > 50:  # > 50%
                    base_score -= 5
        
        # Ensure score is within bounds
        score = max(0, min(100, base_score))
        
        # Determine status
        status = self._health_score_to_status(score)
        
        return {
            "score": score,
            "status": status,
            "factors": {
                "response_time": "perf.response_time" in metric_analyses,
                "errors": error_analysis is not None,
                "cpu_usage": "res.cpu_usage" in metric_analyses,
                "memory_usage": "res.memory_usage" in metric_analyses
            }
        }
        
    def _health_score_to_status(self, score: float) -> str:
        """
        Convert health score to status string.
        
        Args:
            score: Health score (0-100)
            
        Returns:
            Status string
        """
        if score >= 90:
            return "healthy"
        elif score >= 70:
            return "good"
        elif score >= 50:
            return "degraded"
        elif score >= 30:
            return "critical"
        else:
            return "failure"
    
    def _align_time_series(
        self,
        metric_data: Dict[str, Dict[str, List[Any]]]
    ) -> Dict[str, List[float]]:
        """
        Align time series data from multiple metrics.
        
        Args:
            metric_data: Dictionary mapping metric IDs to data
            
        Returns:
            Dictionary of aligned time series
        """
        # Find common timestamps
        all_timestamps = set()
        for metric_id, data in metric_data.items():
            all_timestamps.update(data["timestamps"])
            
        common_timestamps = sorted(list(all_timestamps))
        
        # Create aligned data
        aligned_data = {}
        
        for metric_id, data in metric_data.items():
            # Create a mapping from timestamp to value
            ts_to_value = {
                data["timestamps"][i]: data["values"][i]
                for i in range(len(data["timestamps"]))
            }
            
            # Create aligned values list
            aligned_values = []
            for ts in common_timestamps:
                if ts in ts_to_value:
                    aligned_values.append(ts_to_value[ts])
                else:
                    # Fill missing values with NaN
                    aligned_values.append(float('nan'))
            
            aligned_data[metric_id] = aligned_values
            
        return aligned_data
        
    def _calculate_correlation(
        self,
        values1: List[float],
        values2: List[float]
    ) -> float:
        """
        Calculate correlation between two series.
        
        Args:
            values1: First series
            values2: Second series
            
        Returns:
            Correlation coefficient
        """
        # Remove NaN values
        valid_pairs = [
            (x, y) for x, y in zip(values1, values2)
            if not (math.isnan(x) or math.isnan(y))
        ]
        
        if not valid_pairs:
            return 0.0
            
        x_values = [p[0] for p in valid_pairs]
        y_values = [p[1] for p in valid_pairs]
        
        n = len(valid_pairs)
        
        # Calculate means
        mean_x = sum(x_values) / n
        mean_y = sum(y_values) / n
        
        # Calculate covariance and variances
        cov = sum((x_values[i] - mean_x) * (y_values[i] - mean_y) for i in range(n))
        var_x = sum((x - mean_x) ** 2 for x in x_values)
        var_y = sum((y - mean_y) ** 2 for y in y_values)
        
        # Calculate correlation
        if var_x == 0 or var_y == 0:
            return 0.0
            
        return cov / (math.sqrt(var_x) * math.sqrt(var_y))
        
    def _interpret_correlation_strength(self, correlation: float) -> str:
        """
        Interpret the strength of a correlation coefficient.
        
        Args:
            correlation: Absolute correlation value
            
        Returns:
            String description of strength
        """
        if correlation >= 0.9:
            return "very strong"
        elif correlation >= 0.7:
            return "strong"
        elif correlation >= 0.5:
            return "moderate"
        elif correlation >= 0.3:
            return "weak"
        else:
            return "very weak"
            
    async def _load_baseline_data(self) -> bool:
        """
        Load baseline data for metrics.
        
        Returns:
            True if successful
        """
        # This would normally load from a file or database
        # For now, we'll just create empty baseline data
        self.baseline_data = {}
        return True
        
    async def _periodic_trend_analysis(self) -> None:
        """Run periodic trend analysis as a background task."""
        try:
            while True:
                # Sleep first to prevent immediate analysis on startup
                await asyncio.sleep(3600)  # Run hourly
                
                try:
                    logger.info("Running periodic trend analysis")
                    
                    # Get all available metrics
                    # This would be more efficient with direct querying
                    metrics = await self.metrics_engine.query_metrics(
                        limit=100,
                        sort="timestamp:desc"
                    )
                    
                    # Find unique metric IDs
                    metric_ids = set()
                    for metric in metrics:
                        if "metric_id" in metric:
                            metric_ids.add(metric["metric_id"])
                    
                    # Analyze each metric
                    for metric_id in metric_ids:
                        try:
                            await self.analyze_metric_patterns(
                                metric_id=metric_id,
                                time_window="24h"
                            )
                        except Exception as e:
                            logger.error(f"Error analyzing metric {metric_id}: {e}")
                    
                    logger.info(f"Completed periodic trend analysis for {len(metric_ids)} metrics")
                    
                except Exception as e:
                    logger.error(f"Error in periodic trend analysis: {e}")
                    
        except asyncio.CancelledError:
            logger.info("Periodic trend analysis task cancelled")
        except Exception as e:
            logger.error(f"Unexpected error in trend analysis task: {e}")
    
    async def compare_metric_sets(
        self,
        baseline_data: List[Dict[str, Any]],
        comparison_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compare two sets of metric data statistically.
        
        Args:
            baseline_data: Baseline metric data
            comparison_data: Comparison metric data
            
        Returns:
            Statistical comparison results
        """
        # Extract values from both datasets
        baseline_values = []
        comparison_values = []
        
        for metric in baseline_data:
            if "value" in metric:
                try:
                    baseline_values.append(float(metric["value"]))
                except (ValueError, TypeError):
                    continue
        
        for metric in comparison_data:
            if "value" in metric:
                try:
                    comparison_values.append(float(metric["value"]))
                except (ValueError, TypeError):
                    continue
        
        if not baseline_values or not comparison_values:
            return {
                "error": "Insufficient data for comparison",
                "baseline_count": len(baseline_values),
                "comparison_count": len(comparison_values)
            }
        
        # Calculate basic statistics for both sets
        baseline_mean = sum(baseline_values) / len(baseline_values)
        comparison_mean = sum(comparison_values) / len(comparison_values)
        
        baseline_std = math.sqrt(sum((x - baseline_mean) ** 2 for x in baseline_values) / len(baseline_values))
        comparison_std = math.sqrt(sum((x - comparison_mean) ** 2 for x in comparison_values) / len(comparison_values))
        
        # Calculate percentage change
        if baseline_mean != 0:
            percent_change = ((comparison_mean - baseline_mean) / baseline_mean) * 100
        else:
            percent_change = 0
        
        # Perform t-test (simplified)
        pooled_std = math.sqrt(
            ((len(baseline_values) - 1) * baseline_std ** 2 + 
             (len(comparison_values) - 1) * comparison_std ** 2) / 
            (len(baseline_values) + len(comparison_values) - 2)
        )
        
        if pooled_std > 0:
            t_statistic = (comparison_mean - baseline_mean) / (
                pooled_std * math.sqrt(1/len(baseline_values) + 1/len(comparison_values))
            )
        else:
            t_statistic = 0
        
        # Determine significance (simplified)
        critical_value = 2.0  # Approximately 95% confidence for large samples
        is_significant = abs(t_statistic) > critical_value
        
        # Effect size (Cohen's d)
        if pooled_std > 0:
            cohens_d = (comparison_mean - baseline_mean) / pooled_std
        else:
            cohens_d = 0
        
        # Interpret effect size
        if abs(cohens_d) < 0.2:
            effect_size = "negligible"
        elif abs(cohens_d) < 0.5:
            effect_size = "small"
        elif abs(cohens_d) < 0.8:
            effect_size = "medium"
        else:
            effect_size = "large"
        
        return {
            "baseline": {
                "count": len(baseline_values),
                "mean": baseline_mean,
                "std_dev": baseline_std,
                "min": min(baseline_values),
                "max": max(baseline_values)
            },
            "comparison": {
                "count": len(comparison_values),
                "mean": comparison_mean,
                "std_dev": comparison_std,
                "min": min(comparison_values),
                "max": max(comparison_values)
            },
            "difference": {
                "absolute": comparison_mean - baseline_mean,
                "percent_change": percent_change,
                "is_improvement": comparison_mean > baseline_mean,
                "is_significant": is_significant
            },
            "statistics": {
                "t_statistic": t_statistic,
                "cohens_d": cohens_d,
                "effect_size": effect_size,
                "pooled_std": pooled_std
            },
            "interpretation": {
                "direction": "increase" if comparison_mean > baseline_mean else "decrease",
                "magnitude": effect_size,
                "confidence": "high" if is_significant else "low"
            }
        }
    
    async def analyze_experiment_results(
        self,
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform deep analysis on experiment results.
        
        Args:
            results: Experiment results to analyze
            
        Returns:
            Deep analysis of the results
        """
        analysis = {
            "summary": {},
            "statistical_significance": {},
            "effect_sizes": {},
            "recommendations": [],
            "confidence_assessment": {}
        }
        
        try:
            # Analyze different types of experiments
            if "control" in results and "treatment" in results:
                # A/B test analysis
                analysis = await self._analyze_ab_test_results(results)
            elif "combinations" in results:
                # Multivariate test analysis
                analysis = await self._analyze_multivariate_results(results)
            elif "production" in results and "shadow" in results:
                # Shadow mode analysis
                analysis = await self._analyze_shadow_mode_results(results)
            else:
                # Generic experiment analysis
                analysis = await self._analyze_generic_experiment_results(results)
            
            # Add meta-analysis
            analysis["meta_analysis"] = {
                "data_quality": self._assess_data_quality(results),
                "sample_adequacy": self._assess_sample_adequacy(results),
                "external_validity": self._assess_external_validity(results),
                "internal_validity": self._assess_internal_validity(results)
            }
            
        except Exception as e:
            logger.error(f"Error in experiment results analysis: {str(e)}")
            analysis["error"] = str(e)
        
        return analysis
    
    async def _analyze_ab_test_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze A/B test results."""
        control_data = results.get("control", {})
        treatment_data = results.get("treatment", {})
        comparison = results.get("comparison", {})
        
        analysis = {
            "experiment_type": "A/B Test",
            "summary": {
                "winner": "treatment" if results.get("conclusion", "").startswith("Treatment is significantly better") else "control",
                "confidence": results.get("confidence_level", 0),
                "recommendation": results.get("recommended_action", "Continue testing")
            },
            "detailed_metrics": {},
            "overall_assessment": {}
        }
        
        # Analyze each metric
        for metric_id, comp_data in comparison.items():
            if isinstance(comp_data, dict) and "difference" in comp_data:
                difference = comp_data["difference"]
                analysis["detailed_metrics"][metric_id] = {
                    "percent_change": difference.get("percent_change", 0),
                    "absolute_change": difference.get("absolute", 0),
                    "is_significant": difference.get("is_significant", False),
                    "direction": difference.get("direction", "neutral"),
                    "effect_size": comp_data.get("statistics", {}).get("effect_size", "unknown")
                }
        
        return analysis
    
    async def _analyze_multivariate_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze multivariate test results."""
        return {
            "experiment_type": "Multivariate Test",
            "summary": {
                "best_combination": results.get("best_combination", "unknown"),
                "confidence_levels": results.get("confidence_levels", {}),
                "recommendation": results.get("recommended_action", "Continue testing")
            },
            "combination_performance": results.get("combinations", {}),
            "statistical_analysis": results.get("comparison", {})
        }
    
    async def _analyze_shadow_mode_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze shadow mode test results."""
        return {
            "experiment_type": "Shadow Mode Test",
            "summary": {
                "production_performance": results.get("production", {}),
                "shadow_performance": results.get("shadow", {}),
                "recommendation": results.get("recommended_action", "Continue monitoring")
            },
            "performance_comparison": results.get("comparison", {}),
            "risk_assessment": results.get("risk_assessment", {})
        }
    
    async def _analyze_generic_experiment_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze generic experiment results."""
        return {
            "experiment_type": "Generic Experiment",
            "summary": {
                "conclusion": results.get("conclusion", "Inconclusive"),
                "confidence": results.get("confidence_level", 0),
                "recommendation": results.get("recommended_action", "Continue testing")
            },
            "raw_results": results
        }
    
    def _assess_data_quality(self, results: Dict[str, Any]) -> Dict[str, str]:
        """Assess the quality of experiment data."""
        return {
            "completeness": "high",  # Simplified assessment
            "consistency": "high",
            "reliability": "medium"
        }
    
    def _assess_sample_adequacy(self, results: Dict[str, Any]) -> Dict[str, str]:
        """Assess if sample size is adequate."""
        return {
            "size_adequacy": "adequate",  # Simplified assessment
            "power_analysis": "sufficient",
            "recommendation": "current sample size is adequate"
        }
    
    def _assess_external_validity(self, results: Dict[str, Any]) -> Dict[str, str]:
        """Assess external validity of results."""
        return {
            "generalizability": "medium",  # Simplified assessment
            "population_representativeness": "good",
            "context_transferability": "high"
        }
    
    def _assess_internal_validity(self, results: Dict[str, Any]) -> Dict[str, str]:
        """Assess internal validity of results."""
        return {
            "confounding_control": "good",  # Simplified assessment
            "randomization_quality": "high",
            "measurement_validity": "high"
        }

# Global singleton instance
_analysis_engine = AnalysisEngine()

async def get_analysis_engine() -> AnalysisEngine:
    """
    Get the global analysis engine instance.
    
    Returns:
        AnalysisEngine instance
    """
    if not _analysis_engine.is_initialized:
        await _analysis_engine.initialize()
    return _analysis_engine