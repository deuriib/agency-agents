# Runbook: Delivery Recovery

Mode: NEXUS-Sprint | Duration: 3-4 weeks | Agents: 15

## Scenario

A program is red. The date has slipped twice, the steering deck says green, the team says otherwise, and nobody can name the single constraint that matters. Status updates have become a ritual for covering variance instead of surfacing it: estimates are quietly re-baselined, the risk row leaves the deck, and the one number that would force a decision is never in the room.

The honest name for this failure mode is **status reporting optimized for the audience instead of for the decision**. The job of this runbook is to make the reported state and the actual state the same number, prove that they are the same number with artifacts, and install a cadence that keeps them the same after the runbook ends.

Scope is one in-flight program that is failing: diagnose the real constraint, renegotiate scope with named owners, restore a delivery cadence. It is not product discovery, not portfolio strategy, and not crisis response. Equally, it is not a motivational exercise: a recovery plan that assumes the cause without evidence is a second failure stacked on the first.

## Applicability

| Use this runbook when | Use a different runbook when |
| --- | --- |
| An in-flight program has slipped at least twice and the reported status does not match observable progress | The work has not started — use `feature-discovery-to-spec` to decide what is worth building and write the spec first |
| The constraint is unproven and every team names a different blocker | Delivery is healthy and you are adding one large feature — use `enterprise-feature` |
| Commitments already made externally must be renegotiated, with named owners signing the change | The change spans many programs, teams, and processes at once — use `digital-transformation-program` |
| The sponsor must choose between scope and date, on evidence, before the next external commitment | Two organizations, toolchains, or delivery models are being merged — use `post-merger-integration` |
| Trust in the numbers has collapsed and a cadence where reported equals actual must be installed | Something is broken in production right now — use `incident-response` |

## Required Inputs

Only what the roster cannot produce. Everything else this runbook needs, it makes.

| Input | Why it blocks | Owner |
| --- | --- | --- |
| Read access to tracker history and commit/deploy logs for the program's full life | Variance cannot be computed from a status field; it needs the raw event history, including the events that were edited | Engineering Manager |
| A sponsor with written authority to cut scope, move the committed date, or stop the program | Recovery without a cutter is a re-labelled plan; every gate below assumes someone can say no | Sponsor |
| The contractual or committed date, as it exists in the contract or commitment | The gap between that date and the one quoted in the plan is usually the first real finding | Program Manager + Legal |
| The status reports as actually sent, last 8 cycles, unedited | The only honest baseline for reported-vs-actual variance; reconstructed status is a second story | Program Manager |
| A written statement of everything already promised externally — customer, board, regulator, partner | Internal scope can be cut; external promises cannot be cut silently | Account Owner |

## Interview and People Data

Written interviews and the safety pulse are the only part of this runbook where people say true things because saying them is safe. Everything below is binding on every artifact the runbook produces, not guidance.

| Rule | What it means in practice |
| --- | --- |
| Interview statements are recorded without individual attribution | A statement is logged as an observation about the program, never by a person: no name, no verbatim quote, no role-and-team combination narrow enough to resolve to one individual |
| Artifacts carry a constraint and its artifacts, never a person's sentence | The variance ledger, the sponsor deck, and the external note may each carry a constraint and the artifacts that support it. None of them may carry a person's sentence, a paraphrase of it, or the fact that someone said it in private |
| The Organizational Psychologist reports aggregates only, at n ≥ 5 | Every published safety or burnout figure rests on at least 5 respondents. Below that the finding is reported as "insufficient sample", not as a number. Raw notes stay with the Organizational Psychologist, are never attached to the ledger, deck, or external note, and are destroyed at handover |
| A named individual never appears in a status line without written consent | Capacity is reported by workstream or role. A person is named only against consent captured in writing before the line is written |

These rules have teeth at the gate that reviews each artifact: G2 for the variance ledger, G3 for the plan and its cut list, G5 for the sponsor deck and the external note. An attributed line fails the gate that touches it.

## Thresholds

Every number this runbook uses is defined here. A number without a definition is an opinion with a decimal point.

