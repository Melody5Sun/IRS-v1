from datetime import datetime
import json
from pathlib import Path

from app.db.sqlite import connect, initialize_database
from app.ingestion.source_registry import JobSource
from app.schemas.job import (
    CompanyDiscoveryStatus,
    JobDiscoveryPreview,
    JobPosting,
    JobRequirementDocument,
)


class JobRepository:
    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path
        initialize_database(db_path)

    def upsert_many(self, jobs: list[JobPosting]) -> int:
        changed_count = 0
        with connect(self.db_path) as connection:
            for job in jobs:
                existing = connection.execute(
                    "SELECT content_hash FROM jobs WHERE source = ? AND external_id = ?",
                    (job.source, job.external_id),
                ).fetchone()
                if existing is None or existing["content_hash"] != job.content_hash:
                    changed_count += 1

                connection.execute(
                    """
                    INSERT INTO jobs (
                        source, company, external_id, title, location, description, url,
                        employment_type, collected_at, last_seen_at,
                        content_hash, status, raw_json
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(source, external_id) DO UPDATE SET
                        company = excluded.company,
                        title = excluded.title,
                        location = excluded.location,
                        description = excluded.description,
                        url = excluded.url,
                        employment_type = excluded.employment_type,
                        last_seen_at = excluded.last_seen_at,
                        content_hash = excluded.content_hash,
                        status = CASE
                            WHEN jobs.status = 'inactive'
                                 AND jobs.content_hash = excluded.content_hash
                            THEN jobs.status
                            ELSE excluded.status
                        END,
                        raw_json = excluded.raw_json
                    """,
                    (
                        job.source,
                        job.company,
                        job.external_id,
                        job.title,
                        job.location,
                        job.description,
                        job.url,
                        job.employment_type,
                        job.collected_at.isoformat(),
                        job.last_seen_at.isoformat(),
                        job.content_hash,
                        job.status,
                        json.dumps(job.raw_json, ensure_ascii=False),
                    ),
                )
        return changed_count

    def list_jobs(
        self,
        status: str = "active",
        company: str | None = None,
        limit: int = 100,
    ) -> list[JobPosting]:
        query = "SELECT * FROM jobs WHERE status = ?"
        params: list[str | int] = [status]
        if company:
            query += " AND company = ?"
            params.append(company)
        query += " ORDER BY collected_at DESC LIMIT ?"
        params.append(limit)

        with connect(self.db_path) as connection:
            rows = connection.execute(query, params).fetchall()
        return [self._row_to_job(row) for row in rows]

    def get_job(self, job_id: int) -> JobPosting | None:
        with connect(self.db_path) as connection:
            row = connection.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return self._row_to_job(row) if row else None

    def save_job_analysis(self, document: JobRequirementDocument) -> None:
        if document.job_id is None:
            raise ValueError("job_id is required before saving job analysis.")

        with connect(self.db_path) as connection:
            connection.execute(
                """
                INSERT INTO job_analysis (
                    job_id, summary, responsibilities_json, required_skills_json,
                    preferred_skills_json, employment_type,
                    candidate_type, seniority_level, remote_policy,
                    visa_sponsorship, work_authorization_notes, degree_required,
                    major_required_json, keywords_json,
                    source_evidence_json, analysis_version, analysis_method,
                    analyzed_at, analysis_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(job_id) DO UPDATE SET
                    summary = excluded.summary,
                    responsibilities_json = excluded.responsibilities_json,
                    required_skills_json = excluded.required_skills_json,
                    preferred_skills_json = excluded.preferred_skills_json,
                    employment_type = excluded.employment_type,
                    candidate_type = excluded.candidate_type,
                    seniority_level = excluded.seniority_level,
                    remote_policy = excluded.remote_policy,
                    visa_sponsorship = excluded.visa_sponsorship,
                    work_authorization_notes = excluded.work_authorization_notes,
                    degree_required = excluded.degree_required,
                    major_required_json = excluded.major_required_json,
                    keywords_json = excluded.keywords_json,
                    source_evidence_json = excluded.source_evidence_json,
                    analysis_version = excluded.analysis_version,
                    analysis_method = excluded.analysis_method,
                    analyzed_at = excluded.analyzed_at,
                    analysis_json = excluded.analysis_json
                """,
                (
                    document.job_id,
                    document.summary,
                    json.dumps(document.responsibilities, ensure_ascii=False),
                    json.dumps(document.required_skills, ensure_ascii=False),
                    json.dumps(document.preferred_skills, ensure_ascii=False),
                    document.employment_type,
                    document.candidate_type,
                    document.seniority_level,
                    document.remote_policy,
                    document.visa_sponsorship,
                    document.work_authorization_notes,
                    document.degree_required,
                    json.dumps(document.major_required, ensure_ascii=False),
                    json.dumps(document.keywords, ensure_ascii=False),
                    json.dumps(document.source_evidence, ensure_ascii=False),
                    document.analysis_version,
                    document.analysis_method,
                    document.analyzed_at.isoformat() if document.analyzed_at else None,
                    document.model_dump_json(),
                ),
            )

    def count_job_analysis(self) -> int:
        with connect(self.db_path) as connection:
            row = connection.execute("SELECT COUNT(*) AS count FROM job_analysis").fetchone()
        return int(row["count"])

    def mark_job_inactive(self, job_id: int, reason: str | None = None) -> None:
        with connect(self.db_path) as connection:
            row = connection.execute("SELECT raw_json FROM jobs WHERE id = ?", (job_id,)).fetchone()
            raw_json = {}
            if row is not None:
                raw_json = json.loads(row["raw_json"])
            raw_json["inactive_reason"] = reason or "No required or preferred skills were extracted."
            connection.execute(
                """
                UPDATE jobs
                SET status = 'inactive',
                    raw_json = ?
                WHERE id = ?
                """,
                (json.dumps(raw_json, ensure_ascii=False), job_id),
            )
            connection.execute("DELETE FROM job_analysis WHERE job_id = ?", (job_id,))

    def ensure_company_sources(self, sources: list[JobSource]) -> None:
        now = datetime.now().astimezone().isoformat()
        with connect(self.db_path) as connection:
            for source in sources:
                connection.execute(
                    """
                    INSERT INTO company_sources (
                        name, company, provider, identifier, enabled, priority, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(name) DO UPDATE SET
                        company = excluded.company,
                        provider = excluded.provider,
                        identifier = excluded.identifier,
                        enabled = excluded.enabled,
                        priority = excluded.priority,
                        updated_at = excluded.updated_at
                    """,
                    (
                        source.name,
                        source.company,
                        source.provider,
                        source.identifier,
                        1 if source.enabled else 0,
                        source.priority,
                        now,
                    ),
                )

    def list_company_sources(self, enabled_only: bool = False) -> list[JobSource]:
        query = "SELECT * FROM company_sources"
        params: list[int] = []
        if enabled_only:
            query += " WHERE enabled = ?"
            params.append(1)
        query += " ORDER BY priority ASC, company ASC, name ASC"
        with connect(self.db_path) as connection:
            rows = connection.execute(query, params).fetchall()
        return [
            JobSource(
                name=row["name"],
                company=row["company"],
                provider=row["provider"],
                identifier=row["identifier"],
                enabled=bool(row["enabled"]),
                priority=row["priority"],
            )
            for row in rows
        ]

    def update_company_source_run_status(
        self,
        source_name: str,
        status: str,
        message: str | None = None,
    ) -> None:
        with connect(self.db_path) as connection:
            connection.execute(
                """
                UPDATE company_sources
                SET last_checked_at = ?,
                    last_status = ?,
                    last_message = ?
                WHERE name = ?
                """,
                (
                    datetime.now().astimezone().isoformat(),
                    status,
                    message,
                    source_name,
                ),
            )

    def upsert_discovery_previews(self, previews: list[JobDiscoveryPreview]) -> int:
        changed_count = 0
        with connect(self.db_path) as connection:
            for preview in previews:
                existing = connection.execute(
                    """
                    SELECT raw_json
                    FROM job_discovery_preview
                    WHERE discovery_source = ? AND external_id = ?
                    """,
                    (preview.discovery_source, preview.external_id),
                ).fetchone()
                raw_json = json.dumps(preview.raw_json, ensure_ascii=False)
                if existing is None or existing["raw_json"] != raw_json:
                    changed_count += 1

                connection.execute(
                    """
                    INSERT INTO job_discovery_preview (
                        discovery_source, external_id, company, title, location, snippet,
                        source_url, final_url, ats_type, jd_quality, status, collected_at,
                        raw_json
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(discovery_source, external_id) DO UPDATE SET
                        company = excluded.company,
                        title = excluded.title,
                        location = excluded.location,
                        snippet = excluded.snippet,
                        source_url = excluded.source_url,
                        final_url = excluded.final_url,
                        ats_type = excluded.ats_type,
                        jd_quality = excluded.jd_quality,
                        status = excluded.status,
                        collected_at = excluded.collected_at,
                        raw_json = excluded.raw_json
                    """,
                    (
                        preview.discovery_source,
                        preview.external_id,
                        preview.company,
                        preview.title,
                        preview.location,
                        preview.snippet,
                        preview.source_url,
                        preview.final_url,
                        preview.ats_type,
                        preview.jd_quality,
                        preview.status,
                        preview.collected_at.isoformat(),
                        raw_json,
                    ),
                )
        return changed_count

    def list_discovery_previews(
        self,
        status: str = "preview",
        limit: int = 100,
    ) -> list[JobDiscoveryPreview]:
        with connect(self.db_path) as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM job_discovery_preview
                WHERE status = ?
                ORDER BY collected_at DESC
                LIMIT ?
                """,
                (status, limit),
            ).fetchall()
        return [self._row_to_discovery_preview(row) for row in rows]

    def clear_all_job_data(self) -> None:
        with connect(self.db_path) as connection:
            connection.execute("DELETE FROM job_match_features")
            connection.execute("DELETE FROM job_analysis")
            connection.execute("DELETE FROM jobs")
            connection.execute("DELETE FROM job_discovery_preview")
            connection.execute("DELETE FROM company_discovery_status")
            connection.execute(
                """
                DELETE FROM sqlite_sequence
                WHERE name IN ('jobs', 'job_discovery_preview', 'company_discovery_status')
                """
            )

    def get_company_discovery_status(
        self,
        normalized_company: str,
        provider: str,
    ):
        with connect(self.db_path) as connection:
            return connection.execute(
                """
                SELECT *
                FROM company_discovery_status
                WHERE normalized_company = ? AND provider = ?
                """,
                (normalized_company, provider),
            ).fetchone()

    def save_company_discovery_status(
        self,
        company: str,
        normalized_company: str,
        provider: str,
        status: str,
        provider_identifier: str | None = None,
        jobs_found_count: int = 0,
        message: str | None = None,
    ) -> None:
        with connect(self.db_path) as connection:
            connection.execute(
                """
                INSERT INTO company_discovery_status (
                    company, normalized_company, provider, provider_identifier,
                    status, jobs_found_count, message, checked_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(normalized_company, provider) DO UPDATE SET
                    company = excluded.company,
                    provider_identifier = excluded.provider_identifier,
                    status = excluded.status,
                    jobs_found_count = excluded.jobs_found_count,
                    message = excluded.message,
                    checked_at = excluded.checked_at
                """,
                (
                    company,
                    normalized_company,
                    provider,
                    provider_identifier,
                    status,
                    jobs_found_count,
                    message,
                    datetime.now().astimezone().isoformat(),
                ),
            )

    def list_company_discovery_statuses(
        self,
        provider: str | None = None,
        limit: int = 100,
    ) -> list[CompanyDiscoveryStatus]:
        query = "SELECT * FROM company_discovery_status"
        params: list[str | int] = []
        if provider:
            query += " WHERE provider = ?"
            params.append(provider)
        query += " ORDER BY checked_at DESC LIMIT ?"
        params.append(limit)
        with connect(self.db_path) as connection:
            rows = connection.execute(query, params).fetchall()
        return [self._row_to_company_discovery_status(row) for row in rows]

    def _row_to_job(self, row) -> JobPosting:
        return JobPosting(
            id=row["id"],
            source=row["source"],
            company=row["company"],
            external_id=row["external_id"],
            title=row["title"],
            location=row["location"],
            description=row["description"],
            url=row["url"],
            employment_type=row["employment_type"],
            collected_at=datetime.fromisoformat(row["collected_at"]),
            last_seen_at=datetime.fromisoformat(row["last_seen_at"]),
            content_hash=row["content_hash"],
            status=row["status"],
            raw_json=json.loads(row["raw_json"]),
        )

    def _row_to_discovery_preview(self, row) -> JobDiscoveryPreview:
        return JobDiscoveryPreview(
            id=row["id"],
            discovery_source=row["discovery_source"],
            external_id=row["external_id"],
            company=row["company"],
            title=row["title"],
            location=row["location"],
            snippet=row["snippet"],
            source_url=row["source_url"],
            final_url=row["final_url"],
            ats_type=row["ats_type"],
            jd_quality=row["jd_quality"],
            status=row["status"],
            collected_at=datetime.fromisoformat(row["collected_at"]),
            raw_json=json.loads(row["raw_json"]),
        )

    def _row_to_company_discovery_status(self, row) -> CompanyDiscoveryStatus:
        return CompanyDiscoveryStatus(
            id=row["id"],
            company=row["company"],
            normalized_company=row["normalized_company"],
            provider=row["provider"],
            provider_identifier=row["provider_identifier"],
            status=row["status"],
            jobs_found_count=row["jobs_found_count"],
            message=row["message"],
            checked_at=datetime.fromisoformat(row["checked_at"]),
        )
