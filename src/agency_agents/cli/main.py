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
from agency_agents.infrastructure.tui import TUIWizard, WizardCancelled
from agency_agents.infrastructure.hash_manager import HashManager, ManifestError
from agency_agents.core.converter import ConverterEngine, UnknownFormatError
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
    """Scan every division dir once; returns division name -> parsed agents.

    A markdown file that opens with frontmatter but cannot be parsed is a hard
    error: silently dropping it would convert an incomplete roster.
    """
    by_division: Dict[str, List] = {}
    parser = MarkdownParser()
    for div in divisions:
        div_path = root_dir / div
        if not (div_path.exists() and div_path.is_dir()):
            continue
        agents = []
        for file in div_path.rglob("*.md"):
            content = file.read_text(encoding="utf-8")
            agent = parser.create_agent(str(file), content)
            if agent is None:
                if content.startswith("---"):
                    raise ValueError(f"Cannot parse agent frontmatter: {file}")
                continue  # non-agent markdown (README, notes) is not part of the roster
            agents.append(agent)
        by_division[div] = agents
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

def _collect_roster(console: Console, root_dir: Path, divisions) -> Dict[str, List]:
    """Parse the roster or exit with a clean error instead of a traceback."""
    try:
        return _collect_by_division(root_dir, divisions)
    except ValueError as e:
        console.print(f"[bold red]❌ {e}[/bold red]")
        raise typer.Exit(code=1)


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
    scope: Optional[str] = typer.Option(None, "--scope", help="Installation scope: 'user' or 'project' (asks in interactive mode, defaults to 'user' otherwise)"),
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
        by_division = _collect_roster(console, root_dir, divisions)
        _handle_list(console, catalog, by_division, divisions, list_what)
        return

    divisions = list(catalog.load_divisions().divisions.keys())
    by_division = _collect_roster(console, root_dir, divisions)
    division_ids = [d.strip() for d in division.split(",") if d.strip()] if division else []
    agent_ids = [a.strip() for a in agent.split(",") if a.strip()] if agent else []

    # Filters, --tool, --dry-run and --no-interactive all force a deterministic,
    # non-interactive run. Only the bare wizard case is interactive.
    interactive_run = interactive and not dry_run and not tool and not (division_ids or agent_ids or agents_file)

    if interactive_run:
        try:
            selection = TUIWizard(root_dir, catalog).run(scope=scope)
        except (WizardCancelled, KeyboardInterrupt, EOFError) as e:
            message = str(e) or "Installation cancelled."
            console.print(f"[bold yellow]{message}[/bold yellow]")
            raise typer.Exit(code=1)

        selected_tools = selection.tools
        scope = selection.scope
        all_agents = [a for d in selection.divisions for a in by_division[d]]
    else:
        scope = scope or "user"
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

    tools_catalog = catalog.load_tools().tools
    unknown = [t for t in selected_tools if t not in tools_catalog]
    if unknown:
        console.print(f"[bold red]❌ Unknown tool(s): {', '.join(unknown)}[/bold red]")
        raise typer.Exit(code=1)

    if scope not in ("user", "project"):
        console.print(f"[bold red]❌ Invalid scope '{scope}'. Use 'user' or 'project'.[/bold red]")
        raise typer.Exit(code=1)

    unsupported = [t for t in selected_tools if not tools_catalog[t].dest.get(scope)]
    if unsupported:
        if tool is None:
            # "install everything" means everything valid for this scope; make
            # the skip visible instead of reporting a clean success.
            console.print(
                f"[bold yellow]⚠ Skipping tools with no {scope} destination: "
                f"{', '.join(unsupported)} (use --scope project)[/bold yellow]"
            )
            selected_tools = [t for t in selected_tools if t not in unsupported]
        else:
            for t in unsupported:
                supported = [s for s in ("user", "project") if tools_catalog[t].dest.get(s)]
                console.print(
                    f"[bold red]❌ {t} has no {scope} destination "
                    f"(supported: {', '.join(supported) or 'none'})[/bold red]"
                )
            raise typer.Exit(code=1)

    if not selected_tools:
        console.print("[bold yellow]No tools applicable to this scope — nothing to install.[/bold yellow]")
        return

    if not all_agents:
        console.print("[bold yellow]No agents matched the selection — nothing to install.[/bold yellow]")
        return

    for tool_kebab in selected_tools:
        _warn_tool_capacity(console, tool_kebab, len(all_agents))

    if dry_run:
        _print_plan(console, installer, all_agents, selected_tools, scope)
        console.print("[bold green]✓ Dry run complete — no files written.[/bold green]")
        return

    failures: List[str] = []
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
            except (RuntimeError, UnknownFormatError) as e:
                failures.append(t_kebab)
                console.print(f"[bold red]❌ Error installing {t_kebab}:[/bold red] {e}")

    if failures:
        console.print(
            f"[bold red]❌ {len(failures)} tool(s) failed to install: "
            f"{', '.join(failures)}[/bold red]"
        )
        raise typer.Exit(code=1)

    console.print("[bold green]✓ Installation process completed![/bold green] ")

