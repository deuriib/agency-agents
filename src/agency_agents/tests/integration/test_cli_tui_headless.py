"""Headless exercise of the real `run_browser` terminal loop.

The model (`browser.py`) is asserted in `tests/unit/test_browser.py`; these tests
assert the seam that unit suite cannot reach — the prompt-toolkit `Keys.Any`
dispatch in `run_browser`. They drive the real `Application` with a pipe input
and `DummyOutput`, so no terminal or pseudo-terminal is required (the condition
D-001 C2 placed on adopting prompt-toolkit).

What is pinned here is the *behaviour a human used to have to catch by hand*:

- arrow / page keys reach the model as the names it understands,
- escape and ctrl-c always cancel (even with a selection),
- enter is the only key that accepts,
- a bug in the key handler degrades to a clean cancel, never a frozen app.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List
from unittest import mock

import pytest
from prompt_toolkit.application import create_app_session
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput

from agency_agents.infrastructure.browser import BrowserModel, BrowserRow
from agency_agents.infrastructure.browser_app import (
    BrowserCancelled,
    choose_project_path,
    choose_scope,
    choose_tools,
    run_browser,
)


def make_model() -> BrowserModel:
    """Two rows: backend-architect (0), growth-hacker (1)."""
    return BrowserModel(
        rows=[
            BrowserRow("engineering", "backend-architect", "Backend Architect", "Designs APIs."),
            BrowserRow("marketing", "growth-hacker", "Growth Hacker", "Runs experiments."),
        ]
    )


def drive(keys: str, model: BrowserModel) -> List[str]:
    """Send raw keystrokes to the real `run_browser` with no terminal attached."""
    with create_pipe_input() as pipe, create_app_session(input=pipe, output=DummyOutput()):
        with mock.patch.object(sys.stdin, "isatty", lambda: True), mock.patch.object(
            sys.stdout, "isatty", lambda: True
        ), mock.patch("shutil.get_terminal_size", lambda: os.terminal_size((80, 24))):
            pipe.send_text(keys)
            return run_browser(model, title="headless")


def test_enter_with_nothing_selected_returns_nothing() -> None:
    assert drive("\r", make_model()) == []


def test_tab_then_enter_returns_the_selection() -> None:
    assert drive("\t\r", make_model()) == ["backend-architect"]


def test_down_arrow_then_tab_selects_the_second_row() -> None:
    """The view receives Down as the raw escape sequence and must move the cursor."""
    assert drive("\x1b[B\t\r", make_model()) == ["growth-hacker"]


def test_up_arrow_is_a_no_op_at_the_top() -> None:
    assert drive("\x1b[A\t\r", make_model()) == ["backend-architect"]


def test_page_down_moves_a_full_page() -> None:
    model = BrowserModel(
        rows=[BrowserRow("d", f"a-{i:03d}", f"A{i}", "x") for i in range(30)]
    )
    # PageDown moves PAGE_SIZE (10) rows, then Tab selects the 11th row.
    assert drive("\x1b[6~\t\r", model) == ["a-010"]


def test_typing_narrows_the_filter_then_tab_selects_the_only_match() -> None:
    assert drive("growth\t\r", make_model()) == ["growth-hacker"]


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


# ------------------------------------------------------------------ tool dialog


def _tool_catalog() -> dict:
    from types import SimpleNamespace

    claude = SimpleNamespace(
        kebab="claude-code", label="Claude Code", order=1,
        dest={"user": [".claude/agents/{slug}.md"], "project": []},
    )
    return {"claude-code": claude}


def _drive_dialog(keys: str) -> None:
    with create_pipe_input() as pipe, create_app_session(input=pipe, output=DummyOutput()):
        with mock.patch.object(sys.stdin, "isatty", lambda: True), mock.patch.object(
            sys.stdout, "isatty", lambda: True
        ):
            pipe.send_text(keys)
            choose_tools(_tool_catalog())


def test_choose_tools_escape_cancels() -> None:
    with pytest.raises(BrowserCancelled):
        _drive_dialog("\x1b")


def test_choose_tools_ctrl_c_cancels() -> None:
    with pytest.raises(BrowserCancelled):
        _drive_dialog("\x03")


# ------------------------------------------------------------------ scope dialog


def _drive_scope(keys: str) -> str:
    with create_pipe_input() as pipe, create_app_session(input=pipe, output=DummyOutput()):
        with mock.patch.object(sys.stdin, "isatty", lambda: True), mock.patch.object(
            sys.stdout, "isatty", lambda: True
        ):
            pipe.send_text(keys)
            return choose_scope()


def test_choose_scope_defaults_to_user() -> None:
    assert _drive_scope("\t\r") == "user"


def test_choose_scope_down_arrow_selects_project() -> None:
    assert _drive_scope("\x1b[B\t\r") == "project"


def test_choose_scope_escape_cancels() -> None:
    with pytest.raises(BrowserCancelled):
        _drive_scope("\x1b")


def test_choose_scope_ctrl_c_cancels() -> None:
    with pytest.raises(BrowserCancelled):
        _drive_scope("\x03")


# ------------------------------------------------------------------ project path


def _drive_path(keys: str, cwd: Path) -> Path:
    with create_pipe_input() as pipe, create_app_session(input=pipe, output=DummyOutput()):
        with mock.patch.object(sys.stdin, "isatty", lambda: True), mock.patch.object(
            sys.stdout, "isatty", lambda: True
        ):
            pipe.send_text(keys)
            return choose_project_path(cwd)


def test_choose_project_path_defaults_to_cwd() -> None:
    assert _drive_path("\r", Path("/tmp/x")) == Path("/tmp/x")


def test_choose_project_path_accepts_a_path() -> None:
    assert _drive_path("/srv/app\r", Path("/tmp/x")) == Path("/srv/app")


def test_choose_project_path_ctrl_c_cancels() -> None:
    with pytest.raises(BrowserCancelled):
        _drive_path("\x03", Path("/tmp/x"))
