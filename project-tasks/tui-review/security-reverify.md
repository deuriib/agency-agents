# Security Re-Verification — TUI (`tui`, bare `install`), post-fix pass

**Reviewer role:** Application security & threat modelling (verification pass, not re-discovery)
**Scope:** verify the claimed fixes for SEC-1 … SEC-6 from `project-tasks/tui-review/security.md` against the
**uncommitted working tree** of `/home/deuriib/projects/agency-agents` (HEAD `253cae4` + local changes).
**Verdict: 🟡 3 RESOLVED · 2 PARTIAL · 1 NOT-ADDRESSED · 1 REGRESSION.** The headline High (fail-open exit)
is genuinely fixed — verified on a real pty through the real console script, with zero files written. But the
fix moved the markup problem instead of closing it (catalog-controlled sinks still crash/spoof), and the new
key-dispatch path introduced a **new fail-open trigger: a bracketed paste containing a bare carriage return
is treated as ENTER and installs**.

**Files re-read as they are now (all lines):**
`src/agency_agents/infrastructure/browser.py` (282), `src/agency_agents/infrastructure/browser_app.py` (257),
`src/agency_agents/cli/main.py` (866 — `_safe`, `install`, `tui`, `_handle_list`, `_collect_roster`,
`_print_plan`, `_browse_and_install`, `_install_agents`),
`src/agency_agents/infrastructure/installer.py` (216),
`src/agency_agents/tests/integration/test_cli_tui_headless.py` (104, new),
plus the diffs of `tests/unit/test_browser.py`, `tests/integration/test_cli_tui.py`,
`tests/integration/test_cli_commands.py`.

**Method.** Static diff reading **plus execution**. Every verdict below has a re-run of the original
reproduction:
real pty (`pty.openpty` + `TIOCSWINSZ`, child drives the real `run_browser`), the real `agency-agents`
console script against a hostile catalog copied from this repo and mutated in place
(`/tmp/evilcat`, divisions symlinked, `HOME` redirected), and the headless pipe harness the fix itself added.
Harness kept for reproduction: **`project-tasks/tui-review/pty_reverify.py`**
(`.venv/bin/python project-tasks/tui-review/pty_reverify.py`).

**Test suite asked for in the task:**

```
$ uv run pytest src/agency_agents/tests/integration/test_cli_tui_headless.py -q
10 passed in 1.45s
```

Wider check of every touched file:

```
$ uv run pytest tests/unit/test_browser.py tests/integration/test_cli_tui.py \
      tests/integration/test_cli_tui_headless.py tests/integration/test_cli_commands.py -q
115 passed in 2.30s
```

---

## 1. Verdict table

| # | Severity | Original finding | Verdict | One-line reason |
|---|---|---|---|---|
| SEC-1 | High | Cancel keys commit the install (fail-open) | **RESOLVED** | Every abort key now raises `BrowserCancelled` with a non-empty selection; E2E `tui` on a pty with `TAB,ESC` exits **1** and writes **0** files. |
| SEC-2 | Medium | Markup-enabled `console.print` over caller/catalog text | **PARTIAL** | The four CLI-selector sinks are clean, but catalog JSON/filename sinks are still unescaped: `MarkupError` and invisible-text spoofing both still reproduce. |
| SEC-3 | Low | Bidi / zero-width display spoofing | **RESOLVED** | `build_rows` → `_display_safe` escapes U+202E/U+200B/U+2028/U+2066/U+2069/C0/C1/DEL; pty frame now carries **0** raw format bytes. Residual gap on the CLI path (see NEW-3). |
| SEC-4 | Low | Key copy contradicted the code | **RESOLVED** | Status line says `tab to select`, `esc cancel` really cancels, and up/down/page/c-n all move — all verified in a pty frame + model result. |
| SEC-5 | Low | Key-handler exception freezes app | **PARTIAL** | `apply_key` failure → clean `BrowserCancelled` (pinned by a test), but a render failure escapes as an uncaught `RuntimeError` traceback and terminal hangup still exits **120** with no message (`OSError` not caught). |
| SEC-6 | Low | `$HOME` tool-presence oracle | **NOT-ADDRESSED** (accepted, per the original report) | No fix claimed and none applied; `- detected` suffix and per-tool destination patterns still render. Informational only. |
| **NEW-1** | **Medium** | **Bracketed paste of a lone CR/LF acts as ENTER → install** | **REGRESSION** | `key_name()` consults raw `event.data` before key identity; a `BracketedPaste`'s data *is* the pasted text, so pasting `\r` accepts and installs. Reproduced E2E: rc=0 + a real file in `~/.claude/agents/`. |
| NEW-2 | Low | Catalog `dest` template / runbook fields unescaped | NEW (SEC-2 residual) | `[black on black]…[/]` in a `dest` hides the real plan line; `[/x]` in a `dest` is a reproducible `MarkupError` traceback. |
| NEW-3 | Low | `_collect_roster` prints a raw-ESC filename | NEW (SEC-2 residual) | A catalog file named `bad\x1b]0;pwned\x07.md` puts a raw `ESC` on stdout and into CI logs. |
| NEW-4 | Nit | `_atomic_write` predictable `.tmp` name is symlink-followed | NEW (hardening) | A pre-created `<dest>.tmp` symlink redirects the write; `os.replace` then leaves the destination as that symlink. No cleanup of `.tmp` on failure. |

