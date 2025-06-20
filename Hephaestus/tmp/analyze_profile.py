#!/usr/bin/env python3
"""
Analyze Profile component for instrumentation
"""
import httpx
import asyncio

MCP_URL = "http://localhost:8088/api/mcp/v2/execute"

async def analyze_profile():
    async with httpx.AsyncClient(timeout=20.0) as client:
        print("=== Analyzing Profile Component ===\n")
        
        # Navigate to profile
        print("1. Navigating to Profile...")
        await client.post(MCP_URL, json={
            "tool_name": "ui_navigate",
            "arguments": {"component": "profile"}
        })
        
        await asyncio.sleep(2)
        
        # Capture profile
        print("\n2. Capturing Profile component...")
        capture_resp = await client.post(MCP_URL, json={
            "tool_name": "ui_capture",
            "arguments": {"area": "profile"}
        })
        
        result = capture_resp.json()
        if result['status'] == 'success':
            data = result['result']
            print(f"   HTML length: {data.get('html_length', 0)}")
            print(f"   Found with: {data.get('found_with_selector', 'Unknown')}")
            
            # Check semantic tags
            selectors = data.get('selectors_available', {})
            semantic_tags = {k: v for k, v in selectors.items() if 'data-tekton' in k and v > 0}
            
            if semantic_tags:
                print(f"\n   Existing semantic tags:")
                for tag, count in semantic_tags.items():
                    print(f"     {tag}: {count}")
            else:
                print("\n   No semantic tags found - good candidate for instrumentation!")
                
            # Check structure
            structure = data.get('structure', {})
            print(f"\n   Total elements: {structure.get('total_element_count', 0)}")
            
            # Run semantic analysis
            print("\n3. Running semantic analysis...")
            analysis_resp = await client.post(MCP_URL, json={
                "tool_name": "ui_semantic_analysis",
                "arguments": {"component": "profile"}
            })
            
            if analysis_resp.status_code == 200:
                analysis = analysis_resp.json()
                if analysis['status'] == 'success':
                    result = analysis['result']
                    print(f"   Semantic score: {result.get('score', 0)}/100")
                    
                    # Show missing elements
                    missing = result.get('missing_elements', [])
                    if missing:
                        print(f"\n   Missing semantic elements:")
                        for item in missing[:5]:  # Show first 5
                            print(f"     - {item}")
                else:
                    print(f"   Analysis failed: {analysis.get('error', 'Unknown')}")

asyncio.run(analyze_profile())