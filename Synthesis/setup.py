#!/usr/bin/env python3
"""
Setup script for Synthesis - Execution Engine for Tekton
"""

from setuptools import setup, find_packages

setup(
    name="synthesis",
    version="1.0.0",
    description="Execution and integration engine for the Tekton ecosystem",
    author="Tekton Team",
    author_email="info@tekton.ai",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.8.0",
        "pydantic>=1.9.0",
        "fastapi>=0.70.0",
        "uvicorn>=0.15.0",
        "asyncio>=3.4.3",
        "python-dotenv>=0.19.0",
        "websockets>=10.0",
        "httpx>=0.20.0",
        "tekton-llm-client>=0.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-asyncio>=0.16.0",
            "pytest-cov>=2.12.0",
            "black>=21.10b0",
            "isort>=5.9.0",
            "mypy>=0.910",
            "flake8>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "synthesis=synthesis.api.app:main",
            "synthesis-register=synthesis.scripts.register_with_hermes:main",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
)