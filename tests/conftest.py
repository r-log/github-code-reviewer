import pytest
from pathlib import Path
from src.reviewer import CodeReviewer
from unittest.mock import patch, MagicMock


@pytest.fixture(autouse=True)
def mock_github_auth():
    """Mock GitHub authentication for all tests."""
    with patch('github.Auth.Token') as mock_auth:
        with patch('github.Github') as mock_gh:
            mock_gh_instance = MagicMock()
            mock_repo = MagicMock()
            mock_pr = MagicMock()

            # Set up chain
            mock_gh.return_value = mock_gh_instance
            mock_gh_instance.get_repo = MagicMock(return_value=mock_repo)
            mock_repo.get_pull = MagicMock(return_value=mock_pr)
            mock_pr.create_review = MagicMock()

            # Store instance for reuse
            mock_gh.mock_instance = mock_gh_instance
            yield mock_gh


@pytest.fixture
def test_config():
    """Basic test configuration."""
    return {
        'rules': {
            'max_line_length': 80,
            'max_file_lines': 300,
            'required_docstrings': True,
            'naming_conventions': {
                'functions': 'snake_case',
                'classes': 'PascalCase',
                'variables': 'snake_case'
            },
            'complexity': {
                'max_cognitive_complexity': 15,
                'max_nested_blocks': 3
            },
            'imports': {
                'groups': ['stdlib', 'third_party', 'local'],
                'require_sorted': True,
                'require_separate_groups': True
            }
        }
    }


@pytest.fixture
def mock_github_token():
    """Mock GitHub token for testing."""
    return "mock_token_123"


@pytest.fixture
def reviewer(test_config):
    """Initialize CodeReviewer instance for testing."""
    with patch('github.Auth.Token') as mock_auth:
        with patch('github.Github') as mock_gh:
            # Create mock objects
            mock_gh_instance = MagicMock()
            mock_repo = MagicMock()
            mock_pr = MagicMock()
            mock_file = MagicMock()

            # Set up chain
            mock_gh.return_value = mock_gh_instance
            mock_gh_instance.get_repo = MagicMock(return_value=mock_repo)
            mock_repo.get_pull = MagicMock(return_value=mock_pr)
            mock_pr.get_files = MagicMock(return_value=[mock_file])
            mock_pr.create_review = MagicMock()

            # Create reviewer with mocked GitHub
            reviewer = CodeReviewer("mock_token_123")
            reviewer.github = mock_gh_instance  # Replace the GitHub instance
            reviewer.rules = test_config['rules']
            return reviewer


@pytest.fixture
def sample_file():
    """Create a mock file object for testing."""
    class MockFile:
        def __init__(self, content: str, filename: str = "test.py"):
            self.filename = filename
            self.patch = content
    return MockFile


@pytest.fixture
def fixtures_path():
    """Path to test fixtures directory."""
    return Path(__file__).parent / 'fixtures'


@pytest.fixture
def import_rules():
    """Override import rules for testing."""
    return {
        'imports': {
            'groups': ['stdlib', 'third_party', 'local'],
            'require_sorted': True,
            'require_separate_groups': True
        }
    }
