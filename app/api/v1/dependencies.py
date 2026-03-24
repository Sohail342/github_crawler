from venv import logger

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.infrastructure.database.repositories import SqlAlchemyRepository
from app.infrastructure.database.session import get_db
from app.infrastructure.github_api.client import GitHubGraphQLClient
from app.use_cases.repository_usecase import CrawlStarsUseCase


async def get_crawl_usecase(db: AsyncSession = Depends(get_db)) -> CrawlStarsUseCase:
    repo_repository = SqlAlchemyRepository(db)
    github_client = GitHubGraphQLClient(settings.GITHUB_TOKEN)
    return CrawlStarsUseCase(repo_repository, github_client)


async def run_crawl_safely(use_case: CrawlStarsUseCase, target_count: int):
    try:
        await use_case.execute(target_count)
    except Exception as e:
        logger.error(f"Crawl failed: {e}")
