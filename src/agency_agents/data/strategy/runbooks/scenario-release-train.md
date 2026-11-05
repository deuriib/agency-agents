# Release Train

Mode: NEXUS-Micro | Duration: 1-2 days per release, recurring | Agents: 9

Roster note: 9 agents are named below, but the Mobile Release Engineer activates only when a mobile surface ships. Most cycles run with 8 active agents, and G3 item 6 applies only when a mobile build is part of the release.

## Scenario

Every release is treated as an event, and events are improvised. Someone remembers the version bump near the end. The notes are written from memory, in a hurry, after the tag. The rollback plan is "revert and hope" — a path nobody has walked since it was designed on a whiteboard. And when it goes wrong, the same two people get paged, because they are the only two who know how the pipeline was wired.

This runbook turns releasing into a scheduled, boring, repeatable run: a go/no-go decision that is allowed to fail, notes generated from merged work rather than recollection, and a rollback that was exercised in staging before anyone needed it in production.

The doctrine is one sentence: **a release is not a version number, it is a verified artifact plus a way back.** A tag pushed over an untested build, with no rehearsed reversal, is not a release — it is a bet with the customer's data as collateral.

Scope is one release, run by the same checklist every cycle. The train departs on a schedule whether or not anyone feels ready, and a NO-GO is a normal, non-punished outcome that costs a slot, not credibility.

## Applicability

| Use this runbook when | Use a different runbook when |
| --- | --- |
| A release is routine and recurring: the mechanism exists and must now run on schedule | The release mechanism does not exist yet (no tag flow, no notes, no provenance) — use `repository-hardening-program` |
| Tests, artifact production and a pipeline already work; the missing piece is the decision and the discipline | Something is already broken in production — use `incident-response` |
| You need a defensible go/no-go record and a rehearsed rollback per cycle | An embargoed emergency patch must ship outside the schedule — use `security-vulnerability-response` |
| Releases slip because preparation is improvised each time | The build pipeline itself is slow, flaky or untrusted — use `developer-experience-platform` |
| The release cadence is internal or commercial | The release is a public OSS version with contributor-facing cadence — use `oss-maintainer-operations` |

## Required Inputs

Only what the roster cannot produce. The release notes, the changelog entry and the go/no-go record are **outputs** of this run, never inputs.

| Input | Why it blocks | Owner |
| --- | --- | --- |
| Release credentials a human controls: registry publish token, store signing identity, production deploy credential | The roster can use a credential, it cannot issue one; an undocumented credential stops the train at the tag | Named credential holder |
| A versioning policy already agreed: numbering scheme, pre-1.0 rules, deprecation window, what counts as breaking | A release does not get to invent its own numbering; retrofitting a compatible version after publish is impossible | Engineering lead + maintainer |
| The current known-issues list with severity and workaround per item | Notes and the go/no-go both need an attested list; the roster can format an entry, not certify it | Product owner |
| A named on-call owner for the release window, reachable, with authority to call rollback | A release with no one accountable for the window is an unsupervised change to production | On-call owner |
| The rollback mechanism as it exists today: previous artifact retention, feature flags, migration reversibility, restore procedure | The run exercises the way back; it cannot invent one at 2am | Platform owner |

## Agent Roster

### Release Command (Always Active)

| Agent | Role | Proven by |
| --- | --- | --- |
| Agents Orchestrator | Owns the schedule and the sequence; convenes the go/no-go, records GO/NO-GO, stops the train when a gate fails | G3 |
| Git Workflow Master | Branch cut, version derivation from the merged diff, tag naming, changelog entry, release-branch freeze | G1 |
| DevOps Automator | Single immutable artifact build, deploy by hash, staged rollout, rollback execution and its rehearsal | G2 |

### Build & Verify (Day 1)

| Agent | Role | Proven by |
| --- | --- | --- |
| Test Automation Engineer | Full suite and smoke pack on the exact commit; separates a real failure from a quarantined flake | G1 |
| Evidence Collector | Evidence pack per release: commit, hash, CI run, test summary, lockfile, deployment readings | M2 |
| Mobile Release Engineer | Store build signing, staged rollout percentage, halt path — only when a mobile surface ships | G3 item 6 |

### Ship & Communicate (Day 2)

