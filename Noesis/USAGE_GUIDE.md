# Noesis Theoretical Analysis - Usage Guide

This guide provides practical examples and workflows for using the Noesis theoretical analysis framework to understand collective CI systems.

## Quick Start

### Installation and Setup

1. **Ensure Dependencies**:
   ```bash
   pip install numpy scipy scikit-learn
   ```

2. **Basic Import**:
   ```python
   import numpy as np
   from noesis.core.theoretical.manifold import ManifoldAnalyzer
   from noesis.core.theoretical.dynamics import DynamicsAnalyzer
   from noesis.core.theoretical.catastrophe import CatastropheAnalyzer
   from noesis.core.theoretical.synthesis import SynthesisAnalyzer
   ```

3. **Test Installation**:
   ```bash
   python validate_tests.py
   ```

### Your First Analysis

```python
import numpy as np
from noesis.core.theoretical.manifold import ManifoldAnalyzer

# Create sample collective CI data
# Simulate 100 time points of a 5-agent system with 3 features each
collective_data = np.random.randn(100, 15)  # 5 agents × 3 features

# Initialize analyzer
analyzer = ManifoldAnalyzer()

# Perform analysis
result = await analyzer.analyze(collective_data)

# View results
print(f"Original dimensions: {collective_data.shape[1]}")
print(f"Intrinsic dimension: {result.data['manifold_structure']['intrinsic_dimension']}")
print(f"Analysis confidence: {result.confidence:.3f}")
```

## Common Use Cases

### 1. Understanding Collective CI Emergence

**Scenario**: You have data from a collective CI system and want to understand how intelligence emerges from individual agent interactions.

```python
import numpy as np
from noesis.core.theoretical.manifold import ManifoldAnalyzer
from noesis.core.theoretical.synthesis import SynthesisAnalyzer

async def analyze_emergence():
    # Simulate collective CI data at different scales
    
    # Small collective (12 agents - known phase transition point)
    small_collective = np.random.randn(200, 36)  # 12 agents × 3 features
    
    # Medium collective (100 agents)
    medium_collective = np.random.randn(200, 300)  # 100 agents × 3 features
    
    # Large collective (8000 agents - another known transition point)
    # Use dimensionally reduced representation for computational feasibility
    large_collective = np.random.randn(200, 50)  # Reduced representation
    
    # Analyze each scale
    manifold_analyzer = ManifoldAnalyzer()
    
    small_result = await manifold_analyzer.analyze(small_collective)
    medium_result = await manifold_analyzer.analyze(medium_collective) 
    large_result = await manifold_analyzer.analyze(large_collective)
    
    # Prepare data for synthesis
    multi_scale_data = {
        'small_scale': {
            'n_agents': 12,
            'intrinsic_dimension': small_result.data['manifold_structure']['intrinsic_dimension'],
            'complexity': np.mean(small_result.data['manifold_structure']['explained_variance']),
            'manifold_structure': small_result.data['manifold_structure']
        },
        'medium_scale': {
            'n_agents': 100,
            'intrinsic_dimension': medium_result.data['manifold_structure']['intrinsic_dimension'],
            'complexity': np.mean(medium_result.data['manifold_structure']['explained_variance']),
            'manifold_structure': medium_result.data['manifold_structure']
        },
        'large_scale': {
            'n_agents': 8000,
            'intrinsic_dimension': large_result.data['manifold_structure']['intrinsic_dimension'],
            'complexity': np.mean(large_result.data['manifold_structure']['explained_variance']),
            'manifold_structure': large_result.data['manifold_structure']
        }
    }
    
    # Extract universal principles
    synthesis_analyzer = SynthesisAnalyzer()
    synthesis_result = await synthesis_analyzer.analyze(multi_scale_data)
    
    # Analyze results
    principles = synthesis_result.data['universal_principles']
    
    print("🧠 Collective Intelligence Emergence Analysis")
    print("=" * 50)
    
    for scale_name, scale_data in multi_scale_data.items():
        print(f"\n{scale_name.title()}:")
        print(f"  Agents: {scale_data['n_agents']}")
        print(f"  Intrinsic Dimension: {scale_data['intrinsic_dimension']}")
        print(f"  Complexity Score: {scale_data['complexity']:.3f}")
    
    print(f"\n🎯 Universal Principles Found: {len(principles)}")
    for principle in principles:
        print(f"  • {principle['principle_type']}: {principle['description']}")
        if 'scaling_exponent' in principle['parameters']:
            print(f"    Scaling exponent: {principle['parameters']['scaling_exponent']:.3f}")
    
    # Check for known collective intelligence transitions
    collective_principle = next(
        (p for p in principles if p['principle_type'] == 'collective_phase_transition'), 
        None
    )
    
    if collective_principle:
        print(f"\n🎉 Detected collective intelligence phase transition!")
        print(f"  Confidence: {collective_principle['confidence']:.3f}")
        print(f"  Evidence scales: {len(collective_principle['evidence'])}")

# Run the analysis
await analyze_emergence()
```

