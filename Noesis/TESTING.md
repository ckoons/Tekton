# Noesis Mathematical Framework - Testing Documentation

This document describes the comprehensive testing framework for the Noesis mathematical analysis components.

## Test Structure

The testing framework consists of several specialized test suites:

### 1. Core Integration Tests (`test_mathematical_framework.py`)
Tests the integration and functionality of all mathematical framework components:

- **Base Framework Validation**: Tests data validation, normalization, and utility functions
- **Manifold Analysis Integration**: Tests dimensional reduction and topology analysis
- **Dynamics Analysis Integration**: Tests SLDS model fitting and regime identification
- **Catastrophe Analysis Integration**: Tests critical transition detection
- **Synthesis Analysis Integration**: Tests universal principle extraction
- **Error Handling**: Tests graceful handling of invalid inputs
- **End-to-End Pipeline**: Tests complete analysis workflow

### 2. Edge Cases & Stress Tests (`test_framework_edge_cases.py`)
Tests framework robustness under challenging conditions:

- **Edge Case Data**: Small datasets, high dimensions, constant data, extreme values
- **Numerical Stability**: Ill-conditioned matrices, multi-scale data, near-singular cases
- **Memory & Performance**: Large dataset processing, memory leak detection
- **Concurrent Operations**: Thread safety and parallel execution

### 3. Test Infrastructure Validation (`validate_tests.py`)
Validates the testing infrastructure itself:

- **Import Validation**: Ensures all required modules can be imported
- **Basic Functionality**: Tests core framework operations
- **Async Operations**: Validates asynchronous execution
- **Data Structures**: Tests serialization and data handling

### 4. Comprehensive Test Runner (`run_all_tests.py`)
Orchestrates all test suites and generates detailed reports:

- **Automated Execution**: Runs all test suites in sequence
- **Detailed Reporting**: Generates JSON reports with metrics
- **Performance Monitoring**: Tracks execution time and resource usage
- **Status Summarization**: Provides clear pass/fail assessment

## Running Tests

### Quick Validation
First, validate that the test infrastructure is working:

```bash
python validate_tests.py
```

This will check:
- ✅ All required modules can be imported
- ✅ Basic framework functionality works
- ✅ Async operations execute correctly
- ✅ Data structures serialize properly

### Full Test Suite
Run the comprehensive test suite:

```bash
python run_all_tests.py
```

This executes all test suites and generates a detailed report.

### Individual Test Suites
Run specific test components:

```bash
# Core integration tests
python -m asyncio test_mathematical_framework.py

# Edge cases and stress tests  
python -m asyncio test_framework_edge_cases.py
```

## Test Coverage

### Mathematical Components Tested

1. **Base Framework** (`noesis.core.theoretical.base`)
   - ✅ Data validation and normalization
   - ✅ Distance computation and dimensionality estimation
   - ✅ Numerical stability checks
   - ✅ Result preparation and serialization

2. **Manifold Analysis** (`noesis.core.theoretical.manifold`)
   - ✅ PCA-based dimensional reduction
   - ✅ Intrinsic dimension estimation
   - ✅ Topology metrics computation
   - ✅ Trajectory pattern analysis
   - ✅ Alternative embedding methods (t-SNE, LLE)

3. **Dynamics Analysis** (`noesis.core.theoretical.dynamics`)
   - ✅ SLDS model initialization and fitting
   - ✅ EM algorithm convergence
   - ✅ Regime identification and Viterbi decoding
   - ✅ Stability analysis and transition prediction

4. **Catastrophe Analysis** (`noesis.core.theoretical.catastrophe`)
   - ✅ Critical transition detection
   - ✅ Early warning signal computation
   - ✅ Stability landscape analysis
   - ✅ Bifurcation classification

5. **Synthesis Analysis** (`noesis.core.theoretical.synthesis`)
   - ✅ Universal principle extraction
   - ✅ Scaling law identification
   - ✅ Cross-scale pattern detection
   - ✅ Emergent property identification

### Integration Points Tested

- ✅ **Component Interoperability**: Data flows correctly between analysis stages
- ✅ **NoesisComponent Integration**: Framework integrates with main component
- ✅ **Error Propagation**: Errors are handled gracefully across the pipeline
- ✅ **Configuration Management**: Component parameters are properly applied
- ✅ **Result Serialization**: All outputs can be converted to JSON format

## Test Data and Scenarios

### Synthetic Test Data
The tests use carefully constructed synthetic data to validate specific behaviors:

