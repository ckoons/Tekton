import httpx
import json

# Test the knowledge/relationships endpoint with a proper POST
test_relationship = {
    "source_id": "test-source",
    "target_id": "test-target",
    "type": "test_relationship",
    "properties": {"test": "value"}
}

# Try different endpoints
endpoints = [
    "/api/v1/knowledge/relationships",
    "/api/v1/knowledge/relationships/relationships"
]

for endpoint in endpoints:
    print(f"\nTrying POST {endpoint}...")
    response = httpx.post(f'http://localhost:8005{endpoint}', 
                         json=test_relationship,
                         follow_redirects=True)
    print(f'Status: {response.status_code}')
    print(f'Response: {response.text[:200]}')

# Also check GET to see if the endpoint exists
print("\n\nChecking knowledge endpoints...")
response = httpx.get('http://localhost:8005/api/v1/knowledge/status')
print(f'Knowledge status: {response.status_code}')