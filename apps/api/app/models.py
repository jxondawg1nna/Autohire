"""Domain models and in-memory fixtures for the AutoHire API."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, EmailStr, Field


class EmployerRole(str, Enum):
    """Role assignments available to employer members."""

    OWNER = "owner"
    RECRUITER = "recruiter"
    HIRING_MANAGER = "hiring_manager"
    CONTRIBUTOR = "contributor"


class EmployerMember(BaseModel):
    """Representation of a user that belongs to an employer organization."""

    user_id: str = Field(..., description="Unique identifier for the user within AutoHire.")
    email: EmailStr = Field(..., description="Work email for the employer member.")
    name: str = Field(..., description="Full name of the member.")
    roles: List[EmployerRole] = Field(default_factory=list, description="Roles granted within the employer.")
    teams: List[str] = Field(default_factory=list, description="IDs of teams the member participates in.")


class Employer(BaseModel):
    """Top-level organization that owns teams, jobs, and workflows."""

    id: str
    name: str
    domain: str
    description: Optional[str] = None
    members: List[EmployerMember] = Field(default_factory=list)


class Team(BaseModel):
    """Functional team within an employer."""

    id: str
    employer_id: str
    name: str
    description: Optional[str] = None
    leads: List[str] = Field(default_factory=list, description="User IDs for the team leads.")


class JobStatus(str, Enum):
    """Lifecycle states for a job opening."""

    OPEN = "open"
    ON_HOLD = "on_hold"
    CLOSED = "closed"


class PipelineStage(BaseModel):
    """A single step in a job pipeline."""

    id: str
    name: str
    order: int
    description: Optional[str] = None
    exit_criteria: Optional[str] = None


class JobPipeline(BaseModel):
    """Workflow definition that candidates move through for a job."""

    id: str
    employer_id: str
    job_id: str
    stages: List[PipelineStage] = Field(default_factory=list)


class Job(BaseModel):
    """Job opening posted by an employer."""

    id: str
    employer_id: str
    team_id: str
    title: str
    description: Optional[str] = None
    status: JobStatus = JobStatus.OPEN
    openings: int = Field(default=1, ge=1)
    location: str
    created_at: datetime
    pipeline_id: str
    hiring_manager_id: Optional[str] = None


class ApplicationStatus(str, Enum):
    """Possible states for an application."""

    NEW = "new"
    SCREENING = "screening"
    INTERVIEW = "interview"
    OFFER = "offer"
    HIRED = "hired"
    REJECTED = "rejected"


class Application(BaseModel):
    """Candidate submission for a particular job."""

    id: str
    employer_id: str
    job_id: str
    candidate_name: str
    candidate_email: EmailStr
    status: ApplicationStatus
    stage_id: str
    submitted_at: datetime
    resume_url: Optional[str] = None
    overall_score: Optional[float] = None


class MicrotaskType(str, Enum):
    """Types of microtasks available."""

    RESUME_REVIEW = "resume_review"
    STRUCTURED_INTERVIEW = "structured_interview"
    SKILL_VALIDATION = "skill_validation"
    DATA_ENRICHMENT = "data_enrichment"


class MicrotaskStatus(str, Enum):
    """Current status of a microtask."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Microtask(BaseModel):
    """Discrete task executed by marketplace workers."""

    id: str
    employer_id: str
    campaign_id: str
    title: str
    type: MicrotaskType
    status: MicrotaskStatus
    instructions: str
    assignee: Optional[str] = None
    related_application_id: Optional[str] = None
    stage_id: Optional[str] = None
    due_at: Optional[datetime] = None
    metadata: Dict[str, str] = Field(default_factory=dict)


class CampaignStatus(str, Enum):
    """Lifecycle of a microtask campaign."""

    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class MicrotaskCampaign(BaseModel):
    """Grouping of microtasks launched for a hiring initiative."""

    id: str
    employer_id: str
    job_id: Optional[str] = None
    name: str
    description: str
    status: CampaignStatus
    launch_date: Optional[datetime] = None
    target_stage_id: Optional[str] = None
    tasks: List[Microtask] = Field(default_factory=list)


