# Reality check — was this Developer Experience Platform run honest?

**Verdict: NEEDS WORK.**
**Claimed at handover:** G1 PASS, G2 PASS, G3 PASS, G4 partially measured, G5 pending.
**What the artifacts actually support:** G1 **FAIL**, G2 **PASS (2 clauses with caveats)**, G3 **FAIL** (5 clauses fail, 3 `UNMEASURED` and therefore fail by the runbook's own rule).

Default position was NEEDS WORK. It survived. But the run is **not fantasy** — the
parts that are measured are genuinely measured and independently reproducible, and
two of them I reproduced byte-for-byte. The dishonesty is concentrated in a small
number of places where a *claim* was fitted to a *document* rather than derived
from a *measurement*. Those places are named below with file and line.

Runbook under test: `strategy/runbooks/scenario-developer-experience-platform.md`
(`Definitions`:44-58, gates `G1`:122-125, `G2`:142-148, `G3`:183-201, `G4`:219-233, `G5`:250-254).

---

## 1. What I verified independently

Nothing below is taken from an orchestrator summary. These commands were run in
this working tree during the review:

| Check | Command | Result |
| --- | --- | --- |
| Evidence transcripts match the `/tmp` originals | `diff -q docs/dx/evidence/*.log /tmp/*.log` | **identical**, no tampering |
| Are the evidence transcripts actually in the change? | `git ls-files docs/dx/evidence/` | **empty — untracked.** Present in the working tree, never `git add`ed |
| Baseline CI percentiles reproduce | `uv run python scripts/ci/ci_metrics.py --limit 20` | CI **p50 33s / p90 51s** (19 runs), Quality **p50 42s / p90 58s** (20 runs), **0 flakes**, M2 `UNMEASURED` — matches `baseline.md`:49-50 exactly |
| Roster size | `uv run agency-agents install --tool claude-code --dry-run` + recursive count of the 18 division dirs | **298 agents** — the 298 is real |
| Install output surface | `uv run agency-agents install --tool claude-code --scope user --dry-run` | dry run prints the plan; **real run prints only `✓ Installation process completed!`** (`cli/main.py`:395) |
| Local gate coverage | `./scripts/gate.sh --list` | **8 checks**, covering `lint`/`types`/`test`/`verify-manifest`/`security` — **not** `documented-commands` |
| Lint gate actually fails now | read `cli/main.py`:99-110 + `scripts/ci/assert_lint_fails.sh` | `raise typer.Exit(code=1)` on every catalog error, with a regression guard wired into CI (`ci.yml`:117-120) |
| Deprecation claim | `grep -rn TUIWizard` | **still present** at `infrastructure/tui.py`:33, imported `cli/main.py`:25, called `cli/main.py`:318 |

> **Resolved after this verdict.** `infrastructure/tui.py` and its test are deleted. `install` with no flags now opens the browser, so the deprecation the documents claimed has actually happened. The finding stands as written because it was true when it was made.
| Baseline tree validity | `git log --date=iso`, commit times vs transcript stamps | baseline ran 2026-11-05T14:57Z, i.e. **before** the 16:26Z commits; branch was still `main`@`1452c6d` — `baseline.md`:12 is truthful |

**Integrity credit, stated plainly:** the two evidence transcripts are
byte-identical to the `/tmp` originals, the baseline was genuinely taken against
`main`'s tree before any work landed, the CI baseline numbers reproduce on demand,
and the clean-room image (`scripts/ci/cleanroom.Dockerfile`:12-20) is a real
`ubuntu:24.04` with only `git`/`curl`/`ca-certificates` — Python, uv and
`agency-agents` genuinely absent, proven by the pre-run `which` block. That is
more evidentiary discipline than most runs of this kind produce.

---

## 2. Clause-by-clause

Counting rule from the runbook (`:200-201`): *"A clause with no post-rewrite
observation yet is reported as `UNMEASURED`, and `UNMEASURED` fails that clause."*

### G1 — `baseline.md` (2 clauses)

| Clause | Status | Evidence |
| --- | --- | --- |
| **1.1** Every metric M1-M10 measured with its source named, or `UNMEASURED` with a reason, **an owner**, and a date | **FAIL** | 8 of 10 rows meet the standard ("Measured baseline" table `baseline.md`:47-56). **M9** (`:55`) gives value "Not counted at baseline", status `UNMEASURED`, and a `—` in place of reason/owner/date — no owner, no date. **M10** (`:56`) gives a reason but no owner and no date. The document's own opening promise (`:4-5`) is "reason, an owner and a measurement date". M2 (`:58-72`) shows what compliance looks like and M9/M10 do not reach it. This is a completeness defect, not a fabrication. |
| **1.2** M1 baseline entry present, never blank | **PASS** | `baseline.md`:47 — "No documented path completes", supported by `evidence/baseline-transcript.log`:127-136 (`step_5_exit: 1`, `step_5_FAILED: true`, `harness_exit: 1`). |

**G1: FAIL** (1 PASS, 1 FAIL). Claimed PASS. The claim is wrong on 1.1.

### G2 — `golden-path.md` (4 clauses)

| Clause | Status | Evidence |
| --- | --- | --- |
| **2.1** ≤ 6 steps, each with a named owner | **PASS** | `golden-path.md`:8-14 — 5 rows, an owner per row. Caveat: the "5" is a retrofitted count (§4.1); the honest *distinct-command* count is 6. Both are ≤ 6, so the ceiling is met either way. |
| **2.2** No two steps share an owner without a handoff note | **PASS** | Steps 1 and 2 share Platform Engineer; note H1 at `golden-path.md`:18-29, and it is closed in code, not prose — `bootstrap.sh` refuses outside a git tree (`bootstrap.sh`:73-80). |
| **2.3** Friction measured at baseline, or `UNMEASURED` with a Phase 3 owner and date | **PASS** (weak) | `golden-path.md`:74-80. Steps 1 and 4 measured (2s, 8s from the baseline transcript). Steps 3 and 5 declared `UNMEASURED` with owners. Caveat: the "date" is the string "Phase 4 run" — a phase label, not a date — and Phase 4 has not run, so both instruments are still unfilled. |
| **2.4** Every mandated-vs-optional decision recorded by the Product Manager with the senior hours it saves | **PASS** (on form) | `golden-path.md`:57-63 — 5 rows, mandate/optional/removed status, hours for each including an explicit `0 h` for the optional tool step, which is exactly what the clause demands. **But the totals line (`:65-67`) is fabricated — see §4.4.** The clause gates on the record existing with a costed figure, and it does; the headline number does not survive scrutiny. |

**G2: PASS** (4 PASS, 2 with caveats). Claimed PASS. This is the one gate whose
claim is broadly defensible.

### G3 — (9 clauses)

| Clause | Status | Evidence |
| --- | --- | --- |
| **3.1** M8 = 100%: every documented command exits 0 in CI | **FAIL** | The `documented-commands` job (`ci.yml`:86-120) runs 6 commands. It does **not** run the full gate (only `./scripts/gate.sh --list`, `:116`), does **not** run `tui` (documented at `README.md` "Or browse the roster"; `cli-faq.md`:30 records that a pipe exits 1, so it can never be an M8 sample), and does **not** run 16 of the 19 `install --tool X` variants the README documents (`quality.yml`:72-74 covers only `antigravity`, `pi-agent`, `oh-my-pi`). No enumerated denominator exists anywhere, and there is no CI run recorded for this branch. M8 cannot be stated as 100%. |
| **3.2** Every deprecated-path entry has its removal commit **merged** | **FAIL** | `golden-path.md`:88-93 has a "Removed in" column containing the word "Phase 3" for all four rows — **no commit SHA**. Nothing is merged: `git log origin/main..HEAD` is 7 unmerged commits, `origin/main` is still `1452c6d`. Worse, one row is **factually false**: `golden-path.md`:92 says `TUIWizard` was "deleted in the same change per D-001", and `m7-tool-decisions.md`:243 promises "the numbered-list methods do not survive the browser" — but `TUIWizard` is live and `tui.py` is **not in the diff at all** (`git diff origin/main --stat -- infrastructure/tui.py` is empty). |
| **3.3** M7 = 100% of tool decisions, M7 criteria, exit path | **FAIL (coverage)** | The two recorded decisions are genuinely strong — `m7-tool-decisions.md` D-001 (`:47-251`) and D-002 (`:252-386`) each carry weighted criteria written before scoring, multiple scored candidates, reproduced arithmetic, a sensitivity check, a verdict and an exit path, and `:387-475` openly documents where the orchestrator draft's arithmetic did not reproduce. That is real work. But the denominator is self-selected: the runbook's own Key Decisions table (`runbook`:275) names the build-vs-adopt questions as **"task runner, dev container, portal"**, and `grep -n "mise\|gate.sh\|task runner\|dev container\|portal" docs/dx/m7-tool-decisions.md` returns **nothing**. The project wrote its own task runner (`scripts/gate.sh`) while `gate.md`:35-40 documents that `mise` and the workflows disagree — the most consequential build-vs-adopt call in Phase 3, and it has no M7 record. 2 of 2 recorded ≠ 100% of required. |
| **3.4** Every Phase 3 step has a before/after M6 count; total ≤ 6 | **FAIL** | The ≤ 6 sub-clause holds numerically (5, or 6 honest). The "before/after step count for every removed step" sub-clause (`runbook`:172-173, `:188`) is **unproven**: the four removed paths at `golden-path.md`:88-93 carry no before/after counts. And the total rests on an instrument retrofitted to the document (§4.1). |
| **3.5** M9 = 0 (no sample pins an SDK version other than the released one) | **PASS** (vacuous) | `m9-stale-samples.md`:3-30 — the population is empty (this repo ships persona markdown, not an SDK), so 0 stale samples holds trivially; the audit commands are re-runnable. Two nits: it invents a third state, `NOT APPLICABLE`, which the runbook does not define (only measured or `UNMEASURED`), and its own "nearest real drift" section (`:34-35`) reports two doc defects that **do not exist at HEAD** (`bootstrap.md`:35 and `golden-path.md`:91 both carry the corrected text) — a stale document about staleness. |
| **3.6** M2 interim, p50 ≤ 12 min / p90 ≤ 18 min over the gate window | **UNMEASURED → FAIL** | Gate window = "the first 20 post-rewrite default-branch runs" (`runbook`:50). The rewrite is not on `main`, so the window holds **0 runs**. `ci_metrics.py` cannot even express the window — it has no post-rewrite filter at all, only `--limit` over the newest runs on a branch (`ci_metrics.py`:69-86, `:177`). |
| **3.7** M3 interim, p50 ≤ 25 min / p90 ≤ 35 min over the same window | **UNMEASURED → FAIL** | Same empty window. The baseline M3 figures are real and I reproduced them, but they are **pre-rewrite baseline material** and the runbook says those "never enter a gate window" (`:49`). |
| **3.8** M4 flake ≤ 4% over the window, every flake owned with a fix-by date | **UNMEASURED → FAIL** | Same empty window, and there is no flake-quarantine list with owners/dates. Additional instrument defect: `ci_metrics.py`:129-138 groups by `headSha` to detect flakes but ignores the `event` and `attempt` fields it fetched at `:79` — a `pull_request` failure and a `push` success on the same SHA are not a re-run, so M4 can overcount. It reported 0 in the baseline window, so no number was inflated here, but the instrument is not faithful to the definition. |
| **3.9** M5: **≥ 20** instrumented clean-machine bootstrap attempts since the rewrite, failure ≤ 5%, zero off-path-command failures | **FAIL** | **Two** golden-path attempts exist (`/tmp/goldenpath-proof.log`, `/tmp/goldenpath-proof-final.log`), both green; plus one baseline attempt. That is **10% of the required sample**. `cleanroom_onboarding.sh` runs exactly one attempt per invocation and has no batch mode (`:95-168`). |

**G3: FAIL** (1 PASS, 5 FAIL, 3 UNMEASURED). Claimed PASS. The claim is not
supported by any artifact — there is **no G3 gate record in the repository at
all**. `grep -rn "3\.1\|3\.6\|3\.9" docs/dx/` returns only incidental string
matches; `docs/dx/scorecard.md`, cited by `baseline.md`:150, **does not exist**;
`docs/dx/evidence-pack.md`, cited by `docs/dx/evidence/.gitignore`:2, **does not
exist**. G3's verdict lives only in the handover summary.

---

## 3. Overall verdict

### **NEEDS WORK**

| Gate | PASS | FAIL | UNMEASURED |
| --- | --- | --- | --- |
| G1 | 1 | 1 | 0 |
| G2 | 4 | 0 | 0 |
| G3 | 1 | 5 | 3 |
| **Total (15 clauses)** | **6** | **6** | **3** |

`UNMEASURED` is not a neutral holding state here: the runbook converts it to a
failure (`:200-201`). So the effective tally is **6 PASS / 9 not-PASS**.
G3 is **BLOCKED**, not merely failing, because three of its clauses cannot be
attempted at all until the rewrite is on `main`.

### The three most serious findings

**(1) The five-step count is a measurement retrofitted to the document.**
`/tmp/goldenpath-proof.log` — a green run, `steps_failed: 0` — recorded **six
steps** (`prove-it-landed` + `observe-installed-agents`). Commit `163d2c2`
("fix(dx): measure five steps, matching the documented path") then **merged the two
into one `run_step`**, wrapping two distinct commands (`agency-agents verify --all`
and `find … | wc -l`) in a single `bash -c` block, and re-ran to get five. The
commit message is candid about the motive: *"which measured six steps against a
document that declares five."*
The developer's actual work is **identical** between the two runs. M6 is defined as
*"distinct commands from clone to first success"* (`runbook`:56) — not as
`run_step` invocations in a harness. Two distinct commands are still two distinct
commands inside one wrapper. The document was never corrected; the instrument was
bent to match it. This is the exact inversion of the runbook's doctrine ("a
documented path nobody executed is not a path") and of its own named pitfall. The
honest count is **6** — which still passes the ≤ 6 ceiling — so the retrofit bought
nothing except a claim. It cost the run its credibility on M6.

**(2) "First success" was silently redefined, so 116s is not M1.**
The runbook's definition (`:44`) is exact: *"the subject's own change is deployed
by the documented path **and** an observability query returns data for it."*
The harness measures neither. `golden-path.sh`:36-46 treats writing the shipped
catalog into `~/.claude/agents` as a "deploy" and a passing `convert-outputs.sha256`
check as the "observable outcome". There is **no deploy workflow** in this repo
(`.github/workflows/` is ci, codeql, labels-sync, quality, release) and
**no observability surface anywhere** (`grep -ri observability docs/dx/ .github/`
returns nothing). There is also **no subject's change** — the run installs the
shipped 298-agent catalog, the same artifact the baseline run produced; nobody
wrote code and watched it land. So `totals_seconds: 116` is a real number for a
real thing ("the documented commands exit 0 on a clean machine in 116s"), but
calling it time-to-first-success, or letting G4 4.3/4.4 be judged against it, is a
definitional drift that is disclosed nowhere. `baseline.md`:137-150 discloses the
*human-subject* gap honestly; it does not disclose that the metric's referent is
absent from the repository.

**(3) A deprecation was claimed that did not happen.**
`golden-path.md`:92 and `m7-tool-decisions.md`:243 both assert `TUIWizard` and its
numbered-list selection methods were deleted in this change. They were not.
`infrastructure/tui.py`:33 still defines `TUIWizard`, `cli/main.py`:25 imports it,
and `cli/main.py`:318 still calls `TUIWizard(...).run(...)` on the bare-wizard path.
`tui.py` does not appear in `git diff origin/main` at all. Combined with the
"Removed in: Phase 3" column (`golden-path.md`:88-93) carrying no commit SHAs and
nothing being merged, G3 3.2 fails outright: no deprecated-path entry has a
**merged removal commit**, and one of the four is affirmatively untrue.

**A fourth, endemic problem — quality of self-description.** Several documents
describe the CLI as doing things it does not:
- `golden-path.md`:13 says step 4 "prints what landed" and `:14` says step 5 shows
  "the install summary … names the files written". The real run prints one line,
  `✓ Installation process completed!` (`cli/main.py`:395), with no tool name, no
  count, no paths — confirmed at `evidence/golden-path-transcript.log`:345-349. The
  298 comes from the harness's own `find | wc -l`, which is not a command the docs
  tell a newcomer to run.
- `gate.md`:3-5 says the gate "runs the exact commands `.github/workflows/ci.yml`
  runs", and the new `CONTRIBUTING.md` "Development setup" section says "a green
  gate means a green CI run". Both are false: `gate.sh --list` shows 8 checks and
  the `documented-commands` job (`ci.yml`:86-120`) is not among them. A newcomer
  can pass the gate and still fail CI on exactly the surface (bootstrap, console
  script) whose breakage created this run.
- `README.md` documents `uv run agency-agents tui --tool claude-code`, which
  `cli-faq.md`:30 itself records "a pipe exits 1" — a documented command that can
  never be proven in CI, published two files away from the doc that says so.

The CLI surface claims that *are* checkable hold up: all 19 `--tool` values in the
README match `tools.json`; `install --list runbooks` really returns 42
(`strategy/runbooks.json`); the 298 roster count is real; the `pyproject.toml`:16
entry-point fix (`agency_agents.cli.main:main`) is correct and minimal; and the D2
lint fix (`cli/main.py`:99-110`) is real and guarded by
`scripts/ci/assert_lint_fails.sh`.

---

## 4. The specific hunts

### 4.1 M6 step count — apples to apples?

**No.** Three separate asymmetries, only one of which is disclosed.

1. **Retrofitted post-hoc** (§3.1): 6 → 5 by relabelling, after a document already
   said 5.
2. **Different scope.** `baseline.sh` runs 5 steps but **omits the verification
   steps CONTRIBUTING documents** — its own comment (`baseline.sh`:13-14`) cites
   `uv run python -m agency_agents lint`, `uv run pytest` and `verify`, and then
   never runs them. The golden path **folds all of that into step 3**
   (`./scripts/gate.sh`, 8 checks, 291 tests, 39s network audit —
   `evidence/golden-path-transcript.log`:153-343`). So the final path does
   materially more work in the same slot count. That cuts in the change's favour
   on step count and against it on wall clock — but it means the two paths are not
   measuring the same journey.
3. **"116s vs 34s" is therefore not a comparison.** 80 of the 116 seconds are the
   gate, 39 of which are a network `pip-audit` the baseline never ran.

The honest framing, which `golden-path.md`:42-50 mostly gives: a **flat count**
with **undocumented steps 2 → 0**. That is a real and valuable win. The
relabelling in `163d2c2` is the part that is not honest, and it was unnecessary —
6 ≤ 6.

### 4.2 G3 clause 3.9 (M5, ≥ 20 attempts) — claimable?

**No.** Two golden-path attempts plus one baseline attempt; the clause wants ≥ 20
**since the rewrite**. Honest status:

> **M5: `UNMEASURED` — 2 instrumented clean-machine bootstrap attempts, both
> green (0% failure), against a required sample of 20. 10% of the threshold, so the
> ≤ 5% failure rate is not statistically meaningful and cannot be claimed.**

The failure *rate* is 0/2 and the harness genuinely proves cleanliness
(`cleanroom_onboarding.sh`:105-128), so the direction is good. The sample is not
there. A batch mode (`--attempts N`) plus a results table would make this
claimable; nothing of the kind exists.

### 4.3 G3 clauses 3.6 / 3.7 / 3.8 (M2/M3/M4 over the first 20 post-rewrite runs) — claimable?

**No, and they are not even *approachable*.** The rewrite is 7 unmerged commits;
`origin/main` is `1452c6d`. Post-rewrite default-branch runs: **0**. Honest status
for all three: **`UNMEASURED`**, which the runbook turns into a failure.

Two further obstacles that would survive a merge:
- `ci_metrics.py` implements **no post-rewrite filter**. It takes the newest `N`
  runs on a branch. Once the rewrite lands, `--limit 20` silently mixes pre- and
  post-rewrite runs until 20 post-rewrite runs exist, and never reports
  "insufficient window" — it reports a percentile over whatever it found. The
  instrument cannot produce the gate window as defined.
- The M4 flake detector ignores `event`/`attempt` (§3.8), so it can count a PR
  failure plus a push success on one SHA as a flake.

### 4.4 The 13.0 hours — measured or invented?

**Invented, and mislabelled as measured.** `golden-path.md`:65 reads *"Total
**measured** senior time removable per onboarding: **13.0 hours**"*. Its own
derivation is `4.0 + 2.5 + 0 + 0.5 + 6.0` (`:59-63`). Every addend is an
unsourced assertion, and the inputs that could source them do not exist:

- `baseline.md`:56 says M10 is `UNMEASURED` — "no onboarding run has ever been
  instrumented". So the baseline for senior hours is, by this run's own admission,
  non-existent.
- **No intervention log exists** in the repository (`find . -iname "*intervention*"`
  → nothing), and there is no onboarding-ticket data.
- `golden-path.md`:66-67 then cites "baseline M10 target was 24 hours from the last
  5 hires" — a figure `baseline.md` explicitly declined to adopt, recording
  `UNMEASURED` instead. The two documents contradict each other, and the
  `golden-path.md` figure is the one with no source.

The largest single item, **6.0 h for "hand-rolling a venv without uv"**, is 46% of
the total and is pure assertion. The honest sentence is: *"Estimated senior time
removable per onboarding: 13.0 hours (estimated, not measured — M10 is
`UNMEASURED` at baseline and no intervention log exists; this becomes a
measurement at G4 clause 4.7)."* G2 clause 2.4 passes on the *record*; this
number does not.

### 4.5 Where documents contradict the code

| Claim | Location | Reality |
| --- | --- | --- |
| `TUIWizard` deleted in this change | `golden-path.md`:92, `m7-tool-decisions.md`:243 | Still live: `infrastructure/tui.py`:33, `cli/main.py`:25,`:318`; file untouched |
| Install "prints what landed" / "names the files written" | `golden-path.md`:13-14 | Prints `✓ Installation process completed!` only — `cli/main.py`:395, transcript `:345-349` |
| Gate = "the exact commands ci.yml runs" / "green gate means green CI" | `gate.md`:3-5, `CONTRIBUTING.md` "Development setup" | 8 checks; the `documented-commands` job (`ci.yml`:86-120`) is absent from `gate.sh` |
| `agency-agents tui` is a documented command | `README.md`, `cli-faq.md`:30-42 | Cannot be executed in CI ("a pipe exits 1") — so M8 can never reach 100% |
| Both docs list a stale-pin/doc-drift defect | `m9-stale-samples.md`:34-35 | Both "defects" are already fixed at HEAD — the M9 doc is itself stale |
| `docs/dx/scorecard.md`, `docs/dx/evidence-pack.md` | `baseline.md`:150, `evidence/.gitignore`:2 | Neither file exists — G5 clauses 5.1/5.3/5.4 have no target |
| The evidence pack is delivered as part of the change | `docs/dx/evidence/.gitignore`:1-5 | The directory is **untracked**: `git ls-files docs/dx/evidence/` is empty. The `.gitignore` exists specifically so the logs "would otherwise silently drop" — but they were never added. A clone of this branch loses the transcript every metric cites |

README/CONTRIBUTING command accuracy that **does** check out: 19/19 `--tool`
values valid, 42 runbooks, 298 agents, `pyproject.toml`:16 entry point correct,
`--runbook` mutually exclusive with `--division` (`cli-faq.md`:15) matches the
CLI's own rejection path.

---

## 5. G4 / G5 — what would have to be true

G4 is correctly reported as partially measured: 4.1/4.3/4.4/4.7 are `UNMEASURED`
for want of a human subject, and `baseline.md`:137-150 says so plainly — that is
the single most honest paragraph in the pack. G4 as a *gate* is **FAIL**, and it is
blocked on more than recruitment:

- 4.5 requires a stall log (`runbook`:225). **None exists** — `newcomer-reading-path.md`
  is a source-derived reading map, not a stall log with step and duration.
- 4.6 requires written consent, a retention window and a viewer list
  (`runbook`:226-228). There is no consent artifact anywhere
  (`find . -iname "*consent*"` → nothing).
- 4.1/4.3/4.4 require the *runbook's* first-success definition, which has no
  referent in this repo (§3.2). A recorded human session will not fix that.

G5 is **pending** and correctly so; 5.1 has no scorecard and 5.2 has no named
owner with written acceptance.

### Ranked — must be fixed before G4/G5 can be claimed

1. **Restore M6 to the honest measurement.** Revert the `163d2c2` relabel (or
   re-document `golden-path.md` as six steps) and record `verify --all` and the
   install-summary check as two distinct commands. 6 ≤ 6, so nothing is lost
   except the inflation. Fix the before/after count for the four removed paths
   (`golden-path.md`:88-93`) — G3 3.4.
2. **Write the missing G3 gate record, honestly.** Create `docs/dx/scorecard.md`
   (cited by `baseline.md`:150 but absent) and state 3.1/3.2/3.3/3.4/3.9 as FAIL
   and 3.6/3.7/3.8 as `UNMEASURED`-until-merged. G3 cannot be PASS with 0
   post-rewrite runs.
3. **Track the evidence pack.** `git add docs/dx/evidence/` and write the missing
   `docs/dx/evidence-pack.md` and `docs/dx/scorecard.md`; an untracked transcript
   is not an artifact a reviewer or a re-run can reach.
4. **Merge the rewrite, then measure the gate window.** Only then can 3.6/3.7/3.8
   start. First add a post-rewrite filter and an insufficient-window guard to
   `ci_metrics.py`, and fix the flake detector to respect `event`/`attempt`.
5. **Instrument M5 to 20 attempts.** Add `--attempts N` batching and record a
   results table; 2 attempts is 10% of the clause.
6. **Make the deprecation claim true or withdraw it.** Either actually remove
   `TUIWizard` (and its tests) in a merged commit, or delete `golden-path.md`:92
   and `m7-tool-decisions.md`:243. Put real commit SHAs in the "Removed in"
   column.
7. **Reconcile gate and CI.** Either add the `documented-commands` job to
   `gate.sh`, or correct `gate.md`:3-5 and the new `CONTRIBUTING.md` claim to say
   the gate mirrors five of six jobs. As written, a green gate does not imply green
   CI — which is the defect this whole run exists to remove.
8. **Define M8's denominator.** Enumerate the documented commands, state which CI
   job executes each, and report a real pass rate. Treat `tui` and the `install
   --tool` variants explicitly rather than silently excluding them.
9. **Relabel the 13.0 hours as an estimate** and drop the 24-hour baseline claim
   that contradicts `baseline.md`:56, or source both from an intervention log.
10. **Fix M9/M10 in `baseline.md`** so G1 1.1 is literally true (owner + date), or
    amend the clause standard to match the table.
11. **Resolve the first-success definition.** Record an explicit scope decision
    that this repo's "deploy" is an install to a tool directory and that there is
    no observability query — or G4's 4.1/4.3/4.4 stay unclaimable forever.

---

## 6. What this run honestly achieved

Stated without inflation, because the useful part of this review is that these
things are real:

- **A broken entry point is genuinely fixed.** `pyproject.toml`:16 now maps to a
  callable that exists; `bootstrap.sh` phase 5 proves it answers
  (`evidence/golden-path-transcript.log`:134-138). This was a real, shipped P0.
- **A gate that printed red and exited 0 now exits 1** (`cli/main.py`:99-110),
  with a regression guard (`scripts/ci/assert_lint_fails.sh`) wired into CI
  (`ci.yml`:117-120). Real fix, real guard.
- **Undocumented steps went from 2 to 0.** `install-uv` and `uv-sync` — folk
  knowledge at baseline (`baseline.sh`:25-34) — are now inside one owned command.
  A clean `ubuntu:24.04` with only `git` really does reach a working console
  script, and I can see it happen in the transcript.
- **The baseline is real and reproducible.** Genuinely taken on `main`'s tree
  before any work, and its M3/M4 numbers reproduce on demand
  (`ci_metrics.py --limit 20`). The M2 `UNMEASURED` reasoning
  (`baseline.md`:58-72) — "not zero, no sample" — is exactly right and is the kind
  of distinction most runs get wrong.
- **Evidence discipline is above average in intent.** The transcripts are
  byte-identical to the originals and the clean-room image is a stated, minimal
  environment rather than an assertion, with every claim pointing at a re-runnable
  command. The delivery is the weak part: the transcripts sit in an **untracked**
  directory, so the change does not actually ship the evidence it cites.
- **The M7 work is strong where it exists** — weighted criteria fixed before
  scoring, arithmetic reproduced by hand, a sensitivity check, and a section
  (`m7-tool-decisions.md`:387-475`) that openly reports where the orchestrator
  draft's numbers failed to reproduce. Self-correction of that kind is rare.
- **The run states its own limitation.** `baseline.md`:137-150 refusing to call an
  engineer-run container a human subject is the reason this review is worth
  writing: the run tried to be honest about the one thing it could not have.
  `/tmp/goldenpath-proof.log` was also left on disk rather than hidden, which is
  how I could reconstruct finding (1).

The gap between "NEEDS WORK" and "BLOCKED" here is small. G2 is defensible; G1 is
one table fix away; G4's honest gap is the run's best feature. What blocks
certification is not fabrication anywhere except the 13.0-hour figure — it is
**three measurement claims that outran their instruments**: a step count edited to
match a document, a first-success definition with no referent, and a gate recorded
as PASS with an empty measurement window.

---

**Reviewer:** Reality Checker (integration/testing)
**Default applied:** NEEDS WORK; not departed from
**Method:** artifact-first — every claim cross-checked against files, transcripts
and re-runnable commands; no claim accepted on the strength of prose
**Evidence location:** `docs/dx/evidence/`, `/tmp/cleanroom-20261105T145724Z.log`,
`/tmp/goldenpath-proof-final.log`, `/tmp/goldenpath-proof.log`
**Re-assessment required:** after fixes 1-3 above, and before G4 recruitment
