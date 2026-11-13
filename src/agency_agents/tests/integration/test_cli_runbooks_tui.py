"""Runbook installation, the lint gate's exit codes, and the console entry point.

Three contracts are pinned here, each closing a defect recorded in
`docs/dx/baseline.md`:

- D1: `pyproject.toml` `[project.scripts]` resolved a callable that did not
  exist, so the installed `agency-agents` command raised ImportError while 222
  tests passed. The entry point is now asserted against the real pyproject.
- D2: `lint` printed catalog errors and exited 0, so the CI gate reported red
  text and green status. Both catalogs are asserted to be fatal.
- Issue #14: runbooks had no installation path through the CLI.
"""

from __future__ import annotations

import importlib
import json
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from agency_agents import __version__
from agency_agents.cli.main import app

runner = CliRunner()

REPO_ROOT = Path(__file__).resolve().parents[4]


def tool(kebab: str, user: list[str], order: int = 1) -> dict[str, Any]:
    return {
        "id": kebab,
        "label": kebab.upper(),
        "short": kebab,
        "kebab": kebab,
        "accent": "#000000",
        "icon": None,
        "order": order,
        "scope": {"user": True, "project": False},
        "detect": {"dirs": [], "agentsDir": None},
        "version": {"bin": kebab, "args": []},
        "format": "identity",
        "installKind": "per-agent",
        "slugFrom": "name",
        "dest": {"user": user, "project": []},
    }


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def write_agent(root: Path, division: str, slug: str, name: str) -> None:
    directory = root / division
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{slug}.md").write_text(
        f"---\nname: {name}\ndescription: Fixture agent.\n---\nBody of {name}\n",
        encoding="utf-8",
    )


RUNBOOKS = {
    "_note": "fixture",
    "runbooks": [
        {
            "slug": "delivery-sprint",
            "title": "Delivery Sprint",
            "mode": "NEXUS-Sprint",
            "duration": "6 weeks",
            "summary": "A fixture runbook with two activation groups.",
            "doc": "strategy/runbooks/scenario-delivery-sprint.md",
            "roster": [
                {
                    "group": "Core Team",
                    "activation": "always",
                    "agents": [
                        "agents-orchestrator",
                        "backend-architect",
                        "frontend-developer",
                    ],
                },
                {
                    "group": "Growth Team",
                    "activation": "week 3+",
                    "agents": ["growth-hacker"],
                },
            ],
        }
    ],
}


