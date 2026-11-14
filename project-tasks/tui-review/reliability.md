# Reliability / Correctness Review — Interactive TUI (`tui`, bare `install`)

**Reviewer role:** Correctness & runtime reliability
**Verdict: 🔴 Unsafe to Ship** (interactive surface only — the flag-driven `install` path is sound)
**Reviewed in full:** `src/agency_agents/infrastructure/browser.py`, `src/agency_agents/infrastructure/browser_app.py`,
`src/agency_agents/cli/main.py` (`tui`, `_browse_and_install`, `_detected_tools`, `_install_agents`),
`src/agency_agents/tests/unit/test_browser.py`, `src/agency_agents/tests/integration/test_cli_tui.py`
**Method:** static read + execution. Every key-dispatch claim below was verified against the installed
`prompt_toolkit 3.0.53` (`Vt100Parser`, `ANSI_SEQUENCES`, a live `Application` driven through
`create_pipe_input`) and every model claim against the real module. 52/52 existing tests pass — they do
not cover the seam that is broken.

**Counts:** 1 critical · 4 high · 5 medium · 6 low (16 findings)

---

## Executive summary

The model (`browser.py`) is genuinely well tested and behaves as documented. The view (`browser_app.py`)
is where the defects live, and they are concentrated in two lines: the `Keys.Any` handler dispatches on
`event.data` (`browser_app.py:178-179`) and the result is compared against keys the model names
(`browser.py:182-191`). Arrow keys, PageUp/PageDown and every non-ANSI named key therefore arrive as raw
escape bytes, match nothing, and are **silently dropped**. The two documentation surfaces inside the app
("up/down move", "space to select", "esc cancel") each describe behaviour the code does not implement —
and one of them, `esc cancel`, actually **installs** when anything is selected.

Nothing found can corrupt already-installed files (`InstallationManager.prune_output` is a no-op), but
`esc` triggering an install is an unintended persisted side effect, which is the reason for the
**Unsafe to Ship** verdict on the TUI.

---

# Critical

## F-01 — Arrow keys and page keys never reach `apply_key`: cursor cannot move

**Severity:** critical
**Where:** `src/agency_agents/infrastructure/browser_app.py:32-48` (`_NAMED_KEYS`), `:176-184` (`_handle`),
`:149` (help text); `src/agency_agents/infrastructure/browser.py:182-185` (`_UP`/`_DOWN`/`_PAGE_UP`/`_PAGE_DOWN`)

**Expected:** pressing `↑`/`↓` moves the cursor one row, `PageUp`/`PageDown` move `PAGE_SIZE` rows — this is
what the on-screen help advertises (`" up/down move"`, `browser_app.py:149`) and what
`test_apply_key_moves_the_cursor` (`tests/unit/test_browser.py:352`) asserts at model level.

**Actual:** arrow keys are delivered to `_handle` as `event.data == "\x1b[A"` / `"\x1b[B"`. `_NAMED_KEYS`
contains only single control bytes, so `_NAMED_KEYS.get("\x1b[A", "\x1b[A")` returns the raw sequence;
`apply_key` matches no set, `len(key) == 1` is false, and the function falls through to
`return CONTINUE` (`browser.py:245`). **Silent no-op, no cursor movement, no feedback.** The same happens
for `PageUp`/`PageDown`/`Home`/`End`/`Delete`/`Shift-Tab`/F-keys. The only working navigation is the
undocumented `Ctrl-N`/`Ctrl-P` (`c-n`/`c-p` are in `_UP`/`_DOWN` and do reach the model) and
`Ctrl-B`/`Ctrl-F` for paging.

**Evidence (executed, not inferred):**

1. `prompt_toolkit.input.vt100_parser.Vt100Parser` on the real bytes:
   `b"\x1b[A" -> KeyPress(Keys.Up, data="\x1b[A")`, `b"\x1b[5~" -> Keys.PageUp`, `b"\x1b[6~" -> Keys.PageDown`.
   `ANSI_SEQUENCES` confirms `'\x1b[A' -> Keys.Up (value 'up')`, `'\x1b[B' -> 'down'`, `'\x1b[5~' -> 'pageup'`,
   `'\x1b[6~' -> 'pagedown'`.
2. A live `Application` with only `@bindings.add(Keys.Any)` receives `event.data == "'\\x1b[A'"` — the raw
   sequence, exactly as the finding states.
