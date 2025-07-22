#!/usr/bin/env python3
"""
Entry point for running tekton-core as a Python module.
Usage: python -m tekton_core
"""

import sys
import os

# Add current directory (tekton-core) and Tekton root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)  # Add tekton-core directory so 'tekton' module can be found

# Add Tekton root to path using TektonEnviron
from shared.env import TektonEnviron
tekton_root = TektonEnviron.get('TEKTON_ROOT')
if tekton_root:
    sys.path.insert(0, tekton_root)  # Add main Tekton directory for shared modules
else:
    # Fallback for development
    tekton_root = os.path.dirname(current_dir)
    sys.path.insert(0, tekton_root)

# Now run the tekton api main
if __name__ == "__main__":
    # Import the main execution
    from tekton.api.__main__ import *