def _load_all_agents(root_dir: Path, engine: ConverterEngine) -> List:
    """Parse every agent in every division once; unparsable agents are fatal."""
    parser = MarkdownParser()
    agents = []
    for div in engine.catalog.load_divisions().divisions.keys():
        div_path = root_dir / div
        if div_path.exists() and div_path.is_dir():
            for file in div_path.rglob("*.md"):
                content = file.read_text(encoding="utf-8")
                agent = parser.create_agent(str(file), content)
                if agent is None:
                    if content.startswith("---"):
                        raise ValueError(f"Cannot parse agent frontmatter: {file}")
                    continue
                agents.append(agent)
    return agents


def _load_roster(console: Console, root_dir: Path, engine: ConverterEngine) -> List:
    """Load every agent or exit with a clean error instead of a traceback."""
    try:
        return _load_all_agents(root_dir, engine)
    except ValueError as e:
        console.print(f"[bold red]❌ {e}[/bold red]")
        raise typer.Exit(code=1)


def _per_agent_tools(engine: ConverterEngine) -> List[str]:
    """Tools whose artifact is one rendered file per agent (manifest scope)."""
    return [
        kebab
        for kebab, tool in engine.catalog.load_tools().tools.items()
        if tool.installKind == "per-agent"
    ]


def _resolve_targets(engine: ConverterEngine, tool: Optional[str], all_tools: bool) -> List[str]:
    """Resolve a single tool argument or the full per-agent set."""
    if all_tools:
        if tool:
            console.print("[bold red]❌ Use either a tool argument or --all, not both.[/bold red]")
            raise typer.Exit(code=1)
        return _per_agent_tools(engine)

    if not tool:
        console.print("[bold red]❌ Name a tool or pass --all.[/bold red]")
        raise typer.Exit(code=1)

    tool_def = engine.catalog.load_tools().tools.get(tool)
    if tool_def is None:
        console.print(f"[bold red]❌ Unknown tool: {tool}[/bold red]")
        raise typer.Exit(code=1)
    if tool_def.installKind != "per-agent":
        console.print(
            f"[bold red]❌ {tool} is a '{tool_def.installKind}' tool; "
            "the manifest covers per-agent tools only.[/bold red]"
        )
        raise typer.Exit(code=1)
    return [tool]


@app.command()
def verify(
    tool: Optional[str] = typer.Argument(None, help="Tool to verify (omit with --all)"),
    all_tools: bool = typer.Option(False, "--all", help="Verify every per-agent tool"),
    manifest_path: Path = typer.Option(Path("convert-outputs.sha256"), help="Path to the hash manifest")
):
    """
    Verify the conversion outputs against a SHA256 manifest.
    """
    root_dir = Path(".").absolute()
    engine = ConverterEngine(root_dir)
    hash_manager = HashManager()
    all_agents = _load_roster(console, root_dir, engine)
    targets = _resolve_targets(engine, tool, all_tools)

    failures = 0
    for t_kebab in targets:
        try:
            mismatches = hash_manager.verify_manifest(manifest_path, all_agents, t_kebab, engine)
        except ManifestError as e:
            console.print(f"[bold red]❌ {e}[/bold red]")
            raise typer.Exit(code=1)

        if mismatches:
            failures += len(mismatches)
            console.print(f"[bold red]❌ {t_kebab}: {len(mismatches)} mismatch(es)[/bold red]")
            for m in mismatches[:20]:
                console.print(f"  - {m}")
            if len(mismatches) > 20:
                console.print(f"  … and {len(mismatches) - 20} more")
        else:
            console.print(f"[bold green]✓ {t_kebab}: all hashes match[/bold green]")

    if failures:
        raise typer.Exit(code=1)

@app.command()
def update_manifest(
    tool: Optional[str] = typer.Argument(None, help="Tool to regenerate (omit with --all)"),
    all_tools: bool = typer.Option(False, "--all", help="Regenerate every per-agent tool"),
    manifest_path: Path = typer.Option(Path("convert-outputs.sha256"), help="Path to update the hash manifest")
):
    """
    Regenerate the SHA256 manifest for one tool, or every per-agent tool with --all.
    """
    root_dir = Path(".").absolute()
    engine = ConverterEngine(root_dir)
    hash_manager = HashManager()
    all_agents = _load_roster(console, root_dir, engine)

    if all_tools:
        targets = _per_agent_tools(engine)
        with console.status("[bold yellow]Regenerating manifest for every per-agent tool..."):
            count = hash_manager.update_all(manifest_path, all_agents, targets, engine)
        console.print(
            f"[bold green]✓ Manifest regenerated: {count} entries "
            f"across {len(targets)} tools at {manifest_path}[/bold green]"
        )
        return

    targets = _resolve_targets(engine, tool, all_tools=False)
    try:
        with console.status(f"[bold yellow]Regenerating manifest for {targets[0]}..."):
            count = hash_manager.update_tool(manifest_path, all_agents, targets[0], engine)
    except ManifestError as e:
        console.print(f"[bold red]❌ {e}[/bold red]")
        raise typer.Exit(code=1)

    console.print(
        f"[bold green]✓ {targets[0]}: {count} entries updated at {manifest_path}[/bold green]"
    )

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


