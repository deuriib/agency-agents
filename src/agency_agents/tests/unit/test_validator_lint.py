"""Lint engine: catalog consistency checks and per-agent linting.

`LintEngine` is the gate that catches a broken roster before it is rendered:
a tool declaring a format nobody implements, a division that exists on disk
but not in ``divisions.json``, and agent files whose frontmatter cannot be
parsed. Each failure mode is asserted by message, because the CLI prints them
verbatim to the user.
"""
import json
from pathlib import Path
from typing import Any

import pytest

from agency_agents.core.validator import LintEngine


def tool_entry(**overrides: Any) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "id": "x",
        "label": "X",
        "short": "X",
        "kebab": "x",
        "accent": "#000",
        "icon": None,
        "order": 1,
        "scope": {"user": True, "project": True},
        "detect": {"dirs": [], "agentsDir": None},
        "version": {"bin": "x", "args": []},
        "format": "identity",
        "installKind": "per-agent",
        "slugFrom": "name",
        "dest": {"user": [".x/{slug}.md"], "project": []},
    }
    entry.update(overrides)
    return {"tools": {"x": entry}}


def seed_divisions(root: Path, names: tuple[str, ...]) -> None:
    (root / "divisions.json").write_text(
        json.dumps(
            {
                "divisions": {
                    name: {"label": name.capitalize(), "icon": "i", "color": "#000000"}
                    for name in names
                }
            }
        ),
        encoding="utf-8",
    )


def write_markdown(root: Path, division: str, name: str, content: str) -> Path:
    path = root / division / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


# ------------------------------------------------------------ tools catalog


def test_tools_flags_key_that_does_not_match_kebab(tmp_path: Path) -> None:
    (tmp_path / "tools.json").write_text(
        json.dumps({"tools": {"alias": tool_entry()["tools"]["x"]}}), encoding="utf-8"
    )

    errors = LintEngine(tmp_path).check_tools_consistency()

    assert errors == ["Tool key 'alias' does not match kebab field 'x'"]


def test_tools_flags_missing_required_fields(tmp_path: Path) -> None:
    (tmp_path / "tools.json").write_text(
        json.dumps(tool_entry(id="", label="")), encoding="utf-8"
    )

    errors = LintEngine(tmp_path).check_tools_consistency()

    assert errors == ["Tool 'x' is missing required fields (id, label, format, or installKind)"]


def test_tools_flags_per_agent_format_without_renderer(tmp_path: Path) -> None:
    (tmp_path / "tools.json").write_text(
        json.dumps(tool_entry(format="no-such-format")), encoding="utf-8"
    )

    errors = LintEngine(tmp_path).check_tools_consistency()

    assert errors == [
        "Tool 'x' is per-agent but format 'no-such-format' has no renderer. "
        "Register it in converter._FORMAT_RENDERERS."
    ]


def test_tools_accepts_non_renderable_format_for_roster_tool(tmp_path: Path) -> None:
    (tmp_path / "tools.json").write_text(
        json.dumps(tool_entry(format="aider-conventions", installKind="roster")),
        encoding="utf-8",
    )

    assert LintEngine(tmp_path).check_tools_consistency() == []


def test_tools_flags_roster_format_that_is_not_known_non_renderable(tmp_path: Path) -> None:
    (tmp_path / "tools.json").write_text(
        json.dumps(tool_entry(format="made-up-roster", installKind="roster")),
        encoding="utf-8",
    )

    errors = LintEngine(tmp_path).check_tools_consistency()

    assert errors == [
        "Tool 'x' (roster) declares format 'made-up-roster' with no renderer "
        "and is not a known non-renderable format."
    ]


@pytest.mark.parametrize("scope_updates", [{"user": [], "project": []}])
def test_tools_flags_tool_without_any_destination(tmp_path: Path, scope_updates: dict[str, list[str]]) -> None:
    (tmp_path / "tools.json").write_text(
        json.dumps(tool_entry(dest=scope_updates)), encoding="utf-8"
    )

    errors = LintEngine(tmp_path).check_tools_consistency()

    assert errors == ["Tool 'x' has no destination for either user or project scope"]


# -------------------------------------------------------------- divisions


def test_divisions_reports_both_missing_and_extra(tmp_path: Path) -> None:
    seed_divisions(tmp_path, ("engineering",))
    (tmp_path / "rogue").mkdir()

    errors = LintEngine(tmp_path).check_divisions_consistency()

    assert sorted(errors) == [
        "Directory 'rogue' found on disk but not defined in divisions.json.",
        "Division 'engineering' defined in divisions.json but missing on disk.",
    ]


def test_divisions_ignores_support_directories(tmp_path: Path) -> None:
    seed_divisions(tmp_path, ("engineering",))
    (tmp_path / "engineering").mkdir()
    for support in ("integrations", "strategy", "examples", "scripts", "src"):
        (tmp_path / support).mkdir()

    assert LintEngine(tmp_path).check_divisions_consistency() == []


# ----------------------------------------------------------- agent linting


def test_lint_accepts_well_formed_agent(tmp_path: Path) -> None:
    write_markdown(
        tmp_path,
        "engineering",
        "code-reviewer.md",
        "---\nname: Code Reviewer\ndescription: Reviews code.\n---\nBody\n",
    )

    assert LintEngine(tmp_path).lint_agents(tmp_path / "engineering") == []


def test_lint_flags_unparsable_frontmatter(tmp_path: Path) -> None:
    path = write_markdown(tmp_path, "engineering", "broken.md", "---\ntitle: No name\n---\nBody\n")

    issues = LintEngine(tmp_path).lint_agents(tmp_path / "engineering")

    assert issues == [(path, "Invalid frontmatter or missing required fields (name)")]


def test_lint_flags_missing_description(tmp_path: Path) -> None:
    path = write_markdown(tmp_path, "engineering", "bare.md", "---\nname: Bare Agent\n---\nBody\n")

    issues = LintEngine(tmp_path).lint_agents(tmp_path / "engineering")

    assert issues == [(path, "Missing description in frontmatter")]


def test_lint_ignores_markdown_without_frontmatter(tmp_path: Path) -> None:
    write_markdown(tmp_path, "engineering", "README.md", "# Engineering\n\nJust docs.\n")

    assert LintEngine(tmp_path).lint_agents(tmp_path / "engineering") == []


def test_lint_scans_nested_directories_and_accumulates_issues(tmp_path: Path) -> None:
    write_markdown(
        tmp_path, "engineering", "sub/broken.md", "---\ntitle: Nothing\n---\nBody\n"
    )
    write_markdown(tmp_path, "engineering", "sub/bare.md", "---\nname: Bare\n---\nBody\n")
    write_markdown(
        tmp_path, "engineering", "good.md", "---\nname: Good\ndescription: Fine.\n---\nBody\n"
    )

    issues = LintEngine(tmp_path).lint_agents(tmp_path / "engineering")

    assert sorted(issue for _, issue in issues) == [
        "Invalid frontmatter or missing required fields (name)",
        "Missing description in frontmatter",
    ]


def test_lint_on_empty_division_returns_nothing(tmp_path: Path) -> None:
    (tmp_path / "engineering").mkdir()

    assert LintEngine(tmp_path).lint_agents(tmp_path / "engineering") == []
