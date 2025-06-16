#!/usr/bin/env python3
"""
Ollama API Client
This module provides functions for interacting with the Ollama API.
"""

import os
import requests
from typing import List, Dict, Any, Optional

# Ollama API settings
OLLAMA_API_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_API_URL = f"{OLLAMA_API_HOST}/api/chat"

def call_ollama_api(model: str, messages: List[Dict[str, str]],
                   system: Optional[str] = None,
                   temperature: float = 0.7, 
                   top_p: float = 0.9,
                   max_tokens: int = 2048) -> Dict[str, Any]:
    """Call the Ollama API with the given parameters."""
    
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature,
            "top_p": top_p,
            "num_predict": max_tokens
        }
    }
    
    if system:
        payload["system"] = system
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Ollama API: {e}")
        return {"error": str(e)}

def check_ollama_status() -> Dict[str, Any]:
    """Check if Ollama is running and get available models."""
    try:
        response = requests.get(f"{OLLAMA_API_HOST}/api/tags")
        if response.status_code != 200:
            return {
                "status": "error", 
                "code": response.status_code,
                "models": []
            }
        
        return {
            "status": "ok",
            "models": [model["name"] for model in response.json().get("models", [])]
        }
    except requests.exceptions.ConnectionError:
        return {
            "status": "error",
            "code": "connection_error",
            "models": []
        }

def pull_model(model_name: str) -> Dict[str, Any]:
    """Pull a model from Ollama."""
    try:
        response = requests.post(f"{OLLAMA_API_HOST}/api/pull", json={"name": model_name})
        if response.status_code != 200:
            return {
                "status": "error",
                "code": response.status_code
            }
        return {
            "status": "ok"
        }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error": str(e)
        }