from typing import Literal

from pydantic import BaseModel, Field, model_validator

# 新加坡就业市场关注的身份状态，已按 IT 学生/应届生场景收窄；
# LLM 判断不了或不属于前三类的一律归 not_stated，不能瞎猜
VisaStatus = Literal["singapore_citizen", "student_pass", "permanent_resident", "not_stated"]
EmploymentType = Literal[
    "internship", "full_time", "part_time", "contract", "freelance", "not_stated"
]
LanguageLevel = Literal["native", "fluent", "intermediate", "basic", "not_stated"]
# not_applicable 用于没有学位产出的条目，比如短期交换/交流经历
Degree = Literal["bachelor", "master", "phd", "diploma", "not_applicable"]
EducationEntryType = Literal["degree", "exchange"]


class ResumeParseRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Plain text extracted from a resume.")


class ResumeProfile(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    skills: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    experience_years: float | None = None
    work_authorization: str | None = None


class Experience(BaseModel):
    company: str
    title: str
    employment_type: EmploymentType = "not_stated"
    start_date: str | None = None
    end_date: str | None = None
    description: str = ""
    country: str | None = None


class Project(BaseModel):
    title: str
    summary: str = ""
    technologies: list[str] = Field(default_factory=list)
    role: str | None = None


class Research(BaseModel):
    title: str
    institution: str | None = None
    summary: str = ""
    start_date: str | None = None
    end_date: str | None = None


class Education(BaseModel):
    institution: str
    entry_type: EducationEntryType = "degree"
    degree: Degree = "not_applicable"
    major: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    country: str | None = None


class Certificate(BaseModel):
    name: str
    issuer: str | None = None
    issue_date: str | None = None
    expiry_date: str | None = None


class Language(BaseModel):
    name: str
    level: LanguageLevel = "not_stated"


class ResumeDocument(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    visa_status: VisaStatus = "not_stated"
    # 由 visa_status 程序化推出，不接受 LLM 直接填写，避免跟 visa_status 自相矛盾
    requires_sponsorship: bool = True
    about: str | None = None
    experiences: list[Experience] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    research: list[Research] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    educations: list[Education] = Field(default_factory=list)
    certificates: list[Certificate] = Field(default_factory=list)
    languages: list[Language] = Field(default_factory=list)

    @model_validator(mode="after")
    def _derive_requires_sponsorship(self) -> "ResumeDocument":
        self.requires_sponsorship = self.visa_status not in (
            "singapore_citizen",
            "permanent_resident",
        )
        return self
