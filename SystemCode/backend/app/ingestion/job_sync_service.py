from app.ingestion.job_source_clients import build_client
from app.ingestion.source_registry import DEFAULT_SOURCES, JobSource
from app.repositories.job_repository import JobRepository
from app.schemas.job import JobSyncResponse, JobSyncSourceResult


class JobSyncService:
    def __init__(
        self,
        repository: JobRepository | None = None,
        sources: list[JobSource] | None = None,
    ) -> None:
        self.repository = repository or JobRepository()
        if sources is None:
            self.repository.ensure_company_sources(DEFAULT_SOURCES)
            self.sources = self.repository.list_company_sources()
        else:
            self.sources = sources

    def sync(self) -> JobSyncResponse:
        source_results: list[JobSyncSourceResult] = []
        fetched_total = 0
        changed_total = 0

        for source in self.sources:
            if not source.enabled:
                source_results.append(
                    JobSyncSourceResult(
                        source=source.name,
                        company=source.company,
                        status="skipped",
                        fetched_count=0,
                        changed_count=0,
                        message="Source is registered but disabled until a stable public API is confirmed.",
                    )
                )
                self.repository.update_company_source_run_status(
                    source.name,
                    "skipped",
                    "Source is registered but disabled until a stable public API is confirmed.",
                )
                continue

            client = build_client(source.provider)
            if client is None:
                source_results.append(
                    JobSyncSourceResult(
                        source=source.name,
                        company=source.company,
                        status="skipped",
                        fetched_count=0,
                        changed_count=0,
                        message=f"Provider '{source.provider}' is not implemented.",
                    )
                )
                self.repository.update_company_source_run_status(
                    source.name,
                    "skipped",
                    f"Provider '{source.provider}' is not implemented.",
                )
                continue

            try:
                jobs = client.fetch(source)
                changed_count = self.repository.upsert_many(jobs)
                fetched_total += len(jobs)
                changed_total += changed_count
                source_results.append(
                    JobSyncSourceResult(
                        source=source.name,
                        company=source.company,
                        status="ok",
                        fetched_count=len(jobs),
                        changed_count=changed_count,
                    )
                )
                self.repository.update_company_source_run_status(
                    source.name,
                    "ok",
                    f"Fetched {len(jobs)} jobs; changed {changed_count}.",
                )
            except Exception as exc:
                message = str(exc)
                source_results.append(
                    JobSyncSourceResult(
                        source=source.name,
                        company=source.company,
                        status="failed",
                        fetched_count=0,
                        changed_count=0,
                        message=message,
                    )
                )
                self.repository.update_company_source_run_status(
                    source.name,
                    "failed",
                    message[:500],
                )

        return JobSyncResponse(
            fetched_count=fetched_total,
            changed_count=changed_total,
            expired_count=0,
            sources=source_results,
        )
