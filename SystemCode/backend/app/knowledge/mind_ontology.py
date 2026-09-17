from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
from typing import Mapping

from app.core.config import settings


@dataclass(frozen=True)
class MindSkill:
    name: str
    synonyms: tuple[str, ...]
    types: tuple[str, ...]
    relations: Mapping[str, tuple[str, ...]]


@dataclass(frozen=True)
class MindConcept:
    name: str
    synonyms: tuple[str, ...]
    categories: tuple[str, ...]


@dataclass(frozen=True)
class MindKnowledgeGraphStats:
    skill_count: int
    concept_count: int
    relation_count: int
    unresolved_implied_skill_reference_count: int


class MindKnowledgeGraph:
    def __init__(
        self,
        skills: tuple[MindSkill, ...],
        concepts: tuple[MindConcept, ...],
    ) -> None:
        self.skills = skills
        self.concepts = concepts
        self._skills_by_name = {self._key(skill.name): skill for skill in skills}
        self._concepts_by_name = {self._key(concept.name): concept for concept in concepts}
        self._skill_aliases = self._build_skill_alias_index(skills)
        self._concept_aliases = self._build_concept_alias_index(concepts)
        self.stats = MindKnowledgeGraphStats(
            skill_count=len(skills),
            concept_count=len(concepts),
            relation_count=sum(
                len(values)
                for skill in skills
                for values in skill.relations.values()
            ),
            unresolved_implied_skill_reference_count=len(
                self.unresolved_implied_skill_references()
            ),
        )

    @classmethod
    def from_files(cls, skills_path: Path, concepts_path: Path) -> "MindKnowledgeGraph":
        skill_records = cls._load_records(skills_path)
        concept_records = cls._load_records(concepts_path)
        skills = tuple(cls._parse_skill(record) for record in skill_records)
        concepts = tuple(cls._parse_concept(record) for record in concept_records)
        return cls(skills=skills, concepts=concepts)

    def get_skill(self, name_or_alias: str) -> MindSkill | None:
        canonical_key = self._skill_aliases.get(self._key(name_or_alias))
        if canonical_key is None:
            return None
        return self._skills_by_name[canonical_key]

    def get_concept(self, name_or_alias: str) -> MindConcept | None:
        lookup_key = self._key(name_or_alias)
        exact_match = self._concepts_by_name.get(lookup_key)
        if exact_match is not None:
            return exact_match

        canonical_keys = self._concept_aliases.get(lookup_key, ())
        if len(canonical_keys) != 1:
            return None
        return self._concepts_by_name[canonical_keys[0]]

    def get_concepts(self, name_or_alias: str) -> tuple[MindConcept, ...]:
        lookup_key = self._key(name_or_alias)
        exact_match = self._concepts_by_name.get(lookup_key)
        if exact_match is not None:
            return (exact_match,)

        canonical_keys = self._concept_aliases.get(lookup_key, ())
        return tuple(self._concepts_by_name[key] for key in canonical_keys)

    def related_skills(self, skill_name_or_alias: str, relation: str) -> tuple[str, ...]:
        skill = self.get_skill(skill_name_or_alias)
        if skill is None:
            return ()
        return skill.relations.get(relation, ())

    def unresolved_implied_skill_references(self) -> tuple[tuple[str, str], ...]:
        unresolved: list[tuple[str, str]] = []
        for skill in self.skills:
            for reference in skill.relations.get("impliesKnowingSkills", ()):
                if self.get_skill(reference) is None:
                    unresolved.append((skill.name, reference))
        return tuple(unresolved)

    @staticmethod
    def _load_records(path: Path) -> list[dict[str, object]]:
        if not path.is_file():
            raise FileNotFoundError(f"找不到 MIND 数据文件：{path}")

        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError(f"MIND 数据文件顶层必须是数组：{path}")

        records: list[dict[str, object]] = []
        for index, item in enumerate(payload):
            if not isinstance(item, dict):
                raise ValueError(f"MIND 数据第 {index} 项不是对象：{path}")
            records.append(item)
        return records

    @classmethod
    def _parse_skill(cls, record: dict[str, object]) -> MindSkill:
        name = cls._required_text(record, "name")
        synonyms = cls._text_tuple(record.get("synonyms"))
        types = cls._text_tuple(record.get("type"))
        relations = {
            key: cls._text_tuple(value)
            for key, value in record.items()
            if key not in {"name", "synonyms", "type"} and value is not None
        }
        return MindSkill(
            name=name,
            synonyms=synonyms,
            types=types,
            relations=relations,
        )

    @classmethod
    def _parse_concept(cls, record: dict[str, object]) -> MindConcept:
        return MindConcept(
            name=cls._required_text(record, "name"),
            synonyms=cls._text_tuple(record.get("synonyms")),
            categories=cls._text_tuple(record.get("category")),
        )

    @classmethod
    def _build_skill_alias_index(
        cls,
        skills: tuple[MindSkill, ...],
    ) -> dict[str, str]:
        aliases: dict[str, str] = {}
        for skill in skills:
            canonical_key = cls._key(skill.name)
            for alias in (skill.name, *skill.synonyms):
                alias_key = cls._key(alias)
                existing = aliases.get(alias_key)
                if existing is not None and existing != canonical_key:
                    raise ValueError(f"MIND 技能别名冲突：{alias}")
                aliases[alias_key] = canonical_key
        return aliases

    @classmethod
    def _build_concept_alias_index(
        cls,
        concepts: tuple[MindConcept, ...],
    ) -> dict[str, tuple[str, ...]]:
        aliases: dict[str, list[str]] = {}
        for concept in concepts:
            canonical_key = cls._key(concept.name)
            for alias in (concept.name, *concept.synonyms):
                alias_key = cls._key(alias)
                candidates = aliases.setdefault(alias_key, [])
                if canonical_key not in candidates:
                    candidates.append(canonical_key)
        return {key: tuple(values) for key, values in aliases.items()}

    @staticmethod
    def _required_text(record: dict[str, object], key: str) -> str:
        value = record.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"MIND 数据缺少有效字段：{key}")
        return value.strip()

    @staticmethod
    def _text_tuple(value: object) -> tuple[str, ...]:
        if value is None:
            return ()
        if isinstance(value, str):
            return (value.strip(),) if value.strip() else ()
        if not isinstance(value, list):
            raise ValueError("MIND 关系字段必须是字符串或数组")

        result: list[str] = []
        for item in value:
            if not isinstance(item, str):
                raise ValueError("MIND 关系数组只能包含字符串")
            if item.strip():
                result.append(item.strip())
        return tuple(result)

    @staticmethod
    def _key(value: str) -> str:
        return value.strip().casefold()


@lru_cache(maxsize=1)
def get_mind_knowledge_graph() -> MindKnowledgeGraph:
    return MindKnowledgeGraph.from_files(
        skills_path=settings.mind_skills_path,
        concepts_path=settings.mind_concepts_path,
    )