Counts this pass: **0 high · 1 medium (new) · 3 low · 1 nit** — versus 1 high at the previous pass.

---

## 2. SEC-1 — High — Cancel keys commit the install → **RESOLVED**

**What changed.**
`browser_app.py::run_browser` now ends with an unconditional abort:

```python
if outcome.get("result") == ABORT:
    raise BrowserCancelled("No agents installed — selection cancelled.")
return model.selection()
```

The old `if ABORT and not model.selected` guard is gone, so a non-empty selection can no longer convert an
abort into a write. Key identity is resolved from the parsed enum, not a byte map:
`press.key.value if isinstance(press.key, Keys) else press.key`, translated by `browser.key_name` — and
`_ABORT = {"escape", "c-c", "c-q"}` is unchanged.

**Re-run of the original table [verified, real pty + real console script].**
Child process = real `run_browser`; `HOME=/tmp/e2ehome` with `.claude/agents/` pre-created so tool detection
picks a destination (i.e. the worst case for the old bug).

| Keys sent | Old result | Result now | Files written |
|---|---|---|---|
| `TAB` then `ESC` | `RESULT_OK:['slug-a']`, installs | `CANCELLED No agents installed` · **rc 1** | **0** |
| `C-A` (select all) then `ESC` | installs everything | `CANCELLED` · **rc 1** | **0** |
| `TAB` then `Ctrl-C` (`\x03`) | `RESULT_OK:['slug-a']`, installs | `CANCELLED` · **rc 1** | **0** |
| `TAB` then `Ctrl-Q` (`\x11`) | installs | `CANCELLED` | **0** |
| `ESC` with nothing selected | correct (`CANCELLED`) | `CANCELLED` | **0** |
| `TAB` then `ENTER` | accepts | `RESULT ['backend-architect']` (accept still works) | — |

Enter is now the only accepting key, which is what the help line claims, and the downstream blast radius the
original finding described (200+ agent files auto-loaded by six tools) is no longer reachable from an
advertised "cancel" key. **The finding is closed.**

**Residual, not a reopening of SEC-1 but note it:** with no `--tool`, `_detected_tools` still auto-selects
every detected tool with no per-tool confirmation (`main.py::_browse_and_install`). `ENTER` = "install into
all six". That is a deliberate product decision; it is now behind an intentional keystroke, which is exactly
the line the original finding asked for.

---

## 3. SEC-2 — Medium — Markup over external text → **PARTIAL**

**What changed.** New `main.py::_safe()` strips `c < " "`, `\x7f` and C1 `\x80`–`\x9f`, then
`rich.markup.escape()`. Applied at seven sinks: `SelectionError` (×2 paths), unknown tool, invalid scope,
unknown tool in the TUI pre-flight, `--list` unknown value, unknown runbook slug.

**The claimed reproductions are genuinely clean [verified]:**

