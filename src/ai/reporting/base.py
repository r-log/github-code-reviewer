from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..models.response import AIResponse, ReviewComment
from ..models.request import ReviewType
from ..storage.base import ReviewRecord


class ReportSection:
    """A section of a review report."""

    def __init__(
        self,
        title: str,
        content: str,
        severity: Optional[str] = None,
        metrics: Optional[Dict[str, Any]] = None
    ):
        self.title = title
        self.content = content
        self.severity = severity
        self.metrics = metrics or {}


class ReviewReport:
    """Container for a complete review report."""

    def __init__(
        self,
        title: str,
        summary: str,
        sections: List[ReportSection],
        timestamp: datetime = datetime.utcnow(),
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.title = title
        self.summary = summary
        self.sections = sections
        self.timestamp = timestamp
        self.metadata = metadata or {}

    @property
    def total_sections(self) -> int:
        return len(self.sections)

    def get_sections_by_severity(self, severity: str) -> List[ReportSection]:
        """Get report sections with specified severity."""
        return [s for s in self.sections if s.severity == severity]


class ReportGenerator(ABC):
    """Base class for report generators."""

    @abstractmethod
    async def generate_file_report(
        self,
        review: AIResponse,
        file_path: str,
        review_type: ReviewType,
        include_code: bool = False
    ) -> ReviewReport:
        """Generate a report for a single file review."""
        pass

    @abstractmethod
    async def generate_multi_file_report(
        self,
        reviews: Dict[str, AIResponse],
        review_type: ReviewType,
        include_code: bool = False
    ) -> ReviewReport:
        """Generate a report for multiple file reviews."""
        pass

    @abstractmethod
    async def generate_historical_report(
        self,
        reviews: List[ReviewRecord],
        file_path: Optional[str] = None,
        review_type: Optional[ReviewType] = None
    ) -> ReviewReport:
        """Generate a report analyzing review history."""
        pass

    @abstractmethod
    async def generate_trend_report(
        self,
        reviews: List[ReviewRecord],
        start_time: datetime,
        end_time: datetime,
        review_type: Optional[ReviewType] = None
    ) -> ReviewReport:
        """Generate a report analyzing review trends over time."""
        pass
