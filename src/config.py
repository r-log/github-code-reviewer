import yaml
from pathlib import Path
from typing import Dict, Any


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
        """Get rule value from configuration.

        Args:
            rule_path: Dot-separated path to rule (e.g., 'complexity.max_nested_blocks')
            default: Default value if rule not found

        Returns:
            Rule value or default
        """
        current = self.config['rules']
        for part in rule_path.split('.'):
            if not isinstance(current, dict) or part not in current:
                return default
            current = current[part]
        return current