```
$ agency-agents install --agent '[/x]' --no-interactive --dry-run
❌ Unknown agent '[/x]'. Use --list agents to see the available roster.      rc=1   # one line, no MarkupError
$ agency-agents install --list '[/x]'
Unknown --list value '[/x]'. Use: tools | teams | agents | runbooks | all     rc=1
$ agency-agents install --tool '[/x]' --no-interactive --dry-run
❌ Unknown tool(s): [/x]                                                      rc=1
$ agency-agents install --scope '[/x]' --agent backend-architect ... --dry-run
❌ Invalid scope '[/x]'. Use 'user' or 'project'.                             rc=1
$ agency-agents install --runbook '[/x]' ...
❌ Unknown runbook '[/x]'. Run `...--list runbooks` to see all 42.             rc=1
```

**The log-injection half is also closed for these sinks [verified, raw bytes]:**

```
$ agency-agents install --agent $'\x1b]0;pwned\x07X' --dry-run | xxd
00000000: e29d 8c20 556e 6b6e 6f77 6e20 6167 656e  ... Unknown agen
00000010: 7420 275d 303b 7077 6e65 6458 272e ...   t ']0;pwnedX'.     # ESC and BEL gone
```

**Why it is PARTIAL — the same class is still reachable from the catalog.** `_safe` was applied to
*selector* text only; three catalog-controlled sinks still hand external strings to a markup-enabled
`Console`:

**(a) `_print_plan` — `tools.json` `dest` templates, `main.py:185`** `console.print(f"    {pattern}  [{marker}]")`

Spoof of the dry-run plan — the user's **only** confirmation surface before a write:

```jsonc
// tools.json -> tools["claude-code"].dest.user
["[black on black].claude/agents/{slug}.md[/] ~/.claude/agents/{slug}.md"]
```

```
$ cd /tmp/evilcat && agency-agents install --tool claude-code --division engineering --non-interactive --dry-run
claude-code (per-agent, 75 agents, scope=user)
    .claude/agents/{slug}.md ~/.claude/agents/{slug}.md      <-- first path renders black-on-black on a tty
```

On a terminal the plan line shows one destination while the installer writes both. Same sink, weaponised for
availability instead of deception:

```jsonc
["[/x] .claude/agents/{slug}.md"]
```
```
MarkupError: closing tag '[/x]' at position 4 doesn't match any open tag      rc=1
```
Fail-closed, but a rich traceback instead of a clean error — the exact symptom SEC-2 was raised for.

**(b) `install` runbook success path, `main.py:322-330`** — `definition.slug`, `.title`, `.mode`,
`.duration`, `group.group`, `group.activation` are interpolated raw ("Runbook **{slug}** — {title}"):

```jsonc
// strategy/runbooks.json -> runbooks[0]
"title": "[bold green]ALL 42 RUNBOOKS VERIFIED CLEAN[/]"
"roster[0].group": "[bold green]core (installed)[/]"
```
```
Runbook startup-mvp — ALL 42 RUNBOOKS VERIFIED CLEAN (NEXUS-Sprint, 4-6 weeks)
  core (installed) always         9 agents
```
Markup consumed; a `[black on black]`/`[/x]` payload in the same fields hides text or raises `MarkupError`.

**(c) `_collect_roster`, `main.py:194`** — `console.print(f"[bold red]❌ {e}[/bold red]")` with
`ValueError(f"Cannot parse agent frontmatter: {file}")`. A POSIX filename may contain `0x1b`:

```
$ ls zz-evil
'bad'$'\033'']0;pwned'$'\a''.md'
$ agency-agents install --list agents          # stdout piped, i.e. into a CI log
❌ Cannot parse agent frontmatter: /tmp/evilcat/zz-evil/bad<ESC>]0;pwned.md
raw ESC in message: 1   raw BEL: 0
```
The `ESC` reaches the terminal/log intact; an unterminated `OSC` then swallows following output on a
compliant terminal. This is the *identical* primitive SEC-2 documented for selectors, just on the catalog
side.

**Also:** no test pins the fix. `grep -rn '\[/x\]\|MarkupError\|_safe' src/agency_agents/tests/` returns only
`_display_safe` unit tests — the report's own recommendation ("regression test: `install --agent '[/x]'` must
exit 1 with a single-line message and no `MarkupError`") was not implemented, which is how (a)–(c) survived.

