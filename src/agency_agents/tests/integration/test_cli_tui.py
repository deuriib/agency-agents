"""The `tui` command and its view layer.

`run_browser` itself opens a full-screen application and is exercised by a human,
not by pytest; what is covered here is everything around it — the command's
selection handling, its target resolution, and the pure renderer that decides
what appears on screen. That split is the point of decision D-001: the view is
thin enough that the untestable part is the terminal loop and nothing else.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from agency_agents.cli.main import app
from agency_agents.infrastructure.browser import BrowserModel, BrowserRow
from agency_agents.infrastructure.browser_app import (
    BrowserCancelled,
    render_screen,
)

runner = CliRunner()

_ANSI = re.compile(r"\x1b\[[0-9;]*m")


def plain(output: str) -> str:
    """Output with ANSI styling removed.

    Rich styles an option name character by character, so `--tool` is not a
    contiguous substring of the raw output even though it renders as one. Reading
    the styled string is how a help-surface assertion passes locally and fails in
    CI, where a terminal is attached.
    """
    return _ANSI.sub("", output)


def tool(kebab: str, user: list[str], dirs: list[str] | None = None, order: int = 1) -> dict[str, Any]:
    return {
        "id": kebab,
        "label": kebab.upper(),
        "short": kebab,
        "kebab": kebab,
        "accent": "#000000",
        "icon": None,
        "order": order,
        "scope": {"user": True, "project": False},
        "detect": {"dirs": dirs or [], "agentsDir": None},
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


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    write_json(
        tmp_path / "tools.json",
        {
            "tools": {
                "claude-code": tool(
                    "claude-code", [".claude/agents/{slug}.md"], dirs=[".claude"], order=1
                ),
                "opencode": tool(
                    "opencode", [".config/opencode/agents/{slug}.md"], dirs=[], order=2
                ),
            }
        },
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
    write_agent(tmp_path, "engineering", "backend-architect", "Backend Architect")
    write_agent(tmp_path, "engineering", "frontend-developer", "Frontend Developer")
    write_agent(tmp_path, "marketing", "growth-hacker", "Growth Hacker")
    return tmp_path


def invoke(repo: Path, args: list[str], monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(repo)
    monkeypatch.setenv("HOME", str(repo / "home"))
    monkeypatch.setenv("USERPROFILE", str(repo / "home"))
    return runner.invoke(app, args, catch_exceptions=False)


def fake_browser(selection: list[str]):
    """Replace the terminal loop with a fixed selection."""

    def _run(model: BrowserModel, title: str = "") -> list[str]:
        return selection

    return _run


# ------------------------------------------------------------------- render_screen


def _model() -> BrowserModel:
    return BrowserModel(
        rows=[
            BrowserRow("engineering", "backend-architect", "Backend Architect", "Designs APIs."),
            BrowserRow("marketing", "growth-hacker", "Growth Hacker", "Runs experiments."),
        ]
    )


def _text(rendered) -> str:
    return "".join(fragment for _, fragment in rendered)


def test_render_shows_the_filter_the_rows_and_the_status() -> None:
    model = _model()

    text = _text(render_screen(model))

    assert "filter: " in text
    assert "engineering/backend-architect" in text
    assert "marketing/growth-hacker" in text
    assert "2 agents" in text


def test_render_marks_selected_rows() -> None:
    model = _model()
    model.toggle()

    text = _text(render_screen(model))

    assert "[x] engineering/backend-architect" in text
    assert "[ ] marketing/growth-hacker" in text


def test_render_explains_an_empty_result() -> None:
    model = _model()
    model.set_query("no-such-agent")

    text = _text(render_screen(model))

    assert "no agent matches this filter" in text


def test_render_shows_the_cursor_on_the_current_row() -> None:
    model = _model()

    rendered = render_screen(model)
    styled = [fragment for style, fragment in rendered if style == "class:cursor"]

    assert len(styled) == 1
    assert "backend-architect" in styled[0]


def test_render_windows_a_long_list_keeping_the_cursor_visible() -> None:
    rows = [
        BrowserRow("d", f"agent-{i:03d}", f"Agent {i}", "x") for i in range(60)
    ]
    model = BrowserModel(rows=rows)
    model.move(40)

    text = _text(render_screen(model))

    assert "agent-040" in text
    # The window is bounded, so the first row is off screen at cursor 40.
    assert "agent-000" not in text


# ------------------------------------------------------------------ command wiring


def test_tui_installs_the_selection(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "agency_agents.cli.main.run_browser", fake_browser(["growth-hacker"])
    )

    result = invoke(repo, ["tui", "--tool", "claude-code"], monkeypatch)

    assert result.exit_code == 0, result.output
    written = list((repo / "home" / ".claude" / "agents").glob("*.md"))
    assert [p.stem for p in written] == ["growth-hacker"]
    assert "Installed 1 agent(s)." in result.output


def test_tui_dry_run_writes_nothing(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "agency_agents.cli.main.run_browser", fake_browser(["growth-hacker"])
    )

    result = invoke(repo, ["tui", "--tool", "claude-code", "--dry-run"], monkeypatch)

    assert result.exit_code == 0
    assert "Dry run complete" in result.output
    assert not (repo / "home" / ".claude").exists()


def test_tui_exits_1_when_the_user_cancels(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def _cancel(model: BrowserModel, title: str = "") -> list[str]:
        raise BrowserCancelled("No agents selected — nothing installed.")

    monkeypatch.setattr("agency_agents.cli.main.run_browser", _cancel)

    result = invoke(repo, ["tui", "--tool", "claude-code"], monkeypatch)

    assert result.exit_code == 1
    assert "nothing installed" in result.output


def test_tui_with_an_empty_selection_installs_nothing(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("agency_agents.cli.main.run_browser", fake_browser([]))

    result = invoke(repo, ["tui", "--tool", "claude-code"], monkeypatch)

    assert result.exit_code == 0
    assert "Nothing selected" in result.output
    assert not (repo / "home" / ".claude").exists()


def test_tui_defaults_to_detected_tools(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Only claude-code declares a detection dir, and only it exists under HOME.
    (repo / "home" / ".claude").mkdir(parents=True)
    monkeypatch.setattr(
        "agency_agents.cli.main.run_browser", fake_browser(["growth-hacker"])
    )

    result = invoke(repo, ["tui"], monkeypatch)

    assert result.exit_code == 0, result.output
    assert (repo / "home" / ".claude" / "agents" / "growth-hacker.md").exists()
    assert not (repo / "home" / ".config" / "opencode").exists()


def test_tui_errors_when_no_tool_is_detected(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "agency_agents.cli.main.run_browser", fake_browser(["growth-hacker"])
    )

    result = invoke(repo, ["tui"], monkeypatch)

    assert result.exit_code == 1
    assert "No supported tool detected" in result.output
    assert "claude-code" in result.output


def test_tui_rejects_an_unknown_tool(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "agency_agents.cli.main.run_browser", fake_browser(["growth-hacker"])
    )

    result = invoke(repo, ["tui", "--tool", "nope"], monkeypatch)

    assert result.exit_code == 1
    assert "Unknown tool" in result.output


def test_tui_rejects_an_invalid_scope(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "agency_agents.cli.main.run_browser", fake_browser(["growth-hacker"])
    )

    result = invoke(repo, ["tui", "--tool", "claude-code", "--scope", "global"], monkeypatch)

    assert result.exit_code == 1
    assert "Invalid scope" in result.output


def test_tui_rejects_a_tool_without_the_requested_scope(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "agency_agents.cli.main.run_browser", fake_browser(["growth-hacker"])
    )

    result = invoke(repo, ["tui", "--tool", "claude-code", "--scope", "project"], monkeypatch)

    assert result.exit_code == 1
    assert "no project destination" in result.output


def test_tui_help_documents_its_flags(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    result = invoke(repo, ["tui", "--help"], monkeypatch)

    assert result.exit_code == 0
    rendered = plain(result.output)
    for flag in ("--tool", "--scope", "--dry-run"):
        assert flag in rendered, rendered
