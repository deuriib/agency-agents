from typing import List, Tuple
from pathlib import Path
from agency_agents.infrastructure.catalog import CatalogManager
from agency_agents.core.converter import NON_RENDERABLE_FORMATS, registered_formats
from agency_agents.core.parser import MarkdownParser
from agency_agents.core.models import Agent

class LintEngine:
    """
    Core logic for validating agents against project conventions.
    Migrates logic from scripts/lint-agents.sh and scripts/check-*.sh.
    """
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.catalog = CatalogManager(root_dir)
        self.parser = MarkdownParser()

    def check_divisions_consistency(self) -> List[str]:
        """
        Ensures directories on disk match divisions.json.
        Replaces scripts/check-divisions.sh.
        """
        errors = []
        catalog = self.catalog.load_divisions()
        defined_divisions = set(catalog.divisions.keys())
        
        # Support dirs that are deliberately not divisions
        ignore = {"integrations", "strategy", "examples", "scripts", "src"}
        # Dot-dirs (.git, .venv, .pytest_cache, .github...) are tooling state, never divisions
        actual_dirs = {
            d.name for d in self.root_dir.iterdir()
            if d.is_dir() and not d.name.startswith(".") and d.name not in ignore
        }

        missing_on_disk = defined_divisions - actual_dirs
        extra_on_disk = actual_dirs - defined_divisions

        for d in missing_on_disk:
            errors.append(f"Division '{d}' defined in divisions.json but missing on disk.")
        for d in extra_on_disk:
            errors.append(f"Directory '{d}' found on disk but not defined in divisions.json.")

        return errors

    def check_tools_consistency(self) -> List[str]:
        """
        Ensures tools.json is internally consistent.
        Replaces scripts/check-tools.sh.
        """
        errors = []
        catalog = self.catalog.load_tools()
        renderer_formats = registered_formats()

        for kebab, tool in catalog.tools.items():
            if kebab != tool.kebab:
                errors.append(f"Tool key '{kebab}' does not match kebab field '{tool.kebab}'")
            if not tool.id or not tool.label or not tool.format or not tool.installKind:
                errors.append(f"Tool '{kebab}' is missing required fields (id, label, format, or installKind)")

            if tool.installKind == "per-agent" and tool.format not in renderer_formats:
                errors.append(
                    f"Tool '{kebab}' is per-agent but format '{tool.format}' has no renderer. "
                    f"Register it in converter._FORMAT_RENDERERS."
                )
            if (
                tool.installKind != "per-agent"
                and tool.format not in renderer_formats
                and tool.format not in NON_RENDERABLE_FORMATS
            ):
                errors.append(
                    f"Tool '{kebab}' ({tool.installKind}) declares format '{tool.format}' with no renderer "
                    f"and is not a known non-renderable format."
                )

            if not any(tool.dest.get(scope) for scope in ("user", "project")):
                errors.append(f"Tool '{kebab}' has no destination for either user or project scope")

        return errors

    def lint_agents(self, division_path: Path) -> List[Tuple[Path, str]]:
        """
        Lints all agent files within a division.
        Replaces scripts/lint-agents.sh.
        """
        issues = []
        for file in division_path.rglob("*.md"):
            content = file.read_text(encoding='utf-8')
            agent = self.parser.create_agent(str(file), content)
            
            if not agent:
                # Check if it's intended to be an agent file (starts with ---)
                if content.startswith("---"):
                    issues.append((file, "Invalid frontmatter or missing required fields (name)"))
                continue
            
            # Additional custom lint rules go here
            if not agent.frontmatter.description:
                issues.append((file, "Missing description in frontmatter"))
                
        return issues
