from typing import Dict, Any, List, Optional, Tuple, Type
from pathlib import Path
import copy
import re
from concurrent.futures import ProcessPoolExecutor, as_completed
from agency_agents.core.models import Agent
from agency_agents.infrastructure.catalog import CatalogManager, ToolDefinition

Filename = str
Content = str
RenderOutput = List[Tuple[Filename, Content]]


class RenderContext:
    """Data passed to renderers to generate tool-specific files."""
    def __init__(self, agent: Agent, tool: ToolDefinition, target_path: Optional[Path] = None):
        self.agent = agent
        self.tool = tool
        self.target_path = target_path


class BaseRenderer:
    """Abstract base for all tool renderers (strategy pattern)."""
    def render(self, context: RenderContext) -> RenderOutput:
        """Returns a list of (filename, content) tuples."""
        raise NotImplementedError

    def frontmatter_overrides(self, frontmatter: Any, agent: Agent) -> None:
        """Strategy hook to inject tool-specific frontmatter. Default: no change."""
        return None

    def _get_effective_frontmatter(self, agent: Agent) -> Any:
        """Deep-copies the agent frontmatter so tool overrides never leak upstream."""
        fm = copy.deepcopy(agent.frontmatter)
        self.frontmatter_overrides(fm, agent)
        return fm

    def _markdown_document(self, frontmatter: Any, body: str) -> str:
        """Standard YAML+markdown agent document shared by identity-like formats."""
        return f"---\n{frontmatter.to_yaml()}\n---\n{body}"


class IdentityRenderer(BaseRenderer):
    """Copies the source agent as-is (frontmatter + body)."""
    def render(self, context: RenderContext) -> RenderOutput:
        fm = self._get_effective_frontmatter(context.agent)
        return [("agent.md", self._markdown_document(fm, context.agent.body))]


# Render-level policy: roster agents promoted to the top of the hierarchy.
# This is a rendering decision, not agent content — it never touches the source
# frontmatter. Only the orchestrator is a primary agent today.
PRIMARY_AGENT_SLUGS = frozenset({"agents-orchestrator"})


def is_primary_agent(agent: Agent) -> bool:
    """True when the agent is declared primary at render time."""
    return agent.slug in PRIMARY_AGENT_SLUGS


class AntigravityRenderer(IdentityRenderer):
    """Antigravity agents are subagents unless the render policy marks them
    primary, in which case they are registered as the main agent instead.

    Each category also declares the exact tools it may use. Antigravity reads
    the `tools` list from frontmatter, so the renderer emits it here instead of
    relying on the source agent's Claude-style tool names.
    """
    # Orchestration surface: delegation plus the shared execution tools.
    MAIN_AGENT_TOOLS = (
        "invoke_subagent",
        "manage_subagents",
        "send_message",
        "manage_task",
        "view_file",
        "write_to_file",
        "replace_file_content",
        "grep_search",
        "find_by_name",
        "list_dir",
        "run_command",
    )
    # Execution-only: every main-agent tool minus the delegation surface.
    SUBAGENT_TOOLS = (
        "view_file",
        "write_to_file",
        "replace_file_content",
        "grep_search",
        "find_by_name",
        "list_dir",
        "run_command",
    )

    def frontmatter_overrides(self, frontmatter: Any, agent: Agent) -> None:
        if is_primary_agent(agent):
            frontmatter.extra.pop("subagent", None)
            frontmatter.extra["mainAgent"] = True
            frontmatter.extra["tools"] = list(self.MAIN_AGENT_TOOLS)
        else:
            frontmatter.extra.pop("mainAgent", None)
            frontmatter.extra["subagent"] = True
            frontmatter.extra["tools"] = list(self.SUBAGENT_TOOLS)


class OpencodeRenderer(IdentityRenderer):
    """opencode agents must declare their mode explicitly.

    Defaults to `subagent` (on-demand via @agent-name). Agents marked primary
    by the render policy are promoted to the primary agent picker.
    """
    def frontmatter_overrides(self, frontmatter: Any, agent: Agent) -> None:
        frontmatter.extra["mode"] = "primary" if is_primary_agent(agent) else "subagent"


class CodexTomlRenderer(BaseRenderer):
    def render(self, context: RenderContext) -> RenderOutput:
        fm = self._get_effective_frontmatter(context.agent)
        content = f'name = "{fm.name}"\ndescription = "{fm.description or ""}"\nbody = """{context.agent.body}"""'
        return [("agent.toml", content)]


class GeminiMdRenderer(IdentityRenderer):
    """Gemini CLI consumes plain agent markdown, same shape as identity."""


class CursorMdcRenderer(IdentityRenderer):
    """Cursor rules use frontmatter + body with a .mdc extension."""


class QwenMdRenderer(BaseRenderer):
    TOOL_NAME_MAP = {
        "WebFetch": "WebFetch", "WebSearch": "WebSearch",
        "Read": "ReadFile", "Write": "WriteFile", "Edit": "Edit",
        "Bash": "Shell", "Grep": "Grep", "Glob": "Glob",
    }

    def _map_tools(self, tools_str: str) -> str:
        tools = [t.strip() for t in tools_str.split(',') if t.strip()]
        return ", ".join(self.TOOL_NAME_MAP.get(t, t) for t in tools)

    def render(self, context: RenderContext) -> RenderOutput:
        fm = self._get_effective_frontmatter(context.agent)
        tools = fm.extra.get("tools", "")
        mapped_tools = self._map_tools(tools)
        content = f"---\nname: {fm.name}\ntools: {mapped_tools}\n---\n\n{context.agent.body}"
        return [("agent.md", content)]


