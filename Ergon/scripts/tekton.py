#!/usr/bin/env python3
"""
Tekton Suite Launcher - Unified launcher for the Tekton ecosystem.

This script orchestrates the startup of all Tekton components in the correct order,
ensuring that dependencies are properly initialized before dependent services.
"""

# This file has been refactored into a module structure for better organization.
# It's kept here for backward compatibility.

import sys
import os
from pathlib import Path

# Add the scripts directory to the Python path if needed
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    # Import from the refactored module
    from tekton.main import main
except ImportError as e:
    print(f"Error importing Tekton modules: {e}")
    print("Please make sure the tekton module is properly installed.")
    
    # For backward compatibility, try to run the original implementation
    print("Attempting to run the original implementation...")
    import os
    import argparse
    import asyncio
    import logging
    import signal
    import time
    import subprocess
    import threading
    
    # Continue with original implementation...
    # Note: In a real installation, the refactored code should be properly installed
    print("Failed to import the refactored module. Please fix the installation.")
    sys.exit(1)

if __name__ == "__main__":
    main()