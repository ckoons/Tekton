# Merge Coordination Implementation Details

## Core Components

### 1. Merge Coordinator Service

```python
# tekton_core/services/merge_coordinator.py
class MergeCoordinatorService:
    """Background service for intelligent merge coordination"""
    
    def __init__(self):
        self.config = {
            "check_interval": 30,  # seconds
            "max_ai_rounds": 3,
            "confidence_threshold": 0.85,
            "worker_pattern": "sprint/worker_*",
            "main_branch": "main",
            "backup_branch": "main-backup"
        }
        
    async def start(self):
        """Main service loop"""
        while True:
            await self.check_ready_branches()
            await self.process_merge_queue()
            await asyncio.sleep(self.config["check_interval"])
```

### 2. Branch Readiness Detection

```python
class BranchMonitor:
    """Monitor worker branches for merge readiness"""
    
    def detect_ready_branches(self):
        """Multiple detection methods"""
        ready = []
        
        # Method 1: .merge_status file
        for branch in self.get_worker_branches():
            if self.has_merge_status_file(branch):
                ready.append(branch)
        
        # Method 2: Commit message signals
        for branch in self.get_worker_branches():
            if "READY_TO_MERGE" in self.get_last_commit_message(branch):
                ready.append(branch)
        
        # Method 3: AI announcement via aish
        inbox_ready = self.check_aish_announcements()
        ready.extend(inbox_ready)
        
        return list(set(ready))  # Deduplicate
```

### 3. AI Consensus Protocol

```python
class AIConsensusEngine:
    """Orchestrate AI team consensus for conflicts"""
    
    async def resolve_conflicts(self, conflicts):
        """Multi-round consensus building"""
        
        for round_num in range(self.max_rounds):
            # Present conflicts to team
            query = self.format_conflict_query(conflicts, round_num)
            responses = await self.team_chat(query)
            
            # Analyze consensus
            consensus = self.analyze_responses(responses)
            
            if consensus.confidence >= self.confidence_threshold:
                return consensus
            
            # Prepare for next round with feedback
            conflicts = self.incorporate_feedback(conflicts, responses)
        
        # No consensus - escalate
        return None
    
    def format_conflict_query(self, conflicts, round_num):
        """Format conflicts for AI discussion"""
        
        if round_num == 0:
            # First round - present raw conflicts
            return f"""MERGE CONFLICT RESOLUTION - Round 1
            
Conflicts to resolve:
{self.format_conflicts(conflicts)}

Please analyze and suggest optimal merge strategy.
Consider: functionality, performance, architecture, maintainability.
"""
        
        else:
            # Subsequent rounds - include previous feedback
            return f"""MERGE CONFLICT RESOLUTION - Round {round_num + 1}

Previous concerns:
{self.summarize_previous_round(conflicts)}

Remaining disagreements:
{self.highlight_disagreements(conflicts)}

Please work toward consensus or clearly state irreconcilable differences.
"""
```

### 4. Human Decision Interface

```python
class HumanDecisionInterface:
    """Simple, efficient human decision system"""
    
    def present_decision(self, conflict_package):
        """Terminal-based A/B interface"""
        
        # Option 1: Simple CLI
        print(self.format_header(conflict_package))
        
        for idx, conflict in enumerate(conflict_package.conflicts):
            print(f"\n[{idx+1}] File: {conflict.file}")
            print(self.format_comparison(conflict))
            
        # Collect all decisions at once
        decisions = input("Enter choices (e.g., 'ABB' for A,B,B): ")
        return self.parse_decisions(decisions)
    
    def format_comparison(self, conflict):
        """Side-by-side comparison with AI analysis"""
        
        return f"""
AI Analysis:
- {conflict.ai_preference} preferred by {conflict.ai_vote_count} AIs
- Reasoning: {conflict.ai_reasoning}

[A] Worker_1's approach:
{conflict.option_a.summary}
+ Pros: {', '.join(conflict.option_a.pros)}
- Cons: {', '.join(conflict.option_a.cons)}

[B] Worker_2's approach:  
{conflict.option_b.summary}
+ Pros: {', '.join(conflict.option_b.pros)}
- Cons: {', '.join(conflict.option_b.cons)}
"""
```

### 5. Learning System Integration

```python
class MergeLearningSystem:
    """Track and learn from merge decisions"""
    
    async def record_merge_outcome(self, merge_event):
        """Store in Engram for pattern learning"""
        
        learning_record = {
            "timestamp": datetime.now(),
            "conflict_type": self.classify_conflict(merge_event),
            "resolution_method": merge_event.resolution_method,
            "ai_consensus": merge_event.ai_consensus,
            "human_override": merge_event.human_decision,
            "outcome_metrics": await self.measure_outcome(merge_event)
        }
        
        # Store for pattern recognition
        await self.engram_store(
            namespace="merge_patterns",
            content=learning_record,
            embeddings=self.generate_embeddings(merge_event)
        )
    
    async def get_similar_merges(self, current_conflict):
        """Find similar past merges for guidance"""
        
        return await self.engram_search(
            namespace="merge_patterns",
            query=current_conflict,
            limit=5
        )
```

