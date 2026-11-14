# Reliability Re-Verification — Interactive TUI (`tui`, bare `install`), fix pass 1

**Reviewer role:** Correctness & runtime reliability
**Mode:** VERIFY of `project-tasks/tui-review/reliability.md` (F-01..F-16) against the **current working tree** (uncommitted changes; base `253cae4`).
**Verdict: 🟡 Needs Hardening** — up from 🔴 *Unsafe to Ship*. Every destructive defect is closed: no key documented as "cancel" installs, no arrow key installs, no unbounded plugin wait, no silent-exit-0 no-op path. What remains is honesty/robustness debt plus **one new defect in new code that re-creates the exact bug class this pass was fixing**.

**Tally:** 12 RESOLVED · 3 PARTIAL · 2 NOT-RESOLVED · **0 REGRESSION** · 0 DEFERRED
**New defects found:** 9 (1 medium, 2 low, 6 nits/hardening) — none can corrupt installed state.

**Files re-read as they are now:** `src/agency_agents/infrastructure/browser.py`, `browser_app.py`, `src/agency_agents/cli/main.py` (`_browse_and_install`, `_install_agents`, `install`), `src/agency_agents/infrastructure/installer.py`, `src/agency_agents/tests/unit/test_browser.py`, `src/agency_agents/tests/integration/test_cli_tui_headless.py` (+ the touched CLI tests).

---

## 0. Re-run evidence (executed, not inferred)

```
$ uv run pytest src/agency_agents/tests/unit/test_browser.py \
                src/agency_agents/tests/integration/test_cli_tui_headless.py -q
51 passed in 1.52s            # test_browser.py 41 + test_cli_tui_headless.py 10

$ uv run pytest -q
300 passed in 6.17s           # whole suite green, no xfail/skip inflation

$ uv run ruff check <5 changed files + tests>
All checks passed!
$ uv run mypy src/agency_agents/infrastructure/browser_app.py
Success: no issues found in 1 source file
```

**The exact reproduction the task asked for:**

```
key_name('up',      '\x1b[A')  -> 'up'        match=True
key_name('down',    '\x1b[B')  -> 'down'      match=True
key_name('pageup',  '\x1b[5~') -> 'pageup'    match=True
key_name('pagedown','\x1b[6~') -> 'pagedown'  match=True

apply_key(model, key_name("down", "\x1b[B")): cursor 0 -> 1     # moves ✅
apply_key(model, "\x1b[B")                  : cursor 0 -> 0     # still a no-op — and now unreachable
```

**The old dispatch path is gone, verified at the source level, not just behaviourally:**

```
$ grep -rn "_NAMED_KEYS" src/ --include=*.py
(no output)                       # the broken byte map no longer exists
$ grep -n "key_sequence\|key_name(" src/agency_agents/infrastructure/browser_app.py
215:        press = event.key_sequence[0]
218:            result = apply_key(model, key_name(key, event.data))
```

`apply_key(model, "\x1b[B")` remaining a no-op is now *correct*: a raw escape sequence is not a key name, and no caller produces one. The seam is `key_name`, and it is table-tested.

**End-to-end through the real `Application` (pipe input + `DummyOutput`, pipe left open so no EOF race):**

```
down  (\x1b[B\t\r)  -> ['growth-hacker']      ok
up    (\x1b[A\t\r)  -> ['backend-architect']  ok
pagedown (\x1b[6~\t\r, 30 rows) -> ['a-010']  ok  (PAGE_SIZE=10)
c-a all then enter  -> ['backend-architect', 'growth-hacker']
c-x clear then enter-> []
tab toggle          -> ['backend-architect']
```

---

## 1. Per-finding verdicts

