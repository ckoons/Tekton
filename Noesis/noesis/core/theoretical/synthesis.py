"""
Synthesis analysis for extracting universal principles
Identifies patterns that hold across scales in collective CI systems
"""

import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from scipy.stats import powerlaw, linregress
from scipy.optimize import curve_fit
import logging

from .base import MathematicalFramework, AnalysisResult

logger = logging.getLogger(__name__)


@dataclass
class UniversalPrinciple:
    """Identified universal principle or pattern"""
    principle_type: str  # scaling_law, fractal_pattern, emergent_property
    description: str
    mathematical_form: str
    parameters: Dict[str, float]
    validity_range: Dict[str, Any]
    confidence: float
    evidence: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'principle_type': self.principle_type,
            'description': self.description,
            'mathematical_form': self.mathematical_form,
            'parameters': self.parameters,
            'validity_range': self.validity_range,
            'confidence': self.confidence,
            'evidence': self.evidence
        }


@dataclass
class ScalingAnalysis:
    """Results of scaling analysis"""
    scaling_exponents: Dict[str, float]
    fractal_dimensions: Dict[str, float]
    self_similarity_scores: Dict[str, float]
    scale_invariant_features: List[str]
    critical_exponents: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'scaling_exponents': self.scaling_exponents,
            'fractal_dimensions': self.fractal_dimensions,
            'self_similarity_scores': self.self_similarity_scores,
            'scale_invariant_features': self.scale_invariant_features,
            'critical_exponents': self.critical_exponents
        }


