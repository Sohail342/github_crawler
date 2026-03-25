import argparse
import asyncio
import logging
import os
import sys

from app.core.config import settings
from app.infrastructure.database.repositories import SqlAlchemyRepository
from app.infrastructure.database.session import AsyncSessionLocal
from app.infrastructure.github_api.client import GitHubGraphQLClient
from app.use_cases.repository_usecase import CrawlStarsUseCase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the project root to sys.path to allow imports from 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def run_crawl(target_count: int):
    logger.info(f"Starting CLI crawl for {target_count} repositories.")

    if not settings.GITHUB_TOKEN:
        logger.error("GITHUB_TOKEN is not set in environment variables.")
        sys.exit(1)

    async with AsyncSessionLocal() as session:
        repo_repository = SqlAlchemyRepository(session)
        github_client = GitHubGraphQLClient(settings.GITHUB_TOKEN)
        use_case = CrawlStarsUseCase(repo_repository, github_client)

        try:
            await use_case.execute(target_count)
            logger.info("Crawl completed successfully.")
        except Exception as e:
            logger.error(f"Crawl failed: {e}")
            sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run GitHub repository crawler")
    parser.add_argument(
        "--count",
        type=int,
        default=100000,
        help="Target number of repositories to crawl",
    )
    args = parser.parse_args()

    asyncio.run(run_crawl(args.count))
