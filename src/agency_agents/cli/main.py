import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from pathlib import Path
from typing import Optional
from agency_agents.core.validator import LintEngine
from agency_agents.core.parser import MarkdownParser
from agency_agents.infrastructure.installer import InstallationManager
from agency_agents.infrastructure.tui import TUIWizard
from agency_agents.infrastructure.hash_manager import HashManager
from agency_agents.core.converter import ConverterEngine

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

@app.command()
def install(
    tool: Optional[str] = typer.Option(None, "--tool", help="Specific tool to install for"),
    interactive: bool = typer.Option(False, "--interactive", help="Use interactive wizard"),
    scope: str = typer.Option("user", "--scope", help="Installation scope: 'user' or 'project'"),
    parallel: bool = typer.Option(False, "--parallel", help="Run conversions in parallel"),
    jobs: int = typer.Option(4, "--jobs", help="Number of parallel jobs")
):
    """
    Install agents for a specific tool or all tools.
    """
    root_dir = Path(".").absolute()
    user_home = Path.home()
    installer = InstallationManager(root_dir, user_home)
    parser = MarkdownParser()
    
    if interactive:
        wizard = TUIWizard(root_dir, installer.catalog)
        selected_tools = wizard.select_tools()
        selected_divs = wizard.select_divisions()
    else:
        selected_tools = [tool] if tool else installer.catalog.load_tools().tools.keys()
        selected_divs = installer.catalog.load_divisions().divisions.keys()

    all_agents = []
    for div in selected_divs:
        div_path = root_dir / div
        if div_path.exists() and div_path.is_dir():
            for file in div_path.rglob("*.md"):
                agent = parser.create_agent(str(file), file.read_text(encoding='utf-8'))
                if agent:
                    all_agents.append(agent)

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
    header += "# (non-agent files), one per contract. Platform-neutral hashes. Regenerate: scripts/test-convert-outputs.sh --update\n"
    
    content = header + "\n".join(new_manifest_lines)
    manifest_path.write_text(content, encoding='utf-8')
    
    console.print(f"[bold green]✓ Manifest updated successfully at {manifest_path}[/bold green]")

if __name__ == "__main__":
    app()
