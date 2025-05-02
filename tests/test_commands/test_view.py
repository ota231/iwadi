import pytest
from unittest import mock
from click.testing import CliRunner
from src.cli.commands.view import view
from pathlib import Path


@pytest.fixture
def runner() -> CliRunner:
    """Fixture to provide a CLI runner for testing."""
    return CliRunner()


def test_view_command_basic(runner: CliRunner) -> None:
    """Basic test for the view command to ensure it runs without errors."""

    # Mock the active project and metadata.db
    active_project = mock.Mock()
    active_project.name = "test_project"
    active_project.path = Path("/mock/path/to/test_project")

    # Create a mock for metadata.db existence
    metadata_db = active_project.path / "metadata.db"

    with mock.patch("pathlib.Path.exists", return_value=True):
        # Create a mock IwadiContext object
        iwadi_ctx = mock.Mock()
        iwadi_ctx.active_project = active_project

        # Mock subprocess.run to prevent actual command execution
        with mock.patch("subprocess.run") as mock_subprocess:
            # Invoke the view command with the mocked context
            result = runner.invoke(view, obj=iwadi_ctx)

            # Assert subprocess.run is called as expected
            mock_subprocess.assert_called_once_with(
                ["datasette", str(metadata_db)], check=True
            )

            # Assert the command ran successfully
            assert result.exit_code == 0
            assert "Launching Datasette for project: test_project" in result.output
