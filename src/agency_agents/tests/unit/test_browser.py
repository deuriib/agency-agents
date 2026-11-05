"""The browse/search/select model behind the interactive TUI.

These tests hold themselves to the condition tool decision D-001 placed on
adopting prompt-toolkit (`docs/dx/m7-tool-decisions.md`): every behaviour the
browser claims is asserted against the pure model and its key handler, with no
terminal involved. If a behaviour can only be observed by driving a TUI, it is
not covered here and the decision's premise is broken.
"""

from __future__ import annotations

from typing import Dict, List

import pytest

from agency_agents.core.models import Agent, AgentFrontmatter
from agency_agents.infrastructure.browser import (
    ABORT,
    ACCEPT,
    CONTINUE,
    PAGE_SIZE,
    BrowserModel,
    BrowserRow,
    apply_key,
    build_rows,
    slugs_for_division,
)


def make_agent(slug: str, name: str, description: str = "A test agent.") -> Agent:
    return Agent(
        slug=slug,
        path=f"/tmp/{slug}.md",
        frontmatter=AgentFrontmatter(name=name, description=description),
        body="Body",
    )


@pytest.fixture
def roster() -> Dict[str, List[Agent]]:
    return {
        "engineering": [
            make_agent("frontend-developer", "Frontend Developer", "Builds user interfaces."),
            make_agent("backend-architect", "Backend Architect", "Designs APIs."),
        ],
        "marketing": [
            make_agent("growth-hacker", "Growth Hacker", "Runs experiments."),
        ],
    }


# --------------------------------------------------------------------- build_rows


def test_rows_are_ordered_by_division_then_name(roster: Dict[str, List[Agent]]) -> None:
    rows = build_rows(roster)

    assert [(r.division, r.slug) for r in rows] == [
        ("engineering", "backend-architect"),
        ("engineering", "frontend-developer"),
        ("marketing", "growth-hacker"),
    ]


def test_rows_are_stable_regardless_of_input_order(roster: Dict[str, List[Agent]]) -> None:
    reversed_roster = {
        division: list(reversed(agents)) for division, agents in reversed(list(roster.items()))
    }

    assert [r.slug for r in build_rows(roster)] == [r.slug for r in build_rows(reversed_roster)]


def test_empty_roster_produces_no_rows() -> None:
    assert build_rows({}) == []


# ------------------------------------------------------------------------ filter


def test_blank_query_shows_every_row(roster: Dict[str, List[Agent]]) -> None:
    model = BrowserModel(rows=build_rows(roster))

    assert len(model.visible()) == 3


def test_query_matches_slug_name_division_and_description(
    roster: Dict[str, List[Agent]],
) -> None:
    model = BrowserModel(rows=build_rows(roster))

    model.set_query("frontend")
    assert [r.slug for r in model.visible()] == ["frontend-developer"]

    model.set_query("Growth Hacker")
    assert [r.slug for r in model.visible()] == ["growth-hacker"]

    model.set_query("marketing")
    assert [r.slug for r in model.visible()] == ["growth-hacker"]

    model.set_query("designs apis")
    assert [r.slug for r in model.visible()] == ["backend-architect"]


def test_query_is_case_insensitive_and_ignores_surrounding_space(
    roster: Dict[str, List[Agent]],
) -> None:
    model = BrowserModel(rows=build_rows(roster))

    model.set_query("  FRONTEND  ")

    assert [r.slug for r in model.visible()] == ["frontend-developer"]


def test_set_query_resets_the_cursor(roster: Dict[str, List[Agent]]) -> None:
    model = BrowserModel(rows=build_rows(roster))
    model.move(2)

    model.set_query("e")

    assert model.cursor == 0


def test_no_match_yields_no_rows_and_no_current(roster: Dict[str, List[Agent]]) -> None:
    model = BrowserModel(rows=build_rows(roster))

    model.set_query("nothing-matches-this")

    assert model.visible() == []
    assert model.current() is None


# ----------------------------------------------------------------------- movement