class JobCreateRequest(BaseModel):
    """Payload used when creating a new job posting."""

    title: str
    team_id: str
    location: str
    openings: int = Field(default=1, ge=1)
    description: Optional[str] = None


@dataclass
class EmployerContext:
    """Context helper returned from authorization checks."""

    employer: Employer
    member: EmployerMember


# ---------------------------------------------------------------------------
# In-memory fixtures
# ---------------------------------------------------------------------------

_EMPLOYERS: Dict[str, Employer] = {
    "emp-1": Employer(
        id="emp-1",
        name="Acme Robotics",
        domain="acmerobotics.com",
        description=(
            "Industrial robotics manufacturer building autonomous assembly systems for "
            "advanced factories."
        ),
        members=[
            EmployerMember(
                user_id="user-1",
                email="alicia.chen@acmerobotics.com",
                name="Alicia Chen",
                roles=[EmployerRole.OWNER, EmployerRole.RECRUITER],
                teams=["team-talent", "team-engineering"],
            ),
            EmployerMember(
                user_id="user-2",
                email="marcus.reed@acmerobotics.com",
                name="Marcus Reed",
                roles=[EmployerRole.RECRUITER],
                teams=["team-talent"],
            ),
            EmployerMember(
                user_id="user-3",
                email="priya.natarajan@acmerobotics.com",
                name="Priya Natarajan",
                roles=[EmployerRole.HIRING_MANAGER],
                teams=["team-engineering"],
            ),
            EmployerMember(
                user_id="user-4",
                email="diego.alvarez@acmerobotics.com",
                name="Diego Alvarez",
                roles=[EmployerRole.CONTRIBUTOR],
                teams=["team-operations"],
            ),
        ],
    )
}

_TEAMS: List[Team] = [
    Team(
        id="team-talent",
        employer_id="emp-1",
        name="Talent Acquisition",
        description="Central recruiting operations coordinating hiring activities.",
        leads=["user-1"],
    ),
    Team(
        id="team-engineering",
        employer_id="emp-1",
        name="Engineering Hiring",
        description="Focuses on robotics software and controls engineering roles.",
        leads=["user-3"],
    ),
    Team(
        id="team-operations",
        employer_id="emp-1",
        name="Operations Recruiting",
        description="Supports plant operations and implementation staff hiring.",
        leads=["user-4"],
    ),
]

_JOBS: List[Job] = [
    Job(
        id="job-robotics-se",
        employer_id="emp-1",
        team_id="team-engineering",
        title="Robotics Software Engineer",
        description=(
            "Own motion planning and perception algorithms for next-generation "
            "assembly lines."
        ),
        status=JobStatus.OPEN,
        openings=2,
        location="Seattle, WA (Hybrid)",
        created_at=datetime(2024, 1, 12, 14, 30, tzinfo=timezone.utc),
        pipeline_id="pipe-robotics-se",
        hiring_manager_id="user-3",
    ),
    Job(
        id="job-controls-lead",
        employer_id="emp-1",
        team_id="team-engineering",
        title="Controls Engineering Lead",
        description="Lead PLC and controls architecture for automated manufacturing cells.",
        status=JobStatus.OPEN,
        openings=1,
        location="Austin, TX",
        created_at=datetime(2024, 2, 3, 9, 15, tzinfo=timezone.utc),
        pipeline_id="pipe-controls-lead",
        hiring_manager_id="user-3",
    ),
    Job(
        id="job-ops-analyst",
        employer_id="emp-1",
        team_id="team-operations",
        title="Manufacturing Operations Analyst",
        description="Analyze deployment data and operational readiness for new lines.",
        status=JobStatus.ON_HOLD,
        openings=1,
        location="Remote - North America",
        created_at=datetime(2023, 12, 5, 16, 5, tzinfo=timezone.utc),
        pipeline_id="pipe-ops-analyst",
        hiring_manager_id="user-4",
    ),
]

