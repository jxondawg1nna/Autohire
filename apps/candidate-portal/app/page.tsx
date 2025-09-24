"use client";

import type { ChangeEvent, FormEvent } from "react";
import { useMemo, useState } from "react";

type TemplateSection = {
  title: string;
  content: string;
};

type ResumeTemplate = {
  id: string;
  name: string;
  description: string;
  sections: TemplateSection[];
  variables: string[];
  coverLetterTemplate?: string | null;
};

type AutoApplyRule = {
  id: string;
  name: string;
  targetRole: string;
  keywords: string[];
  locations: string[];
  resumeTemplateId: string | null;
  coverLetterTemplateId: string | null;
  status: "active" | "paused";
};

type AutomationStep = {
  name: string;
  status: "pending" | "running" | "completed" | "failed";
  timestamp: string;
  detail?: string;
};

type AutomationLog = {
  id: string;
  ruleId: string | null;
  jobId: string;
  jobTitle: string;
  company: string;
  channel: "native" | "playwright";
  status: "submitted" | "failed" | "skipped";
  submittedAt: string;
  auditTrail: AutomationStep[];
  notes?: string;
};

type CandidateProfile = {
  candidate: {
    name: string;
    title: string;
    yearsExperience: number;
    email: string;
    summary: string;
  };
  skills: string[];
  achievements: string[];
};

type JobFormState = {
  title: string;
  company: string;
  location: string;
};

type RuleFormState = {
  name: string;
  targetRole: string;
  keywords: string;
  locations: string;
  resumeTemplateId: string;
  coverLetterTemplateId: string;
};

const candidateProfile: CandidateProfile = {
  candidate: {
    name: "Jordan Rivers",
    title: "Product Designer",
    yearsExperience: 8,
    email: "jordan.rivers@autohire.app",
    summary:
      "Product storyteller blending research, systems thinking, and prototyping to ship lovable multi-platform experiences.",
  },
  skills: [
    "Design systems leadership",
    "Mixed-method research",
    "Rapid prototyping",
    "Journey orchestration",
  ],
  achievements: [
    "Grew trial-to-paid conversion by 28% by redesigning onboarding flows with experimentation across 3 cohorts.",
    "Scaled a modular design system that accelerated shipping velocity across 6 cross-functional squads.",
    "Reduced support volume by 35% by launching proactive education and simplifying workflows.",
  ],
};

const resumeTemplates: ResumeTemplate[] = [
  {
    id: "product-story",
    name: "Product Story Narrative",
    description:
      "Balanced resume that highlights storytelling, research, and impact for product design roles.",
    sections: [
      {
        title: "Professional Summary",
        content:
          "{{candidate.name}} is a {{candidate.yearsExperience}}-year {{candidate.title}} who ships lovable experiences by pairing strategy with craft. Ready to support {{job.company}} as a {{job.title}} with a bias for experimentation and measurable outcomes.",
      },
      {
        title: "Core Strengths",
        content: "Key tools and rituals: {{skills}}.",
      },
      {
        title: "Recent Impact",
        content: "Signature wins:\n{{achievements}}",
      },
    ],
    variables: [
      "candidate.name",
      "candidate.title",
      "candidate.yearsExperience",
      "job.company",
      "job.title",
      "skills",
      "achievements",
    ],
    coverLetterTemplate:
      "Hello {{job.company}} team,\n\nI'm energized by the {{job.title}} opening and the opportunity to blend research, strategy, and craft to deliver measurable product wins. {{candidate.name}}",
  },
  {
    id: "growth-optimizer",
    name: "Growth Optimizer",
    description: "Data-forward resume tuned for experimentation and lifecycle marketing roles.",
    sections: [
      {
        title: "Mission Statement",
        content:
          "Growth leader with {{candidate.yearsExperience}} years refining the full funnel. Specialized in activation, retention, and monetization for SaaS and marketplace products.",
      },
      {
        title: "Experiments That Moved Metrics",
        content: "Highlights:\n{{achievements}}",
      },
      {
        title: "Toolkit",
        content: "Stacks mastered: {{skills}}.",
      },
    ],
    variables: ["candidate.yearsExperience", "achievements", "skills"],
    coverLetterTemplate:
      "Hi there,\n\nThe experimentation culture at {{job.company}} caught my eye. I'm eager to bring a hypothesis-driven mindset and a knack for cross-functional facilitation to the {{job.title}} role.",
  },
];

