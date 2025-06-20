#!/usr/bin/env python3
"""
Trace what happens when navigation is triggered
"""
import httpx
import asyncio

MCP_URL = "http://localhost:8088/api/mcp/v2/execute"

async def mcp_request(tool_name, arguments, timeout=20.0):
    """Make MCP request with specified timeout"""
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(MCP_URL, json={
            "tool_name": tool_name,
            "arguments": arguments
        })
        return response.json()

async def trace_navigation():
    print("=== Tracing Rhetor Navigation ===\n")
    
    # First, inject some console logging
    print("1. Injecting console interceptor...")
    inject_result = await mcp_request("ui_sandbox", {
        "changes": [{
            "type": "script",
            "content": """
            // Intercept console.log to capture messages
            window._originalConsoleLog = window._originalConsoleLog || console.log;
            window._navigationLogs = [];
            console.log = function(...args) {
                const msg = args.join(' ');
                window._navigationLogs.push(msg);
                window._originalConsoleLog(...args);
            };
            return 'Console interceptor installed';
            """
        }],
        "preview": False
    })
    
    print(f"   Result: {inject_result.get('status', 'Unknown')}")
    
    # Simulate clicking on Rhetor nav item
    print("\n2. Simulating click on Rhetor nav item...")
    click_result = await mcp_request("ui_interact", {
        "selector": ".nav-item[data-component='rhetor']",
        "action": "click"
    })
    
    print(f"   Click result: {click_result.get('status', 'Unknown')}")
    
    # Wait for any async operations
    await asyncio.sleep(3)
    
    # Get the console logs
    print("\n3. Retrieving console logs...")
    logs_result = await mcp_request("ui_sandbox", {
        "changes": [{
            "type": "script",
            "content": """
            const relevantLogs = window._navigationLogs.filter(log => 
                log.includes('rhetor') || 
                log.includes('Rhetor') ||
                log.includes('COMPONENT ACTIVATION') ||
                log.includes('MinimalLoader') ||
                log.includes('loadComponent')
            ).slice(-10);
            return relevantLogs.length > 0 ? relevantLogs : ['No relevant logs found'];
            """
        }],
        "preview": False
    })
    
    if logs_result['status'] == 'success':
        logs = logs_result['result'].get('changes_applied', [['No logs']])[0]
        print("\n   Navigation logs:")
        if isinstance(logs, list):
            for log in logs:
                print(f"     - {log}")
        else:
            print(f"     {logs}")
    
    # Check final state
    print("\n4. Checking final state...")
    state_result = await mcp_request("ui_capture", {})
    loaded = state_result['result'].get('loaded_component', 'Unknown')
    print(f"   Loaded component: {loaded}")
    
    # Check if minimalLoader exists and has correct path
    print("\n5. Checking minimalLoader configuration...")
    loader_check = await mcp_request("ui_sandbox", {
        "changes": [{
            "type": "script",
            "content": """
            if (window.minimalLoader) {
                const rhetorPath = window.minimalLoader.componentPaths['rhetor'];
                return {
                    loaderExists: true,
                    rhetorPath: rhetorPath || 'Not defined',
                    currentComponent: window.minimalLoader.currentComponent
                };
            } else {
                return { loaderExists: false };
            }
            """
        }],
        "preview": False
    })
    
    if loader_check['status'] == 'success':
        config = loader_check['result'].get('changes_applied', [{}])[0]
        print(f"   Loader config: {config}")

# Run trace
asyncio.run(trace_navigation())