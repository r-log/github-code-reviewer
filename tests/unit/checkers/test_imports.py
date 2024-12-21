import pytest
from src.reviewer import CodeReviewer


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


@pytest.fixture
def reviewer_with_import_rules(mock_github_token, import_rules):
    """Create reviewer with specific import rules."""
    reviewer = CodeReviewer(mock_github_token)
    reviewer.rules.update(import_rules)
    return reviewer


def test_import_order(reviewer_with_import_rules, sample_file):
    """Test import order checking."""
    bad_imports = """
    import json
    from typing import List
    import os  # Out of order
    import sys
    from datetime import datetime
    """
    file = sample_file(bad_imports)
    comments = reviewer_with_import_rules._check_imports(
        bad_imports.split('\n'), file)
    assert len(comments) > 0
    assert any('not properly sorted' in comment['body'].lower()
               for comment in comments)


def test_import_grouping(reviewer_with_import_rules, sample_file):
    """Test import grouping checks."""
    mixed_imports = """
    import os
    import requests  # Third-party mixed with stdlib
    import sys
    from pathlib import Path
    """
    file = sample_file(mixed_imports)

    # Add debug prints
    print("\n=== Debug test_import_grouping ===")
    print(f"Code being checked:\n{mixed_imports}")
    print(f"\nImport rules: {reviewer_with_import_rules.rules.get('imports')}")

    comments = reviewer_with_import_rules._check_imports(
        mixed_imports.split('\n'), file)

    print("\nImport check results:")
    for comment in comments:
        print(f"- Line {comment['line']}: {comment['body']}")
    print("=====================================\n")

    assert len(comments) > 0
    assert any('group' in comment['body'].lower()
               for comment in comments)


def test_clean_imports(reviewer_with_import_rules, sample_file):
    """Test properly organized imports."""
    good_imports = """
    # Standard library imports
    import os
    import sys
    from pathlib import Path

    # Third-party imports
    import pytest
    import requests

    # Local imports
    from myapp.utils import helper
    """
    file = sample_file(good_imports)

    # Add debug prints
    print("\n=== Debug test_clean_imports ===")
    print(f"Input imports:\n{good_imports}")

    comments = reviewer_with_import_rules._check_imports(
        good_imports.split('\n'), file)

    print("\nImport check results:")
    for comment in comments:
        print(f"- Line {comment['line']}: {comment['body']}")
    print("=====================================\n")

    assert len(comments) == 0


def test_complex_imports(reviewer_with_import_rules, sample_file):
    """Test handling of complex import scenarios."""
    complex_imports = """
    from typing import List, Optional
    import sys
    import os
    
    import pytest
    from pytest import fixture
    
    from . import local_module
    from .utils import helper
    """
    file = sample_file(complex_imports)
    comments = reviewer_with_import_rules._check_imports(
        complex_imports.split('\n'), file)
    assert len(comments) > 0
    assert any('sorted' in comment['body'].lower()
               for comment in comments)


def test_relative_imports(reviewer_with_import_rules, sample_file):
    """Test handling of relative imports."""
    relative_imports = """
    from ..base import BaseClass
    from . import local
    from ...utils import helper
    """
    file = sample_file(relative_imports)
    comments = reviewer_with_import_rules._check_imports(
        relative_imports.split('\n'), file)
    # Should warn about relative imports if configured to do so
    if reviewer_with_import_rules.rules.get('imports', {}).get('warn_on_relative_imports'):
        assert len(comments) > 0
        assert any('relative import' in comment['body'].lower()
                   for comment in comments)
