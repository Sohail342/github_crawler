from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.models.repository import Repository


class RepositoryRepo(ABC):
    @abstractmethod
    async def get_by_github_id(self, github_id: int) -> Optional[Repository]:
        pass

    @abstractmethod
    async def save_batch(self, repositories: List[Repository]) -> None:
        pass

    @abstractmethod
    async def list_all(self, limit: int = 100) -> List[Repository]:
        pass
