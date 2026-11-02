"""End-to-end behaviour of every CLI command through ``CliRunner``.

Each test seeds a throwaway repository (catalog JSON + agent markdown) and
asserts the observable contract: files written, messages printed, and exit
codes. Nothing here reaches the network or the real home directory.
"""
import json
import subprocess
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner, Result

from agency_agents.cli.main import app
from agency_agents.core.converter import ConverterEngine
from agency_agents.infrastructure.hash_manager import MANIFEST_HEADER

runner = CliRunner()

AGENT_MD = """---
name: {name}
description: Test agent for CLI coverage.
version: 1.0.0
---
Body of {name}
"""

BODY_A = " ".join(f"alpha{i}" for i in range(30))
BODY_OVERLAP = " ".join(f"alpha{i}" for i in range(15)) + " " + " ".join(
    f"beta{i}" for i in range(15)
)


def tool(
    kebab: str,
    fmt: str = "identity",
    kind: str = "per-agent",
    user: list[str] | None = None,
    project: list[str] | None = None,
    order: int = 1,
    prefix: str | None = None,
) -> dict[str, Any]:
    return {
        "id": kebab,
        "label": kebab.upper(),
        "short": kebab,
        "kebab": kebab,
        "accent": "#000000",
        "icon": None,
        "order": order,
        "scope": {"user": user is not None, "project": project is not None},
        "detect": {"dirs": [], "agentsDir": None},
        "version": {"bin": kebab, "args": []},
        "format": fmt,
        "installKind": kind,
        "slugFrom": "name" if kind == "per-agent" else None,
        "slugPrefix": prefix,
        "dest": {"user": user or [], "project": project or []},
    }