def test_move_is_clamped_to_the_visible_rows(roster: Dict[str, List[Agent]]) -> None:
    model = BrowserModel(rows=build_rows(roster))

    model.move(-5)
    assert model.cursor == 0

    model.move(100)
    assert model.cursor == 2


def test_move_is_a_no_op_when_nothing_matches(roster: Dict[str, List[Agent]]) -> None:
    model = BrowserModel(rows=build_rows(roster))
    model.cursor = 3
    model.set_query("no-such-agent")

    model.move(1)

    assert model.cursor == 0
    assert model.current() is None


def test_current_returns_the_row_under_the_cursor(roster: Dict[str, List[Agent]]) -> None:
    model = BrowserModel(rows=build_rows(roster))

    model.move(1)

    assert model.current() is not None
    assert model.current().slug == "frontend-developer"


def test_current_clamps_when_cursor_exceeds_a_narrowed_list(
    roster: Dict[str, List[Agent]],
) -> None:
    model = BrowserModel(rows=build_rows(roster))
    model.cursor = 2
    model.query = "engineering"

    current = model.current()

    assert current is not None
    assert current.slug == "frontend-developer"


# ---------------------------------------------------------------------- selection


def test_toggle_selects_then_deselects_the_current_row(
    roster: Dict[str, List[Agent]],
) -> None:
    model = BrowserModel(rows=build_rows(roster))

    first = model.toggle()
    assert first is not None and first.slug == "backend-architect"
    assert model.selection() == ["backend-architect"]
    assert model.is_selected(first) is True

    second = model.toggle()
    assert second is not None
    assert model.selection() == []


def test_toggle_with_nothing_matching_returns_none(roster: Dict[str, List[Agent]]) -> None:
    model = BrowserModel(rows=build_rows(roster))
    model.set_query("no-such-agent")

    assert model.toggle() is None
    assert model.selection() == []


def test_select_all_visible_only_selects_matching_rows(
    roster: Dict[str, List[Agent]],
) -> None:
    model = BrowserModel(rows=build_rows(roster))
    model.set_query("engineering")

    added = model.select_all_visible()

    assert added == 2
    assert model.selection() == ["backend-architect", "frontend-developer"]


def test_select_all_visible_counts_only_newly_selected_rows(
    roster: Dict[str, List[Agent]],
) -> None:
    model = BrowserModel(rows=build_rows(roster))
    model.toggle()

    assert model.select_all_visible() == 2


def test_selection_is_returned_in_roster_order_not_click_order(
    roster: Dict[str, List[Agent]],
) -> None:
    model = BrowserModel(rows=build_rows(roster))
    model.move(2)
    model.toggle()
    model.move(-2)
    model.toggle()

    assert model.selection() == ["backend-architect", "growth-hacker"]


def test_clear_selection_empties_it(roster: Dict[str, List[Agent]]) -> None:
    model = BrowserModel(rows=build_rows(roster))
    model.select_all_visible()

    model.clear_selection()

    assert model.selection() == []


# ------------------------------------------------------------------------ detail


def test_detail_names_the_agent_division_and_slug(roster: Dict[str, List[Agent]]) -> None:
    model = BrowserModel(rows=build_rows(roster))

    lines = model.detail_lines()

    assert "Backend Architect" in lines[0]
    assert "division: engineering" in lines[1]
    assert "slug: backend-architect" in lines[2]
    assert lines[4] == "Designs APIs."


def test_detail_marks_selection_state(roster: Dict[str, List[Agent]]) -> None:
    model = BrowserModel(rows=build_rows(roster))
    model.toggle()

    assert "[selected]" in model.detail_lines()[0]


def test_detail_falls_back_when_the_description_is_missing() -> None:
    model = BrowserModel(
        rows=[BrowserRow(division="d", slug="s", name="N", description="")]
    )

    assert model.detail_lines()[4] == "(no description)"


