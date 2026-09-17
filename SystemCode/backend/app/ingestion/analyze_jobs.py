from app.services.job_requirement_service import JobRequirementService


class DisabledGeminiService:
    def is_configured(self) -> bool:
        return False


def main() -> None:
    service = JobRequirementService(gemini_service=DisabledGeminiService())
    analyzed_count = service.analyze_active_jobs()
    total_count = service.repository.count_job_analysis()
    print(f"analyzed_count={analyzed_count}")
    print(f"job_analysis_count={total_count}")


if __name__ == "__main__":
    main()
