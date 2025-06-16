#!/usr/bin/env python3
"""
Command Line Arguments for Ollama Bridge
This module provides functions for parsing command line arguments.
"""

import argparse
from typing import Any

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Ollama Bridge for Engram Memory")
    parser.add_argument("model", type=str, help="Ollama model to use (e.g., llama3:8b)")
    parser.add_argument("--system", type=str, help="Custom system prompt (overrides defaults)", default="")
    parser.add_argument("--temperature", type=float, help="Temperature (0.0-1.0)", default=0.7)
    parser.add_argument("--top-p", type=float, help="Top-p sampling", default=0.9)
    parser.add_argument("--max-tokens", type=int, help="Maximum tokens to generate", default=2048)
    parser.add_argument("--client-id", type=str, help="Engram client ID", default="ollama")
    parser.add_argument("--memory-functions", action="store_true", 
                        help="Enable memory function detection in model responses")
    parser.add_argument("--prompt-type", type=str, choices=["memory", "communication", "combined"], 
                        default="combined", help="Type of system prompt to use")
    parser.add_argument("--available-models", type=str, nargs="+", 
                        help="List of available AI models for communication", 
                        default=["Claude"])
    parser.add_argument("--hermes-integration", action="store_true",
                        help="Enable Hermes integration for centralized database services")
    return parser.parse_args()

def display_args(args: argparse.Namespace) -> None:
    """Display the command line arguments."""
    print(f"\nOllama Bridge with Engram Memory")
    print(f"Model: {args.model}")
    print(f"Client ID: {args.client_id}")
    print(f"Type 'exit' or '/quit' to exit, '/reset' to reset chat history\n")