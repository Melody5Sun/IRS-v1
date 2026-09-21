"""硬约束规则：每条规则是 FilterEngine 的一个方法，命中即把岗位记为剔除。

新增规则 = 在 FilterEngine 里加一个 @Rule 方法（用到的取值放进 constants.py），主流程不用改。
"""

import collections
import collections.abc

# 兼容补丁：experta 1.9.4 锁定的 frozendict==1.2 仍在用 Python 3.10 起已移除的 collections.Mapping，
# 不补这一行 import experta 就会报 AttributeError；必须放在 import experta 之前
if not hasattr(collections, "Mapping"):
    collections.Mapping = collections.abc.Mapping  # type: ignore[attr-defined]

from experta import MATCH, TEST, Fact, KnowledgeEngine, Rule  # noqa: E402

from app.rule_engine.constants import (  # noqa: E402
    ACTIVE_STATUS,
    DEGREE_RANK,
    DEGREE_UNCONSTRAINED,
    EXPERIENCED_CANDIDATE,
    NOT_STATED,
    REMOTE_POLICY_MATCHES_ANY,
    STUDENT_DEGREE_MISSING_RANK,
)


class Student(Fact):
    """学生画像中与硬约束相关的字段（由 engine.build_student_fact 从 UserProfile 计算）。"""


class Job(Fact):
    """一条岗位：jobs.id/status + job_analysis 的全部列（由 engine.load_job_facts 读库并清洗）。"""


class FilterEngine(KnowledgeEngine):
    def __init__(self) -> None:
        super().__init__()
        # 岗位 id -> 剔除它的规则名集合；只用于统计各规则的剔除数量，不对外展示
        self.rejections: dict[int, set[str]] = {}

    def _reject(self, job_id: int, rule_name: str) -> None:
        self.rejections.setdefault(job_id, set()).add(rule_name)

    # 规则 1 状态：岗位必须是 active
    @Rule(Job(id=MATCH.job_id, status=MATCH.status), TEST(lambda status: status != ACTIVE_STATUS))
    def reject_status(self, job_id: int) -> None:
        self._reject(job_id, "status")

    # 规则 2 学历：学生最高学历 >= 岗位要求；岗位未说明或学生侧缺失时不约束
    @Rule(
        Student(degree_rank=MATCH.rank),
        Job(id=MATCH.job_id, degree_required=MATCH.required),
        TEST(
            lambda rank, required: rank > STUDENT_DEGREE_MISSING_RANK
            and required not in DEGREE_UNCONSTRAINED
            and DEGREE_RANK[required] > rank
        ),
    )
    def reject_degree(self, job_id: int) -> None:
        self._reject(job_id, "degree")

    # 规则 3 工作模式：hybrid 岗位对任何选择都放行；其余取值必须在学生 work_modes 中
    # 注意：学生选了 hybrid 并不会放行 onsite/remote 岗位（按字面匹配）
    @Rule(
        Student(work_modes=MATCH.modes),
        Job(id=MATCH.job_id, remote_policy=MATCH.policy),
        TEST(
            lambda modes, policy: bool(modes)
            and policy != NOT_STATED
            and policy not in REMOTE_POLICY_MATCHES_ANY
            and policy not in modes
        ),
    )
    def reject_work_mode(self, job_id: int) -> None:
        self._reject(job_id, "work_mode")

    # 规则 4 雇佣类型：岗位类型必须在学生 target_employment_types 中
    @Rule(
        Student(employment_types=MATCH.types),
        Job(id=MATCH.job_id, employment_type=MATCH.employment_type),
        TEST(
            lambda types, employment_type: bool(types)
            and employment_type != NOT_STATED
            and employment_type not in types
        ),
    )
    def reject_employment_type(self, job_id: int) -> None:
        self._reject(job_id, "employment_type")

    # 规则 5 候选人类型：experienced 岗位要求学生至少有一段全职经历（经历为空也剔除，是唯一不放行缺失的规则）
    @Rule(
        Student(has_full_time_experience=MATCH.has_full_time),
        Job(id=MATCH.job_id, candidate_type=MATCH.candidate_type),
        TEST(lambda has_full_time, candidate_type: candidate_type == EXPERIENCED_CANDIDATE and not has_full_time),
    )
    def reject_candidate_type(self, job_id: int) -> None:
        self._reject(job_id, "candidate_type")

    # 规则 6 行业：岗位行业必须在学生 target_industries 中
    @Rule(
        Student(industries=MATCH.industries),
        Job(id=MATCH.job_id, industry=MATCH.industry),
        TEST(lambda industries, industry: bool(industries) and industry != NOT_STATED and industry not in industries),
    )
    def reject_industry(self, job_id: int) -> None:
        self._reject(job_id, "industry")
