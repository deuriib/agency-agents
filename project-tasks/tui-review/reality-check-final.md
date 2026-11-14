# Reality Check — Final Production-Readiness Gate: Interactive TUI

**Reviewer**: TestingRealityChecker (final integration gate)
**Subject**: `tui` command + bare `install` browser, `agency-agents`
**Tree**: `253cae4` + uncommitted fix pass (8 files: 4 source, 4 test; 1 test file untracked)
**Date**: 2026-11-13
**Verdict**: **PASS** — conditional on one mechanical release step (commit the untracked test file, §9 R1)

Every claim below was re-verified against the working tree by running it. I did not read
the fix-pass summary and take it as evidence; where the summary and the tree disagreed, the
tree wins and the disagreement is recorded.

---

## 1. Mandatory gates (all run by me, raw results)

| # | Command | Result | Status |
|---|---------|--------|--------|
| 1 | `uv run pytest -q` | `Pytest: 302 passed in 6.66s` (re-run: `302 passed in 6.33s`) | PASS |
| 2 | `uv run pytest -q --cov=agency_agents --cov-branch --cov-fail-under=80` | exit 0; `coverage report` → `TOTAL 1598 stmts, 94 miss, 574 branch, 48 partial, 93.0%` | PASS |
| 3a | `uv run ruff check .` | `Ruff: No issues found` (exit 0) | PASS |
| 3b | `bash scripts/ci/mypy_ratchet.sh` | `mypy: current=36 baseline=36` → `Type-check ratchet passed.` (current <= baseline) | PASS |
| 4 | `uv build` | `Successfully built dist/py_agency_agents-1.14.0.tar.gz` and `…-py3-none-any.whl` | PASS |
| 5 | `uv run pytest src/agency_agents/tests/integration/test_cli_tui_headless.py -q` | `12 passed in 2.34s`, stable over 5 consecutive runs (2.20–2.31s) | PASS |

Note on gate 2 output: the repo's conftest prints only the one-line pytest summary, so the
coverage table is not shown inline. I verified the gate by reading `.coverage` with
`uv run coverage report --show-missing` **and** by the exit code of the `--cov-fail-under=80`
run (0). Both agree.

Build integrity: the artifacts are not stale — the wheel carries the fixes
(`browser_app.py` matches for `BracketedPaste|get_size|handle_sigint=False` = 3), and the
sdist carries them too.

CI parity check: `.github/workflows/ci.yml` runs `ruff check .`, `scripts/ci/mypy_ratchet.sh`,
and `pytest -q --cov=agency_agents --cov-branch --cov-report=term-missing --cov-report=xml
--cov-fail-under=80`. The gates above are the same gates, so a green local run means a green
CI run *for the files that are committed* (see R1).

---

## 2. Gate 5 — does the headless test drive the real prompt-toolkit `Application`?

**Yes. Not a mock.** `tests/integration/test_cli_tui_headless.py` builds a real pipe input and
a real application session:

```python
with create_pipe_input() as pipe, create_app_session(input=pipe, output=DummyOutput()):
    ...  pipe.send_text(keys); return run_browser(model, title="headless")
```

`run_browser` is the production function; no `Application` is patched anywhere in the file.
Raw bytes go through prompt-toolkit's own vt100 parser (`\x1b[B` for Down, `\x1b[6~` for
PageDown, `\x03` for Ctrl-C, `\x1b[200~…\x1b[201~` for bracketed paste), so the `Keys.Any`
dispatch and `key_name` translation are exercised for real. The only patches are
`sys.stdin.isatty`/`sys.stdout.isatty` (to pass the tty guard) and, in one test, `apply_key`
(to force a handler exception).

The three required assertions are present and are behavioural, not "a key was pressed":

| Required assertion | Test | Mechanism |
|---|---|---|
| Arrow keys move the cursor | `test_down_arrow_then_tab_selects_the_second_row` → `drive("\x1b[B\t\r") == ["growth-hacker"]` | cursor actually moved before Tab selected, so the *wrong* row would be selected if dispatch regressed. `test_up_arrow_is_a_no_op_at_the_top` and `test_page_down_moves_a_full_page` (`["a-010"]`) pin clamping and PAGE_SIZE. |
| Esc / Ctrl-C cancel **with a selection** | `test_escape_with_a_selection_cancels` (`"\t\x1b"`), `test_ctrl_c_with_a_selection_cancels` (`"\t\x03"`), both `pytest.raises(BrowserCancelled)` | the selection is made *first*, which is exactly the SEC-1 defect shape |
| Exception in key handler cancels | `test_an_exception_in_the_key_handler_cancels` (`apply_key` → `RuntimeError`, expects `BrowserCancelled`) | proves no freeze in the alternate screen |

