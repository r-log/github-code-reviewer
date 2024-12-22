<div align="center">
  <h1>🤖 GitHub Code Reviewer</h1>
  
  <p>An intelligent code review assistant powered by Python</p>

  <p>
    <a href="#features">Features</a> •
    <a href="#installation">Installation</a> •
    <a href="#usage">Usage</a> •
    <a href="#documentation">Docs</a> •
    <a href="#contributing">Contributing</a>
  </p>

  <p>
    <img src="https://img.shields.io/github/license/r-log/github-code-reviewer" alt="License">
    <img src="https://img.shields.io/github/stars/r-log/github-code-reviewer" alt="Stars">
    <img src="https://img.shields.io/github/forks/r-log/github-code-reviewer" alt="Forks">
    <img src="https://img.shields.io/github/issues/r-log/github-code-reviewer" alt="Issues">
  </p>
</div>

## ✨ Features

🔍 **Automated Code Review**

- Smart code analysis
- Style guide enforcement
- Best practices checking

🚀 **Easy Integration**

- GitHub Actions support
- Simple API
- Customizable rules

⚡ **Performance**

- Fast analysis
- Minimal setup
- Efficient processing

## 🛠️ Installation

# Clone the repository

git clone https://github.com/r-log/github-code-reviewer.git

# Install dependencies

pip install -r requirements.txt

## 📖 Usage

1. Set up your GitHub token:

export GITHUB_TOKEN=your_token_here

2. Run a code review:

from github_code_reviewer import Reviewer

reviewer = Reviewer()
reviewer.review_pr("owner/repository", pr_number=123)

## 📚 Documentation

Explore our comprehensive documentation:

- 📝 [Getting Started Guide](docs/guides/getting-started.md)
- ⚙️ [Configuration Guide](docs/guides/configuration.md)
- 🔧 [API Reference](docs/api/README.md)
- 🤝 [Contributing Guidelines](docs/contributing/CONTRIBUTING.md)

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See our [Contributing Guide](docs/contributing/CONTRIBUTING.md) for more details.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💬 Support

Need help? Here's how to get support:

- 📋 [Open an Issue](https://github.com/r-log/github-code-reviewer/issues)
- 💡 [Feature Requests](https://github.com/r-log/github-code-reviewer/issues/new?template=feature_request.md)
- 🐛 [Bug Reports](https://github.com/r-log/github-code-reviewer/issues/new?template=bug_report.md)

## ⭐ Show your support

Give a ⭐️ if this project helped you!

---

<div align="center">
  Made with ❤️ by <a href="https://github.com/r-log">r-log</a>
</div>
