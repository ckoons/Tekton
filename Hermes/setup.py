from setuptools import setup, find_packages

setup(
    name="hermes",
    version="0.1.0",
    description="Vector Operations and Messaging Framework for Tekton",
    author="Tekton Team",
    author_email="example@example.com",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20.0",
        "qdrant-client>=1.0.0",
        "faiss-cpu>=1.7.0",
        "sentence-transformers>=2.2.0",
        "pyzmq>=23.0.0",
        "fastapi>=0.68.0",
        "pydantic>=1.9.0",
    ],
    extras_require={
        "gpu": [
            "faiss-gpu>=1.7.0",
            "torch>=1.10.0",
        ],
        "lancedb": [
            "lancedb>=0.1.0",
        ],
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "black>=21.5b2",
            "flake8>=3.9.0",
            "mypy>=0.812",
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