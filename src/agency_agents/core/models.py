from pydantic import BaseModel, Field, field_validator
from typing import Dict, Optional, List, Any
import re
import unicodedata

class AgentFrontmatter(BaseModel):
    """
    Represents the YAML frontmatter of an agent file.
    Equivalent to the parsing logic in scripts/lib.sh.
    """
    name: str = Field(..., description="The human-readable name of the agent")
    description: Optional[str] = None
    version: Optional[str] = "1.0.0"
    tags: List[str] = Field(default_factory=list)
    icon: Optional[str] = None
    vibe: Optional[str] = None
    color: Optional[str] = None
    subagent: Optional[bool] = True
    extra: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("name")
    @classmethod
    def name_must_be_present(cls, v):
        if not v or not v.strip():
            raise ValueError("Agent name cannot be empty")
        return v

    def to_yaml(self) -> str:
        """Converts the frontmatter model back to a YAML string."""
        lines = []
        # Explicitly handle standard fields to keep order and formatting
        fields = [
            ("name", self.name),
            ("description", self.description),
            ("version", self.version),
            ("tags", self.tags),
            ("icon", self.icon),
            ("vibe", self.vibe),
            ("color", self.color),
            ("subagent", self.subagent),
        ]
        for k, v in fields:
            if v is not None:
                # Format tags as a simple YAML list
                if isinstance(v, list):
                    if not v: continue
                    v_str = f"[{', '.join(map(str, v))}]"
                else:
                    v_str = str(v).lower() if isinstance(v, bool) else str(v)
                lines.append(f"{k}: {v_str}")
        
        # Add extra fields
        for k, v in self.extra.items():
            lines.append(f"{k}: {v}")
            
        return "\n".join(lines)
class Agent(BaseModel):
    """
    The complete Agent domain model.
    """
    slug: str
    path: str
    frontmatter: AgentFrontmatter
    body: str

    @property
    def filename(self) -> str:
        return f"{self.slug}.md"

def slugify(text: str) -> str:
    """
    Standardized slugification: "Frontend Developer" -> "frontend-developer"
    Replaces the bash slugify implementation in lib.sh.
    """
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '-', text)