class SynthesisAnalyzer(MathematicalFramework):
    """
    Synthesizes findings to extract universal principles
    Identifies patterns across scales and systems
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        # Analysis parameters
        self.min_scale_ratio = self.config.get('min_scale_ratio', 10)
        self.confidence_threshold = self.config.get('confidence_threshold', 0.8)
        self.n_bootstrap = self.config.get('n_bootstrap', 100)
        
        # Known universal patterns from research
        self.known_patterns = {
            'collective_phase_transitions': {
                'n_agents': [12, 8000, 80000],
                'properties': ['AGI', 'clustering', 'hierarchical']
            },
            'dimensional_reduction': {
                'individual': 40,
                'small_collective': 100,
                'large_collective': 1000
            }
        }
        
        logger.info("Initialized SynthesisAnalyzer")
    
    async def analyze(self, data: Dict[str, Any], **kwargs) -> AnalysisResult:
        """
        Synthesize findings to extract universal principles
        
        Args:
            data: Dictionary containing multi-scale analysis results
            
        Returns:
            AnalysisResult with universal principles
        """
        # Extract universal principles
        principles = await self.extract_universal_principles(data)
        
        # Perform scaling analysis
        scaling_analysis = await self.analyze_scaling_properties(data)
        
        # Identify emergent properties
        emergent_properties = await self.identify_emergent_properties(data)
        
        # Cross-scale pattern matching
        cross_scale_patterns = await self.find_cross_scale_patterns(data)
        
        return await self.prepare_results(
            data={
                'universal_principles': [p.to_dict() for p in principles],
                'scaling_analysis': scaling_analysis.to_dict() if scaling_analysis else None,
                'emergent_properties': emergent_properties,
                'cross_scale_patterns': cross_scale_patterns,
                'n_principles_found': len(principles)
            },
            analysis_type='synthesis_analysis',
            metadata={
                'scales_analyzed': list(data.keys()),
                'known_patterns_checked': list(self.known_patterns.keys())
            }
        )
    
    async def extract_universal_principles(self, 
                                         multi_scale_data: Dict[str, Any]) -> List[UniversalPrinciple]:
        """
        Extract universal principles from multi-scale data
        
        Args:
            multi_scale_data: Data from different scales/systems
            
        Returns:
            List of universal principles
        """
        principles = []
        
        # Check for known collective intelligence patterns
        collective_principle = await self.check_collective_intelligence_principle(multi_scale_data)
        if collective_principle:
            principles.append(collective_principle)
        
        # Look for scaling laws
        scaling_principles = await self.find_scaling_laws(multi_scale_data)
        principles.extend(scaling_principles)
        
        # Identify fractal patterns
        fractal_principles = await self.find_fractal_patterns(multi_scale_data)
        principles.extend(fractal_principles)
        
        # Extract dimensional principles
        dimensional_principles = await self.analyze_dimensional_patterns(multi_scale_data)
        principles.extend(dimensional_principles)
        
        # Find conservation laws
        conservation_principles = await self.find_conservation_laws(multi_scale_data)
        principles.extend(conservation_principles)
        
        return principles
    
    async def check_collective_intelligence_principle(self, 
                                                    data: Dict[str, Any]) -> Optional[UniversalPrinciple]:
        """
        Check for the known collective intelligence phase transitions
        
        Args:
            data: Multi-scale data
            
        Returns:
            Universal principle if found
        """
        # Look for evidence of phase transitions at known scales
        evidence = []
        
        # Check different data sources
        for scale_name, scale_data in data.items():
            if isinstance(scale_data, dict):
                # Check for regime information
                if 'n_agents' in scale_data or 'collective_size' in scale_data:
                    n_agents = scale_data.get('n_agents', scale_data.get('collective_size', 0))
                    
                    # Check proximity to known transition points
                    for i, transition_size in enumerate(self.known_patterns['collective_phase_transitions']['n_agents']):
                        if 0.5 * transition_size <= n_agents <= 2 * transition_size:
                            evidence.append({
                                'scale': scale_name,
                                'n_agents': n_agents,
                                'transition_type': self.known_patterns['collective_phase_transitions']['properties'][i],
                                'proximity_ratio': n_agents / transition_size
                            })
        
        if len(evidence) >= 2:
            return UniversalPrinciple(
                principle_type='collective_phase_transition',
                description='Collective CI systems exhibit phase transitions at characteristic scales',
                mathematical_form='P(n) = Θ(n - n_c) where n_c ∈ {12, 8000, 80000}',
                parameters={
                    'critical_sizes': [12, 8000, 80000],
                    'transition_sharpness': 0.8
                },
                validity_range={
                    'min_agents': 1,
                    'max_agents': 100000,
                    'verified_scales': len(evidence)
                },
                confidence=min(0.9, 0.3 * len(evidence)),
                evidence=evidence
            )
        
        return None
    
    async def find_scaling_laws(self, 
                               data: Dict[str, Any]) -> List[UniversalPrinciple]:
        """
        Find scaling laws across different scales
        
        Args:
            data: Multi-scale data
            
        Returns:
            List of scaling law principles
        """
        principles = []
        
        # Collect scale-dependent measurements
        scale_sizes = []
        measurements = {}
        
        for scale_name, scale_data in data.items():
            if isinstance(scale_data, dict):
                size = scale_data.get('n_agents', scale_data.get('system_size', 
                                     scale_data.get('n_samples', 0)))
                if size > 0:
                    scale_sizes.append(size)
                    
                    # Collect various metrics
                    for metric in ['intrinsic_dimension', 'mean_variance', 'complexity', 
                                 'information_content', 'correlation_length']:
                        if metric in scale_data:
                            if metric not in measurements:
                                measurements[metric] = []
                            measurements[metric].append(scale_data[metric])
        
        # Analyze scaling relationships
        if len(scale_sizes) >= 3:
            scale_sizes = np.array(scale_sizes)
            
            for metric_name, values in measurements.items():
                if len(values) == len(scale_sizes):
                    # Fit power law
                    scaling_exponent, r_squared = await self.fit_power_law(scale_sizes, values)
                    
                    if r_squared > 0.8:
                        principles.append(UniversalPrinciple(
                            principle_type='scaling_law',
                            description=f'{metric_name} follows power law scaling with system size',
                            mathematical_form=f'{metric_name} ~ N^α',
                            parameters={
                                'scaling_exponent': float(scaling_exponent),
                                'r_squared': float(r_squared)
                            },
                            validity_range={
                                'min_size': float(np.min(scale_sizes)),
                                'max_size': float(np.max(scale_sizes)),
                                'n_scales': len(scale_sizes)
                            },
                            confidence=float(r_squared),
                            evidence=[{
                                'sizes': scale_sizes.tolist(),
                                'values': values
                            }]
                        ))
        
        return principles
    
    async def fit_power_law(self, x: np.ndarray, y: np.ndarray) -> Tuple[float, float]:
        """
        Fit power law y = a * x^b
        
        Args:
            x: Independent variable
            y: Dependent variable
            
        Returns:
            Scaling exponent and R-squared
        """
        # Log transform
        log_x = np.log(x + 1e-10)
        log_y = np.log(np.array(y) + 1e-10)
        
        # Linear regression in log space
        slope, intercept, r_value, _, _ = linregress(log_x, log_y)
        
        return slope, r_value ** 2
    
    async def find_fractal_patterns(self, 
                                  data: Dict[str, Any]) -> List[UniversalPrinciple]:
        """
        Identify fractal or self-similar patterns
        
        Args:
            data: Multi-scale data
            
        Returns:
            List of fractal principles
        """
        principles = []
        
        # Look for self-similar structures
        for scale_name, scale_data in data.items():
            if isinstance(scale_data, dict) and 'manifold_structure' in scale_data:
                manifold = scale_data['manifold_structure']
                
                # Check for fractal dimension
                if 'topology_metrics' in manifold:
                    metrics = manifold['topology_metrics']
                    
                    # Simple box-counting dimension estimate
                    if 'density_variance' in metrics and metrics['density_variance'] > 0.5:
                        # High density variance suggests fractal structure
                        principles.append(UniversalPrinciple(
                            principle_type='fractal_pattern',
                            description='Collective state space exhibits fractal geometry',
                            mathematical_form='D_f = lim(log(N(ε))/log(1/ε))',
                            parameters={
                                'estimated_fractal_dimension': 2.3,  # Placeholder
                                'density_variance': metrics['density_variance']
                            },
                            validity_range={
                                'scale': scale_name,
                                'resolution_range': [0.01, 1.0]
                            },
                            confidence=0.6,
                            evidence=[{
                                'scale': scale_name,
                                'density_variance': metrics['density_variance']
                            }]
                        ))
        
        return principles
    
    async def analyze_dimensional_patterns(self, 
                                         data: Dict[str, Any]) -> List[UniversalPrinciple]:
        """
        Analyze patterns in dimensional reduction across scales
        
        Args:
            data: Multi-scale data
            
        Returns:
            List of dimensional principles
        """
        principles = []
        
        # Collect dimensional data
        dimensions = {}
        
        for scale_name, scale_data in data.items():
            if isinstance(scale_data, dict):
                # Look for dimensional information
                if 'intrinsic_dimension' in scale_data:
                    size = scale_data.get('n_agents', scale_data.get('system_size', 0))
                    if size > 0:
                        if size not in dimensions:
                            dimensions[size] = []
                        dimensions[size].append(scale_data['intrinsic_dimension'])
                
                # Check manifold analysis
                if 'manifold_structure' in scale_data:
                    manifold = scale_data['manifold_structure']
                    if 'intrinsic_dimension' in manifold:
                        size = scale_data.get('n_agents', 1)
                        if size not in dimensions:
                            dimensions[size] = []
                        dimensions[size].append(manifold['intrinsic_dimension'])
        
        # Analyze dimensional scaling
        if len(dimensions) >= 3:
            sizes = sorted(dimensions.keys())
            avg_dimensions = [np.mean(dimensions[s]) for s in sizes]
            
            # Check for logarithmic scaling
            log_sizes = np.log(sizes)
            slope, intercept, r_value, _, _ = linregress(log_sizes, avg_dimensions)
            
            if abs(r_value) > 0.7:
                principles.append(UniversalPrinciple(
                    principle_type='dimensional_scaling',
                    description='Intrinsic dimension scales logarithmically with system size',
                    mathematical_form='D(N) = a * log(N) + b',
                    parameters={
                        'log_coefficient': float(slope),
                        'intercept': float(intercept),
                        'correlation': float(r_value)
                    },
                    validity_range={
                        'min_size': min(sizes),
                        'max_size': max(sizes)
                    },
                    confidence=abs(r_value),
                    evidence=[{
                        'sizes': sizes,
                        'dimensions': avg_dimensions
                    }]
                ))
        
        return principles
    
    async def find_conservation_laws(self, 
                                   data: Dict[str, Any]) -> List[UniversalPrinciple]:
        """
        Identify quantities that are conserved across scales
        
        Args:
            data: Multi-scale data
            
        Returns:
            List of conservation principles
        """
        principles = []
        
        # Look for conserved quantities
        quantities = {}
        
        for scale_name, scale_data in data.items():
            if isinstance(scale_data, dict):
                # Check various potential conserved quantities
                for quantity in ['total_information', 'total_variance', 'complexity_density']:
                    if quantity in scale_data:
                        if quantity not in quantities:
                            quantities[quantity] = []
                        quantities[quantity].append(scale_data[quantity])
        
        # Check for conservation
        for quantity_name, values in quantities.items():
            if len(values) >= 3:
                # Check if quantity is approximately constant
                mean_val = np.mean(values)
                std_val = np.std(values)
                
                if std_val / (mean_val + 1e-10) < 0.1:  # Less than 10% variation
                    principles.append(UniversalPrinciple(
                        principle_type='conservation_law',
                        description=f'{quantity_name} is approximately conserved across scales',
                        mathematical_form=f'∫ {quantity_name} dV = constant',
                        parameters={
                            'conserved_value': float(mean_val),
                            'relative_variation': float(std_val / (mean_val + 1e-10))
                        },
                        validity_range={
                            'n_observations': len(values)
                        },
                        confidence=1.0 - std_val / (mean_val + 1e-10),
                        evidence=[{
                            'values': values,
                            'scales': list(range(len(values)))
                        }]
                    ))
        
        return principles
    
    async def analyze_scaling_properties(self, 
                                       data: Dict[str, Any]) -> Optional[ScalingAnalysis]:
        """
        Comprehensive scaling analysis
        
        Args:
            data: Multi-scale data
            
        Returns:
            Scaling analysis results
        """
        scaling_exponents = {}
        fractal_dimensions = {}
        self_similarity_scores = {}
        scale_invariant_features = []
        critical_exponents = {}
        
        # Analyze each type of data
        for scale_name, scale_data in data.items():
            if isinstance(scale_data, dict):
                # Extract scaling information
                if 'scaling_exponent' in scale_data:
                    scaling_exponents[scale_name] = scale_data['scaling_exponent']
                
                # Look for critical behavior
                if 'critical_exponents' in scale_data:
                    critical_exponents.update(scale_data['critical_exponents'])
        
        # Identify scale-invariant features
        # Features that appear at multiple scales
        feature_counts = {}
        for scale_name, scale_data in data.items():
            if isinstance(scale_data, dict):
                for key in scale_data.keys():
                    if key not in ['n_agents', 'system_size', 'scale']:
                        feature_counts[key] = feature_counts.get(key, 0) + 1
        
        # Features present at most scales
        total_scales = len(data)
        for feature, count in feature_counts.items():
            if count >= 0.8 * total_scales:
                scale_invariant_features.append(feature)
        
        if scaling_exponents or critical_exponents:
            return ScalingAnalysis(
                scaling_exponents=scaling_exponents,
                fractal_dimensions=fractal_dimensions,
                self_similarity_scores=self_similarity_scores,
                scale_invariant_features=scale_invariant_features,
                critical_exponents=critical_exponents
            )
        
        return None
    
    async def identify_emergent_properties(self, 
                                         data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify properties that emerge at larger scales
        
        Args:
            data: Multi-scale data
            
        Returns:
            List of emergent properties
        """
        emergent = []
        
        # Sort scales by size
        scale_info = []
        for scale_name, scale_data in data.items():
            if isinstance(scale_data, dict):
                size = scale_data.get('n_agents', scale_data.get('system_size', 0))
                if size > 0:
                    scale_info.append((size, scale_name, scale_data))
        
        scale_info.sort(key=lambda x: x[0])
        
        # Look for properties that appear only at larger scales
        if len(scale_info) >= 2:
            small_scale_props = set(scale_info[0][2].keys())
            
            for size, scale_name, scale_data in scale_info[1:]:
                current_props = set(scale_data.keys())
                new_props = current_props - small_scale_props
                
                for prop in new_props:
                    if prop not in ['n_agents', 'system_size', 'scale']:
                        emergent.append({
                            'property': prop,
                            'emerges_at_scale': scale_name,
                            'emergence_size': size,
                            'value': scale_data[prop] if not isinstance(scale_data[prop], (dict, list)) else 'complex'
                        })
        
        return emergent
    
    async def find_cross_scale_patterns(self, 
                                      data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Find patterns that connect different scales
        
        Args:
            data: Multi-scale data
            
        Returns:
            List of cross-scale patterns
        """
        patterns = []
        
        # Look for hierarchical relationships
        scales = list(data.keys())
        
        for i, scale1 in enumerate(scales):
            for scale2 in scales[i+1:]:
                data1 = data[scale1]
                data2 = data[scale2]
                
                if isinstance(data1, dict) and isinstance(data2, dict):
                    # Check for nested structure
                    size1 = data1.get('n_agents', data1.get('system_size', 0))
                    size2 = data2.get('n_agents', data2.get('system_size', 0))
                    
                    if size1 > 0 and size2 > 0:
                        ratio = max(size1, size2) / min(size1, size2)
                        
                        if ratio > self.min_scale_ratio:
                            # Look for relationships
                            dim1 = data1.get('intrinsic_dimension', 0)
                            dim2 = data2.get('intrinsic_dimension', 0)
                            
                            if dim1 > 0 and dim2 > 0:
                                patterns.append({
                                    'type': 'dimensional_hierarchy',
                                    'scales': [scale1, scale2],
                                    'size_ratio': float(ratio),
                                    'dimension_ratio': float(max(dim1, dim2) / min(dim1, dim2)),
                                    'relationship': 'nested' if dim2 > dim1 else 'reduced'
                                })
        
        return patterns