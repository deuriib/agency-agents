# Adversarial review — interactive TUI (`browser.py` / `browser_app.py` / D-001 C2)

**Board seat:** Refuter / assumption-stress.
**Subject:** `src/agency_agents/infrastructure/browser.py` (245 lines),
`src/agency_agents/infrastructure/browser_app.py` (201 lines),
`docs/dx/m7-tool-decisions.md` §D-001, `src/agency_agents/tests/integration/test_cli_tui.py`.
**Base commit:** `ae559df` (`feat(cli): complete the command surface …`), only commit touching `browser_app.py`.

**Overall verdict: Accept with caveats — 3 high findings must be resolved before merge.**
D-001's verdict is *not* voided and I am not asking for a re-score: the C2 anchor the
decision bought (75 = "headless run is possible but you hand-assemble the harness") is
exactly what the code supports today. My refutation is narrower and worse for the current
state: the repository **paid for that anchor and never spends it**, and the substitute
control it uses instead ("a human exercises it") has already shipped two user-visible
defects that a five-line headless test would have caught.

Findings by severity: **3 high · 5 medium · 3 low**.

---

## How this review was conducted

I did not review the claim, I tested it. Everything below is reproducible from
`project-tasks/tui-review/headless_probe.py` (committed next to this report):

```bash
.venv/bin/python project-tasks/tui-review/headless_probe.py          # key-by-key transcript
.venv/bin/python -m pytest project-tasks/tui-review/headless_probe.py -q \
    --cov=agency_agents.infrastructure.browser_app --cov-branch --cov-report=term-missing
```

Result: **9 headless tests drive the real `run_browser`**, and `browser_app.py` goes from
`line-rate="0.6364" branch-rate="0.6667"` (`coverage.xml`) to **83.2 % line / 83.3 %
branch — above the `--cov-fail-under=80` floor — with zero production changes.**
The production-side blocker is one line: `sys.stdin.isatty()` (`browser_app.py:166`), and it
is already mockable.

---

## Findings

### F-01 — HIGH — "the untestable part is the terminal loop" is false, and the docstring that says it is false propagates the error

**Assumption challenged.** `test_cli_tui.py:3-7`: *"`run_browser` itself opens a full-screen
application and is exercised by a human, not by pytest; … the view is thin enough that the
untestable part is the terminal loop and nothing else."*

**Evidence.**
- The terminal loop **is** drivable: `create_pipe_input()` + `DummyOutput()` +
  `create_app_session(...)` + two `mock.patch.object(sys, …isatty)` calls. No production
  edit. Transcript (probe, verbatim):

  ```
  '\t\r'      tab, enter        -> RETURN ['backend-architect']
  '\x01\r'    c-a, enter        -> RETURN ['backend-architect', 'growth-hacker']
  '\x1b'      esc only          -> CANCELLED
  '\t\x1b'    tab, esc          -> RETURN ['backend-architect']
  ```
- Coverage delta on `browser_app.py`: **63.6 % → 83.2 %**. The uncovered statements
  `173-201` — the key-binding closure, the `ACCEPT`/`ABORT` exit branch, the
  `application.run()` call, the `BrowserCancelled` branch and the return — are uncovered
  *by choice*, not by impossibility.
- D-001's own C2 anchors (`docs/dx/m7-tool-decisions.md:83`) make this the decisive point:
  `100 = documented headless harness … · 75 = headless run is possible but you hand-assemble
  the harness`. The verdict claims the 75 anchor; the repo uses the 0 anchor.
- Revisit trigger (b) (`m7-tool-decisions.md:246`) — *"browser tests need a pseudo-terminal"* —
  is not met, so nothing forces the issue. That is the trap: the condition was written to
  detect untestability, but the failure mode here is *untested*, not *untestable*.

**Recommended resolution: change.** Add the harness (≈40 lines, model below) to
`test_cli_tui.py`, and rewrite the module docstring to say what is true: the view is thin
*and* the loop is headlessly asserted. Keep the 75 anchor honest by noting that the harness
is hand-assembled — that is exactly the anchor's wording and it is defensible; "a human
exercises it" is not.

