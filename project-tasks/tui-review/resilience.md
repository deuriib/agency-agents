# TUI Resilience Review — graceful degradation under partial failure

**Scope:** `src/agency_agents/infrastructure/browser_app.py`, `src/agency_agents/infrastructure/browser.py`,
`src/agency_agents/cli/main.py` (`tui`, `install`, `_browse_and_install`, `_detected_tools`, `choose_tools`),
plus `src/agency_agents/infrastructure/installer.py` where the install loop it calls is defined.

**Environment:** repo `main` @ `253cae4` (v1.14.0), Python 3.13.18, prompt-toolkit 3.0.53, rich, typer.

**Method:** source read plus live experiments — the CLI driven inside a real
pseudo-terminal (`pty.fork` + `TIOCSWINSZ` + `SIGWINCH`), with scripted keystrokes,
mid-run resizes, `kill -INT`, pty hangup, pathological roster data (5 KB names,
CJK/emoji, zero-width, bidi overrides, raw ANSI escapes), and fault-injected
installers. Every "verified" claim below was reproduced, not inferred. Reproduction
recipes are in the appendix.

**Verdict:** the *guard* work is genuinely good — non-tty is loud and names the flag,
an empty roster is a clean error, and pathological text cannot crash the renderer.
The **degradation envelope in the interactive layer is the weak spot**: there is one
unrecoverable freeze (C1), the multi-tool install is shared-fate with non-atomic
writes into the user's tool config (H1, H2), and the tool-picker modal has no escape
hatch while misdescribing its own keys (H3). All three are reachable by an ordinary
user on an ordinary bad day.

---

## 1. Failure-mode table

| # | Dependency / surface | Failure type | Current impact | Status |
|---|---|---|---|---|
| 1 | prompt-toolkit key-handler dispatch (`browser_app.py:176-197`) | Any exception raised by `apply_key` | Traceback drawn inside the alt screen, "Press ENTER to continue…", app **never exits**; Enter does not recover; SIGKILL required; terminal left in alt screen | **Cascading** |
| 2 | Tool destination filesystem (`installer.py:102,122`) | `EACCES`, `ENOSPC`, `ENAMETOOLONG`, SIGINT mid-write | Traceback, batch aborted mid-way, **truncated agent files** left behind; recovery is manual | **Cascading** |
| 3 | Sibling tools in one install batch (`main.py:566-578`) | Any exception type other than `RuntimeError`/`UnknownFormatError` | Remaining tools never attempted; no aggregate "N failed" report; successes unreported | **Cascading** |
| 4 | `choose_tools` dialog (`browser_app.py:82-98`) | User presses Esc or Ctrl-C | **No exit** — modal keeps running; only Tab→Cancel works; on-screen text is wrong ("enter confirms") | **Cascading** |
| 5 | OS signal surface (`browser_app.py:190-197`) | `SIGINT` from parent/systemd/IDE | Ignored while the browser runs; process survives until SIGKILL | **Cascading** |
| 6 | Terminal (tty) | Hangup / pty close | SIGHUP terminates the process (exit `-1`); acceptable | **Contained** |
| 7 | Terminal size | 5×20, 3×10, 1×1 | No crash; frame drawn but list unusable, no "too small" message; dialog falls back to "Window too small" and stops responding | **Degraded** |
| 8 | Non-tty stdin **and/or** stdout | Pipe, CI, `> log` | Loud: exit 1, message names `--tool` / `--no-interactive` | **Contained** |
| 9 | Empty roster | No parseable agents | Clean red error, exit 1 | **Contained** |
| 10 | Roster text | 5 KB names, CJK, emoji, combining, zero-width, U+202E, raw `ESC[31m` | Renders, sanitized by prompt-toolkit (escape sequences neutralised), clipped at screen edge | **Contained** |
| 11 | Filter vs. keys (`browser.py:166,186`) | User types a space (advertised as "select") or a typo | 0 rows shown; Enter then exits **0** with "Nothing selected" | **Degraded** |
| 12 | `--jobs` flag (`main.py:259`, `converter.py:389`) | `--jobs 0` | `ValueError` traceback panel, exit 1 | **Degraded** (loud but crude) |
| 13 | `tools.json` `detect.dirs` | Empty array (`aider`, `kimi`) | Never auto-detected → dialog always shown; by design | **Contained** |

---

## 2. Findings

