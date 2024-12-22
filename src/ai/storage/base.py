from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from datetime import datetime

from ..models.response import AIResponse
from ..models.request import ReviewType


class ReviewRecord:
    """Record of a code review."""

    def __init__(
        self,
        id: str,
        file_path: str,
        review_type: ReviewType,
        review_response: AIResponse,
        timestamp: datetime,
        metadata: Optional[Dict] = None
    ):
        self.id = id
        self.file_path = file_path
        self.review_type = review_type
        self.review_response = review_response
        self.timestamp = timestamp
        self.metadata = metadata or {}


class StorageProvider(ABC):
    """Base class for review history storage providers."""

    @abstractmethod
    async def save_review(
        self,
        file_path: str,
        review_type: ReviewType,
        review: AIResponse,
        metadata: Optional[Dict] = None
    ) -> str:
        """Save a review and return its ID."""
        pass

    @abstractmethod
    async def get_review(self, review_id: str) -> Optional[ReviewRecord]:
        """Get a review by its ID."""
        pass

    @abstractmethod
    async def get_file_reviews(
        self,
        file_path: str,
        limit: Optional[int] = None,
        review_type: Optional[ReviewType] = None
    ) -> List[ReviewRecord]:
        """Get review history for a file."""
        pass

    @abstractmethod
    async def get_reviews_in_timeframe(
        self,
        start_time: datetime,
        end_time: datetime,
        review_type: Optional[ReviewType] = None
    ) -> List[ReviewRecord]:
        """Get reviews within a timeframe."""
        pass

    @abstractmethod
    async def delete_review(self, review_id: str) -> bool:
        """Delete a review by its ID."""
        pass

    @abstractmethod
    async def cleanup_old_reviews(self, older_than: datetime) -> int:
        """Delete reviews older than specified datetime."""
        pass
