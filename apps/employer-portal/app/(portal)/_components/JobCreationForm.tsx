"use client";

import { useState } from "react";

import { createJob } from "@/lib/api";
import type { JobCreateRequest, Team } from "@/lib/types";

type JobCreationFormProps = {
  employerId: string;
  teams: Team[];
};

const baseState = {
  title: "",
  team_id: "",
  location: "",
  openings: 1,
  description: "",
};

type FormStatus = "idle" | "submitting" | "success" | "error";

export default function JobCreationForm({ employerId, teams }: JobCreationFormProps) {
  const [formState, setFormState] = useState(() => ({
    ...baseState,
    team_id: teams[0]?.id ?? "",
  }));
  const [status, setStatus] = useState<FormStatus>("idle");
  const [message, setMessage] = useState<string | null>(null);

  const handleChange = (event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = event.target;
    setFormState((prev) => ({
      ...prev,
      [name]: name === "openings" ? Number(value) : value,
    }));
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const payload: JobCreateRequest = {
      title: formState.title.trim(),
      team_id: formState.team_id || teams[0]?.id || "",
      location: formState.location.trim(),
      openings: formState.openings || 1,
      description: formState.description.trim() || undefined,
    };

    if (!payload.title || !payload.team_id || !payload.location) {
      setMessage("Please provide a title, location, and select a team.");
      setStatus("error");
      return;
    }

    try {
      setStatus("submitting");
      await createJob(employerId, payload);
      setStatus("success");
      setMessage("Job created successfully. A default pipeline has been provisioned.");
      setFormState({
        ...baseState,
        team_id: teams[0]?.id ?? "",
      });
    } catch (error) {
      setStatus("error");
      const detail = error instanceof Error ? error.message : "Unable to create job.";
      setMessage(detail);
    }
  };

  const disabled = status === "submitting";

  return (
    <form className="card form" onSubmit={handleSubmit}>
      <div className="form-row">
        <label htmlFor="title">Job title</label>
        <input
          id="title"
          name="title"
          value={formState.title}
          onChange={handleChange}
          placeholder="Robotics Software Engineer"
          required
        />
      </div>
      <div className="form-row">
        <label htmlFor="team_id">Hiring team</label>
        <select id="team_id" name="team_id" value={formState.team_id} onChange={handleChange} required>
          <option value="" disabled>
            Select a team
          </option>
          {teams.map((team) => (
            <option key={team.id} value={team.id}>
              {team.name}
            </option>
          ))}
        </select>
      </div>
      <div className="form-row three-col">
        <div>
          <label htmlFor="location">Location</label>
          <input
            id="location"
            name="location"
            value={formState.location}
            onChange={handleChange}
            placeholder="Seattle, WA (Hybrid)"
            required
          />
        </div>
        <div>
          <label htmlFor="openings">Openings</label>
          <input
            id="openings"
            name="openings"
            type="number"
            min={1}
            value={formState.openings}
            onChange={handleChange}
            required
          />
        </div>
      </div>
      <div className="form-row">
        <label htmlFor="description">Summary</label>
        <textarea
          id="description"
          name="description"
          value={formState.description}
          onChange={handleChange}
          rows={4}
          placeholder="Highlight the role mission, core skills, and key deliverables."
        />
      </div>
      <button type="submit" disabled={disabled} className="primary">
        {disabled ? "Creating job..." : "Create job"}
      </button>
      {message ? (
        <p className={`form-message ${status}`}>{message}</p>
      ) : null}
    </form>
  );
}
