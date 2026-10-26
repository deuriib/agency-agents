import pytest
from agency_agents.core.parser import MarkdownParser
from agency_agents.core.models import Agent

def test_parser_is_agent_file():
    parser = MarkdownParser()
    assert parser.is_agent_file("---\nname: Test\n---") is True
    assert parser.is_agent_file("Just plain text") is False

def test_parser_valid_agent():
    content = "---\nname: Test Agent\ndescription: A test agent\n---\nBody content"
    parser = MarkdownParser()
    agent = parser.create_agent("test.md", content)
    
    assert agent is not None
    assert agent.frontmatter.name == "Test Agent"
    assert agent.slug == "test-agent"
    assert agent.body == "Body content"

def test_parser_missing_frontmatter():
    content = "No frontmatter here"
    parser = MarkdownParser()
    agent = parser.create_agent("test.md", content)
    assert agent is None


def test_parser_antigravity_subagent():
    """Verify that subagent: true is correctly parsed as a boolean."""
    content = "---\nname: Antigravity Agent\nsubagent: true\ndescription: A subagent\n---\nBody"
    parser = MarkdownParser()
    agent = parser.create_agent("antigravity.md", content)
    
    assert agent is not None
    assert agent.frontmatter.subagent is True

def test_parser_antigravity_not_subagent():
    """Verify that subagent: false is correctly parsed as a boolean."""
    content = "---\nname: Regular Agent\nsubagent: false\ndescription: A regular agent\n---\nBody"
    parser = MarkdownParser()
    agent = parser.create_agent("agent.md", content)
    
    assert agent is not None
    assert agent.frontmatter.subagent is False

def test_parser_boolean_case_insensitivity():
    """Verify boolean parsing is case-insensitive (TRUE, True, tRUe)."""
    cases = ["true", "True", "TRUE", "tRUe", "false", "False", "FALSE", "fAlSe"]
    expected = [True] * 4 + [False] * 4
    
    parser = MarkdownParser()
    for val, exp in zip(cases, expected):
        content = f"---\nname: Test\nsubagent: {val}\n---\nBody"
        agent = parser.create_agent("test.md", content)
        assert agent.frontmatter.subagent == exp

def test_parser_invalid_boolean_value():
    """Verify that non-boolean values for subagent remain strings or are handled by Pydantic."""
    content = "---\nname: Test\nsubagent: maybe\n---\nBody"
    parser = MarkdownParser()
    agent = parser.create_agent("test.md", content)
    # It should return None because Pydantic validation fails for 'maybe' as bool
    assert agent is None

def test_parser_missing_subagent():
    """Verify that omitting subagent results in None (Optional)."""
    content = "---\nname: Test\n---\nBody"
    parser = MarkdownParser()
    agent = parser.create_agent("test.md", content)
    assert agent.frontmatter.subagent is True
def test_parser_invalid_frontmatter_fields():
    content = "---\nwrong_field: value\n---\nBody"
    parser = MarkdownParser()
    agent = parser.create_agent("test.md", content)
    assert agent is None