_PIPELINES: Dict[str, JobPipeline] = {
    "job-robotics-se": JobPipeline(
        id="pipe-robotics-se",
        employer_id="emp-1",
        job_id="job-robotics-se",
        stages=[
            PipelineStage(
                id="stage-robotics-1",
                name="Resume Review",
                order=1,
                description="Talent team screens resumes for robotics experience.",
                exit_criteria="Meets robotics software prerequisites",
            ),
            PipelineStage(
                id="stage-robotics-2",
                name="Technical Phone Screen",
                order=2,
                description="Live coding and perception systems discussion.",
                exit_criteria="Score of 3+ on evaluation rubric",
            ),
            PipelineStage(
                id="stage-robotics-3",
                name="Onsite Interview",
                order=3,
                description="Full-day onsite with cross-functional panel.",
                exit_criteria="Green from two technical panels",
            ),
            PipelineStage(
                id="stage-robotics-4",
                name="Offer",
                order=4,
                description="Final approvals, compensation, and closing tasks.",
            ),
        ],
    ),
    "job-controls-lead": JobPipeline(
        id="pipe-controls-lead",
        employer_id="emp-1",
        job_id="job-controls-lead",
        stages=[
            PipelineStage(
                id="stage-controls-1",
                name="Resume Review",
                order=1,
                description="Recruiting ops validates PLC project history.",
            ),
            PipelineStage(
                id="stage-controls-2",
                name="Panel Interview",
                order=2,
                description="Cross-disciplinary engineering panel interview.",
            ),
            PipelineStage(
                id="stage-controls-3",
                name="Leadership Round",
                order=3,
                description="Executive alignment and team leadership assessment.",
            ),
        ],
    ),
    "job-ops-analyst": JobPipeline(
        id="pipe-ops-analyst",
        employer_id="emp-1",
        job_id="job-ops-analyst",
        stages=[
            PipelineStage(
                id="stage-ops-1",
                name="Resume Review",
                order=1,
                description="Operations team reviews analytics and Six Sigma background.",
            ),
            PipelineStage(
                id="stage-ops-2",
                name="Case Study",
                order=2,
                description="Timed scenario evaluating deployment throughput."
            ),
            PipelineStage(
                id="stage-ops-3",
                name="Final Interview",
                order=3,
                description="Panel with manufacturing leadership.",
            ),
        ],
    ),
}

_APPLICATIONS: List[Application] = [
    Application(
        id="app-001",
        employer_id="emp-1",
        job_id="job-robotics-se",
        candidate_name="Sasha Patel",
        candidate_email="sasha.patel@example.com",
        status=ApplicationStatus.SCREENING,
        stage_id="stage-robotics-2",
        submitted_at=datetime(2024, 2, 5, 17, 45, tzinfo=timezone.utc),
        resume_url="https://files.autohire.dev/resumes/sasha-patel.pdf",
        overall_score=3.7,
    ),
    Application(
        id="app-002",
        employer_id="emp-1",
        job_id="job-robotics-se",
        candidate_name="Kerry Johnson",
        candidate_email="kerry.johnson@example.com",
        status=ApplicationStatus.NEW,
        stage_id="stage-robotics-1",
        submitted_at=datetime(2024, 2, 8, 11, 12, tzinfo=timezone.utc),
        resume_url="https://files.autohire.dev/resumes/kerry-johnson.pdf",
    ),
    Application(
        id="app-003",
        employer_id="emp-1",
        job_id="job-controls-lead",
        candidate_name="Omar Siddiqui",
        candidate_email="omar.siddiqui@example.com",
        status=ApplicationStatus.INTERVIEW,
        stage_id="stage-controls-2",
        submitted_at=datetime(2024, 1, 29, 15, 5, tzinfo=timezone.utc),
        overall_score=4.2,
    ),
    Application(
        id="app-004",
        employer_id="emp-1",
        job_id="job-ops-analyst",
        candidate_name="Dana Flores",
        candidate_email="dana.flores@example.com",
        status=ApplicationStatus.SCREENING,
        stage_id="stage-ops-1",
        submitted_at=datetime(2023, 12, 21, 10, 40, tzinfo=timezone.utc),
    ),
]

