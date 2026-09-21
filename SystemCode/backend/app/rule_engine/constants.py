"""规则引擎用到的全部取值常量和映射表：规则代码只引用这里的名字，不写死字符串。"""

from typing import get_args

from app.schemas.common import CandidateType, Degree, EmploymentType, RemotePolicy
from app.schemas.profile import TARGET_INDUSTRIES

# 岗位侧"未说明"：该字段不构成拒绝理由
NOT_STATED = "not_stated"

# 规则 1：只保留 active 岗位
ACTIVE_STATUS = "active"

# 规则 2：学历等级映射（数字越大学历越高）；学生取所有学历条目中的最大值
DEGREE_RANK: dict[str, int] = {
    "not_applicable": 0,
    "diploma": 1,
    "bachelor": 2,
    "master": 3,
    "phd": 4,
}
# 岗位 degree_required 取这些值时不约束
DEGREE_UNCONSTRAINED = frozenset({NOT_STATED, "not_applicable"})
# 学生最高学历只到这一级（只有交换等无学位条目）时，视为学生侧缺失
STUDENT_DEGREE_MISSING_RANK = DEGREE_RANK["not_applicable"]

# 规则 3：岗位 remote_policy 取这些值时，学生选了任何工作模式都放行
REMOTE_POLICY_MATCHES_ANY = frozenset({"hybrid"})

# 规则 5：岗位要求有经验时，学生至少要有一段这种类型的经历
EXPERIENCED_CANDIDATE = "experienced"
FULL_TIME_EMPLOYMENT = "full_time"

# 岗位侧各字段的合法词表：词表外的取值按"不约束"处理并记日志
JOB_FIELD_VOCAB: dict[str, frozenset[str]] = {
    "degree_required": frozenset(get_args(Degree)),
    "remote_policy": frozenset(get_args(RemotePolicy)),
    "employment_type": frozenset(get_args(EmploymentType)),
    "candidate_type": frozenset(get_args(CandidateType)),
    "industry": frozenset(TARGET_INDUSTRIES),
}