### 2. Detecting Regime Changes in Collective Behavior

**Scenario**: Your collective CI system shows different behavioral patterns over time, and you want to identify when transitions occur.

```python
import numpy as np
from noesis.core.theoretical.dynamics import DynamicsAnalyzer

async def detect_regime_changes():
    # Simulate collective CI time series with regime changes
    np.random.seed(42)  # For reproducible results
    
    # Create data with 3 distinct regimes
    regime1_data = np.random.randn(100, 8) * 0.5  # Low variance
    regime2_data = np.random.randn(80, 8) * 2.0   # High variance  
    regime3_data = np.random.randn(120, 8) * 1.0  # Medium variance
    
    # Add regime-specific patterns
    regime2_data[:, 0] += 3.0  # Shift in first feature
    regime3_data[:, 1] -= 2.0  # Shift in second feature
    
    # Combine into time series
    time_series = np.vstack([regime1_data, regime2_data, regime3_data])
    
    print(f"📊 Analyzing time series with {len(time_series)} time points")
    
    # Initialize dynamics analyzer
    analyzer = DynamicsAnalyzer({
        'n_regimes': 4,  # Allow for discovery of unknown regimes
        'em_iterations': 30,
        'min_regime_duration': 15
    })
    
    # Perform analysis
    result = await analyzer.analyze(time_series)
    
    # Extract results
    slds_model = result.data['slds_model']
    regime_identification = result.data['regime_identification']
    stability_analysis = result.data['stability_analysis']
    
    print(f"\n🌊 Dynamics Analysis Results")
    print("=" * 40)
    print(f"Model convergence confidence: {result.confidence:.3f}")
    print(f"Number of regimes detected: {slds_model['n_regimes']}")
    print(f"Current regime: {regime_identification['current_regime']}")
    
    # Analyze regime transitions
    transition_points = regime_identification['transition_points']
    regime_sequence = regime_identification['regime_sequence']
    
    print(f"\n🔄 Regime Transitions ({len(transition_points)} detected):")
    for i, transition_point in enumerate(transition_points):
        prev_regime = regime_sequence[transition_point - 1] if transition_point > 0 else 'start'
        next_regime = regime_sequence[transition_point]
        print(f"  {i+1}. Time {transition_point}: {prev_regime} → {next_regime}")
    
    # Analyze regime stability
    stability_scores = regime_identification['stability_scores']
    print(f"\n📈 Regime Stability Scores:")
    for regime_id, stability in stability_scores.items():
        print(f"  Regime {regime_id}: {stability:.3f}")
    
    # Predict future transitions
    predicted_transitions = regime_identification['predicted_transitions']
    if predicted_transitions:
        print(f"\n🔮 Predicted Transitions:")
        for prediction in predicted_transitions[:3]:  # Show first 3
            print(f"  {prediction['timestep']} steps: "
                  f"{prediction['from_regime']} → {prediction['to_regime']} "
                  f"(p={prediction['probability']:.3f})")
    
    # Visualize regime sequence (simplified)
    print(f"\n📊 Regime Timeline (first 50 points):")
    timeline = "".join([str(r) for r in regime_sequence[:50]])
    print(f"  {timeline}")
    
    return result

# Run the analysis
result = await detect_regime_changes()
```

### 3. Predicting Critical Transitions

**Scenario**: You want to detect early warning signals before your collective CI system undergoes a critical transition.

