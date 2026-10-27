import json
from pathlib import Path

from typer.testing import CliRunner

from agency_agents.cli.main import app

runner = CliRunner()

AGENT_MD = """---
name: {name}
description: Test agent for CLI integration coverage.
version: 1.0.0
---
Body of {name}
"""

TOOLS_DATA = {
    "tools": {
        "claude-code": {
            "id": "cc", "label": "Claude Code", "short": "Claude", "kebab": "claude-code",
            "accent": "#000", "icon": None, "order": 1,
            "scope": {"user": True, "project": True},
            "detect": {"dirs": [], "agentsDir": None},
            "version": {"bin": "claude", "args": []},
            "format": "identity", "installKind": "per-agent", "slugFrom": "source",
            "dest": {"user": [".claude/agents/{slug}.md"], "project": [".claude/agents/{slug}.md"]},
        },
        "aider": {
            "id": "aider", "label": "Aider", "short": "Aider", "kebab": "aider",
            "accent": "#000", "icon": None, "order": 2,
            "scope": {"user": False, "project": True},
            "detect": {"dirs": [], "agentsDir": None},
            "version": {"bin": "aider", "args": []},
            "format": "aider-conventions", "installKind": "roster", "slugFrom": None,
            "dest": {"user": [], "project": ["CONVENTIONS.md"]},
        },
    }
}

DIVISIONS_DATA = {
    "divisions": {
        "engineering": {"label": "Engineering", "icon": "e", "color": "#000000"},
        "marketing": {"label": "Marketing", "icon": "m", "color": "#000000"},
    }
}


def write_agent(dir_path: Path, slug: str, name: str):
    dir_path.mkdir(parents=True, exist_ok=True)
    (dir_path / f"{slug}.md").write_text(AGENT_MD.format(name=name), encoding="utf-8")


def seeded_root(tmp_path: Path) -> Path:
    (tmp_path / "tools.json").write_text(json.dumps(TOOLS_DATA), encoding="utf-8")
    (tmp_path / "divisions.json").write_text(json.dumps(DIVISIONS_DATA), encoding="utf-8")
    write_agent(tmp_path / "engineering", "code-reviewer", "Code Reviewer")
    write_agent(tmp_path / "engineering", "devops-automator", "DevOps Automator")
    write_agent(tmp_path / "marketing", "growth-hacker", "Growth Hacker")
    return tmp_path


def run_in_root(tmp_path: Path, args: list, monkeypatch=None):
    root = seeded_root(tmp_path)
    import os
    cwd = os.getcwd()
    os.chdir(root)
    try:
        if monkeypatch is not None:
            # Defensive sandbox: even a test that mis-targets the user scope
            # can never write outside tmp_path.
            monkeypatch.setenv("HOME", str(root))
            monkeypatch.setenv("USERPROFILE", str(root))
        return runner.invoke(app, args, catch_exceptions=False)
    finally:
        os.chdir(cwd)


def test_dry_run_writes_nothing(tmp_path, monkeypatch):
    result = run_in_root(tmp_path, ["install", "--no-interactive", "--dry-run"], monkeypatch)
    assert result.exit_code == 0, result.output
    assert (tmp_path / ".claude").exists() is False
    assert "claude-code" in result.output
    assert "3 agents" in result.output
    assert "nothing written" in result.output


def test_dry_run_with_division_filter_counts_subset(tmp_path, monkeypatch):
    result = run_in_root(tmp_path, ["install", "--no-interactive", "--tool", "claude-code", "--division", "marketing", "--dry-run"], monkeypatch)
    assert result.exit_code == 0, result.output
    assert "1 agents" in result.output
    assert (tmp_path / ".claude").exists() is False


def test_install_by_division_writes_only_selected(tmp_path, monkeypatch):
    result = run_in_root(tmp_path, ["install", "--no-interactive", "--scope", "project", "--tool", "claude-code", "--division", "engineering"], monkeypatch)
    assert result.exit_code == 0, result.output
    agents_dir = tmp_path / ".claude" / "agents"
    installed = sorted(f.name for f in agents_dir.iterdir())
    assert installed == ["code-reviewer.md", "devops-automator.md"]


def test_install_by_agent_display_name(tmp_path, monkeypatch):
    result = run_in_root(tmp_path, ["install", "--no-interactive", "--scope", "project", "--tool", "claude-code", "--agent", "Growth Hacker"], monkeypatch)
    assert result.exit_code == 0, result.output
    installed = sorted(f.name for f in (tmp_path / ".claude" / "agents").iterdir())
    assert installed == ["growth-hacker.md"]


def test_install_agents_file_with_comments(tmp_path, monkeypatch):
    f = tmp_path / "team.txt"
    f.write_text("# sprint team\nCode Reviewer\n# next sprint\ngrowth-hacker\n", encoding="utf-8")
    result = run_in_root(tmp_path, ["install", "--no-interactive", "--scope", "project", "--tool", "claude-code", "--agents-file", "team.txt"], monkeypatch)
    assert result.exit_code == 0, result.output
    installed = sorted(f.name for f in (tmp_path / ".claude" / "agents").iterdir())
    assert installed == ["code-reviewer.md", "growth-hacker.md"]


def test_install_unknown_agent_exits_1(tmp_path, monkeypatch):
    result = run_in_root(tmp_path, ["install", "--no-interactive", "--tool", "claude-code", "--agent", "ghost"], monkeypatch)
    assert result.exit_code == 1
    assert "ghost" in result.output
    assert (tmp_path / ".claude").exists() is False


def test_list_teams_shows_counts(tmp_path):
    result = run_in_root(tmp_path, ["install", "--list", "teams"])
    assert result.exit_code == 0, result.output
    assert "engineering" in result.output and "marketing" in result.output
    assert "2 agents" in result.output
    assert "1 agents" in result.output


def test_list_agents_prints_slugs(tmp_path):
    result = run_in_root(tmp_path, ["install", "--list", "agents"])
    assert result.exit_code == 0, result.output
    assert " growth-hacker" in result.output
    assert "code-reviewer" in result.output


def test_list_all_shows_tools_and_teams(tmp_path):
    result = run_in_root(tmp_path, ["install", "--list", "all"])
    assert result.exit_code == 0, result.output
    assert "Tools (2)" in result.output
    assert "Teams (2)" in result.output


def test_list_unknown_value_exits_1(tmp_path):
    result = run_in_root(tmp_path, ["install", "--list", "bogus"])
    assert result.exit_code == 1
