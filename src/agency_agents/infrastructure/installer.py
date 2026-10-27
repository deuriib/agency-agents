import os
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple, Dict
from agency_agents.core.models import Agent
from agency_agents.core.converter import ConverterEngine, RenderContext
from agency_agents.infrastructure.catalog import CatalogManager, ToolDefinition

class InstallationManager:
    """
    Handles the physical deployment of converted agents to target paths.
    Includes pruning, collision detection, and Roster accumulation.
    """
    def __init__(self, root_dir: Path, user_home: Path):
        self.root_dir = root_dir
        self.user_home = user_home
        self.catalog = CatalogManager(root_dir)
        self.converter = ConverterEngine(root_dir)

    def resolve_path(self, pattern: str, slug: str, scope: str = "user", tool_kebab: Optional[str] = None) -> Path:
        # DSH honors env overrides for its skills root (legacy parity).
        if tool_kebab == "dsh":
            if scope == "user" and os.environ.get("DSH_HOME"):
                return Path(os.environ["DSH_HOME"]) / "skills" / slug / "SKILL.md"
            if scope == "project" and os.environ.get("DSH_SKILLS_DIR"):
                return Path(os.environ["DSH_SKILLS_DIR"]) / slug / "SKILL.md"

        path_str = pattern.replace("{slug}", slug)
        full_path = Path(path_str)
        if scope == "user":
            return self.user_home / full_path
        return self.root_dir / full_path

    def check_collisions(self, agents: List[Agent], tool_kebab: str, scope: str = "user") -> List[str]:
        tool = self.catalog.load_tools().tools.get(tool_kebab)
        if not tool: return []
        
        seen_paths = {}
        collisions = []
        
        for agent in agents:
            dests = tool.dest.get(scope, [])
            for pattern in dests:
                target = self.resolve_path(pattern, agent.slug, scope)
                if target in seen_paths:
                    collisions.append(f"Collision: {agent.slug} and {seen_paths[target]} both target {target}")
                seen_paths[target] = agent.slug
        
        return collisions

    def prune_output(self, tool_kebab: str, scope: str = "user"):
        if scope == "project":
            tool = self.catalog.load_tools().tools.get(tool_kebab)
            if not tool: return
            for pattern in tool.dest.get("project", []):
                p = self.root_dir / Path(pattern).parent
                if p.exists() and p.is_dir():
                    pass

    def install_agent_for_tool(
        self,
        agent: Agent,
        tool_kebab: str,
        scope: str = "user",
        outputs: Optional[List[Tuple[str, str]]] = None,
    ):
        tool = self.catalog.load_tools().tools.get(tool_kebab)
        if not tool:
            return

        if outputs is None:
            outputs = self.converter.convert_agent_for_tool(agent, tool_kebab)
        if not outputs:
            return

        dests = tool.dest.get(scope, [])
        if not dests: return

        slug = agent.slug
        if tool.slugPrefix:
            slug = f"{tool.slugPrefix}{slug}"

        for i, pattern in enumerate(dests):
            filename, content = outputs[i] if i < len(outputs) else outputs[0]
            target_base = self.resolve_path(pattern, slug, scope, tool_kebab=tool_kebab)
            target_base.parent.mkdir(parents=True, exist_ok=True)
            target_base.write_text(content, encoding='utf-8')

    def install_roster(self, agents: List[Agent], tool_kebab: str, scope: str = "user"):
        tool = self.catalog.load_tools().tools.get(tool_kebab)
        if not tool or tool.installKind != "roster":
            return

        header = f"# Agency Agents Roster for {tool.label}\n\n"
        body = ""
        for agent in agents:
            body += f"## {agent.frontmatter.name}\n{agent.body}\n\n---\n\n"
        
        full_content = header + body
        dests = tool.dest.get(scope, [])
        for pattern in dests:
            target = self.resolve_path(pattern, "roster", scope)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(full_content, encoding='utf-8')

    def install_plugin(self, tool_kebab: str, scope: str = "user"):
        """
        Special handler for plugins (Hermes).
        Runs the build script since plugins are built artifacts.
        """
        tool = self.catalog.load_tools().tools.get(tool_kebab)
        if not tool or tool.installKind != "plugin":
            return

        # We call the existing build script to ensure 1:1 artifact generation
        # but manage it from the modular architecture.
        build_script = self.root_dir / "scripts" / "build-hermes-plugin.py"
        if not build_script.exists():
            raise RuntimeError(f"Hermes build script not found at {build_script}")

        # Execute the builder. We pass the root_dir and the destination from tool.dest
        dest_pattern = tool.dest.get(scope, [None])[0]
        if not dest_pattern:
            raise RuntimeError(f"No destination defined for plugin {tool_kebab}")
        
        out_dir = self.resolve_path(dest_pattern, "router", scope).parent
        
        try:
            subprocess.run(
                ["uv", "run", "python", str(build_script), "--out", str(out_dir)],
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Hermes plugin build failed: {e.stderr}")

    def install_all_for_tool(
        self,
        agents: List[Agent],
        tool_kebab: str,
        scope: str = "user",
        parallel: bool = False,
        jobs: int = 4,
    ):
        tool = self.catalog.load_tools().tools.get(tool_kebab)
        if not tool: return

        if tool.installKind == "plugin":
            self.install_plugin(tool_kebab, scope)
            return

        if tool.installKind == "roster":
            self.install_roster(agents, tool_kebab, scope)
            return

        collisions = self.check_collisions(agents, tool_kebab, scope)
        if collisions:
            raise RuntimeError(f"Installation failed due to slug collisions:\n" + "\n".join(collisions))

        self.prune_output(tool_kebab, scope)

        outputs_by_slug: Dict[str, List[Tuple[str, str]]] = {}
        if parallel:
            outputs_by_slug = self.converter.convert_all_parallel(agents, tool_kebab, jobs=jobs)

        for agent in agents:
            outputs = outputs_by_slug.get(agent.slug) if parallel else None
            self.install_agent_for_tool(agent, tool_kebab, scope=scope, outputs=outputs)
