"""Pure browse/search/select model behind the interactive TUI.

The model owns every behaviour the browser claims — filtering, cursor movement,
multi-selection, the detail text and the resulting install plan. It imports no
terminal library, so each behaviour is asserted directly in tests without a
pseudo-terminal.

This split is a binding condition of tool decision D-001 in
`docs/dx/m7-tool-decisions.md`: prompt-toolkit won the toolkit evaluation
partly because the untestable-in-CI penalty was removed by keeping the view
thin. A terminal-dependent behaviour added here would void that verdict.

The view lives in `browser_app.py` and holds no state of its own.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Set

from agency_agents.core.models import Agent


@dataclass(frozen=True)
class BrowserRow:
    """One agent as the browser shows it."""

    division: str
    slug: str
    name: str
    description: str

    def matches(self, needle: str) -> bool:
        """Case-insensitive substring match over every field the user can see."""
        return (
            needle in self.slug.lower()
            or needle in self.name.lower()
            or needle in self.division.lower()
            or needle in self.description.lower()
        )


def build_rows(by_division: Mapping[str, Sequence[Agent]]) -> List[BrowserRow]:
    """Flatten the roster into rows, ordered by division then agent name.

    Sorting is explicit rather than dict-insertion order so two runs over the
    same corpus always present the same list — a browser whose order depends on
    filesystem iteration is unusable for keyboard navigation.
    """
    rows: List[BrowserRow] = []
    for division in sorted(by_division):
        for agent in by_division[division]:
            rows.append(
                BrowserRow(
                    division=division,
                    slug=agent.slug,
                    name=agent.frontmatter.name,
                    description=(agent.frontmatter.description or "").strip(),
                )
            )
    rows.sort(key=lambda row: (row.division, row.name.lower(), row.slug))
    return rows


@dataclass
class BrowserModel:
    """Everything the browser remembers, with no reference to a screen."""

    rows: List[BrowserRow]
    query: str = ""
    cursor: int = 0
    selected: Set[str] = field(default_factory=set)

    # ------------------------------------------------------------------ filter

    def visible(self) -> List[BrowserRow]:
        """Rows matching the current query, in stable order."""
        needle = self.query.strip().lower()
        if not needle:
            return list(self.rows)
        return [row for row in self.rows if row.matches(needle)]

    def set_query(self, query: str) -> None:
        """Replace the query and reset the cursor to the first match.

        Keeping the cursor where it was would leave it pointing past the end of
        a narrowed list, which is how a filtered browser shows a blank detail
        pane with rows still visible.
        """
        self.query = query
        self.cursor = 0

    # --------------------------------------------------------------- movement

    def move(self, delta: int) -> None:
        """Move the cursor by delta, clamped to the visible rows."""
        visible = self.visible()
        if not visible:
            self.cursor = 0
            return
        self.cursor = max(0, min(len(visible) - 1, self.cursor + delta))

    def current(self) -> Optional[BrowserRow]:
        """The row under the cursor, or None when nothing matches."""
        visible = self.visible()
        if not visible:
            return None
        return visible[min(self.cursor, len(visible) - 1)]

    # -------------------------------------------------------------- selection

    def toggle(self) -> Optional[BrowserRow]:
        """Toggle the current row's selection; returns the row acted on."""
        row = self.current()
        if row is None:
            return None
        if row.slug in self.selected:
            self.selected.discard(row.slug)
        else:
            self.selected.add(row.slug)
        return row

    def select_all_visible(self) -> int:
        """Select every visible row; returns how many were newly selected."""
        added = 0
        for row in self.visible():
            if row.slug not in self.selected:
                self.selected.add(row.slug)
                added += 1
        return added

    def clear_selection(self) -> None:
        self.selected.clear()

    def is_selected(self, row: BrowserRow) -> bool:
        return row.slug in self.selected

    def selection(self) -> List[str]:
        """Selected slugs in roster order, which makes the plan reproducible."""
        return [row.slug for row in self.rows if row.slug in self.selected]

    # ----------------------------------------------------------------- detail

    def detail_lines(self) -> List[str]:
        """Plain-text detail for the row under the cursor."""
        row = self.current()
        if row is None:
            return ["No agent matches the current filter."]
        mark = "selected" if self.is_selected(row) else "not selected"
        return [
            f"{row.name}  [{mark}]",
            f"division: {row.division}",
            f"slug: {row.slug}",
            "",
            row.description or "(no description)",
        ]

    # ----------------------------------------------------------------- status

    def status_line(self) -> str:
        """One-line summary the view prints below the list."""
        shown = len(self.visible())
        total = len(self.rows)
        picked = len(self.selected)
        scope = f"{shown}/{total} shown" if self.query.strip() else f"{total} agents"
        return f"{scope} | {picked} selected | type to filter, space to select, enter to install"


def slugs_for_division(rows: Iterable[BrowserRow], division: str) -> List[str]:
    """Slugs belonging to one division, used by the view's division jump keys."""
    return [row.slug for row in rows if row.division == division]


# Outcomes of one keystroke. The view turns them into redraw/exit decisions and
# nothing else, so key handling is asserted without a terminal.
CONTINUE = "continue"
ACCEPT = "accept"
ABORT = "abort"

# Named keys the browser understands. Everything else that is printable widens
# the filter, which is what makes the list searchable by just typing.
_UP = {"up", "c-p"}
_DOWN = {"down", "c-n"}
_PAGE_UP = {"pageup", "c-b"}
_PAGE_DOWN = {"pagedown", "c-f"}
_TOGGLE = {"tab"}
_SELECT_ALL = {"c-a"}
_CLEAR = {"c-x"}
_BACKSPACE = {"backspace", "c-h"}
_ACCEPT = {"enter", "c-m"}
_ABORT = {"escape", "c-c", "c-q"}

try:
    from prompt_toolkit.keys import Keys as _Keys

    _BACKSPACE.add(str(_Keys.ControlH))
    _BACKSPACE.add(str(_Keys.Backspace))
except Exception:  # pragma: no cover - prompt_toolkit is a hard dependency
    pass

PAGE_SIZE = 10


def apply_key(model: BrowserModel, key: str) -> str:
    """Apply one keystroke to the model and report the outcome.

    `key` is either a prompt-toolkit key name (`"up"`, `"tab"`, `"enter"`) or a
    literal character. A printable character widens the filter; a named key
    performs its action. This is the whole input contract of the browser.
    """
    if key in _ABORT:
        return ABORT
    if key in _ACCEPT:
        return ACCEPT
    if key in _UP:
        model.move(-1)
        return CONTINUE
    if key in _DOWN:
        model.move(1)
        return CONTINUE
    if key in _PAGE_UP:
        model.move(-PAGE_SIZE)
        return CONTINUE
    if key in _PAGE_DOWN:
        model.move(PAGE_SIZE)
        return CONTINUE
    if key in _TOGGLE:
        model.toggle()
        return CONTINUE
    if key in _SELECT_ALL:
        model.select_all_visible()
        return CONTINUE
    if key in _CLEAR:
        model.clear_selection()
        return CONTINUE
    if key in _BACKSPACE:
        model.set_query(model.query[:-1])
        return CONTINUE
    if key == "c-u":
        model.set_query("")
        return CONTINUE
    if len(key) == 1 and key.isprintable():
        model.set_query(model.query + key)
        return CONTINUE
    return CONTINUE