Two weaknesses in the file (recorded, non-blocking):

- **Dead patch**: it patches `shutil.get_terminal_size` and `os.terminal_size((80, 24))`, but
  production reads `application.output.get_size()` and `DummyOutput().get_size()` returns
  `Size(rows=40, columns=80)`. The patch has no effect, so the test silently does **not**
  control terminal size and does **not** cover the adaptive-height/min-size logic (see F1).
- The docstring over-claims slightly: nothing in this file pins "enter is the only key that
  accepts" beyond the accept-path tests; the abort-path coverage is what makes that true.

---

## 3. Gate 6 — independent verification of the two security claims

### (a) `run_browser` raises `BrowserCancelled` on ANY abort — CONFIRMED

`grep -rn "ABORT and" src/` → **no match**. The old `if ABORT and not selected` guard is gone
everywhere in `src/`. The current code path is unconditional:

```python
if result in (ACCEPT, ABORT):
    outcome["result"] = result
    event.app.exit()
...
if outcome.get("result") != ACCEPT:
    raise BrowserCancelled("No agents installed — selection cancelled.")
return model.selection()
```

Accept is the only value that returns a selection; ABORT, an EOF exit, and an exit with no
result all land on the `!= ACCEPT` branch. The surrounding exits are also failures: no-tty
guard, size guard, `run()`-raised `(EOFError, KeyboardInterrupt, OSError, RuntimeError)`, and
`failure["error"]` set by the key handler. `application.run(handle_sigint=False, …)` means
Ctrl-C arrives as a key press (`c-c` → `_ABORT`) rather than being swallowed by SIGINT.

Live confirmation on a real pty (not the unit harness), 6 probes + 4 CLI cases:
`tab,ESC`, `tab,Ctrl-C`, `c-a,ESC`, `tab,c-q` all returned
`CANCELLED No agents installed — selection cancelled.` and the CLI exited 1 with no plan.

### (b) `install --agent '[/x]' --no-interactive --dry-run` exits 1, one line, no traceback — CONFIRMED

```
$ uv run agency-agents install --agent '[/x]' --no-interactive --dry-run
❌ Unknown agent '[/x]'. Use --list agents to see the available roster.
EXIT=1        stdout lines=1   stderr bytes=0
```

I extended the probe beyond the single claim, since one quiet path proves little:

| Input | Result |
|---|---|
| `--tool '[/bold]'` | exit 1, `❌ Unknown tool(s): [/bold]`, stderr 0 bytes |
| `--scope '[/x]'` | exit 1, `❌ Invalid scope '[/x]'. Use 'user' or 'project'.`, stderr 0 |
| `--list '[/bold]'` | exit 1, `Unknown --list value '[/bold]'. …`, stderr 0 |
| `--runbook '[/x]'` | exit 1, `❌ Unknown runbook '[/x]'. …`, stderr 0 |
| `--agent $'a\x1b[31mred\x07b'` | exit 1; `od -c` shows `a [ 3 1 m r e d b` — the ESC and BEL are **stripped**, brackets printed literally |
| `echo "" \| agency-agents install` (no tty) | exit 1, one line, stderr 0 bytes |
| `tui --tool '[/x]'` / `tui --scope '[/x]'` in a pty | exit 1 **before the first frame** ("Browse agents" never rendered) |

`_safe()` = strip C0/C1/DEL (keeping `\n`/`\t`) + `rich.markup.escape`; every user-facing
interpolation I found now goes through it (lines 179–195, 239, 259, 326–331, 368, 374, 470–500).

---

## 4. Independent pty evidence (my own harness, not the prior reviewer's)

`project-tasks/tui-review/final_gate_pty.py` (new, mine) drives the **real CLI**
(`.venv/bin/python -m agency_agents tui --dry-run`, and bare `install`) on a real
`/dev/ptmx` slave with a real `TIOCSWINSZ`, plus a child probe that prints the exact selection
returned by the real `run_browser`. Log: `project-tasks/tui-review/final-gate-pty.log`.

