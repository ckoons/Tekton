"""
Latent Space Reasoning Visualization Utilities

This module provides tools for visualizing and analyzing latent space reasoning traces,
enabling better understanding of the iterative reasoning process.
"""

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("tekton.utils.latent_space_visualizer")

# Import main visualizer class
from tekton.utils.latent_space_visualizer.visualizer import LatentSpaceVisualizer

# Re-export for backward compatibility
__all__ = ["LatentSpaceVisualizer"]