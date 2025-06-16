#!/usr/bin/env python

from setuptools import setup, find_packages
import os

requires = [
    'fastapi>=0.100.0',
    'uvicorn>=0.22.0',
    'pydantic>=2.0.0',
    'asyncio',
    'aiohttp',
    'sse-starlette',
    'websockets',
    'matplotlib',  # Optional for visualizations
    'networkx',    # Optional for visualizations
    'requests',
    'python-multipart',
    'tekton-core>=0.1.0',  # FastMCP integration
]

setup(
    name="telos",
    version="0.1.0",
    description="Requirements Management, Tracing and Validation for Tekton",
    long_description="Telos provides a comprehensive system for documenting, organizing, tracking, and validating project requirements with hierarchical visualization and bidirectional tracing capabilities.",
    author="Tekton Project",
    author_email="tekton@example.com",
    url="https://github.com/example/tekton",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "telos": ["ui/templates/*.html", "ui/static/css/*.css", "ui/static/js/*.js"],
    },
    install_requires=requires,
    entry_points={
        'console_scripts': [
            'telos=telos.ui.cli:main',
            'telos-api=telos.api.app:start_server',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
