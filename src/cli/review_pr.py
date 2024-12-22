#!/usr/bin/env python3
"""Command line interface for GitHub code reviewer."""

import sys
from src.ai.reviewer import Reviewer


def main():
    """Main entry point."""
    if len(sys.argv) != 3:
        print("Usage: review_pr.py <repository> <pr_number>")
        sys.exit(1)

    repository = sys.argv[1]
    pr_number = int(sys.argv[2])

    reviewer = Reviewer()
    reviewer.review_pr(repository, pr_number)


if __name__ == "__main__":
    main()
