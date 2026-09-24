from datetime import datetime
import json
from pathlib import Path
import sqlite3

from app.db.sqlite import connect, initialize_database
from app.schemas.interview_question import InterviewQuestion


class InterviewQuestionRepository:
    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path
        # 延迟到第一次真正访问数据库时才建表/迁移，避免 import app 时就改写 data/careerpilot.db
        self._initialized = False

    def _connect(self) -> sqlite3.Connection:
        if not self._initialized:
            initialize_database(self.db_path)
            self._initialized = True
        return connect(self.db_path)

    def upsert_many(self, questions: list[InterviewQuestion]) -> int:
        changed_count = 0
        with self._connect() as connection:
            for question in questions:
                existing = connection.execute(
                    "SELECT question_text FROM interview_questions WHERE source = ? AND external_id = ?",
                    (question.source, question.external_id),
                ).fetchone()
                if existing is None or existing["question_text"] != question.question_text:
                    changed_count += 1

                connection.execute(
                    """
                    INSERT INTO interview_questions (
                        source, external_id, question_text, standard_answer,
                        question_text_en, standard_answer_en, roles_json,
                        difficulty_level, company, collected_at,
                        question_embedding_json, skills_json, keywords_json
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(source, external_id) DO UPDATE SET
                        question_text = excluded.question_text,
                        standard_answer = excluded.standard_answer,
                        question_text_en = excluded.question_text_en,
                        standard_answer_en = excluded.standard_answer_en,
                        roles_json = excluded.roles_json,
                        difficulty_level = excluded.difficulty_level,
                        company = excluded.company,
                        collected_at = excluded.collected_at,
                        question_embedding_json = excluded.question_embedding_json,
                        skills_json = excluded.skills_json,
                        keywords_json = excluded.keywords_json
                    """,
                    (
                        question.source,
                        question.external_id,
                        question.question_text,
                        question.standard_answer,
                        question.question_text_en,
                        question.standard_answer_en,
                        json.dumps(question.roles, ensure_ascii=False),
                        question.difficulty_level,
                        question.company,
                        question.collected_at.isoformat(),
                        json.dumps(question.question_embedding) if question.question_embedding else None,
                        json.dumps(question.skills, ensure_ascii=False),
                        json.dumps(question.keywords, ensure_ascii=False),
                    ),
                )
        return changed_count

    def list_questions(self, company: str | None = None, limit: int = 100) -> list[InterviewQuestion]:
        query = "SELECT * FROM interview_questions"
        params: list[str | int] = []
        if company:
            query += " WHERE company = ?"
            params.append(company)
        query += " ORDER BY collected_at DESC LIMIT ?"
        params.append(limit)

        with self._connect() as connection:
            rows = connection.execute(query, params).fetchall()
        return [self._row_to_question(row) for row in rows]

    def count(self) -> int:
        with self._connect() as connection:
            row = connection.execute("SELECT COUNT(*) AS count FROM interview_questions").fetchone()
        return int(row["count"])

    def _row_to_question(self, row) -> InterviewQuestion:
        return InterviewQuestion(
            id=row["id"],
            source=row["source"],
            external_id=row["external_id"],
            question_text=row["question_text"],
            standard_answer=row["standard_answer"],
            question_text_en=row["question_text_en"],
            standard_answer_en=row["standard_answer_en"],
            roles=json.loads(row["roles_json"]),
            difficulty_level=row["difficulty_level"],
            company=row["company"],
            collected_at=datetime.fromisoformat(row["collected_at"]),
            question_embedding=json.loads(row["question_embedding_json"]) if row["question_embedding_json"] else None,
            skills=json.loads(row["skills_json"]),
            keywords=json.loads(row["keywords_json"]),
        )
