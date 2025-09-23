from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def list_jobs() -> dict[str, str]:
    """Placeholder endpoint returning jobs using hybrid search filters."""

    return {"message": "Job listing endpoint stub."}


@router.get("/{job_id}")
async def get_job(job_id: str) -> dict[str, str]:
    """Placeholder endpoint returning job detail."""

    return {"message": f"Details for job {job_id} will be served here."}
