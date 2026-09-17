from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
import hashlib
import re
from typing import Protocol
from urllib.parse import urlparse

import httpx

from app.ingestion.source_registry import JobSource
from app.schemas.job import JobPosting


class JobSourceClient(Protocol):
    def fetch(self, source: JobSource) -> list[JobPosting]:
        ...


class HTMLTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        clean_data = data.strip()
        if clean_data:
            self.parts.append(clean_data)

    def get_text(self) -> str:
        return " ".join(self.parts)


def strip_html(value: str | None) -> str:
    if not value:
        return ""
    parser = HTMLTextParser()
    parser.feed(unescape(value))
    return re.sub(r"\s+", " ", parser.get_text()).strip()


def make_content_hash(*parts: str | None) -> str:
    content = "|".join(part or "" for part in parts)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def contains_marker(text: str, marker: str) -> bool:
    if len(marker) <= 3 and marker.strip().isalnum():
        return re.search(rf"(?<![a-z0-9]){re.escape(marker)}(?![a-z0-9])", text) is not None
    return marker in text


def is_campus_tech_job(title: str, description: str, location: str | None) -> bool:
    title_text = f" {title.lower()} "
    searchable_text = f" {title} {description} ".lower()
    location_text = (location or "").lower()
    candidate_markers = (
        "analyst program",
        "apprentice",
        "campus",
        "co-op",
        "early career",
        "fresh graduate",
        "graduate",
        "intern",
        "internship",
        "launch program",
        "management associate",
        "new grad",
        "student",
        "summer analyst",
        "summer associate",
        "trainee",
        "university",
    )
    title_tech_markers = (
        "ai",
        "application",
        "backend",
        "back-end",
        "business intelligence",
        "cloud",
        "cyber security",
        "cybersecurity",
        "data analyst",
        "data engineer",
        "data science",
        "data scientist",
        "developer",
        "devops",
        "engineering",
        "frontend",
        "front-end",
        "full stack",
        "full-stack",
        "information security",
        "information systems",
        "information technology",
        "machine learning",
        "mobile",
        "platform",
        "programmer",
        "quant developer",
        "qa",
        "security engineer",
        "site reliability",
        "software",
        "solutions architect",
        "systems engineer",
        "technical analyst",
        "technology analyst",
        "test engineer",
        "ui engineer",
        "web",
    )
    tech_markers = (
        ".net",
        "algorithm",
        "analytics",
        "android",
        "api",
        "application",
        "artificial intelligence",
        "automation",
        "aws",
        "azure",
        "backend",
        "back-end",
        "big data",
        "blockchain",
        "business intelligence",
        "c#",
        "c++",
        "cloud",
        "computer science",
        "computer vision",
        "crm",
        "cyber security",
        "cybersecurity",
        "database administrator",
        "data analyst",
        "data analytics",
        "data engineer",
        "data scientist",
        "ai",
        "data",
        "database",
        "data engineering",
        "data science",
        "developer",
        "development",
        "devops",
        "digital",
        "docker",
        "embedded",
        "erp",
        "engineering",
        "etl",
        "firmware",
        "frontend",
        "front-end",
        "full stack",
        "full-stack",
        "gcp",
        "git",
        "go ",
        "golang",
        "hardware",
        "hpc",
        "infrastructure",
        "ios",
        "it ",
        "java",
        "javascript",
        "kotlin",
        "kubernetes",
        "linux",
        "information security",
        "information systems",
        "information technology",
        "machine learning",
        "microservices",
        "ml",
        "mobile",
        "network",
        "node",
        "nlp",
        "platform",
        "product engineering",
        "programmer",
        "programming",
        "python",
        "qa",
        "quant",
        "react",
        "reliability engineer",
        "robotics",
        "sap",
        "scrum",
        "security",
        "site reliability",
        "software",
        "solution architect",
        "sql",
        "sre",
        "systems",
        "technical",
        "technology",
        "test engineer",
        "typescript",
        "ui engineer",
        "ux engineer",
        "web",
        "engineer",
    )
    excluded_title_markers = (
        "account executive",
        "accounting",
        "admin",
        "assistant",
        "benefits",
        "brand",
        "communications",
        "compensation",
        "content",
        "customer success",
        "employee engagement",
        "employee relations",
        "events",
        "finance intern",
        "financial planning",
        "fraud operations",
        "generalist",
        "general counsel",
        "growth marketing",
        "head of",
        "hr ",
        "human resource",
        "implementation consultant",
        "investment analyst",
        "legal",
        "management",
        "marketing",
        "manager",
        "office",
        "operations intern",
        "partnership",
        "payroll",
        "people",
        "policy",
        "procurement",
        "public relations",
        "recruiter",
        "recruiting",
        "recruitment",
        "sales",
        "specialist",
        "strategy",
        "talent acquisition",
        "counsel",
    )
    senior_title_markers = (
        "chief",
        "director",
        "head",
        "lead",
        "principal",
        "senior",
        "staff",
    )
    title_candidate_markers = (
        "apprentice",
        "campus",
        "co-op",
        "early career",
        "entry level",
        "fresh graduate",
        "graduate",
        "intern",
        "internship",
        "junior",
        "new grad",
        "programme",
        "program",
        "student",
        "summer analyst",
        "summer associate",
        "trainee",
        "university",
    )
    title_has_tech_marker = any(
        contains_marker(title_text, marker) for marker in title_tech_markers
    )
    title_has_candidate_marker = any(
        contains_marker(title_text, marker) for marker in title_candidate_markers
    )
    if any(contains_marker(title_text, marker) for marker in excluded_title_markers):
        return False
    if (
        any(contains_marker(title_text, marker) for marker in senior_title_markers)
        and not title_has_candidate_marker
    ):
        return False

    has_candidate_marker = title_has_candidate_marker
    text_tech_marker_count = sum(
        1 for marker in tech_markers if contains_marker(searchable_text, marker)
    )
    has_tech_marker = title_has_tech_marker or text_tech_marker_count >= 2
    return has_candidate_marker and has_tech_marker and "singapore" in location_text