3. End-to-end through the real dispatch chain (`_NAMED_KEYS.get(raw, raw)` → `apply_key`):

   ```
   Up        raw='\x1b[A'  -> key='\x1b[A'  result=continue changed=False
   Down      raw='\x1b[B'  -> key='\x1b[B'  result=continue changed=False
   PageUp    raw='\x1b[5~' -> key='\x1b[5~' result=continue changed=False
   PageDown  raw='\x1b[6~' -> key='\x1b[6~' result=continue changed=False
   ```

**Verdict on the reported defect: CONFIRMED.** This is a real, 100 %-reproducible break of the browser's
primary advertised control, invisible to the test suite because `test_browser.py` feeds `apply_key` the
name `"down"` that the view never produces.

**Fix (smallest correct one — do not hardcode ANSI sequences; terminals in DECCKM mode send `\x1bOA`):**
dispatch on the *parsed key identity*, not on raw bytes, and keep the byte map only for characters.
Extract the translation into a pure function in `browser.py` so it stays assertable without a terminal
(D-001 stays intact):

```python
# browser.py
_CHAR_NAMES = {"\r": "enter", "\n": "enter", "\t": "tab", "\x08": "c-h", "\x7f": "backspace"}

def key_name(key: str, data: str) -> str:
    """Name a key press: control bytes by value, named keys by their pt name."""
    return _CHAR_NAMES.get(data, key)
```

```python
# browser_app.py
@bindings.add(Keys.Any)
def _handle(event) -> None:
    key = event.key.value if event.key is not Keys.Any else event.data
    result = apply_key(model, key_name(key, event.data))
    ...
```

`Keys.Up.value == "up"`, `Keys.PageUp.value == "pageup"`, `Keys.Escape.value == "escape"`,
`Keys.ControlA.value == "c-a"` — all already the exact names `apply_key` understands.
**Careful:** `ANSI_SEQUENCES` resolves `\t` to `Keys.ControlI` (`"c-i"`) and `\n` to `Keys.ControlJ`
(`"c-j"`), which the model does not know; that is why `_CHAR_NAMES` must be consulted first, otherwise the
fix silently breaks `tab`/`enter`. Add table tests for `("\x1b[A")->"up"`, `("\x1b[5~")->"pageup"`,
`("\t")->"tab"`, `("\r")->"enter"` in `test_browser.py`.

---

# High

## F-02 — `esc` with a selection installs files, while the help line says "esc cancel"

**Severity:** high
**Where:** `src/agency_agents/infrastructure/browser_app.py:199-200` vs `:149-150`; caller
`src/agency_agents/cli/main.py:460-468`

**Expected:** `esc` cancels — the browser's own help text says `"esc cancel"`
(`browser_app.py:149-150`), and `ABORT` is the name the model gives that key (`browser.py:191`).

**Actual:** `run_browser` raises `BrowserCancelled` **only when nothing is selected**
(`browser_app.py:199`). With a non-empty selection, `ABORT` returns `model.selection()`, and
`_browse_and_install` proceeds straight to `_install_agents` (`main.py:521`) and writes into `$HOME`.
Pressing the key documented as "cancel" writes files.

The failure is not hypothetical: prompt_toolkit flushes a lone `ESC` after `ttimeoutlen` (0.5 s). A
terminal or multiplexer that delivers an arrow key's bytes in two chunks — slow ssh, tmux redraw, a busy
box — degrades `\x1b[A` into `ESC` + `[`. Measured with a 0.6 s gap:

```
gap=0.6s -> ["'\\x1b'", "'['"]      # ESC delivered alone -> ABORT -> install
```

So an arrow-key press (already broken per F-01) can, with a selection on screen, trigger an install.

**Fix:** make `ABORT` always cancel, and be honest about the work that is retained:

```python
if outcome.get("result") == ABORT:
    kept = len(model.selected)
    raise BrowserCancelled(
        f"No agents installed — {kept} selection(s) discarded. Press enter to install."
    )
```

If "abort keeps the work" is a real requirement, the help text must read `esc install selection`, and the
action needs an explicit confirmation step — never the accidental-ESC path.

## F-03 — Terminal EOF inside `Application.run()` raises `EOFError`; nothing catches it → traceback

