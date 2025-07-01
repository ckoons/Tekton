#!/usr/bin/env python3
"""
Terma Main Entry Point

Clean replacement for old PTY-based Terma.
This is a native terminal orchestrator - no web terminals, just native apps with aish.
"""

import sys
import os
from pathlib import Path

# Add terma to path
terma_path = Path(__file__).parent.parent
sys.path.insert(0, str(terma_path))

# Import and run the new terminal service
from api.terminal_service import main

if __name__ == "__main__":
    print("🚀 Terma v2.0 - Native Terminal Orchestrator")
    print("   No more web terminals - launching real native terminals!")
    main()