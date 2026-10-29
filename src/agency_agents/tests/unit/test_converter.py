import pytest
from pathlib import Path
from agency_agents.core.converter import ConverterEngine, RenderContext
from agency_agents.core.models import Agent, AgentFrontmatter
from agency_agents.infrastructure.catalog import CatalogManager

def test_identity_renderer():
    engine = ConverterEngine(Path("."))
    agent = Agent(slug="test", path="p", frontmatter=AgentFrontmatter(name="T"), body="Hello")
    outputs = engine.convert_agent_for_tool(agent, "claude-code") # identity format
    assert "Hello" in outputs[0][1]
    assert "name: T" in outputs[0][1]

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

def test_antigravity_overrides():
    """Verify that AntigravityRenderer correctly injects subagent: true."""
    engine = ConverterEngine(Path("."))
    fm = AgentFrontmatter(name="AntiTest")
    agent = Agent(slug="anti", path="p", frontmatter=fm, body="Body")
    outputs = engine.convert_agent_for_tool(agent, "antigravity")
    
    assert "subagent: true" in outputs[0][1]
    assert "name: AntiTest" in outputs[0][1]

def test_opencode_overrides():
    """Verify that OpencodeRenderer correctly injects mode: subagent."""
    engine = ConverterEngine(Path("."))
    fm = AgentFrontmatter(name="OpenTest")
    agent = Agent(slug="open", path="p", frontmatter=fm, body="Body")
    outputs = engine.convert_agent_for_tool(agent, "opencode")
    
    assert "mode: subagent" in outputs[0][1]
    assert "name: OpenTest" in outputs[0][1]

def test_opencode_primary_mode():
    """The orchestrator is rendered as a primary agent in opencode."""
    engine = ConverterEngine(Path("."))
    fm = AgentFrontmatter(name="Agents Orchestrator")
    agent = Agent(slug="agents-orchestrator", path="p", frontmatter=fm, body="Body")
    outputs = engine.convert_agent_for_tool(agent, "opencode")

    assert "mode: primary" in outputs[0][1]
    assert "mode: subagent" not in outputs[0][1]

def test_antigravity_primary_mode():
    """The orchestrator becomes a main agent, not a subagent."""
    engine = ConverterEngine(Path("."))
    fm = AgentFrontmatter(name="Agents Orchestrator")
    agent = Agent(slug="agents-orchestrator", path="p", frontmatter=fm, body="Body")
    outputs = engine.convert_agent_for_tool(agent, "antigravity")

    assert "mainAgent: true" in outputs[0][1]
    assert "subagent: true" not in outputs[0][1]

def test_render_policy_is_scoped_to_orchestrator():
    """Primary status is a render-level policy, not agent content."""
    from agency_agents.core.converter import PRIMARY_AGENT_SLUGS

    assert PRIMARY_AGENT_SLUGS == frozenset({"agents-orchestrator"})

def test_identity_has_no_mode():
    """mode/mainAgent are render directives; tool-agnostic output carries none."""
    engine = ConverterEngine(Path("."))
    fm = AgentFrontmatter(name="Agents Orchestrator")
    agent = Agent(slug="agents-orchestrator", path="p", frontmatter=fm, body="Body")
    outputs = engine.convert_agent_for_tool(agent, "claude-code")

    assert "mode:" not in outputs[0][1]
    assert "mainAgent:" not in outputs[0][1]
    assert "subagent:" not in outputs[0][1]

def test_identity_no_overrides():
    """Verify that standard identity tools do not get extra properties."""
    engine = ConverterEngine(Path("."))
    fm = AgentFrontmatter(name="Standard")
    agent = Agent(slug="std", path="p", frontmatter=fm, body="Body")
    outputs = engine.convert_agent_for_tool(agent, "claude-code")
    
    assert "mode: subagent" not in outputs[0][1]
