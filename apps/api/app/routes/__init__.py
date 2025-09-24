"""Route configuration for the AutoHire API."""

from fastapi import APIRouter

from . import candidates, employers, jobs, microtasks

api_router = APIRouter()
api_router.include_router(candidates.router, prefix="/candidates", tags=["candidates"])
api_router.include_router(employers.router, prefix="/employers", tags=["employers"])
api_router.include_router(
    jobs.router,
    prefix="/employers/{employer_id}/jobs",
    tags=["jobs"],
)
api_router.include_router(
    microtasks.router,
    prefix="/employers/{employer_id}/microtasks",
    tags=["microtasks"],
)