### C1 — CRITICAL: an exception in the `Keys.Any` handler freezes the app with no way out

**Where:** `src/agency_agents/infrastructure/browser_app.py:176-184` (handler body), `:197` (`application.run()`).

**Scenario:** `apply_key` raises anything — a model bug, a `MemoryError` after a huge
paste-driven query, a `RecursionError`, or a future row/description shape that
`browser.py` does not expect. The exception is raised inside prompt-toolkit's input
reader callback, so it never reaches `run_browser`; prompt-toolkit's event-loop
exception handler prints the traceback over the alt screen and awaits Enter
(`Application._handle_exception`, `set_exception_handler=True` by default).

**Verified:** with `apply_key` patched to raise on the second keystroke:

```
File ".../browser_app.py", line 179, in _handle
    result = apply_key(model, _NAMED_KEYS.get(key, key))
RuntimeError: boom from apply_key
Exception boom from apply_key
Press ENTER to continue...
```

The process was still alive after 10 s, and stayed alive after Enter and Esc were
sent — it had to be SIGKILLed. The captured stream never contains `ESC[?1049l`
(leave alt screen), so the user's shell is left in the alternate screen and needs
`reset`/`stty sane`. The user also loses the selection they built.

**Current:** unrecognised key-handler failure = unrecoverable hang, no message
naming a flag, requires killing the terminal.
**Desired:** a keystroke can never kill the app. Any handler failure must degrade to
"cancel with an explanation", restore the terminal, exit 1, and name the flag route —
the same contract as the non-tty guard at `:166-171`.

**Fix:**

```python
    failure: Dict[str, BaseException] = {}

    @bindings.add(Keys.Any)
    def _handle(event) -> None:
        key = event.data
        try:
            result = apply_key(model, _NAMED_KEYS.get(key, key))
        except Exception as exc:          # one bad keystroke must not kill the app
            failure["error"] = exc
            event.app.exit()
            return
        if result in (ACCEPT, ABORT):
            outcome["result"] = result
            event.app.exit()
            return
        event.app.invalidate()

    try:
        application.run()
    finally:
        pass  # prompt_toolkit already restored the terminal in its own finally

    if "error" in failure:
        raise BrowserCancelled(
            f"The browser hit an internal error ({failure['error']}). "
            "Nothing was installed. Use the flags instead: "
            "`agency-agents install --tool <kebab> --no-interactive`."
        ) from failure["error"]
```

Catch `Exception`, not `BaseException`, so a real Ctrl-C/SIGINT still propagates.
Treat anything that reaches the renderer the same way (see M3/L1): the rule is
"interactive surface fails soft and loud, never silently and never fatally".

---

### H1 — HIGH: one unexpected exception type aborts the whole multi-tool install batch

**Where:** `src/agency_agents/cli/main.py:566-578` (`_install_agents`, `except (RuntimeError, UnknownFormatError)`),
`main.py:400-407` and `main.py:521-529` (aggregate report), `installer.py:102,122,147-155`.

**Scenario:** `install --tool a,b,c` (or a browser install into two detected tools).
Tool `a` succeeds. Tool `b` raises something outside the two caught types:
`PermissionError`/`OSError` from `mkdir`/`write_text` (`installer.py:101-102,121-122`),
`FileNotFoundError` because `uv` is absent in `install_plugin` (`installer.py:147-155`,
`subprocess.run` only wraps `CalledProcessError`), a `KeyError`, or a
`ProcessPoolExecutor` worker exception re-raised by `future.result()`
(`converter.py:392`).

**Verified** (unit-level fault injection, then end-to-end with a read-only project dir):

```
❌ Error installing t1: boom runtime         <- RuntimeError is aggregated
   ESCAPED: builtins.PermissionError [Errno 13] Permission denied
```

and end-to-end: `install --tool claude-code --scope project` in a read-only cwd
prints a rich traceback panel (`PermissionError: [Errno 13] … '/tmp/…/.claude'`) and
exits 1.

**Current:** the loop dies mid-batch. No "N tool(s) failed" summary, no list of what
*did* install, remaining tools never attempted, and the user gets a Python stack dump
instead of "that directory is not writable".
**Desired:** per-tool containment — every tool in the batch is attempted, the summary
reports installed/failed explicitly, and the failure text names the path and the flag.

**Fix:**

