from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Dict, Iterable, Sequence
from uuid import UUID, uuid4


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class JobProvenance:
    run_id: str
    adapter: str
    scraped_at: datetime
    ingested_at: datetime = field(default_factory=utcnow)
    raw_url: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "adapter": self.adapter,
            "scraped_at": self.scraped_at.isoformat(),
            "ingested_at": self.ingested_at.isoformat(),
            "raw_url": self.raw_url,
        }


@dataclass
class JobRecord:
    id: UUID
    external_id: str
    title: str
    company: str
    description: str
    source_url: str
    location: str | None
    remote: bool | None
    employment_type: str | None
    salary_min: int | None
    salary_max: int | None
    currency: str | None
    posted_at: datetime | None
    scraped_at: datetime
    source: str
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)
    provenance: list[JobProvenance] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "external_id": self.external_id,
            "title": self.title,
            "company": self.company,
            "description": self.description,
            "source_url": self.source_url,
            "location": self.location,
            "remote": self.remote,
            "employment_type": self.employment_type,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "currency": self.currency,
            "posted_at": self.posted_at.isoformat() if self.posted_at else None,
            "scraped_at": self.scraped_at.isoformat(),
            "source": self.source,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "provenance": [prov.to_dict() for prov in self.provenance],
        }


@dataclass
class ScrapeRun:
    id: str
    adapter: str
    received: int
    created: int
    updated: int
    ignored: int
    started_at: datetime
    completed_at: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "adapter": self.adapter,
            "received": self.received,
            "created": self.created,
            "updated": self.updated,
            "ignored": self.ignored,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat(),
        }


@dataclass
class ScrapeSchedule:
    adapter: str
    interval_minutes: int
    enabled: bool = True
    last_run_at: datetime | None = None
    last_run_id: str | None = None
    last_result: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "adapter": self.adapter,
            "interval_minutes": self.interval_minutes,
            "enabled": self.enabled,
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
            "last_run_id": self.last_run_id,
            "last_result": self.last_result,
            "metadata": self.metadata,
        }