| # | Verdict | One-line reason |
|---|---------|-----------------|
| **F-01** | ✅ **RESOLVED** | `key_name()` is pure and table-tested; `event.key_sequence[0].key.value` + char-map-first resolves `up/down/pageup/pagedown` (and keeps `tab/enter/backspace`, which pt names `c-i`/`c-m`/`c-h`); verified end-to-end through a real `Application`. `_NAMED_KEYS` is deleted, so the dead path cannot come back. |
| **F-02** | ✅ **RESOLVED** | Any `ABORT` now cancels: `esc`, `c-c`, `c-q`, with and without a selection (verified: all five abort paths raise `BrowserCancelled("No agents installed — selection cancelled.")`). The destructive install-on-esc is gone, including for the degraded "ESC then `[`" arrow split, which now cancels instead of installing. |
| **F-03** | ✅ **RESOLVED** | `application.run(handle_sigint=False)` inside `except (EOFError, KeyboardInterrupt)`; verified by closing the pipe mid-run and by injecting `KeyboardInterrupt` from `run()` — both surface as the intended `BrowserCancelled` message, no traceback. |
| **F-04** | ✅ **RESOLVED** | Detected project-only tools are skipped with a warning and the rest install (verified with a `cursor`-style project-only tool + `claude-code`, scope=user: exit 0, `⚠ Skipping tools with no user destination: cursor`, 1 agent written); all-unsupported set → `No tool applicable to this scope` + exit 1; explicit `--tool` still hard-errors. |
| **F-05** | ✅ **RESOLVED** | `timeout=300` present, and all three failure classes are converted to actionable `RuntimeError`s — verified by injecting `TimeoutExpired` → "timed out after 300s: uv", `FileNotFoundError` → "needs `uv` on PATH", `CalledProcessError` → "failed: <stderr>". The TUI can no longer hang or traceback after the alt-screen closes. |
| **F-06** | ✅ **RESOLVED** | Both no-op paths raise `typer.Exit(code=1)`: empty browser selection (verified, and the integration assertion was updated 0→1) and empty tool dialog (verified: `exit=1, No tool selected — nothing installed.`). Exit 0 is now reserved for a real install. |
| **F-07** | ⚠️ **PARTIAL** | The lie is gone — status line now reads `type to filter, tab to select, enter to install`. But the *mechanism* it documented is untouched: `apply_key(m, " ")` still appends an invisible space and **resets the cursor to row 0** (verified: cursor 4 → 0, `query=' '`, `selected=[]`, filters nothing), and the F-11 no-op guard does not cover it because the query *does* change. |
| **F-08** | ✅ **RESOLVED** | Tool/scope/destination checks are hoisted above `run_browser`; verified that `--tool nope`, `--scope global` and `--tool cursor` (project-only, scope=user) all exit 1 **without opening the browser** (`browser_opened=False`). |
| **F-09** | ⚠️ **PARTIAL** | A guard exists, but its threshold is wrong: it admits **≥60x20** while `render_screen` still emits **27 lines** and 72-column rules (measured: 27 non-empty lines with `LIST_HEIGHT=15`). Verified: a **80x24** terminal — the exact case reported — and a 60x20 terminal both pass the guard and are still clipped; only <20 rows / <60 cols are refused. Adaptive height was explicitly deferred. |
| **F-10** | ✅ **RESOLVED** | `choose_tools(..., scope=...)` filters by destination; verified by capturing the widget's `values`: scope=user → `['claude-code']`, scope=project → `['cursor']`, scope=None → both. Defaults stay consistent with detection. |
| **F-11** | ✅ **RESOLVED** | `set_query` returns early on an identical query; verified `backspace` and `c-u` on an empty query leave the cursor at 5. |
| **F-12** | ✅ **RESOLVED** | The dead `_BACKSPACE.add(str(Keys.ControlH))` block and its blanket `except Exception: pass` are deleted, replaced by an explicit `_CHAR_NAMES` table; the backspace set is now static and the view no longer guesses. |
| **F-13** | ⚠️ **PARTIAL** | `current()` is lower-clamped (verified: `cursor=-2` → `a-000`, not the second-to-last row). `_draw_window` is **not**: `cursor = min(model.cursor, len(visible)-1)` still yields `-2`, so no row carries `class:cursor` while the detail pane describes row 0 — the invariant is now enforced in one place and violated in the other. |
| **F-14** | ❌ **NOT-RESOLVED** | Pasting is still silently dropped: `\x1b[200~growth\x1b[201~` arrives as `Keys.BracketedPaste`, `apply_key` sees a multi-character payload, matches nothing and returns `CONTINUE` (verified end-to-end: the paste filtered nothing). No hint was added either. |
| **F-15** | ❌ **NOT-RESOLVED** | `len(key) == 1` printable contract unchanged; `e\u0301` is still discarded (verified: query unchanged at `'A'`). Not touched by this pass. |
| **F-16** | ✅ **RESOLVED** | The formerly invisible seam is now covered at both levels: 6 new unit tests (`key_name` table incl. the `c-i`/`c-m` trap, `apply_key` on arrow names, `_display_safe`, `set_query` no-op, negative-cursor clamp) and 10 headless tests that drive the **real** `run_browser` (arrows move, pagedown pages, esc/c-c cancel with and without selection, enter accepts, handler exception cancels). Residual gap: the *new* failure paths added in this pass (size guard, EOF message, F-04 skip branch, "internal error") have **no test** — see N-02/N-10. |

