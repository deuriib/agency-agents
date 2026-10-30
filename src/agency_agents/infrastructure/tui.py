"""Interactive install wizard.

The installer used to ask for a tool and then silently install every team into
the default scope. Every choice the flags can express — tools, scope, teams —
is now a wizard step, and the summary is confirmed before anything is written.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


SCOPES = ("user", "project")


class WizardCancelled(Exception):
    """Raised when the user aborts the wizard or selects nothing."""


@dataclass
class InstallSelection:
    """What the wizard decided; mirrors the non-interactive flags."""

    tools: List[str]
    scope: str
    divisions: List[str]


class TUIWizard:
    """Collects tool, scope, and team choices for an interactive install."""

    def __init__(self, root_dir: Path, catalog_manager):
        self.root_dir = root_dir
        self.catalog = catalog_manager
        self.console = Console()

    # ------------------------------------------------------------------ input

    def _ask(self, label: str, completer=None) -> str:
        return prompt(f"{label}: ", completer=completer).strip()

    def _ask_choice(self, raw: str, options: Sequence[str], default: str) -> str:
        """Accept a 1-based index, a name, or empty for the default."""
        raw = raw.strip().lower()
        if not raw:
            return default
        if raw.isdigit():
            index = int(raw)
            if 1 <= index <= len(options):
                return options[index - 1]
            raise WizardCancelled(f"Choice {index} is out of range (1-{len(options)}).")
        if raw in options:
            return raw
        raise WizardCancelled(f"Unknown choice '{raw}'. Options: {', '.join(options)}")

    def _resolve_multi(self, raw: str, ids: Sequence[str], default: List[str]) -> List[str]:
        """Accept indices, ids, 'all', 'none', or empty for the default."""
        raw = raw.strip().lower()
        if not raw:
            return list(default)
        if raw == "all":
            return list(ids)
        if raw == "none":
            return []

        chosen: List[str] = []
        for token in (t.strip() for t in raw.split(",")):
            if not token:
                continue
            if token.isdigit():
                index = int(token)
                if not 1 <= index <= len(ids):
                    self.console.print(
                        f"[yellow]⚠ Ignoring {index}: out of range (1-{len(ids)})[/yellow]"
                    )
                    continue
                selected = ids[index - 1]
            elif token in ids:
                selected = token
            else:
                self.console.print(f"[yellow]⚠ Ignoring unknown entry '{token}'[/yellow]")
                continue
            if selected not in chosen:
                chosen.append(selected)
        return chosen

    # --------------------------------------------------------------- detection

    def _is_detected(self, tool) -> bool:
        """A tool counts as installed when one of its detection dirs exists."""
        dirs = tool.detect.get("dirs") or []
        for rel in dirs:
            if (Path.home() / rel).exists() or (self.root_dir / rel).exists():
                return True
        return False

    # ------------------------------------------------------------------- steps

    def select_tools(self) -> List[str]:
        """Numbered tool list; empty input picks detected tools, else all."""
        tools = sorted(self.catalog.load_tools().tools.values(), key=lambda t: t.order)
        ids = [t.kebab for t in tools]
        detected = [t.kebab for t in tools if self._is_detected(t)]

        table = Table(title="Tools", show_lines=False)
        table.add_column("#", justify="right", style="dim")
        table.add_column("Tool")
        table.add_column("Kebab", style="cyan")
        table.add_column("Installed", justify="center")
        for index, tool in enumerate(tools, 1):
            table.add_row(
                str(index),
                tool.label,
                tool.kebab,
                "yes" if tool.kebab in detected else "",
            )
        self.console.print(table)

        hint = "detected tools" if detected else "all tools"
        self.console.print(
            f"[dim]Enter numbers or names separated by commas. "
            f"Empty = {hint}. 'all' / 'none' also work.[/dim]"
        )
        raw = self._ask("Tools", completer=WordCompleter(ids))
        selected = self._resolve_multi(raw, ids, detected or ids)

        if not selected:
            raise WizardCancelled("No tools selected — nothing to install.")
        return selected

    def select_scope(self, tools: Sequence[str]) -> str:
        """Only offers scopes that at least one selected tool actually supports."""
        catalog = self.catalog.load_tools().tools
        support: Dict[str, List[str]] = {
            scope: [t for t in tools if catalog[t].dest.get(scope)] for scope in SCOPES
        }
        available = [scope for scope in SCOPES if support[scope]]
        if not available:
            raise WizardCancelled("None of the selected tools has a destination.")

        default = "user" if "user" in available else available[0]

        table = Table(title="Scope")
        table.add_column("#", justify="right", style="dim")
        table.add_column("Scope")
        table.add_column("Destination")
        table.add_column("Tools", justify="right")
        destinations = {
            "user": "your home directory",
            "project": "the current project",
        }
        for index, scope in enumerate(available, 1):
            table.add_row(str(index), scope, destinations[scope], str(len(support[scope])))
        self.console.print(table)

        skipped = {
            scope: [t for t in tools if t not in support[scope]] for scope in available
        }
        for scope, missing in skipped.items():
            if missing:
                self.console.print(
                    f"[dim]{scope} scope will skip: {', '.join(missing)} "
                    f"(no {scope} destination)[/dim]"
                )

        raw = self._ask("Scope", completer=WordCompleter(available))
        chosen = self._ask_choice(raw, available, default)

        missing = skipped.get(chosen, [])
        if missing:
            self.console.print(
                f"[yellow]⚠ Skipping tools with no {chosen} destination: "
                f"{', '.join(missing)}[/yellow]"
            )
        return chosen

    def select_divisions(self) -> List[str]:
        """Numbered team list; empty input installs every team."""
        divisions = self.catalog.load_divisions().divisions
        ids = list(divisions.keys())
        counts = {name: self._count_agents(name) for name in ids}

        table = Table(title="Teams")
        table.add_column("#", justify="right", style="dim")
        table.add_column("Division", style="cyan")
        table.add_column("Label")
        table.add_column("Agents", justify="right")
        for index, name in enumerate(ids, 1):
            table.add_row(str(index), name, divisions[name].label, str(counts[name]))
        self.console.print(table)
        self.console.print(
            "[dim]Enter numbers or names separated by commas. "
            "Empty = all teams. 'all' / 'none' also work.[/dim]"
        )

        raw = self._ask("Teams", completer=WordCompleter(ids))
        selected = self._resolve_multi(raw, ids, ids)
        if not selected:
            raise WizardCancelled("No teams selected — nothing to install.")
        return selected

    def _count_agents(self, division: str) -> int:
        path = self.root_dir / division
        if not path.is_dir():
            return 0
        return sum(
            1
            for file in path.rglob("*.md")
            if file.read_text(encoding="utf-8").startswith("---")
        )

    # ------------------------------------------------------------------ driver

    def confirm(self, selection: InstallSelection) -> None:
        """Show the decision and require an explicit yes."""
        table = Table(title="Ready to install", show_header=False)
        table.add_column("Field", style="bold")
        table.add_column("Value")
        table.add_row("Tools", ", ".join(selection.tools))
        table.add_row("Scope", selection.scope)
        table.add_row("Teams", ", ".join(selection.divisions))
        self.console.print(table)

        answer = self._ask("Install? [Y/n]").lower()
        if answer not in ("", "y", "yes"):
            raise WizardCancelled("Installation cancelled.")

    def run(self, scope: Optional[str] = None) -> InstallSelection:
        """Walk every step and return the confirmed selection."""
        self.console.print(
            Panel.fit(
                "[bold]The Agency — Installer[/bold]\n"
                "Pick the tools, the scope, and the teams to install.",
                border_style="blue",
            )
        )

        tools = self.select_tools()
        chosen_scope = scope or self.select_scope(tools)
        divisions = self.select_divisions()
        selection = InstallSelection(tools=tools, scope=chosen_scope, divisions=divisions)
        self.confirm(selection)
        return selection
