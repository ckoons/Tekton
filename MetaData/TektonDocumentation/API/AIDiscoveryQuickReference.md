# AI Discovery Quick Reference for aish

## Essential Commands

```bash
# List all available AIs
ai-discover list

# Find best AI for a task
ai-discover best planning
ai-discover best code-analysis

# Get AI details
ai-discover info apollo-ai

# Test connections
ai-discover test

# JSON output for parsing
ai-discover --json list
```

## Name Resolution in aish

When user types: `echo "hello" | apollo`

Try in order:
1. Exact match: `id == "apollo"`
2. Name match: `name == "apollo"`  
3. Component match: `component == "apollo"`
4. Prefix match: `id.startswith("apollo-")`
5. Fuzzy match with suggestions

## Role-Based Routing

Support `@role` syntax:
```bash
echo "analyze this code" | @code-analysis
echo "plan this project" | @planning
echo "remember this" | @memory
```

## Python Integration Pattern

```python
import subprocess
import json
from typing import Optional, Dict

class AIResolver:
    def __init__(self):
        self._cache = {}
        self._cache_time = 0
        self._cache_ttl = 300  # 5 minutes
    
    async def discover_ais(self) -> List[Dict]:
        """Get all available AIs with caching."""
        if time.time() - self._cache_time > self._cache_ttl:
            result = subprocess.run(
                ['ai-discover', '--json', 'list'],
                capture_output=True,
                text=True
            )
            self._cache = json.loads(result.stdout)['ais']
            self._cache_time = time.time()
        return self._cache
    
    async def resolve_name(self, name: str) -> Optional[Dict]:
        """Resolve a user-provided name to an AI."""
        # Handle @role syntax
        if name.startswith('@'):
            role = name[1:]
            result = subprocess.run(
                ['ai-discover', '--json', 'best', role],
                capture_output=True,
                text=True
            )
            return json.loads(result.stdout)
        
        # Try to find by name
        ais = await self.discover_ais()
        
        # Exact matches
        for ai in ais:
            if name in [ai['id'], ai['name'], ai['component']]:
                return ai
        
        # Prefix match
        for ai in ais:
            if ai['id'].startswith(f"{name}-"):
                return ai
        
        return None
    
    def get_socket(self, ai: Dict) -> Tuple[str, int]:
        """Get socket info from AI discovery data."""
        return (ai['connection']['host'], ai['connection']['port'])
```

## Socket Communication

```python
import socket
import json

def send_to_ai(host: str, port: int, message: dict) -> dict:
    """Send message to AI specialist."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    
    # Send message
    sock.send(json.dumps(message).encode() + b'\n')
    
    # Read response
    response = b''
    while b'\n' not in response:
        response += sock.recv(4096)
    
    sock.close()
    return json.loads(response.decode().strip())

# Example usage
response = send_to_ai('localhost', 45010, {
    'type': 'chat',
    'content': 'Create a project plan',
    'max_tokens': 1000
})
print(response['content'])
```

## Error Handling

```python
async def safe_resolve(name: str) -> Optional[Dict]:
    """Resolve with helpful error messages."""
    ai = await resolve_name(name)
    
    if not ai:
        # Get available names for suggestion
        ais = await discover_ais()
        names = [ai['name'] for ai in ais if ai['status'] == 'healthy']
        
        print(f"Error: AI '{name}' not found.")
        print(f"Available AIs: {', '.join(names)}")
        print(f"Try: ai-discover list")
        return None
    
    if ai['status'] != 'healthy':
        print(f"Warning: {ai['name']} is {ai['status']}")
        # Try to find alternative
        alt = await find_alternative(ai['roles'][0])
        if alt:
            print(f"Using {alt['name']} instead")
            return alt
    
    return ai
```

## Complete aish Integration

```python
# In aish's socket_registry.py

class SocketRegistry:
    def __init__(self):
        self.resolver = AIResolver()
        self._direct_mappings = {}  # For optimization
    
    async def get_specialist_socket(self, name: str) -> Optional[Tuple[str, int]]:
        """Get socket for specialist using discovery."""
        # Check cache first
        if name in self._direct_mappings:
            ai_id = self._direct_mappings[name]
            # Verify still healthy
            ai = await self.resolver.resolve_name(ai_id)
            if ai and ai['status'] == 'healthy':
                return self.resolver.get_socket(ai)
        
        # Discover
        ai = await self.resolver.resolve_name(name)
        if ai and ai['status'] == 'healthy':
            # Cache for performance
            self._direct_mappings[name] = ai['id']
            return self.resolver.get_socket(ai)
        
        # Fallback to team-chat if configured
        if self.fallback_enabled:
            return await self.get_socket_info('team-chat')
        
        return None
```

## Available Roles

Standard roles for `@role` syntax:
- `@orchestration` - Complex task coordination
- `@code-analysis` - Code review and analysis
- `@planning` - Project and task planning
- `@knowledge-synthesis` - Research and reasoning
- `@memory` - Context and memory management
- `@messaging` - Communication tasks
- `@learning` - Adaptive learning tasks
- `@agent-coordination` - Multi-agent tasks

## Testing Your Integration

```bash
# Test discovery works
ai-discover list | grep healthy

# Test role resolution  
ai-discover best planning

# Test your client
echo "test" | your_aish_client apollo
echo "test" | your_aish_client @planning
echo "test" | your_aish_client non_existent  # Should show helpful error
```