def test_detail_explains_an_empty_filter_result(roster: Dict[str, List[Agent]]) -> None:
    model = BrowserModel(rows=build_rows(roster))
    model.set_query("no-such-agent")

    assert model.detail_lines() == ["No agent matches the current filter."]


# ------------------------------------------------------------------------ status


def test_status_reports_total_when_unfiltered(roster: Dict[str, List[Agent]]) -> None:
    model = BrowserModel(rows=build_rows(roster))

    assert model.status_line().startswith("3 agents")


def test_status_reports_shown_over_total_when_filtered(
    roster: Dict[str, List[Agent]],
) -> None:
    model = BrowserModel(rows=build_rows(roster))
    model.set_query("engineering")

    assert model.status_line().startswith("2/3 shown")


def test_status_reports_the_selection_count(roster: Dict[str, List[Agent]]) -> None:
    model = BrowserModel(rows=build_rows(roster))
    model.select_all_visible()

    assert "3 selected" in model.status_line()


# --------------------------------------------------------------------- apply_key


def test_apply_key_moves_the_cursor(roster: Dict[str, List[Agent]]) -> None:
    model = BrowserModel(rows=build_rows(roster))

    assert apply_key(model, "down") == CONTINUE
    assert model.cursor == 1
    assert apply_key(model, "up") == CONTINUE
    assert model.cursor == 0


def test_apply_key_pages_by_the_page_size(roster: Dict[str, List[Agent]]) -> None:
    rows = [
        BrowserRow(division="d", slug=f"agent-{i:03d}", name=f"A{i}", description="")
        for i in range(PAGE_SIZE * 3)
    ]
    model = BrowserModel(rows=rows)

    apply_key(model, "pagedown")
    assert model.cursor == PAGE_SIZE

    apply_key(model, "pageup")
    assert model.cursor == 0


def test_apply_key_toggles_with_tab(roster: Dict[str, List[Agent]]) -> None:
    model = BrowserModel(rows=build_rows(roster))

    apply_key(model, "tab")

    assert model.selection() == ["backend-architect"]


def test_apply_key_select_all_and_clear(roster: Dict[str, List[Agent]]) -> None:
    model = BrowserModel(rows=build_rows(roster))

    apply_key(model, "c-a")
    assert len(model.selection()) == 3

    apply_key(model, "c-x")
    assert model.selection() == []


def test_apply_key_enter_accepts_and_escape_aborts(
    roster: Dict[str, List[Agent]],
) -> None:
    model = BrowserModel(rows=build_rows(roster))

    assert apply_key(model, "enter") == ACCEPT
    assert apply_key(model, "escape") == ABORT
    assert apply_key(model, "c-c") == ABORT


def test_printable_keys_widen_the_filter(roster: Dict[str, List[Agent]]) -> None:
    model = BrowserModel(rows=build_rows(roster))

    for char in "growth":
        assert apply_key(model, char) == CONTINUE

    assert model.query == "growth"
    assert [r.slug for r in model.visible()] == ["growth-hacker"]


def test_backspace_narrows_and_resets_cursor(roster: Dict[str, List[Agent]]) -> None:
    model = BrowserModel(rows=build_rows(roster))
    model.set_query("growth")
    model.cursor = 0

    apply_key(model, "backspace")

    assert model.query == "growt"


def test_ctrl_u_clears_the_query(roster: Dict[str, List[Agent]]) -> None:
    model = BrowserModel(rows=build_rows(roster))
    model.set_query("growth")

    apply_key(model, "c-u")

    assert model.query == ""
    assert len(model.visible()) == 3


def test_unknown_named_keys_are_ignored(roster: Dict[str, List[Agent]]) -> None:
    model = BrowserModel(rows=build_rows(roster))

    assert apply_key(model, "f13") == CONTINUE
    assert model.query == ""


def test_slugs_for_division_filters_by_division(roster: Dict[str, List[Agent]]) -> None:
    rows = build_rows(roster)

    assert slugs_for_division(rows, "marketing") == ["growth-hacker"]
    assert slugs_for_division(rows, "nope") == []
