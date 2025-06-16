#\!/bin/bash
echo "Testing Terma API server..."
curl -s http://localhost:8765/health
echo -e "

Creating a new terminal session..."
curl -s -X POST http://localhost:8765/api/sessions -H "Content-Type: application/json" -d {shell_command:/bin/bash}
echo -e "

Listing active sessions..."
curl -s http://localhost:8765/api/sessions
echo -e "

Testing UI server..."
curl -s -I http://localhost:8766/terminal

