import pytest
from src.config import ConfigManager
from pathlib import Path


@pytest.fixture
def test_config_file(tmp_path):
    """Create a test configuration file."""
    config_content = """
    rules:
      max_line_length: 120
      complexity:
        max_nested_blocks: 4
    """
    config_file = tmp_path / "test_config.yml"
    config_file.write_text(config_content)
    return str(config_file)


def test_default_config():
    """Test loading default configuration."""
    config = ConfigManager()
    assert config.get_rule('max_line_length') == 100
    assert config.get_rule('complexity.max_nested_blocks') == 3


def test_custom_config(test_config_file):
    """Test merging custom configuration."""
    config = ConfigManager(test_config_file)
    assert config.get_rule('max_line_length') == 120
    assert config.get_rule('complexity.max_nested_blocks') == 4
    # Default values should still be present
    assert config.get_rule('required_docstrings') is True