**Fix:** make `_safe` the *only* way external text is printed (add it to `_print_plan`'s `pattern`, the runbook
fields, `group.*`, and `_collect_roster`), or better, print these as `rich.text.Text` objects so escaping
cannot be forgotten; add the three tests.

---

## 4. SEC-3 — Low — Bidi / zero-width spoofing → **RESOLVED**

**What changed.** `browser.py::_display_safe()` replaces any character whose `unicodedata.category` is in
`("Cc", "Cf", "Zl", "Zp")` with a visible `\uXXXX` escape; applied to `division`, `frontmatter.name` and
`description` in `build_rows`. `slug` is untouched (already `[a-z0-9-]`).

**Re-run through the production path (`build_rows` → `render_screen`) [verified]:**

| Frontmatter payload | `row.name` now | raw format chars left in the rendered frame |
|---|---|---|
| `\u202eAuditor\u202c (real: Finance)` | `'\\u202eAuditor\\u202c (real: Finance)'` | **0** |
| `z\u200bw` | `'z\\u200bw'` | **0** |
| `a\u2028b` (line separator) | `'a\\u2028b'` | **0** |
| `\u2066evil\u2069` (LRI/PDI) | `'\\u2066evil\\u2069'` | **0** |
| `\x1b[31mred` (C0) | `'\\u001b[31mred'` | **0** |
| `\x9b2J` (C1 CSI) | `'\\u009b2J'` | **0** |
| `a\x7fb` (DEL) | `'a\\u007fb'` | **0** |

And on a real pty frame, the original payload row is now visible text, not a spoofed glyph run:
`raw U+202E bytes = 0, raw U+200B = 0, literal '\\u202e' occurrences = 8`. The sneakier spoof (make a row
*look* unselected, or make `slug-bidi` read as another agent) no longer works, and the fix is stronger than
asked: C0/C1 are now escaped to `\uXXXX` as well, so the browser no longer depends on prompt-toolkit's
display mapping for those.

**Two residual notes (defence-in-depth, not reopening the finding):**
1. Sanitisation lives in `build_rows` only. A `BrowserRow` constructed directly (as the fix's own new test
   `make_model()` and `headless_probe.py` do) is **not** sanitised — `render_screen` has no second line of
   defence. Cheap hardening: apply `_display_safe` inside `render_screen`/`_draw_window` too, or in
   `BrowserRow.__post_init__`.
2. `_safe()` (CLI, NEW-3 below) does **not** strip `Cf`, so a bidi selector still prints raw on the CLI error
   path: `install --agent $'\u202eekat_deriuqer\u202c'` emits `e2 80 ae` / `e2 80 ac` verbatim, while
   `_display_safe` would have escaped them. The same one-line category filter should be shared.

---

## 5. SEC-4 — Low — Misleading key copy → **RESOLVED**

**What changed.** `status_line()` → `"… | type to filter, tab to select, enter to install"`; arrows now move
because `key_name("down", "\x1b[B") == "down"` and `_DOWN` contains `"down"`; `esc` really cancels (SEC-1).

**Re-run on a real pty (raw key sequences, model result) [verified]:**

| Keys | Result | Meaning |
|---|---|---|
| `DOWN, TAB, ENTER` | `['growth-hacker']` | **arrow moves** (was: dead) |
| `DOWN DOWN, TAB, ENTER` | `['deal-strategist']` | arrow moves repeatedly |
| `DOWN, UP, TAB, ENTER` | `['backend-architect']` | up/down symmetric |
| `PAGEDOWN, TAB, ENTER` | `['deal-strategist']` | page moves `PAGE_SIZE` |
| `c-n, TAB, ENTER` | `['growth-hacker']` | emacs binding preserved |
| `type 'sales', TAB, ENTER` | `['deal-strategist']` | filter + toggle |
| `F1`, `DEL`, `Home`, `Ctrl-Right`, multi-char paste | ignored, no crash | totality preserved |

**Rendered copy, straight out of the captured pty frame [verified]:**
`tab to select` = **present**, `tab toggle` = present, `esc cancel` = present, `up/down move` = present,
`space to select` = **absent**. The status line and the code now agree, and every key the screen advertises
does what it says.

