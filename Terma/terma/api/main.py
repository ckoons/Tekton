#!/usr/bin/env python3
"""
Terma Main Entry Point

Clean replacement for old PTY-based Terma.
This is a native terminal orchestrator - no web terminals, just native apps with aish.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add terma to path
terma_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(terma_path))

# Import and run the app
from terma.api.app import start_server

if __name__ == "__main__":
    print("🚀 Terma v2.0 - Native Terminal Orchestrator")
    print("   No more web terminals - launching real native terminals!")
    
    # Get port from command line if provided
    port = None
    if "--port" in sys.argv:
        idx = sys.argv.index("--port")
        if idx + 1 < len(sys.argv):
            port = int(sys.argv[idx + 1])
    
    # Run the server
    asyncio.run(start_server(port=port))