| Agent | Role | Proven by |
| --- | --- | --- |
| Technical Writer | Notes generated from the merged PR range, breaking changes with an upgrade command, changelog entry | M4 |
| Support Responder | Support brief before full rollout, known-issues reconciliation, escalation path posted in the release channel | G4 |

### Verdict

| Agent | Role | Proven by |
| --- | --- | --- |
| Risk Reviewer | Holds the NO-GO; reads the evidence pack, records the verdict and the dissent, refuses a trade of one failed item against a stack of passing ones | M1 |

## Thresholds

Every number below is decided in advance and read before any phase depends on it: Day 1's G1 is a test-failure threshold, and Day 2's G4 is an error-rate threshold. A threshold negotiated while a dashboard is red is not a threshold.

| Threshold | Value | Why that number |
| --- | --- | --- |
| Test failure rate to ship | 0 failing; at most 2 quarantined flakes, each with a named owner and a date; a third quarantined flake, or any quarantined flake with no owner or date, is a failed gate | Quarantined tests run outside the suite, so counting them is the only thing that keeps a shrinking suite honest |
| Production error rate to ship | 5xx rate at or below the trailing 7-day baseline + 0.5 pp over the 24 h before G3 | A release into an already-degraded service cannot be distinguished from a bad release |
| Observation window | 60 min total: 10% for 10 min, 50% for 20 min, 100% for 30 min | Short enough to fit a release day, long enough to see a slow failure |
| Threshold crossing to rollback decision | 15 min, one named caller, no group vote | Rollbacks decay by committee; the decision is executive, the diagnosis is not |
| Staging rollback rehearsal elapsed time | Decision to previous artifact serving at or under 20 min, timed and recorded in this cycle's release record | A rehearsal is a measurement, not a promise: an untimed rehearsal proves the path exists, not that it fits the window |
| Production restore objective | Decision to previous artifact serving at or under 20 min in production, proven by at least one real production restore per trailing quarter; owned by DevOps Automator | A staging rehearsal cannot prove a production restore: production state, credentials, traffic and data volume are exactly what staging does not reproduce |
| Hotfix criteria | Caused by this release, no workaround, and either at least 5% of requests affected or any authentication or payment path | Below that line the defect joins the next scheduled train |

## Day 1: Prepare & Verify

Preparation ends with a candidate, not an intention. Everything downstream references a commit hash, and no step is allowed to rebuild the thing it just tested.

```text
├── Git Workflow Master → cut the release branch from the commit that will ship; derive
│   the version from the merged PR range under the agreed policy, never typed by hand
├── Test Automation Engineer → full suite plus smoke pack on that exact commit SHA in
│   CI; the green run is recorded next to the SHA, not next to a branch name
├── Test Automation Engineer → any skipped or quarantined test is named with an owner
│   and a date; a silent skip is a failure, not a pass
├── DevOps Automator → build the artifact once from that SHA, push it immutably to the
│   registry, record the hash; from here the artifact is addressed by hash
├── Evidence Collector → evidence pack: SHA, artifact hash, CI run URL, test summary,
│   dependency lockfile, artifact size, migration-set digest, and the store build
│   signature when a mobile surface ships — one directory per release, linked from the record
├── Mobile Release Engineer (mobile surface only) → sign the store build with the release
│   credential, record the resulting signature in the evidence pack, set the staged
│   rollout percentage, and exercise the halt path in staging
└── Quality Gate (G1): the candidate is built once from a named commit SHA, the full
    suite is green on that same SHA, the artifact hash is recorded against it, and the
    `Test failure rate to ship` threshold holds — more than 2 quarantined flakes, or any
    quarantined flake without a named owner and a date, fails G1 even when the suite is
    green, because quarantined tests run outside the suite and would otherwise shrink it
    unnoticed.
```

Then the way back is proven, not described. A rollback procedure that has only been read is a hypothesis.

