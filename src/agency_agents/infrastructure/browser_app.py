"""Interactive agent browser — the view layer for GitHub issue #13.

This module renders `browser.BrowserModel` and forwards keystrokes to
`browser.apply_key`. It holds no state of its own: every behaviour it exposes is
already asserted against the model without a terminal, which is the condition
tool decision D-001 in `docs/dx/m7-tool-decisions.md` placed on adopting
prompt-toolkit.

The renderer is a pure function of the model (`render_screen`), so the layout can
be asserted in tests by reading strings instead of driving a terminal.
"""

from __future__ import annotations

from typing import Dict, List

from prompt_toolkit import Application
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import Layout, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles import Style

from agency_agents.infrastructure.browser import ABORT, ACCEPT, BrowserModel, apply_key

LIST_HEIGHT = 15

# `Keys.Any` delivers control keys as their raw escape sequence, so they are
# mapped back to the names `apply_key` understands before dispatch.
_NAMED_KEYS: Dict[str, str] = {
    "\r": "enter",
    "\n": "enter",
    "\t": "tab",
    "\x1b": "escape",
    "\x03": "c-c",
    "\x11": "c-q",
    "\x01": "c-a",
    "\x18": "c-x",
    "\x15": "c-u",
    "\x02": "c-b",
    "\x06": "c-f",
    "\x08": "c-h",
    "\x0e": "c-n",
    "\x10": "c-p",
    "\x7f": "backspace",
}

_STYLE = Style.from_dict(
    {
        "title": "bold",
        "cursor": "reverse",
        "selected": "bold",
        "dim": "fg:ansibrightblack",
    }
)


class BrowserCancelled(Exception):
    """Raised when the user leaves the browser without installing."""


def _draw_window(model: BrowserModel) -> tuple[List[tuple[str, str]], int]:
    """Lines for the on-screen slice of rows, plus the absolute cursor index.

    The browser draws a window instead of a scrollable pane: it keeps the layout
    a single control and makes "which rows are on screen" a pure function a test
    can assert.
    """
    visible = model.visible()
    if not visible:
        return [], 0
    cursor = min(model.cursor, len(visible) - 1)
    start = max(0, cursor - LIST_HEIGHT // 2)
    start = min(start, max(0, len(visible) - LIST_HEIGHT))
    lines: List[tuple[str, str]] = []
    for offset, row in enumerate(visible[start : start + LIST_HEIGHT]):
        absolute = start + offset
        mark = "[x]" if model.is_selected(row) else "[ ]"
        style = ""
        if absolute == cursor:
            style = "class:cursor"
        elif model.is_selected(row):
            style = "class:selected"
        lines.append((style, f" {mark} {row.division}/{row.slug}  -  {row.name}\n"))
    return lines, cursor


def render_screen(model: BrowserModel, title: str = "Browse agents") -> FormattedText:
    """Build the whole screen as formatted text. Pure: no terminal required."""
    parts: List[tuple[str, str]] = [
        ("class:title", f" {title}\n"),
        ("", f" filter: {model.query}\n"),
        ("", "-" * 72 + "\n"),
    ]

    rows, _ = _draw_window(model)
    if rows:
        parts.extend(rows)
    else:
        parts.append(("class:dim", " no agent matches this filter\n"))

    parts.append(("", "-" * 72 + "\n"))
    for line in model.detail_lines():
        parts.append(("class:dim", " " + line + "\n"))
    parts.append(("", "-" * 72 + "\n"))
    parts.append(("", " " + model.status_line() + "\n"))
    parts.append(
        (
            "class:dim",
            " up/down move  tab toggle  c-a all  c-x clear  c-u reset  "
            "enter install  esc cancel\n",
        )
    )
    return FormattedText(parts)


def run_browser(model: BrowserModel, title: str = "Browse agents") -> List[str]:
    """Run the full-screen browser; returns the selected slugs.

    Raises `BrowserCancelled` only when the user aborts with nothing selected.
    Aborting with a selection returns it: the selection was deliberate work, and
    discarding it silently would be hostile.
    """
    bindings = KeyBindings()
    outcome: Dict[str, str] = {}

    @bindings.add(Keys.Any)
    def _handle(event) -> None:  # type: ignore[no-untyped-def]
        key = event.data
        result = apply_key(model, _NAMED_KEYS.get(key, key))
        if result in (ACCEPT, ABORT):
            outcome["result"] = result
            event.app.exit()
            return
        event.app.invalidate()

    body = Window(
        FormattedTextControl(lambda: render_screen(model, title)),
        always_hide_cursor=True,
    )
    application: Application[None] = Application(
        layout=Layout(body),
        key_bindings=bindings,
        style=_STYLE,
        full_screen=True,
        mouse_support=False,
    )
    application.run()

    if outcome.get("result") == ABORT and not model.selected:
        raise BrowserCancelled("No agents selected \u2014 nothing installed.")
    return model.selection()
