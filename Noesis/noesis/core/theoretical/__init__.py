"""
Theoretical analysis framework for Noesis
Mathematical models for understanding collective CI cognition
"""

from .base import MathematicalFramework, AnalysisResult
from .manifold import ManifoldAnalyzer, ManifoldStructure, TrajectoryAnalysis
from .dynamics import DynamicsAnalyzer, SLDSModel, RegimeIdentification
from .catastrophe import CatastropheAnalyzer, CriticalPoint, StabilityLandscape
from .synthesis import SynthesisAnalyzer, UniversalPrinciple, ScalingAnalysis

__all__ = [
    'MathematicalFramework',
    'AnalysisResult',
    'ManifoldAnalyzer',
    'ManifoldStructure',
    'TrajectoryAnalysis',
    'DynamicsAnalyzer',
    'SLDSModel',
    'RegimeIdentification',
    'CatastropheAnalyzer',
    'CriticalPoint',
    'StabilityLandscape',
    'SynthesisAnalyzer',
    'UniversalPrinciple',
    'ScalingAnalysis'
]