| Threshold | Value | Why that value |
| --- | --- | --- |
| Schedule variance that triggers this runbook | Two or more slipped dates, or remaining-work variance above 10% against plan at any cycle | One slip is estimation noise; two is a pattern. 10% sits at the edge of normal measurement error, above it the trend is real |
| Variance that triggers a re-plan inside the window | Remaining-work variance above 5% against the re-baselined plan at any cycle | Above 5% the plan is wrong, not the work; re-planning is cheaper than explaining |
| "At risk" item | Any committed item with (a) no named owner, (b) an open dependency on a party outside the team, or (c) under 20% schedule buffer against its remaining estimate | These are the three states that precede a slip, and 20% buffer leaves no room for a normal bad week |
| Confidence required to re-commit a date | At least 80% of committed scope delivered by the committed date, from throughput measured over 4 weeks or 3 sprints, stated as a band. The window is historical by default: the 4 weeks or 3 sprints come from the tracker history that is a required input, because in Week 2 the run has only one week of itself to measure. In-run throughput is admissible only from Week 3 onward. The window actually used is named on the re-committed date, beside its arithmetic | Below 80% the date is a hope; under 4 weeks throughput is not stable enough to extrapolate. A Week 2 date extrapolated from one in-run week is a single sample wearing a band |
| Evidence required to name the constraint | At least 2 independent artifacts for the primary cause, and 1 artifact for each ranked alternative | Two sources kill a single-source narrative; ranking alternatives kills the politically convenient one |
| Measurement completeness | 100% of claims in scope marked, no sampling | A sampled variance is a guess with a table around it |
| Re-plan window | Weekly, fixed day and slot, 1 hour maximum, decisions only, status reading prohibited, verified from the meeting log at G4 | A longer or less frequent loop lets variance re-hide between sessions; a log with start, end, and no status entries is the only proof the loop stayed a decision loop |
| Forecast cycle | 2 weeks of committed items, hit rate measured at the end of each cycle. A 4-week run holds exactly one complete cycle (Week 3 through end of Week 4), so in-run accuracy is a single observation; the rate lives in P1 | Short enough that the commitment is real, long enough that hitting it means something; one cycle is the most this run can honestly produce |
| Decision latency tolerance | Median 3 business days from request to a named decision | Past 3 days the queue, not the work, is the constraint |
| Exit tolerance | Remaining-work variance of 5% or less for 2 consecutive cycles | One clean cycle can be luck; the second proves the cadence survived contact |

## Agent Roster

### Command (Always Active)

| Agent | Role | Proven by |
| --- | --- | --- |
| Agents Orchestrator | Pipeline controller; owns the variance ledger and the weekly gate sequence | G2 |
| Senior Project Manager | Re-baseline arithmetic: remaining committed work divided by measured throughput produces the new date | M2 |
| Chief of Staff | Decision routing; clears the sponsor queue that inflates decision latency | M5 |

### Diagnosis (Week 1)

| Agent | Role | Proven by |
| --- | --- | --- |
| Project Shepherd | Runs the re-baseline interviews; surfaces the constraint nobody will name in a group session | G1 |
| Studio Producer | Portfolio capacity overlay: which other commitments consume the same people and the same dependencies | M4 |
| Analytics Reporter | Tracker history and commit/deploy log forensics: cycle time, WIP, reopen rate, claimed-versus-actual cadence | M1 |
| Evidence Collector | One artifact per status claim; a claim with no artifact is struck from the record | G2 |

### Recovery Plan (Week 2)

| Agent | Role | Proven by |
| --- | --- | --- |
| Meeting Notes Specialist | Owns the decision log artifact: every decision carries a named owner and a date; no orphan action survives the session | G4 |
| Sprint Prioritizer | Cut list against the committed date, ranked by value and by whether the cut relieves the named constraint | G3 |
| Risk Reviewer | Residual exposure of every cut — quality debt, security, contractual obligation — recorded against the owner who accepted it | M6 |
| Change Management Consultant | One story and one number, delivered to sponsor, customer, and team inside the same window | G5 |

### Execution & Proof (Week 3-4)

| Agent | Role | Proven by |
| --- | --- | --- |
| Studio Operations | New cadence: fixed reporting slot, fixed inputs, mandatory reconciliation before a report is sent | G4 |
| Organizational Psychologist | Psychological safety and burnout signal; heroics are recorded as a capacity finding, not celebrated | P3 |
| Executive Summary Generator | Sponsor-facing report where the reported state is the tracker state, variance named in the first line | M1 |
| Reality Checker | Independent recomputation of remaining work and variance; default verdict NEEDS WORK | G5 |

## Week 1: Diagnosis