```python
import numpy as np
from noesis.core.theoretical.catastrophe import CatastropheAnalyzer

async def predict_critical_transitions():
    # Simulate system approaching critical transition
    np.random.seed(123)
    
    # Pre-transition: stable behavior
    n_pre = 150
    pre_transition = np.random.randn(n_pre, 6) * 0.3
    
    # Transition period: increasing variance (critical slowing down)
    n_transition = 50
    transition_variance = np.linspace(0.3, 2.0, n_transition)
    transition_data = []
    for i, var in enumerate(transition_variance):
        point = np.random.randn(6) * var
        transition_data.append(point)
    transition_data = np.array(transition_data)
    
    # Post-transition: new stable state with higher variance
    n_post = 100
    post_transition = np.random.randn(n_post, 6) * 2.0 + np.array([2.0, 0, -1.0, 0, 1.0, 0])
    
    # Combine into trajectory
    trajectory = np.vstack([pre_transition, transition_data, post_transition])
    
    print(f"🔱 Analyzing trajectory for critical transitions")
    print(f"Total trajectory length: {len(trajectory)} points")
    
    # Initialize catastrophe analyzer
    analyzer = CatastropheAnalyzer({
        'window_size': 30,
        'warning_threshold': 1.5,
        'potential_resolution': 50
    })
    
    # Perform analysis
    result = await analyzer.analyze(trajectory)
    
    # Extract results
    critical_points = result.data['critical_points']
    warning_signals = result.data['early_warning_signals']
    
    print(f"\n🚨 Critical Transition Analysis")
    print("=" * 40)
    print(f"Analysis confidence: {result.confidence:.3f}")
    print(f"Critical points detected: {len(critical_points)}")
    
    # Analyze early warning signals
    print(f"\n⚠️ Early Warning Signals:")
    if 'warning_level' in warning_signals:
        level = warning_signals['warning_level']
        score = warning_signals.get('composite_warning_score', 0)
        print(f"  Overall warning level: {level.upper()} (score: {score:.3f})")
    
    if warning_signals.get('variance_increasing', False):
        trend = warning_signals.get('variance_trend', 0)
        print(f"  ✓ Variance increasing (trend: {trend:.4f})")
    
    if warning_signals.get('critical_slowing_down', False):
        ac_trend = warning_signals.get('autocorrelation_trend', 0)
        print(f"  ✓ Critical slowing down (AC trend: {ac_trend:.4f})")
    
    skewness = warning_signals.get('mean_skewness', 0)
    if abs(skewness) > 0.3:
        print(f"  ✓ Distribution asymmetry (skewness: {skewness:.3f})")
    
    # Analyze detected critical points
    if critical_points:
        print(f"\n🎯 Critical Points Detected:")
        for i, cp in enumerate(critical_points):
            print(f"  {i+1}. Type: {cp['transition_type']}")
            print(f"     Confidence: {cp['confidence']:.3f}")
            print(f"     Warning signals: {', '.join(cp['warning_signals'])}")
            
            # Show stability change
            if 'variance_ratio' in cp['stability_change']:
                ratio = cp['stability_change']['variance_ratio']
                print(f"     Variance change: {ratio:.2f}x")
    
    # Generate recommendations
    print(f"\n💡 Recommendations:")
    
    warning_level = warning_signals.get('warning_level', 'low')
    if warning_level == 'high':
        print("  🔴 HIGH RISK: Critical transition imminent")
        print("     - Increase monitoring frequency")
        print("     - Prepare intervention strategies")
        print("     - Consider system stabilization measures")
    elif warning_level == 'medium':
        print("  🟡 MEDIUM RISK: Approaching critical transition")
        print("     - Monitor variance and autocorrelation trends")
        print("     - Review system parameters")
    else:
        print("  🟢 LOW RISK: System appears stable")
        print("     - Continue regular monitoring")
    
    return result

# Run the analysis
result = await predict_critical_transitions()
```

### 4. Real-Time Streaming Analysis

**Scenario**: You want to perform live theoretical analysis of your collective CI system as it operates.

