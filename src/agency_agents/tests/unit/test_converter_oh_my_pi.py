"""Contract tests for the oh-my-pi (``omp``) agent frontmatter.

omp does not read the source block: it requires non-empty string ``name`` and
``description``, resolves ``tools`` against its own builtin names, and only lets
an agent delegate when it holds the ``task`` tool plus ``spawns``. The expected
shape comes from omp 18.13.3 — ``docs/task-agent-discovery.md``,
``discovery/helpers.ts`` (``parseAgentFields``), ``tools/builtin-names.ts``, and
the agents ``omp agents unpack`` writes out.
"""
import re
from pathlib import Path
from typing import Any, Dict, List

import yaml

from agency_agents.core.converter import PRIMARY_AGENT_SLUGS, ConverterEngine, OhMyPiRenderer
from agency_agents.core.models import Agent, AgentFrontmatter
from agency_agents.core.parser import MarkdownParser
from agency_agents.infrastructure.catalog import CatalogManager

REPO_ROOT = Path(__file__).resolve().parents[4]

# omp's BUILTIN_TOOL_NAMES. A tool outside this set is not an allowlist entry,
# it is a name omp silently ignores, so every emitted name must appear here.
OMP_BUILTIN_TOOLS = frozenset(
    {
        "read",
        "bash",
        "edit",
        "ast_grep",
        "ast_edit",
        "ask",
        "debug",
        "ida",
        "eval",
        "github",
        "glob",
        "grep",
        "find",
        "lsp",
        "checkpoint",
        "rewind",
        "context_notes",
        "new_context",
        "security_scan",
        "task",
        "wait",
        "todo",
        "web_search",
        "write",
        "memory_edit",
        "retain",
        "recall",
        "reflect",
        "learn",
        "manage_skill",
    }
)

# Names omp reserves for the session sentinels; an agent using one is rejected.
OMP_RESERVED_NAMES = frozenset({"main", "sub"})

# The contract keys, in the order omp's own agents declare them.
OMP_KEYS = ("name", "description", "tools", "spawns", "blocking", "structured", "autoloadSkills")

SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _render(agent: Agent) -> str:
    engine = ConverterEngine(REPO_ROOT)
    outputs = engine.convert_agent_for_tool(agent, "oh-my-pi")
    assert len(outputs) == 1
    filename, content = outputs[0]
    assert filename == "agent.md"
    return content


def _frontmatter(content: str) -> Dict[str, Any]:
    """The rendered block, parsed the way omp parses it: YAML, then a body."""
    assert content.startswith("---\n"), "rendered agent must open with frontmatter"
    block = content.split("---\n", 2)[1]
    parsed = yaml.safe_load(block)
    assert isinstance(parsed, dict), "frontmatter must parse to a mapping"
    return parsed


def _agent(slug: str, name: str, description: str | None = None) -> Agent:
    return Agent(
        slug=slug,
        path=f"{slug}.md",
        frontmatter=AgentFrontmatter(name=name, description=description),
        body="\n# Body\n\nHello.\n",
    )


def test_specialist_declares_the_execution_surface_only():
    fm = _frontmatter(_render(_agent("frontend-developer", "Frontend Developer", "Builds UI.")))

    assert fm["tools"] == ["read", "write", "edit", "grep", "glob", "find", "bash", "web_search"]
    # No `task` tool means no delegation, and `spawns` without it would be dead.
    assert "task" not in fm["tools"]
    assert "spawns" not in fm
    assert fm["blocking"] is True


def test_orchestrator_declares_the_delegation_surface():
    fm = _frontmatter(_render(_agent("agents-orchestrator", "Agents Orchestrator", "Runs the pipeline.")))

    assert fm["tools"][:2] == ["task", "wait"]
    assert fm["spawns"] == "*"
    # The pipeline fans out without waiting at the gating step.
    assert fm["blocking"] is False


def test_vasquez_delegates_like_the_orchestrator():
    """The process steward convenes the reviews and gates, so it spawns too."""
    fm = _frontmatter(_render(_agent("vasquez", "Vasquez", "Enforces the gates.")))

    assert fm["tools"][:2] == ["task", "wait"]
    assert fm["spawns"] == "*"
    assert fm["blocking"] is False


def test_every_primary_agent_carries_the_delegation_surface():
    for slug in PRIMARY_AGENT_SLUGS:
        fm = _frontmatter(_render(_agent(slug, slug, "Delegates.")))

        assert "task" in fm["tools"], slug
        assert fm["spawns"] == "*", slug
        assert fm["blocking"] is False, slug


def test_a_specialist_never_gets_the_delegation_surface():
    for slug in ("frontend-developer", "agents-orchestrator-helper"):
        fm = _frontmatter(_render(_agent(slug, slug, "Executes.")))

        assert "task" not in fm["tools"], slug
        assert "spawns" not in fm, slug
        assert fm["blocking"] is True, slug


def test_name_is_the_slug_omp_dispatches_by():
    fm = _frontmatter(_render(_agent("frontend-developer", "Frontend Developer", "Builds UI.")))

    # omp looks the agent up by exact name, so the display name must not leak.
    assert fm["name"] == "frontend-developer"


