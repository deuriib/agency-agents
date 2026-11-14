# TUI Resilience Review — re-verification after the fix pass

**Scope (working tree, uncommitted):** `src/agency_agents/infrastructure/browser_app.py`,
`browser.py`, `src/agency_agents/cli/main.py`, `src/agency_agents/infrastructure/installer.py`,
`src/agency_agents/tests/integration/test_cli_tui_headless.py` (+ the edited `test_cli_tui.py`,
`test_cli_commands.py`, `test_browser.py`).

**Baseline:** repo `main` @ `253cae4` (v1.14.0), Python 3.13.18, prompt-toolkit 3.0.53, typer,
rich. Diff under review: `+314 / -99` across 7 files.

**Method:** this pass did not re-discover. Each row of `resilience.md` was re-run against the
code as it is now, with the original reproduction where one existed: `pty.fork()` + `TIOCSWINSZ`
harnesses driving the *real* CLI (`.venv/bin/agency-agents`, no `uv` wrapper, so signals land on
the right process), fault-injected installers, a closed-pipe EOF scenario, an injected
`ENOSPC` during a write, and a read-only project directory. Harnesses are committed alongside
this report:

* `project-tasks/tui-review/reverify_probe.py` — pty runner (keys, signals, winsize, alt-screen detection).
* `project-tasks/tui-review/reverify_run.py` — M6 / M4 / M1a / M1b / M5 / M2 / C1 / M3 / L2 / H1.
* `project-tasks/tui-review/reverify_run2.py` — SIGINT & SIGTERM, EOF, arrow keys, dialog smoke.
* `project-tasks/tui-review/reverify_run3.py` — arrow-key install proof, EOF, two-phase dialog.
* `project-tasks/tui-review/reverify_run4.py` — atomic write, `--jobs 0`, plugin path, H1 end-to-end, M1c, L1.
* `project-tasks/tui-review/reverify_run5.py` — H3 root cause + verified one-line fix, dialog SIGINT.

**Test suite:** `uv run pytest -q` → **300 passed, 2 warnings in 5.75 s** (0 failed, 0 errors;
the new module alone: 10 passed). `ruff check src/agency_agents` → clean. `mypy src/agency_agents`
→ 36 errors, **identical count and locations to the `HEAD` baseline** (verified by stashing the
working tree), so no typing regression.

---

## 1. Verdicts

