import pytest
from pathlib import Path
from agency_agents.infrastructure.installer import InstallationManager
from agency_agents.core.models import Agent, AgentFrontmatter

def test_path_resolution(tmp_path):
    installer = InstallationManager(tmp_path, tmp_path / "home")
    # User scope
    path = installer.resolve_path(".config/agents/{slug}.md", "my-agent", "user")
    assert path == tmp_path / "home" / ".config/agents/my-agent.md"
    # Project scope
    path = installer.resolve_path(".opencode/agents/{slug}.md", "my-agent", "project")
    assert path == tmp_path / ".opencode/agents/my-agent.md"

def test_collision_detection(tmp_path):
    installer = InstallationManager(tmp_path, tmp_path / "home")
    fm = AgentFrontmatter(name="Agent")
    # Two agents that would result in the same slug
    agent1 = Agent(slug="collision", path="p1", frontmatter=fm, body="b1")
    agent2 = Agent(slug="collision", path="p2", frontmatter=fm, body="b2")
    
    import json
    tools = {"tools": {"claude-code": {"id":"cc","label":"CC","short":"C","kebab":"claude-code","accent":"#000","icon":None,"order":1,"scope":{"user":True,"project":True},"detect":{"dirs":[],"agentsDir":None},"version":{"bin":"c","args":[]},"format":"identity","installKind":"per-agent","slugFrom":"source","dest":{"user":[".claude/agents/{slug}.md"],"project":[]}}}}
    with open(tmp_path / "tools.json", "w") as f:
        json.dump(tools, f)
    collisions = installer.check_collisions([agent1, agent2], "claude-code")
    assert len(collisions) > 0
    assert "Collision" in collisions[0]

def test_roster_installation(tmp_path):
    installer = InstallationManager(tmp_path, tmp_path / "home")
    fm = AgentFrontmatter(name="A1")
    agent1 = Agent(slug="a1", path="p1", frontmatter=fm, body="b1")
    fm2 = AgentFrontmatter(name="A2")
    agent2 = Agent(slug="a2", path="p2", frontmatter=fm2, body="b2")
    
    # Mock tool as roster
    import json
    tools = {"tools": {"aider": {"id":"a","label":"A","short":"S","kebab":"aider","accent":"#000","icon":None,"order":1,"scope":{"user":True,"project":True},"detect":{"dirs":[],"agentsDir":None},"version":{"bin":"a","args":[]},"format":"identity","installKind":"roster","slugFrom":None,"dest":{"user":[],"project":["CONVENTIONS.md"]}}}}
    with open(tmp_path / "tools.json", "w") as f:
        json.dump(tools, f)
    installer.catalog.load_tools().tools["aider"].installKind = "roster"
    installer.catalog.load_tools().tools["aider"].dest = {"project": ["CONVENTIONS.md"]}
    
    installer.install_roster([agent1, agent2], "aider", "project")
    
    result_file = tmp_path / "CONVENTIONS.md"
    assert result_file.exists()
    content = result_file.read_text()
    assert "A1" in content
    assert "A2" in content