_MICROTASK_CAMPAIGNS: Dict[str, MicrotaskCampaign] = {
    "camp-robotics-resume": MicrotaskCampaign(
        id="camp-robotics-resume",
        employer_id="emp-1",
        job_id="job-robotics-se",
        name="Robotics Resume Review Sprint",
        description="Crowdsourced evaluation of robotics software candidate resumes.",
        status=CampaignStatus.ACTIVE,
        launch_date=datetime(2024, 2, 6, 13, 0, tzinfo=timezone.utc),
        target_stage_id="stage-robotics-1",
        tasks=[
            Microtask(
                id="task-robotics-1",
                employer_id="emp-1",
                campaign_id="camp-robotics-resume",
                title="Evaluate robotics perception experience",
                type=MicrotaskType.RESUME_REVIEW,
                status=MicrotaskStatus.IN_PROGRESS,
                instructions="Score perception and motion planning experience against rubric.",
                assignee="worker-21",
                related_application_id="app-001",
                stage_id="stage-robotics-1",
                due_at=datetime(2024, 2, 9, 23, 59, tzinfo=timezone.utc),
                metadata={"resume_url": "https://files.autohire.dev/resumes/sasha-patel.pdf"},
            ),
            Microtask(
                id="task-robotics-2",
                employer_id="emp-1",
                campaign_id="camp-robotics-resume",
                title="Score robotics controls background",
                type=MicrotaskType.RESUME_REVIEW,
                status=MicrotaskStatus.PENDING,
                instructions="Confirm PLC, C++, and ROS2 experience meets baseline.",
                related_application_id="app-002",
                stage_id="stage-robotics-1",
                due_at=datetime(2024, 2, 10, 18, 0, tzinfo=timezone.utc),
            ),
        ],
    ),
    "camp-controls-calibration": MicrotaskCampaign(
        id="camp-controls-calibration",
        employer_id="emp-1",
        job_id="job-controls-lead",
        name="Controls Interview Calibration",
        description="Align panel scoring for controls engineering leadership interviews.",
        status=CampaignStatus.PAUSED,
        launch_date=datetime(2024, 1, 18, 9, 30, tzinfo=timezone.utc),
        target_stage_id="stage-controls-2",
        tasks=[
            Microtask(
                id="task-controls-1",
                employer_id="emp-1",
                campaign_id="camp-controls-calibration",
                title="Review panel rubric alignment",
                type=MicrotaskType.DATA_ENRICHMENT,
                status=MicrotaskStatus.COMPLETED,
                instructions="Aggregate interviewer feedback for rubric improvement.",
                assignee="worker-42",
                stage_id="stage-controls-2",
            ),
            Microtask(
                id="task-controls-2",
                employer_id="emp-1",
                campaign_id="camp-controls-calibration",
                title="Score sample interview transcript",
                type=MicrotaskType.STRUCTURED_INTERVIEW,
                status=MicrotaskStatus.PENDING,
                instructions="Score calibration interview using leadership rubric.",
                stage_id="stage-controls-2",
            ),
        ],
    ),
}


# ---------------------------------------------------------------------------
# Query helpers
# ---------------------------------------------------------------------------

def list_employers_for_user(user_id: str) -> List[Employer]:
    """Return employers the supplied user belongs to."""

    return [
        employer
        for employer in _EMPLOYERS.values()
        if any(member.user_id == user_id for member in employer.members)
    ]


def get_employer(employer_id: str) -> Optional[Employer]:
    """Fetch a single employer by its identifier."""

    return _EMPLOYERS.get(employer_id)


def get_employer_member(employer_id: str, user_id: str) -> Optional[EmployerMember]:
    """Look up membership for a user within an employer."""

    employer = get_employer(employer_id)
    if not employer:
        return None
    return next((member for member in employer.members if member.user_id == user_id), None)


def list_teams_for_employer(employer_id: str) -> List[Team]:
    """Return all teams for an employer."""

    return [team for team in _TEAMS if team.employer_id == employer_id]


