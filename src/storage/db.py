import sqlite3
import json
from pathlib import Path
from typing import List
from src.api.base_api import Paper
from src.cli.project import Project
from src.storage.init_db import create_tables


# TODO: add tests
def get_db_path(project: Project) -> Path:
    return project.path / "iwadi.db"


def save_paper_in_db(paper: Paper, project: Project, pdf_path: Path) -> None:
    db_path = get_db_path(project)
    create_tables(db_path)  # auto-init if not present

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO papers (
                id, title, authors, abstract,
                pdf_path, publication_date,
                source, doi, citation_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                paper.id,
                paper.title,
                json.dumps(paper.authors),
                paper.abstract,
                str(pdf_path),
                paper.publication_date.isoformat() if paper.publication_date else None,
                paper.source,
                paper.doi,
                paper.citation_count or 0,
            ),
        )
        conn.commit()


def get_papers(project: Project) -> List[Paper]:
    db_path = get_db_path(project)
    create_tables(db_path)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM papers")
        rows = cursor.fetchall()

    papers = []
    for row in rows:
        papers.append(
            Paper(
                id=row[0],
                title=row[1],
                authors=json.loads(row[2]),
                abstract=row[3],
                pdf_url=None,  # not stored, only local path
                publication_date=None if not row[5] else row[5],
                source=row[6],
                doi=row[7],
                citation_count=row[8],
            )
        )
    return papers
