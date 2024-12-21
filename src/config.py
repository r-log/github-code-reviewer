import yaml
from pathlib import Path
from typing import Dict, Any
import fnmatch


class ConfigManager:
    """Manage configuration for the code reviewer."""

    def __init__(self, custom_config_path: str = None):
        """Initialize configuration manager.

        Args:
            custom_config_path: Path to custom configuration file
        """
        self.config = self._load_default_config()
        if custom_config_path:
            self._merge_custom_config(custom_config_path)

    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration."""
        default_path = Path(__file__).parent.parent / \
            'config' / 'default_config.yml'
        with open(default_path, 'r') as f:
            return yaml.safe_load(f)

    def _merge_custom_config(self, custom_path: str) -> None:
        """Merge custom configuration with defaults."""
        with open(custom_path, 'r') as f:
            custom_config = yaml.safe_load(f)
            self._deep_merge(self.config, custom_config)

    def _deep_merge(self, base: Dict, update: Dict) -> None:
        """Deep merge two dictionaries."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def get_rule(self, rule_path: str, default: Any = None) -> Any:
        """Get rule value from config.

        Handles nested rules using dot notation.
        """
        parts = rule_path.split('.')
        current = self.config['rules']

        for part in parts:
            if not isinstance(current, dict):
                return default
            current = current.get(part, default)

        return current

    def should_ignore_file(self, filename: str) -> bool:
        """Check if file should be ignored based on patterns."""
        patterns = self.get_rule('ignore_patterns', [])
        return any(fnmatch.fnmatch(filename, pattern) for pattern in patterns)

    def is_test_file(self, filename: str) -> bool:
        """Check if file is a test file based on patterns."""
        test_patterns = self.get_rule('test_files.patterns', [])
        return any(fnmatch.fnmatch(filename, pattern) for pattern in test_patterns)

    def should_ignore_rule(self, filename: str, rule: str) -> bool:
        """Check if specific rule should be ignored for file."""
        if self.is_test_file(filename):
            ignored_rules = self.get_rule('test_files.ignore_rules', [])
            return rule in ignored_rules
        return False
