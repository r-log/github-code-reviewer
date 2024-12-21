import pytest
from unittest.mock import Mock, patch, MagicMock
from src.reviewer import CodeReviewer


@pytest.fixture(autouse=True)
def mock_github_auth():
    """Mock GitHub authentication for all tests."""
    with patch('github.Auth.Token') as mock_auth:
        with patch('github.Github') as mock_gh:
            mock_gh_instance = MagicMock()
            mock_repo = MagicMock()
            mock_pr = MagicMock()

            # Set up the chain
            mock_gh.return_value = mock_gh_instance
            mock_gh_instance.get_repo = MagicMock(return_value=mock_repo)
            mock_repo.get_pull = MagicMock(return_value=mock_pr)
            mock_pr.create_review = MagicMock()

            yield mock_gh


@pytest.fixture
def mock_github():
    """Mock GitHub API interactions."""
    with patch('github.Auth.Token') as mock_auth:
        with patch('github.Github') as mock_gh:
            # Create mock objects
            mock_gh_instance = MagicMock()
            mock_repo = MagicMock()
            mock_pr = MagicMock()
            mock_file = MagicMock()

            # Set up the chain BEFORE any other configuration
            mock_gh.return_value = mock_gh_instance
            mock_gh_instance.get_repo = MagicMock(return_value=mock_repo)
            mock_repo.get_pull = MagicMock(return_value=mock_pr)
            mock_pr.get_files = MagicMock(return_value=[mock_file])
            mock_pr.create_review = MagicMock()

            # Configure mock file after chain setup
            mock_file.filename = "test.py"
            mock_file.patch = """
            def bad_function():
                # Missing docstring
                pass
            """

            yield mock_gh


def test_review_pull_request(mock_github, reviewer):
    """Test the complete pull request review process."""
    with patch('github.Github') as mock_gh_class:
        # Add debug prints
        print("\n=== Debug test_review_pull_request ===")
        print(f"Mock GitHub instance: {mock_github}")
        print(f"Reviewer GitHub instance: {reviewer.github}")

        # Use the same mock instance
        reviewer.github = mock_github.return_value
        print(
            f"Are instances same after update? {mock_github.return_value == reviewer.github}")

        mock_gh_class.return_value = mock_github.return_value
        reviewer.review_pull_request("test/repo", 1)

        # Add more debug prints
        print(
            f"Get repo call count: {mock_github.return_value.get_repo.call_count}")
        print(
            f"Get repo calls: {mock_github.return_value.get_repo.call_args_list}")
        print("=====================================\n")

        # Verify the chain of calls
        mock_github.return_value.get_repo.assert_called_once_with("test/repo")
        mock_github.return_value.get_repo.return_value.get_pull.assert_called_once_with(
            1)

        # Verify review was created with comments
        mock_pr = mock_github.return_value.get_repo.return_value.get_pull.return_value
        assert mock_pr.create_review.called

        # Verify review content
        call_kwargs = mock_pr.create_review.call_args[1]
        assert 'body' in call_kwargs
        assert 'comments' in call_kwargs
        assert call_kwargs['event'] == 'COMMENT'


def test_review_with_no_issues(mock_github, reviewer):
    """Test review of clean code."""
    # Override mock file with clean code
    mock_file = MagicMock()
    mock_file.filename = "test.py"
    mock_file.patch = """
    def good_function():
        \"\"\"A well-documented function.
        
        This function demonstrates good coding practices.
        \"\"\"
        pass
    """

    mock_pr = mock_github.return_value.get_repo.return_value.get_pull.return_value
    mock_pr.get_files.return_value = [mock_file]

    # Mock the GitHub instance creation
    with patch('github.Github') as mock_gh_class:
        mock_gh_class.return_value = mock_github.return_value

        # Run the review
        reviewer.review_pull_request("test/repo", 1)

        # Verify no review was created for clean code
        assert not mock_pr.create_review.called


def test_review_with_multiple_files(mock_github, reviewer):
    """Test reviewing multiple files in a PR."""
    # Create multiple mock files
    mock_files = [
        MagicMock(filename="good.py", patch="""
        def good_function() -> None:
            \"\"\"This function demonstrates proper documentation standards.
            
            The function serves as an example of well-documented code that 
            follows best practices including type hints and docstrings.
            It uses full sentences and proper punctuation throughout.
            
            Returns:
                None: This function does not return any value.
            \"\"\"
            print("This is a good function")

        # Use the function to avoid unused warning
        good_function()
        """),
        MagicMock(filename="bad.py", patch="""
        def bad_function():
            pass  # No docstring
        """)
    ]

    mock_pr = mock_github.return_value.get_repo.return_value.get_pull.return_value
    mock_pr.get_files.return_value = mock_files

    # Mock the GitHub instance creation
    with patch('github.Github') as mock_gh_class:
        mock_gh_class.return_value = mock_github.return_value
        reviewer.github = mock_github.return_value

        # Run the review
        reviewer.review_pull_request("test/repo", 1)

        # Verify review was created with appropriate comments
        assert mock_pr.create_review.called
        call_kwargs = mock_pr.create_review.call_args[1]
        assert 'bad.py' in call_kwargs['body']
        assert 'good.py' not in call_kwargs['body']