**Regression check on the previously-verified-correct behaviour:** `_draw_window` windowing, empty-`visible()` rendering, `BrowserModel` determinism, and `_browse_and_install` aggregate failure handling all still hold (suite green, spot-checked `render_screen` for empty/1/N rows). I found **no regression** in anything the first report certified.

---

## 2. New defects introduced or exposed by this pass

### N-01 — The tool dialog's "Esc cancels" is a two-key *chord*, so Esc alone does nothing 🟠 MEDIUM

**Where:** `src/agency_agents/infrastructure/browser_app.py:94-96` (`choose_tools`)
**Trigger:** `agency-agents install` on a machine with **no detected tool** — the first-run path, i.e. the primary way a new user meets this dialog. It is also the surface whose own label says `"Space toggles, Tab moves, Enter confirms, Esc cancels."`

```python
@bindings.add("escape", "c-c")          # ← ONE binding, key SEQUENCE: Escape, then Ctrl-C
def _cancel(event) -> None:
    event.app.exit(exception=KeyboardInterrupt())
```

`KeyBindings.add(*keys)` takes **one positional per key in the sequence** (`key_bindings.py`: `keys = tuple(_parse_key(k) for k in keys)`), so this registers Escape‑then‑Ctrl‑C, **not** "Escape or Ctrl-C".

**Current behaviour (verified, 4 s alarm around a real `Application` + pipe input):**

| keys sent | result |
|---|---|
| `\x1b\x03` (Esc **then** Ctrl‑C) | `BrowserCancelled` — proves the chord is what got bound |
| `\x1b` (Esc alone) | **dialog still running** (key buffered as a sequence prefix, then discarded — it also swallows the *next* keystroke) |
| `\x03` (Ctrl‑C alone) | **dialog still running** |

**Expected:** Esc and Ctrl‑C each cancel on their own, as the label and the docstring ("Escape and Ctrl-C cancel — the same keys the browser teaches") both promise. This is the *same* defect class as F-07/F-02 — a UI that documents a key the handler does not implement — reintroduced in new code by the same pass that fixed it.

**Impact:** not a lock — Tab‑Tab‑Enter reaches the **Cancel** button, which returns `None` → `[]` → `"No tool selected — nothing installed."` + exit 1. So it degrades to "the documented escape hatch is dead", not "the app is stuck".

**Fix (smallest):**

```python
def _cancel(event) -> None:
    event.app.exit(exception=KeyboardInterrupt())

bindings.add("escape")(_cancel)
bindings.add("c-c")(_cancel)
```

Then add a headless `choose_tools` test that feeds `"\x1b"` and `"\x03"` and asserts `BrowserCancelled` — the guard that would have caught this.

### N-02 — The size guard consults the wrong size source and admits terminals it knows are too small 🟡 LOW

**Where:** `browser_app.py:200-208`
`shutil.get_terminal_size()` reads `COLUMNS`/`LINES` **from the environment first**, then `os.get_terminal_size(sys.__stdout__)`. Consequences:

1. **False refusals / false passes under stale `COLUMNS`/`LINES`** — very common in `tmux`, CI wrappers and long-lived shells. A user in a 200x50 terminal with `COLUMNS=40` exported is refused; the reverse silently passes.
2. **The threshold contradicts the layout** — guard says 60x20, layout needs 74x27 (F-09). Measured: 80x24 and 60x20 both pass and render clipped.
3. It queries stdout's terminal, not `application.output`, so a session where pt renders to `/dev/tty` is measured on the wrong device.

**Fix:** after `Application` construction, `size = application.output.get_size()` (`Output.get_size()` already does the env-var dance *and* the right fd), and drive both the guard and `render_screen(model, title, height)` from it so the guard can never be looser than the layout.

### N-03 — `_safe()` strips newlines, flattening multi-line error messages 🟡 LOW

**Where:** `cli/main.py:46-58`, applied at `:608` (`Error installing {tool}: {_safe(e)}`)
`"".join(c for c in str(value) if c >= " " ...)` drops `\n` (and `\t`). Verified:

```
in : 'Installation failed due to slug collisions:\n  - a/b/c vs d/e/f\n  - x/y/z'
out: 'Installation failed due to slug collisions:  - a/b/c vs d/e/f  - x/y/z'
```

