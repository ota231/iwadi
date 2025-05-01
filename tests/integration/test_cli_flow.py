import subprocess


def test_full_cli_flow() -> None:
    subprocess.run(["iwadi", "create-project", "FlowProj"], capture_output=True)
    subprocess.run(["iwadi", "search", "deep learning"], capture_output=True)

    result = subprocess.run(
        ["iwadi", "save", "--interactive", "--project", "FlowProj"],
        input="1\n",  # simulate selecting a paper
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Saved" in result.stdout or "✓" in result.stdout


# TODO: CLI Runner