```
SUMMARY 19/20 passed   (RC=1 — the one failure is H4, a cosmetic 80-column truncation, F3)

CASE A   accept-2nd-row                  exit=0 PASS   1 agents, dry run complete
CASE A2  enter-nothing-selected          exit=1 PASS   "Nothing selected"
CASE A3  invalid-tool-before-browse      exit=1 PASS   browse never rendered
CASE A4  invalid-scope-before-browse     exit=1 PASS   browse never rendered
CASE B   esc-with-selection              exit=1 PASS   no plan, no install
CASE C   ctrl-c-with-selection           exit=1 PASS   no plan, no install
CASE D   filter-then-accept              exit=0 PASS   "growth" narrowed, then accepted
CASE E   24-row-help-line-visible        exit=1 PASS   status + help lines both rendered
CASE F   19-row-refused                  exit=1 PASS   "needs at least 60x20", no traceback
CASE H2  60x20-boundary-accepts          exit=0 PASS   1 agents, dry run complete
CASE H3  59-cols-refused                 exit=1 PASS   refused before the first frame
CASE G   paste-cr-does-not-install       exit=1 PASS   bracketed-paste CR never accepts
CASE H   bare-install-esc                exit=1 PASS   the `install` browser cancels too
PROBE P1 down-tab-enter        RESULT ['growth-hacker']
PROBE P2 down-down-tab-enter   RESULT ['deal-strategist']
PROBE P3 pagedown-tab-enter    RESULT ['deal-strategist']
PROBE P4 c-a-esc               CANCELLED
PROBE P5 tab-enter             RESULT ['backend-architect']
PROBE P6 c-q-after-tab         CANCELLED
```

Layout arithmetic checked, not assumed: fixed overhead is exactly 12 lines
(3 header/filter/separator + 1 separator + 5 detail + 1 separator + status + help), and
`max(3, rows-12)` fits 24-row and 20-row terminals **exactly**. Live: at 100x24 the help line
and status line are both in the rendered byte stream; the old fixed 15-row window (12+15=27 > 24)
would have clipped them, so the clipping defect is genuinely fixed.

