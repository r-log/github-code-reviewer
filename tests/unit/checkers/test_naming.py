import pytest
from src.reviewer import CodeReviewer


def test_class_naming(reviewer, sample_file):
    """Test class naming convention checks."""
    # Test bad class name
    bad_code = """
    class badClass:
        pass
    """
    file = sample_file(bad_code)
    comments = reviewer._check_naming_conventions(bad_code.split('\n'), file)
    assert len(comments) == 1
    assert "should be in PascalCase" in comments[0]['body']

    # Test good class name
    good_code = """
    class GoodClassName:
        pass
    """
    file = sample_file(good_code)
    comments = reviewer._check_naming_conventions(good_code.split('\n'), file)
    assert len(comments) == 0


def test_function_naming(reviewer, sample_file):
    """Test function naming convention checks."""
    # Test bad function name
    bad_code = """
    def badFunction():
        pass
    """
    file = sample_file(bad_code)
    comments = reviewer._check_naming_conventions(bad_code.split('\n'), file)
    assert len(comments) == 1
    assert "should be in snake_case" in comments[0]['body']

    # Test good function name
    good_code = """
    def good_function_name():
        pass
    """
    file = sample_file(good_code)
    comments = reviewer._check_naming_conventions(good_code.split('\n'), file)
    assert len(comments) == 0


def test_variable_naming(reviewer, sample_file):
    """Test variable naming convention checks."""
    # Test bad variable name
    bad_code = """
    BadVariableName = 42
    """
    file = sample_file(bad_code)
    comments = reviewer._check_naming_conventions(bad_code.split('\n'), file)
    assert len(comments) == 1
    assert "should be in snake_case" in comments[0]['body']

    # Test good variable name
    good_code = """
    good_variable_name = 42
    """
    file = sample_file(good_code)
    comments = reviewer._check_naming_conventions(good_code.split('\n'), file)
    assert len(comments) == 0