**What a harness needs (answer to the brief's question 1), none of which `run_browser` gives
cleanly today):
1. a way past `sys.stdin.isatty()` — mockable today, but only because it reads the module
   global; a `assume_tty: bool = False` or an injected `input`/`output` pair would remove the
   monkeypatch entirely;
2. an injected input stream — `create_app_session(input=…, output=DummyOutput())` works
   *around* `run_browser`, precisely because `Application` is constructed without
   `input=`/`output=` (`browser_app.py:190-196`);
3. an observable outcome — already present (return value / `BrowserCancelled`), so no
   production API change is required;
4. optional: a handle on the `Application` to assert on app state. Not needed, because
   `render_screen` is pure and the model is inspectable after the run — which is the one
   genuinely strong part of this design.

---

### F-02 — HIGH — the arrow keys and PageUp/PageDown are dead, and the on-screen help advertises them

**Assumption challenged.** "The view is a thin pass-through; if the model is right, the
product is right." It is not a pass-through: `_NAMED_KEYS` is a *lossy translation layer*
and nothing tests it.

**Evidence.**
- `browser_app.py:149` renders `" up/down move  tab toggle …"` — the first thing a user tries.
- `_NAMED_KEYS` (`browser_app.py:32-50`) contains **no escape sequences** for arrows or
  paging. `Keys.Any` delivers those keys as their raw bytes: I verified with an instrumented
  `Application` that `Keys.Any` receives `'\x1b[B'` (Down), `'\x1b[A'` (Up), `'\x1b[6~'`
  (PageDown), `'\x1b[H'`, `'\x1b[3~'`, `'\x1bOP'`.
- `apply_key` then hits `len(key) == 1` (`browser.py:242`) with a 3-char string, and
  returns `CONTINUE` — a silent no-op. Confirmed end to end:
  `'\x1b[B\r'` → `RETURN [] , cursor=0`; `'\x1b[6~\r'` → `RETURN [], cursor=0`.
  Only `c-p`/`c-n`/`c-b`/`c-f` move the cursor.
- The unit suite *blesses* this: `test_browser.py:313-316` asserts
  `apply_key(model, "down")` moves the cursor — a key string the view can never produce —
  and `test_browser.py:394` asserts *"unknown named keys are ignored"* using `"f13"`. That
  test is the regression guard for the bug: `'\x1b[B'` takes the same "unknown, ignore"
  path.
- This is not a theoretical gap. It is a defect a human should have caught and did not,
  which is the empirical refutation of the "human tests it" position. `--cov-branch` and
  100 % model coverage both stay green while the headline navigation key does nothing.

**Recommended resolution: change.** Either bind `Keys.Up/Down/PageUp/PageDown` in
`browser_app.py` explicitly, or add `"\x1b[A" / "\x1b[B" / "\x1b[5~" / "\x1b[6~"` (and
`\x1bOA`/`\x1bOB` application-mode variants) to `_NAMED_KEYS`; then assert the *bytes* in the
headless harness, not the invented names. Change the help line to state the binding that
actually exists until the fix lands, and delete the `"f13"` test's false reassurance (or
re-point it at a genuinely unbound key with an explicit comment that escape sequences are
handled in the view).

---

### F-03 — HIGH — Esc and Ctrl-C *install*; the help says "esc cancel"; no confirmation exists anywhere

**Assumption challenged.** *"Aborting with a selection returns it (deliberate work shouldn't
be discarded)."* The rationale is defensible in the abstract. The implementation turns the
two universal cancel gestures into write commands, in a programme whose D-001 exit path
promises a safety net that is not in the code.

**Evidence.**
- `run_browser:199-201`: only `outcome == ABORT and not model.selected` raises. Any ABORT
  *with* a selection falls through to `return model.selection()`.
- `browser.py:191`: `_ABORT = {"escape", "c-c", "c-q"}` — so **Ctrl-C installs too**. Probe:
  `'\t\x03'` → `RETURN ['backend-architect']`.
- `browser_app.py:150`: the rendered help reads `"enter install  esc cancel"`. That string is
  false whenever anything is selected. The screen tells the user the opposite of what the
  key does.
