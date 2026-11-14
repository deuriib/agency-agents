# Security / Pen-Test Review — Interactive TUI (`tui`, bare `install`)

**Reviewer role:** Application security & threat modelling (Full Review Board seat)
**Verdict: 🟡 Conditional pass on injection — one High-severity fail-open write path must be fixed before ship.**
The headline question of this review ("can a malicious catalog or a typed query break out of the TUI and
inject terminal escape sequences?") resolves to **no, it cannot** — and I show the mechanism and the
byte-level evidence below. The real risk in this surface is not injection, it is a **fail-open exit**: the
keys the UI documents as *cancel* commit an install.

**Reviewed in full (every line):**
`src/agency_agents/infrastructure/browser.py` (245 lines),
`src/agency_agents/infrastructure/browser_app.py` (201 lines),
`src/agency_agents/cli/main.py` (834 lines — `tui`, `install`, `_browse_and_install`, `_detected_tools`,
`_install_agents`, `_collect_by_division`, `_collect_roster`, `_print_plan`, `_handle_list`).
Supporting reads for taint tracking: `core/models.py`, `core/parser.py`, `core/selection.py`,
`infrastructure/catalog.py`.

**Method:** static data-flow tracing (catalog file → `BrowserRow` → `FormattedText` → terminal; CLI argv →
`console.print`) **plus execution**. Injection claims were tested against a real pseudo-terminal
(`pty.openpty`), driving the real `run_browser` and the real `agency-agents` console script, and inspecting
the raw bytes written to the tty (`cat -v` of the captured frame). Library internals were read at source
level in the installed versions: **prompt_toolkit 3.0.53**, **rich 15.0.0**. Every claim below is
labelled **[verified]** (I executed it and read the bytes) or **[static]** (read from source only).

**Counts:** 1 high · 1 medium · 4 low · 6 explicit false positives.

---

## 1. Attack-surface map (what actually crosses a trust boundary)

| Input | Trust level | Path into the TUI | Path into `rich` |
|---|---|---|---|
| Agent `name`, `description`, `division` (markdown frontmatter) | **untrusted** (any catalog repo/fork) | `build_rows` → `render_screen` → `FormattedText` | **none** — grep of `main.py` finds frontmatter names only at line 780, which writes to a *file*, never to `console.print` |
| Agent `slug` | derived, `slugify()`-sanitized to `[a-z0-9-]` | same | none |
| Live filter `query` | **local user only**, one printable char per keystroke | `render_screen` line 131 | none |
| CLI selectors (`--agent`, `--division`, `--tool`, `--list`, `--runbook`, `--scope`, `--agents-file` ids) | caller-supplied (CI wrapper / another agent may pass it through) | — | **yes**, interpolated into markup-enabled f-strings |
| `tools.json` / `runbooks.json` fields | catalog (semi-trusted) | — | **yes** (`kebab`, `title`, `dest` patterns) |
| Keystrokes (`Keys.Any` + `event.data`) | local user / terminal | `apply_key` | none |

Two conclusions follow immediately and they shape the whole report:

1. The **TUI render path is the untrusted-data path**, and it is safe (§3, F-1 … F-4).
2. The **`rich` path is the CLI path**, and it is *not* fed frontmatter — but it is fed caller text and is
   markup-enabled (§4, SEC-2).

---

## 2. Risk-ranked findings

| # | Severity | Finding | Location | Exploitable by |
|---|---|---|---|---|
| SEC-1 | **High** | Fail-open exit: `escape` / `c-c` / `c-q` — the three keys the UI labels *cancel* — return the current selection, so the browser proceeds to install. No confirmation, no preview. | `browser_app.py:191,199-201` + `browser.py:191` → sink `main.py:461-527` | local user accident; a hostile catalog makes the payload |
| SEC-2 | **Medium** | Markup-enabled `console.print` over caller/catalog strings: `MarkupError` traceback (fails closed but ugly), output spoofing on the error path, and — when stdout is *not* a tty — intact terminal control sequences written into logs. | `main.py:352,358,489,494,222-225,307,330,489` | caller-supplied selector; `--agents-file` content; catalog JSON |
| SEC-3 | Low | Unicode bidi/zero-width characters pass through `FormattedText` to the terminal untouched → row/detail-pane display spoofing (ESC-stripping does not cover this class). | `browser.py:38-44`, `browser_app.py:131,143` | hostile catalog |
| SEC-4 | Low | On-screen key copy instructs the user to press keys that do something else on a *writing* operation (`space to select` = filter+reset; `esc cancel` = install; `up/down move` = dead). Operator-instruction integrity on a destructive action. | `browser.py:166`; `browser_app.py:150` | — (misleading by construction; overlaps reliability/refuter findings) |
| SEC-5 | Low | TUI error path: prompt_toolkit's default exception handler **resumes** the loop after printing "Press ENTER to continue…", so a deterministic failure is a stuck UI, not a clean exit; terminal hangup escapes as an uncaught `OSError` traceback (rc 120). | `browser_app.py:197` | local / environmental |
| SEC-6 | Low | `$HOME` tool-presence oracle surfaced in the tool dialog ("- detected") and the dry-run plan — screen-share only. | `browser_app.py:57-62`, `main.py:532-547`, `main.py:203-212` | shoulder-surfer / screen recording |

---

## 3. Findings

### SEC-1 — High — Cancel keys commit the install (fail-open exit)

**Where:** `browser_app.py:191` sets `outcome["result"] = ABORT` on `escape`; `browser_app.py:199-201`:

```python
199:     if outcome.get("result") == ABORT and not model.selected:
200:         raise BrowserCancelled("No agents selected — nothing installed.")
201:     return model.selection()
```

`browser.py:191` declares `_ABORT = {"escape", "c-c", "c-q"}`. The guard only aborts when the selection is
**empty**; with any selection, the "abort" is converted into "install this".

**Reproduction [verified]** — real `run_browser`, real pty, 3-row model:

| Keys sent | Model result |
|---|---|
| `TAB` then `ESC` (single, flushed) | `RESULT_OK:['slug-a']` ← install proceeds |
| `TAB` then `Ctrl-C` (`\x03`) | `RESULT_OK:['slug-a']` ← install proceeds |
| `Ctrl-A` (select all) then `ESC` | `RESULT_OK:['slug-a','slug-b','slug-c']` ← installs everything |
| `ESC` with nothing selected | `RESULT_CANCELLED:No agents selected` ← correct |
| `ENTER` with nothing selected | `RESULT_OK:[]` → "Nothing selected" ← correct |

**Downstream blast radius [verified]:** `main.py:461-527` treats a non-empty return as approval, and because
`_detected_tools` returns **6 tools on this host** (`antigravity, claude-code, copilot, openclaw, opencode,
pi-agent`) it skips the tool dialog entirely (`main.py:474-485`) and installs into all six destinations with
no confirmation. The real roster is 200+ agents, so `Ctrl-A` + `ESC` writes 200+ attacker-influenceable
markdown files into `~/.claude/agents/`, `~/.copilot/agents/`, `~/.config/opencode/agents/`,
`~/.openclaw/agency-agents/`, … — files those tools auto-load as instructions.

**Expected:** a key documented as *cancel* (`browser_app.py:150` renders `enter install  esc cancel`)
aborts and writes nothing.
**Actual:** it writes the full selection. `Ctrl-A` is the most common "select all / beginning-of-line"
muscle-memory key in a terminal, and `ESC` is the reflex that follows a mistake.

**Security framing:** this is a local write with no privilege boundary crossing, but the *content* is
catalog-controlled and the *trigger* is an affordance the program itself advertise as safe. That
combination — no confirmation + documented-safe trigger + bulk write into config that other AI tools
execute — is why I rate it High rather than a UX nit. It is also the same root cause the reliability
reviewer reported as "esc triggering an install"; **please dedupe the fix, not the finding.**

**Fix (pick one, prefer A):**
- **A.** Make the outcome explicit and require `ACCEPT` to write: return a small result object
  (`status: accept|abort`, `selection`) instead of a bare list; in `_browse_and_install`, `abort` →
  `BrowserCancelled` unconditionally (`main.py:462` already handles it correctly).
- **B.** Keep the current semantics but make it visible: before writing, print the plan (tools × agent
  count) and require an explicit `y` when the count exceeds a threshold. This is a mitigation, not a fix —
  the UI text would still say "cancel" for a key that writes.
- Cheap partial: drop `c-c`/`c-q` from `_ABORT`-with-selection and make `escape` unconditional.

---

### SEC-2 — Medium — Markup-enabled `console.print` over caller/catalog strings

**Where:** every error path interpolates caller text into a markup string with markup enabled (rich's
`Console()` default). Verified sinks:

* `main.py:352` `console.print(f"[bold red]❌ {e}[/bold red]")` — `e` is `SelectionError`, whose message
  embeds the raw selector (`core/selection.py:110-114`).
* `main.py:358` `Unknown tool(s): {', '.join(unknown)}`
* `main.py:489` same in the TUI path (unreachable from the browser, which only yields real slugs).
* `main.py:494` `Invalid scope '{resolved_scope}'`
* `main.py:222-225` `Unknown --list value '{list_what}'`
* `main.py:317,322` runbook slug/title/groups (catalog JSON)
* `main.py:203-212` `_print_plan` — `tool.dest` patterns (catalog JSON, may contain `/`)

**Reproduction [verified]** — three separate commands, each ending in an uncaught `MarkupError` traceback:

```
$ agency-agents install --agent '[/x]' --no-interactive --dry-run
MarkupError: closing tag '[/x]' at position 27 doesn't match any open tag        # exit 1

$ agency-agents install --list '[/x]'
MarkupError: closing tag '[/x]' at position 32 doesn't match any open tag        # exit 1

$ agency-agents install --tool '[/x]' --no-interactive --dry-run
MarkupError: closing tag '[/x]' at position 29 doesn't match any open tag        # exit 1
```

**Expected:** `Unknown agent '[/x]'. Use --list agents …` (a clean, one-line error).
**Actual:** a rich traceback panel. It **fails closed** (exit 1, nothing installed) — so this is a DoS and an
output-integrity bug, not a code-execution bug.

**Second, worse half — log injection [verified].** When stdout is *not* a tty, rich emits no style codes, so
caller-supplied control bytes reach the file/log **intact**:

```
$ agency-agents install --agent $'\x1b]0;pwned\x07X' --dry-run   # stdout piped
b"\xe2\x9d\x8c Unknown agent '\x1b]0;pwnedX'. Use --list agents to see the available roster.\n"
                                        ^ raw ESC, contiguous, an executable OSC 0
```

Any CI job, `tee`d log, or artifact that later gets `cat`-ed to a terminal executes that OSC (title spoof,
and `OSC 52` for clipboard write on terminals that enable it). On a real tty the same input happened to be
split by rich's interleaved SGR runs (`ESC` `ESC[0m` `]` …), which is an **accident of styling, not a
control** — do not rely on it.

**Spoofing variant [verified at unit level]:** `[bold green]✔ Installed 42 agents[/]` inside a selector
renders as a green success line while the process exits 1 — a wrapper that relays user text can be made to
print a forged success.

**Not reachable from frontmatter:** I grepped `main.py` for every frontmatter access; agent `name` /
`description` / `division` never reach `console.print` on the `tui`/`install` paths (only `main.py:780`,
which writes file content). So this finding is about **CLI selectors + catalog JSON**, not the catalog's
agent prose. That distinction is exactly why it is Medium and not High.

**Fix:**
- Wrap untrusted values: `from rich.markup import escape` → `f"[bold red]❌ {escape(str(e))}[/bold red]"`,
  or print them as a separate object: `console.print("❌", e, style="bold red", markup=False)`, or build
  `rich.text.Text` objects (never markup) for anything containing external data.
- Strip C0/C1 from any string of external origin before printing (`"".join(c for c in s if c >= " " and c != "\x7f")`).
- Same treatment for `tools.json` / `runbooks.json` fields at their sinks.
- Regression test: `install --agent '[/x]'` must exit 1 with a single-line message and no `MarkupError`.

---

### SEC-3 — Low — Unicode bidi / zero-width characters reach the terminal (display spoofing)

**Where:** `browser.py:38-44` (`build_rows` copies `name`/`description` verbatim), rendered at
`browser_app.py:131` (filter) and `:143` (rows), `:146-149` (detail pane).

**Reproduction [verified]:** a row whose name is `"\u202eAuditor\u202c (real: Finance)"` renders as the
literal fragment `' [ ] div/slug-bidi  -  \u202eAuditor\u202c (real: Finance)\n'` **[verified @
`render_screen`]** and the raw UTF-8 bytes `e2 80 ae` (U+202E RTL OVERRIDE) appear in the captured pty
frame **[verified]** — prompt_toolkit only remaps `\x00`–`\x1f`, `\x7f`, `\x80`–`\x9f` and `\xa0`
(`prompt_toolkit/layout/screen.py` `Char.display_mappings`); Unicode format characters are not in that
table. Zero-width space (U+200B) and combining marks likewise pass through (they simply do not advance the
cell).

**Expected:** control/format characters are visibly escaped, as C0 already is (`^[`, `^G`).
**Actual:** a catalog author can embed RTL overrides and zero-width characters that a bidi-capable terminal
will reorder, so the row can *read* differently from its content (e.g. make a row look unselected, or make
`slug-bidi` look like a different agent). Impact is display-only — no escape reaches the terminal, and the
detail pane always shows the real `slug`, which limits the deception.

**Fix:** normalize at the model boundary, one line in `build_rows`:

```python
def _display_safe(text: str) -> str:
    return "".join(c if unicodedata.category(c) not in ("Cc", "Cf", "Zl", "Zp") else
                   "\\u%04x" % ord(c) for c in text)
```

Apply to `name`/`description`/`division` (keep `slug` as-is — already `[a-z0-9-]`). Add a unit test with
U+202E / U+200B / U+2028.

---

### SEC-4 — Low — On-screen key instructions contradict the code on a writing action

**Where:** `browser.py:166` —

```python
166: return f"{scope} | {picked} selected | type to filter, space to select, enter to install"
```

`SPACE` is **not** a select key: `_TOGGLE = {"tab"}` (`browser.py:186`), and `apply_key` falls through to
`browser.py:242-244`, so space is appended to the filter and `set_query` resets the cursor to row 0.
**[verified]**: keys `SPACE TAB ENTER` → `RESULT_OK:['slug-a'] QUERY:' '`.

Also `browser_app.py:150` renders `enter install  esc cancel` (ESC installs — SEC-1), and the help line's
`up/down move` is dead (arrow keys arrive as `event.data == '\x1b[B'`, a multi-char string that `apply_key`
drops at `:242`; `c-n`/`c-p` work — **[verified]**: `TAB DOWN TAB ENTER` → `[]`, `TAB c-n TAB ENTER` →
`['slug-a','slug-b']`).

**Security relevance:** the TUI's only self-documentation is this text, and it tells the operator that a
cursor-resetting key selects and that the safe-looking exit key is a no-op. On an action that writes 200+
files, misleading operator instructions are an integrity issue, not cosmetics.
**Fix:** render the truth (`tab toggle`) or implement space as toggle; fix `esc` per SEC-1; drop or fix
`up/down`. Overlaps the reliability and refuter findings on the same lines — one fix closes all three.

---

### SEC-5 — Low — Error path inside the TUI resumes instead of exiting; hangup escapes as a traceback

**Where:** `browser_app.py:197` `application.run()` — no `try/except`, and prompt_toolkit's default
`set_exception_handler=True` (`prompt_toolkit/application/application.py:619-637, 1024`) catches loop
exceptions, leaves the alternate screen, prints the traceback, waits for `ENTER`, and **resumes the loop**.
**[verified]**: a render callback forced to raise produced `…Press ENTER to continue...` and the app kept
running instead of unwinding to `main.py`.

Consequence: a *deterministic* render failure is an unbreakable "exception → press ENTER → exception" loop
rather than a clean `BrowserCancelled`. I could not construct a data-driven trigger (`render_screen` is
string formatting only — no data path can raise), so this is defence-in-depth, not an exploitable DoS.

Separately, killing the terminal mid-session escapes as an uncaught `OSError: [Errno 5]` at
`prompt_toolkit/output/flush_stdout.py:38` and exits **120** **[verified]**. It does *not* reach the install
step — fail-closed, but by accident, and with a traceback. Also note `Application` with
`full_screen=True` cannot restore the tty after `SIGKILL`; a killed browser leaves the user's shell in the
alternate screen (`reset` required). Cosmetic/availability only.

**Fix:** wrap `application.run()` in `try/except (EOFError, OSError, RuntimeError)` → `BrowserCancelled`,
and pass `set_exception_handler=False` (or convert the handler into an exit) so a broken render aborts the
browser instead of looping.

---

### SEC-6 — Low — `$HOME` tool-presence oracle in UI

**Where:** `main.py:532-547` `_detected_tools` (existence checks under `Path.home()`),
`browser_app.py:57-62` (`"- detected"` suffix per tool), `main.py:203-212` (`_print_plan` prints every
destination pattern for the chosen scope).

Discloses which of `.claude`, `.copilot`, `.cursor`, `.config/opencode`, … exist for this user. **Not a
secret in any meaningful sense** (the paths are the tool's own documented config dirs, and the dry-run plan
is the feature), but it is content on screen during a screen-share or recorded demo. No fix required; note
it so nobody mistakes the dry-run plan for a leak later.

---

## 4. Explicit false positives (checked, not vulnerable — with the reason)

**F-1 — Terminal escape / OSC / CSI injection from agent frontmatter or the typed query: NOT POSSIBLE.**
This is the main hypothesis of the review and it is refuted at three layers:

1. `FormattedText` fragments are `(style, text)` tuples — `text` is **literal**, never parsed
   (`browser_app.py:129-153`). A name containing `[bold red]` renders as those 11 characters; there is no
   markup language in the prompt_toolkit path at all.
2. Every character in the buffer is normalized: `prompt_toolkit/layout/screen.py` `Char.display_mappings`
   maps `\x00`–`\x1f` → `^@ … ^_`, `\x7f` → `^?`, and `\x80`–`\x9f` → `<80> … <9f>` **(so both 7-bit
   `ESC` and 8-bit C1 `0x9b` CSI become visible text)**; `prompt_toolkit/output/vt100.py:518`
   (`Vt100_Output.write`) additionally does `data.replace("\x1b", "?")`.
3. Raw bytes are only emitted for fragments whose style contains `[ZeroWidthEscape]`
   (`prompt_toolkit/renderer.py:217-219`). `browser_app.py` never sets that style — the only styles used
   are `""`, `class:title`, `class:cursor`, `class:selected`, `class:dim` (all repo constants).

**Byte-level proof [verified].** Four payloads were placed in `division` / `name` / `description` / `query`
— `\x1b[2J`, `\x1b[H`, `\x1b[1;1H`, `\x1b[31m`, `\x1b]0;pwned-title\x07` (OSC 0), `\x1b]52;c;…\x07`
(OSC 52 clipboard) — and `run_browser` was driven in a pty. Captured frame, `cat -v`:

```
^[[0m filter: q^[[0;34m^[^[[0m[2J^[[0;34m^[^[[0m]0;title^[[0;34m^GM-bM-^@M-.^[[0mX^[[0m
```

Counting the raw bytes across the whole frame: **OSC 0 = 0, OSC 52 = 0, `CSI 2J` = 0, `CSI 1;1H` = 0,
`SGR 31m` = 0, BEL = 0**, while the **9 ESC characters present in the data render as 9 `^[` pairs**. Every
raw ESC in the stream is prompt_toolkit's own (`?1049h`, `?25l`, `0m`, …). The same holds with
`TERM=dumb` (0 raw payload sequences; 38 ESCs, all prompt_toolkit's).

**Filter `query` is additionally unreachable-by-design:** `apply_key:242` only appends
`len(key) == 1 and key.isprintable()`, so ESC/BEL/C1 can never enter the query in the first place; a
bracketed paste arrives as one multi-char `event.data` and is dropped entirely **[verified]**.

**F-2 — "A description could inject fake rows / fake status line via newlines": NOT POSSIBLE.**
`MarkdownParser.parse` (`core/parser.py:22-37`) is line-oriented: `data[k.strip()] = v.strip()`, so every
frontmatter value is a **single line** — `\n` cannot appear in `name` or `description`. A stray `\r` is
mapped to `^M` by `display_mappings`. There is no multi-line YAML block scalar support, therefore no
newline-based UI spoofing. (The flip side is a real *functional* limitation — see F-6 — but it is not a
vulnerability.)

**F-3 — "Crafted keys crash the CLI (DoS)": NOT REPRODUCED.** Twelve input classes were driven through the
real `run_browser` in a pty; none raised, none corrupted model state:

| Input | Result |
|---|---|
| `F1` `\x1bOP`, `Delete` `\x1b[3~`, `Home` `\x1b[H`, `End` `\x1b[F` | ignored, no crash |
| `PageDown` `\x1b[6~` | ignored (dead key), no crash |
| bracketed paste `\x1b[200~evil\x1b[2J…\x1b[201~` | dropped whole, no crash, no injection |
| `Alt-x` + invalid UTF-8 `\x80\xff\xc3` | clean `BrowserCancelled` |
| 8000 printable chars | query grows, no crash, no truncation limit hit |
| geometric degeneracy: pty 1×1, 0×0, 2×20 | runs, no `ZeroDivisionError` |
| `TERM=dumb`, `TERM` unset | runs, payloads still neutralized |

`apply_key` is total: every branch is a set-membership test or `str`/`int` arithmetic, and the fall-through
returns `CONTINUE`. `[static]`

**F-4 — "Non-tty guard can be bypassed into a silent no-op / half-install": NO, it is fail-closed.**
`browser_app.py:166` requires **both** `sys.stdin.isatty()` and `sys.stdout.isatty()` before constructing
the `Application`; otherwise `BrowserCancelled` → `main.py:462-464` → `typer.Exit(1)`. **[verified]**

```
$ printf '' | agency-agents tui            # exit 1
The browser needs a terminal, and this session has none. Use the flags instead:
`agency-agents install --tool <kebab> --no-interactive`.
$ printf '' | agency-agents install        # exit 1, same message
```

Exit code **1** in both cases (checked with `$?` directly, not through a pipe), so a script cannot mistake a
refusal for a successful install. A hangup mid-session also exits non-zero (rc 120, SEC-5) without writing.
Complements the reliability reviewer's point that the guard's *message* is good; from a security standpoint
the guard is complete for the paths I could reach.

**F-5 — Command injection / unsafe deserialization: NONE in scope.**
`grep` over the three files: no `shell=True`, no `os.system`, no `eval`/`exec`/`pickle`. The single
`subprocess` use is `main.py:766-770` — an argv **list** (`["uv","run","python",build_script,"--out",target]`)
in `convert`, not reachable from the TUI. Catalog JSON is loaded with `json.load` + pydantic; agent
frontmatter is **hand-parsed line-by-line** (`core/parser.py`), *not* `yaml.load` — so there is no
`!!python/object` deserialization surface and no YAML entity-expansion bomb.

**F-6 — Secrets / credentials / PII in TUI output or errors: NONE FOUND.**
No env reads, no token/key/credential handling, no `os.environ` access in the reviewed paths.
`_print_plan` prints catalog **relative** destination patterns (`.claude/agents/{slug}.md`, confirmed
against `tools.json`) — never an expanded `$HOME`. Error texts carry catalog paths (`_collect_roster`'s
`ValueError` includes the offending file path) and installer `RuntimeError` texts (`installer.py`
`Unknown tool`, `no destination for scope`, `slug collisions`) — repo-relative paths and slugs only. The one
privacy-shaped item is SEC-6 (which config dirs exist), and it is marginal.
*Related note (out of scope, flagged for the board):* `_collect_by_division` prints the failing path into
`console.print` markup at `main.py:176-178`; a filename **cannot** contain `/`, so it cannot contain a
closing rich tag and cannot raise `MarkupError` — I verified `bad[red].md` parses fine and `a[/b].md` is
impossible to create on POSIX. Cosmetic tag-eating only.

---

## 5. Positive controls already in place (keep them)

- `mouse_support=False` (`browser_app.py:195`) — no mouse-reporting parser in the attack surface.
- `always_hide_cursor=True` + `full_screen=True` — no cursor-position echo of on-screen data.
- The browser writes nothing to disk itself; every write goes through `_install_agents`/`InstallationManager`
  (`main.py:551-583`), the same pipeline as flag-driven install, and failures aggregate into one non-zero
  exit (`main.py:519-527`) rather than a partial silent success.
- `ISIG` is disabled in raw mode (`prompt_toolkit/input/vt100.py:268`), so `Ctrl-Z`/`Ctrl-\` cannot suspend
  or dump core mid-render; `Ctrl-C` is delivered to the app, not the kernel.
- Model/view split with no state in the view (`browser_app.py`) means the security-relevant state
  (`selected`, `query`, `cursor`) can be asserted headlessly — cheap place to put the regression tests below.

---

## 6. Top three fixes by risk reduction per unit of effort

1. **Make abort mean abort** (`browser_app.py:191,199-201` + `main.py:461`) — ~5 lines, removes the only
   path in this surface that writes files the user did not confirm. Closes SEC-1 and half of SEC-4.
2. **Stop feeding external strings to markup** (`main.py:352,358,489,494,222,317,322`, `_print_plan`) —
   `rich.markup.escape()` + C0/C1 stripping, ~10 lines + one regression test. Closes SEC-2 (crash, spoofing
   and the non-tty log-injection primitive in one shot).
3. **Sanitize display text at the model boundary** (`browser.py:_display_safe` on `name`/`description`/
   `division`) — ~6 lines, one unit test; closes SEC-3 and makes the TUI the second place (after C0) where
   "this string came from a file I do not control" is visibly handled.

Optional 4th, cheap: wrap `application.run()` (`browser_app.py:197`) in `try/except (EOFError, OSError,
RuntimeError) → BrowserCancelled` and pass `set_exception_handler=False` — turns SEC-5's stuck-loop into a
clean refusal.

---

## 7. Appendix — reproduction harness

All TUI evidence above came from one 40-line harness: `pty.openpty()` → set winsize via
`ioctl(TIOCSWINSZ)` → `Popen([sys.executable, child.py], stdin=slave, stdout=slave, stderr=slave)` where
`child.py` builds a `BrowserModel` with the payload rows and calls `run_browser(model)` → parent writes
keystroke bytes to the master fd, drains output, then asserts on `out.count(b"\x1b]0;pwned-title\x07")`
etc. Key sequences used: `\t` (toggle), `\x1b[B` (down), `\x1b` (escape), `\x03` (c-c), `\x01` (c-a),
`\x7f` (backspace), `\x15` (c-u), `\x1b[200~…\x1b[201~` (bracketed paste), `\x1bOP` (F1).
Environment: `.venv/bin/python`, prompt_toolkit 3.0.53, rich 15.0.0, Python 3.13.18, `TERM=xterm-256color`
(repeated with `TERM=dumb` and unset).

Suggested permanent tests (headless, no pty needed except the first):
- `render_screen` output for a payload row contains `^[` and never contains `\x1b` — covers F-1/F-2.
- `run_browser` in a pty: `TAB` + `ESC` must not return a non-empty selection — covers SEC-1.
- `install --agent '[/x]'` exits 1 with one line and no `MarkupError` — covers SEC-2.
- `build_rows` maps U+202E/U+200B to `\uXXXX` escapes — covers SEC-3.
