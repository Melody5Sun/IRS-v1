import logging
import sqlite3

import pytest

from app.rule_engine import filter_jobs
from app.rule_engine.engine import evaluate
from app.schemas.profile import JobSearchConstraints, UserProfile
from app.schemas.resume import Education, Experience, ResumeDocument

DDL = """
create table jobs (
    id INTEGER primary key autoincrement,
    source TEXT not null, company TEXT not null, external_id TEXT not null,
    title TEXT not null, location TEXT, description TEXT not null, url TEXT not null,
    employment_type TEXT, collected_at TEXT not null, last_seen_at TEXT not null,
    content_hash TEXT not null, status TEXT default 'active' not null,
    raw_json TEXT default '{}' not null,
    unique (source, external_id)
);
create table job_analysis (
    job_id INTEGER primary key references jobs,
    summary TEXT default '' not null,
    responsibilities_json TEXT default '[]' not null,
    required_skills_json TEXT default '[]' not null,
    preferred_skills_json TEXT default '[]' not null,
    employment_type TEXT default 'not_stated' not null,
    candidate_type TEXT default 'not_stated' not null,
    seniority_level TEXT default 'not_stated' not null,
    remote_policy TEXT default 'not_stated' not null,
    degree_required TEXT default 'not_stated' not null,
    major_required_json TEXT default '[]' not null,
    keywords_json TEXT default '[]' not null,
    source_evidence_json TEXT default '[]' not null,
    analysis_json TEXT default '{}' not null,
    industry TEXT default 'Software & IT Services' not null
);
"""


def make_db(*jobs: dict, connection: sqlite3.Connection | None = None) -> sqlite3.Connection:
    """每个 dict 是一条岗位：status 写入 jobs，其余键写入 job_analysis；analysis=False 表示不建分析记录。"""
    connection = connection or sqlite3.connect(":memory:")
    connection.executescript(DDL)
    for index, job in enumerate(jobs, start=1):
        job = dict(job)
        job_id = job.pop("id", index)
        with_analysis = job.pop("analysis", True)
        connection.execute(
            "insert into jobs (id, source, company, external_id, title, description, url,"
            " collected_at, last_seen_at, content_hash, status) values (?, 's', 'c', ?, 't', 'd', 'u', 'x', 'x', 'h', ?)",
            (job_id, str(job_id), job.pop("status", "active")),
        )
        if with_analysis:
            columns = ["job_id", *job]
            connection.execute(
                f"insert into job_analysis ({', '.join(columns)}) values ({', '.join('?' * len(columns))})",
                (job_id, *job.values()),
            )
    return connection


def make_profile(
    degrees: tuple[str, ...] = (),
    experience_types: tuple[str, ...] = (),
    exchange_only: bool = False,
    **constraints,
) -> UserProfile:
    educations = [Education(institution="U", degree=degree) for degree in degrees]
    if exchange_only:
        educations = [Education(institution="U", entry_type="exchange", degree="not_applicable")]
    return UserProfile(
        resume=ResumeDocument(
            educations=educations,
            experiences=[Experience(company="C", title="T", employment_type=t) for t in experience_types],
        ),
        constraints=JobSearchConstraints(**constraints),
    )


def kept_ids(profile: UserProfile, *jobs: dict) -> list[int]:
    kept, _ = evaluate(profile, make_db(*jobs))
    return kept


# ---------- 规则 1：状态 ----------

def test_status_keeps_active_and_rejects_inactive() -> None:
    assert kept_ids(make_profile(), {"status": "active"}, {"status": "inactive"}) == [1]


# ---------- 规则 2：学历 ----------

