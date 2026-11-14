"""Runnable proof for F-01/F-02/F-03 in `refuter.md`.

This module is NOT collected by the repo's test suite (it lives outside the
package). It exists to make the review's central claim reproducible: the shipped
`run_browser` can be driven headlessly from pytest, with no change to production
code, by mocking only `sys.stdin.isatty` / `sys.stdout.isatty` and injecting a
pipe input through `create_app_session`.

Run it directly for a key-by-key transcript:

    .venv/bin/python project-tasks/tui-review/headless_probe.py

Or run it as a test module to reproduce the coverage delta quoted in the report:

    .venv/bin/python -m pytest project-tasks/tui-review/headless_probe.py -q \
        --cov=agency_agents.infrastructure.browser_app --cov-branch \
        --cov-report=term-missing
"""

from __future__ import annotations

import sys
from typing import List, Tuple
from unittest import mock

from prompt_toolkit.application import create_app_session
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput

from agency_agents.infrastructure.browser import BrowserModel, BrowserRow
from agency_agents.infrastructure.browser_app import BrowserCancelled, run_browser


def make_model() -> BrowserModel:
    """A two-row model: backend-architect (cursor 0), growth-hacker (cursor 1)."""
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
        ):
            pipe.send_text(keys)
            return run_browser(model, title="headless")


# --------------------------------------------------------------------- pytest API


def test_enter_with_nothing_selected_returns_nothing() -> None:
    assert drive("\r", make_model()) == []


def test_tab_then_enter_returns_the_selection() -> None:
    assert drive("\t\r", make_model()) == ["backend-architect"]


def test_escape_without_a_selection_raises() -> None:
    try:
        drive("\x1b", make_model())
    except BrowserCancelled as exc:
        assert "nothing installed" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("expected BrowserCancelled")


def test_escape_with_a_selection_returns_it() -> None:
    """F-03: Esc with a selection installs; the on-screen help says 'esc cancel'."""
    assert drive("\t\x1b", make_model()) == ["backend-architect"]


def test_ctrl_c_with_a_selection_also_returns_it() -> None:
    assert drive("\t\x03", make_model()) == ["backend-architect"]


def test_select_all_then_enter_returns_both_rows() -> None:
    assert drive("\x01\r", make_model()) == ["backend-architect", "growth-hacker"]


def test_typing_narrows_the_filter_then_tab_selects_the_only_match() -> None:
    assert drive("growth\t\r", make_model()) == ["growth-hacker"]


def test_down_arrow_does_not_move_the_cursor() -> None:
    """F-02: the view receives '\\x1b[B' for Down and drops it, so Tab acts on row 0."""
    assert drive("\x1b[B\t\r", make_model()) == ["backend-architect"]


def test_a_selection_hidden_by_the_filter_is_still_installed() -> None:
    """F-03: select row 0, filter it out of sight, press Esc -> row 0 installs."""
    assert drive("\ta-4\x1b", _wide_model()) == ["a-0"]


def _wide_model() -> BrowserModel:
    return BrowserModel(
        rows=[BrowserRow("d", f"a-{i}", f"A {i}", "desc") for i in range(5)]
    )


# ------------------------------------------------------------------ transcript


CASES: List[Tuple[str, str]] = [
    ("\t\r", "tab, enter"),
    ("\x01\r", "c-a, enter"),
    ("\t\x03", "tab, ctrl-c"),
    ("\t\x1b", "tab, esc"),
    ("\x1b", "esc only"),
    ("\x1b[B\r", "down-arrow, enter"),
    ("\x1b[A\t\r", "up-arrow, tab, enter"),
    ("\x1b[6~\r", "page-down, enter"),
    ("\x1bg\r", "alt-g (esc then g), enter"),
]

if __name__ == "__main__":
    print(f"{'keys':12s} {'meaning':24s} -> outcome")
    for keys, meaning in CASES:
        model = make_model()
        try:
            outcome = f"RETURN {drive(keys, model)}"
        except BrowserCancelled:
            outcome = "CANCELLED"
        except Exception as exc:  # noqa: BLE001 - transcript only
            outcome = f"EXC {type(exc).__name__}: {exc}"
        print(
            f"{keys!r:12s} {meaning:24s} -> {outcome}  "
            f"[query={model.query!r} cursor={model.cursor} selected={sorted(model.selected)}]"
        )
