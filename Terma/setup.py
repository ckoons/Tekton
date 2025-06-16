from setuptools import setup, find_packages

setup(
    name="terma",
    version="0.1.0",
    description="Terminal integration system for Tekton",
    author="Casey Koons",
    author_email="cskoons@gmail.com",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.95.0",
        "uvicorn>=0.21.1",
        "websockets>=11.0.3",
        "pydantic>=1.10.7",
        "python-dotenv>=1.0.0",
        "httpx>=0.24.0",
        "requests>=2.28.2",
        "xterm.js>=5.1.0",
        "ptyprocess>=0.7.0",
    ],
    entry_points={
        "console_scripts": [
            "terma=terma.cli.main:main",
        ],
    },
    python_requires=">=3.10",
)