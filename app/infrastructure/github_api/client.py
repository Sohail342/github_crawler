import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

import httpx

from app.core.config import settings
from app.domain.models.repository import Repository
from app.domain.repositories.github_repository import GitHubRepository

logger = logging.getLogger(__name__)


class GitHubGraphQLClient(GitHubRepository):
    URL = settings.GITHUB_ENDPOINT

    def __init__(self, token: str):
        self.headers = {"Authorization": f"Bearer {token}"}

    async def fetch_repositories_batch(
        self, query: str = "is:public", after: Optional[str] = None
    ) -> Tuple[List[Repository], Optional[str], Dict[str, Any]]:
        query_gql = """
        query ($query: String!, $cursor: String) {
          search(query: $query, type: REPOSITORY, first: 100, after: $cursor) {
            pageInfo {
              hasNextPage
              endCursor
            }
            edges {
              node {
                ... on Repository {
                  databaseId
                  nameWithOwner
                  stargazerCount
                  createdAt
                  updatedAt
                }
              }
            }
          }
          rateLimit {
            limit
            cost
            remaining
            resetAt
          }
        }
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.URL,
                    json={
                        "query": query_gql,
                        "variables": {"query": query, "cursor": after},
                    },
                    headers=self.headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()

                if "errors" in data:
                    logger.error(f"GraphQL Errors: {data['errors']}")
                    raise Exception(f"GraphQL Errors: {data['errors']}")

                search_data = data["data"]["search"]
                rate_limit = data["data"]["rateLimit"]

                repos = []
                for edge in search_data["edges"]:
                    node = edge["node"]
                    if not node:
                        continue  # Skip null nodes
                    repos.append(
                        Repository(
                            github_id=node["databaseId"],
                            full_name=node["nameWithOwner"],
                            stargazer_count=node["stargazerCount"],
                            created_at=datetime.fromisoformat(
                                node["createdAt"].replace("Z", "+00:00")
                            ),
                            updated_at=datetime.fromisoformat(
                                node["updatedAt"].replace("Z", "+00:00")
                            ),
                            last_crawled_at=datetime.now(timezone.utc),
                        )
                    )

                has_next = search_data["pageInfo"]["hasNextPage"]
                next_cursor = search_data["pageInfo"]["endCursor"] if has_next else None

                return repos, next_cursor, rate_limit

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 403:
                    # Potential rate limit
                    logger.warning("Rate limit hit or forbidden access.")
                raise e

    async def run_crawl(self, target_count: int = 100000, batch_callback=None):
        count = 0

        start_date = datetime(2008, 1, 1, tzinfo=timezone.utc)
        end_date = datetime.now(timezone.utc)

        current_start = start_date
        while count < target_count and current_start < end_date:
            # Partition by day to ensure < 1000 results per segment
            next_start = current_start + timedelta(days=1)
            date_query = f"created:{current_start.date()}"
            query = f"is:public {date_query}"

            logger.info(f"Crawling segment: {query}")

            cursor = None
            segment_count = 0
            while segment_count < 1000:
                repos, cursor, rate_limit = await self.fetch_repositories_batch(
                    query, cursor
                )

                if not repos:
                    break

                if batch_callback:
                    await batch_callback(repos)

                segment_count += len(repos)
                count += len(repos)

                logger.info(
                    f"Progress: {count}/{target_count} repos. Rate Limit: {rate_limit['remaining']}"
                )

                if count >= target_count:
                    return

                if not cursor:
                    break

                # Rate limit handling
                if rate_limit["remaining"] < 100:
                    reset_at = datetime.fromisoformat(
                        rate_limit["resetAt"].replace("Z", "+00:00")
                    )
                    wait_seconds = (
                        reset_at - datetime.now(timezone.utc)
                    ).total_seconds()
                    if wait_seconds > 0:
                        logger.info(
                            f"Rate limit low. Waiting for {wait_seconds:.2f} seconds."
                        )
                        await asyncio.sleep(wait_seconds + 1)

            current_start = next_start
