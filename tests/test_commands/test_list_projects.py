import subprocess


def test_list_projects() -> None:
    subprocess.run(["iwadi", "create-project", "ProjectA"], capture_output=True)
    result = subprocess.run(["iwadi", "list-projects"], capture_output=True, text=True)

    assert result.returncode == 0
    assert "ProjectA" in result.stdout


# TODO: CLI Runner
