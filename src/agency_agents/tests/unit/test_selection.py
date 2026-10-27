from pathlib import Path

import pytest

from agency_agents.core.models import Agent, AgentFrontmatter
from agency_agents.core.selection import (
    SelectionError,
    agent_aliases,
    agent_cap,
    build_roster_index,
    parse_agents_file,
    resolve_agent,
    select_agents,
)


def make_agent(slug: str, name: str, path: str = None) -> Agent:
    return Agent(
        slug=slug,
        path=path or f"{slug}.md",
        frontmatter=AgentFrontmatter(name=name, description="d"),
        body="b",
    )


def test_aliases_cover_slug_name_and_stem():
    agent = make_agent("test-analyst", "Test Analyst", path="testing/test-analyst.md")
    aliases = agent_aliases(agent)
    assert "test-analyst" in aliases          # slug and file stem
    assert "test-analyst" in aliases          # display name slugifies to the same id


def test_alias_display_name_resolves_when_distinct_from_stem():
    agent = make_agent("code-reviewer", "Code Reviewer")
    index = build_roster_index([agent])
    assert resolve_agent("Code Reviewer", index) is agent
    assert resolve_agent("code-reviewer", index) is agent


def test_alias_tolerates_agency_prefix():
    agent = make_agent(
        "agency-neural-network-architect",
        "Neural Network Architect",
        path="specialized/agency-neural-network-architect.md",
    )
    index = build_roster_index([agent])
    assert resolve_agent("neural-network-architect", index) is agent


def test_resolve_unknown_returns_none():
    assert resolve_agent("nobody", build_roster_index([make_agent("a", "A")])) is None


def test_parse_agents_file_strips_comments_and_blanks(tmp_path):
    f = tmp_path / "team.txt"
    f.write_text(
        "# core team\n"
        "code-reviewer\n"
        "\n"
        "devops-automator   # from runbook\n",
        encoding="utf-8",
    )
    assert parse_agents_file(f) == ["code-reviewer", "devops-automator"]


def test_select_by_division_and_agent_union_dedups():
    a = make_agent("a1", "A 1")
    b = make_agent("b1", "B 1")
    by_division = {"eng": [a], "mkt": [b]}
    selected = select_agents(by_division, divisions=["eng"], agent_ids=["B 1"])
    assert sorted(x.slug for x in selected) == ["a1", "b1"]


def test_select_unknown_division_fails_fast():
    with pytest.raises(SelectionError, match="nope"):
        select_agents({"eng": [make_agent("a1", "A 1")]}, divisions=["nope"])


def test_select_unknown_agent_fails_fast():
    with pytest.raises(SelectionError, match="Unknown agent 'ghost'"):
        select_agents({"eng": [make_agent("a1", "A 1")]}, agent_ids=["ghost"])


def test_select_unknown_agents_file_entry_fails_fast(tmp_path):
    f = tmp_path / "team.txt"
    f.write_text("ghost\n", encoding="utf-8")
    with pytest.raises(SelectionError, match="ghost"):
        select_agents({"eng": [make_agent("a1", "A 1")]}, agents_file=f)


def test_empty_agents_file_is_an_error(tmp_path):
    f = tmp_path / "team.txt"
    f.write_text("# only comments\n", encoding="utf-8")
    with pytest.raises(SelectionError, match="No agent ids"):
        select_agents({"eng": [make_agent("a1", "A 1")]}, agents_file=f)


def test_no_filters_returns_everything_once():
    a = make_agent("a1", "A 1")
    by_division = {"eng": [a], "mkt": [a]}  # same agent in two divisions
    selected = select_agents(by_division)
    assert len(selected) == 1 and selected[0].slug == "a1"


def test_unreadable_agents_file_fails_fast_with_message(tmp_path):
    f = tmp_path / "team.txt"
    f.write_bytes(b"\xff\xfe" + "code-reviewer\n".encode("utf-16-le"))
    with pytest.raises(SelectionError, match="not valid UTF-8"):
        select_agents({"eng": [make_agent("a1", "A 1")]}, agents_file=f)


def test_missing_agents_file_fails_fast_with_message(tmp_path):
    with pytest.raises(SelectionError, match="agents-file not found"):
        select_agents({"eng": [make_agent("a1", "A 1")]}, agents_file=tmp_path / "ghost.txt")


def test_opencode_cap_is_soft():
    assert agent_cap("opencode") == 119
    assert agent_cap("claude-code") == 0
