from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Allow for minimal installation with basic dependencies
# Full dependencies are in requirements.txt
basic_requirements = [
    "pydantic>=2.4.0",
    "sqlalchemy>=2.0.0",
    "typer>=0.9.0",
    "rich>=13.3.5",
    "python-dotenv>=1.0.0",
    "tekton-core>=0.1.0",
]

# Try to read requirements.txt, but don't fail if it's not available
# This makes it easier to install in agent-specific environments
try:
    with open("requirements.txt", "r", encoding="utf-8") as f:
        requirements = f.read().splitlines()
except FileNotFoundError:
    requirements = basic_requirements

setup(
    name="ergon",
    version="0.1.0",
    author="AI Agent Team",
    author_email="info@example.com",
    description="Ergon: Intelligent Tool, Agent, and Workflow Manager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ckoons/Ergon",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ergon=ergon.cli.main:app",
        ],
    },
    include_package_data=True,
)
