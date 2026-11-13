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

import sys
from typing import Any, Dict, List, Mapping, Optional, Sequence

from prompt_toolkit import Application
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import Layout, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles import Style

from agency_agents.infrastructure.browser import (
    ABORT,
    ACCEPT,
    BrowserModel,
    apply_key,
    key_name,
)

LIST_HEIGHT = 15

# Key identity is resolved in `run_browser` from prompt-toolkit's parsed `Keys`
# enum (``.value``) plus the raw bytes, translated through `browser.key_name`.
# No byte map lives here: `key_name` is the single, assertable seam.

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


def choose_tools(
    tools_catalog: Mapping[str, Any],
    detected: Sequence[str] = (),
    scope: Optional[str] = None,
) -> List[str]:
    """Ask for the target tools with a checkbox dialog.

    `scope` restricts the offered tools to those with a destination for the
    resolved scope, so the picker never lists a choice guaranteed to fail one
    line later. Escape and Ctrl-C cancel — the same keys the browser teaches —
    and surface as `BrowserCancelled`.
    """
    from prompt_toolkit.application import get_app
    from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
    from prompt_toolkit.layout.containers import HSplit
    from prompt_toolkit.widgets import Button, CheckboxList, Dialog, Label

    ordered = sorted(tools_catalog.values(), key=lambda t: t.order)
    if scope is not None:
        ordered = [t for t in ordered if t.dest.get(scope)]
    values = [
        (tool.kebab, f"{tool.label} ({tool.kebab})" + (" - detected" if tool.kebab in detected else ""))
        for tool in ordered
    ]
    default = [value for value, _ in values if value in detected]

    checkbox = CheckboxList(values=values, default_values=default)

    def ok_handler() -> None:
        get_app().exit(result=checkbox.current_values)

    bindings = KeyBindings()
    bindings.add("tab")(focus_next)
    bindings.add("s-tab")(focus_previous)

    @bindings.add("escape")
    @bindings.add("c-c")
    def _cancel(event) -> None:  # type: ignore[no-untyped-def]
        event.app.exit(exception=KeyboardInterrupt())

    dialog = Dialog(
        title="Install into which tools?",
        body=HSplit(
            [Label(text="Space toggles, Tab moves, Enter confirms, Esc cancels."), checkbox],
            padding=1,
        ),
        buttons=[
            Button(text="Ok", handler=ok_handler),
            Button(text="Cancel", handler=lambda: get_app().exit(result=None)),
        ],
        with_background=True,
    )
    application: Application[Any] = Application(
        layout=Layout(dialog),
        key_bindings=bindings,
        mouse_support=True,
        full_screen=True,
    )
    try:
        chosen = application.run()
    except (EOFError, KeyboardInterrupt) as exc:
        # No terminal to ask in (piped stdin, CI) or the user walked away. Either
        # way the answer is a flag, so the message names it instead of leaving the
        # caller to guess why nothing installed.
        kebab_list = ", ".join(sorted(tools_catalog))
        raise BrowserCancelled(
            f"No tool selected, so nothing was installed. "
            f"Pass --tool <kebab> to skip the question. Available: {kebab_list}"
        ) from exc
    return list(chosen or [])


def _draw_window(model: BrowserModel, list_height: int) -> tuple[List[tuple[str, str]], int]:
    """Lines for the on-screen slice of rows, plus the absolute cursor index.

    The browser draws a window instead of a scrollable pane: it keeps the layout
    a single control and makes "which rows are on screen" a pure function a test
    can assert.
    """
    visible = model.visible()
    if not visible:
        return [], 0
    cursor = min(model.cursor, len(visible) - 1)
    start = max(0, cursor - list_height // 2)
    start = min(start, max(0, len(visible) - list_height))
    lines: List[tuple[str, str]] = []
    for offset, row in enumerate(visible[start : start + list_height]):
        absolute = start + offset
        mark = "[x]" if model.is_selected(row) else "[ ]"
        style = ""
        if absolute == cursor:
            style = "class:cursor"
        elif model.is_selected(row):
            style = "class:selected"
        lines.append((style, f" {mark} {row.division}/{row.slug}  -  {row.name}\n"))
    return lines, cursor


def render_screen(
    model: BrowserModel, title: str = "Browse agents", list_height: int = LIST_HEIGHT
) -> FormattedText:
    """Build the whole screen as formatted text. Pure: no terminal required."""
    parts: List[tuple[str, str]] = [
        ("class:title", f" {title}\n"),
        ("", f" filter: {model.query}\n"),
        ("", "-" * 72 + "\n"),
    ]

    rows, _ = _draw_window(model, list_height)
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
            " up/down move  tab toggle  c-a all  c-x clear  enter install  esc cancel\n",
        )
    )
    return FormattedText(parts)


