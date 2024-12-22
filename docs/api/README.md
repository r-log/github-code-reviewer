<div align="center">
  <h1>🔌 API Documentation</h1>
  
  <p>Complete API reference for GitHub Code Reviewer</p>

  <p>
    <a href="#core-api">Core API</a> •
    <a href="#configuration">Configuration</a> •
    <a href="#review-rules">Rules</a> •
    <a href="#examples">Examples</a>
  </p>
</div>

## 🎯 Core API

### Reviewer Class

The main class for performing code reviews.

from github_code_reviewer import Reviewer

# Initialize with default settings

reviewer = Reviewer()

# Initialize with custom settings

reviewer = Reviewer(
token="your_github_token",
api_url="https://api.github.com",
config_path="path/to/config.yaml"
)

#### Methods

##### `review_pr()`

Review a specific pull request.

reviewer.review_pr(
repo="owner/repository",
pr_number=123,
rules=["style", "security", "performance"]
)

##### `review_commit()`

Review a specific commit.

reviewer.review_commit(
repo="owner/repository",
commit_sha="abc123",
rules=["style", "security"]
)

## ⚙️ Configuration

### Configuration Object

from github_code_reviewer import Config

config = Config(
github_token="your_token",
max_files=50,
file_extensions=[".py", ".js", ".ts"],
ignore_patterns=["tests/", "docs/"]
)

### YAML Configuration

github:
token: ${GITHUB_TOKEN}
api_url: "https://api.github.com"

review:
max_files: 50
file_extensions: - ".py" - ".js" - ".ts"
ignore_patterns: - "tests/" - "docs/"

## 📋 Review Rules

### Built-in Rules

| Rule            | Description                         | Default |
| --------------- | ----------------------------------- | ------- |
| `style`         | Code style checks                   | ✅      |
| `security`      | Security vulnerability checks       | ✅      |
| `performance`   | Performance improvement suggestions | ✅      |
| `documentation` | Documentation completeness          | ❌      |

### Custom Rules

Create your own review rules:

from github_code_reviewer import Rule

class CustomRule(Rule):
def **init**(self):
self.name = "custom_rule"
self.description = "My custom review rule"

    def review(self, content, file_path):
        # Your review logic here
        return {
            "issues": [],
            "suggestions": []
        }

## 🎯 Examples

### Basic Review

from github_code_reviewer import Reviewer

# Initialize reviewer

reviewer = Reviewer(token="your_github_token")

# Review a PR

result = reviewer.review_pr("owner/repo", pr_number=123)

# Print results

for issue in result.issues:
print(f"Issue: {issue.message} in {issue.file}:{issue.line}")

### Custom Configuration

from github_code_reviewer import Reviewer, Config

# Create custom configuration

config = Config(
max_files=100,
file_extensions=[".py"],
ignore_patterns=["tests/"]
)

# Initialize reviewer with custom config

reviewer = Reviewer(config=config)

# Review with custom rules

result = reviewer.review_pr(
"owner/repo",
pr_number=123,
rules=["style", "custom_rule"]
)

### GitHub Actions Integration

from github_code_reviewer import Reviewer, GithubActions

# Initialize for GitHub Actions

reviewer = Reviewer.from_github_actions()

# Automatically review PR

reviewer.review_current_pr()

## 🔄 Workflow Integration

### Event Handlers

from github_code_reviewer import Reviewer

reviewer = Reviewer()

@reviewer.on_issue_found
def handle_issue(issue):
print(f"Found issue: {issue.message}")

@reviewer.on_review_complete
def handle_complete(result):
print(f"Review complete: {len(result.issues)} issues found")

## 🛠️ Advanced Usage

### Batch Processing

from github_code_reviewer import Reviewer

reviewer = Reviewer()

# Review multiple PRs

prs = [123, 124, 125]
results = reviewer.review_multiple_prs("owner/repo", prs)

# Review repository

repo_results = reviewer.review_repository(
"owner/repo",
branch="main",
max_commits=10
)

## 📚 Additional Resources

- 📖 [Getting Started Guide](../guides/getting-started.md)
- ⚙️ [Configuration Guide](../guides/configuration.md)
- 🤝 [Contributing](../contributing/CONTRIBUTING.md)
- 🐛 [License](../../LICENSE) (Apache 2.0)
- 🐛 [Issue Tracker](https://github.com/r-log/github-code-reviewer/issues)

---

<div align="center">
  <p>Need help? Join our <a href="https://github.com/r-log/github-code-reviewer/discussions">discussions</a>!</p>
  <p>Made with ❤️ by r-log</p>
</div>