const initialRules: AutoApplyRule[] = [
  {
    id: "design-remote",
    name: "Remote Product Design Roles",
    targetRole: "Senior Product Designer",
    keywords: ["Figma", "design system", "user research"],
    locations: ["Remote", "United States"],
    resumeTemplateId: "product-story",
    coverLetterTemplateId: "product-story",
    status: "active",
  },
  {
    id: "growth-marketing",
    name: "Lifecycle & Growth Marketing",
    targetRole: "Lifecycle Marketing Manager",
    keywords: ["experiment", "activation", "retention"],
    locations: ["Hybrid", "San Francisco", "Remote"],
    resumeTemplateId: "growth-optimizer",
    coverLetterTemplateId: "growth-optimizer",
    status: "paused",
  },
];

const seededAutomationLogs: AutomationLog[] = [
  {
    id: "log-native-success",
    ruleId: "design-remote",
    jobId: "job-4231",
    jobTitle: "Senior Product Designer",
    company: "Canvas Labs",
    channel: "native",
    status: "submitted",
    submittedAt: "2024-05-01T17:22:00.000Z",
    auditTrail: [
      {
        name: "render_resume",
        status: "completed",
        timestamp: "2024-05-01T17:19:00.000Z",
        detail: "Rendered product-story template",
      },
      {
        name: "render_cover_letter",
        status: "completed",
        timestamp: "2024-05-01T17:20:30.000Z",
        detail: "Generated cover letter with personalization",
      },
      {
        name: "submit_native_application",
        status: "completed",
        timestamp: "2024-05-01T17:22:00.000Z",
        detail: "Submitted via ATS API",
      },
    ],
    notes: "Resume and cover letter uploaded. Awaiting recruiter review.",
  },
  {
    id: "log-playwright-failure",
    ruleId: "growth-marketing",
    jobId: "job-9654",
    jobTitle: "Lifecycle Marketing Manager",
    company: "Velocity Labs",
    channel: "playwright",
    status: "failed",
    submittedAt: "2024-05-02T19:12:00.000Z",
    auditTrail: [
      {
        name: "launch_browser",
        status: "completed",
        timestamp: "2024-05-02T19:07:00.000Z",
        detail: "Started Chromium via Playwright",
      },
      {
        name: "fill_application_form",
        status: "failed",
        timestamp: "2024-05-02T19:12:00.000Z",
        detail: "Captcha challenge blocked automation",
      },
    ],
    notes: "Manual follow-up recommended due to captcha interruption.",
  },
];

const PLACEHOLDER_PATTERN = /{{\s*([\w.]+)\s*}}/g;

function resolvePlaceholder(context: Record<string, unknown>, path: string): unknown {
  const segments = path.split(".");
  let current: unknown = context;
  for (const segment of segments) {
    if (typeof current !== "object" || current === null) {
      return undefined;
    }
    current = (current as Record<string, unknown>)[segment];
  }
  return current;
}

function formatValue(value: unknown): string {
  if (value === undefined || value === null) {
    return "";
  }
  if (Array.isArray(value)) {
    return value.map((item) => `• ${item}`).join("\n");
  }
  return String(value);
}

function renderText(template: string, context: Record<string, unknown>): string {
  return template.replace(PLACEHOLDER_PATTERN, (_, key) => formatValue(resolvePlaceholder(context, key)));
}

function formatDate(isoDate: string): string {
  const parsed = new Date(isoDate);
  if (Number.isNaN(parsed.getTime())) {
    return isoDate;
  }
  return parsed.toLocaleString();
}

function statusClass(base: string): string {
  return `status-pill status-pill--${base}`;
}

