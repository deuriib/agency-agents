import re
from typing import Tuple, Optional
from agency_agents.core.models import AgentFrontmatter, Agent, slugify

class MarkdownParser:
    """
    Handles the extraction of frontmatter and body from markdown files.
    Replaces get_field, get_body, and is_agent_file from lib.sh.
    """
    
    FRONTMATTER_PATTERN = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)

    @classmethod
    def is_agent_file(cls, content: str) -> bool:
        return content.startswith("---")

    @classmethod
    def parse(cls, path: str, content: str) -> Tuple[Optional[AgentFrontmatter], str]:
        match = cls.FRONTMATTER_PATTERN.match(content)
        if not match:
            return None, content

        yaml_block = match.group(1)
        body = content[match.end():]
        
        # Simple YAML parsing for now to avoid heavy dependencies immediately, 
        # but structured for Pydantic validation.
        data = {}
        for line in yaml_block.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                data[k.strip()] = v.strip()

        try:
            # We pass everything to Pydantic for validation
            fm = AgentFrontmatter(**data)
            return fm, body
        except Exception:
            # Return raw data as extra if validation fails or handle as needed
            return None, content

    @classmethod
    def create_agent(cls, path: str, content: str) -> Optional[Agent]:
        fm, body = cls.parse(path, content)
        if not fm:
            return None
        
        return Agent(
            slug=slugify(fm.name),
            path=path,
            frontmatter=fm,
            body=body
        )