```text
├── DevOps Automator → rollback rehearsal in staging inside this cycle: deploy the
│   previous released artifact over the candidate, from the registry, by hash; record
│   elapsed time from decision to previous version serving, and record the digest of the
│   migration set the rehearsal ran against
├── DevOps Automator → feature-flag path exercised separately: disable the new
│   behaviour without redeploying, confirm the old behaviour returns
├── DevOps Automator → migration reversibility on a staging copy refreshed from
│   production: run the down path, then the up path, twice, and keep the log
├── Technical Writer → notes regenerated from the merged PR range after the branch
│   freeze; every breaking line carries an upgrade command; a line no merged PR explains
│   is traced to that PR or deleted
├── Support Responder → known-issues list reconciled against the notes: title, impact,
│   workaround, and whether the release makes it better or worse
├── Evidence Collector → attach rollback timing, the rehearsal's migration-set digest,
│   the migration reversal log and the notes diff to the release record; the pack is what
│   the go/no-go reads, not a screen share
├── Risk Reviewer → assemble the go/no-go checklist with each item pre-marked and
│   linked to its evidence; reserve the verdict for the next morning
└── Quality Gate (G2): the way back is exercised, not asserted — a timed staging
    rollback and a completed migration reversal sit in this release's record, and every
    notes line traces to a merged PR.
```

## Day 2: Ship, Observe & Close

### The Go/No-Go Checklist (G3)

Six items, each falsifiable by a single observation. A missing rollback exercise is a NO-GO even when every other item is green; so is a store build whose signature does not match the tested build, and so is a halt path that was never exercised.

| # | Item | Fails when | Evidence |
| --- | --- | --- | --- |
| 1 | Tests green on the exact commit | Any failing test, the green run is on a different SHA than the tag, or the quarantined count breaks the `Test failure rate to ship` threshold | CI run URL next to the SHA; quarantined list with owners and dates |
| 2 | Artifact hash matches the tested build | The deployed hash differs from the hash recorded at G1, or the artifact was rebuilt after testing | Registry digest vs deploy log |
| 3 | Rollback exercised in staging within this cycle | The last rehearsal predates this release's artifact, or the migration-set digest recorded with that rehearsal differs from this release's migration-set digest | Timed rehearsal log and migration-set digest, G2 |
| 4 | Notes generated from merged PRs | A notes line with no merged PR behind it, or a breaking change with no upgrade command | Notes diff vs PR range |
| 5 | Migration reversible | Down path fails, or the reversal has never run against production-shaped data | Migration reversal log, G2 |
| 6 | Store build signature matches the tested build, and the halt path was exercised in staging this cycle (mobile surface only) | The store build is signed with a signature or key that does not match the tested build, or the halt path was never pulled in staging during this cycle | Signature record in the evidence pack; staging halt-path log |

```text
├── Agents Orchestrator (or this cycle's recorded convener) → convene the go/no-go over
│   the release record, 30 minutes, one checklist item at a time, each marked pass or
│   fail in writing
├── Risk Reviewer → read the evidence pack, not the summary; record verdict plus dissent
├── Git Workflow Master → confirm the version follows the policy for this diff, and the
│   deprecation window is stated on anything being deprecated
├── Support Responder → confirm the on-call owner for the window is reachable and the
│   escalation path is posted before the artifact moves
├── Agents Orchestrator → NO-GO path: the train stops, the failed item becomes one work
│   item with an owner and a date, and the slot passes to the next scheduled release
└── Quality Gate (G3): GO is recorded with six passing items and zero blanks (item 6 is
    not applicable only when no mobile surface ships); a release with no rollback
    exercise, or a mobile release whose signature does not match the tested build or
    whose halt path was never exercised, is NO-GO regardless of the other items.
```

### Ship, Observe, Close

```text
├── DevOps Automator → deploy the registry artifact by hash, not by branch; the deploy
│   log shows the same hash the go/no-go approved
├── DevOps Automator → staged rollout per Thresholds; each step holds its slice of the
│   observation window before the next step starts
├── Evidence Collector → capture readings at T+5, T+15 and T+60 minutes: error rate,
│   p95 latency, saturation, top exception, request volume against the prior window
├── Support Responder → publish the support brief before rollout reaches 100%: what
│   changed, what to tell a user, where to escalate
├── Technical Writer → notes and changelog published against the tag; every breaking
│   entry carries the upgrade command a user can actually run
├── Agents Orchestrator → on a threshold crossing: rollback decided inside 15 minutes by
│   the named caller, executed by DevOps Automator, and the release closes as ROLLED BACK
│   with the same evidence discipline — a rolled-back release is a completed run, not a
│   failed one
├── Risk Reviewer → record the outcome and name the owners and measurement dates for the
│   post-release metrics before the release note is closed
└── Quality Gate (G4): the release record for the tag holds an observation-window reading
    inside the thresholds — or a completed rollback inside the production restore
    objective — plus the published notes, the published support brief, and named owners
    for post-release metrics.
```

