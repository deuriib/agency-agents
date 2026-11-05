"""Tests for catalog root resolution and the installer's project-root split."""

from __future__ import annotations

from importlib import resources
from pathlib import Path

from agency_agents.infrastructure.catalog import resolve_catalog_root
from agency_agents.infrastructure.installer import InstallationManager


def _write_anchors(root: Path) -> None:
    (root / "tools.json").write_text("{}", encoding="utf-8")
    (root / "divisions.json").write_text('{"divisions": {}}', encoding="utf-8")


def _bundled_data() -> Path:
    return Path(str(resources.files("agency_agents.data")))


def test_resolves_cwd_when_running_from_a_checkout(monkeypatch, tmp_path):
    checkout = tmp_path / "checkout"
    checkout.mkdir()
    _write_anchors(checkout)
    monkeypatch.chdir(checkout)

    assert resolve_catalog_root().resolve() == checkout.resolve()


def test_falls_back_to_bundled_data_outside_a_checkout(monkeypatch, tmp_path):
    # An empty directory has no catalog anchors, so the bundled copy is used.
    monkeypatch.chdir(tmp_path)

    assert resolve_catalog_root().resolve() == _bundled_data().resolve()


def test_bundled_data_is_a_complete_catalog():
    bundled = _bundled_data()
    assert (bundled / "tools.json").is_file()
    assert (bundled / "divisions.json").is_file()
    assert (bundled / "strategy" / "runbooks.json").is_file()


def test_installer_project_scope_targets_project_root(tmp_path):
    catalog_root = tmp_path / "catalog"
    catalog_root.mkdir()
    _write_anchors(catalog_root)
    project = tmp_path / "project"
    project.mkdir()

    installer = InstallationManager(catalog_root, tmp_path / "home", project_root=project)

    target = installer.resolve_path(".claude/agents/{slug}.md", "frontend-developer", scope="project")
    assert target == project / ".claude" / "agents" / "frontend-developer.md"


def test_installer_project_root_defaults_to_catalog_root(tmp_path):
    catalog_root = tmp_path / "catalog"
    catalog_root.mkdir()
    _write_anchors(catalog_root)

    installer = InstallationManager(catalog_root, tmp_path / "home")

    target = installer.resolve_path(".claude/agents/{slug}.md", "frontend-developer", scope="project")
    assert target == catalog_root / ".claude" / "agents" / "frontend-developer.md"
