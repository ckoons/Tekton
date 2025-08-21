#!/usr/bin/env python3
"""
Entry point for running tekton-core as a Python module.
Usage: python -m tekton_core
"""

import sys
import os

# Get paths
current_dir = os.path.dirname(os.path.abspath(__file__))

# IMPORTANT: Add Tekton root FIRST to ensure we use the main tekton library
# not any local tekton subdirectory
from shared.env import TektonEnviron
tekton_root = TektonEnviron.get('TEKTON_ROOT')
if tekton_root:
    sys.path.insert(0, tekton_root)  # Add main Tekton directory for shared modules
else:
    # Fallback for development - parent directory contains main tekton library
    tekton_root = os.path.dirname(current_dir)
    sys.path.insert(0, tekton_root)

# Then add current directory for local tekton-core modules
sys.path.insert(1, current_dir)  # Add tekton-core directory second

# Now run the tekton_api main
if __name__ == "__main__":
    # Import the main execution
    from tekton_api.api.__main__ import *