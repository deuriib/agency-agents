from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import re
from concurrent.futures import ProcessPoolExecutor, as_completed
from agency_agents.core.models import Agent
from agency_agents.infrastructure.catalog import CatalogManager, ToolDefinition

class RenderContext:
    """Data passed to renderers to generate tool-specific files."""
    def __init__(self, agent: Agent, tool: ToolDefinition, target_path: Path):
        self.agent = agent
        self.tool = tool
        self.target_path = target_path

class BaseRenderer:
    """Abstract base for all tool renderers."""
    def render(self, context: RenderContext) -> List[Tuple[str, str]]:
        """Returns a list of (filename, content) tuples."""
        raise NotImplementedError

class IdentityRenderer(BaseRenderer):
    def render(self, context: RenderContext) -> List[Tuple[str, str]]:
        return [("agent.md", context.agent.body)]

class CodexTomlRenderer(BaseRenderer):
    def render(self, context: RenderContext) -> List[Tuple[str, str]]:
        fm = context.agent.frontmatter
        content = f'name = "{fm.name}"\ndescription = "{fm.description or ""}"\nbody = """{context.agent.body}"""'
        return [("agent.toml", content)]

class OpenClawRenderer(BaseRenderer):
    def render(self, context: RenderContext) -> List[Tuple[str, str]]:
        fm = context.agent.frontmatter
        return [
            ("SOUL.md", f"# Soul: {fm.name}\n\n{context.agent.body}"),
            ("AGENTS.md", f"# Agent: {fm.name}\n\n{fm.description or ''}"),
            ("IDENTITY.md", f"# Identity: {fm.name}\n\nTags: {', '.join(fm.tags)}")
        ]

class QwenRenderer(BaseRenderer):
    def _map_tools(self, tools_str: str) -> str:
        mapping = {
            "WebFetch": "WebFetch", "WebSearch": "WebSearch",
            "Read": "ReadFile", "Write": "WriteFile", "Edit": "Edit",
            "Bash": "Shell", "Grep": "Grep", "Glob": "Glob"
        }
        tools = [t.strip() for t in tools_str.split(',')]
        return ", ".join([mapping.get(t, t) for t in tools])

    def render(self, context: RenderContext) -> List[Tuple[str, str]]:
        fm = context.agent.frontmatter
        tools = fm.extra.get("tools", "")
        mapped_tools = self._map_tools(tools)
        content = f"--- \nname: {fm.name}\ntools: {mapped_tools}\n---\n\n{context.agent.body}"
        return [("agent.md", content)]

class VibeRenderer(BaseRenderer):
    def render(self, context: RenderContext) -> List[Tuple[str, str, str]]:
        fm = context.agent.frontmatter
        toml_content = f'name = "{fm.name}"\ncolor = "{fm.color or "#FFFFFF"}"\n'
        md_content = f"# {fm.name}\n\n{context.agent.body}"
        return [
            ("agent.toml", toml_content),
            ("prompt.md", md_content)
        ]

class KimiRenderer(BaseRenderer):
    def render(self, context: RenderContext) -> List[Tuple[str, str]]:
        fm = context.agent.frontmatter
        return [
            ("agent.yaml", f"name: {fm.name}\nversion: {fm.version}"),
            ("system.md", context.agent.body)
        ]

class ZCodeRenderer(BaseRenderer):
    def render(self, context: RenderContext) -> List[Tuple[str, str]]:
        return [("agent.md", context.agent.body)]

class OsaurusRenderer(BaseRenderer):
    def render(self, context: RenderContext) -> List[Tuple[str, str]]:
        return [("SKILL.md", context.agent.body)]

def _parallel_render_worker(agent_data: tuple):
    """Standalone function for ProcessPoolExecutor to avoid pickling issues with complex objects."""
    agent, tool_kebab, format_name, root_dir_str = agent_data
    from agency_agents.infrastructure.catalog import CatalogManager
    catalog = CatalogManager(Path(root_dir_str))
    tool = catalog.load_tools().tools.get(tool_kebab)
    
    renderers = {
        "identity": IdentityRenderer(),
        "codex-toml": CodexTomlRenderer(),
        "qwen-md": QwenRenderer(),
        "openclaw-workspace": OpenClawRenderer(),
        "vibe-toml": VibeRenderer(),
        "kimi-agent": KimiRenderer(),
        "zcode-md": ZCodeRenderer(),
        "skill-md": OsaurusRenderer(),
    }
    renderer = renderers.get(format_name, IdentityRenderer())
    context = RenderContext(agent, tool, Path(""))
    return (agent.slug, renderer.render(context))

class ConverterEngine:
    """
    Handles the conversion of source agents into tool-specific formats.
    Implements parallel processing for mass conversion.
    """
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.catalog = CatalogManager(root_dir)
        self.renderers: Dict[str, BaseRenderer] = {
            "identity": IdentityRenderer(),
            "codex-toml": CodexTomlRenderer(),
            "qwen-md": QwenRenderer(),
            "openclaw-workspace": OpenClawRenderer(),
            "vibe-toml": VibeRenderer(),
            "kimi-agent": KimiRenderer(),
            "zcode-md": ZCodeRenderer(),
            "skill-md": OsaurusRenderer(),
        }

    def get_renderer(self, format_name: str) -> BaseRenderer:
        return self.renderers.get(format_name, IdentityRenderer())

    def convert_agent_for_tool(self, agent: Agent, tool_kebab: str) -> List[Tuple[str, str]]:
        tool = self.catalog.load_tools().tools.get(tool_kebab)
        if not tool: return []
        
        renderer = self.get_renderer(tool.format)
        context = RenderContext(agent, tool, Path(""))
        return renderer.render(context)

    def convert_all_parallel(self, agents: List[Agent], tool_kebab: str, jobs: int = 4) -> Dict[str, List[Tuple[str, str]]]:
        """Converts multiple agents in parallel using ProcessPoolExecutor."""
        tool = self.catalog.load_tools().tools.get(tool_kebab)
        if not tool: return {}
        
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
