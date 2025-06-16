"""
Exporters for Latent Space Reasoning Traces

This module provides functions for exporting reasoning traces to various formats.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
import logging

# Get logger
logger = logging.getLogger("tekton.utils.latent_space_visualizer.exporters")

def export_trace_json(reasoning_trace: Dict[str, Any], output_file: Optional[str] = None) -> str:
    """
    Export a reasoning trace to JSON format.
    
    Args:
        reasoning_trace: The reasoning trace data
        output_file: Path for the output JSON file (generated if not provided)
        
    Returns:
        Path to the exported JSON file
    """
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"reasoning_trace_{timestamp}.json"
        
    # Ensure the directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(reasoning_trace, f, indent=2)
        
    logger.info(f"Exported reasoning trace to {output_file}")
    return output_file