## Integration Points

### 1. With aish

```bash
# New aish commands
aish merge-coordinator start      # Start background service
aish merge-coordinator status     # Check queue and status
aish merge-coordinator decide     # Handle human escalations
aish merge-announce ready         # Worker announces readiness
```

### 2. With Git Hooks

```bash
# .git/hooks/post-commit
#!/bin/bash
# Auto-announce readiness based on commit message
if git log -1 --pretty=%B | grep -q "READY_TO_MERGE"; then
    aish merge-announce ready
fi
```

### 3. With Worker AI Scripts

```python
# In worker completion handler
def signal_merge_readiness(self):
    """Multiple ways to signal readiness"""
    
    # Method 1: File marker
    with open(".merge_status", "w") as f:
        f.write("READY_TO_MERGE")
    
    # Method 2: Git commit
    subprocess.run([
        "git", "commit", "--allow-empty", 
        "-m", "READY_TO_MERGE: Feature complete"
    ])
    
    # Method 3: aish announcement
    subprocess.run(["aish", "merge-announce", "ready"])
```

## Configuration Options

```yaml
# ~/.tekton/merge_coordinator.yaml
merge_coordinator:
  # Timing
  check_interval: 30
  merge_timeout: 300
  
  # AI Consensus
  max_ai_rounds: 3
  confidence_threshold: 0.85
  required_ai_votes: 3
  
  # Branches
  worker_pattern: "sprint/worker_*"
  main_branch: "main"
  backup_branch: "main-backup"
  
  # Human Interface
  escalation_timeout: 3600  # 1 hour
  decision_format: "simple"  # or "detailed"
  
  # Learning
  pattern_matching: true
  improvement_tracking: true
  
  # Notifications
  notify_on_conflict: true
  notify_on_merge: true
  notify_method: "terminal"  # or "web", "email"
```

## Testing Strategy

### 1. Simulation Environment

```python
# tests/test_merge_coordinator.py
class MergeCoordinatorTestSuite:
    """Comprehensive testing for merge scenarios"""
    
    def setup_test_workers(self):
        """Create multiple worker branches with conflicts"""
        
        # Worker 1: Optimization approach A
        self.create_worker_branch("worker_1", {
            "optimization.py": "cache_with_redis()",
            "config.py": "CACHE_TYPE = 'redis'"
        })
        
        # Worker 2: Optimization approach B
        self.create_worker_branch("worker_2", {
            "optimization.py": "cache_with_lru()",
            "config.py": "CACHE_TYPE = 'memory'"
        })
        
    async def test_ai_consensus_success(self):
        """Test successful AI consensus"""
        # Test implementation
        
    async def test_human_escalation(self):
        """Test human decision flow"""
        # Test implementation
```

### 2. Integration Tests

```bash
# Test full workflow
./run_merge_coordinator_test.sh

# Expected output:
# ✓ Worker detection
# ✓ Conflict identification  
# ✓ AI consensus (2 rounds)
# ✓ Merge application
# ✓ Learning system update
```

## Deployment Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Worker 1      │     │   Worker 2      │     │   Worker N      │
│ (Tekton-claude1)│     │ (Tekton-claude2)│     │ (Tekton-worker) │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         │                       ▼                       │
         │              ┌─────────────────┐             │
         └─────────────►│ Merge Coordinator│◄────────────┘
                        │  (tekton-core)   │
                        └────────┬────────┘
                                 │
                        ┌────────▼────────┐
                        │   AI Consensus  │
                        │  (team-chat)    │
                        └────────┬────────┘
                                 │
                        ┌────────▼────────┐
                        │ Human Decision  │
                        │   (if needed)   │
                        └────────┬────────┘
                                 │
                        ┌────────▼────────┐
                        │   Main Branch   │
                        │   (protected)   │
                        └─────────────────┘
```

## Monitoring and Metrics

```python
class MergeCoordinatorMetrics:
    """Track system performance"""
    
    metrics = {
        "total_merges": 0,
        "auto_merges": 0,
        "ai_resolved": 0,
        "human_resolved": 0,
        "average_merge_time": 0,
        "ai_consensus_rounds": [],
        "conflict_types": {},
        "learning_improvements": []
    }
    
    def dashboard(self):
        """Real-time merge coordination dashboard"""
        
        return f"""
╔═══════════════════════════════════════╗
║    Merge Coordinator Dashboard        ║
╠═══════════════════════════════════════╣
║ Active Workers:        {self.active_workers()}
║ Pending Merges:        {self.pending_count()}
║ In AI Discussion:      {self.in_discussion()}
║ Awaiting Human:        {self.human_queue()}
║                                       ║
║ Today's Stats:                        ║
║   Auto-merged:         {self.auto_today()}
║   AI Consensus:        {self.ai_today()}
║   Human Decisions:     {self.human_today()}
║   Avg Time:           {self.avg_time()}
║                                       ║
║ Success Rate:         {self.success_rate()}%
║ Learning Score:       {self.learning_score()}/100
╚═══════════════════════════════════════╝
"""
```