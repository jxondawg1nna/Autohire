export interface JobLocation {
  city?: string | null;
  region?: string | null;
  country?: string | null;
  latitude?: number | null;
  longitude?: number | null;
}

export interface JobMetadata {
  company?: string;
  compensation_min?: number;
  compensation_max?: number;
  employment_types?: string[];
  remote?: boolean;
  [key: string]: unknown;
}

export interface JobHit {
  id: string;
  external_id: string;
  title: string;
  description?: string | null;
  location?: JobLocation | null;
  metadata?: JobMetadata | null;
  score: number;
  highlights?: Record<string, unknown> | null;
  distance_km?: number | null;
  indexed_at?: string | null;
}

export interface FacetBucket {
  name: string;
  count: number;
}

export interface SearchResponse {
  query: string;
  total: number;
  hits: JobHit[];
  facets: Record<string, FacetBucket[]>;
}

export interface JobSearchFilters {
  query: string;
  employmentTypes: string[];
  remote: "any" | "remote" | "on-site";
  minCompensation?: string;
  maxCompensation?: string;
  latitude?: string;
  longitude?: string;
  radius?: string;
}
