import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

from agency_agents.core.converter import NON_RENDERABLE_FORMATS, registered_formats
from agency_agents.core.models import Agent
from agency_agents.core.parser import MarkdownParser
from agency_agents.infrastructure.catalog import CatalogManager

# NEXUS activation modes, mapped to the roster size each mode can actually carry.
# A Micro runbook runs in minutes-to-days and cannot sustain a 30-agent roster;
# a Full program runs for months and needs depth. Values leave headroom above the
# largest roster the catalog currently ships (Micro 13, Sprint 22, Full 33).
RUNBOOK_MODE_CAPACITY = {
    "NEXUS-Micro": 16,
    "NEXUS-Sprint": 26,
    "NEXUS-Full": 40,
}
RUNBOOK_DOC_DIR = "strategy/runbooks"
RUNBOOK_SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


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

        # Support dirs that are deliberately not divisions.
        # dist/ is generated build output; docs/ is documentation (docs site, doctrine).
        ignore = {"integrations", "strategy", "examples", "scripts", "src", "dist", "docs"}
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

    def _division_names(self) -> List[str]:
        """Division directories on disk, in catalog order."""
        try:
            names = list(self.catalog.load_divisions().divisions.keys())
        except (OSError, ValueError):
            return []
        return [n for n in names if (self.root_dir / n).is_dir()]

    def _agent_slug_index(self) -> Dict[str, Path]:
        """Map every real agent slug (the .md stem) to its file.

        Only files that open with frontmatter are agents; README and notes inside a
        division are documentation, not roster entries.
        """
        index: Dict[str, Path] = {}
        for division in self._division_names():
            for file in (self.root_dir / division).rglob("*.md"):
                try:
                    head = file.read_text(encoding="utf-8")[:3]
                except OSError:
                    continue
                if head == "---":
                    index[file.stem] = file
        return index

    def check_runbooks_consistency(self) -> List[str]:
        """
        Ensures strategy/runbooks.json and strategy/runbooks/ agree with the catalog.

        A runbook is the app's one-click deploy unit, so a broken entry fails silently:
        the roster installs partially or not at all. This check mirrors
        check_divisions_consistency and guarantees four things — every roster slug
        resolves to a real agent file, every referenced doc exists, every doc in the
        directory is registered, and each roster fits its NEXUS mode.
        """
        errors: List[str] = []
        # A project that ships no runbooks is valid: ``strategy/`` is optional doctrine,
        # not a division. Only a strategy/ directory that exists but has no registry is
        # a defect, because that means someone meant to ship runbooks and broke the index.
        if not (self.root_dir / "strategy").is_dir():
            return errors
        try:
            catalog = self.catalog.load_runbooks()
        except FileNotFoundError:
            return ["strategy/runbooks.json is missing."]
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            return [f"strategy/runbooks.json cannot be parsed: {exc}"]

        agent_index = self._agent_slug_index()
        registered_docs: set[str] = set()
        seen_slugs: set[str] = set()

        for runbook in catalog.runbooks:
            if not RUNBOOK_SLUG_PATTERN.match(runbook.slug):
                errors.append(f"Runbook slug '{runbook.slug}' is not kebab-case.")
            if runbook.slug in seen_slugs:
                errors.append(f"Runbook slug '{runbook.slug}' is registered more than once.")
            seen_slugs.add(runbook.slug)

            if runbook.mode not in RUNBOOK_MODE_CAPACITY:
                allowed = " | ".join(RUNBOOK_MODE_CAPACITY)
                errors.append(
                    f"Runbook '{runbook.slug}' declares mode '{runbook.mode}'; expected one of {allowed}."
                )

            doc_path = Path(runbook.doc)
            registered_docs.add(doc_path.as_posix())
            if not doc_path.as_posix().startswith(RUNBOOK_DOC_DIR + "/"):
                errors.append(
                    f"Runbook '{runbook.slug}' doc '{runbook.doc}' must live under {RUNBOOK_DOC_DIR}/."
                )
            if not (self.root_dir / doc_path).is_file():
                errors.append(f"Runbook '{runbook.slug}' doc '{runbook.doc}' does not exist.")

            if not runbook.roster:
                errors.append(f"Runbook '{runbook.slug}' has an empty roster.")

            roster_slugs: List[str] = []
            for group in runbook.roster:
                if not group.agents:
                    errors.append(f"Runbook '{runbook.slug}' group '{group.group}' lists no agents.")
                for agent_slug in group.agents:
                    roster_slugs.append(agent_slug)
                    if agent_slug not in agent_index:
                        errors.append(
                            f"Runbook '{runbook.slug}' references unknown agent slug '{agent_slug}'."
                        )

            duplicates = sorted({s for s in roster_slugs if roster_slugs.count(s) > 1})
            for duplicate in duplicates:
                errors.append(
                    f"Runbook '{runbook.slug}' lists agent '{duplicate}' in more than one group."
                )

            capacity = RUNBOOK_MODE_CAPACITY.get(runbook.mode)
            if capacity is not None and len(roster_slugs) > capacity:
                errors.append(
                    f"Runbook '{runbook.slug}' rosters {len(roster_slugs)} agents, over the "
                    f"{runbook.mode} limit of {capacity}."
                )

        docs_dir = self.root_dir / RUNBOOK_DOC_DIR
        if docs_dir.is_dir():
            for doc in sorted(docs_dir.glob("*.md")):
                relative = doc.relative_to(self.root_dir).as_posix()
                if relative not in registered_docs:
                    errors.append(
                        f"Runbook doc '{relative}' is not registered in strategy/runbooks.json."
                    )

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
