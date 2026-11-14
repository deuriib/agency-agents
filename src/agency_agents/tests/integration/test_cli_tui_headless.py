"""Headless exercise of the real `run_install_tui` terminal loop.

The models (`browser.py`) are asserted in `tests/unit/test_browser.py`; these
tests assert the seam that unit suite cannot reach — the prompt-toolkit
`Keys.Any` dispatch in `run_install_tui`. They drive the real `Application`
with a pipe input and `DummyOutput`, so no terminal or pseudo-terminal is
required (the condition D-001 C2 placed on adopting prompt-toolkit).

What is pinned here is the *behaviour a human used to have to catch by hand*:

- the integrated flow walks scope → project path → harness → agents,
- arrow / page keys reach the model as the names it understands,
- escape and ctrl-c always cancel (even with a selection),
- enter is the only key that accepts,
- a bug in the key handler degrades to a clean cancel, never a frozen app.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import List
from unittest import mock

import pytest
from prompt_toolkit.application import create_app_session
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput

from agency_agents.infrastructure.browser import (
    BrowserModel,
    BrowserRow,
    HarnessOption,
    InstallFlow,
)
from agency_agents.infrastructure.browser_app import (
    BrowserCancelled,
    InstallSelection,
    render_harness_screen,
    render_path_screen,
    render_scope_screen,
    run_install_tui,
)


def make_model() -> BrowserModel:
    """Two rows: backend-architect (0), growth-hacker (1)."""
    return BrowserModel(
        rows=[
            BrowserRow("engineering", "backend-architect", "Backend Architect", "Designs APIs."),
            BrowserRow("marketing", "growth-hacker", "Growth Hacker", "Runs experiments."),
        ]
    )


def _tool_catalog() -> dict:
    claude = SimpleNamespace(
        kebab="claude-code", label="Claude Code", order=1,
        dest={"user": [".claude/agents/{slug}.md"], "project": [".claude/agents/{slug}.md"]},
    )
    opencode = SimpleNamespace(
        kebab="opencode", label="opencode", order=2,
        dest={"user": [".config/opencode/agents/{slug}.md"], "project": [".opencode/agents/{slug}.md"]},
    )
    return {"claude-code": claude, "opencode": opencode}


def drive(
    keys: str,
    model: BrowserModel,
    *,
    scope: str | None = "user",
    tool: str | None = "claude-code",
    detected: tuple[str, ...] = (),
) -> InstallSelection:
    """Drive the agents stage directly by presetting scope and tool."""
    with create_pipe_input() as pipe, create_app_session(input=pipe, output=DummyOutput()):
        with mock.patch.object(sys.stdin, "isatty", lambda: True), mock.patch.object(
            sys.stdout, "isatty", lambda: True
        ), mock.patch("shutil.get_terminal_size", lambda: os.terminal_size((80, 24))):
            pipe.send_text(keys)
            return run_install_tui(
                model, _tool_catalog(), detected,
                scope=scope, tool=tool, title="headless",
            )


def drive_full(keys: str, model: BrowserModel, *, detected: tuple[str, ...] = ()) -> InstallSelection:
    """Drive the whole flow from the scope stage (no presets)."""
    with create_pipe_input() as pipe, create_app_session(input=pipe, output=DummyOutput()):
        with mock.patch.object(sys.stdin, "isatty", lambda: True), mock.patch.object(
            sys.stdout, "isatty", lambda: True
        ), mock.patch("shutil.get_terminal_size", lambda: os.terminal_size((80, 24))):
            pipe.send_text(keys)
            return run_install_tui(model, _tool_catalog(), detected, title="headless")


# ------------------------------------------------------------------ agents stage


def test_enter_with_nothing_selected_returns_nothing() -> None:
    assert drive("\r", make_model()).agents == []


def test_tab_then_enter_returns_the_selection() -> None:
    assert drive("\t\r", make_model()).agents == ["backend-architect"]


def test_down_arrow_then_tab_selects_the_second_row() -> None:
    """The view receives Down as the raw escape sequence and must move the cursor."""
    assert drive("\x1b[B\t\r", make_model()).agents == ["growth-hacker"]


def test_up_arrow_is_a_no_op_at_the_top() -> None:
    assert drive("\x1b[A\t\r", make_model()).agents == ["backend-architect"]


def test_page_down_moves_a_full_page() -> None:
    model = BrowserModel(
        rows=[BrowserRow("d", f"a-{i:03d}", f"A{i}", "x") for i in range(30)]
    )
    # PageDown moves PAGE_SIZE (10) rows, then Tab selects the 11th row.
    assert drive("\x1b[6~\t\r", model).agents == ["a-010"]


def test_typing_narrows_the_filter_then_tab_selects_the_only_match() -> None:
    assert drive("growth\t\r", make_model()).agents == ["growth-hacker"]


def test_escape_with_a_selection_cancels() -> None:
    with pytest.raises(BrowserCancelled):
        drive("\t\x1b", make_model())


def test_ctrl_c_with_a_selection_cancels() -> None:
    with pytest.raises(BrowserCancelled):
        drive("\t\x03", make_model())


def test_escape_without_a_selection_cancels() -> None:
    with pytest.raises(BrowserCancelled):
        drive("\x1b", make_model())


def test_an_exception_in_the_key_handler_cancels() -> None:
    """A bad keystroke must never freeze the app in the alternate screen."""
    with mock.patch(
        "agency_agents.infrastructure.browser_app.apply_key",
        side_effect=RuntimeError("boom from apply_key"),
    ):
        with pytest.raises(BrowserCancelled):
            drive("\r", make_model())


# ------------------------------------------------------------------ full flow


def test_full_flow_user_scope_accepts_detected_harness() -> None:
    """Scope (user) → harness (detected default) → agents, all in one screen."""
    result = drive_full("\r\r\t\r", make_model(), detected=("claude-code",))

    assert result.scope == "user"
    assert result.project_root is None
    assert result.tools == ["claude-code"]
    assert result.agents == ["backend-architect"]


def test_full_flow_project_scope_asks_for_a_path() -> None:
    """Project scope routes through the path stage before harness + agents."""
    keys = "\x1b[B\r" + "/tmp/proj\r" + "\r" + "\t\r"
    result = drive_full(keys, make_model(), detected=("claude-code",))

    assert result.scope == "project"
    assert result.project_root == Path("/tmp/proj")
    assert result.tools == ["claude-code"]
    assert result.agents == ["backend-architect"]


def test_scope_escape_cancels_before_anything() -> None:
    with pytest.raises(BrowserCancelled):
        drive_full("\x1b", make_model())


def test_harness_tab_toggles_off_the_detected_default() -> None:
    """Toggling a pre-checked harness deselects it, so the install is empty."""
    # scope: enter (user); harness: tab (deselect claude-code) + enter; agents: enter
    result = drive_full("\r\t\r\r", make_model(), detected=("claude-code",))

    assert result.scope == "user"
    assert result.tools == []


def test_tool_preset_skips_the_harness_stage() -> None:
    """An explicit --tool goes scope → agents, skipping the harness picker."""
    result = drive("\r\t\r", make_model(), scope=None, tool="claude-code")

    assert result.scope == "user"
    assert result.tools == ["claude-code"]
    assert result.agents == ["backend-architect"]


# ------------------------------------------------------------------ pure renderers


def _text(rendered) -> str:
    return "".join(fragment for _, fragment in rendered)


def test_render_scope_screen_marks_the_cursor() -> None:
    assert "Install scope" in _text(render_scope_screen(0))

    styled = [f for s, f in render_scope_screen(1) if s == "class:cursor"]
    assert len(styled) == 1
    assert "project" in styled[0]


def test_render_path_screen_shows_current_and_typed() -> None:
    text = _text(render_path_screen("/srv/app", Path("/tmp/x")))

    assert "Project root" in text
    assert "current: /tmp/x" in text
    assert "install into: /srv/app" in text


def test_render_harness_screen_marks_selected_and_detected() -> None:
    tools = [
        HarnessOption(kebab="claude-code", label="Claude Code", detected=True),
        HarnessOption(kebab="opencode", label="opencode", detected=False),
    ]

    text = _text(render_harness_screen(tools, 0, {"claude-code"}))

    assert "[x] claude-code" in text
    assert "Claude Code" in text
    assert "detected" in text
    assert "[ ] opencode" in text
