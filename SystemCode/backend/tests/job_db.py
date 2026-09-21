"""规则引擎和接口测试共用的造数据工具。

用真实的 app/db/schema.sql 建表：以后 schema 再改（比如再删一列），依赖它的测试会直接失败，
而不是像以前自带一份 DDL 那样和真实结构脱节后继续全绿。
"""

import json
import sqlite3
from pathlib import Path

from app.db.sqlite import SCHEMA_PATH
from app.parsers.job_industry_classifier import normalize_company_name
from app.schemas.profile import JobSearchConstraints, UserProfile
from app.schemas.resume import Education, Experience, ResumeDocument


def make_db(*jobs: dict, connection: sqlite3.Connection | None = None) -> sqlite3.Connection:
    """每个 dict 是一条岗位。

    - status / company / title 写入 jobs（company 默认 c<id>）
    - industry 写入 company_industries（按公司存，不给则该公司没有行业记录）
    - required_skills / preferred_skills 写入 analysis_json（下游技能评分读这份文档）
    - analysis_json 可整体覆盖（用来造坏数据）；analysis=False 表示不建分析记录
    - 其余键作为 job_analysis 的列写入
    """
    connection = connection or sqlite3.connect(":memory:")
    connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    for index, job in enumerate(jobs, start=1):
        job = dict(job)
        job_id = job.pop("id", index)
        with_analysis = job.pop("analysis", True)
        company = job.pop("company", f"c{job_id}")
        title = job.pop("title", f"t{job_id}")
        industry = job.pop("industry", None)
        required_skills = job.pop("required_skills", [])
        preferred_skills = job.pop("preferred_skills", [])
        analysis_json = job.pop(
            "analysis_json",
            json.dumps(
                {
                    "job_id": job_id,
                    "company": company,
                    "title": title,
                    "required_skills": required_skills,
                    "preferred_skills": preferred_skills,
                }
            ),
        )
        connection.execute(
            "insert into jobs (id, source, company, external_id, title, description, url,"
            " collected_at, last_seen_at, content_hash, status) values (?, 's', ?, ?, ?, 'd', 'u', 'x', 'x', 'h', ?)",
            (job_id, company, str(job_id), title, job.pop("status", "active")),
        )
        if industry is not None:
            connection.execute(
                "insert or replace into company_industries (normalized_company, company, industry) values (?, ?, ?)",
                (normalize_company_name(company), company, industry),
            )
        if with_analysis:
            job = {
                **job,
                "required_skills_json": json.dumps(required_skills),
                "preferred_skills_json": json.dumps(preferred_skills),
                "analysis_json": analysis_json,
            }
            columns = ["job_id", *job]
            connection.execute(
                f"insert into job_analysis ({', '.join(columns)}) values ({', '.join('?' * len(columns))})",
                (job_id, *job.values()),
            )
    return connection


def make_file_db(tmp_path: Path, *jobs: dict) -> Path:
    """把 make_db 的结果落成文件库（接口和 screen_jobs 走只读文件连接，不能用内存库）。"""
    db_path = tmp_path / "jobs.db"
    connection = make_db(*jobs, connection=sqlite3.connect(db_path))
    connection.commit()
    connection.close()
    return db_path


# 接口测试用的四个岗位：1、2 通过；3 行业不符；4 已下线
API_JOBS = (
    {"title": "Backend Engineer", "company": "Alpha", "industry": "Gaming",
     "employment_type": "internship", "required_skills": ["python", "sql"]},
    {"title": "Infra Engineer", "company": "Beta", "industry": "Gaming",
     "employment_type": "internship", "required_skills": ["kubernetes", "aws"]},
    {"title": "Web Engineer", "company": "Gamma", "industry": "Internet",
     "employment_type": "internship", "required_skills": ["python"]},
    {"title": "Old Job", "company": "Delta", "industry": "Gaming", "status": "inactive",
     "employment_type": "internship", "required_skills": ["python"]},
)


def make_api_profile(**overrides) -> UserProfile:
    """会通过 API_JOBS 里 1、2 号岗位的画像；overrides 覆盖求职约束。"""
    constraints = {"target_employment_types": ["internship"], "target_industries": ["Gaming"], **overrides}
    return make_profile(degrees=("bachelor",), skills=("Python", "SQL"), **constraints)


def make_profile(
    degrees: tuple[str, ...] = (),
    experience_types: tuple[str, ...] = (),
    exchange_only: bool = False,
    skills: tuple[str, ...] = (),
    **constraints,
) -> UserProfile:
    educations = [Education(institution="U", degree=degree) for degree in degrees]
    if exchange_only:
        educations = [Education(institution="U", entry_type="exchange", degree="not_applicable")]
    return UserProfile(
        resume=ResumeDocument(
            skills=list(skills),
            educations=educations,
            experiences=[Experience(company="C", title="T", employment_type=t) for t in experience_types],
        ),
        constraints=JobSearchConstraints(**constraints),
    )
