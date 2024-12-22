<div align="center">
  <h1>⚡ Quick Start Guide</h1>
  
  <p>Get started with GitHub Code Reviewer in minutes</p>

  <p>
    <a href="#installation">Installation</a> •
    <a href="#setup">Setup</a> •
    <a href="#first-review">First Review</a> •
    <a href="#next-steps">Next Steps</a>
  </p>
</div>

## 🚀 One-Minute Setup

### 1️⃣ Installation

# Using pip

pip install github-code-reviewer

# Or clone and install from source

git clone https://github.com/r-log/github-code-reviewer.git
cd github-code-reviewer
pip install -e .

### 2️⃣ Configuration

# Set your GitHub token

export GITHUB_TOKEN=your_token_here

# Create basic config file (optional)

github:
token: ${GITHUB_TOKEN}
api_url: "https://api.github.com"

review:
max_files: 50
file_extensions: - ".py" - ".js"
ignore_patterns: - "tests/" - "docs/"

### 3️⃣ Your First Review

# Basic usage

from github_code_reviewer import Reviewer

reviewer = Reviewer()
reviewer.review_pr("owner/repo", pr_number=123)

# With custom configuration

reviewer = Reviewer(
token="your_token",
config_path="path/to/config.yaml"
)
result = reviewer.review_pr("owner/repo", pr_number=123)

## 🎯 Common Use Cases

### GitHub Actions Integration

name: Code Review
on:
pull_request:
types: [opened, synchronize]

jobs:
review:
runs-on: ubuntu-latest
steps: - uses: actions/checkout@v3 - name: Run Review
env:
GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
run: |
pip install github-code-reviewer
python -m github_code_reviewer review

### Batch Processing

# Review multiple PRs

reviewer = Reviewer()
prs = [123, 124, 125]
results = reviewer.review_multiple_prs("owner/repo", prs)

### Custom Rules

# Define custom review rules

from github_code_reviewer import Rule

class MyCustomRule(Rule):
def review(self, content, file_path):
return {
"issues": [],
"suggestions": ["Consider adding more comments"]
}

## 📚 Next Steps

- 📖 Read the [Full Documentation](../api/README.md)
- ⚙️ Explore [Configuration Options](../guides/configuration.md)
- 🔧 Learn about [Custom Rules](../guides/custom-rules.md)
- 🤝 Check the [Contributing Guide](../contributing/CONTRIBUTING.md)

## ❓ Common Issues

1. Authentication Issues

   - Verify your token has correct permissions
   - Check if token is properly exported

2. Rate Limiting

   - Use authenticated requests
   - Implement caching if needed

3. Configuration
   - Validate YAML syntax
   - Check file paths are correct

## 🆘 Need Help?

- 📋 [Open an Issue](https://github.com/r-log/github-code-reviewer/issues)
- 💬 [Join Discussions](https://github.com/r-log/github-code-reviewer/discussions)
- 📧 Contact maintainers

---

<div align="center">
  <p>Ready to improve your code reviews? Let's get started! 🚀</p>
  <p>Made with ❤️ by the GitHub Code Reviewer team</p>
</div>
