export default function HomePage() {
  return (
    <main style={{ padding: "4rem", maxWidth: "960px", margin: "0 auto" }}>
      <h1>AutoHire Candidate Portal</h1>
      <p>
        This is the placeholder experience for the candidate-facing application. It
        will eventually surface onboarding, profile management, job discovery, microtasks,
        and automation controls.
      </p>
      <ul>
        <li>Onboarding wizard with resume parsing</li>
        <li>Job and microtask discovery with hybrid search</li>
        <li>Auto-apply rules and resume improvement workflows</li>
      </ul>
      <p>
        Refer to the documentation in <code>docs/</code> for the comprehensive
        specification and acceptance criteria.
      </p>
    </main>
  );
}
