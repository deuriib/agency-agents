import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ToolDefinition(BaseModel):
    id: str
    label: str
    short: str
    kebab: str
    accent: str
    icon: Optional[str] = None
    order: int
    scope: Dict[str, bool]
    detect: Dict[str, Any]
    version: Dict[str, Any]
    format: str
    installKind: str
    slugFrom: Optional[str] = None
    slugPrefix: Optional[str] = None
    dest: Dict[str, List[str]]

class ToolsCatalog(BaseModel):
    tools: Dict[str, ToolDefinition]

class DivisionDefinition(BaseModel):
    label: str
    icon: str
    color: str

class DivisionsCatalog(BaseModel):
    divisions: Dict[str, DivisionDefinition]

class RunbookRosterGroup(BaseModel):
    """One activation phase of a runbook roster (``group`` is the prose label)."""
    group: str
    activation: str
    agents: List[str] = Field(default_factory=list)

class RunbookDefinition(BaseModel):
    """A NEXUS scenario runbook: prose doc plus the machine-readable roster."""
    slug: str
    title: str
    mode: str
    duration: str
    summary: str
    doc: str
    roster: List[RunbookRosterGroup] = Field(default_factory=list)

class RunbooksCatalog(BaseModel):
    _note: Optional[str] = None
    runbooks: List[RunbookDefinition] = Field(default_factory=list)

class CatalogManager:
    """
    Provides centralized access to project source-of-truth JSON files.
    Replaces the implicit JSON usage in scripts/check-*.sh.
    """
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir

    def load_tools(self) -> ToolsCatalog:
        path = self.root_dir / "tools.json"
        with open(path, 'r', encoding='utf-8') as f:
            return ToolsCatalog(**json.load(f))

    def load_divisions(self) -> DivisionsCatalog:
        path = self.root_dir / "divisions.json"
        with open(path, 'r', encoding='utf-8') as f:
            return DivisionsCatalog(**json.load(f))

    def load_runbooks(self) -> RunbooksCatalog:
        path = self.root_dir / "strategy" / "runbooks.json"
        with open(path, 'r', encoding='utf-8') as f:
            return RunbooksCatalog(**json.load(f))


def _is_catalog_root(path: Path) -> bool:
    """True when ``path`` holds the two catalog anchor files."""
    return (path / "tools.json").is_file() and (path / "divisions.json").is_file()


def _bundled_catalog_root() -> Path:
    """Return the catalog directory bundled inside the installed package."""
    from importlib import resources

    # Wheels are installed unpacked, so ``files()`` yields a real directory path
    # rather than a location inside a zip archive.
    return Path(str(resources.files("agency_agents.data")))


def resolve_catalog_root() -> Path:
    """Return the directory that holds the agent catalog.

    A repository checkout wins when the process runs from one: the long-standing
    development and CI workflow keeps ``tools.json``, ``divisions.json`` and the
    division directories in the working directory. Otherwise the catalog bundled
    into the installed wheel is used, so ``pip install py-agency-agents`` works
    without a clone. ``Path.cwd()`` is the final fallback so the pre-existing
    error surfaces are unchanged when neither location is a catalog.
    """
    cwd = Path.cwd()
    if _is_catalog_root(cwd):
        return cwd
    bundled = _bundled_catalog_root()
    if _is_catalog_root(bundled):
        return bundled
    return cwd
