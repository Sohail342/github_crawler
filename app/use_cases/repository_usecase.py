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

        accumulated_repos = []
        chunk_size = 1000

        async def on_batch(repositories):
            accumulated_repos.extend(repositories)
            if len(accumulated_repos) >= chunk_size:
                # Keep only the latest version of a repo in the current batch
                unique_repos = {r.github_id: r for r in accumulated_repos}.values()
                logger.info(
                    f"Saving de-duplicated batch of {len(unique_repos)} repositories to DB."
                )
                await self.repo_repository.save_batch(list(unique_repos))
                accumulated_repos.clear()

        await self.github_client.run_crawl(
            target_count=target_count, batch_callback=on_batch
        )

        # Save any remaining repositories in the buffer
        if accumulated_repos:
            unique_repos = {r.github_id: r for r in accumulated_repos}.values()
            logger.info(
                f"Saving final de-duplicated batch of {len(unique_repos)} repositories to DB."
            )
            await self.repo_repository.save_batch(list(unique_repos))

        logger.info("Crawl completed successfully.")
