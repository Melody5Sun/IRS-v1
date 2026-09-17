import re

from app.parsers.job_skill_lexicon import SKILL_SYNONYMS


def find_job_skill_matches(text: str) -> list[tuple[str, str]]:
    normalized_text = text.lower()
    matches: dict[str, str] = {}
    for skill, aliases in SKILL_SYNONYMS.items():
        for alias in aliases:
            # 技能别名自身可以包含句点，边界只阻止它嵌入更长的单词或技术名称。
            pattern = rf"(?<![\w+#]){re.escape(alias.lower())}(?![\w+#])"
            if re.search(pattern, normalized_text):
                matches[skill] = alias
                break
    return sorted(matches.items())
