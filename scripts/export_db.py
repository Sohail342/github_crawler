import asyncio
import csv
import logging
import os
import sys

from sqlalchemy import select

from app.infrastructure.database.models import RepositoryModel
from app.infrastructure.database.session import AsyncSessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the project root to sys.path to allow imports from 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def export_to_csv(filename: str = "repositories.csv"):
    logger.info(f"Exporting repositories to {filename}...")

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(RepositoryModel))
        repos = result.scalars().all()

        if not repos:
            logger.info(
                "No repositories found in the database. Creating an empty CSV with headers."
            )

        with open(filename, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(
                [
                    "github_id",
                    "full_name",
                    "stargazer_count",
                    "created_at",
                    "updated_at",
                    "last_crawled_at",
                ]
            )

            for repo in repos:
                writer.writerow(
                    [
                        repo.github_id,
                        repo.full_name,
                        repo.stargazer_count,
                        repo.created_at.isoformat() if repo.created_at else "",
                        repo.updated_at.isoformat() if repo.updated_at else "",
                        repo.last_crawled_at.isoformat()
                        if repo.last_crawled_at
                        else "",
                    ]
                )

    logger.info(f"Exported {len(repos)} repositories successfully.")


if __name__ == "__main__":
    asyncio.run(export_to_csv())
