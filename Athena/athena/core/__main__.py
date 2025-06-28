"""
Main entry point for Athena AI specialist when run as module.
"""
import os
import sys

# Add paths before any imports to avoid module issues
script_path = os.path.realpath(__file__)
tekton_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_path))))
sys.path.insert(0, tekton_root)

# Set TEKTON_ROOT environment variable
if 'TEKTON_ROOT' not in os.environ:
    os.environ['TEKTON_ROOT'] = tekton_root

from .ai_specialist import main

if __name__ == '__main__':
    main()