```python
        except Exception as e:                      # per-tool bulkhead, not shared fate
            failures.append(f"{t_kebab}: {e}")
            console.print(f"[bold red]❌ Error installing {t_kebab}:[/bold red] {e}")
```

and in the callers, report both sides:

```python
    installed = [t for t in selected_tools if t not in failed_names]
    if installed:
        console.print(f"[green]✓ Installed into: {', '.join(installed)}[/green]")
```

Also wrap the plugin subprocess (`installer.py:147`) so a missing `uv` becomes
`RuntimeError("Hermes plugin build needs `uv` on PATH")`, and validate `--jobs`
(`main.py:259`) as `jobs >= 1` before the executor (`converter.py:389`) raises
`ValueError` from inside a rich status block (see L3).

---

### H2 — HIGH: writes are non-atomic and unpruned, so a failure leaves truncated files in the user's tool config

**Where:** `src/agency_agents/infrastructure/installer.py:102` (`target_base.write_text(content)`),
`:122` (`target.write_text(full_content)`), `:59-66` (`prune_output` is dead code — its body is `pass`),
`:195-197` (sequential writes, no rollback).

**Scenario:** the install phase runs with the terminal back in cooked mode, so Ctrl-C
is a real `SIGINT` → `KeyboardInterrupt` raised inside `write_text`. Nothing in
`_install_agents`, `_browse_and_install`, or `install` catches it. `Path.write_text`
truncates then writes, so an interrupt, `ENOSPC`, or an `ENAMETOOLONG` slug leaves a
**partial agent file** in `~/.claude/agents/…` (or a partial roster file for
`installKind: roster`, which concatenates *all* agents into one blob at `:122`).
A second failure mode is stale state: `prune_output` does nothing, so artifacts from a
previous install are never removed and a partially-applied batch can never be
distinguished from a complete one.

**Current:** silent corruption of the artifact itself; the next run does not repair
it; recovery is "notice it, delete it by hand".
**Desired:** every artifact appears atomically or not at all, and the tool reports the
set it wrote so a rerun is verifiable.

**Fix:** write beside the target and rename:

```python
    target = self.resolve_path(pattern, slug, scope, tool_kebab=tool_kebab)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(target.name + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, target)          # atomic on the same filesystem
```

plus accumulate `written: List[Path]` and print it (or `--dry-run`-style listing) on
failure, and either implement `prune_output` or delete it so the next reader is not
misled into believing cleanup happens.

---

### H3 — HIGH: the tool-picker modal has no escape hatch and misdescribes its own keys

**Where:** `src/agency_agents/infrastructure/browser_app.py:82-88` (dialog construction, `text="Space toggles, enter confirms."`).

**Scenario / verified** (real pty, `choose_tools` against the shipped `tools.json`):

| Input | Result |
|---|---|
| `Esc` | nothing happens — dialog keeps running (test timed out, killed) |
| `Ctrl-C` (`\x03`) | nothing happens — same hang |
| `Enter` on the list | toggles the highlighted entry (`[*] Claude Code`) — does **not** confirm, contrary to the dialog's own text |
| `Tab`, `Enter` | lands on **Cancel** → returns `None` |
| 4×15 terminal | renders "Window too small" and stops responding |

prompt-toolkit's `_create_app` for dialogs (`shortcuts/dialogs.py`) binds only
`tab`/`s-tab`; `load_basic_bindings()` maps `c-c`, `c-q`, `<sigint>` and friends to an
explicit no-op (`key_binding/bindings/basic.py:135-147`). So there is **no cancel key
at all** — only Tab-navigation to the Cancel button — and nothing on screen says so.
The browse step has already happened, so a user who lands here by accident (no tool
detected) and presses Esc/Ctrl-C as the previous screen taught them ("esc cancel")
is stuck until they kill the terminal.

**Current:** possible dead-end modal, contradictory on-screen contract, no
documented exit.
**Desired:** Esc and Ctrl-C cancel out of the dialog and produce the same loud,
flag-naming exit as the browser; the hint text matches the real bindings.

**Fix:** build the dialog with explicit bindings (or hunt for a focus target on
`escape`/`c-c` that exits with `KeyboardInterrupt`), then reuse the existing
`except (EOFError, KeyboardInterrupt)` branch at `:89-97`:

