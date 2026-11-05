# Runbook: Bug Triage & Defect Elimination

> **Mode**: NEXUS-Sprint | **Duration**: 2 weeks | **Agents**: 15

## Scenario

The tracker holds more bugs than anyone can count — the count itself is unknown, because nobody agrees which entries are defects. Standup re-litigates priority because no written severity scale exists, so the list is sorted by who complained loudest. The same defect returns two releases after its "fix" patched one call site. Customers report breakage publicly before engineering hears of it. Most tickets carry no steps to reproduce.

This runbook triages the backlog against a printed severity scale and a printed disposition table, attributes each defect to one layer, and locks every fix behind a test plus a signal. Because the backlog is uncountable, Week 1 ends with a **numbered scope list capped by committed capacity**, and Week 2 closes only bugs on that list.

**Non-negotiable close rule:** a bug closes only as (a) *fixed*, with an automated test observed failing for the recorded cause before the fix and passing after it, or (b) a signed `won't-fix` row from the disposition table. There is no third close path. Case (a) and case (b) are the only two values the close rule accepts, and Success Criteria measures them at 100%, not at a threshold with a tolerated remainder.

## Applicability

| Use this runbook when | Use a different runbook when |
| --- | --- |
| Bug volume, priority disputes, and repeat defects dominate | Production is broken right now — `incident-response` |
| Backlog drains on a schedule, not today | A vulnerability was reported — `security-vulnerability-response` |
| Repeat defects need cause elimination, not patching | Policy and gates are missing repo-wide — `repository-hardening-program` |
| Public reports beat internal visibility | Code must be restructured before fixes hold — `codebase-modernization-program` |
| Closed bugs return, and closure is disputed in review | The complaint is visual inconsistency, not defects — `design-system-and-ui-quality` |

A P0 that is still bleeding on the day it is triaged is handed to `incident-response`; this runbook resumes at cause elimination once the outage is contained.

## Required Inputs

| Input | Why it blocks | Owner |
| --- | --- | --- |
| Read access to the error tracker and logs, retained at least as far back as the oldest bug on the list | Without a trace, request ID, or build number, nothing is reproduced or attributed | Reliability Reviewer |
| Read access to the support desk and the public issue channels | Reports reach engineering only after a customer escalates publicly | Support Responder |
| CI write access to add tests and required checks | The close rule cannot be enforced if a lock cannot land | Test Automation Engineer |
| One tracker designated as the system of record, writable by the roster | Dispositions scatter across tools and duplicate detection stops working | Agents Orchestrator |
| Committed defect capacity for the sprint, in engineer-days | The scope cap has nothing to divide with, so the list becomes every bug | Agents Orchestrator |
| A named authority who may sign `won't-fix` and accept a `duplicate` merge | An unsigned exception is not defensible in review | Sprint Prioritizer |

The severity scale is **not** an input. Week 1 produces it, from the impact and reach observed on the bugs actually in the queue.

## Severity Scale (Week 1 output)

Severity is derived from two observed inputs: **impact** (what the user cannot do) and **reach** (share of active accounts hitting it). The scale below is printed once, applied to every bug, and cited by every gate.

| Level | Definition | Example | First response | Inside the scope cap |
| --- | --- | --- | --- | --- |
| P0 | Customer-facing outage or data loss/corruption with no workaround | Checkout refuses all payments; records deleted on save | 1 hour | Yes, uncapped |
| P1 | Major function broken or degraded; workaround is costly | SSO login fails for one tenant; exports fail above 10k rows | 1 business day | Yes, uncapped |
| P2 | Contained defect; workaround is cheap and documented | Wrong default sort; missing validation on one field | 3 business days | Yes, to the capacity line |
| P3 | Cosmetic or copy defect with no functional impact | Misaligned label; typo in a tooltip | 10 business days | Not this sprint |

Below P3 is not a severity. A bug with no severity after triage is a triage failure, and the Week 1 gate names it. A **business day** is a working day, and a response clock starts when the bug or the public report lands in the queue.

## Dispositions (Week 1 output)

Every open bug leaves Week 1 with exactly one disposition. Five exist; nothing else closes or parks a bug, and the gates cite this table by row.

| Disposition | What it requires | Signed by | Next step |
| --- | --- | --- | --- |
| `fix-now` | Severity P0–P2, on the numbered scope list, plus a recorded failing reproduction | Reliability Reviewer for P0/P1; Test Results Analyzer for P2 | Locked and fixed in Week 2 under the close rule |
| `fix-later` | A severity, a reason it is outside the cap, and a dated re-review | Sprint Prioritizer | Re-ranked on that date; the bug stays open |
| `needs-info` | One specific question addressed to a named person, the data needed, and a silence deadline | Support Responder | Signed `won't-fix` if the deadline passes unanswered |
| `won't-fix` | A written rationale, a named business owner, and the product line it applies to | Sprint Prioritizer + that owner | Legal close; recorded in the won't-fix log |
| `duplicate` | A canonical bug ID and the merged reporter list | Test Results Analyzer | Closed against the canonical bug, which carries the work |

