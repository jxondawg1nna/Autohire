export type EmployerRole = "owner" | "recruiter" | "hiring_manager" | "contributor";

export const EMPLOYER_ROLE_LABELS: Record<EmployerRole, string> = {
  owner: "Owner",
  recruiter: "Recruiter",
  hiring_manager: "Hiring manager",
  contributor: "Contributor",
};

export type EmployerMember = {
  user_id: string;
  email: string;
  name: string;
  roles: EmployerRole[];
  teams: string[];
};

export type Employer = {
  id: string;
  name: string;
  domain: string;
  description?: string | null;
  members: EmployerMember[];
};

export type Team = {
  id: string;
  employer_id: string;
  name: string;
  description?: string | null;
  leads: string[];
};

export type JobStatus = "open" | "on_hold" | "closed";

export type Job = {
  id: string;
  employer_id: string;
  team_id: string;
  title: string;
  description?: string | null;
  status: JobStatus;
  openings: number;
  location: string;
  created_at: string;
  pipeline_id: string;
  hiring_manager_id?: string | null;
};

export type PipelineStage = {
  id: string;
  name: string;
  order: number;
  description?: string | null;
  exit_criteria?: string | null;
};

export type JobPipeline = {
  id: string;
  employer_id: string;
  job_id: string;
  stages: PipelineStage[];
};

export type JobCreateRequest = {
  title: string;
  team_id: string;
  location: string;
  openings: number;
  description?: string;
};

export type ApplicationStatus = "new" | "screening" | "interview" | "offer" | "hired" | "rejected";

export type Application = {
  id: string;
  employer_id: string;
  job_id: string;
  candidate_name: string;
  candidate_email: string;
  status: ApplicationStatus;
  stage_id: string;
  submitted_at: string;
  resume_url?: string | null;
  overall_score?: number | null;
};

export type MicrotaskType =
  | "resume_review"
  | "structured_interview"
  | "skill_validation"
  | "data_enrichment";

export type MicrotaskStatus = "pending" | "in_progress" | "completed";

export type Microtask = {
  id: string;
  employer_id: string;
  campaign_id: string;
  title: string;
  type: MicrotaskType;
  status: MicrotaskStatus;
  instructions: string;
  assignee?: string | null;
  related_application_id?: string | null;
  stage_id?: string | null;
  due_at?: string | null;
  metadata: Record<string, string>;
};

export type CampaignStatus = "draft" | "active" | "paused" | "completed";

export type MicrotaskCampaign = {
  id: string;
  employer_id: string;
  job_id?: string | null;
  name: string;
  description: string;
  status: CampaignStatus;
  launch_date?: string | null;
  target_stage_id?: string | null;
  tasks: Microtask[];
};