- No confirmation step exists: `grep -rn "confirm(" src/agency_agents` returns only the
  dialog's prose `"enter confirms"`. `_browse_and_install` (`cli/main.py:461-514`) goes
  straight from `run_browser` to `_install_agents`. The exit-path table
  (`m7-tool-decisions.md:245`) claims *"`_ask` … and `confirm()` survive as the final explicit
  yes/no"* — that is not true of the shipped tree, so the record's safety argument is
  fiction.
- Worst case, reproduced: select row `a-0`, filter to `a-4` (so `a-0` is off-screen), press
  Esc → `RETURN ['a-0']`. The user cancelled while looking at a row they never selected, and
  a different agent was installed.
- Inconsistency in the same breath: `run_browser`'s own docstring says it raises
  `BrowserCancelled` *"when the user aborts"* — but it only raises when the abort is
  *empty-handed*. Two behaviours, one word, one key.

**Recommended resolution: change.** Make the destructive key unambiguous — Esc/Ctrl-C always
`BrowserCancelled` (nothing written), Enter always accepts — and, because `confirm()` no
longer exists, either reinstate a final yes/no or delete the claim from the D-001 exit-path
row. If the team keeps "abort returns work", then: (a) the help line must read
`enter/esc install` — the current text is a defect either way — (b) Ctrl-C must stay a true
cancel (it is `SIGINT` semantics; a user who hits Ctrl-C does not consent to writing files),
and (c) a final confirm should absorb the ambiguity.

---

### F-04 — MEDIUM — "detection is the only safe default" is not scope-aware, and one stray dotdir converts it into a hard failure

**Assumption challenged.** `_detected_tools` (`cli/main.py:532-546`) treats "a directory
exists under `$HOME`" as a safe default for *both* scopes, then the caller hard-fails on any
mismatch.

**Evidence.**
- Detection reads `Path.home()` only (`cli/main.py:543`) while `--scope project` writes into
  cwd. A project-scoped install is therefore authorised by a HOME signal.
- Four tools have no project destination — `osaurus`, `kimi`, `openclaw`, `hermes`
  (`src/agency_agents/data/tools.json`, `dest.project: []`). A single `~/.osaurus` makes
  `tui --scope project` exit 1 for a detected set that otherwise supports project
  (`cli/main.py:497-505`, all-or-nothing `raise typer.Exit(code=1)`).
- The flag path already solved this differently: `install` warns and *skips*
  (`cli/main.py:365-377`, `"⚠ Skipping tools with no {scope} destination"`, then filters).
  So the browser path and the flag path disagree about the same condition — a direct
  violation of D-001 MC2's spirit ("one meaning") even though `InstallSelection` is shared.

**Recommended resolution: change.** Filter the detected set by the requested scope before the
hard check, or reuse the skip-with-warning branch. Add a test with a detected user-only tool
and `--scope project`.

---

### F-05 — MEDIUM — the detection default's premise is partly empty, and its own docstring contradicts the code

**Assumption challenged.** *"Detection is the only safe default"* — and, in the function
docstring, *"an empty result is an error rather than a silent no-op"*.

**Evidence.**
- `aider` and `kimi` declare `detect.dirs: []` — **they can never be detected** (§
  `tools.json`). A machine with only Aider or Kimi installed always takes the dialog path.
- The docstring says an empty result is an error; the code (`cli/main.py:474-486`) falls back
  to `choose_tools(...)` and only errors if *that* is cancelled. Acceptable behaviour, wrong
  documentation.
