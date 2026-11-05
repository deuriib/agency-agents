# The golden path — one route, five documented steps (G2)

There is exactly one supported route from a clean machine to a developer's own
change running in the tool they use. Alternatives are removed, not maintained.

## The five steps

| # | Step | Command | Owner | Target friction | Instrument |
| --- | --- | --- | --- | --- | --- |
| 1 | Get the code | `git clone <url> && cd agency-agents` | Platform Engineer | Under 2 minutes, no ticket | M1 step timing, clean-room transcript |
| 2 | Bootstrap | `./scripts/bootstrap.sh` | Platform Engineer → Developer Tooling Engineer (handoff note H1) | One command, zero senior help, actionable failure text | M5 bootstrap failure rate |
| 3 | Run the gate | `./scripts/gate.sh` | Developer Tooling Engineer | Same checks as CI, cheapest check first | M2, M3, M8 |
| 4 | Install your work | `agency-agents install --tool <tool>` | DevOps Automator | One command, main to your tool, prints what landed | M1 deploy step timing |
| 5 | Prove it landed | `agency-agents verify --all` and the install summary | SRE (Site Reliability Engineer) | One command, no ticket, names the files written | G4 visibility check |

Five steps against a ceiling of six (G2 clause 2.1).

### Handoff note H1 — steps 1 and 2 share an owner

Step 1 and step 2 are both owned by the Platform Engineer. The handoff is
explicit: **step 1 is a git operation and step 2 is a toolchain operation**, and
they fail for different reasons with different remediation. Step 1's failure mode
is network or credential; step 2's is interpreter, lockfile or toolchain drift.

Because the two failures are not diagnosable by the same person in the same
context, `scripts/bootstrap.sh` refuses to run outside a git working tree and
names the clone as the fix, closing the handoff in code rather than in prose. The
five phases it runs, and what each failure message means, are in
`docs/dx/bootstrap.md`.

## What this path can and cannot prove

The runbook defines **first success** as *the subject's own change is deployed by
the documented path **and** an observability query returns data for it*. This
repository has neither a deploy target nor an observability surface: it publishes
markdown agents and a CLI, and `grep -ri observability` over this tree returns
nothing. The definition therefore has no referent here, and **M1 is
`UNMEASURED` for this run.**

What *was* measured on a proven-clean machine is narrower and must be named
narrowly:

> **Clean clone → a working, verified local install: 5 documented commands,
> 0 failures, 116 seconds, 298 agents installed and manifest-verified.**

That is a real and reproducible result, and it is **not** M1. An earlier draft of
this document described those 116 seconds as "time to first success" without
noting that the runbook's definition demands a deploy and an observability query.
That was a silent redefinition, and it is corrected here rather than defended. The
runbook's own doctrine applies to this document: a threshold nobody defined, or a
definition quietly swapped for a convenient one, is a fail.

Where the analogues fall short, explicitly:

| Runbook term | What this run actually did | Gap |
| --- | --- | --- |
| Deployed change | Wrote 298 rendered agents into `~/.claude/agents` | Nothing was published or served; there is no environment to deploy to |
| Observability query | `agency-agents verify --all` (SHA-256 manifest) plus a file-count assertion | A manifest check proves integrity, not that a running system emits telemetry |
| Subject's own change | The subject installed the published catalog unchanged | No change of the subject's was deployed, so "their own change" was not exercised |

Closing these needs either a deploy surface (issue #12, publishing to PyPI, is the
nearest analogue) or an explicit, written decision that this repository's "first
success" is an install-and-verify event. That decision belongs to the platform
owner at G5 handover, not to this document.

## What changed from the baseline, and why

| Baseline step | Golden-path step | Change |
| --- | --- | --- |
| clone | 1 | Unchanged |
| `install-uv` (undocumented, guessed) | folded into 2 | Bootstrap owns runtime acquisition |
| `uv sync` (undocumented, guessed) | folded into 2 | Bootstrap owns dependency resolution |
| `python -m agency_agents install` | 4 | Same command, now reachable as `agency-agents` |
| — (did not exist) | 3 | The gate had no one-command entry point |
| — (did not exist) | 5 | Nothing proved the install landed |

M6 before/after: **5 documented commands → 5 documented commands**, with the
composition changed. Two commands a newcomer had to *guess* (`install-uv`,
`uv-sync`) are absorbed into one command the repo owns, and two commands that did
not exist at all are added (the gate and the proof). The count is flat; the number
of commands requiring undocumented knowledge drops from 2 to 0, and the number
that exit non-zero drops from 1 to 0.

This is a deliberate, costed trade, not a step reduction. Claiming a reduction by
hiding bootstrap work inside a script would be exactly the "measure the happy
path" pitfall the runbook names, so the count is reported flat.

