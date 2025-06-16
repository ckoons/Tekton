#!/usr/bin/env python3
"""
Run Database MCP Server

This script starts the Hermes Database MCP Server that provides
database services through the MCP protocol.
"""

import os
import sys
import argparse
import logging

# Add project root to path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, ".."))
sys.path.insert(0, project_root)

# Import Hermes module
from hermes.api.database_mcp_server import main

if __name__ == "__main__":
    # Run the server
    main()