**Nit introduced by the same mechanism as NEW-1:** `_CHAR_NAMES` maps `"\n"` → `"enter"`, so **`Ctrl-J` now
accepts and installs** (previously `c-j` was a no-op). `TAB, LF` → `RETURN ['backend-architect']` [verified].
Ctrl-J is indistinguishable from Enter on many terminals, so this is defensible, but it widens the accept
surface by one byte and should be a conscious choice, not a side effect of the byte table.

---

## 6. SEC-5 — Low — Error path freezes / hangup traceback → **PARTIAL**

**What changed.** `run_browser` wraps `apply_key` in `try/except Exception` → records the failure, exits the
app, and raises `BrowserCancelled`; and wraps `application.run(handle_sigint=False)` in
`except (EOFError, KeyboardInterrupt)` → `BrowserCancelled`.

**(a) Fixed and pinned [verified]** — the new headless test
`test_an_exception_in_the_key_handler_cancels` patches `apply_key` to raise and asserts `BrowserCancelled`.
It passes (`10 passed`). A bad keystroke can no longer freeze the app in the alternate screen.

**(b) Render-callback failure — behaviour changed but still not clean [verified, real pty].** With
`render_screen` patched to raise:

```
child still running after 2x ENTER: False
saw 'Press ENTER to continue': False
marker: ['\x1b[?12l\x1b[?25h@@ESCAPED@@ RuntimeError render exploded']
```

The original "resumes forever" loop no longer reproduces, but the exception now propagates **out of**
`application.run()` as an uncaught `RuntimeError` — the user gets a Python traceback instead of
`BrowserCancelled`, and `main.py` has no `except` for it. Fail-closed (exit 1, nothing written), not clean.
The original fix text asked for `except (EOFError, OSError, RuntimeError)` and/or
`set_exception_handler=False`; neither is there — only `(EOFError, KeyboardInterrupt)` and no
`set_exception_handler` argument.

**(c) Terminal hangup — unchanged [verified].** Close the pty master mid-session:

```
exit code: 120 | after 0.16 s
traceback printed: no   marker: none
```

Exit **120** with no message and no `BrowserCancelled`: exactly the previously reported behaviour. The
`OSError` the report named is still not caught, so the CLI cannot explain itself. Fail-closed by accident.

**Fix (cheap, ~3 lines):** `except (EOFError, KeyboardInterrupt, OSError, RuntimeError)` →
`BrowserCancelled`, and pass `set_exception_handler=False` to `Application(...)` so a renderer defect
unwinds to the same clean refusal.

---

## 7. SEC-6 — Low — `$HOME` tool-presence oracle → **NOT-ADDRESSED (accepted)**

No fix was claimed and none was applied; the original report explicitly said "no fix required". Re-verified
present: the tool dialog still renders `" - detected"` per tool (`choose_tools`) and `--dry-run` still prints
every destination pattern per scope (`_print_plan`). Both are the feature working as designed; the disclosure
is "which config dirs exist under `$HOME`", which is screen-share-only. **Verdict: unchanged, accepted risk.**
Note the new `scope=` filtering in `choose_tools` *narrows* the disclosure slightly (tools with no destination
for the resolved scope are no longer listed).

---

## 8. New findings and regressions this pass

### NEW-1 — **Medium** — Bracketed paste of a lone CR/LF is treated as ENTER and installs (fail-open regression)

**Where.** `browser_app.py::run_browser._handle`:

```python
press = event.key_sequence[0]
key = press.key.value if isinstance(press.key, Keys) else press.key
result = apply_key(model, key_name(key, event.data))
```

`key_name` (`browser.py`) looks up `_CHAR_NAMES` on **`event.data` first**:

```python
return _CHAR_NAMES.get(data, key)     # {"\r": "enter", "\n": "enter", "\t": "tab", ...}
```

