#!/usr/bin/env python
"""
Setup script for the Prometheus/Epimethius Planning System.
"""

from setuptools import setup, find_packages

setup(
    name="prometheus",
    version="0.1.0",
    description="Prometheus/Epimethius Planning System for Tekton",
    author="Tekton Team",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "pydantic>=1.8.2",
        "aiohttp>=3.8.1",
        "networkx>=2.6.3",  # For graph-based algorithms
        "pandas>=1.3.3",    # For data analysis
        "matplotlib>=3.4.3", # For visualizations
        "python-dateutil>=2.8.2",
        "tekton-core>=0.1.0",  # For MCP support
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.5",
            "black>=21.9b0",
            "isort>=5.9.3",
            "mypy>=0.910",
        ],
    },
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "prometheus-server=prometheus.api.app:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)