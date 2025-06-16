#!/usr/bin/env python3
"""
Tekton Component Definitions

Defines the metadata and configuration for all Tekton components.
"""

import threading
from typing import Dict, Any

# Component metadata
COMPONENTS = {
    "database": {
        "name": "Database Services",
        "description": "Core SQLite and vector databases",
        "dependencies": [],
        "startup_sequence": 1
    },
    "engram": {
        "name": "Engram Memory Service",
        "description": "Centralized memory and embedding service",
        "dependencies": ["database"],
        "startup_sequence": 2,
        "client_id": "engram_core"
    },
    "ergon": {
        "name": "Ergon Agent Framework",
        "description": "Agent and tool management framework",
        "dependencies": ["database", "engram"],
        "startup_sequence": 3,
        "client_id": "ergon_core" 
    },
    "ollama": {
        "name": "Ollama Integration",
        "description": "Local LLM integration through Ollama",
        "dependencies": ["database", "engram"],
        "startup_sequence": 10,
        "optional": True
    },
    "claude": {
        "name": "Claude Integration",
        "description": "Anthropic Claude API integration",
        "dependencies": ["database", "engram"],
        "startup_sequence": 11,
        "optional": True
    },
    "openai": {
        "name": "OpenAI Integration",
        "description": "OpenAI API integration",
        "dependencies": ["database", "engram"],
        "startup_sequence": 12,
        "optional": True
    }
}

# Tracks the running components and their processes
running_components = {}
component_processes = {}
running_lock = threading.RLock()