def runbook(
    slug: str,
    *,
    title: str = "Late Sprint",
    mode: str = "NEXUS-Micro",
    duration: str = "1 week",
    roster: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a runbook entry; the roster defaults to a valid orchestrator-only set."""
    return {
        "slug": slug,
        "title": title,
        "mode": mode,
        "duration": duration,
        "summary": "Fixture runbook.",
        "doc": f"strategy/runbooks/scenario-{slug}.md",
        "roster": (
            roster
            if roster is not None
            else [
                {
                    "group": "Command",
                    "activation": "always",
                    "agents": ["agents-orchestrator"],
                }
            ]
        ),
    }


def write_runbooks(repo: Path, entries: list[dict[str, Any]]) -> None:
    """Write the runbook registry and the docs it points at.

    The consistency check requires every registered doc to exist: a roster whose
    prose is missing installs agents nobody can read about.
    """
    write_json(repo / "strategy" / "runbooks.json", {"_note": "fixture", "runbooks": entries})
    for entry in entries:
        doc = repo / entry["doc"]
        doc.parent.mkdir(parents=True, exist_ok=True)
        doc.write_text(f"# {entry['title']}\n", encoding="utf-8")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    write_json(
        tmp_path / "tools.json",
        {"tools": {"claude-code": tool("claude-code", [".claude/agents/{slug}.md"])}},
    )
    write_json(
        tmp_path / "divisions.json",
        {
            "divisions": {
                "engineering": {"label": "Engineering", "icon": "e", "color": "#000000"},
                "marketing": {"label": "Marketing", "icon": "m", "color": "#000000"},
            }
        },
    )
    write_json(tmp_path / "strategy" / "runbooks.json", RUNBOOKS)
    # The consistency check requires every registered doc to exist: a roster whose
    # prose is missing installs agents nobody can read about.
    for runbook_entry in RUNBOOKS["runbooks"]:
        doc = tmp_path / runbook_entry["doc"]
        doc.parent.mkdir(parents=True, exist_ok=True)
        doc.write_text(f"# {runbook_entry['title']}\n", encoding="utf-8")
    write_agent(tmp_path, "engineering", "agents-orchestrator", "Agents Orchestrator")
    write_agent(tmp_path, "engineering", "backend-architect", "Backend Architect")
    write_agent(tmp_path, "engineering", "frontend-developer", "Frontend Developer")
    write_agent(tmp_path, "marketing", "growth-hacker", "Growth Hacker")
    return tmp_path


def invoke(repo: Path, args: list[str], monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(repo)
    monkeypatch.setenv("HOME", str(repo / "home"))
    monkeypatch.setenv("USERPROFILE", str(repo / "home"))
    return runner.invoke(app, args, catch_exceptions=False)


# ------------------------------------------------------- issue #14: --list runbooks


def test_list_runbooks_prints_slug_mode_duration_count_and_doc(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    result = invoke(repo, ["install", "--list", "runbooks"], monkeypatch)

    assert result.exit_code == 0
    assert "delivery-sprint" in result.output
    assert "NEXUS-Sprint" in result.output
    assert "6 weeks" in result.output
    assert "4 agents" in result.output
    assert "strategy/runbooks/scenario-delivery-sprint.md" in result.output


def test_list_runbooks_is_sorted_by_slug(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    write_runbooks(
        repo,
        [runbook("zzz-late"), RUNBOOKS["runbooks"][0]],
    )

    result = invoke(repo, ["install", "--list", "runbooks"], monkeypatch)

    assert result.exit_code == 0
    assert result.output.index("delivery-sprint") < result.output.index("zzz-late")


def test_unknown_list_value_names_runbooks_as_an_option(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    result = invoke(repo, ["install", "--list", "nope"], monkeypatch)

    assert result.exit_code == 1
    assert "runbooks" in result.output


def test_list_help_documents_runbooks(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    result = invoke(repo, ["install", "--help"], monkeypatch)

    assert "runbooks" in result.output


# ------------------------------------------------------- issue #14: --runbook install


def test_runbook_dry_run_resolves_every_activation_group(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    result = invoke(
        repo,
        ["install", "--runbook", "delivery-sprint", "--tool", "claude-code", "--dry-run"],
        monkeypatch,
    )

    assert result.exit_code == 0
    # Every roster agent, including the week 3+ group: activation is a NEXUS
    # scheduling concept, not an install filter.
    assert "4 agents" in result.output
    assert "Core Team" in result.output
    assert "Growth Team" in result.output
    assert "week 3+" in result.output
    assert not (repo / "home" / ".claude").exists()


def test_runbook_installs_every_roster_agent(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    result = invoke(
        repo,
        ["install", "--runbook", "delivery-sprint", "--tool", "claude-code"],
        monkeypatch,
    )

    assert result.exit_code == 0
    written = sorted(p.name for p in (repo / "home" / ".claude" / "agents").glob("*.md"))
    assert written == [
        "agents-orchestrator.md",
        "backend-architect.md",
        "frontend-developer.md",
        "growth-hacker.md",
    ]


def test_runbook_is_a_selector_and_rejects_division(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    result = invoke(
        repo,
        ["install", "--runbook", "delivery-sprint", "--division", "engineering"],
        monkeypatch,
    )

    assert result.exit_code == 1
    assert "--division" in result.output
    assert "Pick one selector" in result.output


def test_runbook_is_a_selector_and_rejects_agent(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    result = invoke(
        repo,
        ["install", "--runbook", "delivery-sprint", "--agent", "growth-hacker"],
        monkeypatch,
    )

    assert result.exit_code == 1
    assert "--agent" in result.output


def test_runbook_is_a_selector_and_rejects_agents_file(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    listing = repo / "team.txt"
    listing.write_text("growth-hacker\n", encoding="utf-8")

    result = invoke(
        repo,
        ["install", "--runbook", "delivery-sprint", "--agents-file", str(listing)],
        monkeypatch,
    )

    assert result.exit_code == 1
    assert "--agents-file" in result.output


def test_unknown_runbook_exits_1_and_points_at_the_listing(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    result = invoke(repo, ["install", "--runbook", "no-such-runbook"], monkeypatch)

    assert result.exit_code == 1
    assert "Unknown runbook" in result.output
    assert "--list" in result.output
    assert "runbooks" in result.output


def test_runbook_with_an_empty_roster_is_an_error(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write_runbooks(repo, [runbook("empty-sprint", roster=[])])

    result = invoke(repo, ["install", "--runbook", "empty-sprint"], monkeypatch)

    assert result.exit_code == 1
    assert "declares no agents" in result.output


def test_runbook_forces_the_non_interactive_path(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Without the guard, --runbook would fall into the interactive wizard."""
    result = invoke(
        repo,
        ["install", "--runbook", "delivery-sprint", "--tool", "claude-code", "--dry-run"],
        monkeypatch,
    )

    assert result.exit_code == 0
    assert "Dry run complete" in result.output


# ------------------------------------------------- D2: the lint gate must gate


def test_lint_fails_on_a_tool_with_no_renderer(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The defect: lint printed the error and exited 0, so CI never saw it."""
    tools = json.loads((repo / "tools.json").read_text(encoding="utf-8"))
    tools["tools"]["broken"] = tool("broken", [".broken/{slug}.md"], order=9)
    tools["tools"]["broken"]["format"] = "no-such-format"
    write_json(repo / "tools.json", tools)

    result = invoke(repo, ["lint"], monkeypatch)

    assert "Tools Consistency Errors" in result.output
    assert result.exit_code == 1


def test_lint_fails_on_an_undeclared_division(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    divisions = json.loads((repo / "divisions.json").read_text(encoding="utf-8"))
    del divisions["divisions"]["marketing"]
    write_json(repo / "divisions.json", divisions)

    result = invoke(repo, ["lint"], monkeypatch)

    assert "Division Consistency Errors" in result.output
    assert result.exit_code == 1


def test_lint_fails_on_an_inconsistent_runbook(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runbooks = json.loads((repo / "strategy" / "runbooks.json").read_text(encoding="utf-8"))
    runbooks["runbooks"][0]["roster"][0]["agents"] = ["ghost-agent"]
    write_json(repo / "strategy" / "runbooks.json", runbooks)

    result = invoke(repo, ["lint"], monkeypatch)

    assert result.exit_code == 1


def test_lint_passes_on_a_consistent_repository(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    result = invoke(repo, ["lint"], monkeypatch)

    assert result.exit_code == 0
    assert "All agents passed linting." in result.output


# ------------------------------------------------- D1: the console entry point


def test_declared_console_script_resolves_to_a_callable() -> None:
    """Guards the exact defect: a script entry naming an attribute that is absent."""
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    scripts = pyproject["project"]["scripts"]

    assert "agency-agents" in scripts
    target = scripts["agency-agents"]
    module_path, _, attribute = target.partition(":")
    assert module_path and attribute, f"entry point {target!r} is not 'module:callable'"

    module = importlib.import_module(module_path)
    resolved = getattr(module, attribute, None)

    assert resolved is not None, (
        f"pyproject.toml declares {target!r} but {module_path}.{attribute} does not exist"
    )
    assert callable(resolved), f"{target!r} resolves to a non-callable"


def test_module_entry_point_answers_help() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "agency_agents", "--help"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    assert result.returncode == 0
    assert "Agency Agents Management Tool" in result.stdout


def test_installed_console_script_answers_help() -> None:
    """Runs the real installed binary when the environment provides one."""
    binary = shutil.which("agency-agents")
    if binary is None:
        pytest.skip("the console script is not installed in this environment")
    result = subprocess.run([binary, "--help"], capture_output=True, text=True)

    assert result.returncode == 0, result.stderr
    assert "Agency Agents Management Tool" in result.stdout


def test_module_entry_point_no_args_exits_zero() -> None:
    """A bare `agency-agents` is help with exit 0, not a "Missing command" (exit 2)."""
    result = subprocess.run(
        [sys.executable, "-m", "agency_agents"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    assert result.returncode == 0, result.stderr
    assert "Agency Agents Management Tool" in result.stdout


def test_version_flag_prints_version() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "agency_agents", "--version"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    assert result.returncode == 0, result.stderr
    assert __version__ in result.stdout


def test_short_version_flag_prints_version() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "agency_agents", "-v"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    assert result.returncode == 0, result.stderr
    assert __version__ in result.stdout


def test_short_help_flag_prints_help() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "agency_agents", "-h"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    assert result.returncode == 0, result.stderr
    assert "Agency Agents Management Tool" in result.stdout
