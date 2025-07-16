#!/usr/bin/env python3
"""
AI Specialist Summary Script
Provides comprehensive information about all AI specialists in the Tekton system
"""
import json
import socket
import subprocess
import os
from typing import Dict, List, Optional

def get_ai_info(port: int) -> Optional[Dict]:
    """Get AI info from a specific port."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect(('localhost', port))
            s.send(b'{"type": "info"}\n')
            response = s.recv(4096)
            return json.loads(response.decode())
    except Exception:
        return None

def get_process_info(ai_id: str) -> Optional[Dict]:
    """Get process info for an AI specialist."""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'generic_specialist' in line and f'--ai-id {ai_id}' in line:
                parts = line.split()
                return {
                    'pid': parts[1],
                    'cpu': parts[2],
                    'memory': parts[3],
                    'command': ' '.join(parts[10:])
                }
    except Exception:
        pass
    return None

def main():
    """Main function to gather AI specialist information."""
    print("=== Tekton AI Specialists Analysis ===\n")
    
    # Define all known AI specialists with their expected ports
    ai_specialists = [
        ('engram-ai', 'engram', 42000),
        ('hermes-ai', 'hermes', 42001),
        ('ergon-ai', 'ergon', 42002),
        ('rhetor-ai', 'rhetor', 42003),
        ('terma-ai', 'terma', 42004),
        ('athena-ai', 'athena', 42005),
        ('prometheus-ai', 'prometheus', 42006),
        ('harmonia-ai', 'harmonia', 42007),
        ('telos-ai', 'telos', 42008),
        ('synthesis-ai', 'synthesis', 42009),
        ('tekton_core-ai', 'tekton_core', 42010),
        ('metis-ai', 'metis', 42011),
        ('apollo-ai', 'apollo', 42012),
        ('penia-ai', 'penia', 42013),
        ('sophia-ai', 'sophia', 42014),
        ('noesis-ai', 'noesis', 42015),
        ('numa-ai', 'numa', 42016),
        ('hephaestus-ai', 'hephaestus', 42080),
    ]
    
    running_ais = []
    
    for ai_id, component, port in ai_specialists:
        ai_info = get_ai_info(port)
        if ai_info:
            process_info = get_process_info(ai_id)
            
            # Get component expertise from the generic_specialist
            try:
                from shared.ai.generic_specialist import COMPONENT_EXPERTISE
                expertise = COMPONENT_EXPERTISE.get(component, {})
                title = expertise.get('title', f'The {component.title()} Specialist')
                expertise_desc = expertise.get('expertise', f'{component.title()} operations')
                focus = expertise.get('focus', f'{component.lower()} specific tasks')
            except ImportError:
                title = f'The {component.title()} Specialist'
                expertise_desc = f'{component.title()} operations'
                focus = f'{component.lower()} specific tasks'
            
            running_ais.append({
                'ai_id': ai_id,
                'component': component,
                'title': title,
                'port': port,
                'model_provider': ai_info.get('model_provider', 'unknown'),
                'model_name': ai_info.get('model_name', 'unknown'),
                'expertise': expertise_desc,
                'focus': focus,
                'process_info': process_info
            })
    
    print(f"Found {len(running_ais)} running AI specialists:")
    print("=" * 80)
    
    for ai in running_ais:
        print(f"AI ID: {ai['ai_id']}")
        print(f"Component: {ai['component']}")
        print(f"Title: {ai['title']}")
        print(f"Port: {ai['port']}")
        print(f"Model: {ai['model_name']} (via {ai['model_provider']})")
        print(f"Expertise: {ai['expertise']}")
        print(f"Focus: {ai['focus']}")
        if ai['process_info']:
            print(f"Process: PID {ai['process_info']['pid']}, CPU {ai['process_info']['cpu']}%, Memory {ai['process_info']['memory']}%")
        print("-" * 80)
    
    # Check for environment variable model overrides
    print("\nModel Configuration Analysis:")
    print("=" * 80)
    print(f"Default model: llama3.3:70b (as defined in specialist_worker.py)")
    print(f"Provider: {os.environ.get('TEKTON_AI_PROVIDER', 'ollama')}")
    
    # Check for component-specific model overrides
    model_overrides = []
    for ai in running_ais:
        env_var = f"{ai['component'].upper()}_AI_MODEL"
        if env_var in os.environ:
            model_overrides.append((ai['component'], env_var, os.environ[env_var]))
    
    if model_overrides:
        print("\nComponent-specific model overrides:")
        for component, env_var, model in model_overrides:
            print(f"  {component}: {env_var}={model}")
    else:
        print("\nNo component-specific model overrides found.")
    
    # Summary statistics
    print(f"\nSummary:")
    print(f"- Total AI specialists found: {len(running_ais)}")
    print(f"- Port range: 42000-42016, 42080")
    print(f"- All using model: llama3.3:70b")
    print(f"- Provider: ollama")
    print(f"- Socket communication protocol")

if __name__ == "__main__":
    main()