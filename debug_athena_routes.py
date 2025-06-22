import httpx
import json

# Test various potential endpoints
endpoints = [
    "/",
    "/api",
    "/api/v1",
    "/api/v1/entities",
    "/api/v1/entities/entities",  # Double entities due to router prefix
    "/api/v1/knowledge",
    "/api/v1/query",
    "/api/v1/discovery"
]

for endpoint in endpoints:
    try:
        response = httpx.get(f'http://localhost:8005{endpoint}')
        print(f'{endpoint}: {response.status_code}')
        if response.status_code == 200:
            print(f'  Response: {json.dumps(response.json(), indent=2)[:200]}...')
    except Exception as e:
        print(f'{endpoint}: ERROR - {e}')

# Try the discovery endpoint to see what routes are available
print("\nTrying discovery endpoint:")
response = httpx.get('http://localhost:8005/api/v1/discovery')
if response.status_code == 200:
    discovery = response.json()
    print("\nAvailable endpoints:")
    for endpoint in discovery.get('endpoints', []):
        print(f"  {endpoint['method']} {endpoint['path']}: {endpoint['description']}")