**Instrument versus document, stated explicitly.** The clean-room harness
(`scripts/ci/paths/golden-path.sh`) measures **six** things: the five documented
commands plus a sixth observation step in which the Evidence Collector asserts the
installed files are visible on disk. M6 counts *distinct developer commands from
clone to first success*, so M6 = 5 and the harness reports 6 measured steps on
purpose. The two numbers are never merged. An earlier revision fused the
observation into the fifth step to make the harness print five; that changed no
work, bought nothing, and was reverted — the instrument names what it measures.

## Mandated versus optional — the costed decisions (G2 clause 2.4)

Each decision names the senior hours it saves. A step left optional with no
costed saving fails G2.

| Decision | Mandated / Optional | Senior hours it saves | Decided by |
| --- | --- | --- | --- |
| `./scripts/bootstrap.sh` as the only bootstrap route | **Mandated** | 4.0 h per new hire — the baseline charged 2 undocumented steps to whoever was on call | DX Engineer + Product Manager |
| `./scripts/gate.sh` as the only pre-push gate | **Mandated** | 2.5 h per new hire — a newcomer otherwise discovers which of the 5 CI jobs to run by pushing and waiting | DX Engineer + Product Manager |
| Which tool to install into | **Optional** | 0 h — genuinely a personal choice, nothing downstream depends on it | Product Manager |
| `mise run ci` as an alternative gate | **Removed** | 0.5 h — a second gate means two answers to "is this green"; `scripts/gate.sh` calls the same tasks | Developer Tooling Engineer |
| Hand-rolling a venv without `uv` | **Removed** | 6.0 h — the pinned interpreter and lockfile are what make CI and local agree | Platform Engineer |

Total senior time the design *claims* to remove per onboarding: **13.0 hours**.

**This figure is an estimate, not a measurement, and no gate may read it.** It is
the sum of the per-decision figures above, and each of those is a judgement with
no instrument behind it: there is no intervention log, no onboarding-channel
ticket history, and no timed human subject, so M10 remains `UNMEASURED` (see
`baseline.md` §2). The baseline figure of "24 hours from the last 5 hires" quoted
in the runbook's Success Criteria table is likewise unverified for this
repository. Treat both as hypotheses to be tested by the first instrumented
onboarding run, not as savings already banked.

## Path friction: measured or `UNMEASURED`

Per G2 clause 2.3, every step's friction is either measured at baseline or
declared `UNMEASURED` at G1 with an instrumentation owner and a date.

| Step | Baseline friction | Status | Instrumentation owner | Measurement date |
| --- | --- | --- | --- | --- |
| 1 Get the code | 2 s (clean-room `step_1_seconds`) | MEASURED | — | — |
| 2 Bootstrap | Step did not exist; its two constituent steps measured 6 s + 18 s | MEASURED (composed) | Platform Engineer | Phase 4 run |
| 3 Run the gate | Not measured — no one-command gate existed | `UNMEASURED` | Developer Tooling Engineer | Phase 4 run |
| 4 Install your work | 8 s (clean-room `step_4_seconds`) | MEASURED | — | — |
| 5 Prove it landed | Not measured — the command surface did not work | `UNMEASURED` | SRE (Site Reliability Engineer) | Phase 4 run |

Steps 3 and 5 are `UNMEASURED` at G2 by construction: they are new, and their
target is judged absolutely on the first clean-machine observation in Phase 4
rather than on a delta that cannot exist.

## Removed paths and their removal commits

| Removed path | Removed in | Why |
| --- | --- | --- |
| `agency_agents:main` broken entry point | Phase 3 | Replaced by a real `main()`; the import no longer fails |
| Manual copying of `strategy/runbooks/` | Phase 3 | Replaced by `install --runbook <slug>` / `install --list runbooks` (tool decision D-002) |
| `TUIWizard` (`infrastructure/tui.py`) | Phase 3 | **Deleted.** `install` with no flags now opens the browser, and the wizard's tool picker survives as a shipped `checkboxlist_dialog`. One interactive surface, no second mental model. Its team list is superseded by the browser's filter, which is strictly better than picking divisions blind |
| "Copy a category" manual `cp` instructions | Phase 3 | Replaced by `--division` / `--agent`, which already existed |

## G2 verdict

```text
G2.1  Six or fewer steps (M6), each with a named owner.                    PASS (5 documented steps)
G2.2  No two steps share an owner without a handoff note.                  PASS (note H1)
G2.3  A step's friction is measured at baseline, or declared UNMEASURED
      with a Phase 3 instrumentation owner and date.                       PASS (steps 3, 5)
G2.4  Every mandated-versus-optional decision is recorded with the senior
      hours it saves.                                                      PASS (§ Mandated vs optional)
```

**G2: PASS**