```python
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.layout import Layout
    from prompt_toolkit.shortcuts import CheckboxList, Dialog, Button
    from prompt_toolkit.application import Application

    kb = KeyBindings()

    @kb.add("escape", "c-c")
    def _cancel(event):                       # Esc must mean what the browser taught
        event.app.exit(exception=KeyboardInterrupt)

    app = Application(
        layout=Layout(dialog),
        key_bindings=kb,
        mouse_support=True,
        full_screen=True,
    )
```

and correct the text to `"Space toggles, Tab moves to Ok, Enter confirms, Esc cancels."`.
A cheaper interim fix: keep `checkboxlist_dialog` but reword the text to name Tab and
add a pre-dialog line telling the user Esc is not an exit — honest, but worse.

---

### M1 — MEDIUM: "nothing installed" is reported with exit code 0 on three paths

**Where:** `main.py:466-468` (browser confirmed with an empty selection),
`main.py:483-485` (dialog returned `[]`, i.e. Cancel → `browser_app.py:98`),
`main.py:384-390` (non-interactive install matched no tools/agents).

**Verified:**

* browser: type a space (advertised as "select"), press Enter →
  `Nothing selected — nothing installed.` — **exit 0**.
* dialog: Tab→Cancel→Enter → `No tool selected — nothing installed.` — **exit 0**
  (`RESULT []` from `choose_tools`).
* contrast: Esc with an empty selection → `BrowserCancelled` → **exit 1**
  (`browser_app.py:199-200`).

The tty guard at `browser_app.py:163-171` exists precisely to prevent "a silent no-op
inside a script that believes it installed something" — that exact outcome is still
reachable through two other doors. Note `tests/integration/test_cli_tui.py:236`
asserts `exit_code == 0`, so the current behaviour is enshrined, not accidental.

**Current:** a run that installed nothing can look successful to a script/CI.
**Desired:** no work done ⇒ non-zero exit; a deliberate Cancel must be
distinguishable from "nothing matched".
**Fix:** `raise typer.Exit(code=1)` at `main.py:468` and `:485`; make `choose_tools`
return `None` (or raise `BrowserCancelled`) when the user pressed Cancel so the caller
can print the flag hint instead of "no tool selected"; update the test to assert the
new code and message.

---

### M2 — MEDIUM: OS-level SIGINT is ignored while the browser is running

**Where:** `browser_app.py:190-197`; prompt-toolkit installs a SIGINT handler that
dispatches a `<sigint>` key event (`application/application.py:806-819`), and
`load_basic_bindings()` binds `<sigint>` to a no-op.

**Verified:** with the browser up, `kill -INT <pid>` → process still running 1.5 s
later; SIGKILL was required.

Note the *keystroke* Ctrl-C works (`\x03` → `_NAMED_KEYS` → `abort` → exit 1), which is
why this is easy to miss: typing Ctrl-C in the terminal works, but every
programmatic interrupt (timeout wrapper, IDE stop button, `systemctl stop`, a parent
script) is swallowed.

**Current:** un-interruptible interactive process; a wrapper has no polite way out.
**Desired:** SIGINT terminates with a conventional exit (130) after restoring the
terminal.
**Fix:** either bind it explicitly and abort:

```python
    @bindings.add(Keys.SIGINT)
    def _interrupt(event) -> None:
        outcome["result"] = ABORT
        event.app.exit(exception=KeyboardInterrupt)
```

or call `application.run(handle_sigint=False)` and catch `KeyboardInterrupt` in
`run_browser` (see M3) so Python's default disposition terminates the process.

---

### M3 — MEDIUM: `run_browser` lets `EOFError` / `KeyboardInterrupt` escape as a traceback

**Where:** `browser_app.py:197` (bare `application.run()`), vs. the dialog's
`except (EOFError, KeyboardInterrupt)` at `:89`.

**Scenario:** prompt-toolkit raises `EOFError` from `run()` when the input stream
closes (`application.py:695,727` set it on the future). A pty close currently
delivers SIGHUP first (verified: exit `-1`), which masks the bug, but any EOF without
a hangup (wrapper closing stdin, `exec 0<&-`, a terminal multiplexer detaching)
surfaces as a raw `EOFError` out of `tui`/`install` — no flag hint, traceback instead
of a message. `KeyboardInterrupt` from an unbound SIGINT path (see M2) is treated the
same way.

**Current:** traceback; the user is told nothing actionable.
**Desired:** both are normal "no terminal / user walked away" outcomes and should
reuse the `BrowserCancelled` wording that already exists.
**Fix:**

