#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
JSONFlow安装脚本
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="jsonflow",
    version="0.1.1",
    author="JSONFlow Contributors",
    author_email="example@example.com",
    description="A library for processing JSON data with operators and pipelines",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/guru4elephant/jsonflow",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "openai>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black",
            "flake8",
            "pytest-cov",
            "twine",
            "build",
        ],
        "bos": [
            "bce-python-sdk>=0.8.0",
        ],
        "all": [
            "bce-python-sdk>=0.8.0",
            "pytest>=6.0",
            "black",
            "flake8",
            "pytest-cov",
            "twine",
            "build",
        ],
    },
    entry_points={
        "console_scripts": [
            "jsonflow=jsonflow.cli:main",
        ],
    },
) 