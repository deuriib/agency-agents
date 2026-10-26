import pytest
from pathlib import Path
from agency_agents.core.converter import ConverterEngine, RenderContext
from agency_agents.core.models import Agent, AgentFrontmatter
from agency_agents.infrastructure.catalog import CatalogManager

def test_identity_renderer():
    engine = ConverterEngine(Path("."))
    agent = Agent(slug="test", path="p", frontmatter=AgentFrontmatter(name="T"), body="Hello")
    outputs = engine.convert_agent_for_tool(agent, "claude-code") # identity format
    assert outputs[0] == ("agent.md", "Hello")

def test_qwen_tool_mapping():
    engine = ConverterEngine(Path("."))
    fm = AgentFrontmatter(name="T", extra={"tools": "Read, Bash"})
    agent = Agent(slug="test", path="p", frontmatter=fm, body="Hello")
    # Manually override tool format for test if needed, but qwen-md is mapped to QwenRenderer
    outputs = engine.convert_agent_for_tool(agent, "qwen")
    assert "ReadFile" in outputs[0][1]
    assert "Shell" in outputs[0][1]

def test_vibe_multi_file():
    engine = ConverterEngine(Path("."))
    fm = AgentFrontmatter(name="VibeAgent", color="#FF0000")
    agent = Agent(slug="vibe", path="p", frontmatter=fm, body="Vibe Body")
    outputs = engine.convert_agent_for_tool(agent, "vibe")
    assert len(outputs) == 2
    assert outputs[0][0] == "agent.toml"
    assert outputs[1][0] == "prompt.md"
