from sqlalchemy import BigInteger, Column, DateTime, Integer, String

from app.infrastructure.database.base_class import Base


class RepositoryModel(Base):
    __tablename__ = "repositories"

    github_id = Column(BigInteger, primary_key=True, index=True)
    full_name = Column(String, index=True, unique=True)
    stargazer_count = Column(Integer)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    last_crawled_at = Column(DateTime(timezone=True), nullable=True)
