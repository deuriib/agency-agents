# Runbook: Developer Experience Platform

Mode: NEXUS-Sprint | Duration: 6 weeks | Agents: 15

## Scenario

Onboarding takes two weeks and three senior engineers. Nobody gets a local environment running from the README alone. CI takes 40 minutes to fail. Nobody can state the lead time for a change. Every SDK sample in the docs is two versions stale.

That cost lands twice: engineers rebuild the environment by trial and error, and changes queue behind the few people who know the undocumented steps.

This runbook removes every step between a developer and their first successful deploy, then proves it by timing a real person on a clean machine. The doctrine: **a documented path nobody executed is not a path.** Anything needing a senior engineer's help is a platform defect, not a trait of the newcomer. Scope is clean machine to deployed, observable code — not repo governance or a public API product.

## Applicability

| Use this runbook when | Use a different runbook when |
| --- | --- |
| Developer throughput and time to first success are the constraint | The repo lacks governance — use `repository-hardening-program` |
| Clone-to-deploy is undocumented, manual, or senior-dependent | The code must be restructured — use `codebase-modernization-program` |
| CI is slow, flaky, and change lead time is unknown | External developers need a contract — use `api-platform-launch` |
| Docs and samples have drifted from shipped code | Contribution and release cadence — use `oss-maintainer-operations` |
| Senior hours per hire must drop | One feature into a healthy product — use `enterprise-feature` |

## Required Inputs

| Input | Why it blocks | Owner |
| --- | --- | --- |
| The identity of the platform owner, named before Week 1 | Unowned paths regress in a quarter; the person is named up front and their written acceptance is earned at G5, never negotiated there | Agents Orchestrator |
| The raw baseline source for time to first success, or a written statement that no source exists | Decides whether Phase 5 claims a delta or only an absolute target; a raw source arrives unadjudicated | Analytics Reporter |
| CI/CD admin access: pipelines, runners, secrets, deploy targets | Nothing can be measured or shortened read-only, and there is no sandbox to deploy into without a target | DevOps Automator |
| A first-time test subject who has never set up this environment, recruited before Week 1 | The DX Engineer's own run is not evidence | DX Engineer |
| A metrics source: per-workflow CI run history, deploy timestamps, incident log | Every gate below fails on a number with no stored source behind it | Analytics Reporter |
| Written consent from each test subject, plus the retention window and the viewer list for the evidence pack | A recorded session of a real person without consent is a liability, not evidence | Evidence Collector |

Every input above is observable before day 1, and nothing a gate produces is also an input: the owner's identity is named up front and their signature is earned at G5, and the baseline arrives as a raw source or as an explicit "no source exists" statement that G1 adjudicates.

The baseline never blocks the run, and it is never assumed: an environment nobody has measured is admitted at G1 as `UNMEASURED` with a reason, an owner, and a measurement date. The difference is only in what may be claimed — with an unmeasured baseline, M1 is judged on the absolute target and no "improved by" line may appear in the scorecard.

## Definitions

Every threshold below is defined here; a gate fails on the observation that the definition names.

