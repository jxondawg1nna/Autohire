from fastapi import APIRouter

from . import candidates, jobs, opencats

api_router = APIRouter()
api_router.include_router(candidates.router, prefix="/candidates", tags=["candidates"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(opencats.router, prefix="/opencats", tags=["opencats"])
