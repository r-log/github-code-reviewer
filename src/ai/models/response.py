from dataclasses import dataclass
from typing import List, Optional, Dict
from datetime import datetime


@dataclass
class ReviewComment:
    """Represents a single review comment."""
    line_number: Optional[int]
    content: str
    severity: str  # 'error', 'warning', 'suggestion', 'praise'
    category: str  # 'security', 'performance', 'style', etc.
    suggested_fix: Optional[str] = None


@dataclass
class AIResponse:
    """Response model for AI code review."""
    comments: List[ReviewComment]
    summary: str
    score: Optional[float] = None  # Overall code quality score (0-1)
    metadata: Dict[str, any] = None
    timestamp: datetime = datetime.utcnow()

    def get_comments_by_severity(self, severity: str) -> List[ReviewComment]:
        """Filter comments by severity level."""
        return [c for c in self.comments if c.severity == severity]

    def get_comments_by_category(self, category: str) -> List[ReviewComment]:
        """Filter comments by category."""
        return [c for c in self.comments if c.category == category]

    @property
    def has_critical_issues(self) -> bool:
        """Check if there are any error-level comments."""
        return any(c.severity == 'error' for c in self.comments)
