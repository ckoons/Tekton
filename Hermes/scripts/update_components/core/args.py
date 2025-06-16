"""
Command-line arguments for update_all_components script.
"""

import argparse
from pathlib import Path
from typing import List


def parse_args():
    """
    Parse command-line arguments for the update script.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Update Tekton components to use Hermes centralized services")
    
    parser.add_argument(
        "--tekton-root",
        type=str,
        default=None,
        help="Path to Tekton root directory (defaults to ../)"
    )
    
    parser.add_argument(
        "--components",
        type=str,
        nargs="*",
        choices=["engram", "ergon", "athena", "harmonia", "hermes", "all"],
        default=["all"],
        help="Components to update (defaults to all)"
    )
    
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip components that already use centralized services"
    )
    
    return parser.parse_args()


def determine_components(args) -> List[str]:
    """
    Determine which components to update based on arguments.
    
    Args:
        args: Parsed arguments
        
    Returns:
        List of component names to update
    """
    components = args.components
    if "all" in components:
        components = ["engram", "ergon", "athena", "harmonia", "hermes"]
    return components


def determine_tekton_root(args) -> Path:
    """
    Determine the Tekton root directory.
    
    Args:
        args: Parsed arguments
        
    Returns:
        Path to Tekton root directory
    """
    if args.tekton_root:
        return Path(args.tekton_root)
    else:
        # Default to two directories up from this file
        return Path(__file__).parent.parent.parent.parent.parent