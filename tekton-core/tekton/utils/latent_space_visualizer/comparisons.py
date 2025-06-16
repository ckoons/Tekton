"""
Comparison Utilities for Latent Space Reasoning Traces

This module provides functions for comparing and visualizing differences
between multiple reasoning traces.
"""

from datetime import datetime
from typing import Dict, Any, Optional
import logging

# Get logger
logger = logging.getLogger("tekton.utils.latent_space_visualizer.comparisons")

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
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"reasoning_comparison_{timestamp}.html"
        
    # Extract basic information
    metadata1 = trace1.get("metadata", {})
    metadata2 = trace2.get("metadata", {})
    
    component1 = metadata1.get("component_id", "unknown")
    component2 = metadata2.get("component_id", "unknown")
    
    thought_id1 = trace1.get("id", "unknown")
    thought_id2 = trace2.get("id", "unknown")
    
    iterations1 = trace1.get("iterations", [])
    iterations2 = trace2.get("iterations", [])
    
    # Generate HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Reasoning Trace Comparison</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.5; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ background-color: #f8f8f8; padding: 20px; margin-bottom: 20px; border-radius: 5px; }}
            .comparison {{ display: flex; gap: 20px; }}
            .trace {{ flex: 1; }}
            .iteration {{ border: 1px solid #ccc; padding: 15px; margin-bottom: 15px; border-radius: 5px; }}
            .iteration-header {{ background-color: #eee; padding: 10px; margin-bottom: 10px; border-radius: 3px; }}
            .final {{ border-color: #4CAF50; }}
            .content {{ white-space: pre-wrap; }}
            .stats {{ margin-top: 20px; padding: 15px; background-color: #f9f9f9; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Reasoning Trace Comparison</h1>
            </div>
            
            <div class="comparison">
                <div class="trace">
                    <h2>{component1} (ID: {thought_id1})</h2>
    """
    
    # Add first trace iterations
    for i, iteration in enumerate(iterations1):
        is_final = i == len(iterations1) - 1
        iteration_class = "iteration final" if is_final else "iteration"
        
        content = iteration.get("content", "")
        iteration_num = iteration.get("iteration", i)
        
        html += f"""
                    <div class="{iteration_class}">
                        <div class="iteration-header">
                            <strong>Iteration {iteration_num}</strong>
                        </div>
                        <div class="content">{content}</div>
                    </div>
        """
    
    html += """
                </div>
                <div class="trace">
                    <h2>{component2} (ID: {thought_id2})</h2>
    """
    
    # Add second trace iterations
    for i, iteration in enumerate(iterations2):
        is_final = i == len(iterations2) - 1
        iteration_class = "iteration final" if is_final else "iteration"
        
        content = iteration.get("content", "")
        iteration_num = iteration.get("iteration", i)
        
        html += f"""
                    <div class="{iteration_class}">
                        <div class="iteration-header">
                            <strong>Iteration {iteration_num}</strong>
                        </div>
                        <div class="content">{content}</div>
                    </div>
        """
    
    html += """
                </div>
            </div>
            
            <div class="stats">
                <h2>Comparison Statistics</h2>
    """
    
    # Add comparison statistics
    iterations_count1 = len(iterations1)
    iterations_count2 = len(iterations2)
    
    html += f"""
                <p><strong>Trace 1 iterations:</strong> {iterations_count1}</p>
                <p><strong>Trace 2 iterations:</strong> {iterations_count2}</p>
                <p><strong>Iteration difference:</strong> {abs(iterations_count1 - iterations_count2)}</p>
    """
    
    # Add more comparison stats
    if iterations1 and iterations2:
        # Compare final content length
        final1 = iterations1[-1].get("content", "")
        final2 = iterations2[-1].get("content", "")
        
        len1 = len(final1)
        len2 = len(final2)
        
        html += f"""
                <p><strong>Final content length (Trace 1):</strong> {len1} characters</p>
                <p><strong>Final content length (Trace 2):</strong> {len2} characters</p>
                <p><strong>Length difference:</strong> {abs(len1 - len2)} characters</p>
        """
    
    html += """
            </div>
        </div>
    </body>
    </html>
    """
    
    # Write HTML to file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)
        
    logger.info(f"Generated comparison visualization at {output_file}")
    return output_file