class VibeTomlRenderer(BaseRenderer):
    def render(self, context: RenderContext) -> RenderOutput:
        fm = self._get_effective_frontmatter(context.agent)
        toml_content = f'name = "{fm.name}"\ncolor = "{fm.color or "#FFFFFF"}"\n'
        md_content = f"# {fm.name}\n\n{context.agent.body}"
        return [
            ("agent.toml", toml_content),
            ("prompt.md", md_content),
        ]


class KimiAgentRenderer(BaseRenderer):
    def render(self, context: RenderContext) -> RenderOutput:
        fm = self._get_effective_frontmatter(context.agent)
        return [
            ("agent.yaml", f"name: {fm.name}\nversion: {fm.version}"),
            ("system.md", context.agent.body),
        ]


class ZcodeMdRenderer(IdentityRenderer):
    """ZCode consumes standard agent markdown."""


class SkillMdRenderer(BaseRenderer):
    """skill-md targets (Osaurus, DSH) only carry the body in SKILL.md."""
    def render(self, context: RenderContext) -> RenderOutput:
        return [("SKILL.md", context.agent.body)]


class OpenClawWorkspaceRenderer(BaseRenderer):
    def render(self, context: RenderContext) -> RenderOutput:
        fm = self._get_effective_frontmatter(context.agent)
        return [
            ("SOUL.md", f"# Soul: {fm.name}\n\n{context.agent.body}"),
            ("AGENTS.md", f"# Agent: {fm.name}\n\n{fm.description or ''}"),
            ("IDENTITY.md", f"# Identity: {fm.name}\n\nTags: {', '.join(fm.tags)}"),
        ]


_FORMAT_RENDERERS: Dict[str, Type[BaseRenderer]] = {
    "identity": IdentityRenderer,
    "codex-toml": CodexTomlRenderer,
    "gemini-md": GeminiMdRenderer,
    "cursor-mdc": CursorMdcRenderer,
    "opencode-md": OpencodeRenderer,
    "qwen-md": QwenMdRenderer,
    "vibe-toml": VibeTomlRenderer,
    "kimi-agent": KimiAgentRenderer,
    "zcode-md": ZcodeMdRenderer,
    "skill-md": SkillMdRenderer,
    "openclaw-workspace": OpenClawWorkspaceRenderer,
}

# Tool-specific overrides take precedence over the format default.
# These encode tool behavior that is not (yet) embedded in tools.json format names.
# Reason: tools.json flips formats across tools over time (see antigravity),
# behavior overrides live here so the catalog stays declarative.
_TOOL_RENDERER_OVERRIDES: Dict[str, Type[BaseRenderer]] = {
    "antigravity": AntigravityRenderer,
    "opencode": OpencodeRenderer,
}

# Formats that may fall back to identity until dedicated renderers are needed:
# windsurf-rules / aider-conventions (roster installs via installer),
# hermes-router-plugin (built via scripts/build-hermes-plugin.py).


def build_renderer_registry() -> Dict[str, BaseRenderer]:
    """Registry keyed by format; instances are stateless so singletons are safe."""
    return {fmt: cls() for fmt, cls in _FORMAT_RENDERERS.items()}


def select_renderer(tool: ToolDefinition, registry: Dict[str, BaseRenderer]) -> BaseRenderer:
    """Pick the renderer for a tool: tool-level override first, format second."""
    override = _TOOL_RENDERER_OVERRIDES.get(tool.kebab)
    if override is not None:
        return override()
    return registry.get(tool.format, IdentityRenderer())


def _parallel_render_worker(agent_data: tuple):
    """Standalone function for ProcessPoolExecutor to avoid pickling issues with complex objects."""
    agent, tool_kebab, format_name, root_dir_str = agent_data
    catalog = CatalogManager(Path(root_dir_str))
    tool = catalog.load_tools().tools.get(tool_kebab)
    registry = build_renderer_registry()

    effective_tool = copy.deepcopy(tool)
    if effective_tool is not None:
        # The worker rebuilds from the catalog; reapply the tool override decision.
        renderer = select_renderer(effective_tool, registry)
    else:
        renderer = registry.get(format_name, IdentityRenderer())

    context = RenderContext(agent, tool)
    return (agent.slug, renderer.render(context))


class ConverterEngine:
    """
    Handles the conversion of source agents into tool-specific formats.
    Implements parallel processing for mass conversion.
    """
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.catalog = CatalogManager(root_dir)
        self.renderers: Dict[str, BaseRenderer] = build_renderer_registry()

    def get_renderer(self, format_name: str) -> BaseRenderer:
        return self.renderers.get(format_name, IdentityRenderer())

    def convert_agent_for_tool(self, agent: Agent, tool_kebab: str) -> RenderOutput:
        tool = self.catalog.load_tools().tools.get(tool_kebab)
        if not tool:
            return []
        renderer = select_renderer(tool, self.renderers)
        context = RenderContext(agent, tool)
        return renderer.render(context)

    def convert_all_parallel(self, agents: List[Agent], tool_kebab: str, jobs: int = 4) -> Dict[str, RenderOutput]:
        """Converts multiple agents in parallel using ProcessPoolExecutor."""
        tool = self.catalog.load_tools().tools.get(tool_kebab)
        if not tool:
            return {}

        format_name = tool.format
        worker_data = [
            (agent, tool_kebab, format_name, str(self.root_dir))
            for agent in agents
        ]

        results = {}
        with ProcessPoolExecutor(max_workers=jobs) as executor:
            future_to_agent = {executor.submit(_parallel_render_worker, data): data[0].slug for data in worker_data}
            for future in as_completed(future_to_agent):
                slug, outputs = future.result()
                results[slug] = outputs

        return results