**Severity:** high
**Where:** `src/agency_agents/infrastructure/browser_app.py:197` (`application.run()`), `:166-171` (tty guard);
caller `src/agency_agents/cli/main.py:460-464` (catches only `BrowserCancelled`)

**Expected:** if the terminal goes away mid-session (ssh drop, tmux session killed, parent closes the pty,
`0</dev/null` on a tty-attached wrapper), the command reports a clean, actionable message and exits 1 —
which is the whole point of the guard at `browser_app.py:163-171`.

**Actual:** `Application.run()` raises `EOFError` when the input stream closes
(`prompt_toolkit/application/application.py:695` and `:727` do `f.set_exception(EOFError)`; `vt100.py:180`
raises it when stdin is not pollable). Verified experimentally:

```
EOF -> raised EOFError :
```

`run_browser` does not catch it, `_browse_and_install` does not catch it, so the user gets a Python
traceback instead of the message the guard was written to produce. Note the inconsistency that proves the
intent: `choose_tools` (`browser_app.py:88`) *does* catch `EOFError`. A real `SIGINT` raises
`KeyboardInterrupt` from the same call and is equally uncaught.

**Fix:**

```python
try:
    application.run()
except (EOFError, KeyboardInterrupt) as exc:
    raise BrowserCancelled(
        "The browser lost its terminal before you finished — nothing installed. "
        "Re-run in an interactive shell, or use `agency-agents install --tool <kebab> --no-interactive`."
    ) from exc
```

## F-04 — One detected tool without a `user` destination aborts the whole TUI run, after the user browses

**Severity:** high
**Where:** `src/agency_agents/cli/main.py:474-505` (`_browse_and_install`) vs `:365-380` (`install`)

**Expected:** the flag-driven path and the TUI path resolve the same target set the same way. For
"everything detected, no explicit `--tool`", `install` **skips** unsupported tools with a visible warning
and installs the rest (`main.py:366-380`).

**Actual:** `_browse_and_install` hard-aborts with exit 1 if *any* detected tool lacks a destination for
the scope (`main.py:497-505`). In the shipped `tools.json`, `cursor` has `detect: [".cursor"]` and
`dest.user: []` (project-only), and `aider`/`windsurf` are project-only too. So on an extremely common
machine — `~/.cursor` exists — `agency-agents tui` (default `--scope user`) opens the browser, the user
filters and selects agents, presses enter, and *then* gets
`❌ cursor has no user destination (supported: project)` and exit 1. Nothing is installed, and the work is
lost. Adding a second detected tool makes a perfectly installable `claude-code` selection fail with it.

**Fix:** mirror `install`'s skip-with-warning when `tool is None` (the detected set is ours, not the user's
choice), keeping the hard error only when the user explicitly passed `--tool`:

```python
unsupported = [t for t in selected_tools if not tools_catalog[t].dest.get(resolved_scope)]
if unsupported and tool is not None:
    ...  # hard error, as today
if unsupported:
    console.print(f"[bold yellow]⚠ Skipping tools with no {resolved_scope} destination: "
                  f"{', '.join(unsupported)} (use --scope project)[/bold yellow]")
    selected_tools = [t for t in selected_tools if t not in unsupported]
if not selected_tools:
    console.print("[bold yellow]No tool applicable to this scope — nothing installed.[/bold yellow]")
    raise typer.Exit(code=1)
```

## F-05 — Plugin install runs `subprocess.run` with no timeout on the TUI install path

**Severity:** high
**Where:** `src/agency_agents/infrastructure/installer.py:147-154`, reached from
`_install_agents` → `install_all_for_tool` → `install_plugin` (`installer.py:177-179`)

**Expected:** every outbound call has a bounded wait. This call shells out to `uv run python
scripts/build-hermes-plugin.py`, and `uv run` resolves/downloads the environment over the network.

**Actual:** `subprocess.run(..., check=True, capture_output=True, text=True)` — no `timeout=`. If uv stalls
on a proxy, a resolver lock, or a slow index, the CLI hangs indefinitely, after the full-screen TUI has
already exited (so the user sees a frozen prompt with no explanation). A missing `uv` binary raises
`FileNotFoundError`, which is neither `RuntimeError` nor `UnknownFormatError`, so it escapes the
`_install_agents` handler (`main.py:575-577`) as a traceback, mid-loop, after other tools were already
installed. `hermes` is `installKind: "plugin"`, `detect.dirs: [".hermes"]`, `dest.user` set — i.e. a
detected tool on a Hermes machine, selectable from the TUI today.

