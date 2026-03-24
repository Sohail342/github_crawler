from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class Repository(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    github_id: int
    full_name: str
    stargazer_count: int
    created_at: datetime
    updated_at: datetime
    last_crawled_at: Optional[datetime] = None