The slug-collision report is the one message in the CLI that is *designed* to be read as a list, and it now arrives as one run-on line. The markup/control-char hardening is right; the newline loss is collateral. **Fix:** keep `\n` (and optionally `\t`) in the allowlist: `if c in "\n\t" or (c >= " " and ...)`.

### N-04 — Broad `except Exception` around the install loop masks programmer errors 🟡 NIT (design)

**Where:** `cli/main.py:604-608` — was `except (RuntimeError, UnknownFormatError)`, now `except Exception`.
A `TypeError`/`AttributeError` in the converter is now reported as `❌ Error installing tool: <message>` and the traceback is lost, which makes a code bug indistinguishable from an I/O failure. **Fix:** `except (RuntimeError, UnknownFormatError, OSError, subprocess.SubprocessError)` — and if broad catching is deliberate (one bad tool must not abort the rest), log the traceback at debug level.

### N-05 — `install_plugin` silently changed from no-op to raising 🟡 NIT (API)

**Where:** `installer.py:140-144` — unknown tool and non-plugin tool now `raise RuntimeError` instead of `return`. Correct today (`install_all_for_tool` only calls it when `installKind == "plugin"`, verified by grep: no other caller), and the suite is green — but this is an untested behaviour change with a blast radius outside the TUI. **Fix:** one test per branch (`install_plugin("claude-code")` → `RuntimeError`).

### N-06 — `_atomic_write` uses a fixed sibling temp name 🟡 NIT

**Where:** `installer.py:121-133` — `tmp = path.with_name(path.name + ".tmp")`.
Good change (a torn write can no longer masquerade as a full install; `prune_output` remains a no-op so nothing is deleted). Two residuals: two concurrent installs of the same artifact race on the same temp path, and a failed `os.replace` leaves `<artifact>.md.tmp` inside the user's tool config dir. **Fix:** `tempfile.NamedTemporaryFile(dir=path.parent, delete=False)` + `finally: unlink(missing_ok=True)`.

### N-07 — `event.key_sequence[0]` can disagree with `event.data` 🟡 NIT

**Where:** `browser_app.py:215-218`. For a flushed multi-press sequence the first press and the raw data describe different things. Harmless today (everything that matters arrives as one press) but undocumented — one sentence in `key_name`'s docstring is enough.

### N-08 — An outcome-less `Application.run()` fails **open** (accepts the selection) 🟡 HARDENING

**Where:** `browser_app.py:240-257`. If `run()` returns without an `ACCEPT`/`ABORT` outcome, `outcome.get("result")` is `None`, the `ABORT` check is skipped, and `return model.selection()` installs whatever happened to be selected. No such path exists today (EOF raises, every exit sets an outcome), but the safe default is the other way round: an exit nobody asked for should cancel. **Fix:** `if outcome.get("result") != ACCEPT: raise BrowserCancelled(...)`.

### N-09 — F-02 residual: a split arrow key now discards the user's selection with no confirmation 🟡 UX/HARDENING

With F-01 fixed, arrows work — but on a slow ssh/tmux link that delivers `\x1b` and `[A` in two chunks, the lone ESC is `ABORT` and the whole session ends: `No agents installed — selection cancelled.` Verified (`"\x1b["` → `BrowserCancelled`). This is strictly better than installing, and I am **not** asking to revert it. If "abort keeps the work" ever becomes a requirement, the answer is `esc` → *"discard N selections? y/n"*, never an implicit install.

---

## 3. Smallest set of changes to reach "Reliable"

1. **N-01 (blocking for honesty):** split the cancel binding into two `bindings.add` calls + a headless `choose_tools` test for `"\x1b"` and `"\x03"`. ~6 lines.
2. **F-09 / N-02 (one change, two findings):** thread the real `application.output.get_size()` into `render_screen`, compute `list_height = max(3, rows - 12)`, and set the guard threshold *from* that computation so a terminal that passes the guard cannot be clipped. This closes F-09 for the common 24-row case and removes the stale-`COLUMNS` hazard.
3. **F-13:** one line — `cursor = max(0, min(model.cursor, len(visible) - 1))` in `_draw_window` — plus an invariant assertion in the existing `render_screen` test.
4. **F-07:** either bind space to toggle (`_TOGGLE = {"tab", "space"}`, `" " -> "space"` in `_CHAR_NAMES`, branch before the printable fallthrough) or make a whitespace-only query a no-op in `set_query` so a stray space stops yanking the cursor.
5. **N-03 / N-04:** keep `\n` in `_safe`; narrow the install-loop handler.
6. **F-14 / F-15 (both cheap, both about not lying to the user):** add a `Keys.BracketedPaste` binding that takes the first line, `strip()`s and `set_query`s it; relax the printable branch to `key.isprintable()` on the payload so combining marks compose.
7. **Tests for the paths this pass added and did not cover:** size guard, EOF/`KeyboardInterrupt` message, F-04 skip-with-warning and "no tool applicable" (verified manually here, but nothing pins them — the existing `"Skipping tools with no user destination"` assertion lives in `test_install_cli.py` and covers the *flag* path only).

