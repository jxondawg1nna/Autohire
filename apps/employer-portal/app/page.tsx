'use client';

import { type ChangeEvent, useCallback, useEffect, useMemo, useState } from 'react';

type SyncScope = 'organization' | 'job';

type SyncConfig = {
  scope: SyncScope;
  target_id: string;
  enabled: boolean;
  last_status: string;
  last_synced_at: string | null;
  retries: number;
  error: string | null;
};

type SyncLog = {
  timestamp: string;
  scope: SyncScope;
  target_id: string;
  entity_type: string;
  status: string;
  message: string;
  retry_count: number;
};

type JobRow = {
  id: string;
  title: string;
  enabled: boolean;
  status: string;
  lastSyncedAt: string | null;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000';
const DEFAULT_ORG_ID = 'org-sync';
const DEFAULT_JOBS: JobRow[] = [
  { id: 'job-1001', title: 'Backend Engineer', enabled: false, status: 'disabled', lastSyncedAt: null },
  { id: 'job-1002', title: 'Data Scientist', enabled: false, status: 'disabled', lastSyncedAt: null },
  { id: 'job-1003', title: 'Product Designer', enabled: false, status: 'disabled', lastSyncedAt: null },
];

async function updateConfig(scope: SyncScope, targetId: string, enabled: boolean): Promise<SyncConfig | null> {
  try {
    const response = await fetch(`${API_BASE}/api/opencats/configs/${scope}/${targetId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled }),
    });
    if (!response.ok) {
      throw new Error(`Failed to update ${scope} configuration`);
    }
    return (await response.json()) as SyncConfig;
  } catch (error) {
    console.error(error);
    return null;
  }
}

async function fetchConfigs(scope?: SyncScope): Promise<SyncConfig[]> {
  const params = scope ? `?scope=${scope}` : '';
  try {
    const response = await fetch(`${API_BASE}/api/opencats/configs${params}`);
    if (!response.ok) {
      throw new Error('Unable to fetch sync configurations');
    }
    const payload = (await response.json()) as { items: SyncConfig[] };
    return payload.items;
  } catch (error) {
    console.error(error);
    return [];
  }
}

async function fetchLogs(limit = 15): Promise<SyncLog[]> {
  try {
    const response = await fetch(`${API_BASE}/api/opencats/logs?limit=${limit}`);
    if (!response.ok) {
      throw new Error('Unable to load sync logs');
    }
    const payload = (await response.json()) as { items: SyncLog[] };
    return payload.items;
  } catch (error) {
    console.error(error);
    return [];
  }
}

function formatTimestamp(value: string | null): string {
  if (!value) return '—';
  const date = new Date(value);
  return date.toLocaleString();
}

export default function EmployerSyncPage(): JSX.Element {
  const [organizationEnabled, setOrganizationEnabled] = useState(false);
  const [jobs, setJobs] = useState<JobRow[]>(DEFAULT_JOBS);
  const [logs, setLogs] = useState<SyncLog[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isBusy, setIsBusy] = useState(false);
  const [lastFetched, setLastFetched] = useState<string | null>(null);

  const organizationStatus = useMemo(() => {
    const orgLogs = logs.filter((log) => log.scope === 'organization' && log.target_id === DEFAULT_ORG_ID);
    return orgLogs.length > 0 ? orgLogs[0].status : organizationEnabled ? 'enabled' : 'disabled';
  }, [logs, organizationEnabled]);

  const refreshAll = useCallback(async () => {
    setIsBusy(true);
    const [configs, remoteLogs] = await Promise.all([fetchConfigs(), fetchLogs()]);
    setLogs(remoteLogs);

    const organizationConfig = configs.find((config) => config.scope === 'organization' && config.target_id === DEFAULT_ORG_ID);
    setOrganizationEnabled(Boolean(organizationConfig?.enabled));

    setJobs((current) =>
      current.map((job) => {
        const jobConfig = configs.find((config) => config.scope === 'job' && config.target_id === job.id);
        return {
          ...job,
          enabled: jobConfig?.enabled ?? job.enabled,
          status: jobConfig?.last_status ?? job.status,
          lastSyncedAt: jobConfig?.last_synced_at ?? job.lastSyncedAt,
        };
      }),
    );

    setLastFetched(new Date().toISOString());
    setIsBusy(false);
  }, []);

  useEffect(() => {
    void refreshAll();
  }, [refreshAll]);

  const handleOrganizationToggle = useCallback(
    async (event: ChangeEvent<HTMLInputElement>) => {
      const enabled = event.target.checked;
      setOrganizationEnabled(enabled);
      setError(null);
      const updated = await updateConfig('organization', DEFAULT_ORG_ID, enabled);
      if (!updated) {
        setError('Unable to update organization sync settings.');
        setOrganizationEnabled((prev) => !prev);
        return;
      }
      setOrganizationEnabled(updated.enabled);
      void refreshAll();
    },
    [refreshAll],
  );

  const handleJobToggle = useCallback(
    async (jobId: string, enabled: boolean) => {
      setJobs((current) => current.map((job) => (job.id === jobId ? { ...job, enabled } : job)));
      setError(null);
      const updated = await updateConfig('job', jobId, enabled);
      if (!updated) {
        setError('Unable to update job sync settings.');
        setJobs((current) => current.map((job) => (job.id === jobId ? { ...job, enabled: !enabled } : job)));
        return;
      }
      setJobs((current) =>
        current.map((job) =>
          job.id === jobId
            ? {
                ...job,
                enabled: updated.enabled,
                status: updated.last_status,
                lastSyncedAt: updated.last_synced_at,
              }
            : job,
        ),
      );
      void refreshAll();
    },
    [refreshAll],
  );

  return (
    <main style={{ padding: '3rem', maxWidth: '1100px', margin: '0 auto' }}>
      <header style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>ATS Synchronization</h1>
        <p style={{ color: '#475569', maxWidth: '800px' }}>
          Control how AutoHire shares jobs, candidates, and applications with your OpenCATS instance. Use the toggles below to
          enable synchronization at the organization or per-job level and review recent activity logs.
        </p>
        {error ? <p style={{ color: '#b91c1c' }}>{error}</p> : null}
        <button
          type="button"
          onClick={() => {
            setError(null);
            void refreshAll();
          }}
          style={{ marginTop: '1rem', padding: '0.5rem 1.25rem', borderRadius: '0.5rem', backgroundColor: '#2563eb', color: 'white' }}
        >
          Refresh data
        </button>
        <p style={{ fontSize: '0.875rem', color: '#64748b', marginTop: '0.75rem' }}>
          Last refreshed: {lastFetched ? formatTimestamp(lastFetched) : 'Loading…'} {isBusy ? '(updating…) ' : ''}
        </p>
      </header>

      <section style={{ marginBottom: '2.5rem', padding: '1.5rem', border: '1px solid #e2e8f0', borderRadius: '0.75rem' }}>
        <h2 style={{ fontSize: '1.25rem', marginBottom: '0.75rem' }}>Organization-wide sync</h2>
        <p style={{ color: '#475569', marginBottom: '1rem' }}>
          When enabled, candidate and application updates from every job will be sent to OpenCATS. Disable to pause all outbound
          updates while keeping existing mappings intact.
        </p>
        <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontWeight: 500 }}>
          <input type="checkbox" checked={organizationEnabled} onChange={handleOrganizationToggle} />
          Sync for organization <code>{DEFAULT_ORG_ID}</code>
          <span style={{ fontSize: '0.875rem', color: '#64748b' }}>Status: {organizationStatus}</span>
        </label>
      </section>

      <section style={{ marginBottom: '2.5rem', padding: '1.5rem', border: '1px solid #e2e8f0', borderRadius: '0.75rem' }}>
        <h2 style={{ fontSize: '1.25rem', marginBottom: '0.75rem' }}>Job-level overrides</h2>
        <p style={{ color: '#475569', marginBottom: '1rem' }}>
          Toggle sync per job to keep drafts private or to correct mappings before sending updates.
        </p>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ textAlign: 'left', borderBottom: '1px solid #e2e8f0' }}>
              <th style={{ padding: '0.75rem' }}>Job</th>
              <th style={{ padding: '0.75rem' }}>Status</th>
              <th style={{ padding: '0.75rem' }}>Last synced</th>
              <th style={{ padding: '0.75rem', textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {jobs.map((job) => (
              <tr key={job.id} style={{ borderBottom: '1px solid #e2e8f0' }}>
                <td style={{ padding: '0.75rem' }}>
                  <div style={{ fontWeight: 600 }}>{job.title}</div>
                  <div style={{ fontSize: '0.875rem', color: '#64748b' }}>Job ID: {job.id}</div>
                </td>
                <td style={{ padding: '0.75rem' }}>{job.status}</td>
                <td style={{ padding: '0.75rem' }}>{formatTimestamp(job.lastSyncedAt)}</td>
                <td style={{ padding: '0.75rem', textAlign: 'right' }}>
                  <label style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}>
                    <input
                      type="checkbox"
                      checked={job.enabled}
                      onChange={(event) => void handleJobToggle(job.id, event.target.checked)}
                    />
                    Enable sync
                  </label>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section style={{ padding: '1.5rem', border: '1px solid #e2e8f0', borderRadius: '0.75rem' }}>
        <h2 style={{ fontSize: '1.25rem', marginBottom: '0.75rem' }}>Recent sync activity</h2>
        <p style={{ color: '#475569', marginBottom: '1rem' }}>
          These entries summarize the most recent synchronization attempts sent to OpenCATS. Review errors to understand why a
          record may require manual intervention or a retry from the API.
        </p>
        {logs.length === 0 ? (
          <p style={{ color: '#94a3b8' }}>No logs available yet.</p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ textAlign: 'left', borderBottom: '1px solid #e2e8f0' }}>
                <th style={{ padding: '0.75rem' }}>Timestamp</th>
                <th style={{ padding: '0.75rem' }}>Scope</th>
                <th style={{ padding: '0.75rem' }}>Target</th>
                <th style={{ padding: '0.75rem' }}>Entity</th>
                <th style={{ padding: '0.75rem' }}>Status</th>
                <th style={{ padding: '0.75rem' }}>Message</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={`${log.timestamp}-${log.target_id}-${log.entity_type}`} style={{ borderBottom: '1px solid #e2e8f0' }}>
                  <td style={{ padding: '0.75rem' }}>{formatTimestamp(log.timestamp)}</td>
                  <td style={{ padding: '0.75rem' }}>{log.scope}</td>
                  <td style={{ padding: '0.75rem' }}>{log.target_id}</td>
                  <td style={{ padding: '0.75rem' }}>{log.entity_type}</td>
                  <td style={{ padding: '0.75rem' }}>{log.status}</td>
                  <td style={{ padding: '0.75rem' }}>
                    {log.message}
                    {log.retry_count > 0 ? (
                      <span style={{ marginLeft: '0.5rem', color: '#b45309' }}>(retry #{log.retry_count})</span>
                    ) : null}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </main>
  );
}
