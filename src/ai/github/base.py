from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from github import Github
from github.PullRequest import PullRequest
from github.Repository import Repository
from github.File import File as GithubFile


@dataclass
class PullRequestInfo:
    """Information about a pull request."""
    number: int
    title: str
    body: str
    base_branch: str
    head_branch: str
    author: str
    created_at: datetime
    updated_at: datetime
    files_changed: List[str]
    diff: Optional[str] = None


@dataclass
class ReviewComment:
    """A review comment to be posted on GitHub."""
    body: str
    path: str
    position: Optional[int] = None  # Line number in the diff
    line: Optional[int] = None      # Line number in the file
    commit_id: Optional[str] = None


class GitHubProvider(ABC):
    """Base class for GitHub integration."""

    def __init__(self, token: str):
        self.client = Github(token)

    @abstractmethod
    async def get_repository(self, repo_name: str) -> Repository:
        """Get a GitHub repository."""
        pass

    @abstractmethod
    async def get_pull_request(self, repo: Repository, pr_number: int) -> PullRequestInfo:
        """Get information about a pull request."""
        pass

    @abstractmethod
    async def get_file_content(self, repo: Repository, path: str, ref: str) -> str:
        """Get the content of a file from the repository."""
        pass

    @abstractmethod
    async def create_review_comment(
        self,
        repo: Repository,
        pr_number: int,
        comment: ReviewComment
    ) -> None:
        """Create a review comment on a pull request."""
        pass

    @abstractmethod
    async def create_review(
        self,
        repo: Repository,
        pr_number: int,
        comments: List[ReviewComment],
        body: str,
        event: str = "COMMENT"  # Can be APPROVE, REQUEST_CHANGES, or COMMENT
    ) -> None:
        """Create a complete review on a pull request."""
        pass

    @abstractmethod
    async def get_commit_diff(
        self,
        repo: Repository,
        base_sha: str,
        head_sha: str
    ) -> str:
        """Get the diff between two commits."""
        pass