## Agent Roster

Activation marks when an agent joins the run. The Root Cause agents join in Week 1, sign a cause there, and stay through Week 2 to land the fix that cause names. Every row below is cited by at least one Quality Gate line or Success Criteria metric; a row cited by neither is removed from the roster.

### Triage Command (Always Active)

| Agent | Role |
| --- | --- |
| Agents Orchestrator | Freezes intake to one queue and one template; enforces both gates |
| Test Results Analyzer | Assigns one disposition from the disposition table per bug |
| Support Responder | Merges support desk and public reports into one queue; owns needs-info asks |
| Feedback Synthesizer | Clusters by symptom, not ticket text; proposes duplicate merges |

### Root Cause (Week 1)

| Agent | Role |
| --- | --- |
| Reliability Reviewer | Reproduces P0/P1; confirms severity; records the minimal failing case |
| Minimal Change Engineer | States the fix as one sentence — layer, cause, change — and looks for the narrowest correct one |
| Backend Architect | Attributes and signs server-side causes and fix scope |
| Frontend Developer | Attributes and signs client causes: state, render path, event handling |
| Database Optimizer | Attributes and signs data-layer causes: queries, constraints, migrations |

### Regression Lock (Week 2)

| Agent | Role |
| --- | --- |
| Test Automation Engineer | Lands the failing test first, as a required check, then turns it green |
| Observability Reviewer | Instruments the path the defect travelled so a recurrence produces a signal, not a customer report |
| Evidence Collector | Attaches the red run, the green run, and the dead reproduction to each closure |
| Reality Checker | Samples closings against the close rule; a single miss reopens the bug |

### Handoff (Week 2)

| Agent | Role |
| --- | --- |
| Technical Writer | Changelog line and documentation correction per fix |
| Sprint Prioritizer | Scope cap arithmetic; won't-fix and fix-later signatures |

## Week 1: Triage, Scope Cap & Root Cause

```text
├── Agents Orchestrator → freeze intake: one queue, one template, one severity scale
├── Support Responder → fold support desk and public channels into the queue; send each
│   needs-info ask to a named person with a silence deadline
├── Feedback Synthesizer → cluster by symptom; flag candidate duplicates against a canonical ID
├── Test Results Analyzer → state impact and reach per bug; propose the severity
├── Reliability Reviewer → reproduce each P0/P1; confirm or correct its severity
├── Backend Architect, Frontend Developer, Database Optimizer → attribute the cause to one
│   layer and sign the attribution
├── Minimal Change Engineer → one sentence per reproduced bug: layer, cause, change
├── Sprint Prioritizer → emit the numbered scope list and print the arithmetic behind N
├── Test Results Analyzer → assign one disposition from the disposition table against that list
└── Quality Gate: every open bug carries a severity from the severity scale and one
    disposition from the disposition table; every P0/P1 carries a failing reproduction and
    a layer-signed cause, or a needs-info whose ask was sent; the scope list is numbered
    with N printed beside its capacity arithmetic, and lists every open P0/P1
```

**Scope cap, defined.** All open P0 and P1 enter the list without a cap. P2 bugs enter in severity-then-age order until the sprint's committed defect capacity, in engineer-days, is consumed at the median fix estimate the layer owners print for those P2 bugs (that median is stated with the list). P3 stays out of this sprint. **N is the count of bugs on that list, and the arithmetic that produced it is printed with the list.** A bug not on the list cannot close in Week 2: it holds `fix-later` with a dated re-review.

## Week 2: Fix, Regression Lock & Handoff

```text
├── Test Automation Engineer → land the lock first: red on the recorded cause, in CI, as a
│   required check; only then let the fix in
├── Minimal Change Engineer → land the fix the cause names; no unrelated cleanup in the diff
├── Backend Architect, Frontend Developer, Database Optimizer → sign the changed layer; a
│   fix crossing layers needs a second signer
├── Observability Reviewer → instrument the defect's path with a signal that fires on a
│   synthetic re-trigger; record the trigger output
├── Evidence Collector → red run, green run, and dead reproduction attached to each closure
├── Technical Writer → changelog line and the doc correction for each fix
├── Sprint Prioritizer → won't-fix, duplicate, and fix-later rows signed with re-review dates
├── Reality Checker → sample closings against the close rule; any miss reopens the bug
└── Quality Gate: every closure is one of the two close-rule cases — a Test Automation Engineer
    lock seen red for the recorded cause and green after the fix, or a won't-fix row with a named
    owner and written rationale; every lock is red when the fix is reverted; every fix diff the
    Minimal Change Engineer lands holds only the change its recorded cause names; every P0/P1 fix
    has an observability signal demonstrated firing once; every closure carries a changelog or
    documentation line
```

