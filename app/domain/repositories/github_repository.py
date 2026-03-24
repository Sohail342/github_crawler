from abc import ABC, abstractmethod
from typing import Any, Callable, List, Optional

from app.domain.models.repository import Repository


class GitHubRepository(ABC):
    @abstractmethod
    async def run_crawl(
        self,
        target_count: int = 100000,
        batch_callback: Optional[Callable[[List[Repository]], Any]] = None,
    ) -> None:
        """
        Runs the crawler to fetch repositories from GitHub.

        Args:
            target_count: Total number of repositories to crawl.
            batch_callback: Async callback function called with each batch of repositories.
        """
        pass
