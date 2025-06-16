#!/usr/bin/env python

from setuptools import setup, find_packages
import os

# Read requirements from file
with open('requirements.txt') as f:
    requires = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="metis",
    version="0.1.0",
    description="Task Management System for Tekton",
    author="Tekton Project",
    author_email="tekton@example.com",
    url="https://github.com/example/tekton",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    entry_points={
        'console_scripts': [
            'metis=metis.__main__:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.8',
)