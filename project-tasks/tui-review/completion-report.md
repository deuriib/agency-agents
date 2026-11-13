# AgentsOrchestrator Completion Report — TUI Hardening Loop

**Run**: tui-full-review-board · **Mode**: Full (Sprint loop) · **Final Status**: COMPLETED (PASS)
**Divisions involved**: engineering, testing

## Summary

Drove a build → test → review → fix → re-review → Reality-Check loop over the interactive
agent-browser TUI (`agency-agents tui` + bare `install`). The Full Review Board (Security,
Reliability, Refuter, Resilience reviewers) surfaced a set of critical/high defects; each was
fixed with evidence and re-verified. Final gate: **Reality Checker PASS** (conditional on the
single mechanical step of committing the untracked regression-test file).

## Pipeline Results

| Gate | Result | Evidence |
|------|--------|----------|
| Unit + integration + headless | **302 passed** | `uv run pytest -q` |
| Coverage floor (CI parity) | **93.0%**, `--cov-fail-under=80` exit 0 | `--cov=agency_agents --cov-branch` |
| Lint | **clean** | `ruff check .` |
| Type ratchet | **current=36 baseline=36** (no growth) | `scripts/ci/mypy_ratchet.sh` |
| Build | wheel + sdist | `uv build` |
| Agent catalog lint | **clean** | `python -m agency_agents lint` |
| Headless browser loop | **12 passed** (drives real prompt-toolkit `Application`) | `test_cli_tui_headless.py` |
| Independent pty smoke | **19/20** (the 1 miss is the cosmetic F3, now fixed) | Reality Checker harness |

## Fixes delivered (root cause → fix)

**Critical / High (was "Unsafe to Ship"):**
- **Arrow/Page keys were dead** — `Keys.Any` delivered arrows as raw `\x1b[A` sequences that the
  byte map dropped. Fix: dispatch on `event.key_sequence[0].key.value` + a new pure
  `browser.key_name(key, data)` (char map wins for tab/enter/backspace). Headless-tested.
- **Esc / Ctrl-C / Ctrl-Q *installed* when a selection existed** (SEC-1 fail-open). Fix: abort
  always cancels — `run_browser` now raises `BrowserCancelled` unless the outcome is exactly
  `ACCEPT`.
- **Key-handler exception froze the app in the alt screen** (C1). Fix: `apply_key` wrapped,
  failure recorded, `event.app.exit()`, then `BrowserCancelled`; `run(handle_sigint=False,
  set_exception_handler=False)` with `except (EOFError, KeyboardInterrupt, OSError, RuntimeError)`.
- **Detected project-only tool aborted the whole run after browsing** (F-04). Fix: skip-with-
  warning for detected tools; hard error only for an explicit `--tool`.
- **Plugin subprocess had no timeout** (F-05). Fix: `timeout=300` + TimeoutExpired /
  FileNotFoundError / CalledProcessError → RuntimeError.
- **One unexpected exception aborted the multi-tool batch** (H1). Fix: per-tool
  `except (RuntimeError, UnknownFormatError, OSError)`.

**Security (pen-test):**
- **Terminal escape injection**: confirmed NOT exploitable (prompt-toolkit neutralizes C0/C1;
  documented with byte-level evidence).
- **Markup/log injection via caller/catalog text** (SEC-2). Fix: `_safe()` strips C0/C1/DEL
  (keeps `\n`/`\t`) + `rich.markup.escape`, applied to selectors, tool names, scope, list values,
  runbook slugs/fields, and dry-run dest patterns.
- **Bidi/zero-width display spoofing** (SEC-3). Fix: `_display_safe()` in `build_rows`.
- **Bracketed-paste CR/LF acted as ENTER → install** (NEW-1 regression). Fix: drop
  `Keys.BracketedPaste` in the handler.

**Resilience / honesty:**
- **Non-atomic writes left torn files** (H2). Fix: `_atomic_write` = `mkstemp` beside target +
  `os.replace` + unlink-on-failure + `chmod 0644`.
- **Tool dialog had no escape hatch** (H3). Fix: rebuilt with `escape`/`c-c` cancel (separate
  bindings, not a chord) + honest hint text.
- **No-op exits were 0** (F-06/M1). Fix: TUI "nothing selected"/"no tool selected" exit 1.
- **"space to select" was a lie** (F-07). Fix: status line now "tab to select".
- **Validated after browse** (F-08/M4). Fix: `--tool`/`--scope` validated before the first frame.
- **Fixed 27-line layout clipped on 24-row terminals** (F-09/N-02). Fix: adaptive list height
  from `application.output.get_size()` (`max(3, rows-12)`) + 60x20 minimum-size refusal.

## Cross-Pipeline Integrity

N/A — single pipeline (no cross-pipeline handoffs).

## Quality Validation

- **Loops run**: 3 (initial review → fix → re-review → Reality Check).
- **Reviewers**: Security, Reliability, Refuter, Resilience (Full Review Board) + Reality Checker.
- **Evidence index**: `project-tasks/tui-review/*.md` (per-reviewer reports + re-verify + final gate).

## Human Approvals

None required — no production deploy, no legal/clinical/tax content, no credentialed access.

## Readiness

**Status**: READY (conditional on staging the untracked regression-test file).
**Quality confidence**: HIGH — critical defect class fixed, independently re-verified, 302 tests
+ 93% branch coverage + clean lint/type/build.

## Remaining (deferred, non-blocking — all Low/nit)

| # | Item | Owner |
|---|------|-------|
| R1 | **Stage/commit `tests/integration/test_cli_tui_headless.py`** (untracked; `-am` would drop it) | release |
| F1 | Add an automated test for the adaptive-height / 60x20 refusal (verified by pty, not in suite) | TUI tests |
| F4 | Non-interactive `install` still exits 0 on a no-op (pre-existing, out of TUI scope) | install cmd |
| F14/F15 | Paste content / multi-codepoint graphemes are dropped rather than pasted into the filter | TUI |

---
**Run Completed**: (see git history) · **Orchestrator**: AgentsOrchestrator
