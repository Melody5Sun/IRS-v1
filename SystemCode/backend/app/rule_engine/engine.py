"""主流程：读库 -> 清洗岗位字段 -> 构造学生 fact -> 运行规则 -> 输出通过全部规则的岗位 id。"""

import logging
import sqlite3
from pathlib import Path

from app.rule_engine.constants import (
    DEGREE_RANK,
    FULL_TIME_EMPLOYMENT,
    JOB_FIELD_VOCAB,
    NOT_STATED,
    STUDENT_DEGREE_MISSING_RANK,
)
from app.rule_engine.rules import FilterEngine, Job, Student
from app.schemas.profile import UserProfile

logger = logging.getLogger(__name__)

# 取 job_analysis 全部列：新规则用到新列时不需要改这里的 SQL
_JOBS_SQL = """
    SELECT j.id AS id, j.status AS status, a.*
    FROM jobs j
    JOIN job_analysis a ON a.job_id = j.id
    ORDER BY j.id
"""


def load_job_facts(connection: sqlite3.Connection) -> list[Job]:
    """读取有分析记录的岗位；词表内的字段做清洗：空值 -> not_stated，未知值 -> not_stated 并记日志。"""
    connection.row_factory = sqlite3.Row
    facts = []
    for row in connection.execute(_JOBS_SQL):
        fields = {key: row[key] for key in row.keys() if key != "job_id"}
        for field, vocab in JOB_FIELD_VOCAB.items():
            value = fields.get(field)
            if value is None or (isinstance(value, str) and not value.strip()):
                fields[field] = NOT_STATED
            elif value not in vocab:
                logger.warning("岗位 %s 的 %s 取值 %r 不在词表内，按不约束处理", fields["id"], field, value)
                fields[field] = NOT_STATED
        facts.append(Job(**fields))
    return facts


def build_student_fact(profile: UserProfile) -> Student:
    resume, constraints = profile.resume, profile.constraints
    # 学历取所有条目中等级最高的一个（含在读），无条目时等同于学生侧缺失
    degree_rank = max(
        (DEGREE_RANK[education.degree] for education in resume.educations),
        default=STUDENT_DEGREE_MISSING_RANK,
    )
    return Student(
        degree_rank=degree_rank,
        work_modes=list(constraints.work_modes),
        employment_types=list(constraints.target_employment_types),
        industries=list(constraints.target_industries),
        has_full_time_experience=any(
            experience.employment_type == FULL_TIME_EMPLOYMENT for experience in resume.experiences
        ),
    )


def evaluate(profile: UserProfile, connection: sqlite3.Connection) -> tuple[list[int], dict[int, set[str]]]:
    """返回 (通过全部规则的岗位 id 升序列表, 岗位 id -> 剔除它的规则名集合)。"""
    job_facts = load_job_facts(connection)
    engine = FilterEngine()
    engine.reset()
    engine.declare(build_student_fact(profile))
    for fact in job_facts:
        engine.declare(fact)
    engine.run()
    kept = [fact["id"] for fact in job_facts if fact["id"] not in engine.rejections]
    return kept, engine.rejections


def connect_read_only(db_path: str) -> sqlite3.Connection:
    # mode=ro：文件不存在时直接报错，不会像默认模式那样新建一个空库
    return sqlite3.connect(Path(db_path).resolve().as_uri() + "?mode=ro", uri=True)


def filter_jobs(profile: UserProfile, db_path: str) -> dict:
    connection = connect_read_only(db_path)
    try:
        kept, _ = evaluate(profile, connection)
    finally:
        connection.close()
    return {"job_ids": kept}
