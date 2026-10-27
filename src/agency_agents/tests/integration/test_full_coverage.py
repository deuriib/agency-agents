import pytest
from pathlib import Path
import json
from agency_agents.core.models import Agent, AgentFrontmatter
from agency_agents.core.converter import ConverterEngine
from agency_agents.infrastructure.installer import InstallationManager

@pytest.fixture
def project_env(tmp_path):
    """Sets up a project environment with a full tools.json catalog."""
    tools_data = {
        "tools": {
            "claude-code": {"id":"cc","label":"Claude Code","short":"Claude","kebab":"claude-code","accent":"#D97757","icon":"claudecode","order":1,"scope":{"user":True,"project":True},"detect":{"dirs":[".claude"],"agentsDir":".claude/agents"},"version":{"bin":"claude","args":["--version"]},"format":"identity","installKind":"per-agent","slugFrom":"source","dest":{"user":[".claude/agents/{slug}.md"],"project":[".claude/agents/{slug}.md"]}},
            "codex": {"id":"codex","label":"Codex","short":"Codex","kebab":"codex","accent":"#10A37F","icon":"codex","order":2,"scope":{"user":True,"project":True},"detect":{"dirs":[".codex"],"agentsDir":".codex/agents"},"version":{"bin":"codex","args":["--version"]},"format":"codex-toml","installKind":"per-agent","slugFrom":"name","dest":{"user":[".codex/agents/{slug}.toml"],"project":[".codex/agents/{slug}.toml"]}},
            "gemini-cli": {"id":"geminiCli","label":"Gemini CLI","short":"Gemini","kebab":"gemini-cli","accent":"#4285F4","icon":"geminicli","order":3,"scope":{"user":True,"project":True},"detect":{"dirs":[".gemini/agents"],"agentsDir":".gemini/agents"},"version":{"bin":"gemini","args":["--version"]},"format":"gemini-md","installKind":"per-agent","slugFrom":"name","dest":{"user":[".gemini/agents/{slug}.md"],"project":[".gemini/agents/{slug}.md"]}},
            "copilot": {"id":"copilot","label":"GitHub Copilot","short":"Copilot","kebab":"copilot","accent":"#6E40C9","icon":"githubcopilot","order":4,"scope":{"user":True,"project":True},"detect":{"dirs":[".github",".copilot"],"agentsDir":".github/agents"},"version":{"bin":"gh","args":["copilot","--version"]},"format":"identity","installKind":"per-agent","slugFrom":"source","dest":{"user":[".copilot/agents/{slug}.md",".github/agents/{slug}.md"],"project":[".github/agents/{slug}.md"]}},
            "qwen": {"id":"qwen","label":"Qwen Code","short":"Qwen","kebab":"qwen","accent":"#615CED","icon":"qwen","order":5,"scope":{"user":True,"project":True},"detect":{"dirs":[".qwen"],"agentsDir":".qwen/agents"},"version":{"bin":"qwen","args":["--version"]},"format":"qwen-md","installKind":"per-agent","slugFrom":"name","dest":{"user":[".qwen/agents/{slug}.md"],"project":[".qwen/agents/{slug}.md"]}},
            "cursor": {"id":"cursor","label":"Cursor","short":"Cursor","kebab":"cursor","accent":"#1F2430","icon":"cursor","order":6,"scope":{"user":False,"project":True},"detect":{"dirs":[".cursor"],"agentsDir":None},"version":{"bin":"cursor","args":["--version"]},"format":"cursor-mdc","installKind":"per-agent","slugFrom":"name","dest":{"user":[],"project":[".cursor/rules/{slug}.mdc"]}},
            "opencode": {"id":"opencode","label":"opencode","short":"opencode","kebab":"opencode","accent":"#FF6B35","icon":"opencode","order":7,"scope":{"user":True,"project":True},"detect":{"dirs":[".config/opencode"],"agentsDir":None},"version":{"bin":"opencode","args":["--version"]},"format":"opencode-md","installKind":"per-agent","slugFrom":"name","dest":{"user":[".config/opencode/agents/{slug}.md"],"project":[".opencode/agents/{slug}.md"]}},
            "osaurus": {"id":"osaurus","label":"Osaurus","short":"Osaurus","kebab":"osaurus","accent":"#10B981","icon":None,"order":8,"scope":{"user":True,"project":False},"detect":{"dirs":[".osaurus"],"agentsDir":".osaurus/skills"},"version":{"bin":"osaurus","args":["--version"]},"format":"skill-md","installKind":"per-agent","slugFrom":"name","slugPrefix":"agency-","dest":{"user":[".osaurus/skills/{slug}/SKILL.md"],"project":[]}},
            "aider": {"id":"aider","label":"Aider","short":"Aider","kebab":"aider","accent":"#8B5CF6","icon":None,"order":9,"scope":{"user":False,"project":True},"detect":{"dirs":[],"agentsDir":None},"version":{"bin":"aider","args":["--version"]},"format":"aider-conventions","installKind":"roster","slugFrom":None,"dest":{"user":[],"project":["CONVENTIONS.md"]}},
            "antigravity": {"id":"antigravity","label":"Antigravity","short":"antigravity","kebab":"antigravity","accent":"#0EA5E9","icon":"antigravity","order":10,"scope":{"user":True,"project":True},"detect":{"dirs":[".gemini/config/skills",".agents/skills"],"agentsDir":".gemini/config/skills"},"version":{"bin":"agy","args":["--version"]},"format":"skill-md","installKind":"per-agent","slugFrom":"name","slugPrefix":"agency-","dest":{"user":[".gemini/config/skills/{slug}/SKILL.md"],"project":[".agents/skills/{slug}/SKILL.md"]}},
            "kimi": {"id":"kimi","label":"Kimi","short":"Kimi","kebab":"kimi","accent":"#0F0F12","icon":"kimi","order":11,"scope":{"user":True,"project":False},"detect":{"dirs":[],"agentsDir":".config/kimi/agents"},"version":{"bin":"kimi","args":["--version"]},"format":"kimi-agent","installKind":"per-agent","slugFrom":"name","dest":{"user":[".config/kimi/agents/{slug}/agent.yaml",".config/kimi/agents/{slug}/system.md"],"project":[]}},
            "openclaw": {"id":"openclaw","label":"OpenClaw","short":"openclaw","kebab":"openclaw","accent":"#E11D48","icon":None,"order":12,"scope":{"user":True,"project":False},"detect":{"dirs":[".openclaw"],"agentsDir":".openclaw/agency-agents"},"version":{"bin":"openclaw","args":["--version"]},"format":"openclaw-workspace","installKind":"per-agent","slugFrom":"name","dest":{"user":[".openclaw/agency-agents/{slug}/SOUL.md",".openclaw/agency-agents/{slug}/AGENTS.md",".openclaw/agency-agents/{slug}/IDENTITY.md"],"project":[]}},
            "windsurf": {"id":"windsurf","label":"Windsurf","short":"Windsurf","kebab":"windsurf","accent":"#09B6A2","icon":"windsurf","order":13,"scope":{"user":False,"project":True},"detect":{"dirs":[".codeium"],"agentsDir":None},"version":{"bin":"windsurf","args":["--version"]},"format":"windsurf-rules","installKind":"roster","slugFrom":None,"dest":{"user":[],"project":[".windsurfrules"]}},
            "hermes": {"id":"hermes","label":"Hermes","short":"Hermes","kebab":"hermes","accent":"#7C3AED","icon":None,"order":14,"scope":{"user":True,"project":False},"detect":{"dirs":[".hermes"],"agentsDir":".hermes/plugins"},"version":{"bin":"hermes","args":["--version"]},"format":"hermes-router-plugin","installKind":"plugin","slugFrom":None,"dest":{"user":[".hermes/plugins/agency-agents-router"],"project":[]}},
            "vibe": {"id":"vibe","label":"Mistral Vibe","short":"Vibe","kebab":"vibe","accent":"#FA520F","icon":None,"order":15,"scope":{"user":True,"project":True},"detect":{"dirs":[".vibe"],"agentsDir":".vibe/agents"},"version":{"bin":"vibe","args":["--version"]},"format":"vibe-toml","installKind":"per-agent","slugFrom":"name","dest":{"user":[".vibe/agents/{slug}.toml",".vibe/prompts/{slug}.md"],"project":[".vibe/agents/{slug}.toml",".vibe/prompts/{slug}.md"]}},
            "zcode": {"id":"zcode","label":"ZCode","short":"ZCode","kebab":"zcode","accent":"#4263EB","icon":"zcode","order":16,"scope":{"user":True,"project":True},"detect":{"dirs":[".zcode"],"agentsDir":".zcode/agents"},"version":{"bin":"zcode","args":["--version"]},"format":"zcode-md","installKind":"per-agent","slugFrom":"name","dest":{"user":[".zcode/agents/{slug}.md"],"project":[".zcode/agents/{slug}.md"]}},
            "dsh": {"id":"deepseekHarness","label":"DeepSeek Harness","short":"DSH","kebab":"dsh","accent":"#4D6BFE","icon":None,"order":17,"scope":{"user":True,"project":True},"detect":{"dirs":[".dsh"],"agentsDir":".dsh/skills"},"version":{"bin":"dsh","args":["--version"]},"format":"skill-md","installKind":"per-agent","slugFrom":"name","slugPrefix":"agency-","dest":{"user":[".dsh/skills/{slug}/SKILL.md"],"project":[".dsh/skills/{slug}/SKILL.md"]}}
        }
    }
    with open(tmp_path / "tools.json", "w") as f:
        json.dump(tools_data, f)
    return tmp_path

