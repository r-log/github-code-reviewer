from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
import os
import yaml

from .validator import ConfigValidator


@dataclass
class AIConfig:
    """AI provider configuration."""
    provider: str = "anthropic"
    model: str = "claude-3-sonnet-20240229"
    temperature: float = 0.7
    max_tokens: Optional[int] = None


@dataclass
class GitHubConfig:
    """GitHub configuration."""
    token: Optional[str] = None
    auto_approve: bool = False
    comment_on_approval: bool = True
    request_changes_on_errors: bool = True
    ignore_files: List[str] = None
    ignore_paths: List[str] = None


@dataclass
class ReviewConfig:
    """Review configuration."""
    type: str = "full"
    max_files: Optional[int] = None
    max_comments: Optional[int] = 50
    min_severity: str = "suggestion"
    focus_areas: Optional[List[str]] = None
    ignore_patterns: Optional[List[str]] = None
    rules: Dict[str, Any] = None


@dataclass
class Config:
    """Main configuration."""
    ai: AIConfig
    github: GitHubConfig
    review: ReviewConfig

    @classmethod
    def from_file(cls, path: str = "config/default_config.yml") -> 'Config':
        """Load configuration from a YAML file."""
        validator = ConfigValidator()

        if not os.path.exists(path):
            # Generate example config if file doesn't exist
            config_data = validator.generate_example_config()
        else:
            with open(path, 'r') as f:
                config_data = yaml.safe_load(f)

        # Validate and apply defaults
        validated_config = validator.validate_with_defaults(config_data)

        return cls(
            ai=AIConfig(**validated_config.get('ai', {})),
            github=GitHubConfig(**validated_config.get('github', {})),
            review=ReviewConfig(**validated_config.get('review', {}))
        )

    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment variables."""
        config = {
            'ai': {
                'provider': os.getenv('AI_PROVIDER', 'anthropic'),
                'model': os.getenv('AI_MODEL', 'claude-3-sonnet-20240229'),
                'temperature': float(os.getenv('AI_TEMPERATURE', '0.7')),
                'max_tokens': int(os.getenv('AI_MAX_TOKENS')) if os.getenv('AI_MAX_TOKENS') else None
            },
            'github': {
                'token': os.getenv('GITHUB_TOKEN'),
                'auto_approve': os.getenv('GITHUB_AUTO_APPROVE', '').lower() == 'true',
                'comment_on_approval': os.getenv('GITHUB_COMMENT_ON_APPROVAL', '').lower() == 'true',
                'request_changes_on_errors': os.getenv('GITHUB_REQUEST_CHANGES_ON_ERRORS', '').lower() == 'true',
                'ignore_files': os.getenv('GITHUB_IGNORE_FILES', '').split(',') if os.getenv('GITHUB_IGNORE_FILES') else None,
                'ignore_paths': os.getenv('GITHUB_IGNORE_PATHS', '').split(',') if os.getenv('GITHUB_IGNORE_PATHS') else None
            },
            'review': {
                'type': os.getenv('REVIEW_TYPE', 'full'),
                'max_files': int(os.getenv('REVIEW_MAX_FILES')) if os.getenv('REVIEW_MAX_FILES') else None,
                'max_comments': int(os.getenv('REVIEW_MAX_COMMENTS', '50')),
                'min_severity': os.getenv('REVIEW_MIN_SEVERITY', 'suggestion'),
                'focus_areas': os.getenv('REVIEW_FOCUS_AREAS', '').split(',') if os.getenv('REVIEW_FOCUS_AREAS') else None,
                'ignore_patterns': os.getenv('REVIEW_IGNORE_PATTERNS', '').split(',') if os.getenv('REVIEW_IGNORE_PATTERNS') else None
            }
        }

        # Validate configuration
        validator = ConfigValidator()
        validated_config = validator.validate_with_defaults(config)

        return cls(
            ai=AIConfig(**validated_config['ai']),
            github=GitHubConfig(**validated_config['github']),
            review=ReviewConfig(**validated_config['review'])
        )

    @classmethod
    def default(cls) -> 'Config':
        """Create default configuration."""
        validator = ConfigValidator()
        config_data = validator.generate_example_config()
        return cls(
            ai=AIConfig(**config_data['ai']),
            github=GitHubConfig(**config_data['github']),
            review=ReviewConfig(**config_data['review'])
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'ai': asdict(self.ai),
            'github': asdict(self.github),
            'review': asdict(self.review)
        }

    def save(self, path: str) -> None:
        """Save configuration to a file."""
        config_data = self.to_dict()

        # Validate before saving
        validator = ConfigValidator()
        validator.validate(config_data)

        with open(path, 'w') as f:
            yaml.safe_dump(config_data, f, default_flow_style=False)
