import { fetchMicrotaskCampaigns } from "@/lib/api";
import { requireEmployerRole } from "@/lib/auth";
import type { EmployerRole, MicrotaskCampaign } from "@/lib/types";

const MICROTASK_ROLES: EmployerRole[] = ["owner", "recruiter", "hiring_manager"];

const summarizeTasks = (campaign: MicrotaskCampaign) => {
  const totals = campaign.tasks.reduce(
    (acc, task) => {
      acc[task.status] = (acc[task.status] ?? 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  );

  const parts = [
    `${campaign.tasks.length} total`,
    `${totals.pending ?? 0} pending`,
    `${totals.in_progress ?? 0} in progress`,
    `${totals.completed ?? 0} complete`,
  ];

  return parts.join(" • ");
};

export default async function MicrotaskCampaignPage() {
  const { employer } = await requireEmployerRole(MICROTASK_ROLES);
  const campaigns = await fetchMicrotaskCampaigns(employer.id);

  return (
    <section className="stack">
      <header className="page-header">
        <div>
          <h1>Microtask campaigns</h1>
          <p className="lead">
            Coordinate sourcing and evaluation campaigns powered by the AutoHire worker network.
          </p>
        </div>
      </header>
      {campaigns.length ? (
        <div className="card-grid">
          {campaigns.map((campaign) => (
            <article key={campaign.id} className="card">
              <header className="card-header">
                <div>
                  <h2>{campaign.name}</h2>
                  <p className="hint">Status: {campaign.status}</p>
                </div>
                {campaign.launch_date ? (
                  <span className="list-meta">
                    Launched {new Date(campaign.launch_date).toLocaleDateString()}
                  </span>
                ) : null}
              </header>
              <p>{campaign.description}</p>
              <p className="hint">{summarizeTasks(campaign)}</p>
              <div className="microtask-list">
                {campaign.tasks.map((task) => (
                  <div key={task.id} className="microtask-item">
                    <p className="list-title">{task.title}</p>
                    <p className="hint">Type: {task.type.replace(/_/g, " ")}</p>
                    <p className="hint">Status: {task.status.replace("_", " ")}</p>
                    {task.related_application_id ? (
                      <p className="hint">Application: {task.related_application_id}</p>
                    ) : null}
                  </div>
                ))}
              </div>
            </article>
          ))}
        </div>
      ) : (
        <p className="hint">
          No microtask campaigns have been launched yet. Use the API to configure sourcing or evaluation
          projects, then monitor progress here.
        </p>
      )}
    </section>
  );
}