def test_description_is_quoted_and_escaped():
    description = 'Ships "the thing": every time, no hedging.'
    fm = _frontmatter(_render(_agent("shipper", "Shipper", description)))

    assert fm["description"] == description


def test_a_pre_quoted_source_description_loses_its_extra_quotes():
    # The parser keeps frontmatter verbatim, so an author-quoted description
    # would otherwise reach omp with the quote characters in the text.
    fm = _frontmatter(_render(_agent("shipper", "Shipper", '"Ships the thing: fast."')))

    assert fm["description"] == "Ships the thing: fast."


def test_missing_description_falls_back_to_the_name():
    fm = _frontmatter(_render(_agent("shipper", "Shipper", None)))

    # omp rejects an empty description, so the agent states its own name instead
    # of the renderer inventing a claim about it.
    assert fm["description"] == "Shipper"


def test_tools_are_only_names_omp_grants_a_subagent():
    """`todo` is a builtin, but omp withholds it from subagent sessions.

    Verified against omp 18.13.3: the main session lists `todo`, an installed
    agent's own tool list never does. Declaring it would name a tool that never
    arrives.
    """
    fm = _frontmatter(_render(_agent("agents-orchestrator", "Agents Orchestrator", "Runs the pipeline.")))

    assert "todo" not in fm["tools"]


def test_structured_stays_off_and_autoload_skills_is_literal():
    fm = _frontmatter(_render(_agent("shipper", "Shipper", "Ships.")))

    # No agent ships an `output` schema, so structured results would be empty.
    assert fm["structured"] is False
    assert fm["autoloadSkills"] == ["*"]


def test_source_metadata_is_not_copied():
    agent = _agent("shipper", "Shipper", "Ships.")
    agent.frontmatter.color = "cyan"
    agent.frontmatter.vibe = "Ships fast."
    agent.frontmatter.version = "2.0.0"
    agent.frontmatter.tags = ["shipping"]
    agent.frontmatter.extra["emoji"] = "🚀"
    agent.frontmatter.extra["tools"] = "Read, Write"

    fm = _frontmatter(_render(agent))

    # omp reads none of these; carrying them would suggest it does.
    assert set(fm) == set(OMP_KEYS) - {"spawns"}


def _roster() -> List[Agent]:
    """Every real agent file in the catalog, parsed the same way install does."""
    catalog = CatalogManager(REPO_ROOT).load_divisions().divisions
    parser = MarkdownParser()
    agents = []
    for division in catalog:
        for path in sorted((REPO_ROOT / division).rglob("*.md")):
            content = path.read_text(encoding="utf-8")
            if not content.startswith("---"):
                continue
            agent = parser.create_agent(str(path), content)
            if agent is not None:
                agents.append(agent)
    return agents


def test_every_agent_in_the_roster_meets_the_omp_contract():
    agents = _roster()
    assert len(agents) >= 290, f"roster walked only {len(agents)} agents"

    failures = []
    for agent in agents:
        content = _render(agent)
        try:
            fm = _frontmatter(content)
        except AssertionError as error:
            failures.append(f"{agent.slug}: {error}")
            continue

        name = fm.get("name")
        if not isinstance(name, str) or name != agent.slug:
            failures.append(f"{agent.slug}: name is {name!r}, omp dispatches by slug")
        if not SLUG_PATTERN.match(agent.slug):
            failures.append(f"{agent.slug}: slug is not a valid omp agent name")
        if agent.slug in OMP_RESERVED_NAMES:
            failures.append(f"{agent.slug}: slug collides with an omp reserved name")

        description = fm.get("description")
        if not isinstance(description, str) or not description.strip():
            failures.append(f"{agent.slug}: description must be a non-empty string")
        expected = OhMyPiRenderer._unwrapped(agent.frontmatter.description or "").strip()
        if description != (expected or agent.frontmatter.name):
            failures.append(f"{agent.slug}: description lost text in rounding")

        tools = fm.get("tools")
        if not isinstance(tools, list) or not tools:
            failures.append(f"{agent.slug}: tools must be a non-empty list")
            continue
        unknown = [tool for tool in tools if tool not in OMP_BUILTIN_TOOLS]
        if unknown:
            failures.append(f"{agent.slug}: unknown omp tools {unknown}")

        if ("task" in tools) != ("spawns" in fm):
            failures.append(f"{agent.slug}: `task` tool and `spawns` must be declared together")
        if "spawns" in fm and fm["spawns"] != "*" and not isinstance(fm["spawns"], list):
            failures.append(f"{agent.slug}: spawns is {fm['spawns']!r}")
        if not isinstance(fm.get("blocking"), bool):
            failures.append(f"{agent.slug}: blocking must be a boolean")
        if fm.get("structured") is not False:
            failures.append(f"{agent.slug}: structured must be false")
        if fm.get("autoloadSkills") != ["*"]:
            failures.append(f"{agent.slug}: autoloadSkills must be the declared wildcard")

        body = content.split("\n---\n", 1)[-1]
        if not body.strip():
            failures.append(f"{agent.slug}: rendered body is empty")

    assert not failures, "omp contract violations:\n" + "\n".join(failures)