@pytest.mark.parametrize(
    ("degrees", "required", "kept"),
    [
        (("bachelor",), "master", False),  # 低于要求：剔除
        (("master",), "master", True),  # 恰好等于要求：保留
        (("bachelor", "phd", "diploma"), "phd", True),  # 最高学历在列表中间
        (("diploma",), "bachelor", False),
        ((), "phd", True),  # 无学历条目：学生侧缺失，不约束
        (("bachelor",), "not_stated", True),
        (("diploma",), "not_applicable", True),
    ],
)
def test_degree(degrees: tuple[str, ...], required: str, kept: bool) -> None:
    assert (kept_ids(make_profile(degrees), {"degree_required": required}) == [1]) is kept


def test_degree_exchange_only_is_treated_as_missing() -> None:
    assert kept_ids(make_profile(exchange_only=True), {"degree_required": "phd"}) == [1]


# ---------- 规则 3：工作模式 ----------

@pytest.mark.parametrize(
    ("work_modes", "policy", "kept"),
    [
        (["onsite"], "hybrid", True),  # hybrid 岗位配任意 work_modes 都放行
        (["remote"], "hybrid", True),
        (["remote"], "onsite", False),  # onsite 岗位配只选 remote 的学生：剔除
        (["onsite", "remote"], "remote", True),
        ([], "onsite", True),  # 学生 work_modes 为空：不约束
        (["hybrid"], "onsite", False),  # 学生只选 hybrid 遇到 onsite 岗位：按字面剔除
        (["hybrid"], "remote", False),
        (["remote"], "not_stated", True),
    ],
)
def test_work_mode(work_modes: list[str], policy: str, kept: bool) -> None:
    profile = make_profile(work_modes=work_modes)
    assert (kept_ids(profile, {"remote_policy": policy}) == [1]) is kept


# ---------- 规则 4：雇佣类型 ----------

@pytest.mark.parametrize(
    ("types", "employment_type", "kept"),
    [
        (["internship"], "internship", True),
        (["internship"], "full_time", False),
        (["internship", "full_time"], "full_time", True),
        (["internship"], "contract", False),
        ([], "full_time", True),  # 学生 target_employment_types 为空：不约束
        (["full_time"], "not_stated", True),  # 岗位 not_stated：不约束
    ],
)
def test_employment_type(types: list[str], employment_type: str, kept: bool) -> None:
    profile = make_profile(target_employment_types=types)
    assert (kept_ids(profile, {"employment_type": employment_type}) == [1]) is kept


# ---------- 规则 5：候选人类型 ----------

@pytest.mark.parametrize(
    ("experience_types", "candidate_type", "kept"),
    [
        ((), "experienced", False),  # experiences 为空：剔除（本规则不放行学生侧缺失）
        (("not_stated",), "experienced", False),
        (("internship",), "experienced", False),  # 只有实习经历
        (("internship", "full_time"), "experienced", True),
        ((), "student", True),
        ((), "new_graduate", True),
        ((), "not_stated", True),
    ],
)
def test_candidate_type(experience_types: tuple[str, ...], candidate_type: str, kept: bool) -> None:
    profile = make_profile(experience_types=experience_types)
    assert (kept_ids(profile, {"candidate_type": candidate_type}) == [1]) is kept


# ---------- 规则 6：行业 ----------

def test_industry_keeps_matching_and_rejects_others() -> None:
    profile = make_profile(target_industries=["Gaming"])
    assert kept_ids(profile, {"industry": "Gaming"}, {"industry": "Internet"}) == [1]


def test_industry_empty_student_list_is_unconstrained() -> None:
    assert kept_ids(make_profile(), {"industry": "Gaming"}, {"industry": "Internet"}) == [1, 2]


# ---------- 通用原则 ----------

def test_unknown_job_value_is_unconstrained_and_logged(caplog: pytest.LogCaptureFixture) -> None:
    profile = make_profile(
        degrees=("diploma",),
        work_modes=["onsite"],
        target_employment_types=["internship"],
        target_industries=["Gaming"],
    )
    job = {
        "degree_required": "doctorate",
        "remote_policy": "flexible",
        "employment_type": "temp",
        "candidate_type": "senior_pro",
        "industry": "Farming",
    }
    with caplog.at_level(logging.WARNING, logger="app.rule_engine.engine"):
        assert kept_ids(profile, job) == [1]
    assert len(caplog.records) == 5


