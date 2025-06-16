"""
Visualization tools for Tekton metrics.

This module provides tools for visualizing metrics data
collected during system operation.
"""

import json
import logging
import textwrap
from typing import Dict, List, Any, Optional, Union, Tuple

logger = logging.getLogger(__name__)

class MetricsVisualizer:
    """Base class for metrics visualization."""
    
    def __init__(self, storage=None):
        """Initialize metrics visualizer.
        
        Args:
            storage: Optional metrics storage engine
        """
        self.storage = storage
    
    def visualize_session(self, session_data):
        """Visualize a single session's metrics.
        
        Args:
            session_data: SessionData object or dict
        """
        raise NotImplementedError("Subclasses must implement visualize_session")
    
    def visualize_comparison(self, sessions):
        """Visualize a comparison of multiple sessions.
        
        Args:
            sessions: List of SessionData objects or dicts
        """
        raise NotImplementedError("Subclasses must implement visualize_comparison")
    
    def visualize_trend(self, sessions):
        """Visualize a trend across multiple sessions.
        
        Args:
            sessions: List of SessionData objects or dicts
        """
        raise NotImplementedError("Subclasses must implement visualize_trend")


class ConsoleVisualizer(MetricsVisualizer):
    """Visualizes metrics in console text format."""
    
    def visualize_session(self, session_data):
        """Visualize a single session's metrics.
        
        Args:
            session_data: SessionData object or dict
            
        Returns:
            Formatted string visualization
        """
        # Ensure we have dict format
        data = session_data.to_dict() if hasattr(session_data, 'to_dict') else session_data
        
        # Basic info
        output = []
        output.append("=" * 80)
        output.append(f"Session: {data['id']}")
        output.append("-" * 80)
        output.append(f"Prompt: {textwrap.shorten(data['prompt'], width=70)}")
        output.append(f"Start Time: {data['start_time']}")
        
        if data.get('end_time'):
            duration = data['end_time'] - data['start_time']
            output.append(f"Duration: {duration:.2f} seconds")
            
        output.append("")
        
        # Spectral metrics
        output.append("Spectral Metrics:")
        output.append("-" * 16)
        
        spectral = data.get('spectral_metrics', {})
        if spectral:
            for key, value in spectral.items():
                output.append(f"{key}: {value:.4f}")
        else:
            output.append("No spectral metrics available")
            
        output.append("")
        
        # Component activations
        output.append("Component Activations:")
        output.append("-" * 21)
        
        activations = data.get('component_activations', {})
        if activations:
            for component, acts in activations.items():
                output.append(f"{component}: {len(acts)} activations")
        else:
            output.append("No component activations recorded")
            
        output.append("")
        
        # Parameter usage
        output.append("Parameter Usage:")
        output.append("-" * 16)
        
        usage = data.get('parameter_usage', {})
        if usage:
            for component, params in usage.items():
                total = params.get('total', 0)
                active = params.get('active', 0)
                util = params.get('utilization', 0)
                output.append(f"{component}: {active}/{total} ({util:.2%} utilization)")
        else:
            output.append("No parameter usage recorded")
            
        output.append("")
        
        # Propagation path
        output.append("Propagation:")
        output.append("-" * 12)
        
        path = data.get('propagation_path', [])
        if path:
            output.append(f"Total steps: {len(path)}")
            
            # Show first few steps
            limit = min(5, len(path))
            for i in range(limit):
                step = path[i]
                output.append(f"  {step['source']} -> {step['destination']} ({step.get('info_content', 0):.2f})")
                
            if len(path) > limit:
                output.append(f"  ... {len(path) - limit} more steps")
        else:
            output.append("No propagation path recorded")
            
        output.append("")
        output.append("=" * 80)
        
        return "\n".join(output)
    
    def visualize_comparison(self, sessions):
        """Visualize a comparison of multiple sessions.
        
        Args:
            sessions: List of SessionData objects or dicts
            
        Returns:
            Formatted string visualization
        """
        if not sessions:
            return "No sessions to compare"
        
        # Ensure we have dict format
        session_dicts = []
        for session in sessions:
            if hasattr(session, 'to_dict'):
                session_dicts.append(session.to_dict())
            else:
                session_dicts.append(session)
        
        # Sort by start time
        session_dicts.sort(key=lambda x: x.get('start_time', 0))
        
        # Extract key metrics for comparison
        output = []
        output.append("=" * 80)
        output.append("Session Comparison")
        output.append("-" * 17)
        output.append("")
        
        # Generate comparison table
        headers = ["Session ID", "Duration", "DE", "PU", "MPT", "MQ"]
        output.append(" | ".join(headers))
        output.append("-" * (len(" | ".join(headers))))
        
        for session in session_dicts:
            session_id = session['id'][:8] + "..."  # Truncate ID
            
            duration = "-"
            if session.get('end_time') and session.get('start_time'):
                duration = f"{session['end_time'] - session['start_time']:.2f}s"
                
            spectral = session.get('spectral_metrics', {})
            de = f"{spectral.get('depth_efficiency', 0):.4f}"
            pu = f"{spectral.get('parametric_utilization', 0):.4f}"
            mpt = f"{spectral.get('min_propagation_threshold', 0)}"
            mq = f"{spectral.get('modularity_quotient', 0):.4f}"
            
            row = [session_id, duration, de, pu, mpt, mq]
            output.append(" | ".join(row))
            
        output.append("")
        
        # Key metric definitions
        output.append("Metric Definitions:")
        output.append("- DE: Depth Efficiency (performance / layer count)")
        output.append("- PU: Parametric Utilization (active parameters / total parameters)")
        output.append("- MPT: Minimum Propagation Threshold (shortest path components)")
        output.append("- MQ: Modularity Quotient (1 - cross-module / within-module flow)")
        
        output.append("")
        output.append("=" * 80)
        
        return "\n".join(output)
    
    def visualize_trend(self, sessions):
        """Visualize a trend across multiple sessions.
        
        Args:
            sessions: List of SessionData objects or dicts
            
        Returns:
            Formatted string visualization
        """
        if not sessions:
            return "No sessions to analyze"
        
        # Ensure we have dict format
        session_dicts = []
        for session in sessions:
            if hasattr(session, 'to_dict'):
                session_dicts.append(session.to_dict())
            else:
                session_dicts.append(session)
        
        # Sort by start time
        session_dicts.sort(key=lambda x: x.get('start_time', 0))
        
        # Extract metrics for trend analysis
        times = []
        de_values = []
        pu_values = []
        mq_values = []
        mpt_values = []
        
        for session in session_dicts:
            # Get timestamp
            time_str = "-"
            if session.get('start_time'):
                from datetime import datetime
                dt = datetime.fromtimestamp(session['start_time'])
                time_str = dt.strftime("%m-%d %H:%M")
            times.append(time_str)
            
            # Get metrics
            spectral = session.get('spectral_metrics', {})
            de_values.append(spectral.get('depth_efficiency', 0))
            pu_values.append(spectral.get('parametric_utilization', 0))
            mq_values.append(spectral.get('modularity_quotient', 0))
            mpt_values.append(spectral.get('min_propagation_threshold', 0))
        
        # Generate ASCII chart
        output = []
        output.append("=" * 80)
        output.append("Spectral Metrics Trend")
        output.append("-" * 21)
        output.append("")
        
        # Simple ASCII chart for DE
        output.append("Depth Efficiency Trend:")
        output.append(self._generate_ascii_chart(de_values, times, max_width=70))
        output.append("")
        
        # Simple ASCII chart for PU
        output.append("Parametric Utilization Trend:")
        output.append(self._generate_ascii_chart(pu_values, times, max_width=70))
        output.append("")
        
        # Simple ASCII chart for MQ
        output.append("Modularity Quotient Trend:")
        output.append(self._generate_ascii_chart(mq_values, times, max_width=70))
        output.append("")
        
        # Simple ASCII chart for MPT
        output.append("Minimum Propagation Threshold Trend:")
        output.append(self._generate_ascii_chart(mpt_values, times, max_width=70, scale=max(mpt_values)/20 if max(mpt_values) > 0 else 1))
        output.append("")
        
        output.append("=" * 80)
        
        return "\n".join(output)
    
    def _generate_ascii_chart(self, values, labels=None, max_width=40, scale=None):
        """Generate a simple ASCII chart.
        
        Args:
            values: List of numeric values
            labels: Optional list of labels
            max_width: Maximum width of the chart
            scale: Custom scale factor
            
        Returns:
            Formatted ASCII chart
        """
        if not values:
            return "No data"
            
        # Determine scale
        max_value = max(values) if values else 0
        if scale is None:
            scale = max_value / max_width if max_value > 0 else 1
            
        # Generate chart
        lines = []
        
        # Y-axis scale
        lines.append(f"{max_value:.2f} |")
        
        # Generate bars
        for i, value in enumerate(values):
            # Bar
            bar_width = int(value / scale) if scale > 0 else 0
            bar = "#" * bar_width
            
            # Label
            label = f"[{i}]" if not labels else f"[{labels[i]}]"
            
            lines.append(f"{value:.2f} | {bar} {label}")
            
        # X-axis
        lines.append("      " + "-" * max_width)
        
        return "\n".join(lines)


