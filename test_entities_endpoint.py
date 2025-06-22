import httpx
import json

# Test the entities endpoint with follow redirects
print("Testing with redirect following...")

# GET entities
response = httpx.get('http://localhost:8005/api/v1/entities/entities', follow_redirects=True)
print(f'GET /api/v1/entities/entities (with redirects): {response.status_code}')
if response.status_code == 200:
    print(f'Response: {json.dumps(response.json(), indent=2)}')

# Now test creating an entity
print("\nTesting entity creation...")
test_entity = {
    "name": "Test Component",
    "entity_type": "component",  # Changed from "type" to "entity_type"
    "properties": {
        "description": "Test component for API verification"
    }
}

response = httpx.post('http://localhost:8005/api/v1/entities/entities', 
                     json=test_entity,
                     follow_redirects=True)
print(f'POST /api/v1/entities/entities: {response.status_code}')
if response.status_code != 200:
    print(f'Response: {response.text}')
else:
    print(f'Created entity: {json.dumps(response.json(), indent=2)}')