from fastapi import APIRouter

router = APIRouter()


@router.get("/crawl")
async def trigger_crawl(
    count: int = 100,
):
    from app.workers.tasks import crawl_repositories_task

    crawl_repositories_task.delay(count)
    return {"message": f"Crawl started for {count} repositories in the background."}
