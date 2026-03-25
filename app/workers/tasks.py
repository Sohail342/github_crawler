import asyncio
import logging

from app.core.config import settings
from app.infrastructure.database.repositories import SqlAlchemyRepository
from app.infrastructure.database.session import AsyncSessionLocal
from app.infrastructure.github_api.client import GitHubGraphQLClient
from app.use_cases.repository_usecase import CrawlStarsUseCase
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.workers.tasks.crawl_repositories_task")
def crawl_repositories_task(target_count: int = 100000):
    """
    Background task to crawl GitHub repositories and save to DB.
    Bridging async use case to synchronous Celery worker using asyncio.run.
    """
    logger.info(f"Starting Celery background crawl for {target_count} repos.")

    if not settings.GITHUB_TOKEN:
        logger.error(
            "GITHUB_TOKEN is not set in the Celery worker environment. Crawl will fail."
        )

    async def _run():
        async with AsyncSessionLocal() as session:
            repo_repository = SqlAlchemyRepository(session)
            github_client = GitHubGraphQLClient(settings.GITHUB_TOKEN)
            use_case = CrawlStarsUseCase(repo_repository, github_client)
            await use_case.execute(target_count)

            from scripts.export_db import export_to_csv

            await export_to_csv("app/repositories.csv")

    try:
        asyncio.run(_run())
        logger.info("Celery background crawl completed successfully.")
    except Exception as e:
        logger.error(f"Celery background crawl failed: {e}")
        raise
