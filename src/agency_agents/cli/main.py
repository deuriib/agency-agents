import typer
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from pathlib import Path
from typing import Optional, Dict, List
from agency_agents.core.validator import LintEngine
from agency_agents.core.parser import MarkdownParser
from agency_agents.core.selection import (
    SelectionError,
    agent_cap,
    select_agents,
)
from agency_agents.infrastructure.installer import InstallationManager
from agency_agents.infrastructure.catalog import CatalogManager
from agency_agents.infrastructure.tui import TUIWizard
from agency_agents.infrastructure.hash_manager import HashManager
from agency_agents.core.converter import ConverterEngine
from agency_agents.core.originality import run_originality_check

# Windows consoles default to cp1252 and crash on the / of status output.
# Force UTF-8 before rich builds its console so the CLI is portable.
for _stream in (sys.stdout, sys.stderr):
    if _stream.encoding and _stream.encoding.lower() not in ("utf-8", "utf8"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

app = typer.Typer(help="Agency Agents Management Tool")
console = Console()

@app.command()
def lint():
    """
    Perform full project linting: divisions, tools, and agents.
    """
    root_dir = Path(".").absolute()
    engine = LintEngine(root_dir)
    
    console.print(Panel("[bold blue]Running Project Linting...[/bold blue]"))

    with console.status("[bold yellow]Checking tools.json..."):
        tool_errors = engine.check_tools_consistency()
    
    if tool_errors:
        console.print("[bold red]❌ Tools Consistency Errors:[/bold red]")
        for err in tool_errors:
            console.print(f"  - {err}")
    else:
        console.print("[bold green]✓ Tools are consistent.[/bold green]")

    with console.status("[bold yellow]Checking divisions..."):
        div_errors = engine.check_divisions_consistency()
    
    if div_errors:
        console.print("[bold red]❌ Division Consistency Errors:[/bold red]")
        for err in div_errors:
            console.print(f"  - {err}")
    else:
        console.print("[bold green]✓ Divisions are consistent.[/bold green]")

    console.print("\n[bold blue]Linting Agent Files...[/bold blue] ")
    all_agent_issues = []
    divisions = engine.catalog.load_divisions().divisions.keys()
    
    for div in divisions:
        div_path = root_dir / div
        if div_path.exists() and div_path.is_dir():
            issues = engine.lint_agents(div_path)
            all_agent_issues.extend(issues)

    if all_agent_issues:
        table = Table(title="Agent Linting Issues")
        table.add_column("File", style="cyan")
        table.add_column("Issue", style="red")
        for file, issue in all_agent_issues:
            table.add_row(str(file.relative_to(root_dir)), issue)
        console.print(table)
        raise typer.Exit(code=1)
    else:
        console.print("[bold green]✓ All agents passed linting.[/bold green]")

def _collect_by_division(root_dir: Path, divisions) -> Dict[str, List]:
    """Scan every division dir once; returns division name -> parsed agents."""
    by_division: Dict[str, List] = {}
    parser = MarkdownParser()
    for div in divisions:
        div_path = root_dir / div
        if not (div_path.exists() and div_path.is_dir()):
            continue
        by_division[div] = [
            agent
            for file in div_path.rglob("*.md")
            if (agent := parser.create_agent(str(file), file.read_text(encoding="utf-8")))
        ]
    return by_division


def _warn_tool_capacity(console: Console, tool_kebab: str, count: int):
    """Mirror legacy behavior: opencode silently drops agents past ~119."""
    cap = agent_cap(tool_kebab)
    if cap > 0 and count > cap:
        console.print(
            f"[bold yellow]⚠ {tool_kebab}: registers only ~{cap} agents "
            f"(upstream bug anomalyco/opencode#27988).[/bold yellow]"
        )
        console.print(
            f"[bold yellow]  You selected {count} — ~{count - cap} won't load. "
            f"Narrow with --division to fix.[/bold yellow]"
        )


def _print_plan(console: Console, installer: InstallationManager, agents, tools, scope: str):
    """--dry-run: show exactly what would be written, then stop. No writes."""
    console.print(Panel("[bold blue]Installation plan (dry run, nothing written)[/bold blue]"))
    for tool_kebab in tools:
        tool = installer.catalog.load_tools().tools.get(tool_kebab)
        if not tool:
            console.print(f"[bold red]  - {tool_kebab}: unknown tool[/bold red]")
            continue
        dests = tool.dest.get(scope, [])
        console.print(f"[bold cyan]{tool_kebab}[/bold cyan] ({tool.installKind}, {len(agents)} agents, scope={scope})")
        for pattern in dests:
            marker = "roster file" if tool.installKind == "roster" else "per agent"
            console.print(f"    {pattern}  [{marker}]")
        if not dests:
            console.print("    [dim]no destinations for this scope[/dim]")

def _handle_list(console: Console, catalog, by_division, divisions, list_what: str):
    """--list: print roster information and exit."""
    tool_keys = list(catalog.load_tools().tools.keys())
    if list_what == "tools":
        for line in tool_keys:
            console.print(f"  {line}")
        return
    team_lines = [
        f"{d:<22} {len(by_division.get(d, [])):>3} agents"
        for d in divisions
    ]
    if list_what in ("teams", "divisions"):
        for line in team_lines:
            console.print(f"  {line}")
        return
    if list_what == "agents":
        for d in divisions:
            for agent in by_division.get(d, []):
                console.print(f"  {d:<20} {agent.slug}")
        return
    if list_what == "all":
        console.print(f"Tools ({len(tool_keys)}):")
        for line in tool_keys:
            console.print(f"  {line}")
        console.print(f"Teams ({len(divisions)}):")
        for line in team_lines:
            console.print(f"  {line}")
        return
    console.print(f"[bold red]Unknown --list value '{list_what}'. Use: tools | teams | agents | all[/bold red]")
    raise typer.Exit(code=1)

@app.command()
def install(
    tool: Optional[str] = typer.Option(None, "--tool", help="Specific tool to install for"),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", help="Use interactive wizard"),
    scope: str = typer.Option("user", "--scope", help="Installation scope: 'user' or 'project'"),
    parallel: bool = typer.Option(False, "--parallel", help="Run conversions in parallel"),
    jobs: int = typer.Option(4, "--jobs", help="Number of parallel jobs"),
    division: Optional[str] = typer.Option(None, "--division", help="Only these teams/divisions (comma-separated)"),
    agent: Optional[str] = typer.Option(None, "--agent", help="Only these agents, by slug, display name or file name without .md (comma-separated)"),
    agents_file: Optional[Path] = typer.Option(None, "--agents-file", help="Agents listed in a file (one id per line, # comments ok)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print the plan and exit without writing anything"),
    list_what: Optional[str] = typer.Option(None, "--list", help="List and exit: tools | teams | agents | all"),
):
    """
    Install agents for a specific tool or all tools.
    """
    root_dir = Path(".").absolute()
    catalog = CatalogManager(root_dir)
    installer = InstallationManager(root_dir, Path.home())

    if list_what:
        divisions = list(catalog.load_divisions().divisions.keys())
        by_division = _collect_by_division(root_dir, divisions)
        _handle_list(console, catalog, by_division, divisions, list_what)
        return

    divisions = list(catalog.load_divisions().divisions.keys())
    by_division = _collect_by_division(root_dir, divisions)
    division_ids = [d.strip() for d in division.split(",") if d.strip()] if division else []
    agent_ids = [a.strip() for a in agent.split(",") if a.strip()] if agent else []

    # Filters, --tool, --dry-run and --no-interactive all force a deterministic,
    # non-interactive run. Only the bare wizard case is interactive.
    interactive_run = interactive and not dry_run and not tool and not (division_ids or agent_ids or agents_file)

    if interactive_run:
        wizard = TUIWizard(root_dir, catalog)
        selected_tools = wizard.select_tools()
        all_agents = [a for agents in by_division.values() for a in agents]
    else:
        selected_tools = [tool] if tool else list(catalog.load_tools().tools.keys())
        try:
            all_agents = select_agents(
                by_division,
                divisions=division_ids,
                agent_ids=agent_ids,
                agents_file=agents_file,
            )
        except SelectionError as e:
            console.print(f"[bold red]❌ {e}[/bold red]")
            raise typer.Exit(code=1)

    if not all_agents:
        console.print("[bold yellow]No agents matched the selection — nothing to install.[/bold yellow]")
        return

    for tool_kebab in selected_tools:
        _warn_tool_capacity(console, tool_kebab, len(all_agents))

    if dry_run:
        _print_plan(console, installer, all_agents, selected_tools, scope)
        console.print("[bold green]✓ Dry run complete — no files written.[/bold green]")
        return

    for t_kebab in selected_tools:
        with console.status(f"[bold yellow]Installing for {t_kebab}..."):
            try:
                installer.install_all_for_tool(
                    all_agents,
                    t_kebab,
                    scope=scope,
                    parallel=parallel,
                    jobs=jobs
                )
            except RuntimeError as e:
                console.print(f"[bold red]❌ Error installing {t_kebab}:[/bold red] {e}")

    console.print("[bold green]✓ Installation process completed![/bold green] ")

@app.command()
def verify(
    tool: str, 
    manifest_path: Path = typer.Option(Path("convert-outputs.sha256"), help="Path to the hash manifest")
):
    """
    Verify the conversion outputs against a SHA256 manifest.
    """
    root_dir = Path(".").absolute()
    engine = ConverterEngine(root_dir)
    hash_manager = HashManager()
    parser = MarkdownParser()
    
    all_agents = []
    divisions = engine.catalog.load_divisions().divisions.keys()
    for div in divisions:
        div_path = root_dir / div
        if div_path.exists() and div_path.is_dir():
            for file in div_path.rglob("*.md"):
                agent = parser.create_agent(str(file), file.read_text(encoding='utf-8'))
                if agent: all_agents.append(agent)

    with console.status(f"[bold yellow]Verifying hashes for {tool}..."):
        mismatches = hash_manager.verify_manifest(manifest_path, all_agents, tool, engine)

    if mismatches:
        console.print("[bold red]❌ Hash Mismatches found:[/bold red]")
        for m in mismatches:
            console.print(f"  - {m}")
        raise typer.Exit(code=1)
    else:
        console.print("[bold green]✓ All hashes match the manifest![/bold green]")

@app.command()
def update_manifest(
    tool: str, 
    manifest_path: Path = typer.Option(Path("convert-outputs.sha256"), help="Path to update the hash manifest")
):
    """
    Regenerate the SHA256 manifest for a specific tool based on current agents.
    """
    root_dir = Path(".").absolute()
    engine = ConverterEngine(root_dir)
    hash_manager = HashManager()
    parser = MarkdownParser()
    
    all_agents = []
    divisions = engine.catalog.load_divisions().divisions.keys()
    for div in divisions:
        div_path = root_dir / div
        if div_path.exists() and div_path.is_dir():
            for file in div_path.rglob("*.md"):
                agent = parser.create_agent(str(file), file.read_text(encoding='utf-8'))
                if agent: all_agents.append(agent)

    with console.status(f"[bold yellow]Generating new manifest for {tool}..."):
        new_manifest_lines = hash_manager.generate_manifest(all_agents, tool, engine)
    
    header = "# convert-outputs manifest v2 — one line per agent (its output across every tool), one per tool\n"
    header += "# (non-agent files), one per contract. Platform-neutral hashes. Regenerate: python -m agency_agents update-manifest\n"
    
    content = header + "\n".join(new_manifest_lines)
    manifest_path.write_text(content, encoding='utf-8')
    
    console.print(f"[bold green]✓ Manifest updated successfully at {manifest_path}[/bold green]")

@app.command("check-originality")
def check_originality(
    files: Optional[List[Path]] = typer.Argument(None, help="Agent .md files to check (default: audit the whole roster)"),
    fail: float = typer.Option(40.0, "--fail", help="FAIL threshold percent (default 40)"),
    warn: float = typer.Option(20.0, "--warn", help="WARN threshold percent (default 20)"),
):
    """Flag agent files that substantially duplicate an existing agent."""
    root_dir = Path(".").absolute()
    code = run_originality_check(files, repo_root=root_dir, fail_threshold=fail, warn_threshold=warn)
    if code != 0:
        raise typer.Exit(code=code)


if __name__ == "__main__":
    app()
