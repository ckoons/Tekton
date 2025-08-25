#!/bin/bash
# Quick test script for SSE streaming endpoints using curl

echo "=== Testing Individual Specialist Streaming ==="
echo "Streaming from apollo-ai..."
echo ""

# Test individual specialist streaming
curl -N -X GET "http://localhost:8003/api/chat/apollo-ai/stream?message=Tell%20me%20a%20joke&include_metadata=true" \
  -H "Accept: text/event-stream"

echo ""
echo ""
echo "=== Testing Team Streaming (POST) ==="
echo "Streaming from all Greek Chorus CIs..."
echo ""

# Test team streaming
curl -N -X POST "http://localhost:8003/api/chat/team/stream" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "What is wisdom?",
    "include_metadata": true,
    "temperature": 0.7,
    "max_tokens": 100
  }'