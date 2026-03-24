from fastapi import APIRouter, BackgroundTasks, Depends

from app.api.v1.dependencies import get_crawl_usecase, run_crawl_safely
from app.use_cases.repository_usecase import CrawlStarsUseCase

router = APIRouter()


@router.get("/crawl")
async def trigger_crawl(
    background_tasks: BackgroundTasks,
    count: int = 100,
    use_case: CrawlStarsUseCase = Depends(get_crawl_usecase),
):
    background_tasks.add_task(run_crawl_safely, use_case, count)
    return {"message": f"Crawl started for {count} repositories in the background."}