@app.command("convert")
def convert(
    tool: Optional[str] = typer.Option(None, "--tool", help="Specific tool to convert (default: all)"),
    out: Path = typer.Option(Path("integrations"), "--out", help="Output directory for generated files"),
    parallel: bool = typer.Option(False, "--parallel", help="Run conversions in parallel"),
    jobs: int = typer.Option(4, "--jobs", help="Number of parallel jobs"),
):
    """Generate tool-specific integration files from the agent roster (legacy convert.sh)."""
    root_dir = Path(".").absolute()
    catalog = CatalogManager(root_dir)
    engine = ConverterEngine(root_dir)

    divisions = list(catalog.load_divisions().divisions.keys())
    by_division = _collect_roster(console, root_dir, divisions)
    all_agents = [a for agents in by_division.values() for a in agents]
    if not all_agents:
        console.print("[bold red]❌ No agents found to convert.[/bold red]")
        raise typer.Exit(code=1)

    tools_catalog = catalog.load_tools().tools
    selected_tools = [tool] if tool else list(tools_catalog.keys())
    unknown = [t for t in selected_tools if t not in tools_catalog]
    if unknown:
        console.print(f"[bold red]❌ Unknown tool(s): {', '.join(unknown)}[/bold red]")
        raise typer.Exit(code=1)

    out.mkdir(parents=True, exist_ok=True)
    failures: List[str] = []

    for t_kebab in selected_tools:
        tool_def = tools_catalog[t_kebab]
        try:
            if tool_def.installKind == "plugin":
                # Hermes is a built artifact; delegate to the restored builder.
                target = out / t_kebab
                target.mkdir(parents=True, exist_ok=True)
                build_script = root_dir / "scripts" / "build-hermes-plugin.py"
                if not build_script.exists():
                    raise RuntimeError(f"build script missing: {build_script}")
                import subprocess
                result = subprocess.run(
                    ["uv", "run", "python", str(build_script), "--out", str(target)],
                    capture_output=True, text=True,
                )
                if result.returncode != 0:
                    detail = (result.stderr or result.stdout or "").strip()
                    raise RuntimeError(f"build failed (exit {result.returncode}): {detail}")
                console.print(f"[bold green]✓ {t_kebab}: built into {target}[/bold green]")
                continue

            if tool_def.installKind == "roster":
                # Roster tools produce a single consolidated file.
                header = f"# Agency Agents Roster for {tool_def.label}\n\n"
                body = "".join(f"## {a.frontmatter.name}\n{a.body}\n\n---\n\n" for a in all_agents)
                target = out / t_kebab
                target.mkdir(parents=True, exist_ok=True)
                filename = "CONVENTIONS.md" if t_kebab == "aider" else ".windsurfrules"
                (target / filename).write_text(header + body, encoding="utf-8")
                console.print(f"[bold green]✓ {t_kebab}: {len(all_agents)} agents -> {target / filename}[/bold green]")
                continue

            target = out / t_kebab
            target.mkdir(parents=True, exist_ok=True)
            count = 0
            if parallel:
                outputs_by_slug = engine.convert_all_parallel(all_agents, t_kebab, jobs=jobs)
            else:
                outputs_by_slug = None
            for agent in all_agents:
                outputs = (
                    outputs_by_slug.get(agent.slug) if outputs_by_slug else None
                ) or engine.convert_agent_for_tool(agent, t_kebab)
                if not outputs:
                    raise RuntimeError(f"renderer produced no output for agent '{agent.slug}'")
                agent_dir = target / agent.slug
                agent_dir.mkdir(parents=True, exist_ok=True)
                for filename, content in outputs:
                    (agent_dir / filename).write_text(content, encoding="utf-8")
                count += 1
            console.print(f"[bold green]✓ {t_kebab}: {count} agents -> {target}[/bold green]")
        except (RuntimeError, UnknownFormatError) as e:
            failures.append(t_kebab)
            console.print(f"[bold red]❌ {t_kebab}: {e}[/bold red]")

    if failures:
        console.print(
            f"[bold red]❌ {len(failures)} tool(s) failed to convert: "
            f"{', '.join(failures)}[/bold red]"
        )
        raise typer.Exit(code=1)

    console.print("[bold green]✓ Conversion complete.[/bold green]")


if __name__ == "__main__":
    app()