def test_all_tools_installation(project_env):
    """Verifies that every tool in tools.json can be processed without crashing."""
    root = project_env
    installer = InstallationManager(root, root / "home")
    fm = AgentFrontmatter(name="Global Agent")
    agent = Agent(slug="global-agent", path="p", frontmatter=fm, body="Global Body")
    
    tools = installer.catalog.load_tools().tools.keys()
    for tool_kebab in tools:
        # We use try-except because some plugins might fail if the build script is missing
        # but the logic should not crash.
        try:
            installer.install_agent_for_tool(agent, tool_kebab, scope="user")
        except RuntimeError as e:
            if "Hermes build script not found" in str(e):
                continue # Expected if script isn't in tmp_path
            raise e

def test_tool_specific_formats(project_env):
    root = project_env
    engine = ConverterEngine(root)
    fm = AgentFrontmatter(name="Tool Test", extra={"tools": "Read, Bash"})
    agent = Agent(slug="test", path="p", frontmatter=fm, body="Body")
    
    # Test Qwen mapping specifically
    qwen_out = engine.convert_agent_for_tool(agent, "qwen")
    assert "ReadFile" in qwen_out[0][1]
    assert "Shell" in qwen_out[0][1]
    
    # Test Vibe multi-file
    vibe_out = engine.convert_agent_for_tool(agent, "vibe")
    assert len(vibe_out) == 2
    assert vibe_out[0][0] == "agent.toml"
    assert vibe_out[1][0] == "prompt.md"

