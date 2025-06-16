#!/usr/bin/env python3
"""
Utility functions for spectral analysis.

This module provides FFT and frequency analysis utilities.
"""

import time
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union

logger = logging.getLogger(__name__)


def compute_frequency_components(time_series: List[float], sampling_rate: float = 1.0) -> Tuple[np.ndarray, np.ndarray]:
    """Compute frequency components using FFT.
    
    Args:
        time_series: Time series data
        sampling_rate: Sampling rate in Hz
        
    Returns:
        Tuple of (frequencies, amplitudes)
    """
    try:
        # Convert to numpy array if not already
        series = np.array(time_series)
        
        # Detrend the data to remove linear trends
        series = series - np.mean(series)
        
        # Apply Hamming window to reduce spectral leakage
        window = np.hamming(len(series))
        series = series * window
        
        # Compute FFT
        fft_result = np.fft.rfft(series)
        
        # Get amplitudes (normalized)
        amplitudes = np.abs(fft_result) / len(series)
        
        # Get frequencies
        frequencies = np.fft.rfftfreq(len(series), d=1.0/sampling_rate)
        
        return (frequencies, amplitudes)
    except Exception as e:
        logger.error(f"Error computing frequency components: {str(e)}")
        # Return empty components as fallback
        return (np.array([]), np.array([]))


def calculate_band_powers(freq_components: Tuple[np.ndarray, np.ndarray], frequency_bands: Dict[str, Tuple[float, float]]) -> Dict[str, float]:
    """Calculate power in each frequency band.
    
    Args:
        freq_components: Tuple of (frequencies, amplitudes)
        frequency_bands: Dict mapping band names to (min_freq, max_freq) tuples
        
    Returns:
        Dict mapping band names to power values
    """
    frequencies, amplitudes = freq_components
    if len(frequencies) == 0:
        return {band: 0.0 for band in frequency_bands}
    
    band_powers = {}
    for band_name, (low_freq, high_freq) in frequency_bands.items():
        # Find indices within this band
        band_indices = np.where((frequencies >= low_freq) & (frequencies < high_freq))[0]
        
        # Calculate power (sum of squared amplitudes)
        if len(band_indices) > 0:
            band_power = np.sum(amplitudes[band_indices]**2)
        else:
            band_power = 0.0
            
        band_powers[band_name] = band_power
    
    # Normalize by total power
    total_power = sum(band_powers.values())
    if total_power > 0:
        for band in band_powers:
            band_powers[band] /= total_power
    
    return band_powers


def calculate_spectral_entropy(freq_components: Tuple[np.ndarray, np.ndarray]) -> float:
    """Calculate spectral entropy as a measure of randomness.
    
    Args:
        freq_components: Tuple of (frequencies, amplitudes)
        
    Returns:
        Spectral entropy value (0-1)
    """
    _, amplitudes = freq_components
    if len(amplitudes) <= 1:
        return 0.0
    
    # Calculate power spectral density
    psd = amplitudes**2
    
    # Normalize PSD
    psd_norm = psd / np.sum(psd)
    
    # Remove zeros to avoid log(0)
    psd_norm = psd_norm[psd_norm > 0]
    
    # Calculate entropy
    entropy = -np.sum(psd_norm * np.log2(psd_norm))
    
    # Normalize to 0-1 range
    max_entropy = np.log2(len(psd_norm))
    if max_entropy > 0:
        normalized_entropy = entropy / max_entropy
    else:
        normalized_entropy = 0.0
    
    return normalized_entropy


def detect_dominant_frequencies(freq_components: Tuple[np.ndarray, np.ndarray], max_peaks: int = 5) -> List[Tuple[float, float]]:
    """Detect dominant frequencies in the signal.
    
    Args:
        freq_components: Tuple of (frequencies, amplitudes)
        max_peaks: Maximum number of peaks to return
        
    Returns:
        List of (frequency, amplitude) tuples for dominant frequencies
    """
    frequencies, amplitudes = freq_components
    if len(frequencies) <= 1:
        return []
    
    # Find local maxima
    peak_indices = []
    for i in range(1, len(amplitudes)-1):
        if amplitudes[i] > amplitudes[i-1] and amplitudes[i] > amplitudes[i+1]:
            peak_indices.append(i)
    
    # Sort by amplitude
    peak_indices.sort(key=lambda i: amplitudes[i], reverse=True)
    
    # Get top peaks
    top_peaks = peak_indices[:max_peaks]
    
    # Return as (frequency, amplitude) tuples
    return [(frequencies[i], amplitudes[i]) for i in top_peaks]