export default function AutomationWorkspacePage() {
  const [selectedTemplateId, setSelectedTemplateId] = useState(resumeTemplates[0]?.id ?? "");
  const [jobForm, setJobForm] = useState<JobFormState>({
    title: "Senior Product Designer",
    company: "Canvas Labs",
    location: "Remote - North America",
  });
  const [rules, setRules] = useState<AutoApplyRule[]>(initialRules);
  const [ruleForm, setRuleForm] = useState<RuleFormState>({
    name: "",
    targetRole: "",
    keywords: "",
    locations: "",
    resumeTemplateId: resumeTemplates[0]?.id ?? "",
    coverLetterTemplateId: resumeTemplates[0]?.id ?? "",
  });
  const [logs] = useState<AutomationLog[]>(seededAutomationLogs);
  const [logFilter, setLogFilter] = useState<string>("all");

  const activeTemplate = useMemo(
    () => resumeTemplates.find((template) => template.id === selectedTemplateId) ?? null,
    [selectedTemplateId],
  );

  const previewContext = useMemo(() => ({
    ...candidateProfile,
    job: { ...jobForm },
  }), [jobForm]);

  const resumePreview = useMemo(() => {
    if (!activeTemplate) {
      return [];
    }
    return activeTemplate.sections.map((section) => ({
      title: section.title,
      content: renderText(section.content, previewContext as Record<string, unknown>),
    }));
  }, [activeTemplate, previewContext]);

  const coverLetterPreview = useMemo(() => {
    if (!activeTemplate) {
      return "";
    }
    const body = activeTemplate.coverLetterTemplate ??
      "Hello {{job.company}} team,\n\nI'm excited about the opportunity to contribute to {{job.title}}.";
    return renderText(body, previewContext as Record<string, unknown>);
  }, [activeTemplate, previewContext]);

  const filteredLogs = useMemo(() => {
    if (logFilter === "all") {
      return logs;
    }
    return logs.filter((log) => log.ruleId === logFilter);
  }, [logFilter, logs]);

  const handleJobChange = (field: keyof JobFormState) => (event: ChangeEvent<HTMLInputElement>) => {
    const { value } = event.target;
    setJobForm((previous) => ({ ...previous, [field]: value }));
  };

  const handleRuleFieldChange = (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = event.target;
    setRuleForm((previous) => ({ ...previous, [name]: value }));
  };

  const handleCreateRule = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!ruleForm.name || !ruleForm.targetRole) {
      return;
    }

    const keywords = ruleForm.keywords
      .split(",")
      .map((keyword) => keyword.trim())
      .filter(Boolean);
    const locations = ruleForm.locations
      .split(",")
      .map((location) => location.trim())
      .filter(Boolean);

    setRules((previous) => [
      ...previous,
      {
        id: `draft-${Date.now()}`,
        name: ruleForm.name,
        targetRole: ruleForm.targetRole,
        keywords,
        locations,
        resumeTemplateId: ruleForm.resumeTemplateId,
        coverLetterTemplateId: ruleForm.coverLetterTemplateId,
        status: "active",
      },
    ]);

    setRuleForm((previous) => ({
      ...previous,
      name: "",
      targetRole: "",
      keywords: "",
      locations: "",
    }));
  };

  const handleToggleRule = (ruleId: string) => {
    setRules((previous) =>
      previous.map((rule) =>
        rule.id === ruleId ? { ...rule, status: rule.status === "active" ? "paused" : "active" } : rule,
      ),
    );
  };

  return (
    <main className="page">
      <header className="page__header">
        <h1>Automation Workspace</h1>
        <p>
          Configure tailored resume templates, rule-driven auto-apply workflows, and monitor automation performance from a
          single control surface.
        </p>
      </header>

      <section className="grid">
        <div className="panel">
          <h2>Target role context</h2>
          <p className="template-meta">
            Update the job details to instantly preview how personalized content adapts across templates.
          </p>
          <div className="field-group">
            <label htmlFor="job-title">Job title</label>
            <input id="job-title" value={jobForm.title} onChange={handleJobChange("title")} placeholder="Senior Product Designer" />
          </div>
          <div className="field-group">
            <label htmlFor="job-company">Company</label>
            <input id="job-company" value={jobForm.company} onChange={handleJobChange("company")} placeholder="Canvas Labs" />
          </div>
          <div className="field-group">
            <label htmlFor="job-location">Location</label>
            <input id="job-location" value={jobForm.location} onChange={handleJobChange("location")} placeholder="Remote" />
          </div>

          <div className="field-group">
            <label htmlFor="template-select">Resume template</label>
            <select
              id="template-select"
              value={selectedTemplateId}
              onChange={(event) => setSelectedTemplateId(event.target.value)}
            >
              {resumeTemplates.map((template) => (
                <option key={template.id} value={template.id}>
                  {template.name}
                </option>
              ))}
            </select>
          </div>
          {activeTemplate ? <p className="template-meta">{activeTemplate.description}</p> : null}
          {activeTemplate ? (
            <div className="resume-variables">
              {activeTemplate.variables.map((variable) => (
                <span key={variable} className="badge">
                  {variable}
                </span>
              ))}
            </div>
          ) : null}
        </div>

        <div className="panel">
          <h2>Preview</h2>
          {resumePreview.map((section) => (
            <div key={section.title} className="section-preview">
              <h3>{section.title}</h3>
              <p className="text-block">{section.content}</p>
            </div>
          ))}

          <div className="cover-letter-preview">
            <h3>Cover letter draft</h3>
            <p className="text-block">{coverLetterPreview}</p>
          </div>
        </div>
      </section>

      <section className="panel">
        <h2>Auto-apply rules</h2>
        <p className="template-meta">
          Prioritize which combinations of keywords, locations, and templates should trigger automated submissions.
        </p>
        <form onSubmit={handleCreateRule}>
          <div className="field-group">
            <label htmlFor="rule-name">Rule name</label>
            <input
              id="rule-name"
              name="name"
              value={ruleForm.name}
              onChange={handleRuleFieldChange}
              placeholder="North America design leadership"
            />
          </div>
          <div className="field-group">
            <label htmlFor="rule-role">Target role</label>
            <input
              id="rule-role"
              name="targetRole"
              value={ruleForm.targetRole}
              onChange={handleRuleFieldChange}
              placeholder="Principal Product Designer"
            />
          </div>
          <div className="field-group">
            <label htmlFor="rule-keywords">Must have keywords</label>
            <input
              id="rule-keywords"
              name="keywords"
              value={ruleForm.keywords}
              onChange={handleRuleFieldChange}
              placeholder="design system, experimentation"
            />
          </div>
          <div className="field-group">
            <label htmlFor="rule-locations">Preferred locations</label>
            <input
              id="rule-locations"
              name="locations"
              value={ruleForm.locations}
              onChange={handleRuleFieldChange}
              placeholder="Remote, Portland"
            />
          </div>
          <div className="field-group">
            <label htmlFor="rule-resume-template">Resume template</label>
            <select
              id="rule-resume-template"
              name="resumeTemplateId"
              value={ruleForm.resumeTemplateId}
              onChange={handleRuleFieldChange}
            >
              {resumeTemplates.map((template) => (
                <option key={template.id} value={template.id}>
                  {template.name}
                </option>
              ))}
            </select>
          </div>
          <div className="field-group">
            <label htmlFor="rule-cover-template">Cover letter template</label>
            <select
              id="rule-cover-template"
              name="coverLetterTemplateId"
              value={ruleForm.coverLetterTemplateId}
              onChange={handleRuleFieldChange}
            >
              {resumeTemplates.map((template) => (
                <option key={template.id} value={template.id}>
                  {template.name}
                </option>
              ))}
            </select>
          </div>
          <div className="form-actions">
            <button type="submit" className="button button--primary">
              Save rule
            </button>
          </div>
        </form>

        <div>
          {rules.map((rule) => (
            <div key={rule.id} className="rule-card">
              <div className="rule-card__header">
                <div>
                  <h3>{rule.name}</h3>
                  <p className="rule-card__meta">Optimizes for {rule.targetRole}</p>
                </div>
                <div className={statusClass(rule.status)}>{rule.status}</div>
              </div>
              <div className="rule-card__meta">
                <span>Keywords:</span>
                <div className="rule-card__chips">
                  {rule.keywords.map((keyword) => (
                    <span key={keyword} className="tag">
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
              <div className="rule-card__meta">
                <span>Locations:</span>
                <div className="rule-card__chips">
                  {rule.locations.map((location) => (
                    <span key={location} className="tag">
                      {location}
                    </span>
                  ))}
                </div>
              </div>
              <div className="rule-card__meta">
                <span>Resume:</span> {rule.resumeTemplateId || "Manual selection"}
              </div>
              <div className="rule-card__meta">
                <span>Cover letter:</span> {rule.coverLetterTemplateId || "Manual selection"}
              </div>
              <div className="form-actions">
                <button type="button" className="button button--ghost" onClick={() => handleToggleRule(rule.id)}>
                  {rule.status === "active" ? "Pause" : "Activate"}
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="panel">
        <h2>Automation activity</h2>
        <p className="template-meta">
          Inspect each submission attempt across native integrations and Playwright-powered browser runs.
        </p>
        <label htmlFor="log-filter">Filter by rule</label>
        <select
          id="log-filter"
          className="rule-filter"
          value={logFilter}
          onChange={(event) => setLogFilter(event.target.value)}
        >
          <option value="all">All runs</option>
          {rules.map((rule) => (
            <option key={rule.id} value={rule.id}>
              {rule.name}
            </option>
          ))}
        </select>

        <div className="logs-grid">
          {filteredLogs.map((log) => (
            <article key={log.id} className="log-card">
              <div className="log-card__header">
                <div>
                  <h3>
                    {log.jobTitle} &middot; {log.company}
                  </h3>
                  <p className="template-meta">Job ID: {log.jobId}</p>
                </div>
                <div>
                  <div className={statusClass(log.status)}>{log.status}</div>
                  <div className="badge" style={{ marginTop: "0.5rem" }}>
                    {log.channel}
                  </div>
                </div>
              </div>
              <p className="template-meta">Submitted {formatDate(log.submittedAt)}</p>
              {log.notes ? <p className="text-block">{log.notes}</p> : null}
              <ul className="audit-steps">
                {log.auditTrail.map((step) => (
                  <li key={`${log.id}-${step.name}`}>
                    <strong>{step.name}</strong>
                    <span>{step.status}</span>
                    {step.detail ? <span> &mdash; {step.detail}</span> : null}
                    <div>{formatDate(step.timestamp)}</div>
                  </li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
