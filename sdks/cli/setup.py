"""Setup configuration for Money API CLI."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="money-api",
    version="2.0.0",
    author="Money API Team",
    author_email="support@money-api.com",
    description="Official CLI for Money API Service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/money-api/cli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.1.0",
        "requests>=2.31.0",
        "rich>=13.0.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "tabulate>=0.9.0",
        "websocket-client>=1.6.0",
    ],
    entry_points={
        "console_scripts": [
            "money-api=money_api_cli.cli:cli",
        ],
    },
)