class ByteDanceCampusClient:
    def __init__(self, timeout_seconds: float = 20.0, page_size: int = 50) -> None:
        self.timeout_seconds = timeout_seconds
        self.page_size = page_size

    def fetch(self, source: JobSource) -> list[JobPosting]:
        payload = {
            "keyword": "",
            "limit": self.page_size,
            "offset": 0,
            "portal_type": 3,
            "portal_entrance": 1,
            "language": "en",
            "recruitment_id_list": ["201", "202"],
            "job_category_id_list": [],
            "location_code_list": [],
            "subject_id_list": [],
            "tag_id_list": [],
            "storefront_id_list": [],
            "job_function_id_list": [],
        }
        headers = {
            "Origin": "https://jobs.bytedance.com",
            "Referer": "https://jobs.bytedance.com/campus/position",
            "User-Agent": "Mozilla/5.0 CareerPilotBot/0.1",
        }
        with httpx.Client(timeout=self.timeout_seconds, headers=headers) as client:
            response = client.post(source.identifier, json=payload)
            response.raise_for_status()
            data = response.json()

        rows = data.get("data", {}).get("job_post_list", [])
        return [job for row in rows if (job := self._normalize_row(source, row)) is not None]

    def _normalize_row(self, source: JobSource, row: dict) -> JobPosting | None:
        title = str(row.get("title") or "").strip()
        external_id = str(row.get("id") or row.get("job_id") or "").strip()
        description = strip_html(row.get("description") or row.get("job_description"))
        requirement = strip_html(row.get("requirement"))
        full_description = "\n\n".join(part for part in [description, requirement] if part)
        location = self._location_from_row(row)
        if not external_id or not title or not full_description:
            return None
        if not is_campus_tech_job(title, full_description, location):
            return None

        now = datetime.now(timezone.utc)
        url = f"https://lifeattiktok.com/search/{external_id}"
        return JobPosting(
            source=source.name,
            company=source.company,
            external_id=external_id,
            title=title,
            location=location,
            description=full_description,
            url=url,
            employment_type=self._employment_type(row),
            collected_at=now,
            last_seen_at=now,
            content_hash=make_content_hash(title, location, full_description),
            raw_json=row,
        )

    def _location_from_row(self, row: dict) -> str | None:
        city_info = row.get("city_info") or row.get("city_info_list") or row.get("city_list")
        if isinstance(city_info, list):
            names = [
                str(item.get("name") or item.get("en_name") or item.get("cn_name"))
                for item in city_info
                if isinstance(item, dict)
            ]
            return ", ".join(name for name in names if name)
        if isinstance(city_info, dict):
            return str(city_info.get("name") or city_info.get("en_name") or city_info.get("cn_name"))
        return None

    def _employment_type(self, row: dict) -> str | None:
        recruit_type = row.get("recruit_type")
        if isinstance(recruit_type, dict):
            return str(recruit_type.get("name") or recruit_type.get("en_name") or "")
        return None


