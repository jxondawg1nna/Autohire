import JobCreationForm from "@/app/(portal)/_components/JobCreationForm";
import { fetchTeams } from "@/lib/api";
import { requireEmployerRole } from "@/lib/auth";
import type { EmployerRole } from "@/lib/types";

const ALLOWED_ROLES: EmployerRole[] = ["owner", "recruiter"];

export default async function JobCreationPage() {
  const { employer } = await requireEmployerRole(ALLOWED_ROLES);
  const teams = await fetchTeams(employer.id);

  return (
    <section className="stack">
      <header className="page-header">
        <div>
          <h1>Create a job</h1>
          <p className="lead">
            Launch new openings for {employer.name}. Jobs automatically provision hiring pipelines and can
            be synced to sourcing channels.
          </p>
        </div>
      </header>
      {teams.length ? (
        <JobCreationForm employerId={employer.id} teams={teams} />
      ) : (
        <p className="hint">
          You need at least one team configured before jobs can be created. Visit the organization setup page
          to add hiring teams.
        </p>
      )}
    </section>
  );
}
