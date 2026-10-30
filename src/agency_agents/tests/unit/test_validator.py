import json
from pathlib import Path

from agency_agents.core.validator import LintEngine


def seed_divisions(tmp_path: Path, names: tuple) -> None:
    (tmp_path / "divisions.json").write_text(
        json.dumps(
            {
                "divisions": {
                    name: {"label": name.capitalize(), "icon": "x", "color": "#000000"}
                    for name in names
                }
            }
        )
    )


def test_divisions_ignores_tooling_dirs(tmp_path):
    seed_divisions(tmp_path, ("engineering", "marketing"))
    (tmp_path / "engineering").mkdir()
    (tmp_path / "marketing").mkdir()
    # Every kind of tooling state a local checkout accumulates
    for tooling in (".venv", ".pytest_cache", ".github", ".git"):
        (tmp_path / tooling).mkdir()

    engine = LintEngine(tmp_path)
    assert engine.check_divisions_consistency() == []


def test_divisions_flags_untracked_support_dir(tmp_path):
    seed_divisions(tmp_path, ("engineering",))
    (tmp_path / "engineering").mkdir()
    (tmp_path / "rogue-div").mkdir()

    engine = LintEngine(tmp_path)
    errors = engine.check_divisions_consistency()
    assert any("rogue-div" in e for e in errors)


def tool_entry(**overrides):
    entry = {
        "id": "x", "label": "X", "short": "X", "kebab": "x", "accent": "#000",
        "icon": None, "order": 1,
        "scope": {"user": True, "project": True},
        "detect": {"dirs": [], "agentsDir": None},
        "version": {"bin": "x", "args": []},
        "format": "identity", "installKind": "per-agent", "slugFrom": "name",
        "dest": {"user": [".x/{slug}.md"], "project": []},
    }
    entry.update(overrides)
    return {"tools": {"x": entry}}


def test_tools_flags_format_without_renderer(tmp_path):
    (tmp_path / "tools.json").write_text(json.dumps(tool_entry(format="made-up-format")))

    errors = LintEngine(tmp_path).check_tools_consistency()
    assert any("made-up-format" in e and "no renderer" in e for e in errors)


def test_tools_accepts_registered_format(tmp_path):
    (tmp_path / "tools.json").write_text(json.dumps(tool_entry(format="antigravity-md")))

    assert LintEngine(tmp_path).check_tools_consistency() == []


def test_tools_flags_tool_without_destinations(tmp_path):
    (tmp_path / "tools.json").write_text(
        json.dumps(tool_entry(dest={"user": [], "project": []}))
    )

    errors = LintEngine(tmp_path).check_tools_consistency()
    assert any("no destination" in e for e in errors)
