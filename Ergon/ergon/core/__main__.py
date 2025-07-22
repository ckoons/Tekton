"""
Main entry point for Ergon AI specialist when run as module.
"""
import os
import sys

# Add paths before any imports to avoid module issues
script_path = os.path.realpath(__file__)
tekton_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_path))))
sys.path.insert(0, tekton_root)

from .ai_specialist import main

if __name__ == '__main__':
    main()