```python
    try:
        application.run()
    except (EOFError, KeyboardInterrupt) as exc:
        raise BrowserCancelled(
            "The browser was interrupted before anything was installed. "
            "Use the flags instead: `agency-agents install --tool <kebab> --no-interactive`."
        ) from exc
```

---

### M4 — MEDIUM: `--tool` / `--scope` are validated only after the interactive session

**Where:** `main.py:455-495` — the browser runs at `:460-464`; `unknown` tool,
invalid scope, and unsupported-scope checks are at `:487-505`. `tui` passes the raw
flags through at `main.py:413-436`.

**Verified:** `tui --tool bogus-tool` draws the browser first. Esc → only
"No agents selected"; the typo is never mentioned. Select an agent, Enter →
`❌ Unknown tool(s): bogus-tool` *after* the browse. Same for `--scope bogus`.

**Current:** a typo costs the user the whole selection session (worse over a slow
SSH/mosh link, where the frame-per-keystroke render is the expensive part).
**Desired:** fail fast — everything known before the first frame is validated before
the first frame.
**Fix:** hoist `:487-505` above `:460` (all three checks depend only on the flags and
the catalog), and keep the post-selection re-check for the dialog branch.

---

### M5 — MEDIUM: in-app help advertises keys that do nothing; the README documents different ones

**Where:** `browser_app.py:146-152` (footer: `up/down move … enter install esc cancel`),
`browser.py:166` (status: `type to filter, space to select, enter to install`),
`browser_app.py:33-51` (`_NAMED_KEYS`), `browser.py:186-190` (`_TOGGLE = {"tab"}`, `_UP`/`_DOWN`/`_PAGE_*`).

**Verified:** in a pty, arrow keys arrive as one `Keys.Any` event whose `data` is the
**raw escape sequence** (`'\x1b[B'`, `'\x1b[A'`, `'\x1b[6~'`), which is not in
`_NAMED_KEYS`, so `apply_key` receives a 3-character string, matches nothing, and
returns `CONTINUE`. End-to-end: Down, Down, Tab, Esc → `cursor=0`, selection `['s0']`
— the cursor never moved. PageUp/PageDown behave the same. `space` is a printable
character, so it lands in the filter: pressing it before Enter yields `0/299 shown`
and then an empty install.

The README (`README.md:131-139`) is honest and documents `Ctrl-P`/`Ctrl-N`,
`Ctrl-B`/`Ctrl-F`, and "arrow keys are not bound yet"; the **in-app** help contradicts
both the README and the model, which is what users actually read.

**Current:** the primary advertised navigation is a silent no-op; the advertised
select key destroys the list instead.
**Desired:** the keys the UI prints are the keys that work.
**Fix:** either bind the sequences (cheap and removes the whole class):

```python
_NAMED_KEYS.update({
    "\x1b[A": "up", "\x1b[B": "down",
    "\x1b[5~": "pageup", "\x1b[6~": "pagedown",
})
```

or dispatch on `event.key` (`event.key == Keys.Down → "down"`, fall back to
`event.data` for single printable characters) and correct the two help strings
(`browser.py:166` → "tab to select"). Add a pty-level test (see L5): the model is
tested (`tests/unit/test_browser.py`), the **key map is not**.

---

### M6 — MEDIUM: no minimum-terminal-size guard

**Where:** `browser_app.py:28` (`LIST_HEIGHT = 15`), `:101-124` (`_draw_window`, no minimum-size
check), `:132,141,144` (fixed 72-character dividers), `:186-196` (single `Window`, no size
`Conditional`), dialog at `:83-88` (`full_screen=True`).

**Verified:** 5×20, 3×10 and 1×1 all render without crashing (good) but show a clipped
frame with **zero** list rows and no explanation; the only feedback is a status line
that is itself off-screen. The resize stress run (5×20 → 40×120 → 3×8 → 30×100)
recovered cleanly, so prompt-toolkit's resize path is fine — the gap is only the
*small* end. The dialog degrades to prompt-toolkit's "Window too small" and does not
respond to Enter.

**Current:** the user sees a broken-looking screen and has to guess.
**Desired:** explicit, actionable refusal below a threshold.
**Fix:**