```text
├── Evidence Collector → verify chain of custody: confirm the 8 unedited status reports are the same artifacts the sponsor received — same content, same cycle dates, no export cleaned on the way through
├── Analytics Reporter → tracker history: created/closed per week, reopen rate, WIP per person,
│   cycle-time trend; commit and deploy frequency compared against claimed progress
├── Project Shepherd → separate written interviews: each team names its own blocker in private,
│   before any group session, so consensus cannot launder the answer; recorded under Interview
│   and People Data — no attribution, no quotes, no identifying detail
├── Studio Producer → portfolio overlay: shared people, shared dependencies, competing dates
├── Agents Orchestrator → open the variance ledger, one row per reported claim; no row carries a
│   person's name or a private statement
│
├── Constraint test — rank all four candidate causes with artifacts, never by intuition:
│   ├── Scope: committed scope grew after baseline (change log is the evidence)
│   ├── Capacity: available person-days below the work in the plan (staffing and absence data)
│   ├── Dependency: work waits on a party the team does not control (measured wait time)
│   └── Decision latency: work waits on a decision nobody owns (request-to-decision timestamps)
│
├── Quality Gate (G1): one cause is named primary with 2 independent artifacts, and the other
│   three are explicitly ranked — "we do not know yet" fails the gate, it is not a finding
├── Agents Orchestrator + Evidence Collector → mark every claim in the last 2 cycles
│   as substantiated / unsupported / contradicted
└── Quality Gate (G2): 100% of claims are marked and the unsupported share is a single number,
    not a range — that number is the starting variance for everything that follows; any ledger row
    that attributes a claim to a person without written consent fails the gate
```

## Week 2: Recovery Plan

```text
├── Chief of Staff → reopen the decision queue: every blocked item gets a decision owner
│   and a due date inside the decision-latency tolerance
├── Sprint Prioritizer → cut list against the committed date, ordered by value and by whether
│   the cut relieves the cause named at G1 — not by which stakeholder is loudest
├── Risk Reviewer → per-cut residual exposure: quality debt, security, contractual obligation
├── Senior Project Manager → new date = remaining committed work ÷ measured throughput, with a
│   confidence band and the measurement window named on the date itself (historical tracker weeks
│   by default, in-run only from Week 3); no date leaves the room without its band and its window
├── Change Management Consultant → one narrative for three audiences; the same number in all three
├── Meeting Notes Specialist → decision log artifact: who decided, when, what it displaced, what
│   it cost; a row with no owner or no date is not yet a decision and is reopened as a blocked item
├── Agents Orchestrator → recovery plan with a named owner per workstream and the weekly
│   re-plan window stated in the plan itself
└── Quality Gate (G3): every cut carries a named owner signature and a residual-risk line, the new
    date shows its arithmetic, the throughput window it used, and its confidence band, and no rule
    in Interview and People Data is broken by the plan — a date without arithmetic fails
```

## Week 3-4: Rebuild Cadence

```text
├── Week 3 — install the cadence that cannot lie:
│   ├── Studio Operations → one reporting slot, fixed day, fixed inputs, fixed owner,
│   │   reconciliation against the tracker completed before the report is sent
│   ├── Executive Summary Generator → sponsor report: first line is the variance, no status
│   │   colour without a variance row behind it
│   ├── Organizational Psychologist → safety pulse: can a team member say "this will slip"
│   │   without penalty; heroics logged as a capacity finding, published only as an aggregate
│   │   (n ≥ 5) and never attributed to the person who carried them
│   ├── Agents Orchestrator → daily block log: what moved, what is waiting, on whom
│   └── Quality Gate (G4): one full cycle in which every reported number traces to an artifact,
│       the unexplained-variance count is zero, 100% of decisions in the decision-log sample carry
│       an owner and a date, and the re-plan meeting log for the cycle shows start and end inside
│       60 minutes with zero status readings
│
├── Week 4 — prove it holds, then hand it over:
│   ├── Project Shepherd → two consecutive cycles, same slot, same owner, same inputs
│   ├── Reality Checker → independent recomputation of remaining work from tracker and commits;
│   │   NEEDS WORK stands until the numbers agree
│   ├── Change Management Consultant → external restatement: customer or partner note matches the
│   │   re-committed date and the reduced scope word for word, and carries constraints and
│   │   artifacts only — never a person's sentence
│   ├── Senior Project Manager → exit re-baseline: what remains, at what rate, deliverable by when
│   └── Quality Gate (G5): the re-committed date and the reduced scope appear identically in the
│       sponsor deck, the external note, and the tracker, after 2 consecutive cycles inside the
│       exit tolerance; the forecast result is read once and named as a single observation, not a
│       rate; the deck and the external note carry constraints and artifacts only; and the raw
│       interview notes are confirmed destroyed at handover
```

