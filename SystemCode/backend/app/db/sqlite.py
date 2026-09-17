from pathlib import Path
import sqlite3


BACKEND_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = BACKEND_ROOT / "data" / "careerpilot.db"
SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    target_path = db_path or DEFAULT_DB_PATH
    target_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(target_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(db_path: Path | None = None) -> None:
    with connect(db_path) as connection:
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        connection.execute("DROP INDEX IF EXISTS idx_jobs_deadline_at")
        for column_name in ("deadline_at", "posted_at"):
            _drop_column_if_exists(connection, "jobs", column_name)
        for column_name in ("required_languages_json", "location_json", "min_experience_years"):
            _drop_column_if_exists(connection, "job_analysis", column_name)


def _drop_column_if_exists(connection: sqlite3.Connection, table_name: str, column_name: str) -> None:
    columns = {
        row["name"]
        for row in connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    }
    if column_name in columns:
        connection.execute(f"ALTER TABLE {table_name} DROP COLUMN {column_name}")
