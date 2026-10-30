"""Functional coverage for the Antigravity render contract.

Renders the real roster (not fixtures) and installs one agent into an isolated
HOME, so a regression in the tool declarations fails before it ships.
"""
from pathlib import Path

from agency_agents.core.converter import ConverterEngine, is_primary_agent
from agency_agents.core.parser import MarkdownParser
from agency_agents.infrastructure.catalog import CatalogManager
from agency_agents.infrastructure.installer import InstallationManager

REPO_ROOT = Path(__file__).resolve().parents[4]

DELEGATION_TOOLS = {"invoke_subagent", "manage_subagents", "send_message", "manage_task"}
EXECUTION_TOOLS = {
    "view_file",
    "write_to_file",
    "replace_file_content",
    "grep_search",
    "find_by_name",
    "list_dir",
    "run_command",
}


def _roster() -> list:
    catalog = CatalogManager(REPO_ROOT)
    parser = MarkdownParser()
    agents = []
    for division in catalog.load_divisions().divisions:
        division_path = REPO_ROOT / division
        if not division_path.is_dir():
            continue
        for file in division_path.rglob("*.md"):
            agent = parser.create_agent(str(file), file.read_text(encoding="utf-8"))
            if agent:
                agents.append(agent)
    return agents


def _tools(content: str) -> set[str]:
    line = next(l for l in content.splitlines() if l.startswith("tools: "))
    raw = line.removeprefix("tools: ").strip().strip("[]")
    return {tool.strip() for tool in raw.split(",") if tool.strip()}


def test_every_rendered_agent_declares_its_tools():
    engine = ConverterEngine(REPO_ROOT)
    agents = _roster()
    assert agents, "roster is empty; the render check would pass vacuously"

    primaries = []
    for agent in agents:
        content = engine.convert_agent_for_tool(agent, "antigravity")[0][1]
        tools = _tools(content)

        assert tools, f"{agent.slug}: no tools declared"
        if is_primary_agent(agent):
            primaries.append(agent.slug)
            assert "mainAgent: true" in content
            assert tools == DELEGATION_TOOLS | EXECUTION_TOOLS
        else:
            assert "subagent: true" in content
            assert "mainAgent:" not in content
            assert tools == EXECUTION_TOOLS
            assert tools.isdisjoint(DELEGATION_TOOLS)

    assert primaries == ["agents-orchestrator"]


def test_installed_artifact_carries_tool_declarations(tmp_path):
    agent = next(a for a in _roster() if a.slug == "agents-orchestrator")
    installer = InstallationManager(REPO_ROOT, tmp_path / "home")

    installer.install_agent_for_tool(agent, "antigravity", scope="user")

    installed = tmp_path / "home" / ".gemini" / "config" / "agents" / "agents-orchestrator.md"
    assert installed.is_file(), f"expected installed artifact at {installed}"

    content = installed.read_text(encoding="utf-8")
    assert "mainAgent: true" in content
    assert _tools(content) == DELEGATION_TOOLS | EXECUTION_TOOLS