**Fix:**

```python
try:
    subprocess.run([...], check=True, capture_output=True, text=True, timeout=300)
except subprocess.TimeoutExpired as e:
    raise RuntimeError(f"Hermes plugin build timed out after 300s: {e.cmd[0]}") from e
except FileNotFoundError as e:
    raise RuntimeError("Hermes plugin build needs `uv` on PATH") from e
except subprocess.CalledProcessError as e:
    raise RuntimeError(f"Hermes plugin build failed: {e.stderr}") from e
```

---

# Medium

## F-06 — Every "nothing happened" path exits 0

**Severity:** medium
**Where:** `src/agency_agents/cli/main.py:466-468`, `:483-485`; reachable keys
`browser.py:213-214` (ACCEPT), `browser.py:112-121` (toggle semantics)

**Expected:** a successful install reports exit 0; a run that wrote nothing does not.

**Actual:** two paths print a yellow note and `return` → exit 0:
`ACCEPT` with an empty selection (`enter` pressed after filtering to nothing, or without ever toggling), and
`choose_tools` returning `[]` (the dialog is confirmed with nothing checked). A CI job or wrapper cannot
distinguish "installed 0 agents" from "installed fine". Worse, the *same* user outcome has two different
exit codes: `esc` with nothing selected → `BrowserCancelled` → exit 1 (`main.py:462-464`), `enter` with
nothing selected → exit 0. Verified: `apply_key(m, "enter")` on a no-match model returns `ACCEPT` with
`selection() == []`.

**Fix:** `raise typer.Exit(code=1)` on both, immediately after the message; keep exit 0 exclusively for
`main.py:530` ("✓ Installed N agent(s)").

## F-07 — Status line advertises "space to select"; space is unbound and silently resets the cursor

**Severity:** medium
**Where:** `src/agency_agents/infrastructure/browser.py:166` (status text), `:186-191` (`_TOGGLE = {"tab"}`),
`:242-244` (printable fallthrough), `:83-89` (`set_query` resets cursor)

**Expected:** the in-app status line is the primary hint surface; `"space to select"`
(`browser.py:166`) should toggle the current row, as every list UI does.

**Actual:** `_TOGGLE` contains only `"tab"`. Space is printable, so it is appended to the query — and because
`visible()` strips the query (`browser.py:78`), a space filters **nothing**, so the keystroke looks dead
while it silently resets the cursor to row 0. Measured:

```
cursor before space: 4
space -> continue  query=' '  cursor=0  selected=[]  visible=6  status="6 agents | 0 selected | ... space to select ..."
```

Repeated spaces accumulate invisible whitespace in the filter field with no matching effect — the filter
then appears "stuck" for the next characters.

**Fix:** either bind space to toggle (`_TOGGLE = {"tab", "space"}` plus `" " -> "space"` in the char map and
a `key == "space"` branch *before* the printable fallthrough) or correct the status text to
`"type to filter, tab to select, enter to install"`. Do not ship a hint that names a key the handler ignores.

## F-08 — `--tool` and `--scope` are validated only after the user finishes browsing

**Severity:** medium
**Where:** `src/agency_agents/cli/main.py:460-505` (browser at `:461`, validation at `:487-505`)

**Expected:** validate at the boundary, before an interactive surface is opened ("fail fast and closed").

**Actual:** `agency-agents tui --tool nope` opens the full-screen browser, lets the user filter and select,
and only then prints `❌ Unknown tool(s): nope` and exits 1. Same for `--scope global` and for a
destination-less tool. The integration tests
(`test_tui_rejects_an_unknown_tool`, `test_tui_rejects_an_invalid_scope`,
`test_tui_rejects_a_tool_without_the_requested_scope`) all pass because they monkeypatch `run_browser`, so
the wasted interactive session is invisible to them.

**Fix:** move `tools_catalog` load + unknown-tool + scope + destination checks above `run_browser`
(lines 470-505 hoisted above 460), leaving only the selection-dependent work after the browser returns.

## F-09 — Fixed 27-line layout is clipped on a standard 24-row terminal

