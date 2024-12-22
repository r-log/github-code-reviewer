from typing import Optional, Dict, List
from datetime import datetime

from ..reviewer import Reviewer
from ..models.request import ReviewType, CodeContext, ReviewSettings
from ..models.response import AIResponse, ReviewComment as AIReviewComment
from .base import GitHubProvider, ReviewComment
from ..exceptions import ReviewError


class GitHubReviewer:
    """GitHub-specific code reviewer."""

    def __init__(
        self,
        github_provider: GitHubProvider,
        reviewer: Reviewer,
        default_review_type: ReviewType = ReviewType.FULL
    ):
        self.github = github_provider
        self.reviewer = reviewer
        self.default_review_type = default_review_type

    async def review_pull_request(
        self,
        repo_name: str,
        pr_number: int,
        review_type: Optional[ReviewType] = None,
        settings: Optional[ReviewSettings] = None,
        store_review: bool = True
    ) -> Dict[str, AIResponse]:
        """Review a GitHub pull request."""
        # Get repository and PR info
        repo = await self.github.get_repository(repo_name)
        pr_info = await self.github.get_pull_request(repo, pr_number)

        # Get file contents and create reviews
        reviews = {}
        for file_path in pr_info.files_changed:
            try:
                # Get file content
                content = await self.github.get_file_content(repo, file_path, pr_info.head_branch)

                # Create review request
                context = CodeContext(
                    file_path=file_path,
                    content=content,
                    diff=pr_info.diff,
                    repository=repo_name,
                    base_branch=pr_info.base_branch,
                    commit_hash=None,  # We'll add this when needed
                    author=pr_info.author,
                    changed_files=pr_info.files_changed
                )

                # Generate review
                review, _ = await self.reviewer.review_file(
                    file_path,
                    content,
                    review_type or self.default_review_type,
                    settings,
                    store_review,
                    **context.__dict__
                )

                reviews[file_path] = review

            except Exception as e:
                raise ReviewError(f"Failed to review {file_path}: {str(e)}")

        return reviews

    async def submit_review(
        self,
        repo_name: str,
        pr_number: int,
        reviews: Dict[str, AIResponse],
        review_type: ReviewType
    ) -> None:
        """Submit reviews as GitHub comments."""
        repo = await self.github.get_repository(repo_name)

        # Convert AI review comments to GitHub review comments
        github_comments = []
        for file_path, review in reviews.items():
            for comment in review.comments:
                github_comments.append(
                    ReviewComment(
                        body=self._format_comment(comment),
                        path=file_path,
                        line=comment.line_number,
                        position=None  # We'll need to calculate this from the diff
                    )
                )

        # Create summary body
        summary = self._create_summary(reviews, review_type)

        # Determine review event based on critical issues
        event = self._determine_review_event(reviews)

        # Submit the review
        await self.github.create_review(
            repo,
            pr_number,
            github_comments,
            summary,
            event
        )

    def _format_comment(self, comment: AIReviewComment) -> str:
        """Format an AI review comment for GitHub."""
        severity_icons = {
            "error": "🔴",
            "warning": "⚠️",
            "suggestion": "💡",
            "praise": "✨"
        }

        formatted = f"{severity_icons.get(comment.severity, '•')} **{comment.category.title()}**\n\n"
        formatted += comment.content

        if comment.suggested_fix:
            formatted += f"\n\n**Suggested Fix:**\n```\n{comment.suggested_fix}\n```"

        return formatted

    def _create_summary(self, reviews: Dict[str, AIResponse], review_type: ReviewType) -> str:
        """Create a summary of all reviews."""
        total_files = len(reviews)
        total_comments = sum(len(review.comments)
                             for review in reviews.values())
        errors = sum(
            len(review.get_comments_by_severity("error"))
            for review in reviews.values()
        )
        warnings = sum(
            len(review.get_comments_by_severity("warning"))
            for review in reviews.values()
        )

        summary = f"# AI Code Review ({review_type.value})\n\n"
        summary += f"Reviewed {total_files} files and found:\n"
        summary += f"- 🔴 {errors} critical issues\n"
        summary += f"- ⚠️ {warnings} warnings\n"
        summary += f"- 💭 {total_comments - errors - warnings} suggestions\n\n"

        # Add individual file summaries
        for file_path, review in reviews.items():
            summary += f"\n## {file_path}\n{review.summary}\n"

        return summary

    def _determine_review_event(self, reviews: Dict[str, AIResponse]) -> str:
        """Determine the review event based on the findings."""
        total_errors = sum(
            len(review.get_comments_by_severity("error"))
            for review in reviews.values()
        )

        if total_errors > 0:
            return "REQUEST_CHANGES"

        total_warnings = sum(
            len(review.get_comments_by_severity("warning"))
            for review in reviews.values()
        )

        if total_warnings > 0:
            return "COMMENT"

        return "APPROVE"
