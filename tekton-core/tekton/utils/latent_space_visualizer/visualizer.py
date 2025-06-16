"""
Latent Space Visualizer

Main class for visualizing and analyzing latent space reasoning traces.
"""

from datetime import datetime
from typing import Dict, Any, Optional
import logging

from tekton.utils.latent_space_visualizer.html_generator import generate_html_trace
from tekton.utils.latent_space_visualizer.exporters import export_trace_json
from tekton.utils.latent_space_visualizer.comparisons import compare_traces

# Get logger
logger = logging.getLogger("tekton.utils.latent_space_visualizer.visualizer")


class LatentSpaceVisualizer:
    """
    Utilities for visualizing and monitoring latent space reasoning.
    
    This class provides methods to generate HTML visualizations and export
    reasoning traces for analysis.
    """
    
    @staticmethod
    def generate_html_trace(
        reasoning_trace: Dict[str, Any], 
        output_file: Optional[str] = None,
        title: str = "Latent Reasoning Trace",
        highlight_changes: bool = True
    ) -> str:
        """
        Generate an HTML visualization of a reasoning trace.
        
        Args:
            reasoning_trace: The reasoning trace data
            output_file: Path for the output HTML file (generated if not provided)
            title: Title for the visualization
            highlight_changes: Whether to highlight changes between iterations
            
        Returns:
            Path to the generated HTML file
        """
        return generate_html_trace(
            reasoning_trace=reasoning_trace,
            output_file=output_file,
            title=title,
            highlight_changes=highlight_changes
        )
    
    @staticmethod
    def export_trace_json(reasoning_trace: Dict[str, Any], output_file: Optional[str] = None) -> str:
        """
        Export a reasoning trace to JSON format.
        
        Args:
            reasoning_trace: The reasoning trace data
            output_file: Path for the output JSON file (generated if not provided)
            
        Returns:
            Path to the exported JSON file
        """
        return export_trace_json(
            reasoning_trace=reasoning_trace,
            output_file=output_file
        )
    
    @staticmethod
    def compare_traces(
        trace1: Dict[str, Any], 
        trace2: Dict[str, Any], 
        output_file: Optional[str] = None
    ) -> str:
        """
        Compare two reasoning traces and generate a comparison visualization.
        
        Args:
            trace1: First reasoning trace
            trace2: Second reasoning trace
            output_file: Path for the output HTML file (generated if not provided)
            
        Returns:
            Path to the generated comparison HTML file
        """
        return compare_traces(
            trace1=trace1,
            trace2=trace2,
            output_file=output_file
        )


# Basic example usage
def main():
    """Example usage of the LatentSpaceVisualizer."""
    # Create a sample reasoning trace
    sample_trace = {
        "id": "thought_1234567890_abcdef",
        "metadata": {
            "component_id": "test_component",
            "created_at": datetime.now().timestamp(),
            "finalized": True,
            "iterations_performed": 3,
            "converged": True,
            "process_type": "iterative_refinement"
        },
        "iterations": [
            {
                "content": "Initial thought about the problem.",
                "timestamp": datetime.now().timestamp() - 300,
                "iteration": 0,
                "metadata": {
                    "processing_time": 1.2
                }
            },
            {
                "content": "Refined thought with more details about the problem and potential solutions.",
                "timestamp": datetime.now().timestamp() - 200,
                "iteration": 1,
                "metadata": {
                    "processing_time": 1.5,
                    "similarity": 0.6
                }
            },
            {
                "content": "Final comprehensive analysis of the problem with detailed solutions and considerations.",
                "timestamp": datetime.now().timestamp() - 100,
                "iteration": 2,
                "metadata": {
                    "processing_time": 1.8,
                    "similarity": 0.85
                }
            }
        ]
    }
    
    # Generate HTML visualization
    output_file = LatentSpaceVisualizer.generate_html_trace(sample_trace)
    print(f"Generated HTML visualization: {output_file}")
    
    # Export to JSON
    json_file = LatentSpaceVisualizer.export_trace_json(sample_trace)
    print(f"Exported JSON trace: {json_file}")


if __name__ == "__main__":
    main()