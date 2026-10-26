import pytest
from pathlib import Path
from agency_agents.core.models import Agent, AgentFrontmatter, slugify

def test_slugify_basic():
    assert slugify("Frontend Developer") == "frontend-developer"
    assert slugify("  Hello World  ") == "hello-world"

def test_slugify_unicode():
    assert slugify("Agente Niñera") == "agente-ninera"
    assert slugify("Systeḿ") == "system"

def test_slugify_special_chars():
    assert slugify("Agent! @#%^&*() Developer") == "agent-developer"
    assert slugify("Agent--Double--Dash") == "agent-double-dash"

def test_agent_model_validation():
    # Valid model
    fm = AgentFrontmatter(name="Test Agent", description="Desc")
    agent = Agent(slug="test-agent", path="path/to/file.md", frontmatter=fm, body="body")
    assert agent.filename == "test-agent.md"

    # Invalid model (empty name)
    with pytest.raises(ValueError):
        AgentFrontmatter(name="  ")
