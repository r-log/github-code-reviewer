from typing import List, Dict, Optional, Union
from pathlib import Path
import asyncio
import logging
from datetime import datetime
import os

from .models.request import AIRequest, CodeContext, ReviewSettings, ReviewType
from .models.response import AIResponse, ReviewComment
from .providers.factory import ProviderFactory
from .storage.sqlite import SQLiteStorage
from .storage.base import ReviewRecord
from .exceptions import ReviewError, ConfigurationError, StorageError
from .reporting.base import ReportGenerator, ReviewReport
from .github.github_provider import GitHubAPIProvider
from .github.reviewer import GitHubReviewer

logger = logging.getLogger(__name__)


class ReviewResult:
    """Container for review results of multiple files."""

    def __init__(self):
        self.reviews: Dict[str, AIResponse] = {}
        self.start_time: datetime = datetime.utcnow()
        self.end_time: Optional[datetime] = None
        self.total_files: int = 0
        self.successful_reviews: int = 0
        self.failed_reviews: int = 0
        self.errors: Dict[str, str] = {}
        self.review_ids: Dict[str, str] = {}  # Map of file_path to review_id

    @property
    def duration(self) -> float:
        """Get review duration in seconds."""
        if not self.end_time:
            return 0
        return (self.end_time - self.start_time).total_seconds()

    def add_review(self, file_path: str, review: AIResponse, review_id: Optional[str] = None):
        """Add a successful review result."""
        self.reviews[file_path] = review
        self.successful_reviews += 1
        if review_id:
            self.review_ids[file_path] = review_id

    def add_error(self, file_path: str, error: str):
        """Add a failed review error."""
        self.errors[file_path] = error
        self.failed_reviews += 1

    def get_critical_issues(self) -> List[tuple[str, ReviewComment]]:
        """Get all error-level comments across all reviews."""
        critical_issues = []
        for file_path, review in self.reviews.items():
            for comment in review.get_comments_by_severity("error"):
                critical_issues.append((file_path, comment))
        return critical_issues


