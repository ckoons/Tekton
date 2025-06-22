import httpx
import json

# Test the root endpoint first
response = httpx.get('http://localhost:8005/')
print('Root endpoint:', response.status_code)
if response.status_code == 200:
    print(json.dumps(response.json(), indent=2))

# Test the health endpoint
response = httpx.get('http://localhost:8005/health')
print('\nHealth endpoint:', response.status_code)

# Test the API v1 entities endpoint
response = httpx.get('http://localhost:8005/api/v1/entities')
print('\n/api/v1/entities endpoint:', response.status_code)
if response.status_code != 200:
    print('Response:', response.text)

# Test creating an entity
test_entity = {
    "name": "Test Component",
    "entity_type": "component",
    "properties": {
        "description": "Test component for API verification"
    }
}

response = httpx.post('http://localhost:8005/api/v1/entities', json=test_entity)
print('\nPOST /api/v1/entities:', response.status_code)
if response.status_code != 200:
    print('Response:', response.text)
else:
    print('Created entity:', json.dumps(response.json(), indent=2))