| Term | Definition used by every gate |
| --- | --- |
| First success | The moment the subject's own change is deployed by the documented path **and** an observability query returns data for it. A local green test run is not first success; a deploy nobody can see is not first success. |
| Time to first success (M1) | Wall clock from the `clone` command to first success, on a clean machine, by a subject using only the docs. Failed attempts and waiting count. Subject breaks and interventions do not — an intervention voids the run. |
| Clean machine | A fresh VM image with no prior copy of the repo, no language runtime from this project, and no cached credential, proven by an empty pre-run `ls` and `which` transcript captured by the Evidence Collector. |
| Intervention | Any senior-engineer action that changes the subject's environment, supplies a credential, or names a command for the subject. One intervention voids the run. A stall the subject resolves alone is not an intervention. |
| Senior hours per onboarding (M10) | Sum of senior-engineer time touching a subject's environment during the run, from the intervention log plus onboarding-channel tickets. M10 is a platform cost measure: it is reported per onboarding run and never attributed to an individual for performance purposes. |
| Post-rewrite run | A completed default-branch run whose pipeline is the one built in Phase 3 — the first commit carrying the new workflow file, and every run after it. Pre-rewrite runs are baseline material and never enter a gate window. |
| Gate window (M2-M4) | The first 20 post-rewrite default-branch runs of a workflow. It is the only window any gate in this runbook reads; the 100-run trend is a Post-runbook commitment. |
| Recorded session | Video plus terminal transcript of one subject's run, captured with that subject's written consent before recording starts, retained 90 days past handover and then deleted, with secrets, tokens and customer data redacted before storage, viewable only by the DX Engineer, the Evidence Collector, the Reality Checker and the subject. |
| CI time to first failure (M2) | Run start to the first failed job reporting a failing step, p50 and p90 over the gate window. |
| CI pipeline duration (M3) | Run start to terminal status of the full default-branch workflow, p50 and p90 over the gate window. |
| Flake (M4) | A run that fails and is re-run to green with no code, config, or dependency change in between. Flake rate = flakes ÷ runs over the gate window, per workflow. |
| Bootstrap failure (M5) | A bootstrap attempt on a clean machine that exits non-zero, or that needs a command absent from the documented path. |
| Step count (M6) | Distinct commands from clone to first success, plus manual UI actions (ticket, approval, secret copy, dashboard click-through). |
| Tool decision pass (M7) | A build-vs-adopt decision that names at least three weighted criteria, scores at least two candidates against them, and records a verdict plus an exit path. Anything less is a fail, not a partial pass. |
| `UNMEASURED` | A metric with no source in the baseline, recorded with reason, owner, and measurement date. It is never a pass. |

## Agent Roster

Every row carries the gate or metric that fails when its work is missing. Ownership is singular: one metric, one owner, and the owner column of Success Criteria is the canonical list. An agent may measure or build against a metric it does not own without becoming a second owner.

### Command (Always Active)

| Agent | Role | Earns its place (gate / metric) |
| --- | --- | --- |
| Agents Orchestrator | Phase gating, Dev↔QA loop, gate re-runs | G1-G5 arbitration |
| DX Engineer | Golden path, friction inventory, timing | M1, M10, G4 |
| Product Manager | Friction ranked by cost, mandated-vs-optional decisions with the senior hours each saves | G2 clause 2.4 |

### Platform Build (Phase 2-3)