class Reviewer:
    """Main class for coordinating code reviews."""

    def __init__(
        self,
        provider_name: str = "anthropic",
        api_key: Optional[str] = None,
        **provider_kwargs
    ):
        """Initialize the reviewer with a specific provider."""
        if not api_key:
            raise ValueError("API key is required")

        self.provider = ProviderFactory.create(
            provider_name=provider_name,
            api_key=api_key,
            **provider_kwargs
        )

    async def review_file(
        self,
        file_path: Union[str, Path],
        content: str,
        review_type: Optional[ReviewType] = None,
        settings: Optional[ReviewSettings] = None,
        store_review: bool = True,
        **context_kwargs
    ) -> tuple[AIResponse, Optional[str]]:
        """Review a single file and optionally store the review."""
        try:
            # Create review request
            request = AIRequest(
                code_context=CodeContext(
                    file_path=str(file_path),
                    content=content,
                    **context_kwargs
                ),
                review_type=review_type or self.default_review_type,
                review_params={},
                settings=settings or self.default_settings
            )

            # Validate request
            if not request.validate():
                raise ReviewError(
                    f"Invalid review request for file: {file_path}")

            # Generate review
            review = await self.provider.generate_review(request)
            review_id = None

            # Store review if storage is available and requested
            if store_review and self.storage:
                try:
                    review_id = await self.storage.save_review(
                        str(file_path),
                        request.review_type,
                        review,
                        context_kwargs
                    )
                except StorageError as e:
                    logger.warning(f"Failed to store review: {str(e)}")

            return review, review_id

        except Exception as e:
            logger.error(f"Failed to review file {file_path}: {str(e)}")
            raise ReviewError(f"Review failed for {file_path}: {str(e)}")

    async def review_files(
        self,
        files: Dict[str, str],
        review_type: Optional[ReviewType] = None,
        settings: Optional[ReviewSettings] = None,
        max_concurrent: int = 3,
        store_reviews: bool = True,
        **context_kwargs
    ) -> ReviewResult:
        """Review multiple files concurrently."""
        result = ReviewResult()
        result.total_files = len(files)

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(max_concurrent)

        async def review_with_semaphore(file_path: str, content: str):
            async with semaphore:
                try:
                    review, review_id = await self.review_file(
                        file_path,
                        content,
                        review_type,
                        settings,
                        store_reviews,
                        **context_kwargs
                    )
                    result.add_review(file_path, review, review_id)
                except Exception as e:
                    result.add_error(file_path, str(e))

        # Create tasks for all files
        tasks = [
            review_with_semaphore(file_path, content)
            for file_path, content in files.items()
        ]

        # Wait for all reviews to complete
        await asyncio.gather(*tasks)
        result.end_time = datetime.utcnow()

        return result

    async def review_changes(
        self,
        files: Dict[str, tuple[str, Optional[str]]],  # (content, diff)
        base_branch: str = "main",
        review_type: Optional[ReviewType] = None,
        settings: Optional[ReviewSettings] = None,
        store_reviews: bool = True,
        **context_kwargs
    ) -> ReviewResult:
        """Review changed files with their diffs."""
        files_with_context = {
            file_path: content for file_path, (content, _) in files.items()
        }

        # Add diff information to context_kwargs
        context_kwargs["base_branch"] = base_branch
        context_kwargs.update({
            "diff": {
                file_path: diff for file_path, (_, diff) in files.items()
                if diff is not None
            }
        })

        return await self.review_files(
            files_with_context,
            review_type,
            settings,
            store_reviews=store_reviews,
            **context_kwargs
        )

    def set_default_settings(self, settings: ReviewSettings):
        """Update default review settings."""
        self.default_settings = settings

    def set_default_review_type(self, review_type: ReviewType):
        """Update default review type."""
        self.default_review_type = review_type

    async def get_file_history(
        self,
        file_path: str,
        limit: Optional[int] = None,
        review_type: Optional[ReviewType] = None
    ) -> List[ReviewRecord]:
        """Get review history for a file."""
        if not self.storage:
            raise StorageError("Storage is not configured")
        return await self.storage.get_file_reviews(file_path, limit, review_type)

    async def get_reviews_in_timeframe(
        self,
        start_time: datetime,
        end_time: datetime,
        review_type: Optional[ReviewType] = None
    ) -> List[ReviewRecord]:
        """Get reviews within a timeframe."""
        if not self.storage:
            raise StorageError("Storage is not configured")
        return await self.storage.get_reviews_in_timeframe(
            start_time, end_time, review_type
        )

    async def cleanup_old_reviews(self, older_than: datetime) -> int:
        """Delete reviews older than specified datetime."""
        if not self.storage:
            raise StorageError("Storage is not configured")
        return await self.storage.cleanup_old_reviews(older_than)

    async def generate_report(
        self,
        result: ReviewResult,
        review_type: ReviewType,
        include_code: bool = False
    ) -> ReviewReport:
        """Generate a report from review results."""
        return await self.report_generator.generate_multi_file_report(
            result.reviews,
            review_type,
            include_code
        )

    async def generate_file_report(
        self,
        file_path: str,
        review: AIResponse,
        review_type: ReviewType,
        include_code: bool = False
    ) -> ReviewReport:
        """Generate a report for a single file review."""
        return await self.report_generator.generate_file_report(
            review,
            file_path,
            review_type,
            include_code
        )

    async def generate_historical_report(
        self,
        file_path: Optional[str] = None,
        review_type: Optional[ReviewType] = None,
        limit: Optional[int] = None
    ) -> ReviewReport:
        """Generate a historical analysis report."""
        if not self.storage:
            raise StorageError("Storage is not configured")

        reviews = await self.storage.get_file_reviews(
            file_path, limit, review_type
        ) if file_path else []

        return await self.report_generator.generate_historical_report(
            reviews,
            file_path,
            review_type
        )

    async def generate_trend_report(
        self,
        start_time: datetime,
        end_time: datetime,
        review_type: Optional[ReviewType] = None
    ) -> ReviewReport:
        """Generate a trend analysis report."""
        if not self.storage:
            raise StorageError("Storage is not configured")

        reviews = await self.storage.get_reviews_in_timeframe(
            start_time,
            end_time,
            review_type
        )

        return await self.report_generator.generate_trend_report(
            reviews,
            start_time,
            end_time,
            review_type
        )

    async def review_pr(self, repository: str, pr_number: int) -> None:
        """Review a pull request."""
        # Import here to avoid circular imports
        from .github.github_provider import GitHubAPIProvider
        from .github.reviewer import GitHubReviewer

        # Get GitHub token
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            raise ValueError("GITHUB_TOKEN environment variable not set")

        # Initialize GitHub components
        github = GitHubAPIProvider(github_token)
        gh_reviewer = GitHubReviewer(
            github_provider=github,
            reviewer=self.provider,
            default_review_type=ReviewType.FULL
        )

        # Set review settings
        settings = ReviewSettings(
            max_comments=50,
            min_severity="suggestion",
            focus_areas=None,
            ignore_patterns=None
        )

        # Review the pull request
        print(f"🔍 Reviewing PR #{pr_number} in {repository}...")
        reviews = await gh_reviewer.review_pull_request(
            repository,
            pr_number,
            review_type=ReviewType.FULL,
            settings=settings
        )

        # Submit the review
        print("📝 Submitting review comments...")
        await gh_reviewer.submit_review(
            repository,
            pr_number,
            reviews,
            ReviewType.FULL
        )

        print("✅ Review completed successfully!")
