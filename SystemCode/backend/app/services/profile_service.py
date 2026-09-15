from app.schemas.profile import JobSearchConstraints, UserProfile
from app.schemas.resume import ParsedResume, ResumeDocument

# 用户提交画像时允许留空的字段（补充说明选填、证书永久有效、交换项目没有专业、个人项目没有角色）
OPTIONAL_FIELDS = {"notes", "expiry_date", "major", "role"}
# 可以一条都不填的列表（学生可能没有）；但只要填了条目，条目里的字段仍要完整
OPTIONAL_LISTS = {"experiences", "projects", "research", "certificates"}

Loc = list[str | int]


def _is_blank(value: object) -> bool:
    # not_stated 是 LLM 解析不出来时的占位，用户手动提交时视同没填
    return value is None or value == "not_stated" or (isinstance(value, str) and not value.strip())


def find_empty_fields(data: dict[str, object], loc: Loc | None = None) -> list[Loc]:
    """返回不允许为空却为空的字段位置，比如 ["resume", "experiences", 0, "country"]。"""
    loc = loc or []
    empty: list[Loc] = []
    for key, value in data.items():
        if key in OPTIONAL_FIELDS:
            continue
        field_loc = [*loc, key]
        if isinstance(value, dict):
            empty += find_empty_fields(value, field_loc)
        elif isinstance(value, list):
            if not value and key not in OPTIONAL_LISTS:
                empty.append(field_loc)
            for index, item in enumerate(value):
                if isinstance(item, dict):
                    empty += find_empty_fields(item, [*field_loc, index])
                elif _is_blank(item):
                    empty.append([*field_loc, index])
        elif _is_blank(value):
            empty.append(field_loc)
    return empty


class ProfileService:
    """本地部署只有一个用户，只保存一份画像。"""

    def __init__(self) -> None:
        # ponytail: 存在进程内存，重启即丢失；之后持久化到数据库
        self.profile: UserProfile | None = None

    def save_resume(self, parsed: ParsedResume) -> None:
        # 重新上传简历时只替换画像，已经填写的求职约束保留
        constraints = self.profile.constraints if self.profile else JobSearchConstraints()
        # 简历里的自我介绍合并进补充说明；用户已经写过 notes 就不覆盖
        if parsed.about and not constraints.notes.strip():
            constraints = constraints.model_copy(update={"notes": parsed.about})
        resume = ResumeDocument.model_validate(parsed.model_dump(exclude={"about"}))
        self.profile = UserProfile(resume=resume, constraints=constraints)


# resumes 和 profile 两个路由共用同一份画像
profile_service = ProfileService()
