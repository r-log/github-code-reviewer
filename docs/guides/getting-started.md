# Getting Started with GitHub Code Reviewer

This guide will help you set up and start using GitHub Code Reviewer for automated code reviews.

## Prerequisites

Before you begin, ensure you have:

- Python 3.8 or higher installed
- A GitHub account
- A GitHub Personal Access Token with appropriate permissions
  - `repo` access for private repositories
  - `public_repo` access for public repositories

## Installation

1. Clone the repository:

git clone https://github.com/r-log/github-code-reviewer.git
cd github-code-reviewer

2. Install required dependencies:

pip install -r requirements.txt

3. For development purposes, install additional dependencies:

pip install -r requirements-dev.txt

## Configuration

1. Set up your GitHub token:

export GITHUB_TOKEN=your_token_here

2. Configure the reviewer settings in `config/code-reviewer.yaml`:

github:
token: ${GITHUB_TOKEN}
api_url: "https://api.github.com"

review:
max_files: 50
file_extensions: - ".py" - ".js" - ".ts"
ignore_patterns: - "tests/" - "docs/"

## Basic Usage

1. Run a code review on a pull request:

from github_code_reviewer import Reviewer

reviewer = Reviewer()
reviewer.review_pr("owner/repository", pr_number=123)

2. Set up automated reviews using GitHub Actions:

name: Code Review

on:
pull_request:
types: [opened, synchronize]

jobs:
review:
runs-on: ubuntu-latest
steps: - uses: actions/checkout@v3 - name: Set up Python
uses: actions/setup-python@v4
with:
python-version: '3.8' - name: Install dependencies
run: |
pip install -r requirements.txt - name: Run code review
env:
GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
run: |
python -m github_code_reviewer review

## Development Setup

1. Install pre-commit hooks:

pre-commit install

2. Run tests:

pytest tests/

## Common Issues and Solutions

### Authentication Issues

- Ensure your GitHub token has the correct permissions
- Verify the token is properly set in your environment

### Rate Limiting

- The GitHub API has rate limits
- Use token authentication to get higher rate limits
- Consider implementing caching for frequent operations

## Next Steps

- Read the Configuration Guide for detailed settings
- Check out Usage Examples for more scenarios
- Review the API Documentation for advanced usage
- Learn how to Contribute to the project

## Support

If you encounter any issues:

1. Check the Issues page
2. Review existing discussions
3. Open a new issue with detailed information about your problem
