from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RepositoryDTO(BaseModel):
    github_id: int
    full_name: str
    stargazer_count: int
    created_at: datetime
    updated_at: datetime
    last_crawled_at: Optional[datetime] = None

    class Config:
        from_attributes = True
