<div align="center">
  <h1>🚀 Getting Started with GitHub Code Reviewer</h1>
  
  <p>Your guide to automated code reviews with GitHub Code Reviewer</p>

  <p>
    <a href="#prerequisites">Prerequisites</a> •
    <a href="#installation">Installation</a> •
    <a href="#configuration">Configuration</a> •
    <a href="#usage">Usage</a> •
    <a href="#development">Development</a>
  </p>
</div>

## 📋 Prerequisites

Before diving in, make sure you have:

✅ Python 3.8 or higher installed
✅ A GitHub account
✅ A GitHub Personal Access Token with:

- `repo` access for private repositories
- `public_repo` access for public repositories

## 🛠️ Installation

### 1️⃣ Clone the Repository

git clone https://github.com/r-log/github-code-reviewer.git
cd github-code-reviewer

### 2️⃣ Install Dependencies

# For basic usage

pip install -r requirements.txt

# For development

pip install -r requirements-dev.txt

## ⚙️ Configuration

### 1️⃣ Set Up GitHub Token

export GITHUB_TOKEN=your_token_here

### 2️⃣ Configure Review Settings

Create or modify `config/code-reviewer.yaml`:

github:
token: ${GITHUB_TOKEN}
api_url: "https://api.github.com"

review:
max_files: 50
file_extensions: - ".py" - ".js" - ".ts"
ignore_patterns: - "tests/" - "docs/"

## 🚀 Basic Usage

### 1️⃣ Run Code Review

from github_code_reviewer import Reviewer

reviewer = Reviewer()
reviewer.review_pr("owner/repository", pr_number=123)

### 2️⃣ GitHub Actions Integration

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

## 🔧 Development Setup

### 1️⃣ Install Pre-commit Hooks

pre-commit install

### 2️⃣ Run Tests

pytest tests/

## ❗ Common Issues and Solutions

### 🔑 Authentication Issues

- Verify token permissions
- Check token environment variable
- Ensure token is valid and not expired

### ⚡ Rate Limiting

- Use authenticated requests
- Implement request caching
- Monitor API usage limits

## 📚 Next Steps

Explore more about GitHub Code Reviewer:

📖 [Configuration Guide](configuration.md)
🎯 [Usage Examples](../examples/basic-usage.md)
📘 [API Documentation](../api/README.md)
🤝 [Contributing Guide](../contributing/CONTRIBUTING.md)

## 🆘 Support

Need help? We've got you covered:

1. 📋 Browse our [Issues](https://github.com/r-log/github-code-reviewer/issues)
2. 💬 Join existing discussions
3. 🔍 Search for similar problems
4. ❓ Open a new issue with details about your problem

---

<div align="center">
  <p>Happy Coding! 🎉</p>
  <p>Made with ❤️ by r-log</p>
</div>
