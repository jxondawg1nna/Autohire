import { fetchTeams } from "@/lib/api";
import { formatRoles, requireEmployerRole } from "@/lib/auth";
import type { EmployerMember, Team } from "@/lib/types";

const formatMemberTeams = (member: EmployerMember, teams: Team[]) => {
  if (!member.teams.length) {
    return "No team assignments";
  }

  const teamNames = teams
    .filter((team) => member.teams.includes(team.id))
    .map((team) => team.name);

  return teamNames.join(", ");
};

export default async function OrgSetupPage() {
  const { employer } = await requireEmployerRole();
  const teams = await fetchTeams(employer.id);
  const memberLookup = new Map(employer.members.map((member) => [member.user_id, member.name]));

  return (
    <section className="stack">
      <header className="page-header">
        <div>
          <h1>Organization setup</h1>
          <p className="lead">
            Configure teams, membership, and collaboration settings for {employer.name}.
          </p>
        </div>
      </header>
      <div className="card-grid">
        <article className="card">
          <h2>Employer profile</h2>
          <dl className="details">
            <div>
              <dt>Domain</dt>
              <dd>{employer.domain}</dd>
            </div>
            <div>
              <dt>Description</dt>
              <dd>{employer.description}</dd>
            </div>
            <div>
              <dt>Total members</dt>
              <dd>{employer.members.length}</dd>
            </div>
          </dl>
          <p className="hint">
            Use the API to update domains, brand assets, and identity integrations when provisioning new
            organizations.
          </p>
        </article>
        <article className="card">
          <h2>Teams</h2>
          <ul className="list">
            {teams.map((team) => (
              <li key={team.id}>
                <div>
                  <p className="list-title">{team.name}</p>
                  <p className="hint">{team.description}</p>
                </div>
                <span className="list-meta">
                  Leads:
                  {team.leads.length
                    ? ` ${team.leads.map((lead) => memberLookup.get(lead) ?? lead).join(", ")}`
                    : " Assign a lead"}
                </span>
              </li>
            ))}
          </ul>
        </article>
        <article className="card">
          <h2>Members</h2>
          <ul className="list">
            {employer.members.map((member) => (
              <li key={member.user_id}>
                <div>
                  <p className="list-title">{member.name}</p>
                  <p className="hint">{member.email}</p>
                  <p className="hint">Teams: {formatMemberTeams(member, teams)}</p>
                </div>
                <span className="list-meta">{formatRoles(member.roles)}</span>
              </li>
            ))}
          </ul>
        </article>
      </div>
    </section>
  );
}
