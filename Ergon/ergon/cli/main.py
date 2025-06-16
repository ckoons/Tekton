"""
Ergon Command Line Interface

This module has been refactored into a more modular structure.
It now serves as the entry point that imports from the new structure.
"""

from ergon.cli.core import app, load_commands

# Load all commands
load_commands()

if __name__ == "__main__":
    app()