```python
    size = shutil.get_terminal_size()
    if size.lines < 20 or size.columns < 60:
        raise BrowserCancelled(
            f"The browser needs at least 60x20, this terminal is {size.columns}x{size.lines}. "
            "Resize it, or skip the browser: `agency-agents install --tool <kebab> --division <name>`."
        )
```

---

### L1 — LOW: long descriptions are silently truncated with no way to read the rest

**Where:** `browser_app.py:186-189` (`Window(...)`; `wrap_lines` defaults to `False`,
`layout/containers.py:1462`), `browser.py:144-158` (`detail_lines` emits the whole
description as one line).

**Verified:** at 80 columns the description ends in an `ESC[79C` skip — the rest is
unreachable, with no wrap, no scroll, no ellipsis. Pathological data does not crash
(5 KB names, CJK, emoji, combining marks, U+202E, zero-width — all fine; raw ANSI
escape sequences are neutralised by prompt-toolkit, so no terminal injection).
**Fix:** `wrap_lines=True, height=D(min=4, preferred=6)` for the detail region, or
wrap in Python to the layout width and cap at ~6 lines with a trailing `…`, so a
20 KB description cannot push the status line off-screen.

### L2 — LOW: `choose_tools` lacks the non-tty guard the browser has

**Where:** `browser_app.py:82-88` vs `:163-171`. Currently masked — `_browse_and_install`
calls the browser first, so a piped run never reaches the dialog. Verified by calling
`choose_tools` directly with piped stdin/stdout: it renders ~40 lines of box drawing
into the pipe, then raises `EOFError` → `BrowserCancelled` (correct outcome, ugly
path). Any future caller, or a background/`nohup` context, inherits the spew.
**Fix:** re-use the same `isatty` check at the top of `choose_tools` (factor it into a
helper both functions call, so the guard cannot drift).

### L3 — LOW: `--jobs` unvalidated; worker exceptions bypass the install net

**Where:** `main.py:259` (`jobs: int = typer.Option(4, ...)`), `converter.py:389`
(`ProcessPoolExecutor(max_workers=jobs)`), `converter.py:392` (`future.result()`).
**Verified:** `install --tool claude-code --agent anthropologist --parallel --jobs 0`
→ rich traceback panel `ValueError: max_workers must be greater than 0`, exit 1.
**Fix:** `if jobs < 1: raise typer.BadParameter(...)` (and an upper bound, e.g. ≤ 32,
so `--jobs 1000` cannot exhaust memory), and let `future.result()` failures flow into
the per-tool containment from H1 rather than out of the stop.

### L4 — LOW: `install_plugin` has a silent no-op path

**Where:** `installer.py:124-131` — `if not tool or tool.installKind != "plugin": return`.
A catalog/tool mismatch installs nothing and reports success; the caller prints
`✓ Installation process completed!`. Combined with `subprocess.run`'s unwrapped
`FileNotFoundError` (`:147`) for a missing `uv`, the plugin path is either silent or a
traceback.
**Fix:** `raise RuntimeError(f"{tool_kebab}: not a plugin tool")` and wrap the
subprocess `FileNotFoundError` into the same message.

### L5 — LOW: no automated coverage of any interactive failure path

