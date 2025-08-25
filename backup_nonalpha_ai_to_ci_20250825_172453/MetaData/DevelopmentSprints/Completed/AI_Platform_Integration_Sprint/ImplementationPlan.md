# CI Platform Integration Sprint - Implementation Plan

## Overview

This document provides detailed, step-by-step implementation instructions for integrating CI specialists throughout the Tekton platform. Follow these steps sequentially for best results.

## Pre-Implementation Checklist

- [ ] Review `SprintPlan.md` and `ArchitecturalDecisions.md`
- [ ] Ensure Anthropic API key is configured
- [ ] Verify socket registry is functioning
- [ ] Backup current Tekton state

## Phase 1: Foundation Setup (Days 1-3)

### 1.1 Create Environment Configuration

**Location**: `.tekton/.env.tekton`

```bash
# Add CI control flag
echo "export TEKTON_REGISTER_AI=false" >> .tekton/.env.tekton
echo "export TEKTON_AI_DEBUG=false" >> .tekton/.env.tekton
echo "export TEKTON_AI_AUTO_RESTART=true" >> .tekton/.env.tekton
```

### 1.2 Update Port Assignments

**File**: `MetaData/TektonDocumentation/port_assignments.md`

Add entries:
```markdown
| Numa     | 8016 | Platform CI Mentor    | All Component Access |
| Noesis   | 8015 | Discovery CI          | Future Sprint        |
```

### 1.3 Create CI Registry Client

**File**: `shared_lib/AIRegistryClient.py`

Key features:
- Async HTTP client for Rhetor API
- File-based fallback mechanism
- Register/deregister CI methods
- Query CI status methods
- Health check integration

```python
class AIRegistryClient:
    def __init__(self):
        self.rhetor_url = "http://localhost:8011"
        self.registry_file = ".tekton/ai_registry.json"
    
    async def register_ai(self, component_name, socket_name, port):
        # Try HTTP first, fallback to file
        pass
    
    async def deregister_ai(self, component_name):
        # Try HTTP first, fallback to file
        pass
    
    async def get_ai_status(self):
        # Read from HTTP or file
        pass
```

### 1.4 Create CI Management Utilities

#### tekton_ai_launcher.py

**Location**: `EnhancedTools/tekton_ai_launcher.py`

Responsibilities:
- Check TEKTON_REGISTER_AI flag
- Launch CI processes for registered components
- Update socket registry
- Handle errors gracefully

Key logic:
```python
1. Read environment flag
2. Get list of running components from enhanced_tekton_status
3. For each component with CI support:
   - Launch CI process
   - Register in socket registry
   - Log success/failure
4. Launch Numa last (after all components)
```

#### tekton_ai_killer.py

**Location**: `EnhancedTools/tekton_ai_killer.py`

Responsibilities:
- Terminate all CI processes
- Deregister from socket registry
- Clean shutdown sequence
- Kill Numa first (before components)

#### tekton_ai_status.py

**Location**: `EnhancedTools/tekton_ai_status.py`

Responsibilities:
- Show all registered CIs
- Display health status
- Show last activity time
- Highlight unresponsive CIs

### 1.5 Create Numa Component

**Location**: `Numa/`

Structure:
```
Numa/
├── main.py
├── numa_ai.py
├── numa_chat.py
├── numa_team_chat.py
├── static/
│   ├── numa_chat.html
│   └── numa_team_chat.html
└── requirements.txt
```

**main.py** features:
- FastAPI application on port 8016
- Health check endpoint
- Chat interface endpoints
- Team chat interface
- Hermes registration

**numa_ai.py** features:
- Platform mentor personality
- Access to all component sockets
- Coaching and guidance prompts
- Socket polling loop

### 1.6 Create Noesis Placeholder

**Location**: `Noesis/`

Minimal structure:
- Basic FastAPI app on port 8015
- Health endpoint
- Placeholder chat interface
- "Coming Soon" messaging

## Phase 2: Integration (Days 4-6)

### 2.1 Update Enhanced Tekton Launcher

**File**: `EnhancedTools/enhanced_tekton_launcher.py`

Modifications:
```python
# After all components are healthy
if os.getenv('TEKTON_REGISTER_AI', 'false').lower() == 'true':
    print("\n🤖 Launching CI Specialists...")
    subprocess.run([sys.executable, 'EnhancedTools/tekton_ai_launcher.py'])
```

Add Numa and Noesis to component list:
```python
components = [
    # ... existing components ...
    {"name": "Numa", "path": "Numa", "port": 8016},
    {"name": "Noesis", "path": "Noesis", "port": 8015},
]
```

### 2.2 Update Enhanced Tekton Killer

**File**: `EnhancedTools/enhanced_tekton_killer.py`

Modifications:
```python
# Before killing components
if os.getenv('TEKTON_REGISTER_AI', 'false').lower() == 'true':
    print("\n🤖 Terminating CI Specialists...")
    subprocess.run([sys.executable, 'EnhancedTools/tekton_ai_killer.py'])
```

