#!/usr/bin/env python3
"""
Apollo Setup Script

This script installs the Apollo package and its dependencies.
"""

import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="apollo",
    version="0.1.0",
    author="Tekton Team",
    author_email="tekton@example.com",
    description="Apollo - Executive Coordinator for Tekton LLM Operations",
    long_description=read('README.md') if os.path.exists('README.md') else '',
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/tekton",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi>=0.95.0",
        "uvicorn>=0.22.0",
        "pydantic>=1.10.7",
        "requests>=2.28.2",
        "websockets>=11.0.3",
        "aiohttp>=3.8.4",
        "python-dotenv>=1.0.0",
        "click>=8.1.3",
        "tiktoken>=0.4.0"
    ],
    entry_points={
        'console_scripts': [
            'apollo=apollo.cli.main:main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.9",
)