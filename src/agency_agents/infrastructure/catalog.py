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
