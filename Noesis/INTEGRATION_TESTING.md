# Noesis-Sophia Integration Testing

This document describes the comprehensive testing framework for validating end-to-end theory-experiment workflows between Noesis and Sophia.

## Overview

The integration testing framework validates complete collaborative workflows between the Noesis theoretical analysis system and the Sophia experimental platform. These tests ensure that:

- Theoretical predictions from Noesis can be properly converted to experimental hypotheses
- Sophia experiments can validate or refute Noesis theories
- Results flow correctly between systems for iterative refinement
- Real-time monitoring and intervention protocols work correctly
- Multi-scale analysis leads to proper scaling experiments

## Test Structure

### Test Modules

1. **`test_noesis_sophia_integration.py`**
   - Core integration between Noesis and Sophia components
   - Theory validation protocol creation and management
   - Hypothesis generation from different analysis types
   - Experiment result interpretation and validation

2. **`test_theory_experiment_protocols.py`**
   - REST API endpoint testing for Sophia integration
   - Protocol lifecycle management
   - Error handling and edge cases
   - Concurrent protocol execution

3. **`test_end_to_end_workflows.py`**
   - Complete realistic workflows from discovery to validation
   - Real-time monitoring to intervention scenarios
   - Multi-scale synthesis to scaling law experiments
   - Iterative theory refinement cycles

### Key Test Classes

#### TestNoesisSophiaIntegration
Tests core integration functionality:
- Theory validation protocol creation
- Hypothesis generation from catastrophe/regime/manifold analysis
- Experiment result interpretation
- Iterative refinement cycle management

#### TestCompleteWorkflows  
Tests realistic end-to-end scenarios:
- `test_discovery_to_validation_workflow()`: Pattern discovery → theory → validation
- `test_real_time_monitoring_to_intervention_workflow()`: Live monitoring → critical detection → intervention
- `test_multi_scale_synthesis_to_scaling_experiments()`: Multi-scale analysis → scaling laws → validation experiments
- `test_iterative_theory_refinement_workflow()`: Theory → experiment → refinement cycles

## Running Tests

### Quick Workflow Validation
```bash
# Run key workflow tests only
./run_integration_tests.py --workflows-only
```

### Full Integration Test Suite
```bash
# Run all integration tests
./run_integration_tests.py

# Run specific module
./run_integration_tests.py --module test_end_to_end_workflows.py
```

### Individual Test Execution
```bash
# Run with pytest for detailed output
python -m pytest test_noesis_sophia_integration.py -v
python -m pytest test_theory_experiment_protocols.py -v
python -m pytest test_end_to_end_workflows.py -v
```

## Test Scenarios

### 1. Discovery to Validation Workflow

**Scenario**: Analyze collective CI data, discover patterns, generate theory, validate experimentally

**Steps**:
1. Analyze collective CI data with manifold and dynamics analyzers
2. Generate theoretical predictions based on discovered patterns
3. Create theory validation protocol with Sophia
4. Execute experiment in Sophia
5. Interpret results and validate theory

**Expected Outcome**: Theory partially or fully validated with actionable insights

### 2. Real-Time Monitoring to Intervention

**Scenario**: Monitor live system, detect critical transition, trigger intervention

**Steps**:
1. Start real-time theoretical monitoring
2. Detect early warning signals of critical transition
3. Generate intervention hypothesis
4. Create urgent experimental intervention protocol
5. Execute intervention experiment
6. Validate intervention effectiveness

**Expected Outcome**: Successful detection and intervention preventing system collapse

### 3. Multi-Scale Synthesis to Scaling Experiments

**Scenario**: Analyze systems at multiple scales, discover scaling laws, validate experimentally

**Steps**:
1. Generate multi-scale collective CI data (12 to 50,000 agents)
2. Perform synthesis analysis to discover scaling relationships
3. Generate scaling law hypothesis (e.g., D(N) = a * N^β)
4. Create validation experiments at intermediate scales
5. Execute scaling experiments
6. Validate scaling law predictions

**Expected Outcome**: Scaling law validated across multiple system sizes

### 4. Iterative Theory Refinement

**Scenario**: Refine theory through multiple experiment cycles

**Steps**:
1. Start with initial theory
2. Create iterative refinement cycle
3. For each iteration:
   - Create experiment from current theory
   - Execute experiment
   - Interpret results
   - Apply refinements to theory
4. Evaluate refinement progress

**Expected Outcome**: Theory progressively improves through iterations

## Test Data and Mocking

### Realistic Test Data Generation

The tests use sophisticated mock data that simulates realistic collective CI behavior:

```python
# Example: Collective CI data with phase transitions
collective_data = {
    "time_series": np.ndarray,     # Shape: (300, 500) - 300 timesteps, 500 features
    "collective_states": np.ndarray,  # Sampled states for manifold analysis
    "metadata": {
        "n_agents": 100,
        "n_features_per_agent": 5,
        "phases": ["independent", "group_coordination", "global_coordination"]
    }
}
```

### Sophia Integration Mocking

