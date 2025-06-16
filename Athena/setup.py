from setuptools import setup, find_packages

setup(
    name="athena",
    version="0.1.0",
    description="Knowledge Graph Engine for Tekton",
    author="Tekton Team",
    author_email="example@example.com",
    packages=find_packages(),
    install_requires=[
        # Graph database
        "neo4j>=4.4.0",
        "py2neo>=2021.2.3",
        
        # API framework
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "websockets>=10.0.0",
        "pydantic>=1.9.0",
        
        # Data processing
        "sqlalchemy>=1.4.0",
        "pandas>=1.3.0",
        "numpy>=1.20.0",
        
        # LLM integration
        "httpx>=0.23.0",
        "jinja2>=3.0.0",
        
        # Utilities
        "python-dotenv>=0.19.0",
        "requests>=2.26.0",
        "aiohttp>=3.8.0",
        
        # Tekton core integration
        "tekton-core>=0.1.0",  # FastMCP is included in tekton-core
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "pytest-asyncio>=0.18.0",
            "black>=21.5b2",
            "flake8>=3.9.0",
            "mypy>=0.812",
        ],
        "ui": [
            "streamlit>=1.10.0",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.9",
)