## Key Decisions

| Decision Point | When | Who Decides | Default if undecided |
| --- | --- | --- | --- |
| Who calls NO-GO | G3, before the artifact leaves the registry | Risk Reviewer; Release Command concurs, never overrules | NO-GO — silence is not approval |
| Whether to ship on a Friday | At G3 and at the calendar | On-call owner for the window, with Risk Reviewer | Do not ship: the window owner's availability is the deciding fact, not the calendar |
| When a hotfix becomes a rollback | Inside the observation window, on a threshold crossing | Named rollback caller (DevOps Automator executes) | Roll back first, diagnose after — a forward fix during a live incident doubles the blast radius |
| Whether a migration ships separately from the code | Day 1, when the migration is reversible only in one direction | Platform owner + Risk Reviewer | Ship migration first, code after; never the reverse |
| Whether to ship with a known issue open | At G3, item by item | Product owner with Risk Reviewer | Ship only with a documented workaround and a support brief that names it |
| Whether to skip a release slot | Scheduling, before Day 1 opens | Agents Orchestrator with the on-call owner | Keep the slot and take a NO-GO; an unreleased train is cheaper than a skipped checklist |

## Success Criteria

| Metric | Target |
| --- | --- |
| M1 Go/no-go record attached to the tag | 100% of releases; 0 deploys without a recorded GO |
| M2 Artifact identity: deployed hash equals tested hash | 100% of releases; 0 rebuilds after testing |
| M3 Rollback proof: timed staging rehearsal in the same cycle, plus a real production restore in the trailing quarter | 100% of releases with a recorded staging rehearsal at or under 20 min; at least one real production restore at or under 20 min per trailing quarter, owned by DevOps Automator |
| M4 Notes traceability | 100% of merged PRs in range mapped to a notes line; 0 unexplained lines |
| M5 Observation window completed inside thresholds | ≥ 90% of releases; 100% of crossings decided inside 15 minutes |
| M6 Release window elapsed, preparation start to close | ≤ 2 business days; median ≤ 1.5 |

## Common Pitfalls

| Pitfall | Mitigation |
| --- | --- |
| Release notes written after the fact, from memory | Notes are generated from the merged PR range at G2 and regenerated after branch freeze; a line no PR explains is traced or deleted, and G3 fails on it |
| A rollback path that has never been executed | The rehearsal is a gate item with a timed log in the release record; missing rehearsal is NO-GO even when every other item is green |
| Shipping a different artifact than the one tested | Build once, address the artifact by hash, deploy by hash; G1 records the hash and G3 compares the deployed digest against it |
| One person holding all release knowledge | Rotate the go/no-go convener among the three always-active agents each cycle and record who convened in the release record; name a second for every role, and let the checklist — not a person — carry the procedure |
| Migrations coupled to deploys, reversed only in theory | Ship the migration separately, run down-then-up twice against production-shaped staging data, and treat an irreversible migration as a design defect |
| A "quick hotfix" that skips every gate | Hotfixes compress the clock, never the gates: G1 on the exact commit, G3 with one approver, G4 with a 30-minute window; a reused rollback rehearsal is valid only if the artifact hash and the migration-set digest in the evidence pack are unchanged, and G3 item 3 compares both before accepting it |

## Post-runbook

Measured after the release window closes, reviewed at the next train's Day 1 so the numbers change the next run.

| Metric | Owner | Measured on |
| --- | --- | --- |
| Change failure rate: releases needing rollback or a hotfix | Risk Reviewer | 14 days after the tag, trailing 5 releases |
| Time to restore: crossing detected to previous version serving | DevOps Automator | Every change-caused incident in a 30-day window |
| Regression escapes: defects traced to this release after close | Test Automation Engineer | The next release's defect intake |
| Notes accuracy: support tickets caused by an undocumented change | Support Responder | 14 days after the tag |
| Hotfixes per release, and how many reused a rehearsal | Agents Orchestrator | Release close-out, reviewed quarterly |
| Last successful rollback rehearsal age | DevOps Automator | Day 1 of every subsequent release |
| Production restore proof: elapsed time of the last real production restore, decision to previous artifact serving | DevOps Automator | Every release, measured against the trailing quarter |
