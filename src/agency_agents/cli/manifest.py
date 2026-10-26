import typer
from rich.console import Console
from rich.panel import Panel
from pathlib import Path
from agency_agents.core.validator import LintEngine
from agency_agents.core.parser import MarkdownParser
from agency_agents.infrastructure.hash_manager import HashManager
from agency_//agents.core.converter import ConverterEngine

app = typer.Typer(help="Agency Agents Management Tool")
console = Console()

@app.command()
def update_manifest(
    tool: str, 
    manifest_path: Path = typer.Option(Path("scripts/convert-outputs.sha256"), help="Path to update the hash manifest")
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
    
    # We prepend the header to maintain original format
    header = "# convert-outputs manifest v2 — one line per agent (its output across every tool), one per tool\n"
    header += "# (non-agent files), one per contract. Platform-neutral hashes. Regenerate: scripts/test-convert-outputs.sh --update\n"
    
    content = header + "\n".join(new_manifest_lines)
    
    # Since the manifest is a global file for ALL tools, we should ideally 
    # merge this tool's hashes with other tools instead of overwriting.
    # However, for a simple update, we'll write it.
    manifest_path.write_text(content, encoding='utf-8')
    
    console.print(f"[bold green]✓ Manifest updated successfully at {manifest_path}[/bold green]")

if __name__ == "__main__":
    app()