## Key Decisions

| Decision Point | When | Who Decides |
| --- | --- | --- |
| Which scope items are cut, and what each cut costs externally | Week 2, before any date is re-committed | Sponsor, on the Sprint Prioritizer cut list with Risk Reviewer exposure |
| The new committed date, its confidence band, and the throughput window it used | Week 2, after throughput is measured — never before, and never on an unnamed window | Senior Project Manager proposes, Sponsor signs, engineering leads confirm the throughput |
| What interview and safety-pulse data may be used for, and what may never leave the room | Week 1, before the first interview is taken | Organizational Psychologist and Agents Orchestrator, bound by Interview and People Data |
| When the sponsor hears the real number, and from whom | Week 1, day 3-5, when the variance ledger closes | Chief of Staff routes, Executive Summary Generator delivers |
| Whether to stop the program instead of extending it | Week 2, if the cut list cannot restore the committed date at 80% confidence | Sponsor, advised by Risk Reviewer |
| What the customer is told about the previous date, and in what order | Week 2, in the same window as the internal decision, never after | Account Owner and Change Management Consultant, approved by Sponsor |
| Whether a disputed constraint claim survives the gate | Week 1 gate review | Project Shepherd and Evidence Collector; deadlock escalates to Sponsor |

## Success Criteria

| Metric | Target |
| --- | --- |
| M1 · Reported-vs-actual variance (unexplained status items per cycle) | 0 by end of Week 3, and 0 again in the following cycle |
| M2 · Forecast accuracy (committed items delivered by their committed date) | Single observation, not a rate: the one complete 2-week cycle the run holds (Week 3 to end of Week 4) delivers at least 80% of its committed items, or the miss and its cause are named at G5. The forecast rate over time is P1 |
| M3 · Remaining-work variance against the re-baselined plan | 5% or less for 2 consecutive cycles |
| M4 · Constraint evidence coverage | 4 of 4 candidate causes ranked, primary backed by at least 2 independent artifacts |
| M5 · Decision latency (median request-to-decision from the decision log) | 3 business days or less |
| M6 · Scope cuts with a named owner signature and recorded residual risk | 100%, signed within 2 business days of the cut being proposed |

## Common Pitfalls

| Pitfall | Mitigation |
| --- | --- |
| A green dashboard on a red program — reporting that optimizes for the audience | Report from artifacts, not from status fields; G2 marks every claim and quantifies the unsupported share before any plan is written |
| Recovery plans that add people — the standard reflex, and usually a capacity multiplier of one minus onboarding drag | Adding people is allowed only where capacity is the named constraint at G1 and the ramp is modelled in the new date; otherwise it is a decision to slip later |
| Re-baselining without telling the customer — the internal date moves, the external promise does not | G5 fails unless the external note matches the tracker word for word; the Account Owner signs before the date changes anywhere |
| Cutting scope without cutting the date — the work shrinks, the deadline does not, and the red program simply becomes smaller and still late | Every cut is paired with either a date change or a measured throughput justification, signed at G3 |
| Heroics that hide systemic capacity failure — a team that absorbs the gap teaches the organization that the plan was fine | Log overtime and recovery work as a capacity finding at G4; sustained heroics re-open the constraint test instead of being celebrated |
| One clean cycle treated as recovery — a good week is mistaken for a fixed system | Exit requires 2 consecutive cycles inside the exit tolerance, with the same cadence owner and the same inputs; a single forecast cycle is reported as one observation, never as an accuracy rate |
| Candour traded for a vivid quote — one attributed sentence in a deck ends the source of every later interview | Constraints and their artifacts go into the ledger and the deck; sentences and raw notes stay with the Organizational Psychologist and are destroyed at handover |

## Post-runbook

Windows longer than the 4-week runbook. If these are not assigned, the recovery decays into a story about a good month.

| Metric | Owner | Measured on |
| --- | --- | --- |
| P1 · Forecast accuracy over 8 weeks (committed items delivered by committed date) | Senior Project Manager | Week 8 after exit, from tracker commitments against delivery |
| P2 · Repeat slippage on the same program (another two slips within 2 quarters) | Project Shepherd | Quarterly portfolio review |
| P3 · Team attrition and burnout signal (voluntary exits and sustained overtime) | Organizational Psychologist | End of the first full quarter after exit |
| P4 · Cadence survival (reported state still equals actual state after handover) | Studio Operations | Monthly for the first quarter after exit |
