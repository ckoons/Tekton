from setuptools import setup, find_packages

setup(
    name="tekton-core",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "faiss-cpu>=1.7.4",
        "qdrant-client>=1.7.0",
        "sentence-transformers>=2.2.2",
        "numpy>=1.20.0",
        "torch>=1.10.0",
    ],
    description="Tekton Core - Shared components for the Tekton system",
    author="Casey Koons",
    author_email="cskoons@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