def test_blank_job_value_is_unconstrained() -> None:
    profile = make_profile(target_industries=["Gaming"], work_modes=["onsite"])
    assert kept_ids(profile, {"industry": " ", "remote_policy": ""}) == [1]


def test_job_without_analysis_is_excluded() -> None:
    assert kept_ids(make_profile(), {}, {"analysis": False}) == [1]


def test_rejections_record_every_failed_rule() -> None:
    profile = make_profile(("bachelor",), target_industries=["Gaming"])
    _, rejections = evaluate(profile, make_db({"status": "inactive", "degree_required": "phd", "industry": "Internet"}))
    assert rejections == {1: {"status", "degree", "industry"}}


# ---------- 入口函数：文件库 + 只读连接 ----------

def test_filter_jobs_reads_file_database(tmp_path) -> None:
    db_path = tmp_path / "jobs.db"
    connection = make_db({}, {"status": "inactive"}, connection=sqlite3.connect(db_path))
    connection.commit()
    connection.close()
    assert filter_jobs(make_profile(), str(db_path)) == {"job_ids": [1]}


def test_filter_jobs_does_not_create_missing_database(tmp_path) -> None:
    with pytest.raises(sqlite3.OperationalError):
        filter_jobs(make_profile(), str(tmp_path / "missing.db"))
    assert not (tmp_path / "missing.db").exists()


# ---------- 端到端 persona ----------

PERSONA_JOBS = (
    # 1 本科实习，现场，AI
    {"employment_type": "internship", "candidate_type": "student", "degree_required": "bachelor",
     "remote_policy": "onsite", "industry": "Artificial Intelligence"},
    # 2 硕士要求实习，混合，FinTech
    {"employment_type": "internship", "candidate_type": "student", "degree_required": "master",
     "remote_policy": "hybrid", "industry": "Financial Technology (FinTech)"},
    # 3 校招全职，远程，软件
    {"employment_type": "full_time", "candidate_type": "new_graduate", "degree_required": "master",
     "remote_policy": "remote", "industry": "Software & IT Services"},
    # 4 有经验全职，未说明工作模式，软件
    {"employment_type": "full_time", "candidate_type": "experienced", "degree_required": "bachelor",
     "industry": "Software & IT Services"},
    # 5 已下线的实习
    {"status": "inactive", "employment_type": "internship", "industry": "Artificial Intelligence"},
)


def test_persona_bachelor_seeking_internship() -> None:
    profile = make_profile(
        ("bachelor",),
        ("internship",),
        work_modes=["onsite", "hybrid"],
        target_employment_types=["internship"],
        target_industries=["Artificial Intelligence", "Financial Technology (FinTech)"],
    )
    # 2 学历不够；3、4 是全职；5 已下线
    assert kept_ids(profile, *PERSONA_JOBS) == [1]


def test_persona_master_seeking_graduate_job() -> None:
    profile = make_profile(
        ("bachelor", "master"),
        ("internship",),
        work_modes=["remote", "hybrid"],
        target_employment_types=["full_time", "internship"],
        target_industries=["Software & IT Services", "Financial Technology (FinTech)"],
    )
    # 1 行业和工作模式都不符；4 需要全职经验；5 已下线
    assert kept_ids(profile, *PERSONA_JOBS) == [2, 3]


def test_persona_experienced_seeking_experienced_job() -> None:
    profile = make_profile(
        ("bachelor",),
        ("internship", "full_time"),
        target_employment_types=["full_time"],
        target_industries=["Software & IT Services"],
    )
    # 3 要求硕士；1、2 是实习；5 已下线
    assert kept_ids(profile, *PERSONA_JOBS) == [4]
