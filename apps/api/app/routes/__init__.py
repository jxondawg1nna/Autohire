from fastapi import APIRouter

from . import application_logs, auto_apply_rules, candidates, jobs, resume_templates

api_router = APIRouter()
api_router.include_router(candidates.router, prefix="/candidates", tags=["candidates"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(resume_templates.router, prefix="/resume-templates", tags=["resume templates"])
api_router.include_router(auto_apply_rules.router, prefix="/auto-apply-rules", tags=["auto apply rules"])
api_router.include_router(application_logs.router, prefix="/application-logs", tags=["application logs"])