| Agent | Role | Earns its place (gate / metric) |
| --- | --- | --- |
| Platform Engineer | Bootstrap, toolchain pinning, old-path removal | M5, G3 |
| Developer Tooling Engineer | Task runner, hooks, local↔CI parity | M3, G3 |
| SRE (Site Reliability Engineer) | Observability, instrumentation, safe deploy | G4 (observability query on the subject's change), G5 alert routing |
| DevOps Automator | Fast-failing pipeline, self-serve deploy | M2, G3 |

### Onboarding Path (Phase 3)

| Agent | Role | Earns its place (gate / metric) |
| --- | --- | --- |
| Codebase Onboarding Engineer | Source-derived newcomer map, stall log | G4 clause 4.5 (stall log), G3 |
| Technical Writer | Tested quickstart, troubleshooting index | M8, G3 |
| Developer Advocate | Samples that preempt questions | M9, G3 |

### Measure (Phase 1, 4)

| Agent | Role | Earns its place (gate / metric) |
| --- | --- | --- |
| Analytics Reporter | CI percentiles, flake rate, per-subject timings, DORA queries | G1, Post-runbook DORA |
| Tool Evaluator | Build-vs-adopt verdicts with stated criteria, exit paths | M7, G3 |
| Workflow Optimizer | Friction timing, before/after step counts, flake quarantine, ranked fixes | M4, M6, G4 |

### Proof (Phase 5)

| Agent | Role | Earns its place (gate / metric) |
| --- | --- | --- |
| Evidence Collector | Consented, redacted recorded sessions, terminal logs, screenshots per claim | G4 clause 4.6 (consent and redaction), G5 |
| Reality Checker | Honest-run verdict, default NEEDS WORK | G4, G5 |

## Phase 1: Measure the Baseline

Nothing is built until the before-state is frozen. Claims are recorded as claims, not data.

```text
Week 1: Freeze the before-state
├── DX Engineer → friction inventory: every step a newcomer performs, with the
│   instrument that measures it today
├── Analytics Reporter → M2 and M3 percentiles plus M4 flake rate, from the last
│   100 runs per workflow (baseline window only; the gate window is defined above)
├── Analytics Reporter → DORA lead time, deploy frequency and change failure rate
│   queries stored with their result snapshot (reported post-runbook)
├── Workflow Optimizer → M6 step count and per-step timing, ranked by engineer-hours
├── Codebase Onboarding Engineer → setup steps the docs omit, read from source and
│   CI config
├── Tool Evaluator → build-vs-adopt questions, candidate lists, M7 criteria
└── Quality Gate G1: the baseline document is signed by the DX Engineer and the
    Analytics Reporter, and every clause below holds.
    1.1 Every metric in M1-M10 is either measured with its source named or marked
        UNMEASURED with a reason, an owner, and a date.
    1.2 The M1 baseline entry is present — a measured value, or an explicit "no
        source exists" admission. Never blank.
```

## Phase 2: The Golden Path

One path, named, numbered, owned. Parallel supported paths are how the current state happened.

```text
Week 2: Design the only supported route
├── DX Engineer → six steps, the only supported route; alternatives get removal
│   dates
├── Platform Engineer → pinned toolchain; bootstrap is one command with
│   actionable failures
├── Product Manager → mandated vs optional steps, each decision recorded with the
│   senior hours it saves; platform matrix costed in senior hours
├── Tool Evaluator → M7 criteria written before any candidate is scored
└── Quality Gate G2: the path is published and every clause below holds.
    2.1 Six or fewer steps (M6), each with a named owner.
    2.2 No two steps share an owner without a handoff note.
    2.3 A step's friction is either measured at baseline or declared UNMEASURED at
        G1 with a Phase 3 instrumentation owner and date.
    2.4 Every mandated-versus-optional decision is recorded by the Product Manager
        with the senior hours that choice saves. A step left optional with no
        costed saving fails here, and no other agent can supply that record.
```

| Step | How the friction is measured today | Target friction | Instrument that fails the gate | If no measurement exists today |
| --- | --- | --- | --- | --- |
| Clone | Stopwatch in the Phase 1 friction inventory on a clean machine; checkout size from `du -sh` after clone | Under 2 minutes, no ticket | M1 step timing, recorded session | Declared `UNMEASURED` at G1; the first Phase 4 clean-machine run becomes the measurement, target judged absolutely, Phase 3 owner and date attached |
| Bootstrap | Intervention count per install across the last 5 new hires, from onboarding-channel tickets | One command, zero senior help | M5 bootstrap failure rate, intervention log | Declared `UNMEASURED` at G1; Phase 3 adds the counter, Phase 4 session supplies the first figure |
| Run | Image digest diff between a developer machine and the CI job; version-skew tickets | Same image digest as CI, seeded data | Digest diff reported at G3 | Declared `UNMEASURED` at G1; parity is then judged by the CI job that compares digests, added in Phase 3 |
| Test | Last 100 CI runs: duration percentiles and re-run-to-green count | Under 5 minutes local, M4 inside its G3 interim target | M2, M3, M4 | Declared `UNMEASURED` at G1; run history backfill is a Phase 1 Analytics Reporter action with a date |
| Deploy | Deploy timestamps from the pipeline plus approval-ticket count and time-in-queue | One command, main to staging | M1 deploy step timing, ticket count | Declared `UNMEASURED` at G1; Phase 3 ticket count is the first instrument, Phase 4 confirms it |
| Observe | Access-queue ticket count tagged observability, plus time from deploy to first dashboard view | Query and log link, no ticket | G4 visibility check on the subject's own change | Declared `UNMEASURED` at G1; the Phase 4 visibility check is the first measurement and cannot be waived |

A step whose friction has no instrument today is never silently targeted. It enters the baseline as `UNMEASURED`, gets an owner and a date in Phase 3, and its target is judged on the first clean-machine observation rather than on a delta.

## Phase 3: Build the Path

```text
Week 3-4: Make the path cheap to follow
├── Developer Tooling Engineer → identical task names local and in CI; the diff of
│   task lists is the acceptance test
├── DevOps Automator → cheapest check first; M2 time to first failure tracked per
│   commit
├── SRE (Site Reliability Engineer) → self-serve deploy with rollback; observe needs
│   no ticket; bootstrap and deploy failures instrumented for M5
├── Workflow Optimizer → flake quarantine with an owner and fix-by date; M6
│   before/after step count for every removed step
├── Technical Writer → quickstart executed in CI (M8); troubleshooting index built
│   from real stalls
├── Developer Advocate → samples regenerated per release (M9); stale ones deleted
├── Codebase Onboarding Engineer → first-week reading path, ten files in order
├── Platform Engineer → delete the old path: scripts, docs, CI jobs
└── Quality Gate G3: every documented command exits 0 in CI (M8 = 100%); every
    deprecated-path entry has its removal commit; every tool decision carries a
    written evaluation against M7 criteria with the exit path named; every step
    touched in Phase 3 has a before/after M6 step count; M9 stale samples = 0.
    Clauses, citable by number:
    3.1 M8 = 100%: every documented command exits 0 in CI.
    3.2 Every deprecated-path entry has its removal commit merged.
    3.3 M7 = 100%: every tool decision carries a written evaluation against the M7
        criteria with the exit path named.
    3.4 M6: every step touched in Phase 3 has a before/after step count, and the
        total path is at most 6 steps.
    3.5 M9 = 0: no sample pins an SDK version other than the released one.
    3.6 M2 interim: over the gate window (first 20 post-rewrite default-branch
        runs), time to first failure p50 ≤ 12 minutes and p90 ≤ 18 minutes.
    3.7 M3 interim: over the same gate window, pipeline duration p50 ≤ 25 minutes
        and p90 ≤ 35 minutes.
    3.8 M4 interim: flake rate ≤ 4% per workflow over the gate window, and every
        flake in that window has an owner and a fix-by date.
    3.9 M5: at least 20 instrumented clean-machine bootstrap attempts since the
        rewrite, with a failure rate ≤ 5% of attempts and zero failures caused by
        a command absent from the documented path.
    Each clause fails the gate by name. A clause with no post-rewrite observation
    yet is reported as UNMEASURED, and UNMEASURED fails that clause.
```

## Phase 4: Onboarding Proof

The non-negotiable gate: **time to first success is measured by timing a real person, on a clean machine, using only the documented path, with the session recorded under that person's written consent. A README nobody executed does not count, and a path that requires a senior engineer's help has failed.** Observers do not intervene; an intervention voids that run and is logged with its step and timestamp.

```text
Week 5: Run it on people who have never seen it
├── DX Engineer → recruit subjects outside the platform team, brief once, leave
├── Codebase Onboarding Engineer → log every stall with its step and duration
├── Analytics Reporter → per-subject timing per step; median and per-subject total
│   for M1
├── Evidence Collector → consent form on file before recording, then recorded
│   session, terminal log, screenshots, redacted before storage
├── Workflow Optimizer → turn every stall into a ranked fix with its M6 step delta
├── Reality Checker → verdict on whether the run was honest (default: NEEDS WORK)
└── Quality Gate G4: all seven clauses hold.
    4.1 Three consecutive subjects reach first success on clean machines.
    4.2 Zero interventions across all three runs.
    4.3 Median time to first success at or under 4 hours (M1).
    4.4 All three subjects at or under 8 hours (M1). Three subjects do not support
        a p90 — the p90 of three numbers is their maximum — so the tail is judged
        subject by subject instead.
    4.5 Every stall is logged with its step and duration.
    4.6 Written consent is on file for every recorded session, the retention window
        and viewer list are recorded with the evidence pack, and no secret, token
        or customer record is visible in it.
    4.7 M10 at or under 2 hours of senior time per onboarding run, from the
        intervention log plus onboarding-channel tickets.
    One intervention, one subject over 8 hours, one unlogged stall, one missing
    consent, or one leaked credential fails it and the path returns to Phase 3. A
    run without consent is not evidence and does not count toward the three.
```

## Phase 5: Scorecard & Handover

```text
Week 6: Make the result visible and owned
├── Analytics Reporter → scorecard beside the baseline, same stored queries,
│   updated automatically
├── SRE (Site Reliability Engineer) → alert on bootstrap and deploy failure rate
│   regression, alert routed to the named owner
├── Platform Engineer → named owner, on-call rotation, deprecation calendar
├── Workflow Optimizer → Post-runbook re-run booked with the Platform Engineer
├── Evidence Collector → evidence pack: baseline, sessions, scorecard, gate records,
│   each item inside the retention window and viewable only by the named viewers
├── Reality Checker → final verdict (default: NEEDS WORK)
└── Quality Gate G5: every clause below holds.
    5.1 The scorecard is published where engineers look and linked from the README.
    5.2 The named platform owner — the person named as an input before Week 1 —
        accepts handover in writing.
    5.3 Every Post-runbook row carries an owner and a measurement date.
    5.4 The evidence pack records its deletion date and its viewer list.
```

## Post-runbook

Metrics whose measurement window is longer than the 6-week run never appear as closed results above. They ship as owned commitments with a date.

| Metric | Why 6 weeks cannot close it | Owner | Measurement date |
| --- | --- | --- | --- |
| DORA lead time for changes, 30-day rolling median ≤ 1 day | A 30-day rolling window plus a trend against baseline does not exist until after handover | Analytics Reporter | Handover + 30 days |
| DORA change failure rate, 30-day rolling ≤ 15% | Same window; failure rate needs deploys and incident records after the path changes | Analytics Reporter | Handover + 30 days |
| Deploy frequency trend, 90 days | The trend must postdate the new deploy path, so it needs a full quarter of deploys | DevOps Automator | Handover + 90 days |
| Steady-state M2, M3, M4 over the trailing 100 default-branch runs | The gate window is 20 post-rewrite runs; a 100-run window does not exist until roughly 90 days after the rewrite, and early windows are still mixed | Analytics Reporter | Handover + 90 days |
| Onboarding cost per hire (senior hours × rate + ramp weeks), per quarter ≤ 1 week of senior time | Cost averages over hiring cohorts, i.e. quarters, not one 6-week run | Platform Engineer | Handover + 180 days |
| Golden-path regression re-proof, quarterly | A path can rot without any single failing gate inside the run | Workflow Optimizer | Handover + 90 days, then quarterly |
| Legacy-path attempts after removal, 90 days = 0 | Usage of a deleted path only shows up in the analytics trail over time | Analytics Reporter | Handover + 90 days |

## Key Decisions

| Decision Point | When | Who Decides |
| --- | --- | --- |
| Build vs adopt: task runner, dev container, portal | Phase 2 start | Tool Evaluator + Platform Engineer |
| Minimum supported platform matrix | Phase 2 | Platform Engineer + SRE (Site Reliability Engineer) |
| Mandated vs optional on the golden path | Phase 2 exit | DX Engineer + Product Manager |
| Local topology: full parity vs light subset | Phase 2-3 | DevOps Automator + SRE (Site Reliability Engineer) |
| What gets deprecated, and when | Phase 3 | Platform Engineer + Product Manager |
| Which metrics are published, and where | Phase 5 | Analytics Reporter + SRE (Site Reliability Engineer) |

## Success Criteria

| Metric | Exact definition | Baseline | Target | Owner | Enforced at |
| --- | --- | --- | --- | --- | --- |
| M1 Time to first success | Clone to deployed-and-visible change, clean machine, documented path, zero interventions | Measured value or a raw source admitted at G1 | Median ≤ 4 hours and every subject ≤ 8 hours | DX Engineer | G4 clause 4.3, 4.4 |
| M2 CI time to first failure | Run start to first failing step reporting, over the gate window | 40 minutes (claimed, re-measured at G1 on the pre-rewrite pipeline) | Interim: p50 ≤ 12 min and p90 ≤ 18 min over the first 20 post-rewrite runs. Steady state: p50 and p90 ≤ 10 min over 100 runs | DevOps Automator | G3 clause 3.6 (interim), Post-runbook (steady state) |
| M3 CI pipeline duration | Run start to terminal status, full default-branch workflow, over the gate window | Measured or `UNMEASURED` | Interim: p50 ≤ 25 min and p90 ≤ 35 min over the same 20 runs. Steady state: p50 ≤ 20 min, p90 ≤ 30 min over 100 runs | Developer Tooling Engineer | G3 clause 3.7 (interim), Post-runbook (steady state) |
| M4 Flake rate | Fails then re-run to green with no change, ÷ runs, over the gate window | Measured or `UNMEASURED` | Interim: ≤ 4% per workflow over the first 20 post-rewrite runs, every flake owned with a fix-by date. Steady state: ≤ 2% per workflow over 100 runs | Workflow Optimizer | G3 clause 3.8 (interim), Post-runbook (steady state) |
| M5 Bootstrap failure rate | Clean-machine bootstrap attempts exiting non-zero or needing an off-path command | Measured or `UNMEASURED` | ≤ 5% of attempts, over at least 20 instrumented attempts | Platform Engineer | G3 clause 3.9 |
| M6 Step count | Commands plus manual UI actions, clone to first success | Measured or `UNMEASURED` | ≤ 6 steps, with before/after counts for every removed step | Workflow Optimizer | G2 clause 2.1, G3 clause 3.4 |
| M7 Tool decision pass | Weighted criteria ≥ 3, candidates scored ≥ 2, verdict plus exit path recorded | No decisions recorded | 100% of tool decisions pass | Tool Evaluator | G3 clause 3.3 |
| M8 Documented-command pass rate | Doc commands executed by CI that exit 0 | Not executed in CI | 100% | Technical Writer | G3 clause 3.1 |
| M9 Stale sample count | Samples whose pinned SDK version differs from the released version | Not counted | 0 | Developer Advocate | G3 clause 3.5 |
| M10 Senior hours per onboarding | Senior time touching a subject's environment, from the intervention log, per onboarding run | 24 hours (from the last 5 hires, or `UNMEASURED`) | ≤ 2 hours | DX Engineer | G4 clause 4.7 |

## Common Pitfalls

| Pitfall | Mitigation |
| --- | --- |
| Built for the platform team's convenience | Decisions validated against a timed test-subject session (G4) |
| Path works only on the author's machine | Docs execute in CI (M8); unusable steps are removed |
| Measuring the happy path while flake rots | M4 is a first-class gate metric, quarantined tests owned |
| Adoption assumed because tooling shipped | Adoption counted from usage; the old path is deleted at G3 |
| Tooling added without deprecating the old path | Each new tool names its predecessor and removal date (M7 exit path) |
| A threshold nobody defined | Every number used by a gate is defined above; undefined is a fail |
| A target that cannot be observed in 6 weeks | Window-bound metrics live in Post-runbook with an owner and a date; a gate reads only the 20-run window it can fill |
| A recorded session with no consent, no retention rule, no redaction | Consent is a blocking input and G4 clause 4.6; the evidence pack records its deletion date and viewer list at G5 |
| A scorecard nobody reads | It sits where engineers look, re-proof is booked at G5 |
