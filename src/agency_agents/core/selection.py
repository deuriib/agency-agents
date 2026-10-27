from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path

from agency_agents.core.models import Agent, slugify


# Per-tool soft capacity (opencode silently drops past ~119 — upstream bug #27988).
AGENT_CAPS: Dict[str, int] = {
    "opencode": 119,
}


def agent_cap(tool_kebab: str) -> int:
    """Soft registration limit per tool; 0 means unlimited."""
    return AGENT_CAPS.get(tool_kebab, 0)


def agent_aliases(agent: Agent) -> Set[str]:
    """The ids that may select this agent: slug, display name, file stem,
    each optionally without the antigravity 'agency-' prefix."""
    candidates = {
        agent.slug,
        agent.frontmatter.name,
        Path(agent.path).stem,
    }
    aliases = {slugify(c) for c in candidates if c}
    prefixed = {a for a in aliases if a}
    aliases |= {a.replace("agency-", "", 1) for a in prefixed if a.startswith("agency-")}
    return {a for a in aliases if a}


def build_roster_index(agents: List[Agent]) -> Dict[str, Agent]:
    """Alias -> agent lookup. Aliases are slugified, unique across the roster."""
    index: Dict[str, Agent] = {}
    for agent in agents:
        for alias in agent_aliases(agent):
            index.setdefault(alias, agent)
    return index


def resolve_agent(request: str, index: Dict[str, Agent]) -> Optional[Agent]:
    """Resolve one user-supplied id (slug, name, or file stem) to an agent."""
    return index.get(slugify(request))


def parse_agents_file(path: Path) -> List[str]:
    """One agent id per line; '#' starts a comment; blank lines ignored.

    Raises SelectionError with a clean, actionable message instead of a raw
    traceback when the file is missing or not decodable as text (e.g. UTF-16
    output from PowerShell redirection).
    """
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError as e:
        raise SelectionError(f"agents-file not found: {path}") from e
    except UnicodeDecodeError as e:
        raise SelectionError(
            f"agents-file is not valid UTF-8 text: {path} "
            f"(re-save the file, or generate it with e.g. Set-Content -Encoding utf8 on Windows)"
        ) from e

    ids: List[str] = []
    for line in lines:
        entry = line.split("#", 1)[0].strip()
        if entry:
            ids.append(entry)
    return ids


class SelectionError(Exception):
    """User-supplied selection names something impossible to install."""


def select_agents(
    by_division: Dict[str, List[Agent]],
    divisions: Optional[List[str]] = None,
    agent_ids: Optional[List[str]] = None,
    agents_file: Optional[Path] = None,
) -> List[Agent]:
    """
    Union of division rosters, explicit ids, and file ids, de-duplicated by slug.

    Raises SelectionError early when a division or id cannot be resolved —
    fail fast closed: an unknown name must never silently install nothing.
    """
    index = build_roster_index(a for div in by_division.values() for a in div)
    selected: Dict[str, Agent] = {}

    if divisions:
        unknown = sorted(set(divisions) - set(by_division))
        if unknown:
            raise SelectionError(f"Unknown division(s): {', '.join(unknown)}")
        for division in divisions:
            for agent in by_division[division]:
                selected.setdefault(agent.slug, agent)

    file_ids = parse_agents_file(agents_file) if agents_file else []
    if agents_file and not file_ids:
        raise SelectionError(f"No agent ids found in {agents_file}")

    for request in (agent_ids or []) + file_ids:
        agent = resolve_agent(request, index)
        if agent is None:
            raise SelectionError(
                f"Unknown agent '{request}'. Use --list agents to see the available roster."
            )
        selected.setdefault(agent.slug, agent)

    if divisions or agent_ids or file_ids:
        return list(selected.values())
    return list({a.slug: a for div in by_division.values() for a in div}.values())
