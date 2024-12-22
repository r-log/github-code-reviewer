from typing import List
import base64
from datetime import datetime

from github.PullRequest import PullRequest
from github.Repository import Repository

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
