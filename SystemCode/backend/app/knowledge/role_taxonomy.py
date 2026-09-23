from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from app.schemas.profile import TARGET_ROLE_CATEGORIES, TARGET_ROLES


@dataclass(frozen=True)
class RoleProfile:
    role: str
    category: str
    aliases: tuple[str, ...]
    description: str
    typical_skills: tuple[str, ...]

    def embedding_text(self) -> str:
        return "\n".join(
            (
                f"Role: {self.role}",
                f"Category: {self.category}",
                f"Aliases: {', '.join(self.aliases)}",
                f"Description: {self.description}",
                f"Typical skills: {', '.join(self.typical_skills)}",
            )
        )


class RoleTaxonomy:
    def __init__(self, profiles: list[RoleProfile], source_hash: str) -> None:
        self.profiles = profiles
        self.source_hash = source_hash
        self.by_role = {profile.role: profile for profile in profiles}

    @classmethod
    def load(cls, path: Path) -> "RoleTaxonomy":
        raw = path.read_bytes()
        payload = json.loads(raw)
        profiles = [
            RoleProfile(
                role=item["role"],
                category=item["category"],
                aliases=tuple(item.get("aliases", [])),
                description=item["description"],
                typical_skills=tuple(item.get("typical_skills", [])),
            )
            for item in payload
        ]
        cls._validate(profiles)
        return cls(profiles, hashlib.sha256(raw).hexdigest())

    @staticmethod
    def _validate(profiles: list[RoleProfile]) -> None:
        roles = [profile.role for profile in profiles]
        if len(roles) != len(set(roles)):
            raise ValueError("role taxonomy contains duplicate role names")
        if set(roles) != set(TARGET_ROLES):
            missing = sorted(set(TARGET_ROLES) - set(roles))
            extra = sorted(set(roles) - set(TARGET_ROLES))
            raise ValueError(f"role taxonomy differs from TARGET_ROLES; missing={missing}, extra={extra}")
        for profile in profiles:
            expected = next(
                category
                for category, category_roles in TARGET_ROLE_CATEGORIES.items()
                if profile.role in category_roles
            )
            if profile.category != expected:
                raise ValueError(f"invalid category for {profile.role}: {profile.category}")
            if not profile.description.strip():
                raise ValueError(f"missing description for {profile.role}")
