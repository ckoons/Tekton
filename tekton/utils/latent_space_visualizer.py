#!/usr/bin/env python3
"""
Latent Space Reasoning Visualization Utilities

This module provides tools for visualizing and analyzing latent space reasoning traces,
enabling better understanding of the iterative reasoning process.

This module has been refactored into a modular structure. This file is kept for
backward compatibility.
"""

# Re-export from modular structure
from tekton.utils.latent_space_visualizer import LatentSpaceVisualizer

# For backward compatibility, re-export the class directly
__all__ = ["LatentSpaceVisualizer"]