# This file can be empty, it's just to make the src directory a Python package

"""GitHub Code Reviewer package."""
from github import Auth
from .reviewer import CodeReviewer

__version__ = '0.1.0'
__all__ = ['CodeReviewer']
