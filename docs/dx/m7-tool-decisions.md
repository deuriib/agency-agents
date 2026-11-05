# M7 tool decisions — agency-agents CLI

M7 is defined by `strategy/runbooks/scenario-developer-experience-platform.md`
as: *a build-vs-adopt decision that names at least three weighted criteria,
scores at least two candidates against them, and records a verdict plus an exit
path. Anything less is a fail, not a partial pass.*

This file is the M7 record for the two tool decisions in the interactive TUI
work: **D-001** (the toolkit that renders the agent browser, GitHub issue #13)
and **D-002** (how runbooks reach a developer's machine, GitHub issue #14).

## Provenance and ordering

**Author:** the Tool Evaluator agent. This is the authoritative record and it
carries the verdict.

**Predecessor:** an Agents Orchestrator draft of this file existed on disk. It
was produced while the Tool Evaluator was believed unavailable, and it was
labelled a draft. It is not an authority this document inherits; it is an
artefact this document audits. Where independent scoring agreed with it, that is
stated. Where it did not, the change and its reason are stated in
[Changes from the orchestrator draft](#changes-from-the-orchestrator-draft),
including the arithmetic errors found in its D-002 tables.

**G3 clause 3.3 — criteria precede scoring.** Criteria, weights, and the
scoring anchors for every criterion were written before any candidate was
scored, and they are printed in that order in each decision below. The order is
the evidence trail: a criterion cannot have been reverse-engineered from a score
it appears above, and every score in this file is reproducible from the anchor
text that sits above it. If a criterion is ever added to a decision after this
date it must appear with its weight, its anchors, and an explicit
`AMENDED — added post-scoring` marker. There are no amended criteria in this
document.

**How to check the arithmetic.** Each decision prints the per-criterion product
(`score × weight`) so a reader can sum the column by hand and get the printed
total. Scores are 0–100 integers; weights are percentages that sum to 100.

**What was verified, and against what.** Capability claims are not taken from
memory or from vendor marketing. Every claim that moved a score is either (a) an
observation from this repository or its resolved lock, or (b) a statement in
current upstream documentation quoted in the [Evidence log](#evidence-log).
Claims that could not be verified were dropped rather than softened.

---

## D-001 — TUI framework for the interactive agent browser (GitHub issue #13)

**Question:** which toolkit renders the interactive agent browser — a
searchable agent list, an agent detail view, and multi-select install — given
that the browser is a *view* over the same selection that `install`'s flags
express?

### Binding constraints

These are established facts about this repository, not preferences. They bound
the decision before any candidate is named.

| # | Constraint | Established by |
| --- | --- | --- |
| K1 | Runtime dependencies are deliberately tiny and frozen: `prompt-toolkit`, `pydantic`, `rich`, `typer` | `pyproject.toml` |
| K2 | `prompt-toolkit` is already a direct runtime dependency and already drives `TUIWizard` (`from prompt_toolkit import prompt`, `WordCompleter`) | `src/agency_agents/infrastructure/tui.py` |
| K3 | The audited runtime set is 15 distributions, and CI audits **runtime only**: `uv export --no-dev --no-emit-project` → `pip-audit --strict -r` | `.github/workflows/ci.yml`, `security` job |
| K4 | CI enforces branch coverage with a hard floor: `--cov=agency_agents --cov-branch --cov-fail-under=80` | `.github/workflows/ci.yml`, `test` job |
| K5 | The browser must reuse the selection semantics `install` already has (`--tool`, `--division`, `--agent`, `--agents-file`, `--dry-run`, `--scope`, `--list`) rather than invent parallel ones | `src/agency_agents/cli/main.py` |
| K6 | Windows is a supported platform: the CLI reconfigures stdout/stderr to UTF-8 specifically to survive `cp1252` consoles | `src/agency_agents/cli/main.py` |

K5 has a consequence worth stating plainly, because it decides the architecture
regardless of which toolkit wins: the browse/search/select state is already a
pure data problem (`InstallSelection` is `tools` + `scope` + `divisions`, and
`select_agents` already resolves a selection from slugs). Whatever renders it
should be a thin view over that model. That is an execution requirement, not a
differentiator — see [Verdict](#d-001-verdict).

### Criteria (written before scoring)

Weights sum to 100. "Anchors" are the fixed scale that makes each score
checkable and prevents post-hoc score drift.

| # | Criterion | Weight | Why this weight | Scoring anchors |
| --- | --- | --- | --- | --- |
| C1 | Audited runtime dependency set after the decision | 25% | CI fails on a CVE in any audited distribution, the repo's product is markdown files, and a runtime dep can only be removed through an M7 exit path — so this cost is permanent in a way UX polish is not. At 25% it can decide a close call but cannot decide it alone | 100 = no change to the 15-distribution set · 75 = +1 · 50 = +2–3 · 25 = +4 or more, **or** the decision leaves two UI frameworks in the runtime set · 0 = requires a native/system dependency |
| C2 | Non-TTY testability under the 80% branch-coverage floor | 25% | The coverage floor is a pipeline gate, not a preference: an untestable view layer gets covered by vacuous tests or the build fails. Weighted equal to C1 because both are hard CI constraints | 100 = documented headless harness that drives keys and asserts on application state with no terminal · 75 = headless run is possible but you hand-assemble the harness and only reach the application layer · 50 = needs a pseudo-terminal · 25 = needs a real interactive terminal |
| C3 | Keyboard-driven browse UX for list + search + detail + multi-select | 20% | The feature exists to stop users memorising flags; if it is unpleasant to drive from the keyboard it has no reason to exist. Below C1/C2 because it is recoverable by better layout work, whereas a dependency or an untestable layer is not | 100 = focus, scroll, filter, and selection all provided with sane defaults · 75 = full-screen keys and filtering available, layout assembled by us · 50 = numbered prompts only · 25 = type-ahead only |
| C4 | Out-of-the-box widgets for list + filter + checkbox selection | 15% | Bespoke widget code is code we own and test forever, so shipped components are real value — but only after the two hard gates above | 100 = list, filter, and checkbox selection all shipped · 60 = list widgets and selection dialogs shipped, filter wiring is ours · 25 = text primitives only · 10 = no UI widgets at all |
| C5 | Maintenance surface and churn risk | 15% | A UI library's upgrade cadence becomes our re-validation cadence; a repo that pins with `uv sync --frozen` still eats the cost whenever it chooses to move | 100 = stdlib, guaranteed present · 80 = mature and slow-moving, wide dependant base · 65 = active development with frequent major releases · 30 = we own the code |

### Candidates

Four candidates. Three adopt, one build, because M7 is a build-vs-adopt
decision and a record with no genuine build option does not answer the question
it was asked.

| Candidate | What it is |
| --- | --- |
| **prompt-toolkit** | The already-installed toolkit (K2). A full-screen `Application` with `Layout`, key bindings, buffers and shipped dialogs |
| **textual** | A CSS-styled TUI framework built on `rich`, with its own widget set and test harness |
| **stdlib `curses`** | No dependency at all; the terminal layer every POSIX Python ships |
| **rich-only, hand-built** | The build option: render with `rich` (already installed) and own the key handling, redraw and scroll state |

Verified capability notes per candidate (sources in the evidence log):

- **prompt-toolkit 3.0.53.** `Application(full_screen=True)` with `Layout`,
  `HSplit`/`VSplit`, `Window`, `FloatContainer`, `ScrollablePane`, `KeyBindings`,
  `BufferControl`, `FormattedTextControl`, and `HighlightSearchProcessor` are
  documented and installed. Shipped widgets include `Dialog`, `CheckboxList`,
  `RadioList`, `Button`, `Frame`, `TextArea`, `SearchToolbar`, `MenuContainer`
  and `MenuItem`; `prompt_toolkit.shortcuts` ships `checkboxlist_dialog`,
  `radiolist_dialog`, `button_dialog`, `yes_no_dialog`, `input_dialog`,
  `message_dialog` and `progress_dialog`. So multi-select from a list **is**
  shipped. What is *not* shipped is incremental fuzzy filtering over a
  programmatic list — that wiring is ours. For C2: `Application.__init__` accepts
  `input=` and `output=`, and `prompt_toolkit.input.create_pipe_input()` plus
  `prompt_toolkit.output.DummyOutput()` exist and are public, so a headless run
  is possible; but there is no documented test harness or pilot object, so the
  harness is hand-assembled.
- **textual 8.2.8.** Base requirements are `markdown-it-py[linkify]>=2.1.0`,
  `mdit-py-plugins`, `platformdirs>=3.6.0,<5`, `pygments>=2.19.2,<3` and
  `rich>=14.2.0`; `requires_python` is `>=3.9,<4.0`; wheels are pure Python
  (`py3-none-any`). Of those, `markdown-it-py`, `mdurl`, `pygments` and `rich`
  are **already** in this project's lock at compatible versions
  (markdown-it-py 4.2.0, pygments 2.21.0, rich 15.0.0), so no version bump is
  forced. The genuinely new distributions are `textual`, `mdit-py-plugins`,
  `platformdirs` and `linkify-it-py`: **four**. `App.run_test()` is documented as
  an async context manager returning a `Pilot` that drives `press()`, `click()`
  and `pause()` headlessly at a default simulated size of 80×24.
- **stdlib `curses`.** Python's own documentation states: *"The Windows version
  of Python doesn't include the `curses` module. The third-party `windows-curses`
  package provides the same interface on Windows."* Given K6, that is a native
  third-party dependency on a supported platform, not a zero-dependency option.
  The same documentation states: *"curses doesn't provide many user-interface
  concepts such as buttons, checkboxes, or dialogs."*
- **rich-only, hand-built.** `rich` renders `Table`, `Panel` and `Live`, and it
  is already a dependency — but it provides no input handling, so the key loop,
  focus model, filter buffer and scroll state are ours to write and own.

### Scores

| Candidate | C1 (25) | C2 (25) | C3 (20) | C4 (15) | C5 (15) | Weighted |
| --- | --- | --- | --- | --- | --- | --- |
| **prompt-toolkit** | 100 | 75 | 80 | 65 | 80 | **81.5** |
| textual | 25 | 100 | 100 | 100 | 65 | **76.0** |
| rich-only, hand-built | 100 | 80 | 25 | 25 | 30 | **58.3** |
| stdlib `curses` | 0 | 25 | 45 | 10 | 85 | **29.5** |

### Arithmetic

```text
prompt-toolkit   C1 100 × 0.25 = 25.00
                 C2  75 × 0.25 = 18.75
                 C3  80 × 0.20 = 16.00
                 C4  65 × 0.15 =  9.75
                 C5  80 × 0.15 = 12.00
                 ----------------------  = 81.50

textual          C1  25 × 0.25 =  6.25
                 C2 100 × 0.25 = 25.00
                 C3 100 × 0.20 = 20.00
                 C4 100 × 0.15 = 15.00
                 C5  65 × 0.15 =  9.75
                 ----------------------  = 76.00

rich-only build  C1 100 × 0.25 = 25.00
                 C2  80 × 0.25 = 20.00
                 C3  25 × 0.20 =  5.00
                 C4  25 × 0.15 =  3.75
                 C5  30 × 0.15 =  4.50
                 ----------------------  = 58.25

stdlib curses    C1   0 × 0.25 =  0.00
                 C2  25 × 0.25 =  6.25
                 C3  45 × 0.20 =  9.00
                 C4  10 × 0.15 =  1.50
                 C5  85 × 0.15 = 12.75
                 ----------------------  = 29.50
```

### Sensitivity — this verdict is not weight-proof

The margin over textual is 5.5 points, and it is carried by C1 and C5. Holding
the other four criteria in the ratio 25 : 20 : 15 : 15 and varying only the C1
weight `w`:

```text
pt(w)       = w + (100 − w)/75 × 56.5      ← 56.5 = 18.75 + 16.00 + 9.75 + 12.00
textual(w)  = 0.25w + (100 − w)/75 × 69.75 ← 69.75 = 25.00 + 20.00 + 15.00 + 9.75
equal at    w ≈ 19.1
```

So: **the verdict holds for any C1 weight at or above ~19%, and textual overtakes
it below that.** The record sets C1 at 25% rather than higher because a single
criterion should not decide a four-candidate field, and rather than lower because
the audited dependency set is a CI gate rather than a taste. A reviewer who
believes +4 audited distributions and a second UI framework in the runtime set
are cheap should say so explicitly and re-weight C1 to 15%; that reviewer is not
wrong about the arithmetic, only about the price.

### D-001 Verdict

**Adopt prompt-toolkit. Weighted score 81.5 / 100. The draft's verdict is
upheld; its score and criteria are not.** (The draft scored the same winner at
87.5 with different weights — see the changes section.)

Reasons, in the order the weights applied:

1. **C1.** It is already installed, so the audited runtime set stays at 15
   distributions. textual would take it to 19 and would move `platformdirs` from
   dev-only into the audited runtime set — today `platformdirs` is reachable in
   `uv.lock` only through `pip-audit` and `virtualenv`, neither of which is
   exported by the `security` job. Adopting textual would also leave two UI
   frameworks in the runtime set, because `TUIWizard` keeps using
   `prompt-toolkit.prompt` unless the wizard is rewritten in the same change.
2. **C2.** Headless testing is possible without a terminal
   (`create_pipe_input()` + `DummyOutput()`), which is what keeps C2 above the
   50-anchor "needs a pseudo-terminal". It is not textual's documented
   `run_test()`/`Pilot`, and the honest score says so.
3. **C3/C4.** Full-screen layout, key bindings, `SearchToolbar` and shipped
   checkbox dialogs cover the feature. What is left — wiring incremental
   filtering to a dialog — is a small amount of code in a layer we would have to
   test anyway.

**Mandatory conditions of adoption.** Without these the verdict is void and the
decision returns to the table:

- **MC1 — the view is thin and the model is pure.** All browse/search/select
  state lives in an importable model that takes no terminal. The
  `prompt_toolkit.Application` is a view over it. Every behaviour the feature
  claims (filter, move, toggle, confirm, cancel) is a test against the model.
  This applies to *any* winner; it is not a justification for this one.
- **MC2 — the selection model stays flag-identical (K5).** The model's output is
  the same `InstallSelection` shape `install` already consumes, so
  `--tool`/`--division`/`--agent`/`--agents-file`/`--dry-run`/`--scope` keep one
  meaning. A browser that can express a selection the flags cannot (or vice
  versa) fails this condition.
- **MC3 — no new runtime distribution.** If the browser cannot be built without
  adding one, this decision is reopened before the code is merged, not after.

### D-001 Exit path

| Field | Value |
| --- | --- |
| Predecessor | The numbered-list selection path in `TUIWizard`: `select_tools`, `select_scope`, `select_divisions`, `_ask_choice`, `_resolve_multi`, and the `rich` `Table`/`Panel` rendering inside them. There is no earlier browser — the browser has no predecessor beyond this |
| Removal date for the predecessor | Phase 3 of `scenario-developer-experience-platform`, in the same change that lands the browser. Per G3 clause 3.2 the deletion is part of that commit, not a follow-up ticket: the numbered-list methods do not survive the browser |
| What must be kept | `WizardCancelled` and the `InstallSelection` shape are retained and become the pure model under MC1/MC2 — they are the contract `install` already depends on. `_ask` (a plain `prompt_toolkit.prompt`) and `confirm()` survive as the final explicit yes/no, which is also why `prompt-toolkit` remains in the runtime set whatever renders the list: choosing another toolkit adds a framework, it does not swap one out |
| Revisit trigger | Any **one** of: (a) the browser needs panes, mouse, or scrollable rich-markup regions beyond a three-region layout; (b) browser tests need a pseudo-terminal, or model-level browser coverage falls below the 80% floor; (c) a tool consumer needs the selection UI rendered in a non-terminal surface; (d) `pip-audit --strict` fails on `prompt-toolkit` and the only fix requires an API change that breaks `Application` usage |
| Revisit date | Scheduled at G5 handover + 90 days; then annually alongside the dependency-audit review. Hard backstop: no later than 12 months after the Phase 3 merge, whether or not anyone remembers |
| Migration cost if we switch | Contained. One module (`src/agency_agents/infrastructure/tui.py`) holds the view; the model, the selection resolution in `core/selection.py`, the installer and the manifest are untouched by the swap. Estimated ≤ 2 engineer-days for textual, of which the dependency review is most of it |
| Reversibility | **High.** Behind one command path, touching no renderer, installer, or manifest contract, with no data migration |

---

## D-002 — Runbook installation surface (GitHub issue #14)

**Question:** how do runbooks reach a developer's machine — copy a directory
from the repo, extend `install` with a `--runbook` selector, or add a
`runbooks` subcommand group?

### Binding constraints

| # | Constraint | Established by |
| --- | --- | --- |
| L1 | Runbooks are already a first-class catalog object, not loose files: `CatalogManager.load_runbooks()` parses `strategy/runbooks.json` into `RunbookDefinition` (`slug`, `title`, `mode`, `duration`, `summary`, `doc`, `roster`) | `infrastructure/catalog.py` |
| L2 | The surface is large and non-trivial: **42 runbooks** and **687** roster agent references | `strategy/runbooks.json` |
| L3 | Runbook consistency is already linted and fatal: `lint` runs `check_runbooks_consistency()` and exits 1 on failure | `cli/main.py`, `core/validator.py` |
| L4 | A runbook roster is a list of agent *slugs*, and `select_agents(agent_ids=...)` already resolves slugs (also display name, file stem, and the `agency-`-stripped alias) | `infrastructure/catalog.py`, `core/selection.py` |
| L5 | `install` owns the semantics that must be inherited: `--tool`, `--scope`, `--dry-run`, `--list`, `--parallel/--jobs`, the per-tool capacity warning (`opencode` ~119 agents), and the aggregate failure exit code | `cli/main.py` |
| L6 | `install` is already a 10-flag flat command, and the CLI has no subcommand groups at all | `cli/main.py` |

### Criteria (written before scoring)

| # | Criterion | Weight | Why this weight | Scoring anchors |
| --- | --- | --- | --- | --- |
| C1 | Discoverable without already knowing the files exist | 25% | This *is* the complaint in #14. A surface nobody finds leaves the original problem exactly where it was, so it carries the joint-highest weight | 100 = its own top-level verb in `agency-agents --help` · 70 = named in the `--help` of the command the user already runs, plus a listing surface · 30 = README prose only · 0 = nowhere |
| C2 | One install verb, one mental model | 25% | A second way to install is how CLIs rot, and G3 clause 3.2 makes a superseded path a removal obligation. Weighted equal to C1 because discoverability bought with a second install path is a bad trade | 100 = the runbook is a selector on the existing install path, no new entry point · 70 = a new entry point that delegates to the same code · 40 = a new entry point with its own copy of the install logic · 0 = no command at all |
| C3 | Reuse of the existing install semantics (L5) | 25% | This is where the real cost and the real risk live: a forked install body is where `--dry-run` quietly stops being dry and where the `opencode` capacity warning goes missing for runbook users | 100 = the runbook resolution feeds the existing call, so every flag is inherited by construction · 70 = inherits by delegating through a refactor · 40 = re-implements the flags · 0 = no install path |
| C4 | Implementation cost and test surface | 15% | Phase 3 budget is one week; anything needing an extract-refactor of the existing `install()` body risks shipped behaviour under an 80% coverage floor | 100 = a resolver plus a listing branch · 70 = resolver plus one small refactor · 40 = extract a shared install entry point from a long function · 20 = new module with duplicated logic |
| C5 | Headroom for the runbook surface to grow (`show`, `pin`, `diff`) | 10% | 42 runbooks and a per-runbook `doc` path suggest more verbs eventually — but "eventually" is speculation, so it takes the lowest weight | 100 = a noun with room for verbs · 50 = one flag that does not stretch · 0 = nothing |

### Candidates

| Candidate | What it is |
| --- | --- |
| **A — selector on `install`** | `install --runbook <slug>` resolves the roster to agent slugs and feeds the existing pipeline; `install --list runbooks` lists all 42 with title, mode, duration, agent count and `doc` path |
| **B — `runbooks` command group** | A new top-level `runbooks` Typer group with `list` and `install` subcommands |
| **C — document manual copying** | Keep `strategy/runbooks/` as repo files; add a README section telling users to copy them |

Notes that set the scores:

- **A** requires no new machinery: `RunbookDefinition.roster` gives slugs (L1) and
  `select_agents(..., agent_ids=...)` resolves slugs natively (L4). `--list`
  already exists and already means "show me what exists"
  (`tools | teams | agents | all`), so `runbooks` is a fifth value, not a new
  surface. The cost is one more flag on a 10-flag command and a new value in
  `--list`; the `interactive_run` guard must also learn `--runbook` so a filtered
  install stays non-interactive, exactly as `--division`/`--agent` already do.
- **B** is the better *home* for a growing runbook surface, but there is no
  shared install entry point to delegate to: `install()` is a single long
  procedural function, so `runbooks install` either duplicates it (C3 drops to
  40) or requires extracting it first (C4 drops to 40) under an 80% coverage
  floor. It is also the first subcommand group in a flat CLI (C2).
- **C** solves nothing in #14: it moves the knowledge requirement from "know the
  files exist" to "find the README section", and it inherits neither `--dry-run`
  nor the capacity warning.

### Scores

| Candidate | C1 (25) | C2 (25) | C3 (25) | C4 (15) | C5 (10) | Weighted |
| --- | --- | --- | --- | --- | --- | --- |
| **A — `install --runbook` + `--list runbooks`** | 70 | 90 | 100 | 90 | 45 | **83.0** |
| B — `runbooks install\|list` group | 90 | 65 | 70 | 55 | 90 | **73.5** |
| C — document manual copying | 20 | 30 | 0 | 70 | 10 | **24.0** |

### Arithmetic

```text
A  install --runbook   C1  70 × 0.25 = 17.50
                       C2  90 × 0.25 = 22.50
                       C3 100 × 0.25 = 25.00
                       C4  90 × 0.15 = 13.50
                       C5  45 × 0.10 =  4.50
                       ----------------------  = 83.00

B  runbooks group      C1  90 × 0.25 = 22.50
                       C2  65 × 0.25 = 16.25
                       C3  70 × 0.25 = 17.50
                       C4  55 × 0.15 =  8.25
                       C5  90 × 0.10 =  9.00
                       ----------------------  = 73.50

C  document copy       C1  20 × 0.25 =  5.00
                       C2  30 × 0.25 =  7.50
                       C3   0 × 0.25 =  0.00
                       C4  70 × 0.15 = 10.50
                       C5  10 × 0.10 =  1.00
                       ----------------------  = 24.00
```

Margin A over B: **9.5 points**, carried by C3 and C4 (reuse and the cost of
building reuse) rather than by C1, which B wins.

### D-002 Verdict

**Adopt option A: `install --runbook <slug>`, plus `install --list runbooks`.
Weighted score 83.0 / 100. This overturns the orchestrator draft, which chose
option B.** The draft's choice was not an arithmetic accident: corrected, its own
table still gives B 93.25 against A's 83.5. It was a *scoring* accident — the
draft credited a brand-new entry point with being more consistent with the
install surface, and easier to build and test, than a selector on that surface.
Changes 6 and 7 correct those scores and the criterion that hid them; change 9
shows A wins even under the draft's own weights.

Instantiation requirements (these are the decision, not implementation advice):

1. `--runbook <slug>` resolves through `CatalogManager.load_runbooks()`; an
   unknown slug is a clean `typer.Exit(code=1)` with the available slugs, the
   same way an unknown `--tool` is handled today.
2. The resolved roster feeds `select_agents(..., agent_ids=roster_slugs)` — no
   new resolution machinery. L3 already guarantees every roster slug resolves;
   a resolution failure at install time is a bug in the catalog, not a user
   error, and should say so.
3. `--runbook` is a **selector, mutually exclusive** with
   `--division`/`--agent`/`--agents-file`. Two selectors in one command is an
   error; silently intersecting them is worse.
4. `--runbook` forces the non-interactive path by joining the existing
   `interactive_run` guard, so `--dry-run`, `--scope`, `--tool`, `--parallel`
   and the `opencode` capacity warning all apply unchanged (C3 = 100).
5. All roster groups are installed, including `week 3+` and `as needed`. Group
   `activation` is a NEXUS scheduling concept, not an install filter; the install
   prints the groups and their activations so the user sees the phases.
6. `--list runbooks` prints, for all 42: slug, title, mode, duration, roster
   agent count, and the `doc` path. The `doc` markdown stays in the repository
   and is not installed — this CLI installs agents.

### D-002 Exit path

| Field | Value |
| --- | --- |
| Predecessor | Manual copying of `strategy/runbooks/` plus the README instructions for it, and hand-building an `--agents-file` per runbook for anyone who wanted the roster installed |
| Removal date for the predecessor | Phase 3, in the same commit that adds `--runbook` and `--list runbooks`. The README manual-copy section is **deleted**, not annotated — G3 clause 3.2 |
| Revisit trigger | Any **one** of: (a) the runbook surface needs a second verb beyond list/install (`show`, `pin`, `diff`, `search`) — a noun with verbs wants to be a noun, and this is the documented route to option B; (b) `install` exceeds 12 flags; (c) `--runbook` and `--agents-file` start needing to compose, which a flag cannot express without becoming a pipeline |
| Revisit date | Handover + 90 days, then annually. Hard backstop: no later than 12 months after the Phase 3 merge |
| Migration cost if we switch to the group | **Low.** The resolution helper and its tests move into a `runbooks` command module and a shared install entry point is extracted then, when there is a second caller to justify the refactor. Estimated ≤ 1 engineer-day. Reversing back to the flag is equally cheap, which is why this decision is safe to make on a 9.5-point margin |
| Reversibility | **High.** One command surface, no data migration, no installer contract change, no user-visible state |

---

## Changes from the orchestrator draft

The draft was audited rather than inherited. Nine changes: five to D-001, four
to D-002.

### D-001 — verdict kept, weights and two scores overturned

| # | Change | Reason |
| --- | --- | --- |
| 1 | **Weight rebalance.** C1 30% → 25%, C3 testability 20% → 25%, C4 15% (was "list + search + detail out of the box"), C5 10% → 15%. Weights still sum to 100 | The draft let one criterion (C1) decide a three-candidate field at 30%, and had no criterion for tool churn, which is the cost a `uv sync --frozen` repo pays whenever it upgrades. Testability was raised to equality with dependency cost because it is also a hard CI gate (K4), not a preference |
| 2 | **Added a fourth candidate: stdlib `curses`** | The draft offered two adopt options and one build option. Python's own docs disqualify `curses` on Windows (K6), which is exactly the kind of near-miss a build-vs-adopt record should show being rejected on evidence rather than never being listed |
| 3 | **Corrected a methodological error in C3.** The draft scored prompt-toolkit's testability *with* the "pure model + thin view" mitigation applied (80) and textual's *without* it (75), while textual additionally ships `App.run_test()`/`Pilot` | Applying a mitigation to one candidate and not the other is not a comparison. Re-scored consistently: prompt-toolkit 75, textual 100. The mitigation is now recorded as MC1 — a condition on the winner, not a credit to it |
| 4 | **Corrected prompt-toolkit's capability facts upward, but its C4 score downward.** 75 → 65 | The draft said prompt-toolkit is "enough … without pulling in a layout widget system", which undersells it: `CheckboxList`, `checkboxlist_dialog` and `radiolist_dialog` are shipped and *are* multi-select from a list. But the criterion asks for list + filter + checkbox selection, and the filter is still ours — which the anchor fixes at 60, so 65. Both facts corrected in opposite directions, so the anchor decides rather than my impression |
| 5 | **Final score 87.5 → 81.5.** Verdict and ranking unchanged | Consequence of changes 1–4 plus textual's C1 40 → 25 (four new audited distributions, not "a new runtime dependency plus its transitive tree"; `platformdirs` moves from dev-only into the audited runtime set) and the dual-framework point the draft missed |

### D-002 — verdict overturned

| # | Change | Reason |
| --- | --- | --- |
| 6 | **Verdict overturned: option A (`install --runbook` + `--list runbooks`) at 83.0 beats option B (the `runbooks` group) at 73.5** | The draft's C2 = 85 for a *new* entry point and C4 = 95 for its testability credited the group above a flag on the existing command. A second install surface cannot be more consistent than the install surface, and a new command that must either duplicate or extract-and-delegate a 100-line function cannot be cheaper to build and test than a selector. Corrected: B's C2 85 → 65, B's C4 95 → 55; A's C1 60 → 70 (it is named in the `--help` of the command users already run, and `--list runbooks` is the listing surface the draft assumed only a group could provide) |
| 7 | **One criterion replaced.** The draft's C3 "Works on a clean checkout with no manual copying" (25%) was scored 100 for A and 100 for B, and 0 for C | A criterion that cannot discriminate between the two real candidates is 25% of dead weight, and it was also the criterion whose 100/100 hid that A and B differ exactly where cost lives. Replaced with "Reuse of the existing install semantics", on which A scores 100 by construction and B scores 70 only after a refactor |
| 8 | **None of the draft's three D-002 totals follows from its own printed scores in its printed columns.** Corrected to 93.25, 83.5 and 21.0 | Hand-check below. Rows 1–2 reproduce under a three-column rotation of the C2–C4 scores and row 3 under a C1↔C2 swap — no single transformation fits all three — so the table cannot be read back per criterion, which is what M7's "checkable arithmetic" requires. The draft's row order and its ~11-point margin survive; its per-criterion values do not. Its **D-001** arithmetic, by contrast, reproduces exactly (87.5 / 73.5 / 70.25) and is not in question |
| 9 | **Added a claim-sensitivity check** to both decisions | #6 means my D-002 verdict must show it is not a weighting artefact: under **the draft's own weights** (35/30/25/10) with my criterion set and honest scores, A still wins 85.5 to 74.0. The draft's outcome came from over-crediting the group, not from its weights |

### Hand-check of the draft's D-002 arithmetic

The draft's D-002 table printed weights 35 / 30 / 25 / 10 (sum 100) and these
scores. Recomputing each row from its own numbers:

```text
draft row 1 — "runbooks install|list"
  95 × 0.35 = 33.25
  85 × 0.30 = 25.50
 100 × 0.25 = 25.00
  95 × 0.10 =  9.50
              ------ = 93.25      printed: 93.0    error: −0.25

draft row 2 — "Extend install --runbook <slug>"
  60 × 0.35 = 21.00
  95 × 0.30 = 28.50
 100 × 0.25 = 25.00
  90 × 0.10 =  9.00
              ------ = 83.50      printed: 81.8    error: −1.70

draft row 3 — "Document 'copy the directory'"
  20 × 0.35 =  7.00
  40 × 0.30 = 12.00
   0 × 0.25 =  0.00
  20 × 0.10 =  2.00
              ------ = 21.00      printed: 22.0    error: +1.00
```

The draft's stated margin between rows 1 and 2 was 11.2. On its printed scores in
its printed columns the margin is **9.75**.

**Provenance of the nine numbers, stated precisely.** I tried to reconstruct the
draft's totals rather than just declare them wrong, and the result is more
interesting than a slip:

| Row | Printed scores C1/C2/C3/C4 | Total as printed | Rotating the C2–C4 scores one column (C2←C4, C3←C2, C4←C3) | Swapping C1↔C2 |
| --- | --- | --- | --- | --- |
| 1 — `runbooks` group | 95 / 85 / 100 / 95 | 93.25 (printed 93.0) | **93.00** ✓ | 92.75 |
| 2 — `install --runbook` | 60 / 95 / 100 / 90 | 83.50 (printed 81.8) | **81.75** ✓ (printed 81.8) | 85.25 |
| 3 — document copy | 20 / 40 / 0 / 20 | 21.00 (printed 22.0) | 23.00 | **22.00** ✓ |

So rows 1 and 2 are both consistent with the *same* three-column rotation, and
that rotation is also what produces the 11.2 margin the draft claimed (11.25).
Row 3 needs a different transformation — a genuine C1↔C2 swap — and no single
transformation explains all three rows. The most defensible reading is a column
misalignment in rows 1–2 plus an independent error in row 3.

**Why this still fails, even though the totals are reachable.** The row order is
stable under every reading (1 > 2 > 3, margin 9.75–11.25 points), so the draft's
D-002 *conclusion* was never in danger. What is not stable is which score belongs
to which criterion — and C1, C2 and C3 carry 35%, 30% and 25%. A reader of that
table cannot tell whether "extend `install --runbook`" scores 95 or 90 on
discoverability, the highest-weight criterion, or whether the group's score of
100 sits on C3 (25%) or C4 (10%). A total that reproduces only under an
unstated column rotation does not satisfy M7's "verdict plus ... arithmetic a
reader can check", because the check is exactly what fails. Recomputing from the
printed scores in the printed columns gives **93.25 / 83.5 / 21.0**, which is what
this record uses and what the corrected numbers in change 8 refer to.

For completeness, the draft's **D-001** arithmetic does reproduce exactly, so it
is not in question: prompt-toolkit 30 + 21.25 + 16 + 11.25 + 9 = 87.5; textual
12 + 23.75 + 15 + 14.25 + 8.5 = 73.5; rich-only 30 + 11.25 + 14 + 6 + 9 = 70.25
(printed 70.3 — correct rounding).

### What survived scrutiny, unedited

- The M7 definition and the "anything less is a fail" standard.
- The exit-path field set (predecessor, removal date, revisit trigger, revisit
  date, migration cost, reversibility), which both decisions keep.
- The mandate that the browser's state live in a pure model with a thin view —
  kept as MC1, but demoted from a scoring argument to a condition.
- The D-001 winner (prompt-toolkit) and its ranking, reached independently.
- The claim that prompt-toolkit provides a full-screen loop, key bindings,
  incremental search and a split layout — verified true, and extended with the
  widgets the draft did not mention.

---

## Evidence log

Everything in this section was observed on 2026-11-05. Claims without a source
here do not appear in this record.

**Repository**

- `pyproject.toml`: runtime dependencies are `prompt-toolkit>=3.0.53`,
  `pydantic>=2.14.1`, `rich>=15.0.0`, `typer>=0.27.3`; `requires-python = ">=3.13"`.
- `uv.lock`: prompt-toolkit 3.0.53, rich 15.0.0, typer 0.27.3, pydantic 2.14.1,
  markdown-it-py 4.2.0, pygments 2.21.0, mdurl 0.1.2.
- Runtime dependency closure resolved from `uv.lock` = **15 distributions**:
  annotated-doc, annotated-types, colorama, markdown-it-py, mdurl,
  prompt-toolkit, pydantic, pydantic-core, pygments, rich, shellingham, typer,
  typing-extensions, typing-inspection, wcwidth.
- `platformdirs` appears in `uv.lock` and is required only by `pip-audit` and
  `virtualenv` — dev tooling, not the runtime closure.
- `.github/workflows/ci.yml`, `security` job: `uv export --format
  requirements-txt --no-dev --no-emit-project --no-hashes` then
  `pip-audit --strict -r` — the audited set is runtime-only.
- `.github/workflows/ci.yml`, `test` job: `--cov=agency_agents --cov-branch
  --cov-fail-under=80`.
- `src/agency_agents/infrastructure/tui.py`: uses `prompt_toolkit.prompt` and
  `WordCompleter`; `InstallSelection(tools, scope, divisions)`.
- `src/agency_agents/cli/main.py`: `install` flags `--tool`, `--interactive`,
  `--scope`, `--parallel`, `--jobs`, `--division`, `--agent`, `--agents-file`,
  `--dry-run`, `--list`; `--list` accepts `tools | teams | agents | all`; the
  `interactive_run` guard excludes filtered runs; `_warn_tool_capacity` warns at
  `opencode`'s cap of 119.
- `src/agency_agents/infrastructure/catalog.py`: `load_runbooks()` →
  `RunbookDefinition(slug, title, mode, duration, summary, doc, roster)`.
- `src/agency_agents/core/selection.py`: `build_roster_index` / `resolve_agent`
  resolve slug, display name, file stem and the `agency-`-stripped alias.
- `strategy/runbooks.json`: 42 runbooks, 687 roster agent references.
- local `prompt_toolkit` 3.0.53 introspection: `Application.__init__` accepts
  `input: Input | None` and `output: Output | None`;
  `prompt_toolkit.input.create_pipe_input` exists;
  `prompt_toolkit.output.DummyOutput` exists; `widgets` exports `Dialog`,
  `CheckboxList`, `RadioList`, `Button`, `Frame`, `Label`, `TextArea`,
  `SearchToolbar`, `MenuContainer`, `MenuItem`, `ProgressBar`;
  `shortcuts` exports `checkboxlist_dialog`, `radiolist_dialog`, `button_dialog`,
  `yes_no_dialog`, `input_dialog`, `message_dialog`, `progress_dialog`.

**Upstream**

- prompt-toolkit, *Building full screen applications*
  (<https://python-prompt-toolkit.readthedocs.io/en/master/pages/full_screen_apps.html>):
  `Application(full_screen=True)`, `Layout`, `HSplit`/`VSplit`/`Window`,
  `FloatContainer`, `ScrollablePane`, `KeyBindings`, `BufferControl`,
  `FormattedTextControl`, `HighlightSearchProcessor`; "the input and output
  device … Both are optional and normally not needed to pass explicitly".
- textual 8.2.8 metadata (<https://pypi.org/pypi/textual/json>):
  `requires_dist` base = `markdown-it-py[linkify]>=2.1.0`, `mdit-py-plugins`,
  `platformdirs<5,>=3.6.0`, `pygments<3.0.0,>=2.19.2`, `rich>=14.2.0`;
  `requires_python` = `<4.0,>=3.9`; wheels `py3-none-any`.
- textual, *Testing* (<https://textual.textualize.io/guide/testing/>):
  `App.run_test()` "will run the app in _headless_ mode"; it is "an _async
  context manager_ which returns a `Pilot`"; `pilot.press`, `pilot.click`,
  `pilot.pause`; "The default size of a simulated app is (80, 24)".
- Python, *Curses Programming with Python*
  (<https://docs.python.org/3/howto/curses.html>): "The Windows version of
  Python doesn't include the `curses` module. The third-party windows-curses
  package provides the same interface on Windows." — and "curses doesn't
  provide many user-interface concepts such as buttons, checkboxes, or dialogs".
- mdit-py-plugins 0.6.1 metadata (<https://pypi.org/pypi/mdit-py-plugins/json>):
  requires only `markdown-it-py>=2.0.0,<5.0.0`, which this project already has.
- linkify-it-py 2.2.0 metadata (<https://pypi.org/pypi/linkify-it-py/json>): no
  runtime `uc-micro-py` dependency in this release.

## Record status

| Field | Value |
| --- | --- |
| Decisions recorded | 2 (D-001, D-002) — M7 requires ≥ 3 weighted criteria, ≥ 2 scored candidates, verdict plus exit path; both decisions clear all three |
| Criteria per decision | 5 weighted criteria each, weights summing to 100, each with a stated reason and a fixed scoring anchor |
| Candidates per decision | D-001: 4 (3 adopt, 1 build). D-002: 3 (2 command shapes, 1 do-nothing) |
| Author | Tool Evaluator |
| Predecessor | Agents Orchestrator draft (audited, not inherited) |
| Date | 2026-11-05 |
| Next review | G5 handover + 90 days; hard backstop 12 months after the Phase 3 merge. Any exit-path trigger pulls a decision forward immediately |
