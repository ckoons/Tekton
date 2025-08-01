#!/usr/bin/env python3
"""Test MCP server directly without threading"""

import os
import sys

# Set up environment
os.environ['TEKTON_ROOT'] = '/Users/cskoons/projects/github/Coder-A'
sys.path.insert(0, os.environ['TEKTON_ROOT'])
sys.path.insert(0, 'src')

# Load environment
from shared.env import TektonEnvironLock
TektonEnvironLock.load()

# Now import and run
from mcp.app import app, start_mcp_server
print("Starting MCP server directly...")
start_mcp_server()