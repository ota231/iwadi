import sqlite3
from pathlib import Path

CREATE_PAPERS_TABLE = """
CREATE TABLE IF NOT EXISTS papers (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    authors TEXT NOT NULL,
    abstract TEXT NOT NULL,
    pdf_path TEXT,
    publication_date TEXT,
    source TEXT NOT NULL,
    doi TEXT,
    citation_count INTEGER DEFAULT 0
);
"""


def create_tables(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(CREATE_PAPERS_TABLE)
        conn.commit()