class JobStore:
    def __init__(self) -> None:
        self._jobs: Dict[UUID, JobRecord] = {}
        self._jobs_by_external: Dict[str, JobRecord] = {}
        self._runs: Dict[str, ScrapeRun] = {}
        self._lock = RLock()

    def list_jobs(self) -> list[JobRecord]:
        with self._lock:
            return list(self._jobs.values())

    def get_job(self, job_id: str) -> JobRecord | None:
        try:
            uid = UUID(job_id)
        except ValueError:
            return None
        with self._lock:
            return self._jobs.get(uid)

    def bulk_ingest(self, adapter: str, run_id: str, jobs: Sequence[dict[str, Any]]) -> ScrapeRun:
        received = len(jobs)
        created = 0
        updated = 0
        ignored = 0
        earliest_scraped_at: datetime | None = None
        fingerprints_seen: set[str] = set()

        with self._lock:
            for payload in jobs:
                fingerprint = payload["external_id"]
                if fingerprint in fingerprints_seen:
                    ignored += 1
                    continue
                fingerprints_seen.add(fingerprint)

                provenance = JobProvenance(
                    run_id=run_id,
                    adapter=adapter,
                    scraped_at=payload.get("scraped_at", utcnow()),
                    raw_url=payload.get("source_url"),
                )
                record, was_created = self._upsert(adapter, payload, provenance)
                if was_created:
                    created += 1
                else:
                    updated += 1
                if earliest_scraped_at is None or provenance.scraped_at < earliest_scraped_at:
                    earliest_scraped_at = provenance.scraped_at

            run = ScrapeRun(
                id=run_id,
                adapter=adapter,
                received=received,
                created=created,
                updated=updated,
                ignored=ignored,
                started_at=earliest_scraped_at or utcnow(),
                completed_at=utcnow(),
            )
            self._runs[run_id] = run
            return run

    def _upsert(self, adapter: str, payload: dict[str, Any], provenance: JobProvenance) -> tuple[JobRecord, bool]:
        fingerprint = payload["external_id"]
        record = self._jobs_by_external.get(fingerprint)
        if record is None:
            record = self._create_record(adapter, payload)
            self._jobs[record.id] = record
            self._jobs_by_external[fingerprint] = record
            created = True
        else:
            self._update_record(record, payload)
            created = False
        record.provenance.append(provenance)
        return record, created

    def _create_record(self, adapter: str, payload: dict[str, Any]) -> JobRecord:
        return JobRecord(
            id=uuid4(),
            external_id=payload["external_id"],
            title=payload["title"],
            company=payload["company"],
            description=payload["description"],
            source_url=payload["source_url"],
            location=payload.get("location"),
            remote=payload.get("remote"),
            employment_type=payload.get("employment_type"),
            salary_min=payload.get("salary_min"),
            salary_max=payload.get("salary_max"),
            currency=payload.get("currency"),
            posted_at=payload.get("posted_at"),
            scraped_at=payload.get("scraped_at", utcnow()),
            source=payload.get("source", adapter),
            metadata=dict(payload.get("metadata") or {}),
        )

    def _update_record(self, record: JobRecord, payload: dict[str, Any]) -> None:
        record.title = payload["title"]
        record.company = payload["company"]
        record.description = payload["description"]
        record.source_url = payload["source_url"]
        record.location = payload.get("location")
        record.remote = payload.get("remote")
        record.employment_type = payload.get("employment_type")
        record.salary_min = payload.get("salary_min")
        record.salary_max = payload.get("salary_max")
        record.currency = payload.get("currency")
        record.posted_at = payload.get("posted_at")
        record.scraped_at = payload.get("scraped_at", record.scraped_at)
        record.source = payload.get("source", record.source)
        record.metadata.update(payload.get("metadata") or {})
        record.updated_at = utcnow()

    def list_runs(self) -> list[ScrapeRun]:
        with self._lock:
            return list(self._runs.values())

    def clear(self) -> None:
        with self._lock:
            self._jobs.clear()
            self._jobs_by_external.clear()
            self._runs.clear()


class ScrapeScheduleStore:
    def __init__(self, default_interval_minutes: int = 60) -> None:
        self._entries: Dict[str, ScrapeSchedule] = {}
        self._lock = RLock()
        self._default_interval_minutes = default_interval_minutes

    def list(self) -> list[ScrapeSchedule]:
        with self._lock:
            return list(self._entries.values())

    def get(self, adapter: str) -> ScrapeSchedule | None:
        with self._lock:
            return self._entries.get(adapter)

    def upsert_many(self, entries: Iterable[ScrapeSchedule]) -> list[ScrapeSchedule]:
        with self._lock:
            for entry in entries:
                existing = self._entries.get(entry.adapter)
                if existing:
                    entry.last_run_at = existing.last_run_at
                    entry.last_run_id = existing.last_run_id
                    entry.last_result = existing.last_result
                self._entries[entry.adapter] = entry
            return list(self._entries.values())

    def mark_run(self, run: ScrapeRun) -> ScrapeSchedule:
        with self._lock:
            entry = self._entries.get(run.adapter)
            if entry is None:
                entry = ScrapeSchedule(adapter=run.adapter, interval_minutes=self._default_interval_minutes)
                self._entries[run.adapter] = entry
            entry.last_run_at = run.completed_at
            entry.last_run_id = run.id
            entry.last_result = {
                "received": run.received,
                "created": run.created,
                "updated": run.updated,
                "ignored": run.ignored,
            }
            return entry

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()


job_store = JobStore()
schedule_store = ScrapeScheduleStore()


def get_job_store() -> JobStore:
    return job_store


def get_schedule_store() -> ScrapeScheduleStore:
    return schedule_store

