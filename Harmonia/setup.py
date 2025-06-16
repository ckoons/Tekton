from setuptools import setup, find_packages

setup(
    name="harmonia",
    version="0.1.0",
    description="Workflow Orchestration Engine for Tekton",
    author="Tekton Team",
    author_email="example@example.com",
    packages=find_packages(),
    install_requires=[
        "pydantic>=1.9.0",
        "fastapi>=0.68.0",
        "sqlalchemy>=1.4.0",
        "pyzmq>=23.0.0",
        "pyyaml>=6.0",
        "uvicorn>=0.15.0",
        "aiohttp>=3.8.0",
        "websockets>=10.0",
        "python-dotenv>=0.19.0",
        "asyncio>=3.4.3",
        "typing_extensions>=4.0.0",
        "tekton-core>=0.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "pytest-asyncio>=0.16.0",
            "black>=21.5b2",
            "flake8>=3.9.0",
            "mypy>=0.812",
        ]
    },
    entry_points={
        "console_scripts": [
            "harmonia=harmonia.__main__:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.9",
)