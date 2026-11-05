# Scorecard & handover — Developer Experience Platform runbook

| Field | Value |
| --- | --- |
| Runbook | `strategy/runbooks/scenario-developer-experience-platform.md` |
| Mode | NEXUS-Sprint |
| Branch | `feat/cli-runbooks-tui` |
| Baseline frozen | 2026-11-05 (`docs/dx/baseline.md`) |
| Scorecard written | 2026-11-05 |
| Post-merge re-measurement | 2026-11-05, `main` @ `0542122` (rewrite merged as `ae559df`) |
| Overall status | **NEEDS WORK** — not production-ready, and it does not claim to be |
| Reality Checker verdict | `docs/dx/reality-check.md` (default upheld) |

This document is deliberately unwilling to mark itself green. The runbook's own
doctrine is that evidence which cannot be re-checked is not evidence, and a gate
that reports failure while closing successfully is worse than no gate — the exact
defect this run found in `lint` (D2). Holding this scorecard to a lower standard
would be the same mistake in prose.

---

## 1. What was delivered, and where the proof is

| # | Change | Proof |
| --- | --- | --- |
| 1 | The installed `agency-agents` console script answers (was `ImportError`) | `pyproject.toml:16`; guarded by `test_declared_console_script_resolves_to_a_callable`, `test_installed_console_script_answers_help` |
| 2 | `lint` exits 1 on a catalog inconsistency (was: reported red, exited 0) | `test_lint_fails_on_a_tool_with_no_renderer`; CI job `documented-commands` runs `scripts/ci/assert_lint_fails.sh` |
| 3 | `install --runbook <slug>` and `install --list runbooks` (issue #14) | 19 tests in `test_cli_runbooks_tui.py`; `docs/dx/m7-tool-decisions.md` D-002 |
| 4 | `tui` browsable agent browser (issue #13) | 35 model tests (`test_browser.py`) + 14 command tests (`test_cli_tui.py`); D-001 |
| 5 | `./scripts/bootstrap.sh` — one command, actionable failures, idempotent | `docs/dx/bootstrap.md`; CI runs it twice |
| 6 | `./scripts/gate.sh` — one pre-push gate, cheapest first | `docs/dx/gate.md`; `--list` reproduced in CI |
| 7 | Clean-room and CI-metrics instruments | `scripts/ci/*`; this scorecard's numbers |
| 8 | `TUIWizard` deleted; `install` with no flags opens the browser, and its tool picker survives as `choose_tools()` over prompt-toolkit's shipped `checkboxlist_dialog` | `git rm src/agency_agents/infrastructure/tui.py`; one interactive surface instead of two |
| 9 | Docs: baseline, golden path, M7 record, newcomer path, M9 audit, CLI FAQ, evidence pack | `docs/dx/` |

Full local gate: `GATE RESULT: PASS — 8 checks, 76.5s`. Test suite: **291 passed**,
branch coverage **92.9%** (floor 80%). mypy ratchet: **39 errors, unchanged from
baseline** — no new type errors were introduced.

**CI is green** on the pull request (`#62`), including the new
`documented-commands` job: `ci/required`, `documented-commands`, `lint`, `types`,
`test`, `verify-manifest`, `security`, the Project Quality Check and CodeQL all
pass (run `42072487592`). Two failures were found and fixed on the way: a
pre-existing test that asserted where the console wraps a path, and a help-surface
assertion that read styled output and therefore behaved differently with a
terminal attached.

## 2. The measured result, stated narrowly

Measured on a proven-clean disposable container (empty work-directory listing and
an empty `which` transcript recorded before the first documented command):

| Run | Commit | Steps measured | Failed | Total |
| --- | --- | --- | --- | --- |
| 1 | `8f04ad7` | 6 | 0 | 474 s |
| 2 | `8f04ad7` | 6 | 0 | 170 s |
| 3 | `8f04ad7` | 6 | 0 | 148 s |

**Median 170 s, range 148–474 s, n = 3, zero failures.** The spread is real and is
almost entirely the network-dependent dependency audit inside step 3; a single
number would have been cherry-picking. Transcripts with commit SHA and image
digest: `docs/dx/evidence/run{1,2,3}-golden-path.log`.

Baseline for comparison (`docs/dx/evidence/baseline-transcript.log`): 5 commands,
**1 failed**, and no path to a working CLI at all.

### Post-merge window status

The rewrite merged as `ae559df`; the gate window that clauses 3.6–3.8 read is the
first 20 default-branch runs carrying it.

| Field | Value |
| --- | --- |
| Window opened | 2026-11-05T17:33:13Z (`ae559df`) |
| Post-rewrite `CI` runs so far | **2 of 20** |
| Those runs | `42075739834` (success), `42076162900` (success) |
| Pre-rewrite 20-run window, for reference | M3 p50 **31 s** / p90 51 s; M4 **0 %**; M2 `UNMEASURED` (no failed run in the window) |

Two runs is a start, not a measurement. `scripts/ci/ci_metrics.py` reads a fixed
window, so until the 20th post-rewrite run exists its numbers still mix pre- and
post-rewrite history. Re-run it after the window fills; do not read the table in
this section as the gate window.

**What this is not.** It is not "time to first success" as the runbook defines it
(a deployed change plus an observability query returning data for it). This
repository has no deploy target and no observability surface, so M1 is
`UNMEASURED`. See `golden-path.md` § "What this path can and cannot prove".

## 3. Gates, clause by clause

`UNMEASURED` is treated as failure, exactly as G3 requires. A clause is only PASS
when an artifact proves it.

### G1 — baseline frozen

| Clause | Status | Evidence |
| --- | --- | --- |
| 1.1 Every metric measured with its source named, or `UNMEASURED` with reason, owner and date | **PASS** | `baseline.md` §2 — M2 and M10 carry reason, owner and date; M9 recorded as an empty population with a reasoned audit |
| 1.2 M1 baseline present and never blank | **PASS** | `baseline.md` §2 — recorded as a measured failure, not blank |

**G1: PASS.**

### G2 — the golden path

| Clause | Status | Evidence |
| --- | --- | --- |
| 2.1 ≤6 steps, each with a named owner | **PASS** | 5 documented commands, `golden-path.md` § "The five steps" |
| 2.2 No two steps share an owner without a handoff note | **PASS** | Handoff note H1, closed in code by `bootstrap.sh`'s git check |
| 2.3 Friction measured at baseline or declared `UNMEASURED` with owner and date | **PASS** | `golden-path.md` § "Path friction"; steps 3 and 5 declared `UNMEASURED` |
| 2.4 Mandated-vs-optional recorded with senior hours | **PASS for the record, not for the numbers** | The decisions and their owners are recorded; the 13.0-hour total is an **estimate with no instrument behind it** and is excluded from every gate (`golden-path.md`) |

**G2: PASS**, with the caveat that clause 2.4's *hours* are estimates. If a
reviewer reads 2.4 as requiring measured hours, it is `UNMEASURED` — that reading
is defensible and is not contested here.

### G3 — the built path

Nine clauses. **This gate is not claimable.**

| Clause | Status | Why |
| --- | --- | --- |
| 3.1 M8 = 100%: every documented command exits 0 in CI | **PARTIAL** — every command CI executes exits 0; the set is not the whole documented surface | CI is green on `31b3047`'s successor commit: `documented-commands`, `lint`, `types`, `test`, `verify-manifest`, `security`, `ci/required` all pass (run `42072487592`). The job runs bootstrap twice, the console script, `install --list runbooks`, `install --runbook … --dry-run`, `gate.sh --list` and the lint-failure assertion. It does **not** cover `tui` (needs a TTY) or 16 of the 19 `install --tool` variants, so M8 is not 100% of the documented surface |
| 3.2 Every deprecated-path entry has its removal commit **merged** | **PASS** | Merged as `ae559df`. Four superseded paths are deleted rather than annotated, and all four are on `main`: the README manual-copy instructions, `TUIWizard` (`infrastructure/tui.py` + `test_tui_wizard.py`), the broken `agency_agents:main` entry point, and "copy a category" as a substitute for `--division`. Verified by `git ls-files` on `main` and by `grep` finding no live reference to the class |
| 3.3 M7 = 100%: every tool decision carries a written evaluation against the criteria with an exit path | **PASS** | `m7-tool-decisions.md`: 2 decisions, weighted criteria written before scoring, arithmetic shown, exit paths named |
| 3.4 M6 before/after for every touched step, total ≤6 | **PASS** | 5 documented commands; before/after table in `golden-path.md`. The harness measures 6 things — the 6th is the Evidence Collector's observation, not a developer command, and the two numbers are never merged |
| 3.5 M9 = 0 stale samples | **UNMEASURED (empty population)** | `m9-stale-samples.md`: this repo ships no SDK, so no sample can pin a version that drifts. The null is reasoned, not silent — but it is not a measured zero |
| 3.6 M2 interim over the first 20 **post-rewrite** default-branch runs | **UNMEASURED — window open, 2/20** | The window opened at `ae559df`. No post-rewrite run has failed yet, so M2 has no sample; M2 is not zero, it is empty. Pre-rewrite reference: p50 33 s / p90 51 s |
| 3.7 M3 interim over the same window | **UNMEASURED — window open, 2/20** | Latest 20-run reading is p50 31 s / p90 51 s, but that window still mixes pre- and post-rewrite runs |
| 3.8 M4 interim flake rate | **UNMEASURED — window open, 2/20** | 0 flakes observed so far; 2 runs cannot establish a rate |
| 3.9 M5: ≥20 instrumented clean-machine bootstrap attempts, failure rate ≤5% | **UNMEASURED** | **3 attempts, 0 failures** — a 0% failure rate over n=3 is not the clause. It needs 20 |

**G3: FAIL (3 PASS / 1 PARTIAL / 5 UNMEASURED).** PASS: 3.2, 3.3, 3.4.
PARTIAL: 3.1. UNMEASURED: 3.5, 3.6, 3.7, 3.8, 3.9. That is nine clauses.

> **Correction.** An earlier revision of this row read "3 PASS / 1 PARTIAL /
> 5 UNMEASURED" while only **two** clauses (3.3, 3.4) were marked PASS — the
> count did not add to its own table. The total is right only now that 3.2 has
> merged. A scorecard whose arithmetic disagrees with its rows is the prose
> version of the `lint` defect this run fixed, so it is corrected rather than
> quietly overwritten.

Clauses 3.6–3.8 close automatically when the 20th post-rewrite run exists; 3.9
needs the bootstrap counter wired to real attempts; 3.1 has CI evidence but not
over the whole documented surface.

### G4 — onboarding proof

| Clause | Status | Why |
| --- | --- | --- |
| 4.1 Three consecutive subjects reach first success on clean machines | **UNMEASURED** | No human subject. Evidence is ENGINEER-EXECUTED |
| 4.2 Zero interventions across all three runs | **UNMEASURED** | There is no intervention log. The operator wrote the command file it then executed — by the runbook's definition that is the strongest possible intervention, not the absence of one |
| 4.3 Median time to first success ≤4 h (M1) | **UNMEASURED** | M1 has no referent in this repository |
| 4.4 Every subject ≤8 h (M1) | **UNMEASURED** | Same |
| 4.5 Every stall logged with step and duration | **UNMEASURED as a subject stall log** | No subject, so no subject stalls. The operator's own stalls are logged in §6 below, which is a different artifact |
| 4.6 Written consent, retention, viewer list, no secret visible | **FAIL for consent; PASS for redaction** | There is no recorded session, so consent cannot exist. 14 credential/identifier patterns were scanned across the transcripts with zero hits (`evidence-pack.md`) — but a redaction scan is not consent |
| 4.7 M10 ≤2 h senior time per onboarding | **UNMEASURED** | No intervention log and no onboarding-channel ticket source |

**G4: FAIL (7 UNMEASURED, 1 partial).** This is the runbook's non-negotiable gate
and it is not satisfied. It cannot be satisfied without recruiting real people.

### G5 — scorecard and handover

| Clause | Status | Note |
| --- | --- | --- |
| 5.1 Scorecard published where engineers look and linked from README | **PASS** | This document, linked from `README.md` |
| 5.2 The named platform owner accepts handover in writing | **UNMEASURED** | No platform owner has been named, which the runbook lists as a blocking input before Week 1. It was not supplied |
| 5.3 Every Post-runbook row carries an owner and a measurement date | **PASS** | §5 below |
| 5.4 Evidence pack records deletion date and viewer list | **PASS** | `evidence-pack.md` |

**G5: PARTIAL.**

## 4. Honest ledger — what this run did not prove

1. **M1.** No deploy, no observability query, no subject's change. `UNMEASURED`.
2. **M10 and the 13.0 senior hours.** No intervention log, no ticket history. The
   hours are estimates and every gate excludes them.
3. **M5 over 20 attempts.** 3 attempts at 0 failures is a promising signal, not
   clause 3.9.
4. **M2/M3/M4 over the post-rewrite gate window.** The window is empty until merge.
5. **Consent and recorded sessions.** Structurally impossible without people.
6. **The gate window is 2/20 filled.** The rewrite is merged (`ae559df`) and CI
   is green on `main`, which closes 3.2 and puts 3.6–3.8 inside an open window.
   It does not close them: two runs cannot measure a p90 or a flake rate.

## 5. Post-runbook commitments

Window-bound metrics ship as owned commitments, not as closed results.

| Metric | Owner | Measurement date |
| --- | --- | --- |
| M2, M3, M4 over the first 20 post-rewrite default-branch runs | Analytics Reporter | Window opened 2026-11-05 (`ae559df`); 2/20 runs. Due at the 20th |
| M5 over ≥20 instrumented bootstrap attempts | Platform Engineer | 2026-12-05 |
| M8 = 100% as actually observed in CI | Technical Writer | **Met for the executed set**: CI green on `main` @ `ae559df` and `0542122`. Remains PARTIAL until `tui` and the other `--tool` variants are covered |
| M9 population audit re-run | Developer Advocate | Handover + 90 days |
| DORA lead time, 30-day rolling median ≤1 day | Analytics Reporter | Handover + 30 days |
| DORA change failure rate, 30-day rolling ≤15% | Analytics Reporter | Handover + 30 days |
| Deploy frequency trend, 90 days | DevOps Automator | Handover + 90 days |
| Golden-path regression re-proof | Workflow Optimizer | Handover + 90 days, then quarterly |
| M1 and M4 as defined, via a real human subject | DX Engineer | Next instrumented onboarding |
| M10 measured from an intervention log | DX Engineer | Next instrumented onboarding |

## 6. The operator's own stall log (a different artifact from clause 4.5)

Recorded because hiding them would be the same dishonesty this runbook exists to
remove. These are harness-author stalls, not subject stalls, and they do **not**
satisfy clause 4.5.

| # | Step | Duration | Cause | Fix |
| --- | --- | --- | --- | --- |
| 1 | clone | ~1 min | The mounted worktree's `.git` file named a host path the container could not see | Ship a self-contained `git bundle` instead of a working tree |
| 2 | pre-run check | ~1 min | The harness listed `/` instead of an empty work directory, and `ubuntu:24.04` ships no git or curl | Pin a `cleanroom.Dockerfile` that states the baseline machine |
| 3 | clone | <1 min | `$1` was not passed; the path file fell back to `main`, which the bundle did not carry | Read `$REF` from the environment |
| 4 | clone | <1 min | The bundle carried only commits, so untracked new scripts were absent | Commit before measuring |
| 5 | step count | ~2 min re-run | An instrument revision fused two assertions to print five steps | Reverted; the harness reports 6 measured steps, M6 reports 5 commands |
| 6 | all runs | 1 killed run | `\| head -18` closed the pipe and SIGPIPE killed the harness | Redirect instead of truncating |

## 7. What must happen before this can be called done

Ranked, as the Reality Checker ordered them:

1. **Recruit three real subjects** and run G4 properly, with consent, an
   intervention log and a recorded session. Nothing else unlocks 4.1–4.7.
2. **Let the window fill.** The merge landed as `ae559df` on 2026-11-05; 3.6–3.8
   close when the 20th post-rewrite default-branch run exists. Re-run
   `scripts/ci/ci_metrics.py` then — not before, and never against a mixed window.
3. **Wire the M5 counter** to real bootstrap attempts and reach 20.
4. **Name the platform owner** — a blocking input that was never supplied — and
   earn their written acceptance for 5.2.
5. **Decide, in writing, what "first success" means for a repository with no
   deploy surface**, or add one (issue #12 is the nearest analogue). Until then M1
   stays `UNMEASURED` and every "time to first success" claim is void.
6. **Extend `documented-commands`** to cover the `tui` surface headlessly and the
   remaining `--tool` variants, or narrow M8's claim to what CI actually executes.
7. **Reconcile `quality.yml`** — it is a second, weaker definition of lint+test
   (no coverage floor, `uv sync` without `--frozen`) and can be green while
   `ci/required` is red.

## 8. Verdict

The work genuinely removes friction a newcomer pays for: a broken binary that now
answers, a gate that now fails when it reports a failure, two guessed steps that
are now one owned command, two entry points that did not exist, and one of two
competing interactive surfaces removed rather than kept alongside the better one.
That is real.

It is **not** a certified developer-experience platform. G1 and G2 hold. G3 is no
longer blocked on a merge — the rewrite landed as `ae559df` and its window is open
at 2 of 20 runs — but it is blocked on that window filling, and on the M5 counter
reaching 20 instrumented attempts. G4 — the gate this runbook calls
non-negotiable — is not satisfied, because it requires timed human beings and none
were available. **NEEDS WORK**, and the ranked items above are the route out.

The single most valuable thing anyone can do next is not on this list: run three
people through the golden path and time them. Everything else is arithmetic that
will close itself.