Model-layer checks I ran directly (not via the repo's tests):

- `_display_safe`: `\u202e…\u202c` → `\\u202e…\\u202c`, `\u200b` → `\\u200b`, `\x1b[2J`,
  `\x1b]0;t\x07`, `\r\n` all neutralised; the rendered screen contains **zero** raw C0 bytes
  and no ESC/OSC sequence. ANSI/bidi injection is closed.
- `key_name`: `c-i`+`\t`→`tab`, `c-m`+`\r`/`\n`→`enter`, `c-h`+`\x7f`→`backspace` (data wins over
  the parsed identity, as documented), `up/down/pageup/pagedown/c-a/escape/printable` pass through.
- `current()` clamps `cursor=99` → last row (and negative → first); `set_query()` resets the
  cursor **and** is a no-op for an identical query (`cursor=7` survived `set_query("")`).
- Installer: real install into a temp `$HOME` → exit 0, artifact complete, **0** `.tmp` files
  left behind; `_atomic_write` = `mkstemp` beside target + `os.replace` + unlink-on-failure.
- Plugin path: `subprocess.run(..., timeout=300)` with `TimeoutExpired` / `FileNotFoundError` /
  `CalledProcessError` each converted to `RuntimeError`.

---

## 5. Claim-by-claim result

| Claim | Verdict | Evidence |
|---|---|---|
| `key_name` + `_display_safe` + `set_query` guard + `current()` clamp (browser.py) | VERIFIED | §4 model checks; 100% line/branch coverage on `browser.py` |
| Key dispatch via `event.key_sequence[0].key.value` + `key_name` | VERIFIED | §2 headless tests (raw escape sequences), §4 probes |
| Abort always cancels | VERIFIED | §3a, no `ABORT and` guard left, pty cases B/C/P4/P6 |
| Key-handler exception → cancel, never hang | VERIFIED | headless `test_an_exception_in_the_key_handler_cancels` |
| Bracket paste dropped | VERIFIED — but the whole payload is dropped, not just CR (F-14, deferred) | pty case G: paste+CR does not install |
| Adaptive list height from `output.get_size()` | VERIFIED live; **untested in the repo suite** (F1) | §4 exact-fit arithmetic; cases E/H2/H3/F |
| Dialog esc / c-c cancel | VERIFIED | headless `test_choose_tools_escape_cancels`, `…_ctrl_c_cancels` |
| `_safe()` markup/control escaping | VERIFIED | §3b table incl. `od -c` byte dump |
| Validate `--tool`/`--scope` before browse | VERIFIED | pty A3/A4 — "Browse agents" never rendered |
| Skip-with-warning for detected scope-unsupported tools | VERIFIED (both entry points) | `install --no-interactive --scope user` → `⚠ Skipping tools with no user destination: cursor, aider, windsurf`; TUI with `HOME={.claude,.cursor}` → `⚠ Skipping … cursor` then claude-code plan, exit 0 |
| No-op exits 1 | VERIFIED **for the TUI path only** | pty A2, and `HOME={.cursor}` → `No tool applicable to this scope — nothing installed.` exit 1. Non-interactive `install` still exits 0 on no-op — pre-existing, unchanged by this pass (F4) |
| Per-tool `except (RuntimeError, UnknownFormatError, OSError)` | VERIFIED by read; `OSError` added, message now `_safe()`d | diff of `_install_agents` |
| `_atomic_write` (mkstemp + `os.replace`) | VERIFIED | §4; live install left no temp files |
| Plugin `timeout=300` + catches | VERIFIED by read | `installer.py:169–181` |

---

## 6. Findings (severity ladder, foundation-conduct)

No **Critical**, no **High**, no **Medium product defect**. Everything below is Low/nit or
test hygiene.

**F1 — Medium (test hygiene): the adaptive-height / minimum-size fix has no automated test, and
the one test that looks like it covers it does not.** `test_cli_tui_headless.py` patches
`shutil.get_terminal_size`, but production reads `application.output.get_size()` and
`DummyOutput` reports `Size(rows=40, columns=80)`. Consequently `browser_app.py:244`
(60x20 refusal) and `:253-254` (`run()` exception wrap) are uncovered by the suite — they are
the only coverage gaps in a module at 91.3%. Behaviour *is* verified (my pty cases E/F/H2/H3),
so this is a regression-protection gap, not a product defect. Fix: pass a sized output stub via
`create_app_session(output=…)` and assert both branches. Owner: whoever owns the TUI tests.

**F2 — Medium (release process): `src/agency_agents/tests/integration/test_cli_tui_headless.py`
is untracked (`??` in `git status`).** A `git commit -am` would ship the fixes without the
regression suite that justifies them, and CI would be green without ever running it. This is the
single condition attached to the PASS (R1).

**F3 — Low (cosmetic): the help line is wider than the terminal, so it is truncated
horizontally on any terminal below ~95 columns.** At 80x24 the rendered text ends
`…enter install  esc ca` — "cancel" is cut. Rows are truncated, not wrapped
(`wrap_lines` is off), so nothing is pushed off-screen and the status line stays visible; the
keys work regardless. Suggested fix: shorten/split the hint line, or drop `c-u reset` and
`c-x clear` into the status line at narrow widths.

**F4 — Low (pre-existing, out of the TUI scope): the non-interactive `install` still exits 0 on
a no-op.** `cli/main.py` lines ~403 and ~408 (`if not selected_tools:` / `if not all_agents:`)
`return` instead of `raise typer.Exit(code=1)`, unlike the fixed TUI path. Unchanged by this
pass (not in the diff) and hard to reach (every division has agents; every scope has tools), so
it is a scripting footgun rather than a defect. Owner: `install` command.

**F5 — Low: `_atomic_write` changes installed file mode from 0644 to 0600.** `mkstemp` creates
`0600`; verified: `-rw------- .claude/agents/backend-architect.md`. Fine (arguably better) for
`--scope user`; for `--scope project` in a group-shared checkout it narrows readability. If
that matters, `os.chmod(tmp, 0o644)` before `os.replace` restores prior behaviour.

**F6 — Low: two `BrowserCancelled` prints are not `_safe()`d** (`cli/main.py:501, 518`).
`rich` raises `MarkupError` on a mismatched closing tag (`Console().print("[bold yellow]boom [/x][/bold yellow]")`
→ `MarkupError`), and the internal-error message embeds `failure['error']`. Reachability is
low (needs an internal exception whose text contains `[/…]`, and catalog tool kebabs are
repo-controlled and linted), but the path exists on the error branch that was fixed to fail
cleanly. Fix is one word: `_safe(e)`.

**F7 — Nit: `test_set_query_is_a_no_op_when_unchanged` is vacuous** — it sets `cursor=0` and
asserts `cursor==0` after `set_query("")`, which passes with or without the guard. I proved the
guard separately (`cursor=7` survived). Strengthen by starting from a non-zero cursor.

**F8 — Nit: `browser.py` was `ruff format --check` clean at HEAD and is now dirty**; the other
touched files were already dirty (127 files repo-wide). CI does not gate on `ruff format`, so
this is drift, not a gate failure — but the fix pass introduced it in a previously clean file.

---

## 7. Known deferred items — do they block production readiness?

| Deferred | Assessment |
|---|---|
| **F-14** paste content dropped rather than filtered | **Acceptable.** Verified: a pasted CR/Tab cannot accept or toggle (pty case G). The failure mode is "my paste did nothing", never "it installed something I did not choose". Costs usability, not safety. |
| **F-15** multi-codepoint graphemes dropped (emoji, combining marks) | **Acceptable.** Dropping a character can only *narrow* what the user typed → the filter under-matches and the user sees rows, never a wrong action. No data loss. |
| **60x20 minimum: <20 rows refused instead of rendered** | **Acceptable.** The refusal is clean, actionable and non-zero: `The browser needs at least 60x20, this terminal is 100x19. Resize it, or skip the browser: …` exit 1, verified at both boundaries (60x20 accepted, 59 cols refused) and no traceback. The documented flag fallback exists. Note that terminals like `tmux` split panes frequently land under 20 rows — the message tells the user exactly what to do, which is an acceptable outcome for a TUI. |
| **SEC-6** `$HOME` tool-presence disclosure | **Acceptable (informational).** It reports which directories exist in the invoking user's own home to the invoking user. No privilege boundary is crossed, nothing is written. |

None of these blocks the release; all four deserve an issue with an owner so they do not
become permanent.

---

## 8. What the fix pass got right, and what the evidence actually shows

The security core is genuinely closed and I could not break it: abort is unconditional, accept
is the only path to a selection, injected control/bidi bytes never reach the terminal, and every
CLI selector that used to raise `MarkupError` now prints one literal line and exits 1. The
reliability fixes are real and match their claims — atomic writes, a bounded plugin build, a
key-handler exception that degrades to a clean cancel, and a layout that fits a 24-row terminal
with exact arithmetic rather than a guess.

Where the summary over-reached: "no-op exits 1" is true of the TUI path it was written for, not
of non-interactive `install` (F4); and the adaptive-height fix, the one claim about *terminal
geometry*, is the only claim with no automated test behind it (F1). Both are documented above
with the evidence that contradicts the shorthand.

---

## 9. Release conditions

- **R1 (must, mechanical):** `git add src/agency_agents/tests/integration/test_cli_tui_headless.py`
  before commit/merge. Without it, CI never runs the suite that proves the abort fix.
- **R2 (should, next sprint):** close F1 (size-stub test for `browser_app.py:242-258`) and F6
  (`_safe(e)` at `cli/main.py:501, 518`).
- **R3 (backlog):** F3 help-line width, F4 non-interactive no-op exit code, F5 file mode,
  F7 vacuous test, F8 format drift.
- **Residual risk accepted:** F-14/F-15 (silent drops), 60x20 refusal, SEC-6 disclosure — see §7.
  Owner: TUI maintainer; expiry: revisit if the TUI gains a scroll pane or mouse support.

---

## 10. Evidence artifacts

| Artifact | What it proves |
|---|---|
| `project-tasks/tui-review/final_gate_pty.log` | the 20-case pty run, 19 pass + F3 failure, with git rev and timestamp |
| `project-tasks/tui-review/final_gate_pty.py` | the harness that produced it (real pty, real CLI, no mocks) |
| `project-tasks/tui-review/_sel_probe.py` | child probe printing the exact slugs `run_browser` returns |
| `git diff` (4 source files) | `_safe`, `key_name`, `_atomic_write`, `timeout=300`, `OSError`, removed `ABORT and` guard, `return`→`Exit(1)` |
| `uv run coverage report --show-missing` | 93.0% total; `browser.py` 100%; `browser_app.py` 91.3% (gaps = F1) |

**Verdict: PASS**, conditional on R1. Re-assessment is not required for the code; it is
required only if F1's uncovered branches are changed again.
