import httpx
import json

# Test various relationship endpoints
endpoints = [
    "/api/v1/relationships",
    "/api/v1/relationships/relationships",
    "/api/v1/knowledge/relationships"
]

for endpoint in endpoints:
    try:
        response = httpx.get(f'http://localhost:8005{endpoint}')
        print(f'{endpoint}: {response.status_code}')
    except Exception as e:
        print(f'{endpoint}: ERROR - {e}')