```python
import asyncio
from noesis.core.noesis_component import NoesisComponent

async def real_time_analysis():
    print("🔄 Starting Real-Time Theoretical Analysis")
    print("=" * 45)
    
    # Initialize Noesis component
    component = NoesisComponent()
    await component.init()
    
    print("✅ Noesis component initialized")
    
    # Check component capabilities
    capabilities = component.get_capabilities()
    theoretical_caps = [cap for cap in capabilities if 'theoretical' in cap.lower()]
    print(f"📋 Theoretical capabilities: {len(theoretical_caps)}")
    for cap in theoretical_caps:
        print(f"  • {cap}")
    
    # Start streaming analysis
    print(f"\n🚀 Starting streaming analysis...")
    success = await component.start_streaming()
    
    if not success:
        print("❌ Failed to start streaming analysis")
        return
    
    print("✅ Streaming analysis started")
    
    try:
        # Monitor for insights
        monitoring_duration = 60  # Monitor for 60 seconds
        check_interval = 5        # Check every 5 seconds
        
        print(f"\n📊 Monitoring for {monitoring_duration} seconds (checking every {check_interval}s)")
        print("Looking for theoretical insights...")
        
        for i in range(monitoring_duration // check_interval):
            await asyncio.sleep(check_interval)
            
            # Get current stream status
            status = await component.get_stream_status()
            print(f"\n⏰ Check {i+1}/{monitoring_duration // check_interval}:")
            print(f"  Stream active: {status.get('active', False)}")
            print(f"  Uptime: {status.get('uptime_minutes', 0):.1f} minutes")
            
            # Get theoretical insights
            insights = await component.get_theoretical_insights()
            
            if insights and 'insights' in insights:
                insight_list = insights['insights']
                print(f"  💡 New insights: {len(insight_list)}")
                
                for insight in insight_list[-3:]:  # Show last 3 insights
                    insight_type = insight.get('type', 'unknown')
                    confidence = insight.get('confidence', 0)
                    description = insight.get('insight', 'No description')
                    print(f"    🎯 {insight_type} (conf: {confidence:.3f}): {description}")
            else:
                print("  ⏳ No new insights yet...")
            
            # Check for critical transitions
            if 'critical_transitions' in insights:
                transitions = insights['critical_transitions']
                if transitions:
                    print(f"  🚨 Critical transitions detected: {len(transitions)}")
                    for transition in transitions:
                        print(f"    ⚠️ {transition.get('type', 'unknown')} transition")
            
            # Monitor system health
            if 'system_health' in insights:
                health = insights['system_health']
                if health.get('warning_level') == 'high':
                    print(f"  🔴 HIGH WARNING: {health.get('message', 'Unknown issue')}")
                elif health.get('warning_level') == 'medium':
                    print(f"  🟡 Medium warning: {health.get('message', 'Monitor closely')}")
    
    except KeyboardInterrupt:
        print(f"\n⏹️ Monitoring interrupted by user")
    
    finally:
        # Stop streaming
        print(f"\n🛑 Stopping streaming analysis...")
        stop_success = await component.stop_streaming()
        
        if stop_success:
            print("✅ Streaming analysis stopped")
        else:
            print("⚠️ Warning: Failed to stop streaming cleanly")
        
        # Get final analysis results
        final_status = await component.get_stream_status()
        print(f"\n📋 Final Status:")
        print(f"  Total uptime: {final_status.get('uptime_minutes', 0):.1f} minutes")
        print(f"  Stream active: {final_status.get('active', False)}")
        
        # Cleanup
        await component.shutdown()
        print("✅ Component shutdown complete")

# Run the streaming analysis
await real_time_analysis()
```

### 5. Complete Multi-Scale Analysis Pipeline

**Scenario**: You want to perform a comprehensive analysis combining all theoretical analysis components.

