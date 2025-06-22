"""
Setup for Tekton Landmarks package
"""

from setuptools import setup, find_packages

setup(
    name="tekton-landmarks",
    version="0.1.0",
    description="Persistent memory system for Tekton Companion Intelligences",
    author="Tekton Team",
    packages=find_packages(),
    install_requires=[
        # No external dependencies, using only stdlib
    ],
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'tekton-landmark=landmarks.tools.cli:main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)