import pytest
from pathlib import Path
from src.reviewer import CodeReviewer
from unittest.mock import patch


def test_reviewer_initialization(mock_github_token, test_config):
    """Test reviewer initialization."""
    reviewer = CodeReviewer(mock_github_token)
    assert reviewer.github is not None
    assert hasattr(reviewer, 'rules')


def test_load_rules(reviewer, fixtures_path):
    """Test loading rules from configuration file."""
    rules = reviewer.rules
    assert isinstance(rules, dict)
    assert 'max_line_length' in rules
    assert 'naming_conventions' in rules
    assert 'complexity' in rules


def test_review_file_with_no_issues(reviewer, sample_file):
    """Test reviewing a file with no issues."""
    with patch.object(reviewer, '_check_dead_code', return_value=[]):
        clean_code = """
        def good_function(x: int, y: int) -> int:
            \"\"\"Add two numbers together.
            
            Args:
                x: First number to add
                y: Second number to add
                
            Returns:
                The sum of x and y
            \"\"\"
            return x + y
        """
        file = sample_file(clean_code)

        # Add debug prints
        print("\n=== Debug test_review_file_with_no_issues ===")
        print(f"Code being checked:\n{clean_code}")

        # Debug each checker
        for checker_name in ['_check_complexity', '_check_docstrings', '_check_imports']:
            checker = getattr(reviewer, checker_name)
            checker_comments = checker(clean_code.split('\n'), file)
            print(f"\n{checker_name} results:")
            for comment in checker_comments:
                print(f"- Line {comment['line']}: {comment['body']}")

        # Check all comments
        comments = reviewer._review_file(file)
        print("\nAll review comments:")
        for comment in comments:
            print(f"- Line {comment['line']}: {comment['body']}")
        print("=====================================\n")

        assert len(comments) == 0


def test_review_file_with_multiple_issues(reviewer, sample_file):
    """Test reviewing a file with multiple issues."""
    bad_code = """
    def badFunction(x,y):
        z=x+y # Bad formatting
        return z
    
    class badClass:
        def __init__(self):
            pass # Missing docstring
    """
    file = sample_file(bad_code)
    comments = reviewer._review_file(file)
    assert len(comments) > 0

    # Check for specific issues
    issues = {comment['body'] for comment in comments}
    assert any('snake_case' in issue for issue in issues)
    assert any('docstring' in issue.lower() for issue in issues)


def test_review_empty_file(reviewer, sample_file):
    """Test reviewing an empty file."""
    file = sample_file("")
    comments = reviewer._review_file(file)
    assert len(comments) == 0


def test_review_non_python_file(reviewer, sample_file):
    """Test reviewing a non-Python file."""
    file = sample_file("console.log('Hello')")
    file.filename = "script.js"
    comments = reviewer._review_file(file)
    assert len(comments) == 0


def test_post_review_formatting(reviewer):
    """Test review comment formatting."""
    comments = [
        {'path': 'test.py', 'line': 1, 'body': 'Issue 1'},
        {'path': 'test.py', 'line': 2, 'body': 'Issue 2'},
    ]

    class MockPR:
        def create_review(self, **kwargs):
            self.review_kwargs = kwargs

    mock_pr = MockPR()
    reviewer._post_review(mock_pr, comments)

    assert 'body' in mock_pr.review_kwargs
    assert 'comments' in mock_pr.review_kwargs
    assert mock_pr.review_kwargs['event'] == 'COMMENT'
    assert all(comment['body'] in mock_pr.review_kwargs['body']
               for comment in comments)
