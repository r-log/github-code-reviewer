from typing import Dict, List, Optional
from datetime import datetime

from ..models.request import ReviewType, ReviewSettings, AIRequest, CodeContext
from ..models.response import AIResponse
from ..providers.base import AIProvider
from .github_provider import GitHubAPIProvider


class GitHubReviewer:
    """GitHub-specific reviewer implementation."""

    def __init__(
        self,
        github_provider: GitHubAPIProvider,
        reviewer: AIProvider,
        default_review_type: ReviewType = ReviewType.FULL
    ):
        """Initialize GitHub reviewer."""
        self.github = github_provider
        self.reviewer = reviewer
        self.default_review_type = default_review_type

    async def review_pull_request(
        self,
        repository: str,
        pr_number: int,
        review_type: Optional[ReviewType] = None,
        settings: Optional[ReviewSettings] = None
    ) -> Dict[str, AIResponse]:
        """Review a GitHub pull request."""
        # Get PR changes from GitHub
        changes = self.github.get_pr_changes(repository, pr_number)

        # Review each changed file
        reviews = {}
        for file_path, (content, diff) in changes.items():
            # Create review request
            request = AIRequest(
                code_context=CodeContext(
                    file_path=file_path,
                    content=content,
                    diff=diff
                ),
                review_type=review_type or self.default_review_type,
                settings=settings or ReviewSettings(),
                review_params={
                    "model": "claude-3-sonnet-20240229",
                    "temperature": 0.7,
                    "max_tokens": 4000
                }
            )

            # Generate review
            try:
                review = await self.reviewer.generate_review(request)
                reviews[file_path] = review
            except Exception as e:
                print(f"Failed to review {file_path}: {str(e)}")
                continue

        return reviews

    async def submit_review(
        self,
        repository: str,
        pr_number: int,
        reviews: Dict[str, AIResponse],
        review_type: ReviewType
    ) -> None:
        """Submit review comments to GitHub."""
        # Format review comments
        comments = []
        for file_path, review in reviews.items():
            for comment in review.comments:
                comments.append({
                    'path': file_path,
                    'line': comment.line_start,
                    'body': f"**{comment.severity.upper()}**: {comment.message}\n\nSuggested fix: {comment.suggested_fix}"
                })

        # Submit review to GitHub
        if comments:
            await self.github.submit_review(
                repository,
                pr_number,
                comments,
                "COMMENT"  # or "REQUEST_CHANGES" based on severity
            )
