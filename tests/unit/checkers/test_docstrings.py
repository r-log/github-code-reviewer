import pytest
from src.reviewer import CodeReviewer


def test_missing_docstring(reviewer, sample_file):
    """Test detection of missing docstrings."""
    code_without_docstring = """
    def function_without_docstring(x, y):
        return x + y
    
    class ClassWithoutDocstring:
        def method_without_docstring(self):
            pass
    """
    file = sample_file(code_without_docstring)
    comments = reviewer._check_docstrings(
        code_without_docstring.split('\n'), file)

    # Verify all missing docstrings are detected
    assert len(comments) == 3
    assert all('Missing docstring' in comment['body'] for comment in comments)

    # Verify specific locations
    lines = [comment['line'] for comment in comments]
    assert 2 in lines  # function
    assert 5 in lines  # class
    assert 6 in lines  # method


def test_proper_docstrings(reviewer, sample_file):
    """Test that proper docstrings pass checks."""
    code_with_docstrings = '''
    def function_with_docstring(x, y):
        """Add two numbers together.
        
        This function takes two numbers and returns their sum.
        
        Args:
            x: First number to add
            y: Second number to add
            
        Returns:
            The sum of x and y
        """
        return x + y
    
    class ClassWithDocstring:
        """A class with proper documentation.
        
        This class demonstrates good docstring practices.
        """
        
        def method_with_docstring(self):
            """A properly documented method.
            
            This method shows how to document class methods.
            """
            pass
    '''
    file = sample_file(code_with_docstrings)
    comments = reviewer._check_docstrings(
        code_with_docstrings.split('\n'), file)
    assert len(comments) == 0


def test_incomplete_docstring(reviewer, sample_file):
    """Test detection of incomplete docstrings."""
    code_with_incomplete_docstring = '''
    def function_with_incomplete_docstring(x, y):
        """Add numbers."""
        return x + y
    '''
    file = sample_file(code_with_incomplete_docstring)
    comments = reviewer._check_docstrings(
        code_with_incomplete_docstring.split('\n'), file)
    assert len(comments) > 0
    assert 'too brief' in comments[0]['body'].lower()


def test_multiline_docstring(reviewer, sample_file):
    """Test handling of multi-line docstrings."""
    code_with_multiline_docstring = '''
    def function_with_multiline_docstring():
        """
        This is a multi-line docstring.
        It spans multiple lines but is still too brief.
        """
        pass
    '''
    file = sample_file(code_with_multiline_docstring)
    comments = reviewer._check_docstrings(
        code_with_multiline_docstring.split('\n'), file)
    assert len(comments) == 0  # Should pass as it has enough content