---

## 4. Residual risk register (unchanged from the first report, for continuity)

* `esc` discards work without confirmation (N-09) — acceptable, documented.
* Row identity is the bare slug, so two divisions sharing a slug would make `toggle` act on both rows; still impossible in the shipped roster, still unenforced (`agency-agents lint` is the right home).
* `_display_safe` escapes at **build** time rather than render time, so `BrowserRow.division/name/description` are no longer the catalog's strings. Harmless today (`slugs_for_division` is test-only), but it is a data-vs-display layering choice worth a comment, and it would bite the day a division-jump key compares `row.division` to a raw `divisions.json` value.
* Nothing in this pass can corrupt already-installed files: writes are atomic, `prune_output` is still a no-op, and the failure path collects per-tool errors and exits 1 after attempting the rest.

---

## Appendix — reproduction script for everything above

```bash
# 1. Targeted suites + full suite
uv run pytest src/agency_agents/tests/unit/test_browser.py \
              src/agency_agents/tests/integration/test_cli_tui_headless.py -q   # 51 passed
uv run pytest -q                                                              # 300 passed

# 2. F-01: key_name translation and the cursor actually moving
uv run python - <<'EOF'
import sys; sys.path.insert(0, "src")
from agency_agents.infrastructure.browser import BrowserModel, BrowserRow, apply_key, key_name
m = BrowserModel(rows=[BrowserRow("d", f"a{i}", f"A{i}", "x") for i in range(3)])
for raw, name in (("\x1b[A","up"),("\x1b[B","down"),("\x1b[5~","pageup"),("\x1b[6~","pagedown")):
    print(name, "->", key_name(name, raw))
apply_key(m, key_name("down", "\x1b[B")); print("cursor:", m.cursor)   # 1
EOF

# 3. F-02/F-03: every exit path through the real Application (pipe left open)
uv run python - <<'EOF'
import os, sys; sys.path.insert(0, "src")
from unittest import mock
from prompt_toolkit.application import create_app_session
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput
from agency_agents.infrastructure.browser import BrowserModel, BrowserRow
from agency_agents.infrastructure.browser_app import BrowserCancelled, run_browser
def model(): return BrowserModel(rows=[BrowserRow("d","a","A","x"), BrowserRow("d","b","B","y")])
def drive(keys, close=False, size=(80,24)):
    with create_pipe_input() as p, create_app_session(input=p, output=DummyOutput()):
        with mock.patch.object(sys.stdin,"isatty",lambda: True), \
             mock.patch.object(sys.stdout,"isatty",lambda: True), \
             mock.patch("shutil.get_terminal_size", lambda: os.terminal_size(size)):
            if keys: p.send_text(keys)
            if close: p.close()
            return run_browser(model(), title="t")
for k in ("\x1b", "\t\x1b", "\t\x03", "\t\x11", "\x1b["):
    try: print(repr(k), "RETURNED", drive(k))
    except BrowserCancelled as e: print(repr(k), "cancelled:", e)
try: drive(None, close=True)
except BrowserCancelled as e: print("EOF ->", e)
EOF

# 4. F-09: the guard admits terminals the layout cannot fit
#    27 non-empty rendered lines; guard threshold is 20 rows / 60 cols.
uv run python -c "
import sys; sys.path.insert(0,'src')
from agency_agents.infrastructure.browser import BrowserModel, BrowserRow
from agency_agents.infrastructure.browser_app import render_screen
m = BrowserModel(rows=[BrowserRow('d', f'a-{i:03d}', f'A{i}', 'desc') for i in range(30)])
lines=''.join(t for _,t in render_screen(m,'T')).split('\n')
print('rendered lines:', len([l for l in lines if l]))"

# 5. N-01: the dialog's cancel is a chord, not two keys  (4s alarm per key)
#    see the probe in this report: '\x1b\x03' cancels; '\x1b' and '\x03' hang.
```