class GreenhouseClient:
    def __init__(self, timeout_seconds: float = 8.0) -> None:
        self.timeout_seconds = timeout_seconds

    def fetch(self, source: JobSource) -> list[JobPosting]:
        url = f"https://boards-api.greenhouse.io/v1/boards/{source.identifier}/jobs"
        response = httpx.get(url, params={"content": "true"}, timeout=self.timeout_seconds)
        response.raise_for_status()
        rows = response.json().get("jobs", [])
        return [job for row in rows if (job := self._normalize_row(source, row)) is not None]

    def _normalize_row(self, source: JobSource, row: dict) -> JobPosting | None:
        title = str(row.get("title") or "").strip()
        external_id = str(row.get("id") or "").strip()
        location = (row.get("location") or {}).get("name")
        description = strip_html(row.get("content"))
        if not external_id or not title or not description:
            return None
        if not is_campus_tech_job(title, description, location):
            return None

        now = datetime.now(timezone.utc)
        return JobPosting(
            source=source.name,
            company=source.company,
            external_id=external_id,
            title=title,
            location=location,
            description=description,
            url=row.get("absolute_url") or "",
            collected_at=now,
            last_seen_at=now,
            content_hash=make_content_hash(title, location, description),
            raw_json=row,
        )


class LeverClient:
    def __init__(self, timeout_seconds: float = 8.0) -> None:
        self.timeout_seconds = timeout_seconds

    def fetch(self, source: JobSource) -> list[JobPosting]:
        url = f"https://api.lever.co/v0/postings/{source.identifier}"
        response = httpx.get(url, params={"mode": "json"}, timeout=self.timeout_seconds)
        response.raise_for_status()
        rows = response.json()
        return [job for row in rows if (job := self._normalize_row(source, row)) is not None]

    def _normalize_row(self, source: JobSource, row: dict) -> JobPosting | None:
        title = str(row.get("text") or "").strip()
        external_id = str(row.get("id") or "").strip()
        location = row.get("categories", {}).get("location")
        description = self._full_description(row)
        if not external_id or not title or not description:
            return None
        if not is_campus_tech_job(title, description, location):
            return None

        now = datetime.now(timezone.utc)
        return JobPosting(
            source=source.name,
            company=source.company,
            external_id=external_id,
            title=title,
            location=location,
            description=description,
            url=row.get("hostedUrl") or row.get("applyUrl") or "",
            employment_type=row.get("categories", {}).get("commitment"),
            collected_at=now,
            last_seen_at=now,
            content_hash=make_content_hash(title, location, description),
            raw_json=row,
        )

    def _full_description(self, row: dict) -> str:
        parts = [
            strip_html(row.get("descriptionPlain") or row.get("description")),
            strip_html(row.get("descriptionBodyPlain") or row.get("descriptionBody")),
            strip_html(row.get("openingPlain") or row.get("opening")),
            strip_html(row.get("additionalPlain") or row.get("additional")),
        ]
        for section in row.get("lists") or []:
            if not isinstance(section, dict):
                continue
            section_title = strip_html(section.get("text"))
            section_content = strip_html(section.get("content"))
            if section_title and section_content:
                parts.append(f"{section_title}: {section_content}")
            elif section_content:
                parts.append(section_content)
        deduped_parts = list(dict.fromkeys(part for part in parts if part))
        return "\n\n".join(deduped_parts)