- **Structured Data**: Multi-regime patterns for dynamics testing
- **Trajectory Data**: Time series with jumps and transitions
- **High-Dimensional Data**: Testing curse of dimensionality
- **Noisy Data**: Gaussian noise with varying SNR levels

### Edge Case Scenarios
- **Minimal Data**: 3-5 sample datasets
- **High Dimensionality**: More features than samples
- **Constant Data**: Zero variance scenarios
- **Extreme Values**: 10+ orders of magnitude differences
- **Sparse Data**: Mostly zero values
- **Correlated Features**: Perfect and near-perfect correlations

### Performance Benchmarks
- **Large Datasets**: 1000+ samples, 20+ dimensions
- **Long Time Series**: 500+ time steps
- **Memory Usage**: Tracking allocation and cleanup
- **Concurrent Execution**: Multiple simultaneous analyses

## Expected Results

### Success Criteria
- ✅ **≥80% Overall Pass Rate**: Most test suites should pass
- ✅ **No Critical Failures**: Core functionality must work
- ✅ **Graceful Error Handling**: Invalid inputs handled properly
- ✅ **Performance Thresholds**: Analyses complete within reasonable time
- ✅ **Memory Stability**: No significant memory leaks

### Performance Expectations
- **Manifold Analysis**: <30 seconds for 1000×20 dataset
- **Dynamics Analysis**: <30 seconds for 500×8 time series
- **Memory Usage**: <500MB peak for large datasets
- **Concurrent Operations**: 2-5x speedup for parallel execution

### Quality Metrics
- **Numerical Stability**: Warnings for ill-conditioned data
- **Result Consistency**: Reproducible results with fixed seeds
- **Confidence Scores**: Appropriate confidence assessment
- **Error Messages**: Clear and actionable error descriptions

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```
   ImportError: No module named 'sklearn'
   ```
   **Solution**: Install dependencies
   ```bash
   pip install numpy scipy scikit-learn
   ```

2. **Memory Errors**
   ```
   MemoryError: Unable to allocate array
   ```
   **Solution**: Reduce test data size or increase available memory

3. **Convergence Warnings**
   ```
   Warning: EM algorithm did not converge
   ```
   **Solution**: Increase iteration limit or check data quality

4. **Performance Issues**
   ```
   Test timeout after 60 seconds
   ```
   **Solution**: Reduce dataset size or increase timeout threshold

### Debug Mode
Enable verbose output for debugging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Configuration
Modify test parameters in individual test files:

```python
# Reduce iterations for faster testing
config = {
    'em_iterations': 5,  # Default: 50
    'variance_threshold': 0.9,  # Default: 0.95
    'window_size': 20  # Default: 50
}
```

## Adding New Tests

### Test Structure
Follow the established pattern for new tests:

```python
async def test_new_feature(self):
    """Test description"""
    print("\n🧪 Testing New Feature...")
    
    try:
        # Test setup
        test_data = create_test_data()
        
        # Component initialization
        analyzer = NewAnalyzer(config)
        
        # Execute analysis
        result = await analyzer.analyze(test_data)
        
        # Validate results
        self.assertEqual(result.analysis_type, 'expected_type')
        self.assertIn('expected_key', result.data)
        
        print("✅ New feature test passed")
        
    except Exception as e:
        print(f"❌ New feature test failed: {e}")
        raise
```

### Test Categories
Organize tests by category:

1. **Unit Tests**: Individual component methods
2. **Integration Tests**: Component interactions
3. **System Tests**: End-to-end workflows
4. **Performance Tests**: Speed and memory benchmarks
5. **Stress Tests**: Edge cases and error conditions

### Documentation
Document new tests in this file with:
- ✅ Purpose and scope
- ✅ Test data requirements
- ✅ Expected outcomes
- ✅ Known limitations

## Continuous Integration

The test suite is designed to be compatible with CI/CD systems:

### GitHub Actions Example
```yaml
name: Test Mathematical Framework
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8
    - name: Install dependencies
      run: pip install numpy scipy scikit-learn
    - name: Validate tests
      run: python validate_tests.py
    - name: Run full test suite
      run: python run_all_tests.py
```

### Test Reports
Automated reports include:
- 📊 Pass/fail rates for each test suite
- ⏱️ Execution times and performance metrics
- 💾 Memory usage patterns
- 📈 Trend analysis across test runs
- 🚨 Alerts for performance regressions

---

## Contact

For questions about the testing framework:
- Review test output and error messages
- Check this documentation for troubleshooting tips
- Examine test source code for implementation details
- Consider the mathematical framework design principles

**Happy Testing!** 🧪🎯