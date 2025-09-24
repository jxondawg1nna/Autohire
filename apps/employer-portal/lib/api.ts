import { API_BASE_URL, DEMO_EMPLOYER_ID, DEMO_USER_ID } from "./config";
import type {
  Application,
  Employer,
  Job,
  JobCreateRequest,
  JobPipeline,
  MicrotaskCampaign,
  Team,
} from "./types";

const defaultHeaders = () => {
  const headers = new Headers();
  headers.set("X-User-Id", DEMO_USER_ID);
  headers.set("X-Employer-Id", DEMO_EMPLOYER_ID);
  return headers;
};

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${path}`;
  const headers = defaultHeaders();
  if (init?.headers) {
    new Headers(init.headers).forEach((value, key) => headers.set(key, value));
  }

  const requestInit: RequestInit = {
    cache: "no-store",
    ...init,
    headers,
  };

  if (requestInit.body && !(requestInit.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(url, requestInit);
  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`;
    try {
      const payload = (await response.json()) as { detail?: string };
      if (payload?.detail) {
        detail = payload.detail;
      }
    } catch (error) {
      // ignore JSON parsing errors for error handling fallback
    }
    throw new Error(detail);
  }

  return (await response.json()) as T;
}

export async function fetchEmployers(): Promise<Employer[]> {
  return apiFetch<Employer[]>("/employers");
}

export async function fetchEmployer(employerId: string): Promise<Employer> {
  return apiFetch<Employer>(`/employers/${employerId}`);
}

export async function fetchTeams(employerId: string): Promise<Team[]> {
  return apiFetch<Team[]>(`/employers/${employerId}/teams`);
}

export async function fetchJobs(employerId: string): Promise<Job[]> {
  return apiFetch<Job[]>(`/employers/${employerId}/jobs`);
}

export async function createJob(employerId: string, payload: JobCreateRequest): Promise<Job> {
  return apiFetch<Job>(`/employers/${employerId}/jobs`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function fetchJobPipeline(employerId: string, jobId: string): Promise<JobPipeline> {
  return apiFetch<JobPipeline>(`/employers/${employerId}/jobs/${jobId}/pipeline`);
}

export async function fetchJobApplications(employerId: string, jobId: string): Promise<Application[]> {
  return apiFetch<Application[]>(`/employers/${employerId}/jobs/${jobId}/applications`);
}

export async function fetchMicrotaskCampaigns(employerId: string): Promise<MicrotaskCampaign[]> {
  return apiFetch<MicrotaskCampaign[]>(`/employers/${employerId}/microtasks/campaigns`);
}
