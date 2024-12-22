from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import os
import yaml


@dataclass
class RuleConfig:
    """Code review rules configuration."""
    max_line_length: int = 100
    max_file_lines: int = 300
    require_type_hints: bool = True
    ignore_patterns: List[str] = None
    required_docstrings: bool = True
    min_docstring_words: int = 5
    complexity: Dict[str, Any] = None
    functions: Dict[str, Any] = None
    magic_numbers: Dict[str, Any] = None
    imports: Dict[str, Any] = None
    naming_conventions: Dict[str, Any] = None
    testing: Dict[str, Any] = None
    duplication: Dict[str, Any] = None
    test_files: Dict[str, Any] = None
    performance: Dict[str, Any] = None
    security: Dict[str, Any] = None
    documentation: Dict[str, Any] = None


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
    rules: RuleConfig = None

    def __post_init__(self):
        if self.rules is None:
            self.rules = RuleConfig()


@dataclass
class Config:
    """Main configuration."""
    ai: AIConfig
    github: GitHubConfig
    review: ReviewConfig

    @classmethod
    def from_file(cls, path: str = "config/default_config.yml") -> 'Config':
        """Load configuration from a YAML file."""
        if not os.path.exists(path):
            return cls.default()

        with open(path, 'r') as f:
            data = yaml.safe_load(f)

        # Convert the existing rules format to our config structure
        rules_data = data.get('rules', {})
        review_data = {
            'type': 'full',
            'max_comments': 50,
            'min_severity': 'suggestion',
            'rules': rules_data
        }

        return cls(
            ai=AIConfig(),  # Default AI config
            github=GitHubConfig(),  # Default GitHub config
            review=ReviewConfig(**review_data)
        )

    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment variables."""
        return cls(
            ai=AIConfig(
                provider=os.getenv('AI_PROVIDER', 'anthropic'),
                model=os.getenv('AI_MODEL', 'claude-3-sonnet-20240229'),
                temperature=float(os.getenv('AI_TEMPERATURE', '0.7')),
                max_tokens=int(os.getenv('AI_MAX_TOKENS')) if os.getenv(
                    'AI_MAX_TOKENS') else None
            ),
            github=GitHubConfig(
                token=os.getenv('GITHUB_TOKEN'),
                auto_approve=os.getenv(
                    'GITHUB_AUTO_APPROVE', '').lower() == 'true',
                comment_on_approval=os.getenv(
                    'GITHUB_COMMENT_ON_APPROVAL', '').lower() == 'true',
                request_changes_on_errors=os.getenv(
                    'GITHUB_REQUEST_CHANGES_ON_ERRORS', '').lower() == 'true',
                ignore_files=os.getenv('GITHUB_IGNORE_FILES', '').split(
                    ',') if os.getenv('GITHUB_IGNORE_FILES') else None,
                ignore_paths=os.getenv('GITHUB_IGNORE_PATHS', '').split(
                    ',') if os.getenv('GITHUB_IGNORE_PATHS') else None
            ),
            review=ReviewConfig(
                type=os.getenv('REVIEW_TYPE', 'full'),
                max_files=int(os.getenv('REVIEW_MAX_FILES')) if os.getenv(
                    'REVIEW_MAX_FILES') else None,
                max_comments=int(os.getenv('REVIEW_MAX_COMMENTS', '50')),
                min_severity=os.getenv('REVIEW_MIN_SEVERITY', 'suggestion'),
                focus_areas=os.getenv('REVIEW_FOCUS_AREAS', '').split(
                    ',') if os.getenv('REVIEW_FOCUS_AREAS') else None,
                ignore_patterns=os.getenv('REVIEW_IGNORE_PATTERNS', '').split(
                    ',') if os.getenv('REVIEW_IGNORE_PATTERNS') else None
            )
        )

    @classmethod
    def default(cls) -> 'Config':
        """Create default configuration."""
        return cls(
            ai=AIConfig(),
            github=GitHubConfig(),
            review=ReviewConfig()
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'ai': {
                'provider': self.ai.provider,
                'model': self.ai.model,
                'temperature': self.ai.temperature,
                'max_tokens': self.ai.max_tokens
            },
            'github': {
                'auto_approve': self.github.auto_approve,
                'comment_on_approval': self.github.comment_on_approval,
                'request_changes_on_errors': self.github.request_changes_on_errors,
                'ignore_files': self.github.ignore_files,
                'ignore_paths': self.github.ignore_paths
            },
            'review': {
                'type': self.review.type,
                'max_files': self.review.max_files,
                'max_comments': self.review.max_comments,
                'min_severity': self.review.min_severity,
                'focus_areas': self.review.focus_areas,
                'ignore_patterns': self.review.ignore_patterns,
                'rules': self.review.rules.__dict__ if self.review.rules else None
            }
        }
