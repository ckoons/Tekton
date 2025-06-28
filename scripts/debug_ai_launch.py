#!/usr/bin/env python3
"""Debug AI launch issues"""

import asyncio
import sys
import os
import subprocess
import json

# Add Tekton root to path
sys.path.insert(0, os.environ.get('TEKTON_ROOT', '/Users/cskoons/projects/github/Tekton'))

from shared.ai.registry_client import AIRegistryClient

async def test_ai_launch(component: str):
    """Test launching an AI and see what happens"""
    print(f"\n=== Testing AI launch for {component} ===")
    
    registry_client = AIRegistryClient()
    ai_id = f"{component}-ai"
    
    # Check if already in registry
    existing = registry_client.get_ai_socket(ai_id)
    if existing:
        print(f"AI {ai_id} already registered on port {existing[1]}")
        return
    
    # Allocate port
    port = registry_client.allocate_port()
    print(f"Allocated port {port} for {ai_id}")
    
    # Launch AI process
    cmd = [
        sys.executable, '-m', 'shared.ai.generic_specialist',
        '--port', str(port),
        '--component', component,
        '--ai-id', ai_id,
        '--verbose'
    ]
    
    print(f"Launching: {' '.join(cmd)}")
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, 'PYTHONPATH': os.environ.get('TEKTON_ROOT')}
    )
    
    # Register with registry
    registry_client.register_platform_ai(
        ai_id=ai_id,
        port=port,
        component=component,
        metadata={
            'description': f'AI specialist for {component}',
            'pid': process.pid
        }
    )
    print(f"Registered {ai_id} with PID {process.pid}")
    
    # Wait a bit for startup
    await asyncio.sleep(2)
    
    # Check if process is still running
    poll = process.poll()
    if poll is not None:
        stdout, stderr = process.communicate()
        print(f"Process exited with code {poll}")
        print(f"STDOUT: {stdout.decode()}")
        print(f"STDERR: {stderr.decode()}")
        return
    
    # Try to connect
    print(f"Attempting to connect to {ai_id} on port {port}...")
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection('localhost', port),
            timeout=5.0
        )
        print(f"✓ Successfully connected to {ai_id}")
        
        # Send a ping
        writer.write(json.dumps({'type': 'ping'}).encode() + b'\n')
        await writer.drain()
        
        # Read response
        data = await asyncio.wait_for(reader.readline(), timeout=5.0)
        response = json.loads(data.decode())
        print(f"✓ Got response: {response}")
        
        writer.close()
        await writer.wait_closed()
        
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        
        # Check if process is still running
        poll = process.poll()
        if poll is not None:
            stdout, stderr = process.communicate()
            print(f"Process exited with code {poll}")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
        else:
            print(f"Process still running (PID {process.pid})")
    
    # Clean up
    if process.poll() is None:
        process.terminate()
        process.wait()

async def main():
    """Test Athena and Sophia AI launches"""
    await test_ai_launch('athena')
    await test_ai_launch('sophia')

if __name__ == '__main__':
    asyncio.run(main())