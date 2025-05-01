import pytest
import subprocess
import shutil
from pathlib import Path
from typing import Generator


@pytest.fixture
def iwadi_project() -> Generator:
    """create appropriate context for test"""
    project_name = "TestProject"
    projects_dir = Path.home() / "iwadi_projects"
    project_dir = projects_dir / project_name

    yield project_name  # provide test function with the project name, then run test
    if project_dir.exists():
        shutil.rmtree(project_dir, ignore_errors=True)


def test_create_project(iwadi_project: str) -> None:
    result = subprocess.run(
        ["iwadi", "create-project", iwadi_project],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"Command failed: {result.stderr}"

    project_dir = Path.home() / "iwadi_projects" / iwadi_project
    assert project_dir.exists(), f"Project dir {project_dir} not found!"


# TODO: CLI Runner
# TODO: Error handling, if project already exists/directory not accessible
# TODO: Custom directory creation works
