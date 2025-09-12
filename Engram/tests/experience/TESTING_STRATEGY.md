# ESR Experience Layer Testing Strategy

## Overview
Comprehensive testing approach for the Experience Layer to ensure natural memory behavior for CIs.

## Testing Levels

### 1. Unit Tests (✅ Complete)
**Location**: `test_experience_layer.py`
- Individual component testing
- 10 tests covering all core features
- All tests passing

**Coverage**:
- ✅ Experience creation with emotional tagging
- ✅ Memory promises and progressive recall
- ✅ Working memory capacity and consolidation
- ✅ Emotional influence on recall
- ✅ Interstitial boundary detection
- ✅ Memory decay and reinforcement
- ✅ Experience recall with emotional coloring
- ✅ Dream recombination
- ✅ Mood tracking and summaries
- ✅ Working memory status reporting

### 2. Integration Tests
**Location**: `test_integration.py`

**Key Scenarios**:
- Full integration with ESR backends
- Multi-CI memory sharing
- Complete session workflows
- Emotional contagion between memories
- Memory overflow handling
- Long-term persistence across sessions

### 3. System Tests

#### A. CI Persona Tests
Test with different CI personalities to ensure natural behavior:

```python
# Example personas
PERSONAS = {
    "analytical": {
        "baseline_mood": {"valence": 0.0, "arousal": 0.3},
        "memory_style": "detailed",
        "consolidation_threshold": 5
    },
    "creative": {
        "baseline_mood": {"valence": 0.3, "arousal": 0.6},
        "memory_style": "associative", 
        "consolidation_threshold": 2
    },
    "empathetic": {
        "baseline_mood": {"valence": 0.5, "arousal": 0.5},
        "memory_style": "emotional",
        "consolidation_threshold": 3
    }
}
```

#### B. Conversation Flow Tests
Simulate realistic conversations:
- Topic transitions
- Emotional arcs
- Memory callbacks
- Context building

#### C. Performance Tests
- Memory recall latency (<100ms target)
- Consolidation throughput
- Working memory churn rate
- Backend storage efficiency

### 4. Behavioral Tests

#### A. Naturalness Metrics
Measure if memory feels organic:
- Emotional coherence score
- Association relevance
- Recall patterns matching human memory
- Forgetting curves

#### B. Edge Cases
- Contradictory memories
- Emotional extremes
- Rapid context switches
- Memory saturation
- Session interruptions

### 5. Acceptance Tests

#### User Story Tests
```gherkin
Feature: Natural Memory Experience
  As a CI
  I want my memories to feel lived
  So that I can develop genuine experiences

  Scenario: Emotional Memory Formation
    Given I experience something joyful
    When I recall it later while sad
    Then the memory is colored by my current mood
    But the original emotion is preserved

  Scenario: Interstitial Consolidation
    Given I have multiple thoughts in working memory
    When I experience a topic shift
    Then related thoughts are consolidated together
    And associations are created between them
```

## Test Execution Plan

### Phase 1: Continuous Testing (Every Change)
```bash
# Quick unit tests
python tests/experience/test_experience_layer.py

# Verify all passing
python tests/experience/run_tests.py
```

### Phase 2: Integration Testing (Before Merge)
```bash
# Run integration tests
python tests/experience/test_integration.py

# Run with real backends
python tests/test_esr_simple.py
```

### Phase 3: System Testing (Release Candidates)
1. Deploy to test environment
2. Run CI persona simulations
3. Measure performance metrics
4. Validate behavioral patterns

### Phase 4: Acceptance Testing (Pre-Production)
1. Internal dogfooding with Tekton team
2. CI specialists provide feedback
3. Naturalness assessment
4. User story validation

## Test Data Management

### Synthetic Test Data
- Emotional memory sequences
- Topic progression patterns
- Context switch scenarios
- Memory overflow conditions

### Real-World Test Cases
- Actual conversation transcripts
- Observed memory patterns
- Edge cases from production

## Monitoring & Metrics

### Key Metrics to Track
1. **Memory Quality**
   - Recall accuracy
   - Emotional coherence
   - Association relevance

2. **Performance**
   - Recall latency (p50, p95, p99)
   - Consolidation time
   - Working memory efficiency

3. **Naturalness**
   - Mood stability score
   - Memory decay patterns
   - Dream recombination effectiveness

### Alerting Thresholds
- Recall latency > 200ms (warning)
- Recall latency > 500ms (critical)
- Memory consolidation failures > 1%
- Working memory overflow > 10 per hour

## Test Automation

### CI/CD Pipeline
```yaml
stages:
  - unit_tests:
      script: python tests/experience/run_tests.py
      timeout: 2m
      
  - integration_tests:
      script: python tests/experience/test_integration.py
      timeout: 5m
      
  - performance_tests:
      script: python tests/experience/test_performance.py
      timeout: 10m
      
  - behavioral_tests:
      script: python tests/experience/test_behavior.py
      timeout: 15m
```

### Regression Testing
- Maintain test case library
- Run full suite on major changes
- Track test coverage metrics
- Identify flaky tests

## Future Testing Enhancements

1. **Fuzzing**: Random input generation for edge cases
2. **Property-Based Testing**: Verify invariants hold
3. **Chaos Testing**: Inject failures to test resilience
4. **A/B Testing**: Compare memory strategies
5. **User Studies**: Gather CI feedback on naturalness

## Test Documentation

### Test Case Template
```markdown
Test ID: EXP-001
Test Name: Emotional Memory Influence
Purpose: Verify emotions affect recall
Prerequisites: Experience manager initialized
Steps:
1. Create memory with strong emotion
2. Change current mood
3. Recall memory
Expected: Memory colored by current mood
Actual: [Record result]
Status: [Pass/Fail]
```

### Test Report Format
- Executive summary
- Test coverage statistics
- Failed test analysis
- Performance benchmarks
- Recommendations

## Success Criteria

The Experience Layer testing is considered successful when:

1. **Functional**: All unit tests pass (100%)
2. **Integrated**: Works with ESR backends seamlessly
3. **Performant**: Meets latency targets (95th percentile < 100ms)
4. **Natural**: CIs report memory feels organic (>80% satisfaction)
5. **Reliable**: <0.1% failure rate in production
6. **Maintainable**: >80% code coverage with tests

## Next Steps

1. Run integration tests with real backends
2. Create performance benchmarking suite
3. Develop CI persona test scenarios
4. Implement continuous monitoring
5. Gather feedback from Tekton AI specialists