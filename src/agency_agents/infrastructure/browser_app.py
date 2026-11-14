"""Interactive install TUI — the view layer for GitHub issue #13.

This module renders the pure state in `browser` and forwards keystrokes to it.
It holds no state of its own: every behaviour it exposes is asserted against the
model without a terminal, which is the condition tool decision D-001 in
`docs/dx/m7-tool-decisions.md` placed on adopting prompt-toolkit.

The install flow is one full-screen application that walks four stages — scope
→ project path → harness → agents — so scope and harness are chosen *inside*
the TUI rather than by separate dialogs that open before it. Each stage renders
the same chrome (bold title, ``-`` separators, reverse-video cursor, dim help
line) and every renderer is a pure function of its state, so the layout can be
asserted by reading strings instead of driving a terminal.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Set

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
    CONTINUE,
    BrowserModel,
    HarnessOption,
    InstallFlow,
    apply_key,
    key_name,
)

LIST_HEIGHT = 15

# Key identity is resolved in `run_install_tui` from prompt-toolkit's parsed
# `Keys` enum (``.value``) plus the raw bytes, translated through
# `browser.key_name`. No byte map lives here: `key_name` is the single,
# assertable seam.

_STYLE = Style.from_dict(
    {
        "title": "bold",
        "cursor": "reverse",
        "selected": "bold",
        "dim": "fg:ansibrightblack",
    }
)

# Key-name sets for the pre-agent stages. They mirror the browser's own named
# keys so the scope/path/harness screens feel like the rest of the TUI.
_UP_KEYS = {"up", "c-p"}
_DOWN_KEYS = {"down", "c-n"}
_ENTER_KEYS = {"enter", "c-m"}
_TAB_KEYS = {"tab"}
_BACKSPACE_KEYS = {"backspace", "c-h"}
_ABORT_KEYS = {"escape", "c-c", "c-q"}

_SCOPE_LABELS = (
    "user     \u2014 install under your home directory",
    "project  \u2014 install into a repository",
)


class BrowserCancelled(Exception):
    """Raised when the user leaves the install flow without installing."""


@dataclass(frozen=True)
class InstallSelection:
    """What the user chose across the whole install flow."""

    scope: str
    project_root: Optional[Path]
    tools: List[str]
    agents: List[str]


# ------------------------------------------------------------------ renderers


def render_scope_screen(scope_index: int) -> FormattedText:
    """Build the scope stage as formatted text. Pure: no terminal required."""
    parts: List[tuple[str, str]] = [
        ("class:title", " Install scope\n"),
        ("", "-" * 72 + "\n"),
    ]
    for index, label in enumerate(_SCOPE_LABELS):
        style = "class:cursor" if index == scope_index else ""
        parts.append((style, f"   {label}\n"))
    parts.append(("", "-" * 72 + "\n"))
    parts.append(("class:dim", " up/down select  enter confirm  esc cancel\n"))
    return FormattedText(parts)


def render_path_screen(path: str, cwd: Path) -> FormattedText:
    """Build the project-path stage as formatted text. Pure: no terminal."""
    parts: List[tuple[str, str]] = [
        ("class:title", " Project root\n"),
        ("", "-" * 72 + "\n"),
        ("class:dim", f" current: {cwd}\n"),
        ("", f" install into: {path}"),
        ("class:cursor", "_\n"),
        ("", "-" * 72 + "\n"),
        ("class:dim", " type a path  enter confirm (empty = current)  esc cancel\n"),
    ]
    return FormattedText(parts)


def render_harness_screen(
    tools: List[HarnessOption], index: int, selected: Set[str]
) -> FormattedText:
    """Build the harness stage as formatted text. Pure: no terminal required."""
    parts: List[tuple[str, str]] = [
        ("class:title", " Install into which tools?\n"),
        ("", "-" * 72 + "\n"),
    ]
    if not tools:
        parts.append(("class:dim", " no harness supports this scope\n"))
    for cursor, option in enumerate(tools):
        mark = "[x]" if option.kebab in selected else "[ ]"
        detected = " - detected" if option.detected else ""
        if cursor == index:
            style = "class:cursor"
        elif option.kebab in selected:
            style = "class:selected"
        else:
            style = ""
        parts.append((style, f" {mark} {option.kebab:<18} {option.label}{detected}\n"))
    parts.append(("", "-" * 72 + "\n"))
    parts.append(("class:dim", " up/down move  tab toggle  enter confirm  esc cancel\n"))
    return FormattedText(parts)


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


# ------------------------------------------------------------------ flow


def _harness_options(
    tools_catalog: Mapping[str, Any], scope: str, detected: Sequence[str]
) -> List[HarnessOption]:
    """Harness options for one scope, ordered and marked with detection."""
    ordered = sorted(tools_catalog.values(), key=lambda t: t.order)
    ordered = [t for t in ordered if t.dest.get(scope)]
    return [
        HarnessOption(kebab=t.kebab, label=t.label, detected=t.kebab in detected)
        for t in ordered
    ]


def _enter_harness(flow: InstallFlow, options: List[HarnessOption]) -> None:
    """Seed the harness stage with its options and detected defaults."""
    flow.tools = list(options)
    flow.harness_index = 0
    flow.harness_selected = {t.kebab for t in options if t.detected}
    flow.stage = "harness"


def _flow_key(
    flow: InstallFlow,
    name: str,
    harness_by_scope: Mapping[str, List[HarnessOption]],
    tool: Optional[str],
) -> str:
    """Dispatch one keystroke to the current stage; returns the outcome.

    The scope/path/harness stages advance inside the flow and always report
    `CONTINUE`; only the agents stage (which reuses `apply_key`) can report
    `ACCEPT`/`ABORT`, so Enter/escape never silently finish the wrong step.
    """
    if name in _ABORT_KEYS:
        return ABORT

    stage = flow.stage
    if stage == "scope":
        if name in _UP_KEYS:
            flow.move_scope(-1)
        elif name in _DOWN_KEYS:
            flow.move_scope(1)
        elif name in _ENTER_KEYS:
            flow.accept_scope()
            flow.stage = flow.next_stage_after_scope()
            if flow.stage == "harness":
                if tool is not None:
                    flow.stage = "agents"  # explicit --tool skips the picker
                else:
                    _enter_harness(flow, harness_by_scope[flow.scope])
        return CONTINUE

    if stage == "path":
        if name in _ENTER_KEYS:
            if tool is not None:
                flow.stage = "agents"
            else:
                _enter_harness(flow, harness_by_scope[flow.scope])
        elif name in _BACKSPACE_KEYS:
            flow.backspace_path()
        elif len(name) == 1 and name.isprintable():
            flow.type_path(name)
        return CONTINUE

    if stage == "harness":
        if name in _UP_KEYS:
            flow.move_harness(-1)
        elif name in _DOWN_KEYS:
            flow.move_harness(1)
        elif name in _TAB_KEYS:
            flow.toggle_harness()
        elif name in _ENTER_KEYS:
            flow.stage = "agents"
        return CONTINUE

    # agents stage
    return apply_key(flow.agents, name)


def _render_flow(flow: InstallFlow, cwd: Path, title: str) -> FormattedText:
    """Render the current stage. Pure dispatch, so each stage stays testable."""
    stage = flow.stage
    if stage == "scope":
        return render_scope_screen(flow.scope_index)
    if stage == "path":
        return render_path_screen(flow.path, cwd)
    if stage == "harness":
        return render_harness_screen(flow.tools, flow.harness_index, flow.harness_selected)
    return render_screen(flow.agents, title=f"{title} - select agents")


def _resolve_project_root(text: str, cwd: Path) -> Path:
    """Resolve the typed path: empty means the current directory."""
    text = text.strip()
    if not text:
        return cwd
    path = Path(text).expanduser()
    if not path.is_absolute():
        path = cwd / path
    return path


def run_install_tui(
    model: BrowserModel,
    tools_catalog: Mapping[str, Any],
    detected: Sequence[str],
    *,
    scope: Optional[str] = None,
    project_root: Optional[Path] = None,
    tool: Optional[str] = None,
    title: str = "Agency Agents",
) -> InstallSelection:
    """Run the whole install flow — scope → path → harness → agents — in one app.

    A preset (from a CLI flag) skips its stage. Returns the resolved selection;
    raises `BrowserCancelled` when there is no terminal, when the user aborts
    (escape / c-c), and when the terminal disappears or a key handler fails.
    """
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        raise BrowserCancelled(
            "The install browser needs a terminal, and this session has none. "
            "Use the flags instead: "
            "`agency-agents install --tool <kebab> --no-interactive`."
        )

    flow = InstallFlow(agents=model)
    flow.scope = scope or "user"
    flow.scope_index = 0 if flow.scope == "user" else 1
    if project_root is not None:
        flow.path = str(project_root)
    if tool is not None:
        flow.tools = [HarnessOption(kebab=tool, label=tool)]
        flow.harness_selected = {tool}

    # First interactive stage, derived from the presets.
    if scope is None:
        flow.stage = "scope"
    elif scope == "project" and project_root is None:
        flow.stage = "path"
    elif tool is None:
        flow.stage = "harness"
    else:
        flow.stage = "agents"

    harness_by_scope = {
        "user": _harness_options(tools_catalog, "user", detected),
        "project": _harness_options(tools_catalog, "project", detected),
    }
    if flow.stage == "harness":
        _enter_harness(flow, harness_by_scope[flow.scope])

    cwd = Path.cwd()
    outcome: Dict[str, str] = {}
    failure: Dict[str, BaseException] = {}
    list_cell: Dict[str, int] = {"height": LIST_HEIGHT}

    bindings = KeyBindings()

    @bindings.add(Keys.Any)
    def _handle(event) -> None:  # type: ignore[no-untyped-def]
        press = event.key_sequence[0]
        if press.key is Keys.BracketedPaste:
            # Paste data is not a key; `key_name` would treat a pasted CR/LF as
            # enter and install. Drop it.
            return
        key = press.key.value if isinstance(press.key, Keys) else press.key
        name = key_name(key, event.data)
        try:
            result = _flow_key(flow, name, harness_by_scope, tool)
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
        FormattedTextControl(lambda: _render_flow(flow, cwd, title)),
        always_hide_cursor=True,
    )
    application: Application[None] = Application(
        layout=Layout(body),
        key_bindings=bindings,
        style=_STYLE,
        full_screen=True,
        mouse_support=False,
    )

    # The agents stage needs the full terminal; guard once up front so a terminal
    # that passes the scope stage can never clip the agents list.
    size = application.output.get_size()
    if size.rows < 20 or size.columns < 60:
        raise BrowserCancelled(
            f"The install browser needs at least 60x20, this terminal is {size.columns}x{size.rows}. "
            "Resize it, or skip the browser: "
            "`agency-agents install --tool <kebab> --no-interactive`."
        )
    list_cell["height"] = max(3, size.rows - 12)

    try:
        application.run(handle_sigint=False, set_exception_handler=False)
    except (EOFError, KeyboardInterrupt, OSError, RuntimeError) as exc:
        raise BrowserCancelled(
            "The install browser lost its terminal before you finished \u2014 nothing installed. "
            "Re-run in an interactive shell, or use "
            "`agency-agents install --tool <kebab> --no-interactive`."
        ) from exc

    if "error" in failure:
        raise BrowserCancelled(
            f"The install browser hit an internal error ({failure['error']}). Nothing was installed. "
            "Use the flags instead: `agency-agents install --tool <kebab> --no-interactive`."
        ) from failure["error"]

    if outcome.get("result") != ACCEPT:
        raise BrowserCancelled("Install cancelled \u2014 nothing installed.")

    selected_tools = [tool] if tool is not None else flow.selected_tools()
    resolved_root = _resolve_project_root(flow.path, cwd) if flow.scope == "project" else None
    return InstallSelection(
        scope=flow.scope,
        project_root=resolved_root,
        tools=selected_tools,
        agents=model.selection(),
    )
