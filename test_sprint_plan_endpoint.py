#!/usr/bin/env python3
"""Test script to verify sprint-plan endpoint is working"""

import requests
import json

# Test the sprint-plan endpoint
sprint_name = "Planning_Team_Workflow_UI_Sprint"
url = f"http://localhost:45012/api/v1/sprints/{sprint_name}/sprint-plan"

print(f"Testing GET {url}")

try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("Success! Sprint plan content:")
        print("-" * 50)
        print(data.get("content", "No content"))
        print("-" * 50)
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Failed to connect: {e}")
    print("Make sure TektonCore is running on port 45012")