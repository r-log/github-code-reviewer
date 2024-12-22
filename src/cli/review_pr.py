import asyncio
import argparse
import os
from typing import Optional

from ..ai.reviewer import Reviewer
from ..ai.models.request import ReviewType, ReviewSettings
from ..ai.providers.factory import ProviderFactory
from ..ai.github.github_provider import GitHubAPIProvider
from ..ai.github.reviewer import GitHubReviewer


async def review_pull_request(
    repo: str,
    pr_number: int,
    github_token: str,
    ai_provider: str = "anthropic",
    ai_token: Optional[str] = None,
    review_type: str = "full",
    max_files: Optional[int] = None
) -> None:
    """Review a GitHub pull request."""
    # Initialize AI reviewer
    ai_token = ai_token or os.getenv("AI_TOKEN")
    if not ai_token:
        raise ValueError(
            "AI token not provided and AI_TOKEN environment variable not set")

    reviewer = Reviewer(
        provider_name=ai_provider,
        api_key=ai_token
    )

    # Initialize GitHub provider
    github_token = github_token or os.getenv("GITHUB_TOKEN")
    if not github_token:
        raise ValueError(
            "GitHub token not provided and GITHUB_TOKEN environment variable not set")

    github = GitHubAPIProvider(github_token)

    # Create GitHub reviewer
    gh_reviewer = GitHubReviewer(
        github_provider=github,
        reviewer=reviewer,
        default_review_type=ReviewType(review_type)
    )

    # Set review settings
    settings = ReviewSettings(
        max_comments=50 if max_files else None,
        min_severity="suggestion",
        focus_areas=None,
        ignore_patterns=None
    )

    try:
        # Review the pull request
        print(f"🔍 Reviewing PR #{pr_number} in {repo}...")
        reviews = await gh_reviewer.review_pull_request(
            repo,
            pr_number,
            review_type=ReviewType(review_type),
            settings=settings
        )

        # Submit the review
        print("📝 Submitting review comments...")
        await gh_reviewer.submit_review(
            repo,
            pr_number,
            reviews,
            ReviewType(review_type)
        )

        print("✅ Review completed successfully!")

    except Exception as e:
        print(f"❌ Error reviewing pull request: {str(e)}")
        raise


def main():
    parser = argparse.ArgumentParser(
        description="Review a GitHub pull request")
    parser.add_argument("repo", help="Repository name (e.g., 'owner/repo')")
    parser.add_argument("pr", type=int, help="Pull request number")
    parser.add_argument("--github-token", help="GitHub API token")
    parser.add_argument("--ai-token", help="AI provider API token")
    parser.add_argument(
        "--ai-provider",
        default="anthropic",
        choices=ProviderFactory.get_available_providers(),
        help="AI provider to use"
    )
    parser.add_argument(
        "--review-type",
        default="full",
        choices=[t.value for t in ReviewType],
        help="Type of review to perform"
    )
    parser.add_argument(
        "--max-files",
        type=int,
        help="Maximum number of files to review"
    )

    args = parser.parse_args()

    asyncio.run(review_pull_request(
        args.repo,
        args.pr,
        args.github_token,
        args.ai_provider,
        args.ai_token,
        args.review_type,
        args.max_files
    ))


if __name__ == "__main__":
    main()