**Non-negotiable:** a green test that was not observed red for the recorded cause does not satisfy the close rule, and neither does a won't-fix without a named owner and a written rationale. Reality Checker's sample of closures is the enforcement, and its finding fails the gate rather than starting a discussion.

## Key Decisions

| Decision Point | When | Who Decides |
| --- | --- | --- |
| Severity scale and the impact/reach mapping | Week 1, before any sorting | Agents Orchestrator + Sprint Prioritizer |
| Disposition per bug, from the printed table | Week 1, per bug | Test Results Analyzer |
| Scope cap: N and the capacity arithmetic | Week 1, day 4 | Sprint Prioritizer + Agents Orchestrator |
| What counts as reproducible for a given bug | Week 1, per P0/P1 | Reliability Reviewer |
| Which layer owns the cause | Week 1, per fix-now bug | Backend Architect / Frontend Developer / Database Optimizer |
| Won't-fix rows for this sprint | Week 1 close and Week 2 close | Sprint Prioritizer + the named business owner |
| What the regression test asserts | Week 2, before the fix | Test Automation Engineer + Reality Checker |
| Close acceptance, and reopening a closure | Week 2, closing gate | Reality Checker |

## Success Criteria

| Metric | Target | Observed by |
| --- | --- | --- |
| Open bugs carrying a severity from the severity scale and one disposition from the disposition table | 100% at the Week 1 gate | Agents Orchestrator |
| Numbered scope list published with N and its capacity arithmetic | 1 list by Week 1 day 4; 100% of closures on that list, 0 closures outside it | Sprint Prioritizer |
| Closures matching the close rule exactly — a failing-then-passing test for the recorded cause, or a signed won't-fix row | 100%; a single closure outside the rule fails the gate | Reality Checker |
| P0/P1 bugs with a failing reproduction and a layer-signed cause, or a needs-info ask that was sent | 100% | Reliability Reviewer |
| Locks observed red before the fix and green after it | 100% of fixed bugs | Evidence Collector |
| P0/P1 fixes with an observability signal demonstrated firing on a synthetic re-trigger | 100% | Observability Reviewer |
| Closures carrying a changelog or documentation line | 100% of P0/P1/P2 fixes | Technical Writer |
| First response inside the severity scale's window | 100% of P0/P1 | Agents Orchestrator |
| Reports that first appeared in a public channel and were queued within 1 business day of appearing | ≥95% | Support Responder |
| Won't-fix and fix-later rows with a named owner or a re-review date and a written reason | 100% | Sprint Prioritizer |
| Duplicate closures naming a canonical bug ID | 100% | Test Results Analyzer |
| Bugs clustered by symptom, with a duplicate candidate ID wherever one exists | 100% at the Week 1 gate | Feedback Synthesizer |
| Fixed bugs whose changed layer is signed by that layer's owner | 100% | Backend Architect / Frontend Developer / Database Optimizer |

## Post-runbook

These windows outlive the 2-week run, so they are measured here and not in Success Criteria.

| Metric | Target | Owner | Measurement date |
| --- | --- | --- | --- |
| Bugs closed this sprint and reopened | ≤5% of the sprint's closures | Reality Checker | Day 44 from sprint start — 30 days after the final closure |
| Recurrences that reached a customer before the Week 2 signal fired | 0 of the recurrences found in the window | Observability Reviewer | Day 44 from sprint start |
| `fix-later` rows still parked with no re-review held | 0 of the rows dated inside the window | Sprint Prioritizer | Day 44 from sprint start |

## Common Pitfalls

| Pitfall | Mitigation |
| --- | --- |
| Triage becomes a meeting where nothing is decided | Every bug leaves with a row from the disposition table and a date |
| The backlog is "drained" by bulk-closing stale tickets | The close rule has two cases only; a rationale-free close reopens in Reality Checker's sample |
| A test written after the fix, green on its first run | The lock lands red for the recorded cause, as a required check |
| UI symptom patched while the data layer stays broken | The cause is attributed and signed by the layer owner before the fix is scoped |
| The fix ships and nothing notices if it comes back | The Observability Reviewer's signal is demonstrated firing once at the gate, and reviewed at day 44 |
| "Cannot reproduce" used as a close reason | `needs-info` with a specific ask, then a signed won't-fix; the bug stays open until one of the two lands |
| Scope creep that quietly re-promises the whole backlog | N is printed with its arithmetic, and a closure outside the list fails the gate |
| Public reports handled only by support | Support routes with reproduction data; engineering decides severity and disposition |