| ID | Original finding | Verdict | Evidence (re-run) |
|---|---|---|---|
| **C1** | key-handler exception freezes the app, needs SIGKILL, terminal left in alt screen | **RESOLVED** | `apply_key` patched to raise on the 2nd keystroke, real pty: exit **1** in 3.7 s, `ESC[?1049l` present (terminal restored), message `The browser hit an internal error (boom from apply_key). Nothing was installed. Use the flags instead: …`. Pinned by `test_an_exception_in_the_key_handler_cancels`. |
| **H1** | one unexpected exception aborts the whole batch | **RESOLVED** | Unit fault injection (`PermissionError` on `t2`): `INSTALLED t1 / ❌ Error installing t2 / INSTALLED t3 / FAILURES ['t2']`. End-to-end in a read-only cwd: `❌ Error installing claude-code: [Errno 13] Permission denied: '/tmp/…/.claude'` + `❌ 1 tool(s) failed to install: claude-code`, exit 1, **no traceback**. |
| **H2** | non-atomic writes leave truncated artifacts | **RESOLVED (core claim)** | `_atomic_write` is used by both `install_agent_for_tool` and `install_roster`. Injected `ENOSPC` after a partial `write_text`: target **does not exist**, no torn content. Residual nits in §3 (`.tmp` orphan, fixed tmp name). |
| **H3** | tool-picker modal has no escape hatch, misdescribes its keys | **PARTIAL — escape hatch still unreachable by the keys users press** | `bindings.add("escape", "c-c")` registers a **two-key sequence**, not two alternatives. Real pty, dialog open: `Esc` alone → **frozen** (SIGKILL at 16 s); `Ctrl-C` alone → **frozen**; `Esc Esc` → frozen; only `Esc` **then** `Ctrl-C` exits. Isolated repro of both variants in `reverify_run5.py`; the corrected form (two separate handlers) exits cleanly on `Esc` **and** on `Ctrl-C`. See §3-N2/N3. |
| **M1** | "nothing installed" exits 0 | **RESOLVED** | Browser `Enter` with nothing selected → exit **1** (`Nothing selected — nothing installed.`). Dialog `Cancel` / `Ok` with nothing ticked → exit **1**. Non-interactive empty matches now exit 1 too (`Unknown agent 'does-not-exist'`, `No agent ids found in …`). `test_cli_tui.py:240` updated to assert 1. |
| **M2** | OS SIGINT ignored while the browser runs | **PARTIAL** | Browser: `kill -INT` (direct and via `exec`, i.e. process group) → exit **1** in ~3.1 s, alt screen restored, flag-naming message. **But the tool dialog still ignores SIGINT**: with the dialog open, SIGINT at t=4 s left the process frozen until the 16 s harness timeout (`choose_tools`' `Application` keeps the default `handle_sigint`). |
| **M3** | `EOFError`/`KeyboardInterrupt` escape as a traceback | **RESOLVED** | Closed input stream behind a mocked tty → `BrowserCancelled: The browser lost its terminal before you finished — nothing installed. Re-run in an interactive shell, or use 'agency-agents install --tool <kebab> --no-interactive'.` No traceback. Nit: exit is 1, not the conventional 130. |
| **M4** | `--tool`/`--scope` validated only after the interactive session | **RESOLVED** | `tui --tool bogus-tool` → exit 1 in **0.7 s** with `❌ Unknown tool 'bogus-tool'.`; no frame drawn (`ESC[?1049h` never emitted). Scope and unsupported-scope checks were hoisted with it, and the picker now filters by scope. |
| **M5** | in-app help advertises keys that do nothing | **RESOLVED** | Real installs into a temp `$HOME`: `tab,enter` → `anthropologist.md`; **`Down`+tab+enter → `geographer.md`**; **`PageDown`+tab+enter → `ui-designer.md`**; `Ctrl-N`+tab → `geographer.md`. Status line now reads `type to filter, tab to select, enter to install`. Residual: the README key table still says "arrow keys are not bound yet". |
| **M6** | no minimum-terminal-size guard | **PARTIAL** | Guard exists and is loud: 40x15 pty → exit 1, `The browser needs at least 60x20, this terminal is 40x15. Resize it, or skip the browser…`, no alt screen entered. Two problems below (§3-N1, §2-M6). |
| **L1** | long descriptions silently truncated | **NOT-RESOLVED (deferred)** | Unchanged: the detail pane is still one **2002-char** fragment (`wrap_lines` absent from the `Window`), so a long description is clipped with no wrap/scroll/ellipsis. |
| **L2** | `choose_tools` lacks the non-tty guard | **PARTIAL (improved)** | No `isatty` helper was factored out, but with piped stdin/stdout the function now writes **0 box-drawing lines** and raises `BrowserCancelled: No tool selected… Available: …` (only prompt-toolkit's `Warning: Input is not a terminal (fd=0)` on stderr). The ugly path is gone; the guard still cannot be reused. |
| **L3** | `--jobs` unvalidated; worker exceptions bypass the install net | **PARTIAL** | `--parallel --jobs 0`: still `ValueError: max_workers must be greater than 0`, but now **contained**: `❌ Error installing claude-code: max_workers must be greater than 0` + `❌ 1 tool(s) failed to install`, exit 1, no traceback. No `jobs >= 1` validation and no upper bound. |
| **L4** | `install_plugin` silent no-op | **RESOLVED** | `install_plugin("claude-code")` → `RuntimeError: claude-code: not a plugin tool`; unknown tool → `RuntimeError: Unknown tool: nope`. |
| **L5** | no coverage of interactive failure paths | **PARTIAL** | New `tests/integration/test_cli_tui_headless.py` (10 tests) pins the `Keys.Any` seam, arrow/PageDown names, Esc/Ctrl-C cancellation and the C1 degradation, so M5 and C1 can no longer regress silently. Still **no test** for the min-size guard's refusal, the dialog bindings, SIGINT, per-tool containment, or `_atomic_write` — i.e. the remaining gaps are exactly the changed-but-unpinned surfaces. |
| **F-05** | plugin subprocess had no `FileNotFoundError`/timeout handling | **RESOLVED** | `timeout=300`; `FileNotFoundError` → `RuntimeError("Hermes plugin build needs `uv` on PATH")` (verified by patching `subprocess.run`); `TimeoutExpired` → `RuntimeError(… timed out after 300s …)`. |

---

## 2. Failure-mode table (current state)

| # | Dependency / surface | Failure type | Current impact | Status |
|---|---|---|---|---|
| 1 | `apply_key` inside the `Keys.Any` handler (`browser_app.py:214-227`) | any `Exception` | Clean cancel: exit 1, terminal restored, flag named | **Contained** |
| 2 | Key *identity* resolution (`event.key_sequence[0]`, `press.key.value`) two lines **above** the try | malformed `KeyPress` | Would reach prompt-toolkit's handler → the old freeze returns | **Degraded** (theoretical) |
| 3 | Sibling tools in one batch (`main.py:604`) | any `Exception` | Batch continues, per-tool error + `N tool(s) failed`, exit 1 | **Contained** |
| 4 | Artifact file writes (`installer.py:130-142`) | `EACCES`, `ENOSPC`, interrupt | Target appears complete or not at all; `*.tmp` orphan left behind | **Contained** |
| 5 | Two concurrent installs, same artifact | fixed `x.md.tmp` name | Two writers share one temp path; last `os.replace` wins with possibly foreign content | **Degraded** |
| 6 | Tool-picker dialog (`browser_app.py:100-104`) | user presses `Esc` or `Ctrl-C` | **Frozen**: neither key is bound alone; only the undocumented `Esc`→`Ctrl-C` chord exits; hint claims "Esc cancels" | **Cascading** |
| 7 | Tool-picker dialog | `SIGINT` (systemd/IDE/wrapper) | Ignored for the app's lifetime | **Cascading** |
| 8 | `choose_tools` value list (`browser_app.py:83-90`) | catalog with no destination for the scope | bare `AssertionError` from `_DialogList.__init__` (`assert len(values) > 0`) | **Degraded** |
| 9 | Terminal size (`browser_app.py:199-206`) | real terminal smaller than 60x20 | Loud refusal, exit 1, nothing drawn | **Contained** |
| 10 | Terminal size | `COLUMNS`/`LINES` exported small in a large terminal | **False refusal** in an adequate 80x24 terminal | **Degraded** |
| 11 | Terminal size | 60x20 exactly (the documented minimum) | Frame is 27 lines / 165 cols on the real roster → help + status clipped at the advertised floor | **Degraded** |
| 12 | `SIGINT` in the browser (`browser_app.py:242`) | `handle_sigint=False` | exit 1 in ~3 s, terminal restored | **Contained** |
| 13 | Terminal EOF while browsing | input stream closes | `BrowserCancelled` + flag hint, exit 1 | **Contained** |
| 14 | OS signal surface | `SIGTERM` | Conventional termination (signal 15) | **Contained** |
| 15 | Non-tty stdin/stdout | pipe, CI, `> log` | Loud, exit 1, names `--tool` / `--no-interactive` | **Contained** |
| 16 | Roster text | 5 KB names, CJK, emoji, zero-width, bidi, raw ANSI | Renders; `_display_safe` now escapes `Cc/Cf/Zl/Zp` so RTL is no longer exploitable | **Contained** |
| 17 | Filter vs. keys | typo / stray space | Enter with no selection now exits **1** | **Contained** |
| 18 | `--jobs` (`main.py:275`) | `0`, or a huge number | ValueError surfaced per tool, exit 1 | **Degraded** (loud but crude) |
| 19 | Plugin build (`installer.py:157-176`) | missing `uv`, hang, non-zero exit | `RuntimeError` with a nameable cause; 300 s ceiling | **Contained** |

---

## 3. New (or newly exposed) failure modes

**N1 — HIGH visibility, cheap: the size guard measures the environment, not the terminal.**
`shutil.get_terminal_size()` prefers `COLUMNS`/`LINES` from the environment. Verified: an **80x24**
pty with `COLUMNS=40 LINES=15` exported → `The browser needs at least 60x20, this terminal is
40x15` → exit 1, browser refused. tmux panes, nested shells, IDE terminals and CI wrappers export
those variables routinely, so the guard that was meant to remove a dead end can now *create* one.
Fix: `size = os.get_terminal_size(sys.stdout.fileno())` (fall back to `shutil` only if that raises).

**N2 — MEDIUM: the dialog now promises a key that does nothing.**
The rebuilt hint reads `Space toggles, Tab moves, Enter confirms, Esc cancels.` but `Esc` alone is
swallowed (verified frozen at 16 s; also `Ctrl-C` alone, and `Esc Esc`). Root cause is one line:

```python
@bindings.add("escape", "c-c")   # prompt-toolkit: a TWO-KEY SEQUENCE
```

`KeyBindings.add(*keys)` builds a sequence, so the app waits for `Esc` followed by `Ctrl-C`. Only
that chord cancels. Verified fix (both keys work, Ok still works):

```python
@bindings.add("escape")
@bindings.add("c-c")
def _cancel(event) -> None:
    event.app.exit(exception=KeyboardInterrupt())
```

(`Application` merges app bindings *after* `load_basic_bindings`, so an app-level `c-c` does
override the library's no-op — confirmed empirically, not by reading.)

**N3 — MEDIUM: the dialog ignores SIGINT.** `run_browser` got `handle_sigint=False`; `choose_tools`
did not. With the dialog open, SIGINT at t=4 s left the process alive past the 16 s timeout. Apply
the same `application.run(handle_sigint=False)` (the surrounding `except KeyboardInterrupt` already
converts it to `BrowserCancelled`).

**N4 — LOW: empty picker list is a bare assertion.** `choose_tools(tools, scope=…)` builds
`CheckboxList(values=[])` when no catalog tool declares a destination for that scope; `_DialogList`
asserts `len(values) > 0` → `AssertionError` (verified). Unreachable through the shipped catalog and
the CLI's pre-validation, but a custom/partial `tools.json` turns it into a traceback. Two lines:
`if not values: raise BrowserCancelled("No tool has a destination for this scope …")`.

**N5 — LOW: `.tmp` orphans and a shared temp name.** On a failed write the injected `ENOSPC` left
`x.md.tmp` behind (the target stayed absent, which is the property that matters). The temp name is
derived only from the target, so two concurrent installs of the same artifact share it. Cheap
hardening: `tempfile.mkstemp(dir=path.parent)` + `os.replace`, and `unlink(missing_ok=True)` in a
`finally`. Cross-destination installs are also per-file atomic, not per-tool transactional: if dest
2 of 3 fails, dests 1-2 remain — acceptable, but worth stating in the runbook.

**N6 — NIT: the C1 guard does not cover key *resolution*.** In `_handle`, `press = event.key_sequence[0]`
and `press.key.value if isinstance(press.key, Keys) else press.key` run outside the `try`. A future
prompt-toolkit change to `key_sequence` would re-open the original freeze. Move both lines inside
the `try` (zero risk, one line of indentation).

**N7 — NIT: exit codes.** A `SIGINT`-driven cancel exits **1** (like a user cancel) rather than the
conventional **130**, and a mutually-swapped `--scope` cancel is indistinguishable from "nothing
matched" by exit code alone. Scripts can still tell `0` from `1`, which is the contract that was
missing before, so this stays a nit.

**N8 — DOC: the README key table is now stale in the other direction.** `README.md:132` still says
"arrow keys are not bound yet" while `Up/Down/PageUp/PageDown` now work. Documentation, not
resilience, but it is the page a stuck user reads.

---

## 4. What this pass actually improved (do not regress)

* **One bad keystroke is no longer fatal.** C1 was the only *unrecoverable* failure (SIGKILL +
  broken terminal); it is now a clean exit 1 with a flag hint, and a headless test pins it.
* **The install batch is no longer shared-fate.** Per-tool `except Exception` + aggregate report
  converted "batch aborted, unknown partial state, stack trace" into "one tool reported, the rest
  installed, exit 1".
* **No torn artifacts.** `os.replace` makes each artifact appear complete or not at all — the
  precondition for ever adding retries safely.
* **The interactive layer is interruptible again** (browser only) and **fails fast** on a bad flag
  before drawing a frame.
* **The key map is now a testable seam** (`key_name`), which is why M5 could be fixed at all.

---

## 5. Top three resilience investments, ranked by risk reduction per effort

1. **Close the dialog's last dead end (~4 lines, N2 + N3 + N4).** Split the cancel binding into two
   single-key handlers (verified working), run that `Application` with `handle_sigint=False`, and
   guard `values == []`. This removes the only remaining *reachable* freeze in the product: the
   modal a user lands in when no tool is detected, where `Esc` — the key the browser just taught
   them — does nothing and the hint says it does.
2. **Take the size guard off the environment (1 line, N1) and set the floor to the layout's real
   need.** Measure the tty fd, not `COLUMNS`; the real roster frame is 27 lines × 165 cols, so a
   60x20 floor still hides the status and help lines. As shipped, the guard can refuse an adequate
   terminal *and* accept an inadequate one — the worst of both.
3. **Pin the remaining fixes with headless tests (5 short tests, L5).** Min-size refusal (mock
   `os.get_terminal_size`), dialog cancel-by-single-key, `_install_agents` containment returning
   `['t2']`, `_atomic_write` leaving no target after a failing write, and the dialog's empty-catalog
   `BrowserCancelled`. All five run without a pty, so CI can hold the line the way it now does for
   C1 and M5.

---

## Appendix — the exact reproductions used

```bash
# full suite
uv run pytest -q                                   # 300 passed

# everything below drives the real CLI under a pty (see reverify_*.py)
uv run python project-tasks/tui-review/reverify_run.py    # C1 M1 M2 M4 M5 M6 L2 H1
uv run python project-tasks/tui-review/reverify_run3.py   # arrow-key installs, EOF, H3 dialog
uv run python project-tasks/tui-review/reverify_run4.py   # H2 atomic write, L3, L4, F-05, L1
uv run python project-tasks/tui-review/reverify_run5.py   # H3 root cause + verified fix, dialog SIGINT

# N1: false size refusal in an adequate terminal
COLUMNS=40 LINES=15 <80x24 pty> .venv/bin/agency-agents tui --tool claude-code
#   -> exit 1, "this terminal is 40x15"

# N2: dialog still frozen by Esc / Ctrl-C (only Esc,Ctrl-C exits)
HOME=$(mktemp -d) .venv/bin/agency-agents tui   # tab, enter, then send 0x1b -> frozen

# H3 fix proof (from reverify_run5.py): separate handlers -> exit 1 on Esc alone and on Ctrl-C alone
```