Every integration test stubs the interactive layer — `run_browser` and `choose_tools`
are monkeypatched in `tests/integration/test_cli_tui.py` (lines 222-345) and
`test_cli_commands.py:440-460` — while `tests/unit/test_browser.py` exercises only the
pure model. Consequences: C1, H3, M2, M5 and M6 are all invisible to CI, and
`test_cli_tui.py:236` actively locks in the M1 exit-0 behaviour. The `Keys.Any` map
(`_NAMED_KEYS`) has no test at all, which is why M5 survived.
Bracketed paste is also silently dropped (one multi-char event → `apply_key` matches
nothing → no-op) — acceptable, but nothing asserts it.
**Fix:** add one `pty`-based smoke test module (this review's harness is ~60 lines)
covering: Down moves the cursor; Esc → exit 1; Enter with an empty selection → exit 1
(after M1); Ctrl-C inside the dialog cancels; an exception in `apply_key` leaves a
restored terminal and exit 1 (after C1).

---

## 3. What already holds (do not regress)

* **Non-tty is loud and names the flag.** `browser_app.py:166-171` → `BrowserCancelled`
  → `main.py:462-464` → exit 1 with
  `The browser needs a terminal … use 'agency-agents install --tool <kebab> --no-interactive'`.
  Verified for `tui` and bare `install` with piped stdin: exit 1, flag named, nothing written.
* **Empty roster is a clean error** (`main.py:455-458`): red message, exit 1, no traceback.
* **The renderer cannot be crashed by data.** 5 KB names, 20 KB descriptions, CJK, emoji,
  combining marks, zero-width characters, bidi overrides, newlines/tabs, and raw ANSI/OSC
  sequences all render; escape sequences are sanitised by prompt-toolkit (no injection),
  and `render_screen` stays a pure function (`browser_app.py:127-153`).
* **Resize is safe.** Four resizes in one session (including 3×8) repaint correctly;
  `SIGWINCH` handling is prompt-toolkit's and does not need work.
* **Terminal hangup terminates.** Closing the pty kills the process via SIGHUP rather
  than leaving a zombie modal behind.
* **No retry storms.** Nothing in the interactive or install path retries; there is no
  queue to grow unboundedly. The risk is the inverse — H2 makes the install
  non-idempotent, so if a wrapper ever adds retries, a truncated file becomes a
  permanent one.

---

## 4. Top three resilience investments, ranked by risk reduction per effort

1. **Make a keystroke non-fatal (C1 + M3, ~15 lines).** Wrap the `Keys.Any` body and
   `application.run()` so every interactive failure becomes `BrowserCancelled` with the
   existing flag message. Converts the only *unrecoverable* failure (SIGKILL + broken
   terminal) into a clean exit 1. Highest payoff for the smallest diff, and it is the
   one row in the table marked Cascading that affects 100 % of interactive users.
2. **Per-tool containment + atomic writes in the install path (H1 + H2 + L3 + L4,
   ~40 lines).** `except Exception` per tool with an installed/failed summary, plus
   `.tmp` + `os.replace()` per artifact. This is the only place where a failure escapes
   the CLI and mutates the user's tool configuration; it reduces the blast radius of a
   single disk/permission problem from "whole batch aborted, unknown partial state" to
   "one tool reported, everything else installed, no torn files".
3. **Make the tool dialog escapable and honest (H3 + M5 + half of M1, ~30 lines).**
   Bind Esc/Ctrl-C to cancel, correct the two misleading help strings, and (optionally,
   ~4 lines) bind the arrow escape sequences. Removes the dead-end modal and the
   silent-no-op keys — the two ways an ordinary user gets stuck in a screen they cannot
   reason about.

---

## Appendix — reproduction

```bash
# 1. non-tty: loud, exit 1, flag named
printf '' | uv run agency-agents tui ; echo "exit=$?"          # -> 1

# 2. arrow keys are dead; Tab selects; Enter with empty selection exits 0
#    (drive the CLI in a pty, send: Down Down Tab Esc / space Enter)

# 3. exception inside the key handler freezes the app
python - <<'PY'
import agency_agents.infrastructure.browser_app as ba
from agency_agents.infrastructure.browser import BrowserModel, BrowserRow
m = BrowserModel(rows=[BrowserRow("d", "a", "A", "desc")])
orig = ba.apply_key; n = {"i": 0}
def boom(model, key):
    n["i"] += 1
    if n["i"] >= 2: raise RuntimeError("boom")
    return orig(model, key)
ba.apply_key = boom
ba.run_browser(m)          # run inside a pty: traceback -> "Press ENTER" -> never exits
PY

# 4. one non-RuntimeError kills the batch
python - <<'PY'
from agency_agents.cli.main import _install_agents
from rich.console import Console
class F:
    def install_all_for_tool(self, agents, tool, **kw):
        raise PermissionError(13, "Permission denied") if tool == "t2" else None
_install_agents(Console(), F(), [], ["t1", "t2", "t3"], "user")   # raises, no summary
PY

# 5. end-to-end permission failure: traceback, exit 1, no aggregate report
mkdir -p /tmp/ro && chmod 0555 /tmp/ro && cd /tmp/ro
uv run agency-agents install --tool claude-code --scope project --no-interactive

# 6. SIGINT ignored while the browser runs
uv run agency-agents tui & sleep 1; kill -INT %1; sleep 1; jobs   # still running

# 7. --jobs 0
HOME=$(mktemp -d) uv run agency-agents install --tool claude-code \
  --agent anthropologist --no-interactive --parallel --jobs 0      # ValueError traceback
```
