"""Setup file for github-code-reviewer package."""

from setuptools import setup, find_packages

setup(
    name="github-code-reviewer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "PyGithub>=2.1.1",
        "PyYAML>=6.0.1",
        "anthropic",
        "aiosqlite>=0.19.0",
        "jsonschema>=4.21.1",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "pytest-asyncio",
            "black",
            "flake8",
            "mypy",
        ],
    },
    python_requires=">=3.11",
)
