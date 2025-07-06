#!/usr/bin/env python3
"""Debug AI launch issues"""

import asyncio
import sys
import os
import subprocess
import json

# Add Tekton root to path
sys.path.insert(0, os.environ.get('TEKTON_ROOT', '/Users/cskoons/projects/github/Tekton'))

# Registry removed - using fixed port calculations
from shared.utils.env_config import get_component_config

async def test_ai_launch(component: str):
    """Test launching an AI and see what happens"""
    print(f"\n=== Testing AI launch for {component} ===")
    
    config = get_component_config()
    ai_id = f"{component}-ai"
    
    # Calculate expected AI port
    component_port = config.get_port(component)
    if not component_port:
        print(f"Component {component} not found in config")
        return
    
    ai_port = (component_port - 8000) + 45000
    print(f"Expected port {ai_port} for {ai_id} (based on component port {component_port})")
    
    # Launch AI process
    cmd = [
        sys.executable, '-m', 'shared.ai.generic_specialist',
        '--port', str(ai_port),
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
    
    # No registry needed - using fixed ports
    print(f"Launched {ai_id} with PID {process.pid} on port {ai_port}")
    
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
    print(f"Attempting to connect to {ai_id} on port {ai_port}...")
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection('localhost', ai_port),
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