# Backend Landmarks Sprint Plan

## Executive Summary

This sprint implements a two-part approach: first analyzing the Tekton backend to understand its architecture, then implementing a landmark system based on those findings. This creates the persistent memory infrastructure needed for Companion Intelligences.

## Part 1: Backend Semantic Analysis (Week 1-2)

### Objectives

1. **Complete Code Analysis**
   - Parse every Python file in Tekton
   - Extract architectural patterns
   - Map dependencies and relationships
   - Identify key decision points

2. **Pattern Discovery**
   - Component boundaries and interfaces
   - Communication patterns (REST, WebSocket, MCP)
   - State management strategies
   - Error handling approaches
   - Performance-critical paths

3. **Landmark Identification**
   - Where are architectural decisions made?
   - What are the performance boundaries?
   - Where are the danger zones?
   - What are the key integration points?

### Methodology

#### 1.1 AST-Based Analysis
```python
# Example approach
import ast
import os

def analyze_python_file(filepath):
    with open(filepath, 'r') as f:
        tree = ast.parse(f.read())
    
    return {
        'classes': extract_classes(tree),
        'functions': extract_functions(tree),
        'decorators': extract_decorators(tree),
        'imports': extract_imports(tree),
        'patterns': identify_patterns(tree)
    }
```

#### 1.2 Dependency Mapping
- Import analysis
- Function call graphs
- Class inheritance trees
- Module relationships

#### 1.3 Pattern Recognition
- FastAPI endpoints → API boundaries
- WebSocket handlers → Real-time communication
- Error handlers → Danger zones
- Performance decorators → Critical paths

### Deliverables

1. **Backend Architecture Document**
   - Module structure
   - Component relationships
   - Communication flows
   - State management

2. **Landmark Location Map**
   ```python
   landmark_locations = {
       "architecture_decisions": [
           {"file": "hermes.py", "line": 45, "reason": "WebSocket vs REST choice"},
           {"file": "engram.py", "line": 120, "reason": "Graph DB selection"}
       ],
       "performance_boundaries": [...],
       "danger_zones": [...],
       "api_contracts": [...]
   }
   ```

3. **Pattern Catalog**
   - Common patterns found
   - Best practices identified
   - Anti-patterns to address

## Part 2: Landmark Implementation (Week 2-4)

### Objectives

1. **Design Landmark System**
   - Based on Part 1 findings
   - Flexible enough for future needs
   - Simple enough to maintain

2. **Build Infrastructure**
   - Storage system
   - Retrieval mechanisms
   - CI memory layer
   - Developer tools

3. **Instrument Backend**
   - Place landmarks throughout code
   - Document decisions
   - Mark boundaries
   - Enable CI understanding

### Landmark Specification

#### 2.1 Landmark Format
```python
@landmark(
    type="architecture_decision",
    id="uuid-here",
    title="Chose AsyncIO over Threading",
    context="Need to handle 1000+ concurrent connections",
    impacts=["performance", "scalability"],
    alternatives_considered=["threading", "multiprocessing"],
    decided_by="Casey",
    date="2024-03-15"
)
async def handle_connection(websocket):
    # Actual code here
```

#### 2.2 Landmark Types
Based on Part 1 findings, we'll define:
- `architecture_decision` - Why we built it this way
- `performance_boundary` - Critical performance paths
- `api_contract` - Interface commitments
- `danger_zone` - Risky/complex code
- `integration_point` - Where components connect
- `state_checkpoint` - State management points

#### 2.3 Storage System
```python
# landmarks/
# ├── registry.json          # Index of all landmarks
# ├── by-type/              # Organized by type
# ├── by-component/         # Organized by component
# └── by-date/             # Chronological order
```

### CI Memory System

#### 2.4 Conversation Persistence
```python
class CIMemory:
    def __init__(self, ci_name: str):
        self.ci_name = ci_name
        self.session_file = f"memory/{ci_name}/session.json"
        self.landmark_cache = self.load_relevant_landmarks()
    
    def remember(self, key: str, value: Any):
        """Store in working memory"""
        
    def recall(self, key: str) -> Any:
        """Retrieve from memory"""
        
    def save_session(self):
        """Persist for next session"""
```

#### 2.5 Multi-CI Protocol
```python
class CICoordinator:
    def __init__(self):
        self.registry = self.load_ci_registry()
    
    def route_query(self, query: str) -> str:
        """Route to appropriate CI based on domain"""
        
    def broadcast_landmark(self, landmark: Landmark):
        """Notify all CIs of new landmark"""
```

### Developer Experience

#### 2.6 CLI Tools
```bash
# Landmark management
tekton landmark add --type=decision --title="..." 
tekton landmark list --type=performance
tekton landmark search "WebSocket"

# CI interaction
tekton ci remember "We decided to use AsyncIO because..."
tekton ci ask "Why did we choose WebSockets?"
```

#### 2.7 IDE Integration
- Landmark annotations in code
- Hover for landmark details
- Quick landmark creation

## Timeline

### Week 1: Backend Analysis
- Days 1-2: Set up analysis framework
- Days 3-4: Analyze core components
- Day 5: Map dependencies

### Week 2: Complete Analysis & Design
- Days 1-2: Analyze remaining components
- Days 3-4: Document patterns and findings
- Day 5: Design landmark system

### Week 3: Build Infrastructure
- Days 1-2: Implement landmark core
- Days 3-4: Build CI memory system
- Day 5: Create developer tools

### Week 4: Instrument & Test
- Days 1-2: Place landmarks in code
- Days 3-4: Test CI interactions
- Day 5: Documentation and cleanup

## Risks and Mitigation

1. **Scope Creep**
   - Mitigation: Strict Part 1 → Part 2 progression
   - Focus on landmarks that enable Numa

2. **Analysis Paralysis**
   - Mitigation: Time-box Part 1 to 2 weeks max
   - "Good enough" analysis, improve iteratively

3. **Over-Engineering**
   - Mitigation: Start simple, file-based
   - Can add sophistication later

## Success Metrics

### Part 1 Metrics
- [ ] 100% of Python files analyzed
- [ ] All architectural patterns documented
- [ ] Landmark locations identified
- [ ] Dependency map complete

### Part 2 Metrics
- [ ] Landmark system operational
- [ ] 50+ landmarks placed in code
- [ ] CI memory persists across sessions
- [ ] Developer tools working

## Next Steps After Sprint

1. **Numa Implementation** - Use landmarks for context
2. **Component CIs** - Specialized CIs per component
3. **Knowledge Graph Integration** - Connect to Athena
4. **Voice Interaction** - Natural landmark creation

---

*This sprint transforms Tekton from a codebase into a living system with memory and understanding.*