def standard_tools() -> dict[str, Any]:
    return {
        "tools": {
            "claude-code": tool(
                "claude-code",
                user=[".claude/agents/{slug}.md"],
                project=[".claude/agents/{slug}.md"],
                order=1,
            ),
            "opencode": tool(
                "opencode",
                fmt="opencode-md",
                user=[".config/opencode/agents/{slug}.md"],
                project=[".opencode/agents/{slug}.md"],
                order=2,
            ),
            "aider": tool(
                "aider",
                fmt="aider-conventions",
                kind="roster",
                project=["CONVENTIONS.md"],
                order=3,
            ),
            "windsurf": tool(
                "windsurf",
                fmt="windsurf-rules",
                kind="roster",
                project=[".windsurfrules"],
                order=4,
            ),
            "hermes": tool(
                "hermes",
                fmt="hermes-router-plugin",
                kind="plugin",
                user=[".hermes/plugins/agency-agents-router"],
                order=5,
            ),
        }
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def write_agent(root: Path, division: str, slug: str, name: str, body: str = "Body") -> Path:
    directory = root / division
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{slug}.md"
    path.write_text(
        f"---\nname: {name}\ndescription: CLI test agent.\n---\n{body}\n",
        encoding="utf-8",
    )
    return path


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    write_json(tmp_path / "tools.json", standard_tools())
    write_json(
        tmp_path / "divisions.json",
        {
            "divisions": {
                "engineering": {"label": "Engineering", "icon": "e", "color": "#000000"},
                "marketing": {"label": "Marketing", "icon": "m", "color": "#000000"},
            }
        },
    )
    write_agent(tmp_path, "engineering", "code-reviewer", "Code Reviewer")
    write_agent(tmp_path, "engineering", "devops-automator", "DevOps Automator")
    write_agent(tmp_path, "marketing", "growth-hacker", "Growth Hacker")
    return tmp_path


def invoke(repo: Path, args: list[str], monkeypatch: pytest.MonkeyPatch) -> Result:
    """Run the CLI inside ``repo`` with HOME pinned to the sandbox."""
    monkeypatch.chdir(repo)
    monkeypatch.setenv("HOME", str(repo / "home"))
    monkeypatch.setenv("USERPROFILE", str(repo / "home"))
    return runner.invoke(app, args, catch_exceptions=False)


# ------------------------------------------------------------------ help surface


def test_root_help_lists_every_command(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    result = invoke(repo, ["--help"], monkeypatch)

    assert result.exit_code == 0
    assert "Agency Agents Management Tool" in result.output
    for command in ("lint", "install", "verify", "update-manifest", "convert", "check-originality"):
        assert command in result.output


def test_install_help_documents_flags(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    result = invoke(repo, ["install", "--help"], monkeypatch)

    assert result.exit_code == 0
    for flag in ("--interactive", "--scope", "--dry-run", "--list", "--agents-file"):
        assert flag in result.output


def test_verify_and_manifest_help_document_manifest_path(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    verify = invoke(repo, ["verify", "--help"], monkeypatch)
    update = invoke(repo, ["update-manifest", "--help"], monkeypatch)

    assert verify.exit_code == 0
    assert "verify" in verify.output.lower()
    assert "--manifest-path" in verify.output and "--all" in verify.output
    assert update.exit_code == 0
    assert "--all" in update.output and "--manifest-path" in update.output


def test_originality_help_documents_thresholds(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    result = invoke(repo, ["check-originality", "--help"], monkeypatch)

    assert result.exit_code == 0
    assert "--fail" in result.output and "--warn" in result.output


# ------------------------------------------------------------------------- lint


def test_lint_clean_project_passes(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    result = invoke(repo, ["lint"], monkeypatch)

    assert result.exit_code == 0, result.output
    assert "Tools are consistent." in result.output
    assert "Divisions are consistent." in result.output
    assert "All agents passed linting." in result.output


def test_lint_prints_catalog_errors_without_blocking(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    write_json(repo / "tools.json", {"tools": {"x": tool("x", fmt="no-renderer")}})
    (repo / "rogue-dir").mkdir()

    result = invoke(repo, ["lint"], monkeypatch)

    assert result.exit_code == 0, result.output
    assert "Tools Consistency Errors" in result.output
    assert "no-renderer" in result.output
    assert "Division Consistency Errors" in result.output
    assert "rogue-dir" in result.output
    assert "All agents passed linting." in result.output


def test_lint_flags_agent_issues_and_exits_1(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (repo / "engineering" / "broken.md").write_text(
        "---\ntitle: no name here\n---\nBody\n", encoding="utf-8"
    )

    result = invoke(repo, ["lint"], monkeypatch)

    assert result.exit_code == 1
    assert "engineering/broken.md" in result.output
    # The rich table wraps the message, so assert the unwrappable prefix.
    assert "Invalid frontmatter or missing required fields" in result.output
    assert "(name)" in result.output


# ---------------------------------------------------------------------- install


def test_install_rejects_unknown_scope(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    result = invoke(
        repo, ["install", "--no-interactive", "--tool", "claude-code", "--scope", "galaxy"], monkeypatch
    )

    assert result.exit_code == 1
    assert "Invalid scope 'galaxy'" in result.output
    assert not (repo / ".claude").exists()


def test_install_with_empty_division_is_a_noop(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    write_json(
        repo / "divisions.json",
        {
            "divisions": {
                "engineering": {"label": "Eng", "icon": "e", "color": "#000000"},
                "design": {"label": "Design", "icon": "d", "color": "#000000"},
            }
        },
    )
    (repo / "design").mkdir()

    result = invoke(
        repo, ["install", "--no-interactive", "--tool", "claude-code", "--division", "design"], monkeypatch
    )

    assert result.exit_code == 0, result.output
    assert "No agents matched the selection" in result.output
    assert not (repo / ".claude").exists()


def test_install_skips_division_without_a_directory(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    write_json(
        repo / "divisions.json",
        {
            "divisions": {
                "engineering": {"label": "Eng", "icon": "e", "color": "#000000"},
                "ghost": {"label": "Ghost", "icon": "g", "color": "#000000"},
            }
        },
    )

    result = invoke(
        repo,
        ["install", "--no-interactive", "--tool", "claude-code", "--scope", "project"],
        monkeypatch,
    )

    assert result.exit_code == 0, result.output
    installed = sorted(p.name for p in (repo / ".claude" / "agents").iterdir())
    assert installed == ["code-reviewer.md", "devops-automator.md"]


def test_install_rejects_unparsable_agent_file(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (repo / "engineering" / "broken.md").write_text("---\ntitle: no name\n---\nBody\n", encoding="utf-8")

    result = invoke(repo, ["install", "--no-interactive", "--tool", "claude-code"], monkeypatch)

    assert result.exit_code == 1
    assert "Cannot parse agent frontmatter" in result.output
    assert "engineering/bro" in result.output  # console hard-wraps the long path
    assert not (repo / ".claude").exists()


def test_install_reports_tool_failure_and_exits_1(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    write_json(
        repo / "tools.json",
        {
            "tools": {
                "broken-tool": tool(
                    "broken-tool", fmt="no-such-format", user=[".broken/{slug}.md"], project=[]
                )
            },
        },
    )

    result = invoke(repo, ["install", "--no-interactive", "--tool", "broken-tool"], monkeypatch)

    assert result.exit_code == 1
    assert "1 tool(s) failed to install: broken-tool" in result.output
    assert "no-such-format" in result.output
    assert "Installation process completed" not in result.output


def test_install_warns_when_selection_exceeds_tool_cap(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Two engineering agents already exist; 118 more reaches 120 (one over the cap).
    for index in range(118):
        write_agent(repo, "engineering", f"bulk-{index}", f"Bulk Agent {index}")

    result = invoke(
        repo,
        ["install", "--no-interactive", "--tool", "opencode", "--division", "engineering", "--dry-run"],
        monkeypatch,
    )

    assert result.exit_code == 0, result.output
    assert "registers only ~119 agents" in result.output
    assert "You selected 120" in result.output
    assert "120 agents" in result.output


def test_install_parallel_output_matches_sequential(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    result = invoke(
        repo,
        [
            "install", "--no-interactive", "--tool", "claude-code",
            "--scope", "project", "--parallel", "--jobs", "2",
        ],
        monkeypatch,
    )

    assert result.exit_code == 0, result.output
    engine = ConverterEngine(repo)
    markdown = (repo / ".claude" / "agents" / "code-reviewer.md").read_text(encoding="utf-8")
    source = (repo / "engineering" / "code-reviewer.md").read_text(encoding="utf-8")
    assert "name: Code Reviewer" in markdown
    assert markdown.split("---")[-1].strip() == source.split("---")[-1].strip()
    assert engine.catalog.load_tools().tools["claude-code"].kebab == "claude-code"


def test_install_all_tools_skipped_when_scope_has_nothing_applicable(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    write_json(
        repo / "tools.json",
        {"tools": {"aider": tool("aider", fmt="aider-conventions", kind="roster", project=["CONVENTIONS.md"])}},
    )

    result = invoke(repo, ["install", "--no-interactive"], monkeypatch)

    assert result.exit_code == 0, result.output
    assert "No tools applicable to this scope" in result.output
    assert not (repo / "CONVENTIONS.md").exists()


# ------------------------------------------------------------------ interactive


def script_prompts(monkeypatch: pytest.MonkeyPatch, answers: list[str]) -> None:
    queue = list(answers)

    def fake_prompt(*args: object, **kwargs: object) -> str:
        if not queue:
            raise AssertionError("wizard asked more questions than scripted")
        return queue.pop(0)

    monkeypatch.setattr("agency_agents.infrastructure.tui.prompt", fake_prompt)


def test_install_interactive_wizard_installs_confirmed_selection(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    script_prompts(monkeypatch, ["1", "project", "engineering", "y"])

    result = invoke(repo, ["install"], monkeypatch)

    assert result.exit_code == 0, result.output
    installed = sorted(p.name for p in (repo / ".claude" / "agents").iterdir())
    assert installed == ["code-reviewer.md", "devops-automator.md"]
    assert "Ready to install" in result.output


def test_install_interactive_cancel_writes_nothing(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    script_prompts(monkeypatch, ["1", "project", "engineering", "n"])

    result = invoke(repo, ["install"], monkeypatch)

    assert result.exit_code == 1
    assert "Installation cancelled." in result.output
    assert not (repo / ".claude").exists()


def test_install_interactive_eof_is_reported_cleanly(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_eof(*args: object, **kwargs: object) -> str:
        raise EOFError

    monkeypatch.setattr("agency_agents.infrastructure.tui.prompt", raise_eof)

    result = invoke(repo, ["install"], monkeypatch)

    assert result.exit_code == 1
    assert "Installation cancelled." in result.output


# ------------------------------------------------------------------------- list


def test_list_tools_prints_every_kebab(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    result = invoke(repo, ["install", "--list", "tools"], monkeypatch)

    assert result.exit_code == 0, result.output
    for kebab in ("claude-code", "opencode", "aider", "windsurf", "hermes"):
        assert kebab in result.output


def test_list_divisions_alias_matches_teams(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    divisions = invoke(repo, ["install", "--list", "divisions"], monkeypatch)
    teams = invoke(repo, ["install", "--list", "teams"], monkeypatch)

    assert divisions.exit_code == teams.exit_code == 0
    assert divisions.output == teams.output
    assert "engineering" in divisions.output and "2 agents" in divisions.output


# ------------------------------------------------------- verify / update-manifest


def test_update_manifest_single_tool_then_verify(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    manifest = repo / "manifest.sha256"

    update = invoke(
        repo, ["update-manifest", "claude-code", "--manifest-path", str(manifest)], monkeypatch
    )

    assert update.exit_code == 0, update.output
    lines = manifest.read_text(encoding="utf-8").splitlines()
    assert lines[0] == MANIFEST_HEADER[0]
    entries = [line for line in lines if line.startswith("agent\t")]
    assert [e.split("\t")[1:3] for e in entries] == [
        ["claude-code", "code-reviewer"],
        ["claude-code", "devops-automator"],
        ["claude-code", "growth-hacker"],
    ]
    assert all(len(e.split("\t")[3]) == 64 for e in entries)

    verify = invoke(
        repo, ["verify", "claude-code", "--manifest-path", str(manifest)], monkeypatch
    )
    assert verify.exit_code == 0, verify.output
    assert "claude-code: all hashes match" in verify.output


def test_verify_detects_content_drift(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    manifest = repo / "manifest.sha256"
    invoke(repo, ["update-manifest", "claude-code", "--manifest-path", str(manifest)], monkeypatch)
    write_agent(repo, "marketing", "growth-hacker", "Growth Hacker", body="Rewritten body")

    result = invoke(repo, ["verify", "claude-code", "--manifest-path", str(manifest)], monkeypatch)

    assert result.exit_code == 1
    assert "1 mismatch(es)" in result.output
    assert "hash mismatch: agent=growth-hacker tool=claude-code" in result.output


def test_verify_reports_tool_without_entries(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    manifest = repo / "manifest.sha256"
    invoke(repo, ["update-manifest", "claude-code", "--manifest-path", str(manifest)], monkeypatch)

    result = invoke(repo, ["verify", "opencode", "--manifest-path", str(manifest)], monkeypatch)

    assert result.exit_code == 1
    assert "Manifest has no entries for tool 'opencode'" in result.output


def test_verify_missing_manifest_exits_1(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    result = invoke(
        repo, ["verify", "claude-code", "--manifest-path", str(repo / "ghost.sha256")], monkeypatch
    )

    assert result.exit_code == 1
    assert "Manifest file not found" in result.output


def test_verify_unknown_tool_exits_1(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    result = invoke(repo, ["verify", "ghost-tool"], monkeypatch)

    assert result.exit_code == 1
    assert "Unknown tool: ghost-tool" in result.output


def test_verify_rejects_tool_argument_together_with_all(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    result = invoke(repo, ["verify", "claude-code", "--all"], monkeypatch)

    assert result.exit_code == 1
    assert "Use either a tool argument or --all" in result.output


def test_verify_requires_a_tool_or_all(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    result = invoke(repo, ["verify"], monkeypatch)

    assert result.exit_code == 1
    assert "Name a tool or pass --all" in result.output


def test_verify_rejects_roster_tool(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    result = invoke(repo, ["verify", "aider"], monkeypatch)

    assert result.exit_code == 1
    assert "is a 'roster' tool" in result.output
    assert "per-agent tools only" in result.output


def test_verify_truncates_after_twenty_mismatches(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    manifest = repo / "manifest.sha256"
    stale = [f"agent\tclaude-code\tstale-{index}\t{'0' * 64}" for index in range(25)]
    manifest.write_text("\n".join([*MANIFEST_HEADER, *stale]) + "\n", encoding="utf-8")

    result = invoke(repo, ["verify", "claude-code", "--manifest-path", str(manifest)], monkeypatch)

    assert result.exit_code == 1
    # 25 stale entries + 3 roster agents with no entry = 28 mismatches.
    assert "28 mismatch(es)" in result.output
    assert "… and 8 more" in result.output


def test_verify_with_unparsable_agent_exits_1(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (repo / "engineering" / "broken.md").write_text("---\ntitle: no name\n---\nBody\n", encoding="utf-8")

    result = invoke(repo, ["verify", "claude-code"], monkeypatch)

    assert result.exit_code == 1
    assert "Cannot parse agent frontmatter" in result.output


def test_update_manifest_all_covers_every_per_agent_tool(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    manifest = repo / "manifest.sha256"

    result = invoke(repo, ["update-manifest", "--all", "--manifest-path", str(manifest)], monkeypatch)

    assert result.exit_code == 0, result.output
    assert "Manifest regenerated: 6 entries across 2 tools" in result.output
    tools = {line.split("\t")[1] for line in manifest.read_text(encoding="utf-8").splitlines() if line.startswith("agent")}
    assert tools == {"claude-code", "opencode"}


def test_update_manifest_rejects_v2_manifest(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    manifest = repo / "manifest.sha256"
    manifest.write_text("# convert-outputs manifest v2\nagent\tcode-reviewer\tdeadbeef\n", encoding="utf-8")

    result = invoke(
        repo, ["update-manifest", "claude-code", "--manifest-path", str(manifest)], monkeypatch
    )

    assert result.exit_code == 1
    assert "Manifest is v2 (tool-less)" in result.output


def test_update_manifest_unknown_tool_exits_1(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    result = invoke(repo, ["update-manifest", "ghost-tool"], monkeypatch)

    assert result.exit_code == 1
    assert "Unknown tool: ghost-tool" in result.output


# -------------------------------------------------------------- check-originality


def test_check_originality_passes_for_a_distinct_roster(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    result = invoke(repo, ["check-originality"], monkeypatch)

    assert result.exit_code == 0, result.output
    assert "PASSED" in result.output
    assert "[OK   ]" in result.output


def test_check_originality_fails_on_identical_agents(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    write_agent(repo, "engineering", "clone-one", "Clone One", body=BODY_A)
    write_agent(repo, "engineering", "clone-two", "Clone Two", body=BODY_A)

    result = invoke(repo, ["check-originality"], monkeypatch)

    assert result.exit_code == 1
    assert "FAILED: 2 agent(s)" in result.output


def test_check_originality_honours_custom_warn_threshold(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    write_agent(repo, "engineering", "partial-one", "Partial One", body=BODY_A)
    write_agent(repo, "engineering", "partial-two", "Partial Two", body=BODY_OVERLAP)

    result = invoke(repo, ["check-originality", "--warn", "21", "--fail", "90"], monkeypatch)

    assert result.exit_code == 0, result.output
    assert "[WARN ]" in result.output
    assert "Thresholds: WARN >= 21%, FAIL >= 90%" in result.output


def test_check_originality_reports_skipped_missing_file(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    result = invoke(repo, ["check-originality", str(repo / "nope.md")], monkeypatch)

    assert result.exit_code == 0, result.output
    assert "skip (not found)" in result.output


# ---------------------------------------------------------------------- convert


def test_convert_single_per_agent_tool_writes_agent_directory(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    result = invoke(repo, ["convert", "--tool", "claude-code", "--out", "out"], monkeypatch)

    assert result.exit_code == 0, result.output
    rendered = repo / "out" / "claude-code" / "code-reviewer" / "agent.md"
    assert rendered.is_file()
    text = rendered.read_text(encoding="utf-8")
    assert "name: Code Reviewer" in text
    assert text.rstrip().endswith("Body")
    assert "3 agents" in result.output


def test_convert_roster_tool_writes_aider_conventions(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    result = invoke(repo, ["convert", "--tool", "aider", "--out", "out"], monkeypatch)

    assert result.exit_code == 0, result.output
    content = (repo / "out" / "aider" / "CONVENTIONS.md").read_text(encoding="utf-8")
    assert content.startswith("# Agency Agents Roster for AIDER")
    assert "## Code Reviewer" in content and "## Growth Hacker" in content
    assert "3 agents" in result.output


def test_convert_roster_tool_writes_windsurf_rules(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    result = invoke(repo, ["convert", "--tool", "windsurf", "--out", "out"], monkeypatch)

    assert result.exit_code == 0, result.output
    assert (repo / "out" / "windsurf" / ".windsurfrules").is_file()


def test_convert_plugin_without_build_script_exits_1(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    result = invoke(repo, ["convert", "--tool", "hermes", "--out", "out"], monkeypatch)

    assert result.exit_code == 1
    assert "build script missing" in result.output
    assert "1 tool(s) failed to convert" in result.output


def test_convert_plugin_invokes_builder(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (repo / "scripts").mkdir()
    script = repo / "scripts" / "build-hermes-plugin.py"
    script.write_text("# fake builder\n", encoding="utf-8")
    calls = []

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = invoke(repo, ["convert", "--tool", "hermes", "--out", "out"], monkeypatch)

    assert result.exit_code == 0, result.output
    assert calls == [["uv", "run", "python", str(script), "--out", "out/hermes"]]
    assert "hermes: built into" in result.output


def test_convert_plugin_builder_failure_is_reported(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (repo / "scripts").mkdir()
    (repo / "scripts" / "build-hermes-plugin.py").write_text("# fake\n", encoding="utf-8")

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 3, stdout="", stderr="boom from builder")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = invoke(repo, ["convert", "--tool", "hermes", "--out", "out"], monkeypatch)

    assert result.exit_code == 1
    assert "build failed (exit 3): boom from builder" in result.output


def test_convert_parallel_matches_sequential_output(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    result = invoke(
        repo, ["convert", "--tool", "claude-code", "--out", "out", "--parallel", "--jobs", "2"], monkeypatch
    )

    assert result.exit_code == 0, result.output
    engine = ConverterEngine(repo)
    from agency_agents.core.parser import MarkdownParser

    content = (repo / "engineering" / "code-reviewer.md").read_text(encoding="utf-8")
    agent = MarkdownParser().create_agent("code-reviewer.md", content)
    assert agent is not None
    expected = engine.convert_agent_for_tool(agent, "claude-code")[0][1]
    rendered = (repo / "out" / "claude-code" / "code-reviewer" / "agent.md").read_text(encoding="utf-8")
    assert rendered == expected


def test_convert_without_agents_exits_1(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    for path in (repo / "engineering").glob("*.md"):
        path.unlink()
    for path in (repo / "marketing").glob("*.md"):
        path.unlink()
    (repo / "engineering" / "README.md").write_text("# Notes\n", encoding="utf-8")

    result = invoke(repo, ["convert", "--out", "out"], monkeypatch)

    assert result.exit_code == 1
    assert "No agents found to convert." in result.output
    assert not (repo / "out").exists()


def test_convert_skill_md_writes_only_the_body(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    write_json(
        repo / "tools.json",
        {"tools": {"empty": tool("empty", fmt="skill-md", user=[".e/{slug}/SKILL.md"])}},
    )

    result = invoke(repo, ["convert", "--tool", "empty", "--out", "out"], monkeypatch)

    # skill-md writes the body alone into SKILL.md, with no frontmatter.
    assert result.exit_code == 0, result.output
    assert (repo / "out" / "empty" / "code-reviewer" / "SKILL.md").is_file()
