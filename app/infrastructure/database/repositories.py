from typing import List, Optional

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.domain.models.repository import Repository
from app.domain.repositories.repo_repository import RepositoryRepo
from app.infrastructure.database.models import RepositoryModel


class SqlAlchemyRepository(RepositoryRepo):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_github_id(self, github_id: int) -> Optional[Repository]:
        result = await self.session.execute(
            select(RepositoryModel).where(RepositoryModel.github_id == github_id)
        )
        model = result.scalar_one_or_none()
        return Repository.model_validate(model) if model else None

    async def save_batch(self, repositories: List[Repository]) -> None:
        if not repositories:
            return

        # Upsert
        stmt = insert(RepositoryModel).values(
            [
                {
                    "github_id": r.github_id,
                    "full_name": r.full_name,
                    "stargazer_count": r.stargazer_count,
                    "created_at": r.created_at,
                    "updated_at": r.updated_at,
                    "last_crawled_at": r.last_crawled_at,
                }
                for r in repositories
            ]
        )

        on_conflict_stmt = stmt.on_conflict_do_update(
            index_elements=["github_id"],
            set_={
                "full_name": stmt.excluded.full_name,
                "stargazer_count": stmt.excluded.stargazer_count,
                "updated_at": stmt.excluded.updated_at,
                "last_crawled_at": stmt.excluded.last_crawled_at,
            },
        )

        await self.session.execute(on_conflict_stmt)
        await self.session.commit()

    async def list_all(self, limit: int = 100) -> List[Repository]:
        result = await self.session.execute(select(RepositoryModel).limit(limit))
        models = result.scalars().all()
        return [Repository.model_validate(m) for m in models]
