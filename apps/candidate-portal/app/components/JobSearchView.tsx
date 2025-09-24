"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import dynamic from "next/dynamic";
import { FacetBucket, JobSearchFilters, SearchResponse } from "../types";

const JobMap = dynamic(() => import("./JobMap").then((mod) => mod.JobMap), {
  ssr: false,
});

const employmentTypeOptions = ["Full-time", "Part-time", "Contract", "Temporary", "Internship"];

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

const defaultFilters: JobSearchFilters = {
  query: "",
  employmentTypes: [],
  remote: "any",
  minCompensation: "",
  maxCompensation: "",
  latitude: "",
  longitude: "",
  radius: "",
};

export function JobSearchView() {
  const [filters, setFilters] = useState<JobSearchFilters>(defaultFilters);
  const [response, setResponse] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchJobs = useCallback(async () => {
    setLoading(true);
    setError(null);

    const params = new URLSearchParams();
    if (filters.query) params.set("query", filters.query);
    filters.employmentTypes.forEach((type) => params.append("employmentTypes", type));
    if (filters.remote === "remote") params.set("remote", "true");
    if (filters.remote === "on-site") params.set("remote", "false");
    if (filters.minCompensation) params.set("min_compensation", filters.minCompensation);
    if (filters.maxCompensation) params.set("max_compensation", filters.maxCompensation);
    if (filters.latitude) params.set("latitude", filters.latitude);
    if (filters.longitude) params.set("longitude", filters.longitude);
    if (filters.radius) params.set("radius_km", filters.radius);
    params.set("limit", "50");

    try {
      const res = await fetch(`${API_BASE}/jobs/search?${params.toString()}`);
      if (!res.ok) {
        throw new Error(`Search failed with status ${res.status}`);
      }
      const data: SearchResponse = await res.json();
      setResponse(data);
    } catch (err) {
      console.error(err);
      setError("Unable to load jobs. Please try again shortly.");
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  const hasResults = response && response.hits.length > 0;

  const center: [number, number] = useMemo(() => {
    if (!response) return [37.7749, -122.4194];
    const firstWithLocation = response.hits.find(
      (hit) => hit.location?.latitude && hit.location?.longitude
    );
    if (!firstWithLocation || !firstWithLocation.location?.latitude) {
      return [37.7749, -122.4194];
    }
    return [firstWithLocation.location.latitude!, firstWithLocation.location.longitude ?? -122.4194];
  }, [response]);

  const activeFacets = useMemo(() => response?.facets ?? {}, [response]);

  const toggleEmploymentType = (type: string) => {
    setFilters((current) => {
      const exists = current.employmentTypes.includes(type);
      const employmentTypes = exists
        ? current.employmentTypes.filter((value) => value !== type)
        : [...current.employmentTypes, type];
      return { ...current, employmentTypes };
    });
  };

  const updateFilter = (key: keyof JobSearchFilters, value: string) => {
    setFilters((current) => ({ ...current, [key]: value }));
  };

  const resetFilters = () => {
    setFilters(defaultFilters);
  };

  const renderFacet = (name: string, buckets: FacetBucket[]) => (
    <div key={name} className="facet-group">
      <h4>{name.replace(/_/g, " ")}</h4>
      <ul>
        {buckets.map((bucket) => (
          <li key={bucket.name}>
            <span>{bucket.name}</span>
            <span>{bucket.count}</span>
          </li>
        ))}
      </ul>
    </div>
  );

  return (
    <div className="job-search-shell">
      <header className="search-header">
        <div>
          <h1>Discover roles tailored to your skills</h1>
          <p>Use hybrid search to explore the freshest job opportunities on AutoHire.</p>
        </div>
      </header>
      <section className="search-controls">
        <div className="filter-row">
          <label htmlFor="query">Keywords</label>
          <input
            id="query"
            type="text"
            value={filters.query}
            onChange={(event) => updateFilter("query", event.target.value)}
            placeholder="Search job titles, companies, or skills"
          />
        </div>
        <div className="filter-grid">
          <div className="filter-column">
            <span className="filter-label">Employment Type</span>
            <div className="checkbox-grid">
              {employmentTypeOptions.map((type) => (
                <label key={type}>
                  <input
                    type="checkbox"
                    checked={filters.employmentTypes.includes(type)}
                    onChange={() => toggleEmploymentType(type)}
                  />
                  <span>{type}</span>
                </label>
              ))}
            </div>
          </div>
          <div className="filter-column">
            <label htmlFor="remote">Work Arrangement</label>
            <select
              id="remote"
              value={filters.remote}
              onChange={(event) => updateFilter("remote", event.target.value as JobSearchFilters["remote"])}
            >
              <option value="any">Any</option>
              <option value="remote">Remote only</option>
              <option value="on-site">On-site</option>
            </select>
            <div className="input-pair">
              <div>
                <label htmlFor="min-comp">Min Compensation</label>
                <input
                  id="min-comp"
                  type="number"
                  min={0}
                  step={1000}
                  value={filters.minCompensation}
                  onChange={(event) => updateFilter("minCompensation", event.target.value)}
                />
              </div>
              <div>
                <label htmlFor="max-comp">Max Compensation</label>
                <input
                  id="max-comp"
                  type="number"
                  min={0}
                  step={1000}
                  value={filters.maxCompensation}
                  onChange={(event) => updateFilter("maxCompensation", event.target.value)}
                />
              </div>
            </div>
          </div>
          <div className="filter-column">
            <span className="filter-label">Geo radius (optional)</span>
            <div className="input-pair">
              <div>
                <label htmlFor="latitude">Latitude</label>
                <input
                  id="latitude"
                  type="number"
                  value={filters.latitude}
                  onChange={(event) => updateFilter("latitude", event.target.value)}
                />
              </div>
              <div>
                <label htmlFor="longitude">Longitude</label>
                <input
                  id="longitude"
                  type="number"
                  value={filters.longitude}
                  onChange={(event) => updateFilter("longitude", event.target.value)}
                />
              </div>
            </div>
            <label htmlFor="radius">Radius (km)</label>
            <input
              id="radius"
              type="number"
              min={0}
              value={filters.radius}
              onChange={(event) => updateFilter("radius", event.target.value)}
            />
          </div>
        </div>
        <div className="control-actions">
          <button type="button" onClick={fetchJobs} disabled={loading}>
            {loading ? "Searching…" : "Search"}
          </button>
          <button type="button" onClick={resetFilters} className="secondary">
            Reset
          </button>
        </div>
      </section>
      <section className="search-results">
        <div className="list-column">
          {loading && <p className="status">Loading roles…</p>}
          {error && <p className="status error">{error}</p>}
          {!loading && !error && hasResults && response && (
            <ul className="job-list">
              {response.hits.map((hit) => (
                <li key={hit.id}>
                  <article>
                    <header>
                      <h3>{hit.title}</h3>
                      {hit.metadata?.company && <span className="company">{hit.metadata.company}</span>}
                    </header>
                    {hit.location?.city && (
                      <p className="location">
                        {hit.location.city}
                        {hit.location.region ? `, ${hit.location.region}` : ""}
                      </p>
                    )}
                    {hit.description && <p className="summary">{hit.description.slice(0, 160)}…</p>}
                    <footer>
                      <span className="score">Score: {hit.score.toFixed(2)}</span>
                      {hit.distance_km != null && (
                        <span className="distance">{hit.distance_km.toFixed(1)} km away</span>
                      )}
                    </footer>
                  </article>
                </li>
              ))}
            </ul>
          )}
          {!loading && !error && (!response || !response.hits.length) && (
            <div className="empty-state">
              <h3>No matches yet</h3>
              <p>Try adjusting your filters to discover more opportunities.</p>
            </div>
          )}
        </div>
        <aside className="map-column">
          {hasResults && response ? (
            <JobMap jobs={response.hits} center={center} zoom={response.hits.length ? 4 : 2} />
          ) : (
            <div className="map-placeholder">Run a search to see openings on the map.</div>
          )}
          {Object.keys(activeFacets).length > 0 && (
            <div className="facet-panel">
              <h3>Facets</h3>
              <div className="facet-list">
                {Object.entries(activeFacets).map(([name, buckets]) => renderFacet(name, buckets))}
              </div>
            </div>
          )}
        </aside>
      </section>
    </div>
  );
}
