import { fetchJobApplications, fetchJobPipeline, fetchJobs } from "@/lib/api";
import { requireEmployerRole } from "@/lib/auth";
import type { EmployerRole, Job, JobPipeline } from "@/lib/types";

const PIPELINE_ROLES: EmployerRole[] = ["owner", "recruiter", "hiring_manager"];

type PipelineSummary = {
  job: Job;
  pipeline: JobPipeline;
  stageCounts: { stageId: string; label: string; count: number }[];
};

export default async function PipelineManagementPage() {
  const { employer } = await requireEmployerRole(PIPELINE_ROLES);
  const jobs = await fetchJobs(employer.id);

  if (!jobs.length) {
    return (
      <section className="stack">
        <header className="page-header">
          <h1>Pipeline management</h1>
          <p className="lead">Create a job first to configure candidate pipelines.</p>
        </header>
        <p className="hint">
          Jobs provision default pipelines that can be tuned for each role. Add customized stages to reflect
          your screening workflow.
        </p>
      </section>
    );
  }

  const pipelineSummaries: PipelineSummary[] = await Promise.all(
    jobs.map(async (job) => {
      const [pipeline, applications] = await Promise.all([
        fetchJobPipeline(employer.id, job.id),
        fetchJobApplications(employer.id, job.id),
      ]);

      const stageCounts = pipeline.stages.map((stage) => ({
        stageId: stage.id,
        label: stage.name,
        count: applications.filter((application) => application.stage_id === stage.id).length,
      }));

      return { job, pipeline, stageCounts };
    })
  );

  return (
    <section className="stack">
      <header className="page-header">
        <div>
          <h1>Pipeline management</h1>
          <p className="lead">
            Monitor stage progression and identify bottlenecks across jobs for {employer.name}.
          </p>
        </div>
      </header>
      <div className="stack">
        {pipelineSummaries.map(({ job, pipeline, stageCounts }) => (
          <article key={job.id} className="card">
            <header className="card-header">
              <div>
                <h2>{job.title}</h2>
                <p className="hint">
                  {job.location} • {pipeline.stages.length} stages • {job.openings} open role
                  {job.openings > 1 ? "s" : ""}
                </p>
              </div>
            </header>
            <div className="stage-list">
              {stageCounts.map((stage) => (
                <div key={stage.stageId} className="stage-pill">
                  <p className="stage-name">{stage.label}</p>
                  <p className="stage-count">{stage.count} applicants</p>
                </div>
              ))}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
