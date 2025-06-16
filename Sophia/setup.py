#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="sophia",
    version="0.1.0",
    description="Machine learning and continuous improvement component for the Tekton ecosystem",
    author="Tekton Team",
    author_email="noreply@example.com",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        # Core dependencies
        "fastapi>=0.95.0",
        "uvicorn[standard]>=0.21.1",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "httpx>=0.24.0",
        "websockets>=10.4",
        
        # Data processing and analysis
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "pandas>=2.0.0",
        "scikit-learn>=1.2.0",
        
        # Storage
        "sqlalchemy>=2.0.0",
        "aiosqlite>=0.18.0",
        "aiofiles>=23.1.0",
        
        # Integration
        "requests>=2.28.0",
        
        # Visualization (for reports)
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        
        # Tekton-specific
        "tekton-llm-client>=0.1.0",
    ],
    extras_require={
        "test": [
            "pytest>=7.3.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
        ],
        "dev": [
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
