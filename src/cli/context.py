from typing import Optional
from pathlib import Path
from src.cli.project import Project


class IwadiContext:
    def __init__(self) -> None:
        self.active_project: Optional[Project] = None

    def set_project(self, project: Project) -> None:
        """Safely set the active project."""
        self.active_project = project

    def get_papers_path(self) -> Path:
        """Get papers path with validation."""
        if not self.active_project:
            raise ValueError("No active project set")
        return self.active_project.papers_path
