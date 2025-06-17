import asyncio
import httpx
import json

async def test_batch():
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "http://localhost:8088/api/mcp/v2/execute",
            json={
                "tool_name": "ui_batch",
                "arguments": {
                    "area": "hephaestus",
                    "operations": [
                        {"action": "add_class", "selector": ".nav-item", "class": "test-class"},
                        {"action": "remove_class", "selector": ".nav-item", "class": "test-class"}
                    ],
                    "atomic": False
                }
            }
        )
        result = response.json()
        print(json.dumps(result, indent=2))

asyncio.run(test_batch())