```python
import numpy as np
from noesis.core.theoretical.manifold import ManifoldAnalyzer
from noesis.core.theoretical.dynamics import DynamicsAnalyzer
from noesis.core.theoretical.catastrophe import CatastropheAnalyzer
from noesis.core.theoretical.synthesis import SynthesisAnalyzer

async def complete_analysis_pipeline():
    print("🧠 Complete Theoretical Analysis Pipeline")
    print("=" * 50)
    
    # Generate comprehensive test data
    np.random.seed(42)
    
    # Collective state data (for manifold analysis)
    collective_states = np.random.randn(300, 20)
    # Add structure: two main components
    collective_states[:150, :10] += 2.0
    collective_states[150:, 10:] += 2.0
    
    # Time series data (for dynamics analysis)  
    time_series = np.cumsum(np.random.randn(250, 12) * 0.1, axis=0)
    # Add regime changes
    time_series[100:150] += np.array([3, 0, -2, 1, 0, -1, 2, 0, 1, -1, 0, 2])
    time_series[200:] += np.array([-1, 2, 0, -2, 1, 0, -1, 1, 0, 2, -1, 0])
    
    # Trajectory data (for catastrophe analysis)
    trajectory = np.cumsum(np.random.randn(200, 8) * 0.2, axis=0)
    # Add critical transition
    trajectory[120:140] += np.random.randn(20, 8) * 2.0  # High variance transition
    trajectory[140:] += np.array([5, 0, -3, 2, 0, -1, 3, 1])  # State shift
    
    print(f"📊 Data prepared:")
    print(f"  Collective states: {collective_states.shape}")
    print(f"  Time series: {time_series.shape}")
    print(f"  Trajectory: {trajectory.shape}")
    
    # Step 1: Manifold Analysis
    print(f"\n1️⃣ Manifold Analysis...")
    manifold_analyzer = ManifoldAnalyzer({
        'variance_threshold': 0.90,
        'embedding_method': 'pca'
    })
    
    manifold_result = await manifold_analyzer.analyze(collective_states)
    manifold_data = manifold_result.data['manifold_structure']
    
    print(f"   ✅ Completed (confidence: {manifold_result.confidence:.3f})")
    print(f"   📐 Intrinsic dimension: {manifold_data['intrinsic_dimension']}")
    print(f"   📊 Explained variance: {np.sum(manifold_data['explained_variance']):.3f}")
    
    # Step 2: Dynamics Analysis
    print(f"\n2️⃣ Dynamics Analysis...")
    dynamics_analyzer = DynamicsAnalyzer({
        'n_regimes': 3,
        'em_iterations': 25
    })
    
    dynamics_result = await dynamics_analyzer.analyze(time_series)
    regime_data = dynamics_result.data['regime_identification']
    
    print(f"   ✅ Completed (confidence: {dynamics_result.confidence:.3f})")
    print(f"   🌊 Regimes detected: {dynamics_result.data['slds_model']['n_regimes']}")
    print(f"   🔄 Transitions: {len(regime_data['transition_points'])}")
    print(f"   📍 Current regime: {regime_data['current_regime']}")
    
    # Step 3: Catastrophe Analysis
    print(f"\n3️⃣ Catastrophe Analysis...")
    catastrophe_analyzer = CatastropheAnalyzer({
        'window_size': 25,
        'warning_threshold': 1.5
    })
    
    # Prepare data for catastrophe analysis
    catastrophe_data = {
        'trajectory': trajectory,
        'manifold': manifold_result.data,
        'dynamics': dynamics_result.data
    }
    
    catastrophe_result = await catastrophe_analyzer.analyze(catastrophe_data)
    critical_points = catastrophe_result.data['critical_points']
    warnings = catastrophe_result.data['early_warning_signals']
    
    print(f"   ✅ Completed (confidence: {catastrophe_result.confidence:.3f})")
    print(f"   🔱 Critical points: {len(critical_points)}")
    print(f"   ⚠️ Warning level: {warnings.get('warning_level', 'unknown')}")
    
    # Step 4: Synthesis Analysis
    print(f"\n4️⃣ Synthesis Analysis...")
    synthesis_analyzer = SynthesisAnalyzer({
        'confidence_threshold': 0.7
    })
    
    # Prepare multi-scale data for synthesis
    synthesis_data = {
        'manifold_analysis': {
            'n_agents': 100,  # Simulated
            'intrinsic_dimension': manifold_data['intrinsic_dimension'],
            'complexity': np.mean(manifold_data['explained_variance']),
            'topology_connectivity': manifold_data['topology_metrics'].get('connectivity', 0),
            'manifold_structure': manifold_data
        },
        'dynamics_analysis': {
            'n_agents': 150,  # Simulated
            'n_regimes': dynamics_result.data['slds_model']['n_regimes'],
            'regime_stability': np.mean(list(regime_data['stability_scores'].values())),
            'transition_frequency': len(regime_data['transition_points']) / len(time_series)
        },
        'catastrophe_analysis': {
            'n_agents': 200,  # Simulated
            'critical_transitions': len(critical_points),
            'warning_score': warnings.get('composite_warning_score', 0),
            'system_stability': 1.0 - warnings.get('composite_warning_score', 0)
        }
    }
    
    synthesis_result = await synthesis_analyzer.analyze(synthesis_data)
    principles = synthesis_result.data['universal_principles']
    emergent_props = synthesis_result.data['emergent_properties']
    
    print(f"   ✅ Completed (confidence: {synthesis_result.confidence:.3f})")
    print(f"   🎯 Universal principles: {len(principles)}")
    print(f"   🌟 Emergent properties: {len(emergent_props)}")
    
    # Summary Report
    print(f"\n📋 COMPREHENSIVE ANALYSIS REPORT")
    print("=" * 50)
    
    print(f"\n🔧 System Architecture:")
    print(f"  • Original state space: {collective_states.shape[1]} dimensions")
    print(f"  • Intrinsic dimension: {manifold_data['intrinsic_dimension']}")
    print(f"  • Dimensionality reduction: {manifold_data['intrinsic_dimension'] / collective_states.shape[1] * 100:.1f}%")
    
    print(f"\n🌊 Behavioral Dynamics:")
    print(f"  • Behavioral regimes: {dynamics_result.data['slds_model']['n_regimes']}")
    print(f"  • Regime transitions: {len(regime_data['transition_points'])}")
    print(f"  • Current regime stability: {regime_data['stability_scores'].get(str(regime_data['current_regime']), 0):.3f}")
    
    print(f"\n🔱 Critical Transitions:")
    print(f"  • Critical points detected: {len(critical_points)}")
    print(f"  • System warning level: {warnings.get('warning_level', 'unknown').upper()}")
    if warnings.get('variance_increasing'):
        print(f"  • Early warning: Increasing variance detected")
    if warnings.get('critical_slowing_down'):
        print(f"  • Early warning: Critical slowing down detected")
    
    print(f"\n🎯 Universal Principles:")
    for i, principle in enumerate(principles[:3], 1):  # Show top 3
        print(f"  {i}. {principle['principle_type'].replace('_', ' ').title()}")
        print(f"     Description: {principle['description']}")
        print(f"     Confidence: {principle['confidence']:.3f}")
    
    print(f"\n🌟 Emergent Properties:")
    for prop in emergent_props[:3]:  # Show top 3
        print(f"  • {prop['property']} emerges at {prop['emerges_at_scale']}")
        print(f"    (system size: {prop['emergence_size']})")
    
    # Overall assessment
    overall_confidence = np.mean([
        manifold_result.confidence,
        dynamics_result.confidence,
        catastrophe_result.confidence,
        synthesis_result.confidence
    ])
    
    print(f"\n📊 Overall Assessment:")
    print(f"  • Analysis confidence: {overall_confidence:.3f}")
    
    if overall_confidence > 0.8:
        print(f"  • Status: HIGH CONFIDENCE - Results are reliable")
    elif overall_confidence > 0.6:
        print(f"  • Status: MEDIUM CONFIDENCE - Results are indicative")
    else:
        print(f"  • Status: LOW CONFIDENCE - More data recommended")
    
    warning_level = warnings.get('warning_level', 'low')
    if warning_level == 'high':
        print(f"  • Alert: System approaching critical transition")
    elif warning_level == 'medium':
        print(f"  • Notice: Increased system monitoring recommended")
    else:
        print(f"  • Status: System appears stable")
    
    return {
        'manifold': manifold_result,
        'dynamics': dynamics_result,
        'catastrophe': catastrophe_result,
        'synthesis': synthesis_result,
        'overall_confidence': overall_confidence
    }

# Run the complete analysis
results = await complete_analysis_pipeline()
```

