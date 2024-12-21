from setuptools import setup, find_packages

setup(
    name="github-code-reviewer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "PyGithub>=2.1.1",
        "PyYAML>=6.0.1",
    ],
    python_requires=">=3.10",
)
