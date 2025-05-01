from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
from typing import Dict
import json
from typing import Optional, List


@dataclass
class Project:
    name: str
    base_path: Path
    created: Optional[str] = None
    papers: Optional[List] = None

    def __post_init__(self) -> None:
        if self.created is None:
            self.created = datetime.now().isoformat()
        if self.papers is None:
            self.papers = []

    @property
    def path(self) -> Path:
        return self.base_path / self.name

    @property
    def papers_path(self) -> Path:
        return self.path / "papers"

    @property
    def notes_path(self) -> Path:
        return self.path / "notes"

    @property
    def metadata_path(self) -> Path:
        return self.path / "project_meta.json"

    def to_dict(self) -> Dict:
        return {
            "project_name": self.name,
            "created": self.created,
            "papers": self.papers,
            "paths": {
                "root": str(self.path),
                "papers": str(self.papers_path),
                "notes": str(self.notes_path),
            },
        }

    def save_metadata(self) -> None:
        """Save project metadata to file"""
        self.metadata_path.write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def from_metadata(cls, metadata_path: Path) -> "Project":
        """Load project from metadata file"""
        data = json.loads(metadata_path.read_text())
        return cls(
            name=data["project_name"],
            base_path=Path(data["paths"]["root"]).parent,
            created=data["created"],
            papers=data["papers"],
        )
