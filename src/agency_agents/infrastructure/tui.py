from typing import List, Tuple
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

class TUIWizard:
    """
    Interactive wizard for selecting tools and divisions for installation.
    Migrates the interactive mode of scripts/install.sh.
    """
    def __init__(self, root_dir: Path, catalog_manager):
        self.root_dir = root_dir
        self.catalog = catalog_manager
        self.console = Console()

    def select_tools(self) -> List[str]:
        """Prompts the user to select which tools to install."""
        tools = self.catalog.load_tools().tools
        tool_list = list(tools.keys())
        
        self.console.print(Panel("[bold blue]Tool Selection[/bold blue]\nType tool names separated by commas, or 'all' for everything."))
        
        completer = WordCompleter(tool_list)
        user_input = prompt("Select tools: ", completer=completer).strip().lower()

        if user_input == 'all' or not user_input:
            return tool_list
        
        selected = [t.strip() for t in user_input.split(',') if t.strip()]
        # Validate selection
        valid = [t for t in selected if t in tools]
        
        if len(valid) < len(selected):
            invalid = set(selected) - set(valid)
            self.console.print(f"[yellow]Warning: Ignoring unknown tools: {', '.join(invalid)}[/yellow]")
            
        return valid

    def select_divisions(self) -> List[str]:
        """Prompts the user to select which divisions to install."""
        divisions = self.catalog.load_divisions().divisions
        div_list = list(divisions.keys())
        
        self.console.print(Panel("[bold blue]Division Selection[/bold blue]\nType division names separated by commas, or 'all' for everything."))
        
        completer = WordCompleter(div_list)
        user_input = prompt("Select divisions: ", completer=completer).strip().lower()

        if user_input == 'all' or not user_input:
            return div_list
        
        selected = [d.strip() for d in user_input.split(',') if d.strip()]
        valid = [d for d in selected if d in divisions]
        
        if len(valid) < len(selected):
            invalid = set(selected) - set(valid)
            self.console.print(f"[yellow]Warning: Ignoring unknown divisions: {', '.join(invalid)}[/yellow]")
            
        return valid