def test_roster_tools_consolidation(project_env):
    root = project_env
    installer = InstallationManager(root, root / "home")
    agents = [
        Agent(slug="a1", path="p1", frontmatter=AgentFrontmatter(name="Agent 1"), body="B1"),
        Agent(slug="a2", path="p2", frontmatter=AgentFrontmatter(name="Agent 2"), body="B2"),
    ]
    
    # Aider is a roster tool
    installer.install_all_for_tool(agents, "aider", scope="project")
    assert (root / "CONVENTIONS.md").exists()
    content = (root / "CONVENTIONS.md").read_text()
    assert "Agent 1" in content and "Agent 2" in content

def test_edge_case_empty_body(project_env):
    root = project_env
    engine = ConverterEngine(root)
    agent = Agent(slug="empty", path="p", frontmatter=AgentFrontmatter(name="Empty"), body="")
    outputs = engine.convert_agent_for_tool(agent, "claude-code")
    content = outputs[0][1]
    # Invariant: an empty body still produces a valid agent document with frontmatter.
    assert "name: Empty" in content
    assert content.endswith("---\n")

def test_edge_case_extreme_tags(project_env):
    root = project_env
    engine = ConverterEngine(root)
    fm = AgentFrontmatter(name="T", tags=["A"*100, "B"*100])
    agent = Agent(slug="t", path="p", frontmatter=fm, body="B")
    outputs = engine.convert_agent_for_tool(agent, "openclaw")
    # Verify IDENTITY.md has tags
    identity_content = next(c for n, c in outputs if n == "IDENTITY.md")
    assert "A"*100 in identity_content