class SmartRecruitersClient:
    def __init__(self, timeout_seconds: float = 8.0) -> None:
        self.timeout_seconds = timeout_seconds

    def fetch(self, source: JobSource) -> list[JobPosting]:
        url = f"https://api.smartrecruiters.com/v1/companies/{source.identifier}/postings"
        response = httpx.get(
            url,
            params={"limit": 100, "country": "sg", "q": "intern"},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        rows = response.json().get("content", [])
        return [job for row in rows if (job := self._normalize_row(source, row)) is not None]

    def _normalize_row(self, source: JobSource, row: dict) -> JobPosting | None:
        title = str(row.get("name") or "").strip()
        external_id = str(row.get("id") or row.get("uuid") or "").strip()
        location_data = row.get("location") or {}
        location = ", ".join(
            part
            for part in [
                location_data.get("city"),
                location_data.get("region"),
                location_data.get("country"),
            ]
            if part
        )
        description = strip_html(row.get("jobAd", {}).get("jobDescription"))
        if not external_id or not title:
            return None
        if not description:
            description = title
        if not is_campus_tech_job(title, description, location):
            return None

        now = datetime.now(timezone.utc)
        return JobPosting(
            source=source.name,
            company=source.company,
            external_id=external_id,
            title=title,
            location=location,
            description=description,
            url=row.get("ref") or "",
            collected_at=now,
            last_seen_at=now,
            content_hash=make_content_hash(title, location, description),
            raw_json=row,
        )


class AshbyClient:
    def __init__(self, timeout_seconds: float = 8.0) -> None:
        self.timeout_seconds = timeout_seconds

    def fetch(self, source: JobSource) -> list[JobPosting]:
        url = f"https://api.ashbyhq.com/posting-api/job-board/{source.identifier}"
        response = httpx.get(url, timeout=self.timeout_seconds)
        response.raise_for_status()
        rows = response.json().get("jobs", [])
        return [job for row in rows if (job := self._normalize_row(source, row)) is not None]

    def _normalize_row(self, source: JobSource, row: dict) -> JobPosting | None:
        title = str(row.get("title") or "").strip()
        external_id = str(row.get("id") or row.get("jobId") or "").strip()
        location = self._location_from_row(row)
        description = strip_html(
            row.get("descriptionHtml")
            or row.get("description")
            or row.get("content")
        )
        if not external_id or not title or not description:
            return None
        if not is_campus_tech_job(title, description, location):
            return None

        now = datetime.now(timezone.utc)
        return JobPosting(
            source=source.name,
            company=source.company,
            external_id=external_id,
            title=title,
            location=location,
            description=description,
            url=row.get("jobUrl") or row.get("applyUrl") or "",
            collected_at=now,
            last_seen_at=now,
            content_hash=make_content_hash(title, location, description),
            raw_json=row,
        )

    def _location_from_row(self, row: dict) -> str | None:
        location = row.get("location")
        if isinstance(location, str):
            return location
        if isinstance(location, dict):
            return str(location.get("name") or location.get("displayName") or "")
        locations = row.get("locations")
        if isinstance(locations, list):
            names = []
            for item in locations:
                if isinstance(item, str):
                    names.append(item)
                elif isinstance(item, dict):
                    names.append(str(item.get("name") or item.get("displayName") or ""))
            return ", ".join(name for name in names if name)
        return None


class WorkdayClient:
    def __init__(self, timeout_seconds: float = 10.0, page_size: int = 20) -> None:
        self.timeout_seconds = timeout_seconds
        self.page_size = page_size
        self.search_terms = (
            "software intern",
            "data intern",
            "technology intern",
            "software graduate",
            "data graduate",
        )

    def fetch(self, source: JobSource) -> list[JobPosting]:
        base_url, tenant, site = self._parse_identifier(source.identifier)
        jobs_by_id: dict[str, JobPosting] = {}
        with httpx.Client(
            timeout=self.timeout_seconds,
            headers={"User-Agent": "Mozilla/5.0 CareerPilotBot/0.1"},
        ) as client:
            for search_term in self.search_terms:
                response = client.post(
                    f"{base_url}/wday/cxs/{tenant}/{site}/jobs",
                    json={
                        "appliedFacets": {},
                        "limit": self.page_size,
                        "offset": 0,
                        "searchText": search_term,
                    },
                )
                response.raise_for_status()
                rows = response.json().get("jobPostings", [])
                for row in rows:
                    external_path = row.get("externalPath")
                    if not external_path:
                        continue
                    detail = client.get(f"{base_url}/wday/cxs/{tenant}/{site}{external_path}")
                    detail.raise_for_status()
                    job = self._normalize_detail(source, detail.json(), external_path)
                    if job is not None:
                        jobs_by_id[job.external_id] = job
        return list(jobs_by_id.values())

    def _parse_identifier(self, identifier: str) -> tuple[str, str, str]:
        parsed_url = urlparse(identifier)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("Workday identifier must be a Workday careers URL.")
        parts = [part for part in parsed_url.path.split("/") if part]
        tenant = parsed_url.netloc.split(".")[0]
        if parts and "-" in parts[0] and len(parts) > 1:
            site = parts[1]
        elif parts:
            site = parts[0]
        else:
            raise ValueError("Workday identifier must include a site path.")
        return f"{parsed_url.scheme}://{parsed_url.netloc}", tenant, site

    def _normalize_detail(
        self,
        source: JobSource,
        payload: dict,
        external_path: str,
    ) -> JobPosting | None:
        info = payload.get("jobPostingInfo") or {}
        title = str(info.get("title") or "").strip()
        external_id = str(info.get("id") or external_path).strip()
        location = self._location_from_info(info)
        description = strip_html(info.get("jobDescription"))
        if not external_id or not title or not description:
            return None
        if not is_campus_tech_job(title, description, location):
            return None

        now = datetime.now(timezone.utc)
        return JobPosting(
            source=source.name,
            company=source.company,
            external_id=external_id,
            title=title,
            location=location,
            description=description,
            url=info.get("externalUrl") or info.get("jobPostingSiteUrl") or source.identifier,
            employment_type=info.get("timeType"),
            collected_at=now,
            last_seen_at=now,
            content_hash=make_content_hash(title, location, description),
            raw_json=payload,
        )

    def _location_from_info(self, info: dict) -> str | None:
        locations = info.get("jobPostingLocations")
        if isinstance(locations, list):
            names = [
                str(item.get("displayName") or item.get("name") or "")
                for item in locations
                if isinstance(item, dict)
            ]
            if names:
                return ", ".join(name for name in names if name)
        location = info.get("location")
        if isinstance(location, str):
            return location
        if isinstance(location, dict):
            return str(location.get("displayName") or location.get("name") or "")
        return None


class TencentCareersClient:
    def __init__(self, timeout_seconds: float = 20.0, page_size: int = 50) -> None:
        self.timeout_seconds = timeout_seconds
        self.page_size = page_size
        self.keywords = (
            "Singapore",
            "intern Singapore",
            "software Singapore",
            "data Singapore",
        )

    def fetch(self, source: JobSource) -> list[JobPosting]:
        jobs_by_id: dict[str, JobPosting] = {}
        with httpx.Client(timeout=self.timeout_seconds) as client:
            for keyword in self.keywords:
                response = client.get(
                    source.identifier,
                    params={
                        "keyword": keyword,
                        "pageIndex": 1,
                        "pageSize": self.page_size,
                        "language": "en-us",
                    },
                )
                response.raise_for_status()
                rows = response.json().get("Data", {}).get("Posts", [])
                for row in rows:
                    job = self._normalize_row(source, row)
                    if job is not None:
                        jobs_by_id[job.external_id] = job
        return list(jobs_by_id.values())

    def _normalize_row(self, source: JobSource, row: dict) -> JobPosting | None:
        title = str(row.get("RecruitPostName") or "").strip()
        external_id = str(row.get("PostId") or row.get("RecruitPostId") or "").strip()
        location = str(row.get("LocationName") or row.get("CountryName") or "").strip()
        responsibility = strip_html(row.get("Responsibility"))
        requirement = strip_html(row.get("Requirement"))
        description = "\n\n".join(part for part in [responsibility, requirement] if part)
        if not external_id or not title or not description:
            return None
        if not is_campus_tech_job(title, description, location):
            return None

        now = datetime.now(timezone.utc)
        url = f"https://careers.tencent.com/en-us/jobdesc.html?postId={external_id}"
        return JobPosting(
            source=source.name,
            company=source.company,
            external_id=external_id,
            title=title,
            location=location,
            description=description,
            url=url,
            employment_type="Intern" if "intern" in title.lower() else None,
            collected_at=now,
            last_seen_at=now,
            content_hash=make_content_hash(title, location, description),
            raw_json=row,
        )


def build_client(provider: str) -> JobSourceClient | None:
    clients: dict[str, JobSourceClient] = {
        "ashby": AshbyClient(),
        "bytedance": ByteDanceCampusClient(),
        "greenhouse": GreenhouseClient(),
        "lever": LeverClient(),
        "smartrecruiters": SmartRecruitersClient(),
        "tencent": TencentCareersClient(),
        "workday": WorkdayClient(),
    }
    return clients.get(provider)