## Best Practices

### 1. Data Preparation

```python
# Always validate and preprocess your data
def prepare_collective_data(raw_data):
    # Remove NaN and infinite values
    data = raw_data[~np.isnan(raw_data).any(axis=1)]
    data = data[~np.isinf(data).any(axis=1)]
    
    # Check minimum data requirements
    if len(data) < 50:
        raise ValueError("Insufficient data points (minimum 50 required)")
    
    # Normalize if needed
    if np.std(data) > 10 * np.mean(np.abs(data)):
        print("⚠️ Large scale differences detected, normalizing...")
        data = (data - np.mean(data, axis=0)) / np.std(data, axis=0)
    
    return data
```

### 2. Configuration Optimization

```python
# Optimize configuration based on data size
def get_optimal_config(data_size, analysis_type):
    if analysis_type == 'manifold':
        if data_size < 1000:
            return {'embedding_method': 'tsne', 'variance_threshold': 0.95}
        else:
            return {'embedding_method': 'pca', 'variance_threshold': 0.90}
    
    elif analysis_type == 'dynamics':
        if data_size < 500:
            return {'n_regimes': 2, 'em_iterations': 20}
        else:
            return {'n_regimes': 4, 'em_iterations': 50}
    
    return {}
```

### 3. Error Handling