**Severity:** medium
**Where:** `src/agency_agents/infrastructure/browser_app.py:28` (`LIST_HEIGHT = 15`), `:127-153`
(`render_screen`), `:186-196` (single non-scrolling `Window`, `full_screen=True`)

**Expected:** the browser adapts to, or at least refuses to run on, a terminal too small for it.

**Actual:** worst-case height = 3 header lines + 15 rows + 1 rule + 5 detail lines + 1 rule + 1 status +
1 help = **27 lines**. The layout is a single `Window` with no scrolling, so on the very common 24-row
terminal the tail is simply cut: the detail pane, the status line and the help line — i.e. the only place
the key map is documented, which matters even more while F-01 is unfixed — are off-screen with no
indication. Width is unbounded too: `FormattedTextControl` does not wrap, so `division/slug — name` and long
descriptions are silently truncated on narrow terminals.

**Fix:** derive the window from the real size instead of a constant, e.g. pass
`application.output.get_size().rows` into `render_screen(model, title, height)` and compute
`list_height = max(3, height - 12)`, plus a guard that prints a one-line "terminal too small (need 20x72)"
message rather than a half-drawn screen.

## F-10 — The tool dialog offers tools that cannot install at the resolved scope

**Severity:** medium
**Where:** `src/agency_agents/infrastructure/browser_app.py:73-95` (`choose_tools`), called from
`src/agency_agents/cli/main.py:479` while the scope is only resolved at `:492`

**Expected:** an interactive picker should not list choices guaranteed to fail one line later.

**Actual:** `choose_tools` builds `values` from **all** catalog tools. With the default `--scope user`,
choosing `aider` or `windsurf` (project-only in `tools.json`) produces
`❌ aider has no user destination (supported: project)` and exit 1 — after the browse, after the dialog,
with no way to recover inside the flow.

**Fix:** resolve `resolved_scope` before the dialog and filter:
`choose_tools(tools_catalog, detected, scope="user")` → `values` restricted to tools with
`definition.dest.get(scope)`. (Coordinate with F-08, which needs the same hoist.)

---

# Low

## F-11 — `backspace`/`c-u` on an empty query silently move the cursor to the top

**Severity:** low
**Where:** `src/agency_agents/infrastructure/browser.py:236-241` → `set_query` (`:83-89`)

**Expected:** a no-op key changes nothing.
**Actual:** `apply_key(m, "backspace")` with `query == ""` calls `set_query("")`, which resets `cursor = 0`.
Verified: cursor 5 → 0 with an empty query. Same for `c-u`. In a 300-agent list, one stray backspace loses
the user's place.
**Fix:** guard both branches (`if model.query:` … else return `CONTINUE` untouched), or reset the cursor in
`set_query` only when the query actually changed.

## F-12 — `_BACKSPACE` gets two entries that can never match, and a blanket `except` hides import failure

**Severity:** low
**Where:** `src/agency_agents/infrastructure/browser.py:193-199`

**Expected:** `str(Keys.ControlH)` meant to add `"c-h"` to the backspace set.
**Actual:** `str(Keys.ControlH) == "Keys.ControlH"` (verified), so `_BACKSPACE` contains the strings
`"Keys.ControlH"` and `"Keys.Backspace"` — dead entries; `Keys.Backspace is Keys.ControlH` anyway. The
`except Exception: pass` also swallows any real failure of a hard dependency, contrary to "no empty
handlers".
**Fix:** `_BACKSPACE.add(_Keys.ControlH.value)` (or delete the block entirely — the view already maps `\x08`
and `\x7f` to `c-h`/`backspace`) and narrow the handler to `except ImportError`.

## F-13 — A negative `model.cursor` renders no cursor highlight while the detail pane still shows a row

**Severity:** low
**Where:** `src/agency_agents/infrastructure/browser_app.py:111` (upper clamp only), `browser.py:103-109`
(`current()` uses `min(cursor, len-1)` with no lower clamp)

**Expected:** one invariant — the cursor index is `0 <= cursor < len(visible)`.
**Actual:** with `cursor = -2`, `_draw_window` clamps to `-2` and no row carries `class:cursor`, while
`current()` resolves `visible[-2]` and the detail pane describes the second-to-last agent. Verified:
`cursor=-2` → `cursor style rows: []`, `current() = a003`. Unreachable through `apply_key` (`move` clamps at
0), but `BrowserModel` is a public mutable dataclass and `test_browser.py` already assigns `model.cursor`
directly.
**Fix:** `cursor = max(0, min(model.cursor, len(visible) - 1))` in `_draw_window`, and clamp in
`current()`; add an invariant test.

