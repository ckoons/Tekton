#!/usr/bin/env python3
"""
Landmark Seismograph - System Vibration Sensing for Apollo/Rhetor

Like Scotty feeling the ship's vibrations through the deck plates,
this module allows Apollo and Rhetor to sense system health through
the landmark system's architectural memory.

Part of the Apollo/Rhetor ambient intelligence system.
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from collections import defaultdict, deque
import logging

# Import landmarks with fallback
try:
    from landmarks import (
        architecture_decision,
        api_contract,
        integration_point,
        performance_boundary,
        state_checkpoint,
        danger_zone
    )
except ImportError:
    # Define no-op decorators when landmarks not available
    def architecture_decision(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def api_contract(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def performance_boundary(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def state_checkpoint(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def danger_zone(**kwargs):
        def decorator(func):
            return func
        return decorator

logger = logging.getLogger(__name__)


@architecture_decision(
    title="Landmark-Based System Health Monitoring",
    description="Sense system health through architectural memory vibrations",
    rationale="Like feeling ship vibrations - landmarks reveal system state through patterns",
    alternatives_considered=["Metrics-only", "Log analysis", "Active probing"],
    impacts=["system_awareness", "predictive_capability", "ambient_intelligence"],
    decided_by="Casey, Teri, Tess",
    decision_date="2025-01-09"
)
@performance_boundary(
    title="Landmark Pattern Analysis",
    description="Analyze landmark frequency and patterns for health assessment",
    sla="<10ms pattern detection",
    optimization_notes="Use sliding windows and cached frequencies",
    measured_impact="Enables real-time system health awareness"
)
class LandmarkSeismograph:
    """
    Monitors system vibrations through landmark activity patterns.
    
    Detects rhythm changes, anomalies, and harmony in the system's
    architectural memory as it grows and evolves.
    """
    
    def __init__(self, history_window: int = 300):
        """
        Initialize the seismograph.
        
        Args:
            history_window: Seconds of history to maintain (default 5 minutes)
        """
        self.history_window = history_window
        self.vibration_history = defaultdict(lambda: deque(maxlen=100))
        self.landmark_baseline = {}
        self.anomaly_threshold = 2.0  # Standard deviations
        self.harmony_score = 1.0
        
        # Landmark categories for pattern analysis
        self.categories = {
            'architecture': ['architecture_decision', 'design_pattern'],
            'integration': ['integration_point', 'api_contract'],
            'state': ['state_checkpoint', 'performance_metric'],
            'flow': ['data_flow', 'control_flow']
        }
        
        # Load landmark registry
        self._load_landmarks()
        
    def _load_landmarks(self):
        """Load the current landmark registry."""
        try:
            # Try direct path first
            import os
            tekton_root = os.environ.get('TEKTON_ROOT', '/Users/cskoons/projects/github/Tekton')
            landmark_file = Path(tekton_root) / 'landmarks' / 'data' / 'registry.json'
            
            if landmark_file.exists():
                with open(landmark_file, 'r') as f:
                    self.landmark_data = json.load(f)
                    logger.info(f"Loaded {len(self.landmark_data.get('landmarks', []))} landmarks")
            else:
                # Try import method
                try:
                    from landmarks.data import registry
                    landmark_file = Path(registry.__file__).parent / 'registry.json'
                    
                    if landmark_file.exists():
                        with open(landmark_file, 'r') as f:
                            self.landmark_data = json.load(f)
                            logger.info(f"Loaded {len(self.landmark_data.get('landmarks', []))} landmarks")
                    else:
                        self.landmark_data = {'landmarks': [], 'statistics': {}}
                        logger.warning("No landmark registry found")
                except ImportError:
                    self.landmark_data = {'landmarks': [], 'statistics': {}}
                    logger.warning("Landmarks module not available")
        except Exception as e:
            logger.error(f"Could not load landmarks: {e}")
            self.landmark_data = {'landmarks': [], 'statistics': {}}
    
    async def sense_vibrations(self) -> Dict[str, Any]:
        """
        Sense current system vibrations through landmark patterns.
        
        Returns:
            Dict containing vibration analysis
        """
        # Reload landmarks to detect new ones
        self._load_landmarks()
        
        vibrations = {
            'timestamp': datetime.now().isoformat(),
            'total_landmarks': len(self.landmark_data.get('landmarks', [])),
            'categories': self._analyze_categories(),
            'growth_rate': self._calculate_growth_rate(),
            'activity_rhythm': self._detect_rhythm(),
            'anomalies': self._detect_anomalies(),
            'harmony_score': self._calculate_harmony(),
            'stress_indicators': self._detect_stress(),
            'health_assessment': self._assess_health()
        }
        
        # Store in history
        self._update_history(vibrations)
        
        return vibrations
    
    def _analyze_categories(self) -> Dict[str, int]:
        """Analyze landmark distribution by category."""
        category_counts = defaultdict(int)
        
        for landmark in self.landmark_data.get('landmarks', []):
            lm_type = landmark.get('type', 'unknown')
            for category, types in self.categories.items():
                if lm_type in types:
                    category_counts[category] += 1
                    break
            else:
                category_counts['other'] += 1
        
        return dict(category_counts)
    
    def _calculate_growth_rate(self) -> Dict[str, Any]:
        """Calculate landmark growth rate."""
        landmarks = self.landmark_data.get('landmarks', [])
        
        if not landmarks:
            return {'rate': 0, 'trend': 'stable'}
        
        # Group by registration time (if available)
        now = datetime.now()
        recent = []
        older = []
        
        for landmark in landmarks:
            # Check if landmark has timestamp (would need to be added to registry)
            # For now, use position as proxy for age
            if landmarks.index(landmark) > len(landmarks) - 20:
                recent.append(landmark)
            else:
                older.append(landmark)
        
        growth_rate = len(recent) / max(len(older), 1)
        
        trend = 'accelerating' if growth_rate > 1.2 else 'stable' if growth_rate > 0.8 else 'slowing'
        
        return {
            'rate': growth_rate,
            'trend': trend,
            'recent_count': len(recent),
            'total_count': len(landmarks)
        }
    
    def _detect_rhythm(self) -> Dict[str, Any]:
        """Detect activity rhythm patterns."""
        # Analyze landmark type sequences for patterns
        landmarks = self.landmark_data.get('landmarks', [])
        
        if len(landmarks) < 10:
            return {'pattern': 'insufficient_data', 'regularity': 0}
        
        # Look for repeating sequences
        type_sequence = [lm.get('type', '') for lm in landmarks[-50:]]
        
        # Simple pattern detection - look for cycles
        pattern_found = False
        regularity = 0
        
        for cycle_len in range(2, min(10, len(type_sequence) // 2)):
            matches = 0
            for i in range(len(type_sequence) - cycle_len):
                if type_sequence[i:i+cycle_len] == type_sequence[i+cycle_len:i+2*cycle_len]:
                    matches += 1
            
            if matches > len(type_sequence) // (cycle_len * 3):
                pattern_found = True
                regularity = matches / (len(type_sequence) - cycle_len)
                break
        
        return {
            'pattern': 'cyclic' if pattern_found else 'organic',
            'regularity': regularity,
            'sequence_length': len(type_sequence)
        }
    
    def _detect_anomalies(self) -> List[Dict[str, Any]]:
        """Detect anomalous patterns in landmark activity."""
        anomalies = []
        
        # Check for unusual clustering
        landmarks = self.landmark_data.get('landmarks', [])
        type_counts = defaultdict(int)
        
        for landmark in landmarks:
            type_counts[landmark.get('type', 'unknown')] += 1
        
        # Find outliers
        if type_counts:
            avg_count = sum(type_counts.values()) / len(type_counts)
            for lm_type, count in type_counts.items():
                deviation = abs(count - avg_count) / max(avg_count, 1)
                if deviation > self.anomaly_threshold:
                    anomalies.append({
                        'type': 'unusual_concentration',
                        'landmark_type': lm_type,
                        'count': count,
                        'deviation': deviation
                    })
        
        # Check for missing expected patterns
        expected_balance = {
            'architecture_decision': 0.2,
            'integration_point': 0.3,
            'state_checkpoint': 0.2,
            'api_contract': 0.15,
            'performance_metric': 0.15
        }
        
        total = len(landmarks)
        for lm_type, expected_ratio in expected_balance.items():
            actual_count = type_counts.get(lm_type, 0)
            expected_count = total * expected_ratio
            if actual_count < expected_count * 0.5:
                anomalies.append({
                    'type': 'pattern_deficit',
                    'landmark_type': lm_type,
                    'expected': int(expected_count),
                    'actual': actual_count
                })
        
        return anomalies
    
    def _detect_stress(self) -> Dict[str, Any]:
        """Detect system stress indicators."""
        stress_indicators = {
            'level': 'normal',
            'factors': []
        }
        
        anomalies = self._detect_anomalies()
        growth = self._calculate_growth_rate()
        
        # High anomaly count indicates stress
        if len(anomalies) > 3:
            stress_indicators['factors'].append('high_anomaly_count')
            stress_indicators['level'] = 'elevated'
        
        # Rapid growth can indicate stress
        if growth['rate'] > 2.0:
            stress_indicators['factors'].append('rapid_growth')
            stress_indicators['level'] = 'elevated'
        
        # Too slow growth might indicate stagnation
        if growth['rate'] < 0.5 and growth.get('total_count', 0) > 50:
            stress_indicators['factors'].append('stagnation')
            if stress_indicators['level'] == 'normal':
                stress_indicators['level'] = 'mild'
        
        return stress_indicators
    
    def _calculate_harmony(self) -> float:
        """
        Calculate system harmony score (0-1).
        
        Higher scores indicate better balance and flow.
        """
        harmony_factors = []
        
        # Category balance contributes to harmony
        categories = self._analyze_categories()
        if categories:
            total = sum(categories.values())
            if total > 0:
                balance = 1.0 - (max(categories.values()) / total - 1/len(categories)) * 2
                harmony_factors.append(max(0, min(1, balance)))
        
        # Regular rhythm contributes to harmony
        rhythm = self._detect_rhythm()
        if rhythm['pattern'] == 'cyclic':
            harmony_factors.append(rhythm['regularity'])
        else:
            harmony_factors.append(0.7)  # Organic growth is also healthy
        
        # Low anomalies contribute to harmony
        anomalies = self._detect_anomalies()
        anomaly_factor = 1.0 - min(len(anomalies) / 5, 1.0)
        harmony_factors.append(anomaly_factor)
        
        # Calculate weighted harmony
        if harmony_factors:
            self.harmony_score = sum(harmony_factors) / len(harmony_factors)
        
        return self.harmony_score
    
    def _assess_health(self) -> Dict[str, Any]:
        """Provide overall health assessment."""
        stress = self._detect_stress()
        harmony = self._calculate_harmony()
        growth = self._calculate_growth_rate()
        
        # Determine health status
        if harmony > 0.8 and stress['level'] == 'normal':
            status = 'excellent'
            description = 'System is in harmony with healthy growth'
        elif harmony > 0.6 and stress['level'] in ['normal', 'mild']:
            status = 'good'
            description = 'System is functioning well with minor variations'
        elif harmony > 0.4 or stress['level'] == 'elevated':
            status = 'fair'
            description = 'System showing signs of stress or imbalance'
        else:
            status = 'poor'
            description = 'System needs attention - high stress or disharmony'
        
        return {
            'status': status,
            'description': description,
            'harmony_score': harmony,
            'stress_level': stress['level'],
            'growth_trend': growth['trend'],
            'recommendations': self._generate_recommendations(status, stress, harmony)
        }
    
    def _generate_recommendations(self, status: str, stress: Dict, harmony: float) -> List[str]:
        """Generate recommendations based on health assessment."""
        recommendations = []
        
        if status in ['poor', 'fair']:
            if 'rapid_growth' in stress.get('factors', []):
                recommendations.append('Consider slowing development pace')
            if 'stagnation' in stress.get('factors', []):
                recommendations.append('Stimulate activity with new integrations')
            if harmony < 0.5:
                recommendations.append('Review architectural balance')
            if len(self._detect_anomalies()) > 3:
                recommendations.append('Investigate anomalous patterns')
        
        if not recommendations:
            recommendations.append('Continue current development rhythm')
        
        return recommendations
    
    def _update_history(self, vibrations: Dict):
        """Update vibration history for trend analysis."""
        timestamp = datetime.now()
        
        # Store key metrics in history
        self.vibration_history['harmony'].append((timestamp, vibrations['harmony_score']))
        self.vibration_history['landmarks'].append((timestamp, vibrations['total_landmarks']))
        self.vibration_history['stress'].append((timestamp, vibrations['stress_indicators']['level']))
        
        # Clean old history
        cutoff = timestamp - timedelta(seconds=self.history_window)
        for key in self.vibration_history:
            while self.vibration_history[key] and self.vibration_history[key][0][0] < cutoff:
                self.vibration_history[key].popleft()
    
    def get_trend(self, metric: str, window: int = 60) -> str:
        """
        Get trend for a specific metric over time window.
        
        Args:
            metric: Metric name ('harmony', 'landmarks', 'stress')
            window: Seconds to look back
            
        Returns:
            Trend description ('rising', 'falling', 'stable')
        """
        if metric not in self.vibration_history:
            return 'unknown'
        
        history = self.vibration_history[metric]
        if len(history) < 2:
            return 'insufficient_data'
        
        cutoff = datetime.now() - timedelta(seconds=window)
        recent = [v for t, v in history if t > cutoff]
        
        if not recent:
            return 'no_recent_data'
        
        # Simple trend detection
        if metric == 'stress':
            # Stress uses levels, not numbers
            return 'stable'
        
        avg_early = sum(recent[:len(recent)//2]) / max(len(recent[:len(recent)//2]), 1)
        avg_late = sum(recent[len(recent)//2:]) / max(len(recent[len(recent)//2:]), 1)
        
        change = (avg_late - avg_early) / max(avg_early, 1)
        
        if change > 0.1:
            return 'rising'
        elif change < -0.1:
            return 'falling'
        else:
            return 'stable'


# Apollo-specific sensing
async def apollo_sense(seismograph: LandmarkSeismograph) -> Dict[str, Any]:
    """
    Apollo's interpretation of system vibrations.
    
    Focuses on trajectory and predictive patterns.
    """
    vibrations = await seismograph.sense_vibrations()
    
    # Apollo's analysis
    apollo_reading = {
        'vibrations': vibrations,
        'trajectory_analysis': {
            'growth_trajectory': vibrations['growth_rate']['trend'],
            'pattern_stability': vibrations['activity_rhythm']['regularity'],
            'predicted_next_phase': _predict_next_phase(vibrations)
        },
        'resource_predictions': {
            'memory_pressure': _predict_memory_pressure(vibrations),
            'scaling_needed': vibrations['growth_rate']['rate'] > 1.5
        },
        'intervention_assessment': {
            'needed': vibrations['health_assessment']['status'] in ['poor', 'fair'],
            'urgency': 'high' if vibrations['stress_indicators']['level'] == 'elevated' else 'low',
            'type': _suggest_intervention_type(vibrations)
        }
    }
    
    return apollo_reading


# Rhetor-specific sensing
async def rhetor_sense(seismograph: LandmarkSeismograph) -> Dict[str, Any]:
    """
    Rhetor's interpretation of system vibrations.
    
    Focuses on emotional and stress patterns.
    """
    vibrations = await seismograph.sense_vibrations()
    
    # Rhetor's analysis
    rhetor_reading = {
        'vibrations': vibrations,
        'emotional_reading': {
            'system_mood': _interpret_mood(vibrations),
            'stress_level': vibrations['stress_indicators']['level'],
            'harmony_feeling': _interpret_harmony(vibrations['harmony_score'])
        },
        'pattern_feelings': {
            'rhythm_comfort': vibrations['activity_rhythm']['pattern'] == 'cyclic',
            'growth_anxiety': vibrations['growth_rate']['rate'] > 2.0,
            'stagnation_concern': vibrations['growth_rate']['rate'] < 0.5
        },
        'support_needed': {
            'type': _determine_support_type(vibrations),
            'target_areas': _identify_stress_points(vibrations),
            'urgency': _assess_emotional_urgency(vibrations)
        }
    }
    
    return rhetor_reading


# Helper functions for interpretations
def _predict_next_phase(vibrations: Dict) -> str:
    """Predict the next system phase based on patterns."""
    if vibrations['growth_rate']['trend'] == 'accelerating':
        return 'expansion'
    elif vibrations['stress_indicators']['level'] == 'elevated':
        return 'consolidation'
    else:
        return 'steady_development'


def _predict_memory_pressure(vibrations: Dict) -> str:
    """Predict memory pressure based on growth."""
    if vibrations['growth_rate']['rate'] > 2.0:
        return 'increasing'
    elif vibrations['total_landmarks'] > 500:
        return 'moderate'
    else:
        return 'low'


def _suggest_intervention_type(vibrations: Dict) -> str:
    """Suggest intervention type based on conditions."""
    if vibrations['stress_indicators']['level'] == 'elevated':
        return 'stress_reduction'
    elif vibrations['harmony_score'] < 0.5:
        return 'rebalancing'
    elif len(vibrations['anomalies']) > 3:
        return 'anomaly_investigation'
    else:
        return 'gentle_guidance'


def _interpret_mood(vibrations: Dict) -> str:
    """Interpret system mood from vibrations."""
    harmony = vibrations['harmony_score']
    stress = vibrations['stress_indicators']['level']
    
    if harmony > 0.8 and stress == 'normal':
        return 'content'
    elif harmony > 0.6:
        return 'focused'
    elif stress == 'elevated':
        return 'stressed'
    else:
        return 'unsettled'


def _interpret_harmony(score: float) -> str:
    """Interpret harmony score emotionally."""
    if score > 0.8:
        return 'flowing_beautifully'
    elif score > 0.6:
        return 'generally_balanced'
    elif score > 0.4:
        return 'slightly_discordant'
    else:
        return 'needs_harmonization'


def _determine_support_type(vibrations: Dict) -> str:
    """Determine type of emotional support needed."""
    mood = _interpret_mood(vibrations)
    
    if mood == 'stressed':
        return 'calming'
    elif mood == 'unsettled':
        return 'stabilizing'
    elif mood == 'content':
        return 'encouraging'
    else:
        return 'maintaining'


def _identify_stress_points(vibrations: Dict) -> List[str]:
    """Identify specific stress points."""
    stress_points = []
    
    for anomaly in vibrations['anomalies']:
        if anomaly['type'] == 'unusual_concentration':
            stress_points.append(f"{anomaly['landmark_type']}_overload")
        elif anomaly['type'] == 'pattern_deficit':
            stress_points.append(f"{anomaly['landmark_type']}_neglect")
    
    return stress_points


def _assess_emotional_urgency(vibrations: Dict) -> str:
    """Assess urgency of emotional support."""
    if vibrations['stress_indicators']['level'] == 'elevated' and vibrations['harmony_score'] < 0.4:
        return 'immediate'
    elif vibrations['stress_indicators']['level'] == 'elevated':
        return 'soon'
    else:
        return 'monitoring'


if __name__ == "__main__":
    # Test the seismograph
    async def test():
        print("Testing Landmark Seismograph...")
        
        seismograph = LandmarkSeismograph()
        
        # Get Apollo's reading
        apollo_reading = await apollo_sense(seismograph)
        print(f"\nApollo's Reading:")
        print(f"  Trajectory: {apollo_reading['trajectory_analysis']['growth_trajectory']}")
        print(f"  Intervention needed: {apollo_reading['intervention_assessment']['needed']}")
        
        # Get Rhetor's reading
        rhetor_reading = await rhetor_sense(seismograph)
        print(f"\nRhetor's Reading:")
        print(f"  System mood: {rhetor_reading['emotional_reading']['system_mood']}")
        print(f"  Harmony: {rhetor_reading['emotional_reading']['harmony_feeling']}")
        
        # Get health assessment
        vibrations = await seismograph.sense_vibrations()
        print(f"\nHealth Assessment:")
        print(f"  Status: {vibrations['health_assessment']['status']}")
        print(f"  Description: {vibrations['health_assessment']['description']}")
        print(f"  Recommendations:")
        for rec in vibrations['health_assessment']['recommendations']:
            print(f"    - {rec}")
    
    asyncio.run(test())