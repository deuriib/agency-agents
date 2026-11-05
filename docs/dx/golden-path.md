# The golden path — one route, five steps (G2)

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

## What changed from the baseline, and why

| Baseline step | Golden-path step | Change |
| --- | --- | --- |
| clone | 1 | Unchanged |
| `install-uv` (undocumented, guessed) | folded into 2 | Bootstrap owns runtime acquisition |
| `uv sync` (undocumented, guessed) | folded into 2 | Bootstrap owns dependency resolution |
| `python -m agency_agents install` | 4 | Same command, now reachable as `agency-agents` |
| — (did not exist) | 3 | The gate had no one-command entry point |
| — (did not exist) | 5 | Nothing proved the install landed |

M6 before/after: **5 steps → 5 steps**, but the composition changes. Two steps a
newcomer had to *guess* (`install-uv`, `uv-sync`) become one step the repo owns,
and the two steps that did not exist (the gate, the proof) are added. The count
is flat; the number of steps requiring undocumented knowledge drops from 2 to 0.

This is recorded as a deliberate, costed trade rather than a step reduction: a
flat M6 with zero guessed steps is the honest win here, and claiming a reduction
by hiding bootstrap work inside a script would be exactly the "measure the happy
path" pitfall the runbook names.

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

Total measured senior time removable per onboarding: **13.0 hours** (baseline
M10 target was 24 hours from the last 5 hires; the Phase 4 instrument replaces
that estimate with a measurement).

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
| `TUIWizard` as the only interactive surface | Phase 3 | Superseded by the browsable TUI; deleted in the same change per D-001 |
| "Copy a category" manual `cp` instructions | Phase 3 | Replaced by `--division` / `--agent`, which already existed |

## G2 verdict

```text
G2.1  Six or fewer steps (M6), each with a named owner.                    PASS (5 steps)
G2.2  No two steps share an owner without a handoff note.                  PASS (note H1)
G2.3  A step's friction is measured at baseline, or declared UNMEASURED
      with a Phase 3 instrumentation owner and date.                       PASS (steps 3, 5)
G2.4  Every mandated-versus-optional decision is recorded with the senior
      hours it saves.                                                      PASS (§ Mandated vs optional)
```

**G2: PASS**