## F-14 — Pasting into the browser is silently dropped

**Severity:** low
**Where:** `src/agency_agents/infrastructure/browser.py:242-244`

**Expected:** pasting an agent name filters to it (the only use of paste in this UI).
**Actual:** bracketed paste arrives as a single `KeyPress(Keys.BracketedPaste, "growth hacker")` (verified);
`apply_key` sees a multi-character string, skips the printable branch, and returns `CONTINUE`. Nothing
happens and nothing explains why.
**Fix:** bind `Keys.BracketedPaste` explicitly — take the first line, `strip()`, and call
`model.set_query(line)` — or show a dim hint that paste is not supported.

## F-15 — Any printable event carrying more than one code point is dropped

**Severity:** low
**Where:** `src/agency_agents/infrastructure/browser.py:242`

**Expected:** `len(key) == 1 and key.isprintable()` is the whole printable contract.
**Actual:** single code points are fine — `é`, `日`, `😀` all append correctly (verified), and so does
`model.query + key` / `query[:-1]` for non-ASCII. But a two-code-point grapheme (`"e\u0301"`) or any IME /
compose event spanning several code points fails `len(key) == 1` and is discarded without feedback.
**Fix:** accept `key.isprintable()` on the data payload and append it, keeping the `len == 1` guard only for
the single-byte named-key path (see F-01 for the surrounding restructure).

## F-16 — The seam that broke has no test, which is why F-01/F-02 shipped

**Severity:** low (process; the root cause of the critical finding)
**Where:** `src/agency_agents/tests/unit/test_browser.py:352-380` (tests `apply_key(model, "down")`),
`src/agency_agents/tests/integration/test_cli_tui.py:120-127` (`fake_browser` replaces `run_browser` entirely)

**Expected:** per D-001 (`docs/dx/m7-tool-decisions.md`), every behaviour the browser claims is asserted
against a pure function. The byte→name adapter (`_NAMED_KEYS` + the `Keys.Any` handler) is pure and is
**not** covered by a single test; `_draw_window` is only reached indirectly through `render_screen`.
**Actual:** the suite asserts that the model handles `"down"`, never that the view can produce `"down"`.
Every key-defect in this report passes CI.
**Fix:** after extracting `key_name()` (F-01), table-test it with real byte sequences and real `Keys`
members; add `_draw_window` tests for empty/1/N-row models and for the cursor-at-bottom clamp; add a
`run_browser` test that patches `Application` (or uses `create_pipe_input`) with `\x1b[A` and asserts
`model.cursor == 1`.

---

# Verified correct (explicitly checked, no change needed)

These were asked about directly, so here is the confirmation with the evidence:

1. **`_draw_window` windowing math — correct, no off-by-one, no blank list.**
   `browser_app.py:111-113` clamps the window start with
   `start = min(max(0, cursor - LIST_HEIGHT // 2), max(0, len(visible) - LIST_HEIGHT))`.
   Exhaustively walked for `len(visible) ∈ {0, 1, 14, 15, 16, 40}` × `cursor ∈ {0, 5, 7, 20, 39}`:
   the window is never longer than `LIST_HEIGHT`, the cursor row is always inside it
   (centered at index 7 mid-list, pinned to index 14 at the bottom, index 0 at the top), and a lone row is
   rendered at index 0. Centering, bottom clamp and top clamp are all correct.
2. **Empty `visible()` — correct.** `_draw_window` returns `([], 0)`; `render_screen:136-139` substitutes
   `" no agent matches this filter"`; `detail_lines:146-147` substitutes
   `"No agent matches the current filter."`; `status_line` reports `0/N shown`. No blank or broken screen.
