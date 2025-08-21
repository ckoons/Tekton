"""
HTML Generation for Latent Space Visualization

This module handles the generation of HTML visualizations for latent space reasoning traces.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

# Get logger
logger = logging.getLogger("tekton.utils.latent_space_visualizer.html_generator")

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
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"reasoning_trace_{timestamp}.html"
        
    # Extract main data
    iterations = reasoning_trace.get("iterations", [])
    metadata = reasoning_trace.get("metadata", {})
    component_id = metadata.get("component_id", "unknown")
    thought_id = reasoning_trace.get("id", "unknown")
    
    # Generate HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.5; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ background-color: #f8f8f8; padding: 20px; margin-bottom: 20px; border-radius: 5px; }}
            .metadata {{ background-color: #f8f8f8; padding: 15px; margin-bottom: 20px; border-radius: 5px; }}
            .iterations {{ display: flex; flex-direction: column; gap: 15px; }}
            .iteration {{ border: 1px solid #ccc; padding: 15px; border-radius: 5px; }}
            .iteration-header {{ background-color: #eee; padding: 10px; margin-bottom: 10px; border-radius: 3px; }}
            .final {{ border-color: #4CAF50; }}
            .content {{ white-space: pre-wrap; }}
            .highlight {{ background-color: #FFFF99; }}
            .metrics {{ margin-top: 10px; display: flex; gap: 15px; }}
            .metric {{ background-color: #e9f7fe; padding: 5px 10px; border-radius: 3px; font-size: 0.9em; }}
            .tabs {{ display: flex; margin-bottom: 10px; }}
            .tab {{ padding: 8px 15px; background-color: #f1f1f1; cursor: pointer; border: 1px solid #ccc; }}
            .tab.active {{ background-color: white; border-bottom: 1px solid white; }}
            .tab-content {{ border: 1px solid #ccc; padding: 15px; margin-top: -1px; }}
            .stats {{ margin-top: 20px; padding: 15px; background-color: #f9f9f9; border-radius: 5px; }}
            .nav {{ margin-bottom: 20px; display: flex; gap: 10px; }}
            .nav-button {{ padding: 5px 10px; background-color: #f1f1f1; text-decoration: none; color: black; border-radius: 3px; }}
        </style>
        <script>
            function showTab(tabId) {{
                // Hide all tab contents
                const contents = document.getElementsByClassName('tab-content');
                for (let content of contents) {{
                    content.style.display = 'none';
                }}
                
                // Deactivate all tabs
                const tabs = document.getElementsByClassName('tab');
                for (let tab of tabs) {{
                    tab.classList.remove('active');
                }}
                
                // Show selected tab content and activate tab
                document.getElementById(tabId).style.display = 'block';
                document.querySelector(`[onclick="showTab('${{tabId}}')"]`).classList.add('active');
            }}
            
            function copyToClipboard(text) {{
                navigator.clipboard.writeText(text).then(() => {{
                    alert('Copied to clipboard!');
                }}).catch(err => {{
                    console.error('Error copying text: ', err);
                }});
            }}
            
            // Highlight differences between iterations when requested
            function highlightDifferences() {{
                const iterations = document.querySelectorAll('.iteration');
                if (iterations.length <= 1) return;
                
                // Create an array of iteration contents
                const contents = [];
                iterations.forEach(iteration => {{
                    const content = iteration.querySelector('.content').textContent;
                    contents.push(content);
                }});
                
                // For each iteration after the first, highlight differences
                for (let i = 1; i < iterations.length; i++) {{
                    const prevContent = contents[i-1];
                    const currContent = contents[i];
                    
                    // Simple word-level diff (could be improved with a proper diff algorithm)
                    const prevWords = prevContent.split(/\\s+/);
                    const currWords = currContent.split(/\\s+/);
                    
                    // Find words in current that weren't in previous
                    const newWords = currWords.filter(word => !prevWords.includes(word));
                    
                    // Highlight new words in the content
                    let highlightedContent = currContent;
                    newWords.forEach(word => {{
                        if (word.length > 3) {{ // Only highlight words of reasonable length
                            const regex = new RegExp(`\\b${{word}}\\b`, 'g');
                            highlightedContent = highlightedContent.replace(regex, `<span class="highlight">${{word}}</span>`);
                        }}
                    }});
                    
                    // Update the content
                    iterations[i].querySelector('.content').innerHTML = highlightedContent;
                }}
            }}
            
            window.onload = function() {{
                // Show the first tab by default
                showTab('tab-all');
                
                // Apply highlighting if enabled
                const highlightEnabled = {str(highlight_changes).lower()};
                if (highlightEnabled) {{
                    highlightDifferences();
                }}
            }};
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{title}</h1>
                <p><strong>Component:</strong> {component_id} | <strong>Thought ID:</strong> {thought_id}</p>
            </div>
            
            <div class="nav">
                <a href="#" class="nav-button" onclick="copyToClipboard('{thought_id}')">Copy Thought ID</a>
                <a href="#metadata" class="nav-button">Metadata</a>
                <a href="#iterations" class="nav-button">Iterations</a>
                <a href="#stats" class="nav-button">Statistics</a>
            </div>
            
            <div class="tabs">
                <div class="tab active" onclick="showTab('tab-all')">All Iterations</div>
                <div class="tab" onclick="showTab('tab-first-last')">First & Last</div>
                <div class="tab" onclick="showTab('tab-metadata')">Metadata</div>
            </div>
            
            <div id="tab-all" class="tab-content">
                <h2 id="iterations">Reasoning Iterations</h2>
                <div class="iterations">
    """
    
    # Add iterations
    for i, iteration in enumerate(iterations):
        # Determine if this is the final iteration
        is_final = i == len(iterations) - 1
        iteration_class = "iteration final" if is_final else "iteration"
        
        # Extract iteration data
        content = iteration.get("content", "")
        timestamp = iteration.get("timestamp", "")
        iteration_num = iteration.get("iteration", i)
        iteration_metadata = iteration.get("metadata", {})
        
        # Format timestamp if it's a number
        if isinstance(timestamp, (int, float)):
            timestamp = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        
        # Add metrics if available
        metrics_html = ""
        if iteration_metadata:
            metrics_html = '<div class="metrics">'
            for key, value in iteration_metadata.items():
                if key in ["processing_time", "similarity", "confidence"]:
                    if key == "processing_time":
                        metrics_html += f'<div class="metric">Time: {value:.2f}s</div>'
                    elif key == "similarity":
                        metrics_html += f'<div class="metric">Similarity: {value:.2f}</div>'
                    elif key == "confidence":
                        metrics_html += f'<div class="metric">Confidence: {value:.2f}</div>'
            metrics_html += '</div>'
        
        html += f"""
                    <div class="{iteration_class}">
                        <div class="iteration-header">
                            <strong>Iteration {iteration_num}</strong> 
                            (Timestamp: {timestamp})
                            {metrics_html}
                        </div>
                        <div class="content">{content}</div>
                    </div>
        """
    
    html += """
                </div>
            </div>
            
            <div id="tab-first-last" class="tab-content" style="display: none;">
                <h2>Initial & Final States</h2>
                <div class="iterations">
    """
    
    # Add just first and last iterations
    if iterations:
        first_iteration = iterations[0]
        first_content = first_iteration.get("content", "")
        first_timestamp = first_iteration.get("timestamp", "")
        first_iteration_num = first_iteration.get("iteration", 0)
        
        # Format timestamp if it's a number
        if isinstance(first_timestamp, (int, float)):
            first_timestamp = datetime.fromtimestamp(first_timestamp).strftime("%Y-%m-%d %H:%M:%S")
        
        html += f"""
                    <div class="iteration">
                        <div class="iteration-header">
                            <strong>Initial State (Iteration {first_iteration_num})</strong> 
                            (Timestamp: {first_timestamp})
                        </div>
                        <div class="content">{first_content}</div>
                    </div>
        """
        
        if len(iterations) > 1:
            last_iteration = iterations[-1]
            last_content = last_iteration.get("content", "")
            last_timestamp = last_iteration.get("timestamp", "")
            last_iteration_num = last_iteration.get("iteration", len(iterations) - 1)
            
            # Format timestamp if it's a number
            if isinstance(last_timestamp, (int, float)):
                last_timestamp = datetime.fromtimestamp(last_timestamp).strftime("%Y-%m-%d %H:%M:%S")
            
            html += f"""
                        <div class="iteration final">
                            <div class="iteration-header">
                                <strong>Final State (Iteration {last_iteration_num})</strong> 
                                (Timestamp: {last_timestamp})
                            </div>
                            <div class="content">{last_content}</div>
                        </div>
            """
    
    html += """
                </div>
            </div>
            
            <div id="tab-metadata" class="tab-content" style="display: none;">
                <h2 id="metadata">Metadata</h2>
                <div class="metadata">
    """
    
    # Add metadata
    for key, value in metadata.items():
        if isinstance(value, dict):
            html += f"<h3>{key}</h3><ul>"
            for subkey, subvalue in value.items():
                html += f"<li><strong>{subkey}:</strong> {subvalue}</li>"
            html += "</ul>"
        else:
            html += f"<p><strong>{key}:</strong> {value}</p>"
    
    html += """
                </div>
            </div>
            
            <div class="stats" id="stats">
                <h2>Statistics</h2>
    """
    
    # Calculate statistics
    if iterations:
        num_iterations = len(iterations)
        
        # Calculate average content length
        total_length = sum(len(iteration.get("content", "")) for iteration in iterations)
        avg_length = total_length / num_iterations if num_iterations > 0 else 0
        
        # Extract processing times if available
        processing_times = []
        for iteration in iterations:
            metadata = iteration.get("metadata", {})
            if "processing_time" in metadata:
                processing_times.append(metadata["processing_time"])
        
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else None
        
        # Extract similarity scores if available
        similarity_scores = []
        for iteration in iterations:
            metadata = iteration.get("metadata", {})
            if "similarity" in metadata:
                similarity_scores.append(metadata["similarity"])
        
        # Add statistics to HTML
        html += f"""
                <p><strong>Number of iterations:</strong> {num_iterations}</p>
                <p><strong>Average content length:</strong> {avg_length:.0f} characters</p>
        """
        
        if avg_processing_time is not None:
            html += f"<p><strong>Average processing time:</strong> {avg_processing_time:.2f} seconds</p>"
        
        if similarity_scores:
            html += f"<p><strong>Final similarity score:</strong> {similarity_scores[-1]:.4f}</p>"
        
        # Add convergence information if available
        if "converged" in metadata:
            converged = metadata["converged"]
            html += f"<p><strong>Convergence status:</strong> {'Converged' if converged else 'Did not converge'}</p>"
        
        # Add other relevant statistics
        if "process_type" in metadata:
            html += f"<p><strong>Process type:</strong> {metadata['process_type']}</p>"
    
    html += """
            </div>
        </div>
    </body>
    </html>
    """
    
    # Write HTML to file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)
        
    logger.info(f"Generated HTML visualization at {output_file}")
    return output_file