Sophia HTTP client interactions are mocked to simulate:
- Successful experiment creation
- Experiment execution with realistic results
- Various error conditions (timeouts, failures)
- Progressive result refinement

```python
# Mock Sophia experiment results
sophia_bridge.client.get.return_value.json.return_value = {
    "experiment_id": "exp_001",
    "metrics_summary": {
        "intrinsic_dimension": {"mean": 5.1, "std": 0.3},
        "regime_stability": {"mean": 0.87, "std": 0.04}
    }
}
```

## Validation Criteria

### Protocol Creation
- ✅ Theory validation protocols created successfully
- ✅ Experiment designs contain appropriate metrics
- ✅ Confidence intervals properly converted
- ✅ Protocol IDs unique and trackable

### Hypothesis Generation  
- ✅ Hypotheses generated from different analysis types
- ✅ Experiment designs match hypothesis requirements
- ✅ Key predictions extracted correctly
- ✅ Source analysis properly attributed

### Result Interpretation
- ✅ Experimental results correctly compared to theory
- ✅ Validation status determined accurately
- ✅ Insights generated from comparisons
- ✅ Refinement suggestions provided

### Workflow Continuity
- ✅ Data flows correctly between workflow steps
- ✅ Protocols persist and remain accessible
- ✅ Error recovery maintains workflow state
- ✅ Concurrent workflows don't interfere

## Error Handling Tests

### Network Failures
- Sophia API timeouts and connection errors
- Partial response handling
- Graceful degradation when Sophia unavailable

### Data Quality Issues
- Malformed analysis results
- Missing required fields
- Invalid confidence intervals
- Extreme or edge case values

### Concurrent Access
- Multiple protocols for same theory
- Concurrent refinement cycles
- Protocol conflict resolution
- Memory management with many protocols

## Performance Validation

### Response Times
- Theory validation protocol creation: < 2 seconds
- Hypothesis generation: < 1 second
- Result interpretation: < 3 seconds
- Full workflow completion: < 30 seconds

### Memory Usage
- Protocol storage scales linearly
- No memory leaks during long workflows
- Proper cleanup after workflow completion

### Concurrent Load
- Multiple workflows execute without interference
- Protocol isolation maintained
- Shared resources properly managed

## Integration Points Tested

### Noesis → Sophia
- Theoretical predictions → Experiment hypotheses
- Analysis results → Experimental designs
- Confidence intervals → Validation criteria
- Real-time insights → Intervention protocols

### Sophia → Noesis
- Experiment results → Theory validation
- Metrics → Comparison analysis
- Observations → Refinement suggestions
- Status updates → Workflow progression

### Bidirectional
- Iterative refinement cycles
- Real-time monitoring protocols
- Multi-experiment validation
- Cross-system error propagation

## Expected Test Results

### Success Criteria
- **95%+ test pass rate**: Nearly all integration tests should pass
- **Complete workflow coverage**: All major workflows validated
- **Error handling verified**: Graceful handling of common failure modes
- **Performance targets met**: Response times within acceptable bounds

### Key Metrics
- Protocol creation success rate: > 98%
- Theory validation accuracy: > 90%
- Workflow completion rate: > 95%
- Error recovery success: > 90%

## Troubleshooting Test Failures

### Common Issues

1. **Import Errors**
   - Ensure all Noesis components are in Python path
   - Check for circular import dependencies
   - Verify mock objects are properly configured

2. **Async Test Failures**
   - Ensure proper `await` usage in async tests
   - Check for race conditions in concurrent tests
   - Verify cleanup in test teardown

3. **Mock Configuration**
   - Ensure Sophia client mocks return expected data
   - Check for proper mock reset between tests
   - Verify side effects are configured correctly

4. **Data Generation**
   - Check numpy random seed for reproducible tests
   - Ensure test data has realistic structure
   - Verify data dimensions match expected formats

### Debug Tools

```bash
# Run with verbose output
python -m pytest test_end_to_end_workflows.py::TestCompleteWorkflows::test_discovery_to_validation_workflow -v -s

# Run with debugger on failure
python -m pytest --pdb test_integration.py

# Run specific workflow test
./run_integration_tests.py --workflows-only
```

## Continuous Integration

### Automated Testing
The integration tests should be run:
- On every commit to integration branches
- Before merging pull requests
- Nightly for full regression testing
- Before releases for validation

### Test Environment
- Mock Sophia instance for consistent testing
- Isolated test data that doesn't affect production
- Proper cleanup after test runs
- Reproducible random seeds for deterministic results

## Future Extensions

### Additional Workflows
- **Cross-system visualization**: Test shared visualization components
- **Data streaming integration**: Test real-time data flow
- **Error propagation**: Test cross-system error handling
- **Performance optimization**: Test scaling behavior

### Advanced Scenarios
- **Multi-modal analysis**: Combine different analysis types
- **Adaptive experiments**: Dynamic experiment modification
- **Federated learning**: Multi-system collaborative learning
- **Real-time adaptation**: Live system modification

This comprehensive testing framework ensures robust integration between Noesis and Sophia, validating that theoretical insights can be effectively translated into experimental validation and system improvement.