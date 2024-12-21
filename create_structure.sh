mkdir -p github-code-reviewer/{src,tests,config,.github/workflows}
cd github-code-reviewer

# Create test directory structure
mkdir -p tests/{unit,integration,fixtures}
mkdir -p tests/unit/checkers
mkdir -p tests/fixtures/sample_files
mkdir -p tests/fixtures/configs

# Create necessary __init__.py files
touch src/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/unit/checkers/__init__.py
touch tests/integration/__init__.py
touch tests/fixtures/__init__.py

# Create test files
touch tests/unit/test_reviewer.py
touch tests/unit/checkers/test_naming.py
touch tests/unit/checkers/test_complexity.py
touch tests/unit/checkers/test_imports.py
touch tests/unit/checkers/test_docstrings.py
touch tests/integration/test_github_integration.py
touch tests/conftest.py

# Create fixture files
touch tests/fixtures/sample_files/good_code.py
touch tests/fixtures/sample_files/bad_code.py
touch tests/fixtures/configs/test_config.yml

# Create main source files
touch src/reviewer.py

# Create setup and configuration files
touch setup.py
touch requirements.txt
touch requirements-dev.txt
touch .gitignore