"""Contract tests against the real tools.json.

Every per-agent tool must resolve to a registered renderer, render output, and
install to the destinations it declares. Fixtures are not involved: a typo in
tools.json fails here before it reaches a user.
"""
from pathlib import Path

from agency_agents.core.converter import ConverterEngine, registered_formats
from agency_agents.core.parser import MarkdownParser
from agency_agents.infrastructure.catalog import CatalogManager
from agency_agents.infrastructure.installer import InstallationManager

REPO_ROOT = Path(__file__).resolve().parents[4]
AGENT_FILE = REPO_ROOT / "engineering" / "engineering-frontend-developer.md"


def _agent():
    content = AGENT_FILE.read_text(encoding="utf-8")
    agent = MarkdownParser().create_agent(str(AGENT_FILE), content)
    assert agent is not None, f"cannot parse {AGENT_FILE}"
    return agent


def _per_agent_tools():
    catalog = CatalogManager(REPO_ROOT).load_tools().tools
    return {k: v for k, v in catalog.items() if v.installKind == "per-agent"}


def test_every_per_agent_format_has_a_renderer():
    tools = _per_agent_tools()
    formats = registered_formats()
    missing = {k: v.format for k, v in tools.items() if v.format not in formats}
    assert not missing, f"per-agent tools with no renderer: {missing}"


def test_new_tools_are_part_of_the_contract():
    tools = _per_agent_tools()
    assert tools["antigravity"].format == "antigravity-md"
    assert tools["pi-agent"].format == "gemini-md"
    assert tools["oh-my-pi"].format == "gemini-md"


def _isolated_installer(tmp_path):
    """Installer pointed at a throwaway project root holding the real catalog.

    Project-scoped tools write under the project root, so using the repo here
    would drop generated files (e.g. .cursor/rules/) into the working tree.
    """
    project = tmp_path / "project"
    project.mkdir()
    (project / "tools.json").write_text(
        (REPO_ROOT / "tools.json").read_text(encoding="utf-8"), encoding="utf-8"
    )
    return InstallationManager(project, tmp_path / "home")


def test_every_per_agent_tool_renders_and_installs(tmp_path):
    engine = ConverterEngine(REPO_ROOT)
    installer = _isolated_installer(tmp_path)
    agent = _agent()

    for kebab, tool in _per_agent_tools().items():
        outputs = engine.convert_agent_for_tool(agent, kebab)
        assert outputs, f"{kebab}: renderer returned nothing"

        scope = "user" if tool.dest.get("user") else "project"
        installer.install_agent_for_tool(agent, kebab, scope=scope)

        slug = f"{tool.slugPrefix or ''}{agent.slug}"
        for pattern in tool.dest[scope]:
            target = installer.resolve_path(pattern, slug, scope, tool_kebab=kebab)
            assert target.is_file(), f"{kebab}: expected installed file {target}"
            assert target.stat().st_size > 0, f"{kebab}: installed file is empty: {target}"
