from app.schemas.profile import JobSearchConstraints, UserProfile
from app.schemas.resume import ResumeDocument


class ProfileService:
    """本地部署只有一个用户，只保存一份画像。"""

    def __init__(self) -> None:
        # ponytail: 存在进程内存，重启即丢失；之后持久化到数据库
        self.profile: UserProfile | None = None

    def save_resume(self, resume: ResumeDocument) -> None:
        # 重新上传简历时只替换画像，已经填写的求职约束保留
        constraints = self.profile.constraints if self.profile else JobSearchConstraints()
        self.profile = UserProfile(resume=resume, constraints=constraints)


# resumes 和 profile 两个路由共用同一份画像
profile_service = ProfileService()
