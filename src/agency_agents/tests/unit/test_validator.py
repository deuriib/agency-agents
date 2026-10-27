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
