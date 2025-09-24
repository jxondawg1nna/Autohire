export default function HomePage() {
  return (
    <main style={{ padding: "4rem", maxWidth: "960px", margin: "0 auto" }}>
      <h1>AutoHire Admin Console</h1>
      <p>
        The admin console will host moderation tools, taxonomy management, feature
        flags, scraping configurations, and observability links for the AutoHire platform.
      </p>
      <ul>
        <li>User and organization administration</li>
        <li>Skills and taxonomy curation</li>
        <li>Feature flag toggles and rollout controls</li>
        <li>Operational dashboards and alerts</li>
      </ul>
      <p>
        Implementation details are documented throughout the `docs/` directory.
      </p>
    </main>
  );
}