3. **`BrowserModel` determinism — correct.** `build_rows` sorts by `(division, name.lower(), slug)`
   (`browser.py:61`), so the non-deterministic `rglob` order in `_collect_by_division`
   (`main.py:131`) cannot leak into the UI. `selection()` walks `self.rows` (roster order), not the
   `selected` set, so the plan is reproducible regardless of click order. `visible()` preserves row order.
   `set_query` resets the cursor to 0. Verified against the live 299-agent roster: no duplicate slugs, and
   no agent slug resolves to a *different* agent through `build_roster_index`'s `setdefault` aliasing, so
   `select_agents(by_division, agent_ids=selection())` round-trips exactly. (Latent coupling worth noting:
   row identity is the bare slug, so two divisions sharing a slug would make `is_selected` toggle both rows
   and `selection()` emit a duplicate — currently impossible, and `agency-agents lint` is the right place to
   keep it that way.)
4. **`apply_key` edge cases — correct except the three noted above.** Unknown named keys (`"f13"`) are
   ignored without touching state; `backspace` removes exactly one code point; `c-u` clears; single-code-point
   non-ASCII (`é`, `日`, `😀`) appends and filters correctly; control bytes that are not mapped
   (`\x04`, `\x17`, `\x00`) fall through harmlessly rather than entering the query.
5. **`_browse_and_install` aggregate failure handling — correct.** A tool that fails raises
   `RuntimeError`/`UnknownFormatError`, is collected in `failures`, and the command exits 1 after attempting
   the rest (`main.py:521-529`, `_install_agents:548-578`). No silent partial success. And
   `InstallationManager.prune_output` (`installer.py:59-66`) is a no-op, so a browser-driven install cannot
   delete previously installed agents — the one data-loss scenario I looked for is not present.

---

# Smallest set of changes to reach a safe state

1. **One patch in two files** fixes F-01 + F-02 + F-03: extract `key_name()` into `browser.py`, dispatch on
   `event.key.value` (F-01), make `ABORT` always cancel (F-02), wrap `application.run()` in
   `except (EOFError, KeyboardInterrupt)` (F-03). This alone makes the TUI navigable, honest, and
   non-destructive.
2. **Then correctness of the install target:** F-04 (skip, don't abort, for detected tools) and F-05 (bound
   the `subprocess.run`). These are what make the command safe to run on a real machine.
3. **Then the honesty pass:** F-06 (no-op exits 1), F-07 (space), F-08/F-10 (validate before the browser,
   filter the dialog by scope), F-09 (height-aware window).
4. **Then tests:** F-16 — table-test `key_name()` and add a `run_browser` test that feeds `\x1b[A`, so this
   class of defect can never ship again.

---

# Appendix — reproduction commands

All evidence in this report is reproducible with the repo's own virtualenv:

```bash
# 1. What prompt_toolkit actually delivers for an arrow key
.venv/bin/python - <<'EOF'
from prompt_toolkit.input.vt100_parser import Vt100Parser
for seq in ('\x1b[A', '\x1b[B', '\x1b[5~', '\x1b[6~'):
    keys = []
    p = Vt100Parser(keys.append); p.feed(seq); p.flush()
    print(repr(seq), [(k.key.name, k.key.value, k.data) for k in keys])
EOF

# 2. The same bytes through the app's dispatch chain
.venv/bin/python - <<'EOF'
import sys; sys.path.insert(0, "src")
from agency_agents.infrastructure.browser import BrowserModel, BrowserRow, apply_key
from agency_agents.infrastructure.browser_app import _NAMED_KEYS
m = BrowserModel(rows=[BrowserRow("d", f"a{i}", f"A{i}", "x") for i in range(3)])
for raw in ("\x1b[A", "\x1b[B", "\x1b[5~", "\x1b[6~"):
    before = m.cursor
    apply_key(m, _NAMED_KEYS.get(raw, raw))
    print(repr(raw), "cursor", before, "->", m.cursor)   # unchanged: arrows are dead
EOF

# 3. Space is not a toggle and resets the cursor
.venv/bin/python -c "
import sys; sys.path.insert(0,'src')
from agency_agents.infrastructure.browser import BrowserModel, BrowserRow, apply_key
m=BrowserModel(rows=[BrowserRow('d',f'a{i}',f'A{i}','x') for i in range(6)]); m.move(4)
apply_key(m,' '); print(m.cursor, repr(m.query), m.selection())"

# 4. Existing suite is green — it does not cover the seam
.venv/bin/python -m pytest src/agency_agents/tests/unit/test_browser.py \
    src/agency_agents/tests/integration/test_cli_tui.py -q     # 52 passed
```
