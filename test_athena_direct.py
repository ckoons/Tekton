#!/usr/bin/env python3
"""Direct test of Athena API"""

import httpx
import json

# Test direct API call
url = "http://localhost:8005/api/v1/entities"
data = {
    "name": "Test Entity",
    "entity_type": "test",
    "properties": {"foo": "bar"}
}

print(f"Testing: POST {url}")
print(f"Data: {json.dumps(data, indent=2)}")

response = httpx.post(url, json=data)
print(f"\nStatus: {response.status_code}")
print(f"Response: {response.text}")

# Also test the root endpoint
print("\n\nTesting root endpoint:")
root = httpx.get("http://localhost:8005/")
print(f"Status: {root.status_code}")
print(f"Response: {root.text}")

# Test API root
print("\n\nTesting API root:")
api_root = httpx.get("http://localhost:8005/api")
print(f"Status: {api_root.status_code}")
print(f"Response: {api_root.text}")

# Test API v1 root
print("\n\nTesting API v1 root:")
api_v1 = httpx.get("http://localhost:8005/api/v1")
print(f"Status: {api_v1.status_code}")
print(f"Response: {api_v1.text}")