import pytest
from pathlib import Path
from agency_agents.core.converter import ConverterEngine, UnknownFormatError
from agency_agents.core.models import Agent, AgentFrontmatter
from agency_agents.infrastructure.catalog import CatalogManager

def test_roster_content_generation(tmp_path):
    # Setup a roster tool in a dummy catalog
    import json
    tools = {"tools": {"aider": {"id":"a","label":"Aider","short":"A","kebab":"aider","accent":"#000","icon":None,"order":1,"scope":{"user":True,"project":True},"detect":{"dirs":[],"agentsDir":None},"version":{"bin":"a","args":[]},"format":"identity","installKind":"roster","slugFrom":None,"dest":{"user":[],"project":["CONVENTIONS.md"]}}}}
    with open(tmp_path / "tools.json", "w") as f:
        json.dump(tools, f)

    from agency_agents.infrastructure.installer import InstallationManager
    installer = InstallationManager(tmp_path, tmp_path / "home")
    
    fm1 = AgentFrontmatter(name="Agent 1")
    agent1 = Agent(slug="a1", path="p1", frontmatter=fm1, body="Body 1")
    fm2 = AgentFrontmatter(name="Agent 2")
    agent2 = Agent(slug="a2", path="p2", frontmatter=fm2, body="Body 2")
    
    installer.install_roster([agent1, agent2], "aider", "project")
    
    result_file = tmp_path / "CONVENTIONS.md"
    assert result_file.exists()
    content = result_file.read_text()
    assert "Agent 1" in content
    assert "Body 1" in content
    assert "Agent 2" in content
    assert "Body 2" in content

def test_parallel_conversion_accuracy(tmp_path):
    import json
    tools = {"tools": {"claude-code": {"id":"cc","label":"C","short":"C","kebab":"claude-code","accent":"#000","icon":None,"order":1,"scope":{"user":True,"project":True},"detect":{"dirs":[],"agentsDir":None},"version":{"bin":"c","args":[]},"format":"identity","installKind":"per-agent","slugFrom":"source","dest":{"user":[".claude/agents/{slug}.md"],"project":[]}}}}
    with open(tmp_path / "tools.json", "w") as f:
        json.dump(tools, f)
        
    engine = ConverterEngine(tmp_path)
    agents = [
        Agent(slug=f"agent-{i}", path="p", frontmatter=AgentFrontmatter(name=f"N{i}"), body=f"B{i}")
        for i in range(10)
    ]
    
    results = engine.convert_all_parallel(agents, "claude-code", jobs=2)
    assert len(results) == 10
    for agent in agents:
        # Invariant: the parallel path must produce byte-identical output
        # to the sequential path for the same agent + tool.
        expected = engine.convert_agent_for_tool(agent, "claude-code")
        assert results[agent.slug] == expected

def test_missing_tool_conversion(tmp_path):
    import json
    # Must have tools.json even if the specific tool is missing
    with open(tmp_path / "tools.json", "w") as f:
        json.dump({"tools": {}}, f)
        
    engine = ConverterEngine(tmp_path)
    agent = Agent(slug="test", path="p", frontmatter=AgentFrontmatter(name="T"), body="B")
    outputs = engine.convert_agent_for_tool(agent, "non-existent-tool")
    assert outputs == []


def test_unknown_format_fails_loudly(tmp_path):
    """A tools.json typo must not fall back to identity rendering."""
    import json
    tools = {"tools": {"mystery": {"id":"m","label":"M","short":"M","kebab":"mystery","accent":"#000","icon":None,"order":1,"scope":{"user":True,"project":True},"detect":{"dirs":[],"agentsDir":None},"version":{"bin":"m","args":[]},"format":"does-not-exist","installKind":"per-agent","slugFrom":"name","dest":{"user":[".mystery/{slug}.md"],"project":[]}}}}
    (tmp_path / "tools.json").write_text(json.dumps(tools))

    engine = ConverterEngine(tmp_path)
    agent = Agent(slug="test", path="p", frontmatter=AgentFrontmatter(name="T"), body="B")

    with pytest.raises(UnknownFormatError, match="does-not-exist"):
        engine.convert_agent_for_tool(agent, "mystery")
    with pytest.raises(UnknownFormatError, match="unknown-format"):
        engine.get_renderer("unknown-format")
