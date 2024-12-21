import pytest
from src.reviewer import CodeReviewer


def test_cognitive_complexity(reviewer, sample_file):
    """Test cognitive complexity checks."""
    complex_code = """
    def complex_function():
        for i in range(10):          # +1 complexity
            if i > 5:                # +2 complexity (nested)
                for j in range(i):   # +3 complexity (nested)
                    if j > 2:        # +4 complexity (nested)
                        if i + j > 10:  # +5 complexity (nested)
                            return True
        return False
    """
    file = sample_file(complex_code)

    # Add debug prints
    print("\n=== Debug test_cognitive_complexity ===")
    print(f"Code being checked:\n{complex_code}")

    comments = reviewer._check_complexity(complex_code.split('\n'), file)
    print("\nComplexity check results:")
    for comment in comments:
        print(f"- Line {comment['line']}: {comment['body']}")
    print("=====================================\n")

    assert len(comments) > 0
    assert any(
        'cognitive complexity' in comment['body'].lower()
        for comment in comments
    )


def test_nested_blocks(reviewer, sample_file):
    """Test nested blocks depth checking."""
    nested_code = """
    def nested_function():
        with open('file') as f:            # depth 1
            for line in f:                 # depth 2
                with open(line) as f2:     # depth 3
                    for item in f2:        # depth 4
                        if item:           # depth 5
                            return item
    """
    file = sample_file(nested_code)
    comments = reviewer._check_complexity(nested_code.split('\n'), file)
    assert len(comments) > 0
    assert any('nesting' in comment['body'].lower() for comment in comments)


def test_simple_function(reviewer, sample_file):
    """Test that simple functions pass complexity checks."""
    simple_code = """
    def simple_function(x, y):
        if x > y:
            return x
        return y
    """
    file = sample_file(simple_code)
    comments = reviewer._check_complexity(simple_code.split('\n'), file)
    assert len(comments) == 0