For a `Keys.BracketedPaste` event, `event.data` is **the pasted payload, not a keystroke**. So a paste whose
entire content is one of those five control characters masquerades as a real key. The previous
implementation dropped bracketed pastes whole — the original report verified that as F-3 ("bracketed paste
`…evil…` dropped whole, no crash, no injection"), so this is a **regression introduced by the fix**.

**Proof (headless pipe, no pty needed):**

```
tab then paste(CR)                    -> RETURN ['backend-architect']     <-- ACCEPT / INSTALL
tab then paste(LF)                    -> RETURN ['backend-architect']     <-- ACCEPT / INSTALL
tab then paste(TAB)                   -> RETURN []                        <-- toggled row 0 off
tab then paste(hello)                 -> RETURN ['backend-architect']     <-- unchanged: multi-char dropped
```

**Proof end-to-end (real console script, real pty, `HOME=/tmp/e2ehome`):**

```
TAB then ESC (cancel)          rc=1  files_written=[]
C-A then ESC (cancel all)      rc=1  files_written=[]
TAB then Ctrl-C                rc=1  files_written=[]
TAB then PASTE(CR)             rc=0  files_written=['.claude/agents/anthropologist.md']   <-- INSTALLED
```

**Attack scenario.** The user selects agents, then pastes something — a command copied out of a README, a
line copied from an editor or spreadsheet (clipboards routinely carry a trailing `\r`/`\n`, and a selection
of just the line ending is a single `\r`), or a payload a hostile document tells them to paste. The browser
reads that paste as ENTER and writes the full selection into every detected tool's agent directory with no
further confirmation — the same "commit without an intentional keystroke" property SEC-1 was raised for,
reached through a different affordance. Impact is bounded by what the user had already selected, hence Medium
and not High, but it is a *writing* operation triggered by an action that is not a key.

**Fix (one condition, ~3 lines).** Pasted text is data, not keystrokes:

```python
if key == "bracketed-paste":          # never dispatch a paste as a keystroke
    event.app.invalidate()            # (optionally: append to the filter in a future feature)
    return
```

plus a regression test: `drive("\t\x1b[200~\r\x1b[201~")` must raise `BrowserCancelled`, not return a
selection. While there, decide explicitly what `Ctrl-J` should do (see SEC-4 nit).

### NEW-2 — Low — `_print_plan` / runbook fields: `MarkupError` + invisible-text spoofing of the write plan

Detailed in §3 (a) and (b). Highest-impact variant: `[black on black]` in a `dest` template hides one of the
two destinations the installer will write to, on the screen the user is asked to trust. Fix: `_safe(pattern)`,
`_safe(definition.title)`, `_safe(group.group)`, …

### NEW-3 — Low — `_collect_roster` puts a raw `ESC` on stdout/logs from a catalog filename

Detailed in §3 (c). Fix: `console.print(f"[bold red]❌ {_safe(e)}[/bold red]")` — and have `_safe` reuse
`_display_safe`'s `Cf` filtering so bidi selectors stop printing raw too.

### NEW-4 — Nit — `_atomic_write`: predictable temp name, symlink-followed, never cleaned up

```python
tmp = path.with_name(path.name + ".tmp")     # predictable, in the destination directory
tmp.write_text(content, encoding="utf-8")
os.replace(tmp, path)
```

`tmp.write_text` **follows symlinks**. A pre-created `<dest>.tmp` symlink redirects the write [verified]:

```
victim.txt before : 'IMPORTANT USER DATA\n'
after _atomic_write(target, 'AGENT PAYLOAD\n'):
  victim.txt      : 'AGENT PAYLOAD\n'      <-- clobbered through the .tmp symlink
  x.md            : 'AGENT PAYLOAD\n'
  target is symlink? True
```

Honest severity: it requires write access to the destination directory, and the *final* path was already
written through a symlink before this change (`Path.write_text`), so this is not a new privilege boundary —
it is a new gadget plus a new leftover artifact (`.tmp` files are never removed on failure). Fix if you touch
it again: `tempfile.mkstemp(dir=path.parent)` + `os.fdopen`, or open with `O_NOFOLLOW | O_EXCL`, and unlink
in a `finally`.

Related nicety, not a vulnerability: `_install_agents` now catches bare `Exception`
(`main.py:604`) instead of `(RuntimeError, UnknownFormatError)`, so a programming error inside the loop is
reported as "Error installing <tool>" rather than surfacing as a bug. Keep the aggregate non-zero exit, but
consider catching `(RuntimeError, OSError, UnknownFormatError)` so `NameError`/`TypeError` still crash loudly.

---

## 9. What the fix got right (keep it)

- **Abort is now a real abort.** The unconditional `if outcome == ABORT: raise` is the correct shape — one
  exit, one meaning, no "selected ⇒ install" special case. Add the paste guard (NEW-1) and this surface has
  exactly one accepting key again.
- **Key dispatch through `Keys` + `key_name`** is the right seam: `key_name` is pure and unit-tested
  (Tab/Enter/Backspace vs prompt-toolkit's `c-i`/`c-m`/`c-h` is exactly the trap that produced SEC-4), and
  the byte map that used to live in the view is gone.
- **The headless integration test is a real gate.** 10 tests over the actual `Application` with a pipe input,
  no pty: escape/c-c always cancel, arrows/page/type work, a key-handler exception cancels. That is the
  testability condition D-001 asked for, satisfied rather than waived.
- **`_safe` in the right place, applied to the right strings** — C0/C1/DEL stripping *before*
  `markup.escape` is the correct order and kills both the crash and the log-injection primitive on the
  selector path.
- **`_display_safe` at the model boundary** is the cheapest place to fix SEC-3, and it now covers `Cf`
  (`Zl`/`Zp`/C0/C1/DEL too) — a superset of what was asked.
- **The stricter empty-selection exit** (`typer.Exit(1)` instead of `return`) closes a "looks like success"
  signal, and the tests were updated to match (`test_cli_tui.py`) rather than deleted.

---

## 10. Top three fixes by risk reduction per unit of effort

1. **Do not dispatch pasted text as keystrokes** (`browser_app.py::_handle`, ~3 lines + 1 test). Removes the
   only remaining way to install without an intentional keystroke — the one regression this pass found.
2. **Route every external string through `_safe`, not just selectors** (`_print_plan` `pattern`, runbook
   `slug/title/mode/duration`, `group.group/activation`, `_collect_roster`'s error; ~6 call sites). Closes
   the remaining `MarkupError` crash, the invisible-text spoof of the write plan, and the filename log
   injection — plus the bidi gap on the CLI path if `_safe` reuses `_display_safe`'s category filter.
3. **Widen `run_browser`'s guard to `(EOFError, KeyboardInterrupt, OSError, RuntimeError)` and pass
   `set_exception_handler=False`** (~3 lines). Turns the leftover traceback and the silent exit 120 into the
   same clean `BrowserCancelled` everything else already uses.

---

## 11. Appendix — exact commands used

```bash
# asked-for suite
uv run pytest src/agency_agents/tests/integration/test_cli_tui_headless.py -q     # 10 passed
uv run pytest tests/unit/test_browser.py tests/integration/test_cli_tui.py \
    tests/integration/test_cli_tui_headless.py tests/integration/test_cli_commands.py -q   # 115 passed

# SEC-1 / SEC-3 / SEC-4 / F-1 on a real pty (drives the real run_browser)
.venv/bin/python project-tasks/tui-review/pty_reverify.py

# SEC-1 end-to-end through the real console script (HOME redirected, .claude/agents pre-created)
# -> TAB,ESC | C-A,ESC | TAB,Ctrl-C  => rc=1, 0 files ;  TAB,paste(CR) => rc=0, 1 file written

# SEC-2 selector sinks
agency-agents install --agent '[/x]' --no-interactive --dry-run
agency-agents install --list '[/x]'
agency-agents install --tool '[/x]' --no-interactive --dry-run
agency-agents install --scope '[/x]' --agent backend-architect --no-interactive --dry-run
agency-agents install --runbook '[/x]' --no-interactive --dry-run
agency-agents install --agent $'\x1b]0;pwned\x07X' --no-interactive --dry-run | xxd

# SEC-2 residual sinks (hostile catalog: /tmp/evilcat, real catalog + mutated fields)
cd /tmp/evilcat && HOME=/tmp/evilhome agency-agents install --tool claude-code --division engineering --no-interactive --dry-run
cd /tmp/evilcat && HOME=/tmp/evilhome agency-agents install --runbook startup-mvp --no-interactive --dry-run
cd /tmp/evilcat && HOME=/tmp/evilhome agency-agents install --list agents
```

Environment: `.venv/bin/python` 3.13.18, prompt-toolkit 3.0.53, rich 15.0.0, `TERM=xterm-256color`,
pty geometry 100x30 (browser) / 120x40 (end-to-end).