class JSONVisualizer(MetricsVisualizer):
    """Provides JSON output for metrics visualization."""
    
    def visualize_session(self, session_data):
        """Visualize a single session's metrics.
        
        Args:
            session_data: SessionData object or dict
            
        Returns:
            JSON string visualization
        """
        # Ensure we have dict format
        data = session_data.to_dict() if hasattr(session_data, 'to_dict') else session_data
        
        # Extract key metrics
        result = {
            "session_id": data['id'],
            "prompt": data['prompt'][:100] + "..." if len(data['prompt']) > 100 else data['prompt'],
            "start_time": data['start_time'],
            "duration": data['end_time'] - data['start_time'] if data.get('end_time') else None,
            "spectral_metrics": data.get('spectral_metrics', {}),
            "component_summary": {
                "count": len(data.get('component_activations', {})),
                "total_activations": sum(len(acts) for acts in data.get('component_activations', {}).values())
            },
            "parameter_summary": {
                "total": sum(usage.get('total', 0) for usage in data.get('parameter_usage', {}).values()),
                "active": sum(usage.get('active', 0) for usage in data.get('parameter_usage', {}).values())
            },
            "propagation_summary": {
                "steps": len(data.get('propagation_path', [])),
                "unique_components": len({step.get('source') for step in data.get('propagation_path', [])}.union(
                                        {step.get('destination') for step in data.get('propagation_path', [])}))
            }
        }
        
        return json.dumps(result, indent=2)
    
    def visualize_comparison(self, sessions):
        """Visualize a comparison of multiple sessions.
        
        Args:
            sessions: List of SessionData objects or dicts
            
        Returns:
            JSON string visualization
        """
        if not sessions:
            return json.dumps({"error": "No sessions to compare"})
        
        # Ensure we have dict format
        session_dicts = []
        for session in sessions:
            if hasattr(session, 'to_dict'):
                session_dicts.append(session.to_dict())
            else:
                session_dicts.append(session)
        
        # Extract key metrics for comparison
        comparison = []
        
        for session in session_dicts:
            # Basic info
            session_info = {
                "session_id": session['id'],
                "start_time": session['start_time']
            }
            
            # Duration
            if session.get('end_time') and session.get('start_time'):
                session_info["duration"] = session['end_time'] - session['start_time']
            
            # Spectral metrics
            spectral = session.get('spectral_metrics', {})
            session_info["spectral_metrics"] = spectral
            
            # Component summary
            session_info["component_count"] = len(session.get('component_activations', {}))
            
            # Parameter summary
            total_params = sum(usage.get('total', 0) for usage in session.get('parameter_usage', {}).values())
            active_params = sum(usage.get('active', 0) for usage in session.get('parameter_usage', {}).values())
            session_info["parameter_usage"] = {
                "total": total_params,
                "active": active_params,
                "utilization": active_params / total_params if total_params > 0 else 0
            }
            
            # Propagation summary
            session_info["propagation_steps"] = len(session.get('propagation_path', []))
            
            comparison.append(session_info)
        
        return json.dumps({"sessions": comparison}, indent=2)
    
    def visualize_trend(self, sessions):
        """Visualize a trend across multiple sessions.
        
        Args:
            sessions: List of SessionData objects or dicts
            
        Returns:
            JSON string visualization
        """
        if not sessions:
            return json.dumps({"error": "No sessions to analyze"})
        
        # Ensure we have dict format
        session_dicts = []
        for session in sessions:
            if hasattr(session, 'to_dict'):
                session_dicts.append(session.to_dict())
            else:
                session_dicts.append(session)
        
        # Sort by start time
        session_dicts.sort(key=lambda x: x.get('start_time', 0))
        
        # Extract metrics for trend analysis
        trend_data = {
            "timestamps": [],
            "session_ids": [],
            "metrics": {
                "depth_efficiency": [],
                "parametric_utilization": [],
                "modularity_quotient": [],
                "min_propagation_threshold": []
            }
        }
        
        for session in session_dicts:
            # Get timestamp and ID
            trend_data["timestamps"].append(session.get('start_time', 0))
            trend_data["session_ids"].append(session['id'])
            
            # Get metrics
            spectral = session.get('spectral_metrics', {})
            trend_data["metrics"]["depth_efficiency"].append(spectral.get('depth_efficiency', 0))
            trend_data["metrics"]["parametric_utilization"].append(spectral.get('parametric_utilization', 0))
            trend_data["metrics"]["modularity_quotient"].append(spectral.get('modularity_quotient', 0))
            trend_data["metrics"]["min_propagation_threshold"].append(spectral.get('min_propagation_threshold', 0))
        
        return json.dumps(trend_data, indent=2)