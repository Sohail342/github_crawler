from fastapi import APIRouter

from app.api.v1 import repository

router = APIRouter()
router.include_router(repository.router, prefix="/api/v1", tags=["Crawl"])