### 2.3 Update Enhanced Tekton Status

**File**: `EnhancedTools/enhanced_tekton_status.py`

Add CI section:
```python
# After component status
if os.getenv('TEKTON_REGISTER_AI', 'false').lower() == 'true':
    print("\n🤖 CI Specialist Status:")
    subprocess.run([sys.executable, 'EnhancedTools/tekton_ai_status.py'])
```

### 2.4 Implement Health Monitoring

**File**: `EnhancedTools/ai_health_monitor.py`

Features:
- Parse debug logs for activity
- Track last spoke timestamps
- Send ESC character after timeout
- Auto-restart unresponsive CIs
- Log all health events

Health check sequence:
```python
1. Check last activity timestamp
2. If > 5 minutes:
   - Send ESC to socket
   - Wait 30 seconds
   - If no response:
     - Mark as unresponsive
     - Attempt restart if enabled
```

## Phase 3: CI Implementation (Days 7-10)

### 3.1 Create Base CI Worker Class

**File**: `shared_lib/AISpecialistWorker.py`

Core features:
```python
class AISpecialistWorker:
    def __init__(self, component_name, socket_name, personality):
        self.component_name = component_name
        self.socket_name = socket_name
        self.personality = personality
        self.llm_client = None
        
    async def start(self):
        # Main polling loop
        pass
        
    async def process_message(self, message):
        # Handle incoming messages
        pass
        
    async def send_to_llm(self, prompt):
        # LLM integration
        pass
```

### 3.2 Implement Component CIs

#### Rhetor AI
- Orchestrator personality
- Team chat moderation
- Component coordination

#### Apollo AI
- Executive coordinator role
- Strategic analysis
- Decision support

#### Numa AI
- Platform mentor role
- Coaching prompts
- Cross-component visibility

### 3.3 LLM Integration

**Model Configuration**:
```python
DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
PREMIUM_MODEL = "claude-3-5-opus-20241022"  # When available
```

**Prompt Templates**:
- Component-specific system prompts
- Coaching/mentoring templates for Numa
- Team chat moderation guidelines

## Phase 4: UI Integration (Days 11-12)

### 4.1 Update Hephaestus Navigation

**File**: `Hephaestus/index.html`

Add Numa as first tab:
```javascript
// Navigation order
const navOrder = [
    'numa',      // Platform CI (NEW - FIRST)
    'rhetor',    // Orchestrator
    'apollo',    // Executive
    // ... rest of components ...
    'noesis',    // Discovery (after sophia)
];
```

### 4.2 Update Rhetor UI

Add Numa integration:
- Include in component lists
- Add to team chat participants
- Update socket connections

### 4.3 Update Team Chat Display

Show CI participants:
- Different styling for CI vs human
- Activity indicators
- Health status badges

## Phase 5: Testing & Documentation (Days 13-14)

### 5.1 Unit Tests

Create tests for:
- CI registry client
- Management utilities
- Health monitoring
- Base worker class

### 5.2 Integration Tests

Test scenarios:
- Full startup with CIs
- Component restart resilience
- CI crash recovery
- Team chat with multiple CIs

### 5.3 Performance Tests

Measure:
- Startup time impact
- Memory usage per AI
- CPU usage patterns
- Socket throughput

### 5.4 Documentation Updates

Update:
- CI Socket Registry Guide
- Component documentation
- Troubleshooting guide
- API documentation

## Rollout Strategy

### Stage 1: Development Testing
1. Enable on single developer machine
2. Test with Rhetor, Apollo, Numa only
3. Monitor logs and performance
4. Fix any critical issues

### Stage 2: Expanded Testing
1. Enable for all core components
2. Test team chat extensively
3. Validate health monitoring
4. Measure API costs

### Stage 3: Full Deployment
1. Enable for all components
2. Monitor for 24-48 hours
3. Collect performance metrics
4. Document any issues

## Troubleshooting Guide

### Common Issues

**AIs not starting**:
- Check TEKTON_REGISTER_AI flag
- Verify API keys configured
- Check socket registry access
- Review error logs

**AI unresponsive**:
- Check debug logs for activity
- Verify socket connectivity
- Manual restart if needed
- Check for LLM API issues

**High API costs**:
- Monitor usage in Penia
- Consider local models
- Adjust polling frequency
- Implement caching

## Post-Sprint Tasks

1. Gather performance metrics
2. Calculate API costs
3. Document lessons learned
4. Plan next CI features
5. Consider additional CI specialists

## Success Validation

Run through this checklist:

- [ ] All utilities created and tested
- [ ] Numa launches after components
- [ ] Numa terminates before components
- [ ] Health monitoring detects issues
- [ ] Auto-restart works correctly
- [ ] Team chat includes all CIs
- [ ] UI shows Numa first
- [ ] No performance regression
- [ ] API costs acceptable
- [ ] Documentation complete

This implementation plan provides a clear path to successfully integrate CI specialists throughout the Tekton platform.