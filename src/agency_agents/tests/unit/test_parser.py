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

def test_parser_invalid_frontmatter_fields():
    content = "---\nwrong_field: value\n---\nBody"
    parser = MarkdownParser()
    agent = parser.create_agent("test.md", content)
    assert agent is None
