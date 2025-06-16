#!/usr/bin/env python3
"""
Update All Components - Converts all Tekton components to use Hermes centralized services.

This script updates Tekton components to use the Unified Registration Protocol
and Centralized Logging System from Hermes.

This file has been refactored into a more modular structure.
It now serves as a compatibility layer that imports from the new structure.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import from refactored structure
from update_components import (
    parse_args,
    determine_components,
    determine_tekton_root,
    UpdateManager
)

# Re-export functions from the refactored structure for backward compatibility
from update_components.updaters.engram import update_engram
from update_components.updaters.ergon import update_ergon
from update_components.updaters.athena import update_athena
from update_components.updaters.harmonia import update_harmonia
from update_components.updaters.hermes import update_hermes_itself
from update_components.utils.module import import_module_from_file


def main():
    """Main function to parse arguments and run the update."""
    # Parse arguments
    args = parse_args()
    
    # Set up logging
    from hermes.utils.logging_helper import setup_logging
    logger = setup_logging("hermes.scripts.update_all_components")
    
    # Determine Tekton root path
    tekton_root = determine_tekton_root(args)
    logger.info(f"Using Tekton root path: {tekton_root}")
    
    # Determine components to update
    components = determine_components(args)
    
    # Create update manager
    manager = UpdateManager(tekton_root, logger)
    
    # Update components
    results = manager.update_components(components)
    
    # Print summary
    manager.print_summary()
    
    return True


if __name__ == "__main__":
    main()