- `choose_tools`'s failure paths (`browser_app.py:74-98`: the `except (EOFError,
  KeyboardInterrupt)` and the message assembly) are **uncovered** — the only tests inject a
  fake `choose_tools` (`test_cli_tui.py:253-268`). The real "no terminal to ask in" behaviour
  of `checkboxlist_dialog` is never exercised, so the claim "*a machine with no detected tool
  can still install*" rests on an untested branch.

**Accept-with-note** on the default itself (it is defensible); **change** the docstring, and
add one test that pushes a non-tty stdin through the real `choose_tools` to prove the
`BrowserCancelled` message surfaces instead of a traceback.

---

### F-06 — MEDIUM — the layout is 27 lines tall regardless of terminal size; the status line gets clipped on a 24-row terminal

**Assumption challenged.** *"The renderer is a pure function of the model, so the layout can
be asserted by reading strings."* It can — but the assertion nobody wrote is the one that
matters: whether the screen fits.

**Evidence.** `LIST_HEIGHT = 15` (`browser_app.py:28`) is a constant; `render_screen` always
emits `1 title + 1 filter + 1 rule + 15 rows + 1 rule + 5 detail + 1 rule + 1 status +
1 help = 27` lines (measured). On the standard 80×24 terminal — and on the 80×24 simulated
size D-001 itself cites for textual — the bottom three lines are clipped: the rule, the
**status line** (`"N/300 shown | M selected | …"`, `browser.py:160-166`) and the help line.
The status line is the only place a multi-select tool reports how much is selected; F-08
makes that line load-bearing. Long descriptions wrap and make it worse.

**Recommended resolution: change.** Clamp the window from
`application.output.get_size().rows` (or at minimum assert `len(rendered.splitlines()) <=
LIST_HEIGHT + 12` and, better, that the status line survives rendering at 80×24).

---

### F-07 — MEDIUM — multi-word filters match nothing, silently

**Assumption challenged.** *"Substring over four fields is enough; the roster is small."*
Performance is fine (measured: 300 rows × 195-char descriptions → **0.45 ms** per
keystroke-plus-render, `visible()` called **3×** per render, no pathological behaviour, no
`O(n²)`). The refutation is semantic, not computational.

**Evidence.** `BrowserRow.matches` (`browser.py:33-40`) is a single contiguous substring test,
so `"designs platform"` / `"api designs"` return 0 rows while each word alone matches ~all.
Measured: `query='designs api platform'` → **0 rows**; `query='agent-1'` → 100 rows. The
empty state renders `"no agent matches this filter"` (`browser_app.py:139`) — a user who
typed two true words is told nothing matches, with no hint that spaces are literal.

**Recommended resolution:** accept-with-note if the intent is literal substring, *or* split
the query on whitespace and require every token to match (AND). Cheap either way; the
current behaviour is the one users will misread as a broken filter.

---

### F-08 — MEDIUM — `c-a` is additive and filter-scoped while its inverse `c-x` is global

**Assumption challenged.** *"`select_all_visible` is fine because its name says 'visible'."*
The name is accurate; the *pairing* is not.

**Evidence.**
- `browser.py:123-130`: additive only, never deselects, and with an empty filter "visible"
  means **the whole roster** — measured 300 rows; Enter then installs all 300 into every
  detected tool (a capacity warning fires per tool, `cli/main.py:513-514`, which is the one
  mitigation).
- `browser.py:132-133`: `clear_selection` clears **everything**, including rows the filter
  hid. So `c-a` is scoped and `c-x` is global: an asymmetric pair with no on-screen cue
  beyond the status line — the line F-06 says can be clipped.
- Selections persist across filter changes and are only visible via the `[x]` marks of rows
  currently rendered; measured: select `a-0`, filter to `a-4`, Enter → installs `['a-0']`.

**Recommended resolution: change** (small): make `c-a` a toggle over visible rows
("select all visible" / "deselect all visible") so it has an in-scope inverse, and mention
the hidden-selection count in the help line. If unchanged, at least add the `BrowserModel`
test that asserts the scoped/global asymmetry so it is a decision rather than an accident.

---

### F-09 — LOW — a pasted or Alt-composed ESC cancels the browser and discards the filter

**Evidence.** `\x1b` maps to `ABORT` (`browser_app.py:35`); probe: `'\x1bg\r'` (Esc then `g`
within the escape window, i.e. Alt-g or a paste beginning with ESC) → `CANCELLED`, query
truncated back to `''`. Terminals that emit Alt as ESC-prefix, and any paste containing ESC,
become a cancel. Low because it needs a specific input; worth a note because it is the same
class of defect as F-02 — the `_NAMED_KEYS` layer has no notion of escape *sequences*.

**Recommended resolution:** accept-with-note (documented escape-timeout behaviour), folded
into the F-02 fix if `_NAMED_KEYS` is reworked.

---

### F-10 — LOW — the "no silent no-op" invariant is enforced only at the tty boundary

**Assumption challenged.** `browser_app.py:163-165`: *"Without this guard the application
draws into nothing, exits on EOF and reports 'nothing selected' with status 0 — a silent
no-op inside a script that believes it installed something."*

**Evidence.** The comment is accurate for the case it addresses, and the guard does hold:
`test_tui_refuses_to_run_without_a_terminal` exercises it for real. But the same "no outcome"
state is reachable one step later: if `application.run()` ever returns without an ACCEPT or
ABORT, `outcome.get(...) is None` → `run_browser` returns `model.selection()` and the CLI
prints `"Nothing selected — nothing installed."` with exit 0. On EOF prompt-toolkit raises
`EOFError` out of `run()` instead (verified), and `_browse_and_install` catches only
`BrowserCancelled` (`cli/main.py:465-469`) — so a hung-up terminal becomes a traceback, not
a silent success. Neither outcome is dangerous; both are unpolished.

**Recommended resolution:** treat a missing outcome as `BrowserCancelled`, and catch
`EOFError` around `application.run()` in the same place. Two lines, removes a whole class of
"what just happened" reports.

---

### F-11 — LOW — `c-q` in `_ABORT` is usually unreachable

**Evidence.** `browser.py:191` includes `"c-q"`; XON/XOFF software flow control consumes
Ctrl-Q in most terminals before the app sees it. Harmless dead binding, but it means the help
line's `esc cancel` is the only cancel the user is told about — see F-03.

**Recommended resolution:** accept-with-note or drop it.

---

## Assumptions I stressed that held up (accept-with-note)

These were on the brief's list and are **not** defects; recording them so the next reviewer
does not re-litigate them.

1. **Detection order/overlap (brief item 3).** Verified against `src/agency_agents/data/tools.json`
   (19 tools): no two tools share a `detect.dirs` entry, and no detect dir is a path prefix of
   another (`.gemini/agents` vs `.gemini/config/agents` are siblings, not a capture). No
   ordering hazard exists; `_detected_tools` also returns `sorted(...)`, so the result is
   deterministic. Two real notes rather than defects: `copilot` detects `.github` in `$HOME`
   and writes to *two* destinations (`.copilot/agents/` and `.github/agents/`), so a
   `~/.github` dotfiles directory silently opts Copilot in; and no destination path is
   written by two different tools (the only `dest` collisions are a tool's own user/project
   pair).
2. **Filter performance (brief item 4).** Measured: 0.45 ms per keystroke + full render at
   the real roster size (~300 agents); `visible()` is called 3× per render, not per row.
   Nothing pathological, no caching needed.
3. **Selection reproducibility.** `selection()` (`browser.py:138-140`) returns roster order,
   so the plan is stable regardless of the order rows were clicked. Good.
4. **Sort stability.** `build_rows` sorts on `(division, name.lower(), slug)`, so slug breaks
   name ties — the docstring's determinism claim holds.
5. **Test-only concerns** highlighted in the brief and confirmed as *real* but *not*
   independent findings: `render_screen` is genuinely pure and well covered; the coverage
   floor is genuinely met; the `fake_browser` monkeypatch in `test_cli_tui.py` is a legitimate
   seam, not a vacuous test — it just tests everything except the thing F-01–F-03 live in.

---

## Decision recommendation

**Accept with caveats.** Directionally this is the right design — pure model, pure renderer,
thin view, `prompt-toolkit` already in the audited set; D-001's arithmetic and its C2 = 75
anchor remain correct and nothing here justifies reopening the toolkit choice.

But the review's central premise must be corrected in the record, not just in the code:

- **F-01** falsifies the sentence the whole test strategy rests on, with a 40-line counter-example.
- **F-02** shows the manual-testing substitute has already failed once (headline navigation key dead, help text lying, unit test blessing it).
- **F-03** shows it has failed a second time, in the direction that writes files: `esc cancel` installs, `Ctrl-C` installs, and the "final explicit yes/no" the D-001 exit path promises does not exist in the tree.

**Falsifiable exit criterion for the board** — I would drop my objection entirely if, before
merge, `pytest` contains: (a) a headless `run_browser` test that feeds raw `'\x1b[B'` and
`'\t\r'` bytes and asserts on the returned list, (b) a headless test asserting Esc-with-a-
selection does *not* write (or that the help text matches whatever it does), and (c) a
`browser_app.py` line rate at or above the 80 % floor from *these* tests rather than from
imports. All three are achievable with the file already committed beside this report.

---

## Appendix A — reproduced transcript

```
keys         meaning                  -> outcome                                          [state after]
'\t\r'       tab, enter               -> RETURN ['backend-architect']                     query='' cursor=0
'\x01\r'     c-a, enter               -> RETURN ['backend-architect', 'growth-hacker']    query='' cursor=0
'\t\x03'     tab, ctrl-c              -> RETURN ['backend-architect']                     query='' cursor=0
'\t\x1b'     tab, esc                -> RETURN ['backend-architect']                     query='' cursor=0
'\x1b'       esc only                 -> CANCELLED                                        query='' cursor=0
'\x1b[B\r'   down-arrow, enter        -> RETURN []                                        query='' cursor=0   <- arrow dead
'\x1b[A\t\r' up-arrow, tab, enter     -> RETURN ['backend-architect']                     query='' cursor=0   <- arrow dead
'\x1b[6~\r'  page-down, enter         -> RETURN []                                        query='' cursor=0   <- paging dead
'\x1bg\r'    alt-g (esc then g)       -> CANCELLED                                        query=''            <- ESC-prefix cancels
```

Key-name delivery, instrumented on a bare `Application` with only `Keys.Any` bound:

```
down      -> ["'\\x1b[B'"]
up        -> ["'\\x1b[A'"]
pagedown  -> ["'\\x1b[6~'"]
home      -> ["'\\x1b[H'"]
delete    -> ["'\\x1b[3~'"]
f1        -> ["'\\x1bOP'"]
tab       -> ["'\\t'"]
```

Layout measurement at `LIST_HEIGHT = 15`: `render_screen` emits **27 lines** for a full
window; an 80×24 terminal clips 3 — the trailing rule, the status line, and the help line.

## Appendix B — resolution checklist

| # | Severity | Resolution | Owner-visible artefact |
| --- | --- | --- | --- |
| F-01 | high | change: add headless harness; fix `test_cli_tui.py:1-8` docstring | `tests/integration/test_cli_tui.py` |
| F-02 | high | change: bind arrow/page keys or extend `_NAMED_KEYS`; drop the `"f13"` false comfort | `browser_app.py:32-50`, `browser.py:182-185`, `test_browser.py:394` |
| F-03 | high | change: Esc/Ctrl-C cancel unconditionally, or relabel help + restore a confirm; fix `m7-tool-decisions.md:245` | `browser_app.py:147-151,199-201`, `docs/dx/m7-tool-decisions.md` |
| F-04 | medium | change: scope-filter detected tools, reuse `install`'s skip branch | `cli/main.py:497-505` |
| F-05 | medium | note + docstring fix + one real `choose_tools` test | `cli/main.py:532-546`, `browser_app.py:64-98` |
| F-06 | medium | change: size the window from the terminal, assert the line budget | `browser_app.py:28,101-124` |
| F-07 | medium | note *or* tokenise the query on whitespace | `browser.py:33-40` |
| F-08 | medium | change: make `c-a` a visible-scope toggle, or document + test the asymmetry | `browser.py:123-133` |
| F-09 | low | note (fold into F-02 if `_NAMED_KEYS` is reworked) | `browser_app.py:35` |
| F-10 | low | change: missing outcome ⇒ cancel; catch `EOFError` | `browser_app.py:197-201`, `cli/main.py:465` |
| F-11 | low | note or drop `c-q` | `browser.py:191` |
