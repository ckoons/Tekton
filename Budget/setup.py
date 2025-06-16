from setuptools import setup, find_packages

setup(
    name="budget",
    version="0.1.0",
    description="Tekton Budget Component for LLM token and cost management",
    author="Tekton Team",
    author_email="noreply@tekton.ai",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pydantic",
        "aiohttp",
        "click",
        "python-dotenv",
        "websockets",
        "beautifulsoup4",
        "litellm",
        "tekton-core>=0.1.0"
    ],
    entry_points={
        'console_scripts': [
            'budget=budget.cli.main:main',
        ],
    },
)