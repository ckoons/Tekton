#!/usr/bin/env python3
from setuptools import setup, find_packages
import os

# Read version from engram/__init__.py
with open(os.path.join("engram", "__init__.py"), "r") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"\'')
            break

# Read long description from README.md
with open("README.md", "r") as f:
    long_description = f.read()

# Define requirements
requirements = [
    "fastapi>=0.103.1",
    "uvicorn>=0.23.2",
    "requests>=2.31.0",
    "python-dotenv>=1.0.0",
    "pydantic>=2.4.2",
    "tekton-core>=0.1.0",
]

# Optional requirements (vector database for memory capabilities)
extras_require = {
    "vector": ["faiss-cpu>=1.7.4"],
}

setup(
    name="engram",
    version=version,
    description="Persistent Memory Traces for AI Assistants",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Casey Koons",
    author_email="cskoons@gmail.com",
    url="https://github.com/cskoons/Engram",
    packages=find_packages(),
    scripts=["engram_consolidated", "engram_start.sh"],
    install_requires=requirements,
    extras_require=extras_require,
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    entry_points={
        "console_scripts": [
            "engram-server=engram.api.server:main",
        ],
    },
)