#!/usr/bin/env python3
"""
Setup script for the Tekton LLM Client package.
"""

from setuptools import setup, find_packages

setup(
    name="tekton-llm-client",
    version="0.1.0",
    description="Unified LLM client for Tekton components",
    author="Tekton Project",
    author_email="tekton@example.com",
    url="https://github.com/cskoons/Tekton",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.8.0",
        "websockets>=10.3",
        "pydantic>=1.9.0",
        "anthropic>=0.5.0",
        "requests>=2.28.0",
        "python-dotenv>=0.20.0",
    ],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)