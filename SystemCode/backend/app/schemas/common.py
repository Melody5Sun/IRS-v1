from typing import Literal

from pydantic import BaseModel


VisaStatus = Literal["singapore_citizen", "student_pass", "permanent_resident", "not_stated"]
EmploymentType = Literal["internship", "full_time", "part_time", "contract", "freelance", "not_stated"]
SkillLevel = Literal["beginner", "intermediate", "advanced", "expert", "not_stated"]
LanguageLevel = Literal["native", "fluent", "intermediate", "basic", "not_stated"]
Degree = Literal["bachelor", "master", "phd", "diploma", "not_applicable", "not_stated"]
EducationEntryType = Literal["degree", "exchange"]
CandidateType = Literal["student", "new_graduate", "experienced", "not_stated"]
RemotePolicy = Literal["onsite", "hybrid", "remote", "not_stated"]
VisaSponsorship = Literal["provided", "not_provided", "not_stated"]
SeniorityLevel = Literal["intern", "entry_level", "junior", "mid", "senior", "not_stated"]
RequirementImportance = Literal["required", "preferred"]
ConstraintStatus = Literal["passed", "failed", "unknown"]


class Location(BaseModel):
    city: str | None = None
    country: str | None = None


class Skill(BaseModel):
    name: str
    level: SkillLevel = "not_stated"


class Language(BaseModel):
    name: str
    level: LanguageLevel = "not_stated"
