import pytest
from pathlib import Path
from agency_agents.infrastructure.installer import InstallationManager
from agency_agents.core.models import Agent, AgentFrontmatter

def test_install_plugin_missing_script(tmp_path):
    installer = InstallationManager(tmp_path, tmp_path / "home")
    import json
    tools = {"tools": {"hermes": {"id":"h","label":"H","short":"H","kebab":"hermes","accent":"#000","icon":None,"order":1,"scope":{"user":True,"project":False},"detect":{"dirs":[],"agentsDir":None},"version":{"bin":"h","args":[]},"format":"plugin","installKind":"plugin","slugFrom":None,"dest":{"user":[".hermes/plugins/router"],"project":[]}}}}
    with open(tmp_path / "tools.json", "w") as f:
        json.dump(tools, f)
        
    with pytest.raises(RuntimeError, match="Hermes build script not found"):
        installer.install_plugin("hermes", "user")

def test_install_plugin_execution_failure(tmp_path):
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    build_script = scripts_dir / "build-hermes-plugin.py"
    build_script.write_text("import sys\nsys.exit(1)")
    
    installer = InstallationManager(tmp_path, tmp_path / "home")
    import json
    tools = {"tools": {"hermes": {"id":"h","label":"H","short":"H","kebab":"hermes","accent":"#000","icon":None,"order":1,"scope":{"user":True,"project":False},"detect":{"dirs":[],"agentsDir":None},"version":{"bin":"h","args":[]},"format":"plugin","installKind":"plugin","slugFrom":None,"dest":{"user":[".hermes/plugins/router"],"project":[]}}}}
    with open(tmp_path / "tools.json", "w") as f:
        json.dump(tools, f)
        
    with pytest.raises(RuntimeError, match="Hermes plugin build failed"):
        installer.install_plugin("hermes", "user")

def test_installation_scope_project_success(tmp_path):
    installer = InstallationManager(tmp_path, tmp_path / "home")
    import json
    tools = {"tools": {"opencode": {"id":"o","label":"O","short":"O","kebab":"opencode","accent":"#000","icon":None,"order":1,"scope":{"user":True,"project":True},"detect":{"dirs":[],"agentsDir":None},"version":{"bin":"o","args":[]},"format":"identity","installKind":"per-agent","slugFrom":"name","dest":{"user":[],"project":[".opencode/agents/{slug}.md"]}}}}
    with open(tmp_path / "tools.json", "w") as f:
        json.dump(tools, f)
        
    agent = Agent(slug="test-agent", path="p", frontmatter=AgentFrontmatter(name="T"), body="B")
    installer.install_agent_for_tool(agent, "opencode", scope="project")
    
    assert (tmp_path / ".opencode/agents/test-agent.md").exists()
