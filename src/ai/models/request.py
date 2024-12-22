from dataclasses import dataclass
from typing import Dict, List, Optional, Literal
from enum import Enum


class ReviewType(str, Enum):
    """Types of code reviews available."""
    FULL = "full"  # Comprehensive review
    SECURITY = "security"  # Security-focused review
    PERFORMANCE = "performance"  # Performance-focused review
    MAINTAINABILITY = "maintainability"  # Maintainability and code quality
    STYLE = "style"  # Code style and formatting
    DOCUMENTATION = "documentation"  # Documentation quality
    QUICK = "quick"  # Quick overview of critical issues


@dataclass
class CodeContext:
    """Context information about the code being reviewed."""
    file_path: str
    content: str
    diff: Optional[str] = None
    language: Optional[str] = None
    repository: Optional[str] = None
    base_branch: Optional[str] = None  # Base branch for comparison
    commit_hash: Optional[str] = None  # Current commit hash
    author: Optional[str] = None  # Code author
    # List of changed files in PR/commit
    changed_files: Optional[List[str]] = None


@dataclass
class ReviewSettings:
    """Settings for the code review."""
    max_comments: Optional[int] = None  # Maximum number of comments to return
    min_severity: Optional[str] = None  # Minimum severity level to report
    focus_areas: Optional[List[str]] = None  # Specific areas to focus on
    ignore_patterns: Optional[List[str]] = None  # Patterns to ignore
    custom_rules: Optional[Dict[str, any]] = None  # Custom review rules


@dataclass
class AIRequest:
    """Request model for AI code review."""
    code_context: CodeContext
    review_type: ReviewType
    review_params: Dict[str, any]  # Additional parameters for the review
    settings: Optional[ReviewSettings] = None
    max_tokens: Optional[int] = None
    temperature: float = 0.7

    def validate(self) -> bool:
        """Validate the request parameters."""
        if not self.code_context.content:
            return False
        if not self.code_context.file_path:
            return False
        if self.temperature < 0 or self.temperature > 1:
            return False
        if not isinstance(self.review_type, ReviewType):
            return False
        return True

    @property
    def is_security_sensitive(self) -> bool:
        """Check if the review involves security-sensitive code."""
        sensitive_patterns = [
            'password', 'token', 'secret', 'auth', 'crypt',
            'security', 'permission', 'access', 'private'
        ]
        return any(pattern in self.code_context.content.lower()
                   for pattern in sensitive_patterns)

    @property
    def is_performance_critical(self) -> bool:
        """Check if the review involves performance-critical code."""
        critical_patterns = [
            'loop', 'query', 'algorithm', 'cache', 'performance',
            'optimization', 'batch', 'concurrent', 'thread'
        ]
        return any(pattern in self.code_context.content.lower()
                   for pattern in critical_patterns)
