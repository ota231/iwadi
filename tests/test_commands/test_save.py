import subprocess


def test_save_with_interactive() -> None:
    result = subprocess.run(
        ["iwadi", "save", "--interactive", "--project", "ProjectA"],
        input="1\n",  # simulate selecting the first paper
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Saved" in result.stdout or "✓" in result.stdout


# TODO: CLI Runner
# TODO: Check if the papers are actually saved in the directory
# TODO: Check specifying a project works by saving to specified project directory
# TODO: Check if not specifying a project works by saving to "active" project directory
