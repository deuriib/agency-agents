import json
from pathlib import Path

import pytest

from agency_agents.core.converter import ConverterEngine
from agency_agents.core.models import Agent, AgentFrontmatter
from agency_agents.infrastructure.hash_manager import (
    MANIFEST_VERSION,
    HashManager,
    ManifestError,
)


def _tool(kebab: str, fmt: str = "identity") -> dict:
    return {
        "id": kebab,
        "label": kebab,
        "short": kebab,
        "kebab": kebab,
        "accent": "#000000",
        "icon": None,
        "order": 1,
        "scope": {"user": True, "project": True},
        "detect": {"dirs": [], "agentsDir": None},
        "version": {"bin": kebab, "args": []},
        "format": fmt,
        "installKind": "per-agent",
        "slugFrom": "name",
        "dest": {"user": [f"{kebab}/{{slug}}.md"], "project": []},
    }


def _engine(tmp_path: Path, tools=("claude-code", "opencode")) -> ConverterEngine:
    payload = {
        "tools": {
            "claude-code": _tool("claude-code"),
            "opencode": _tool("opencode", fmt="opencode-md"),
            **{t: _tool(t) for t in tools if t not in ("claude-code", "opencode")},
        }
    }
    (tmp_path / "tools.json").write_text(json.dumps(payload), encoding="utf-8")
    return ConverterEngine(tmp_path)


def _agent(slug: str, name: str, body: str = "Body") -> Agent:
    return Agent(slug=slug, path=f"{slug}.md", frontmatter=AgentFrontmatter(name=name), body=body)


def test_manifest_round_trip(tmp_path):
    engine = _engine(tmp_path)
    agents = [_agent("alpha", "Alpha"), _agent("beta", "Beta")]
    manifest = tmp_path / "manifest.sha256"
    manager = HashManager()

    assert manager.update_all(manifest, agents, ["claude-code", "opencode"], engine) == 4
    assert manager.verify_manifest(manifest, agents, "claude-code", engine) == []
    assert manager.verify_manifest(manifest, agents, "opencode", engine) == []


def test_verify_detects_changed_output(tmp_path):
    engine = _engine(tmp_path)
    agents = [_agent("alpha", "Alpha")]
    manifest = tmp_path / "manifest.sha256"
    manager = HashManager()
    manager.update_all(manifest, agents, ["claude-code"], engine)

    changed = [_agent("alpha", "Alpha", body="Different body")]
    mismatches = manager.verify_manifest(manifest, changed, "claude-code", engine)

    assert any("hash mismatch" in m for m in mismatches)


def test_verify_detects_missing_and_stale_entries(tmp_path):
    engine = _engine(tmp_path)
    manifest = tmp_path / "manifest.sha256"
    manager = HashManager()
    manager.update_all(manifest, [_agent("alpha", "Alpha")], ["claude-code"], engine)

    mismatches = manager.verify_manifest(manifest, [_agent("beta", "Beta")], "claude-code", engine)

    assert any("missing entry" in m for m in mismatches)
    assert any("stale entry" in m for m in mismatches)


def test_update_tool_preserves_other_tools(tmp_path):
    engine = _engine(tmp_path)
    agents = [_agent("alpha", "Alpha")]
    manifest = tmp_path / "manifest.sha256"
    manager = HashManager()

    manager.update_all(manifest, agents, ["claude-code", "opencode"], engine)
    manager.update_tool(manifest, agents, "opencode", engine)

    version, entries = manager.parse_manifest(manifest)
    assert version == MANIFEST_VERSION
    assert ("claude-code", "alpha") in entries
    assert ("opencode", "alpha") in entries


def test_verify_reports_unknown_tool(tmp_path):
    engine = _engine(tmp_path)
    agents = [_agent("alpha", "Alpha")]
    manifest = tmp_path / "manifest.sha256"
    manager = HashManager()
    manager.update_all(manifest, agents, ["claude-code"], engine)

    mismatches = manager.verify_manifest(manifest, agents, "opencode", engine)

    assert len(mismatches) == 1
    assert "no entries for tool 'opencode'" in mismatches[0]


def test_v2_manifest_is_rejected(tmp_path):
    manifest = tmp_path / "manifest.sha256"
    manifest.write_text(
        "# convert-outputs manifest v2 — tool-less\nagent\talpha\tdeadbeef\n",
        encoding="utf-8",
    )

    with pytest.raises(ManifestError, match="v2"):
        HashManager().parse_manifest(manifest)


def test_missing_manifest_is_rejected(tmp_path):
    with pytest.raises(ManifestError, match="not found"):
        HashManager().parse_manifest(tmp_path / "nope.sha256")