def get_team(employer_id: str, team_id: str) -> Optional[Team]:
    """Retrieve a specific team ensuring it belongs to the employer."""

    team = next((team for team in _TEAMS if team.id == team_id), None)
    if team and team.employer_id == employer_id:
        return team
    return None


def list_jobs_for_employer(employer_id: str) -> List[Job]:
    """Return jobs scoped to the employer."""

    return [job for job in _JOBS if job.employer_id == employer_id]


def get_job_for_employer(employer_id: str, job_id: str) -> Optional[Job]:
    """Fetch a job verifying it belongs to the employer."""

    job = next((job for job in _JOBS if job.id == job_id), None)
    if job and job.employer_id == employer_id:
        return job
    return None


def get_job_pipeline(employer_id: str, job_id: str) -> Optional[JobPipeline]:
    """Return the pipeline for a job if owned by the employer."""

    pipeline = _PIPELINES.get(job_id)
    if pipeline and pipeline.employer_id == employer_id:
        return pipeline
    return None


def list_job_applications(employer_id: str, job_id: str) -> List[Application]:
    """Retrieve applications for a job scoped to the employer."""

    return [
        application
        for application in _APPLICATIONS
        if application.job_id == job_id and application.employer_id == employer_id
    ]


def list_microtask_campaigns(employer_id: str) -> List[MicrotaskCampaign]:
    """Return microtask campaigns for the employer."""

    return [campaign for campaign in _MICROTASK_CAMPAIGNS.values() if campaign.employer_id == employer_id]


def get_microtask_campaign(employer_id: str, campaign_id: str) -> Optional[MicrotaskCampaign]:
    """Fetch a specific microtask campaign scoped to the employer."""

    campaign = _MICROTASK_CAMPAIGNS.get(campaign_id)
    if campaign and campaign.employer_id == employer_id:
        return campaign
    return None


def list_microtasks_for_campaign(employer_id: str, campaign_id: str) -> List[Microtask]:
    """Return microtasks for a campaign ensuring tenant isolation."""

    campaign = get_microtask_campaign(employer_id, campaign_id)
    return campaign.tasks if campaign else []


# ---------------------------------------------------------------------------
# Mutation helpers (stub implementations)
# ---------------------------------------------------------------------------

def create_job(employer_id: str, request: JobCreateRequest) -> Job:
    """Create a job with a default pipeline for demonstration purposes."""

    if not get_employer(employer_id):
        raise ValueError("Employer does not exist.")

    if not get_team(employer_id, request.team_id):
        raise ValueError("Team does not belong to employer.")

    job_id = f"job-{uuid4().hex[:8]}"
    pipeline_id = f"pipe-{uuid4().hex[:8]}"
    created_at = datetime.now(tz=timezone.utc)

    job = Job(
        id=job_id,
        employer_id=employer_id,
        team_id=request.team_id,
        title=request.title,
        description=request.description,
        status=JobStatus.OPEN,
        openings=request.openings,
        location=request.location,
        created_at=created_at,
        pipeline_id=pipeline_id,
    )

    default_stages = [
        PipelineStage(
            id=f"{pipeline_id}-stage-1",
            name="Resume Review",
            order=1,
            description="Recruiting review for basic qualifications.",
        ),
        PipelineStage(
            id=f"{pipeline_id}-stage-2",
            name="Phone Screen",
            order=2,
            description="Initial recruiter or hiring manager conversation.",
        ),
        PipelineStage(
            id=f"{pipeline_id}-stage-3",
            name="Interview Loop",
            order=3,
            description="Structured onsite or virtual interview loop.",
        ),
        PipelineStage(
            id=f"{pipeline_id}-stage-4",
            name="Offer",
            order=4,
            description="Final offer creation and approvals.",
        ),
    ]

    pipeline = JobPipeline(
        id=pipeline_id,
        employer_id=employer_id,
        job_id=job_id,
        stages=default_stages,
    )

    _JOBS.append(job)
    _PIPELINES[job_id] = pipeline

    return job
