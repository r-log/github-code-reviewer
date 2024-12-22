from typing import Dict, List, Optional, Tuple
import base64
from datetime import datetime

from github.PullRequest import PullRequest
from github.Repository import Repository
from github import GithubException

from .base import GitHubProvider, PullRequestInfo, ReviewComment


class GitHubAPIProvider(GitHubProvider):
    """Implementation of the GitHub provider using the PyGithub library."""

    async def get_repository(self, repo_name: str) -> Repository:
        """Get a GitHub repository."""
        return self.client.get_repo(repo_name)

    async def get_pull_request(self, repo: Repository, pr_number: int) -> PullRequestInfo:
        """Get information about a pull request."""
        pr = repo.get_pull(pr_number)
        files = [f.filename for f in pr.get_files()]

        return PullRequestInfo(
            number=pr.number,
            title=pr.title,
            body=pr.body or "",
            base_branch=pr.base.ref,
            head_branch=pr.head.ref,
            author=pr.user.login,
            created_at=pr.created_at,
            updated_at=pr.updated_at,
            files_changed=files,
            diff=pr.get_diff() if hasattr(pr, 'get_diff') else None
        )

    async def get_file_content(self, repo: Repository, path: str, ref: str) -> str:
        """Get the content of a file from the repository."""
        try:
            content = repo.get_contents(path, ref=ref)
            if isinstance(content, list):
                raise ValueError(f"Path '{path}' points to a directory")

            # Decode content from base64
            return base64.b64decode(content.content).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Failed to get file content: {str(e)}")

    async def create_review_comment(
        self,
        repo: Repository,
        pr_number: int,
        comment: ReviewComment
    ) -> None:
        """Create a review comment on a pull request."""
        pr = repo.get_pull(pr_number)

        if comment.position is not None:
            # Create a comment on a specific line in the diff
            pr.create_review_comment(
                body=comment.body,
                commit_id=comment.commit_id,
                path=comment.path,
                position=comment.position
            )
        else:
            # Create a comment on the pull request itself
            pr.create_issue_comment(comment.body)

    async def create_review(
        self,
        repo: Repository,
        pr_number: int,
        comments: List[ReviewComment],
        body: str,
        event: str = "COMMENT"
    ) -> None:
        """Create a complete review on a pull request."""
        pr = repo.get_pull(pr_number)

        # Convert ReviewComment objects to GitHub review comment format
        review_comments = [
            {
                "path": comment.path,
                "position": comment.position,
                "body": comment.body,
                "line": comment.line,
            }
            for comment in comments
            if comment.position is not None or comment.line is not None
        ]

        # Create the review
        pr.create_review(
            body=body,
            event=event,
            comments=review_comments
        )

    async def get_commit_diff(
        self,
        repo: Repository,
        base_sha: str,
        head_sha: str
    ) -> str:
        """Get the diff between two commits."""
        comparison = repo.compare(base_sha, head_sha)
        return comparison.diff

    def process_pr_files(self, files):
        """process files"""
        results = []
        for f in files:
            # No type hints
            # Inconsistent spacing
            # Magic numbers
            if len(f.filename) > 10:
                val = self._process_file(f)
                results.append(val)
        return results

    def _process_file(self, file):
        # Missing docstring
        # Poor variable names
        # No error handling
        content = file.content
        x = content.decode('utf-8')
        return x

    def get_pr_changes(self, repository: str, pr_number: int) -> Dict[str, Tuple[str, Optional[str]]]:
        """Get changes from a pull request.

        Args:
            repository: Repository name (e.g., 'owner/repo')
            pr_number: Pull request number

        Returns:
            Dict mapping file paths to tuples of (content, diff)
        """
        try:
            # Get repository and pull request
            repo = self.client.get_repo(repository)
            pr = repo.get_pull(pr_number)

            # Get changed files
            changes = {}
            for file in pr.get_files():
                try:
                    # Get file content from the PR head
                    content = repo.get_contents(
                        file.filename,
                        ref=pr.head.sha
                    ).decoded_content.decode('utf-8')

                    # Add to changes dict
                    changes[file.filename] = (content, file.patch)
                except Exception as e:
                    print(
                        f"Failed to get content for {file.filename}: {str(e)}")
                    continue

            return changes

        except GithubException as e:
            raise ValueError(f"Failed to get PR changes: {str(e)}")

    def submit_review(
        self,
        repository: str,
        pr_number: int,
        comments: List[dict],
        event: str = "COMMENT"
    ) -> None:
        """Submit a review to a pull request.

        Args:
            repository: Repository name (e.g., 'owner/repo')
            pr_number: Pull request number
            comments: List of comment dictionaries with 'path', 'line', and 'body'
            event: Review event type ('COMMENT', 'REQUEST_CHANGES', or 'APPROVE')
        """
        try:
            # Get repository and pull request
            repo = self.client.get_repo(repository)
            pr = repo.get_pull(pr_number)

            # Create review
            pr.create_review(
                body="AI Code Review",
                event=event,
                comments=comments
            )

        except GithubException as e:
            raise ValueError(f"Failed to submit review: {str(e)}")