def run_browser(model: BrowserModel, title: str = "Browse agents") -> List[str]:
    """Run the full-screen browser; returns the selected slugs.

    Raises `BrowserCancelled` when there is no terminal, when the terminal is too
    small, when the user aborts (escape / c-c), and when the terminal disappears
    or the key handler fails. Enter is the only key that accepts: the keys the
    help labels "cancel" never install.
    """
    # A pipe is not a terminal. Without this guard the application draws into
    # nothing, exits on EOF and reports "nothing selected" with status 0 — a
    # silent no-op inside a script that believes it installed something.
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        raise BrowserCancelled(
            "The browser needs a terminal, and this session has none. "
            "Use the flags instead: "
            "`agency-agents install --tool <kebab> --no-interactive`."
        )

    bindings = KeyBindings()
    outcome: Dict[str, str] = {}
    failure: Dict[str, BaseException] = {}
    list_cell: Dict[str, int] = {"height": LIST_HEIGHT}

    @bindings.add(Keys.Any)
    def _handle(event) -> None:  # type: ignore[no-untyped-def]
        press = event.key_sequence[0]
        if press.key is Keys.BracketedPaste:
            # Paste data is not a key; `key_name` would treat a pasted CR/LF as
            # enter and install. Drop it.
            return
        key = press.key.value if isinstance(press.key, Keys) else press.key
        try:
            result = apply_key(model, key_name(key, event.data))
        except Exception as exc:  # one bad keystroke must never hang the app
            failure["error"] = exc
            event.app.exit()
            return
        if result in (ACCEPT, ABORT):
            outcome["result"] = result
            event.app.exit()
            return
        event.app.invalidate()

    body = Window(
        FormattedTextControl(lambda: render_screen(model, title, list_cell["height"])),
        always_hide_cursor=True,
    )
    application: Application[None] = Application(
        layout=Layout(body),
        key_bindings=bindings,
        style=_STYLE,
        full_screen=True,
        mouse_support=False,
    )

    # Size the list from the real terminal so the layout always fits: a fixed
    # 15-row window clipped the help/status line on the very common 24-row
    # terminal. The guard below and the render above must read the same source,
    # or a terminal that passes the guard can still be clipped.
    size = application.output.get_size()
    if size.rows < 20 or size.columns < 60:
        raise BrowserCancelled(
            f"The browser needs at least 60x20, this terminal is {size.columns}x{size.rows}. "
            "Resize it, or skip the browser: "
            "`agency-agents install --tool <kebab> --no-interactive`."
        )
    list_cell["height"] = max(3, size.rows - 12)

    try:
        application.run(handle_sigint=False, set_exception_handler=False)
    except (EOFError, KeyboardInterrupt, OSError, RuntimeError) as exc:
        raise BrowserCancelled(
            "The browser lost its terminal before you finished \u2014 nothing installed. "
            "Re-run in an interactive shell, or use "
            "`agency-agents install --tool <kebab> --no-interactive`."
        ) from exc

    if "error" in failure:
        raise BrowserCancelled(
            f"The browser hit an internal error ({failure['error']}). Nothing was installed. "
            "Use the flags instead: `agency-agents install --tool <kebab> --no-interactive`."
        ) from failure["error"]

    if outcome.get("result") != ACCEPT:
        raise BrowserCancelled("No agents installed \u2014 selection cancelled.")
    return model.selection()