```python
async def robust_analysis(analyzer, data, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = await analyzer.analyze(data)
            
            # Check result quality
            if result.confidence < 0.5:
                print(f"⚠️ Low confidence result: {result.confidence:.3f}")
                if result.warnings:
                    print(f"   Warnings: {', '.join(result.warnings)}")
            
            return result
            
        except Exception as e:
            print(f"❌ Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise
            
            # Modify data/config for retry
            if "singular" in str(e).lower():
                # Add noise to break singularities
                data = data + np.random.randn(*data.shape) * 0.001
```

### 4. Performance Monitoring

```python
import time
import psutil
import os

def monitor_performance(func):
    async def wrapper(*args, **kwargs):
        # Track performance
        start_time = time.time()
        process = psutil.Process(os.getpid())
        start_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        try:
            result = await func(*args, **kwargs)
            
            end_time = time.time()
            end_memory = process.memory_info().rss / 1024 / 1024
            
            duration = end_time - start_time
            memory_used = end_memory - start_memory
            
            print(f"⏱️ Performance: {duration:.2f}s, {memory_used:.1f}MB")
            
            return result
            
        except Exception as e:
            print(f"❌ Analysis failed after {time.time() - start_time:.2f}s")
            raise
    
    return wrapper
```

## Troubleshooting Common Issues

### Issue 1: Low Confidence Results

**Symptoms**: Analysis returns confidence < 0.6

**Solutions**:
```python
# Check data quality
def diagnose_low_confidence(data, result):
    print("🔍 Diagnosing low confidence...")
    
    # Check data properties
    print(f"Data shape: {data.shape}")
    print(f"Data range: [{data.min():.3f}, {data.max():.3f}]")
    print(f"Missing values: {np.isnan(data).sum()}")
    
    # Check for correlation issues
    if data.shape[1] > 1:
        corr_matrix = np.corrcoef(data.T)
        max_corr = np.max(np.abs(corr_matrix[np.triu_indices_from(corr_matrix, k=1)]))
        print(f"Max correlation: {max_corr:.3f}")
        
        if max_corr > 0.95:
            print("⚠️ High correlation detected - consider feature selection")
    
    # Check warnings
    if result.warnings:
        print(f"Warnings: {', '.join(result.warnings)}")
```

### Issue 2: Memory Errors

**Symptoms**: MemoryError or system slowdown

**Solutions**:
```python
# Data subsampling for large datasets
def handle_large_data(data, max_samples=5000):
    if len(data) > max_samples:
        print(f"⚠️ Large dataset ({len(data)} samples), subsampling to {max_samples}")
        indices = np.random.choice(len(data), max_samples, replace=False)
        return data[indices]
    return data

# Batch processing
async def batch_analysis(analyzer, data, batch_size=1000):
    results = []
    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        result = await analyzer.analyze(batch)
        results.append(result)
    return results
```

### Issue 3: Convergence Problems

**Symptoms**: EM algorithm warnings, poor regime identification

**Solutions**:
```python
# Adaptive configuration
def adaptive_dynamics_config(data):
    n_samples = len(data)
    
    if n_samples < 100:
        return {'n_regimes': 2, 'em_iterations': 10}
    elif n_samples < 500:
        return {'n_regimes': 3, 'em_iterations': 25}
    else:
        return {'n_regimes': 4, 'em_iterations': 50}
```

This usage guide provides practical examples for leveraging the Noesis theoretical analysis framework to understand collective CI systems across different scales and scenarios.