"""Interactive installer wizard.

The wizard exists to collect every choice the flags can express. A regression
here means `install` silently installs the wrong tools, scope, or teams — so
each step is exercised against a real catalog, not a mock of itself.
"""
import json
from pathlib import Path

import pytest
from rich.console import Console

from agency_agents.infrastructure.tui import (
    InstallSelection,
    TUIWizard,
    WizardCancelled,
)


TOOLS = {
    "tools": {
        "claude-code": {
            "id": "cc", "label": "Claude Code", "short": "Claude", "kebab": "claude-code",
            "accent": "#000", "icon": None, "order": 1,
            "scope": {"user": True, "project": True},
            "detect": {"dirs": [".claude"], "agentsDir": ".claude/agents"},
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

DIVISIONS = {
    "divisions": {
        "engineering": {"label": "Engineering", "icon": "e", "color": "#000000"},
        "marketing": {"label": "Marketing", "icon": "m", "color": "#000000"},
    }
}

AGENT = "---\nname: {name}\ndescription: test\n---\n\nBody of {name}\n"


@pytest.fixture
def root(tmp_path):
    (tmp_path / "tools.json").write_text(json.dumps(TOOLS), encoding="utf-8")
    (tmp_path / "divisions.json").write_text(json.dumps(DIVISIONS), encoding="utf-8")
    for division, slug, name in (
        ("engineering", "code-reviewer", "Code Reviewer"),
        ("engineering", "devops-automator", "DevOps Automator"),
        ("marketing", "growth-hacker", "Growth Hacker"),
    ):
        path = tmp_path / division
        path.mkdir(exist_ok=True)
        (path / f"{slug}.md").write_text(AGENT.format(name=name), encoding="utf-8")
    return tmp_path


@pytest.fixture
def wizard(root, monkeypatch, tmp_path):
    from agency_agents.infrastructure.catalog import CatalogManager

    # Detection reads Path.home(); pin it so a developer's real ~/.claude never
    # changes what the wizard preselects.
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    instance = TUIWizard(root, CatalogManager(root))
    instance.console = Console(record=True, width=120, force_terminal=False)
    return instance


def feed(monkeypatch, answers):
    """Replace prompt() with a scripted list of answers."""
    queue = list(answers)

    def fake_prompt(*args, **kwargs):
        if not queue:
            raise AssertionError("wizard asked more questions than the script provides")
        return queue.pop(0)

    monkeypatch.setattr("agency_agents.infrastructure.tui.prompt", fake_prompt)
    return queue


def test_select_tools_accepts_indices(wizard, monkeypatch):
    feed(monkeypatch, ["1"])
    assert wizard.select_tools() == ["claude-code"]


def test_select_tools_accepts_names(wizard, monkeypatch):
    feed(monkeypatch, ["aider, claude-code"])
    assert wizard.select_tools() == ["aider", "claude-code"]


def test_select_tools_empty_defaults_to_all_when_nothing_detected(wizard, monkeypatch):
    feed(monkeypatch, [""])
    assert wizard.select_tools() == ["claude-code", "aider"]


def test_select_tools_empty_defaults_to_detected_tools(wizard, monkeypatch, tmp_path):
    home = tmp_path / "home"
    (home / ".claude").mkdir(parents=True)
    feed(monkeypatch, [""])
    assert wizard.select_tools() == ["claude-code"]


def test_select_tools_warns_on_unknown_entry(wizard, monkeypatch):
    feed(monkeypatch, ["1,ghost"])
    assert wizard.select_tools() == ["claude-code"]
    assert "ghost" in wizard.console.export_text()


def test_select_tools_rejects_empty_selection(wizard, monkeypatch):
    feed(monkeypatch, ["none"])
    with pytest.raises(WizardCancelled, match="No tools selected"):
        wizard.select_tools()


def test_select_scope_offers_only_supported_scopes(wizard, monkeypatch):
    feed(monkeypatch, [""])
    assert wizard.select_scope(["aider"]) == "project"


def test_select_scope_defaults_to_user_and_warns_about_skips(wizard, monkeypatch):
    feed(monkeypatch, [""])
    assert wizard.select_scope(["claude-code", "aider"]) == "user"
    assert "aider" in wizard.console.export_text()


def test_select_scope_accepts_index(wizard, monkeypatch):
    feed(monkeypatch, ["2"])
    assert wizard.select_scope(["claude-code"]) == "project"


def test_select_divisions_empty_installs_every_team(wizard, monkeypatch):
    feed(monkeypatch, [""])
    assert wizard.select_divisions() == ["engineering", "marketing"]


def test_select_divisions_accepts_names_and_counts_agents(wizard, monkeypatch):
    feed(monkeypatch, ["engineering"])
    assert wizard.select_divisions() == ["engineering"]
    text = wizard.console.export_text()
    assert "Engineering" in text and "2" in text


def test_confirm_requires_explicit_yes(wizard, monkeypatch):
    feed(monkeypatch, ["n"])
    with pytest.raises(WizardCancelled, match="cancelled"):
        wizard.confirm(InstallSelection(["claude-code"], "user", ["engineering"]))


def test_confirm_accepts_default(wizard, monkeypatch):
    feed(monkeypatch, [""])
    wizard.confirm(InstallSelection(["claude-code"], "user", ["engineering"]))
    assert "claude-code" in wizard.console.export_text()


def test_run_walks_every_step(wizard, monkeypatch):
    feed(monkeypatch, ["1", "2", "engineering", "y"])
    selection = wizard.run()
    assert selection == InstallSelection(
        tools=["claude-code"], scope="project", divisions=["engineering"]
    )


def test_run_skips_scope_question_when_scope_is_given(wizard, monkeypatch):
    feed(monkeypatch, ["1", "marketing", "y"])
    selection = wizard.run(scope="user")
    assert selection.scope == "user"
    assert selection.divisions == ["marketing"]
    assert selection.tools == ["claude-code"]
