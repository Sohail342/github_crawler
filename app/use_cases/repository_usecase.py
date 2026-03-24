import logging

from app.domain.repositories.github_repository import GitHubRepository
from app.domain.repositories.repo_repository import RepositoryRepo

logger = logging.getLogger(__name__)


class CrawlStarsUseCase:
    def __init__(
        self, repo_repository: RepositoryRepo, github_client: GitHubRepository
    ):
        self.repo_repository = repo_repository
        self.github_client = github_client

    async def execute(self, target_count: int = 100000):
        logger.info(f"Starting crawl for {target_count} repositories.")

        async def on_batch(repositories):
            await self.repo_repository.save_batch(repositories)

        await self.github_client.run_crawl(
            target_count=target_count, batch_callback=on_batch
        )

        logger.info("Crawl completed successfully.")
