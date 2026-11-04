# Runbook: Feature Discovery to Spec

> **Mode**: NEXUS-Sprint | **Duration**: 3 weeks | **Agents**: 15

## Scenario

A feature request arrives as one sentence from sales. It gets built over six weeks, then rejected by the users it was meant for. Nobody wrote down what "done" meant, so stakeholders defended different definitions, QA had nothing to fail against, and the post-launch argument was recollection rather than evidence.

This runbook converts a request into a **spec whose acceptance criteria a test can run against**, plus an explicit list of what is not being built. It stops before implementation. Three weeks, four gates: evidence in week 1, framing and options in week 2, the specification and the decision in week 3.

The agents do evidence, framing, specification, and grading. They do not approve anything. Every gate below is an agent passing judgement on an artifact, and the decision belongs to the named humans who can sign, fund, or veto it. The run exists to hand each of them one page to read and one dated row to sign, so approval is a recorded act rather than a recollection.

Doctrine: **an acceptance criterion QA cannot fail is a wish.** "Improve the experience" is a wish. "The export returns a CSV of 10,000 rows in under 5 seconds at p95, or a 504 with a typed error body" is a criterion.

## Applicability

| Use this runbook when | Use a different runbook when |
| --- | --- |
| The request is one sentence or one sales commitment | The spec is agreed and must ship — `enterprise-feature` |
| "Done" is disputed and QA has nothing to assert | No product exists — `startup-mvp` |
| You must decide *what* to build and contract it | The answer is needed in five days — `design-sprint` |
| Nobody can name the non-goals | The backlog needs sequencing — `product-sprint-prioritizer` territory |
| Build vs buy vs decline is open | Production is broken — `incident-response` |
| Prior features were rejected by target users | The code is the problem — `codebase-modernization-program` |

## Required Inputs

Nothing this runbook produces is an input. The spec body, the acceptance-criteria register, and the out-of-scope list are outputs of weeks 1–3; listing them as blockers would make the run circular. Every input below exists before day 1 and is owned outside the run.

| Input | Why it blocks | Owner |
| --- | --- | --- |
| The request verbatim, with its source record (email, CRM note, call transcript) | Paraphrase erases the constraint behind it | Product Manager |
| Read access to usage data, the support queue, and churn records, with the dataset names | Frequency claims stay anecdote without a countable source | Analytics Reporter |
| Named approvers who can sign or veto, in writing — one row per approver with the decision they own (scope, budget, or risk) and the authority basis behind it (delegation, contract clause, or budget line) | An approver whose authority is unstated cannot approve, and approvals discovered at handoff restart discovery | Senior Project Manager |
| The named human with budget authority for a buy decision, and the ceiling they control | A build / buy / decline call by people who cannot commit money is a recommendation, not a decision | Senior Project Manager |
| A committed decision date on the calendar, agreed by those approvers | An undated discovery does not end, it gets quieter | Product Manager |
| The requester's committed implementation start date, as a calendar date (kickoff) | Every Post-runbook window is measured from it; an undated kickoff makes those metrics unmeasurable | Product Manager |
| Written confirmation that no implementation work has started | Code before the contract turns the spec into an excuse | Senior Project Manager |
| The requester, for one 30-minute interrogation, and their signature on the non-goals and the kickoff date | Half the request is an unstated workaround | Deal Strategist |
| The current UI surface in scope (routes, screens) and the existing brand source | Concepts cannot be drawn against an imagined interface | UI Designer |

## Thresholds

Every threshold this runbook references, defined once. A gate or metric that cites a term below uses this definition, not a local reading.

| Term | Definition | Where checked |
| --- | --- | --- |
| Evidence is sufficient | A claim is sufficient when it is supported by ≥2 independent sources in ≥2 different channels (e.g. ticket queue plus interview), at least one being quantitative with n ≥ 30 records or ≥5 interviews, each openable by a second person, and no open contradiction. Anything below is labelled `weak` and cannot be the only basis for an option. | G1 |
| Contradicted | A claim is contradicted when ≥2 independent sources disagree with it. A contradicted claim kills the option that depended on it. | G1 |
| Decision deadline | 17:00 on week 3, day 5 — the calendar date recorded in Required Inputs. At that moment the gate records PASS, NEEDS WORK, or NO DECISION. NO DECISION is a failed run, not an extension. | G4, M6 |
| Approver decision | One row per named approver from Required Inputs, recorded in the G4 record: the decision (approve, veto, or pending), the authority basis — the delegation, contract clause, or budget line that lets that person decide — and the date it was taken. An approver with no row, or a row still `pending` at the deadline, blocks PASS. Silence is not approval, and an agent's verdict is not a substitute for a human's decision. | G4, M7 |
| Kickoff | The implementation start date the requester commits to at G4, as a calendar date. It is the zero point for every Post-runbook window; a kickoff left relative ("when we start") makes those metrics unmeasurable, so G4 fails without a date. | G4, Post-runbook |
| Criterion is runnable | It names an observable, a unit, a threshold, a failure condition, and a named test owner, so a QA engineer who is not the author can write the assertion and someone is accountable for running it. The test: what line in a test file goes red? If the answer is prose, it is not runnable. | G3, M1 |
| Concept set | Three distinct solutions to the **recommended option's** primary flow, each with a wireframe or screenshot a non-author can read, differing in layout or information hierarchy — not in colour — plus one chosen with the reason written down. Concepts are drawn for the recommendation only, after the options are sized: concepts for every surviving option would triple the drawing time and grade nothing the gate can use. | G2, M4 |
| Reworked requirement | A requirement in the kickoff baseline whose acceptance text changes after kickoff, excluding typo and link fixes and changes carrying a change-record ID. Rework rate = reworked ÷ baseline count. | Post-runbook |
| Changed after kickoff | Any edit to a requirement's goal, threshold, or a non-goal, with or without a change record. | Post-runbook |

## Agent Roster

The trace column names the gate or metric that makes the agent's output load-bearing: G1–G4 are the quality gates in the week sections, M1–M7 are the Success Criteria rows.

### Evidence (Week 1)

| Agent | Slug | Role | Trace |
| --- | --- | --- | --- |
| Trend Researcher | `product-trend-researcher` | Table stakes, differentiating, or irrelevant, with a source per claim | G1, M2 |
| Research Synthesist | `research-synthesist` | Claim register; every claim labelled evidenced / weak / contradicted / unknown, with each label earning its name | G1, M2 |
| UX Researcher | `design-ux-researcher` | 5–8 interviews on the current workflow and what it costs | G1, M3 |
| Feedback Synthesizer | `product-feedback-synthesizer` | Tickets, churn, and reviews clustered into recurring jobs | G1, M3 |
| Analytics Reporter | `support-analytics-reporter` | Instrumented counts: how many accounts, how often, which segment, over which window — every frequency carries a source query, a date, and an n | G1, M3 |

### Framing (Week 2)

| Agent | Slug | Role | Trace |
| --- | --- | --- | --- |
| Product Manager | `product-manager` | Problem statement with no solution nouns; the recommendation and its author | G2, M6 |
| Deal Strategist | `sales-deal-strategist` | What the account needs to close, minus the feature name it asked for; the close evidence each option has to answer to | G2, M4 |
| Sprint Prioritizer | `product-sprint-prioritizer` | Three options (S / M / L) with cost of delay and preconditions | G2, M4 |
| UI Designer | `design-ui-designer` | Three distinct concepts of the recommended option's primary flow, one selected with a written reason | G2, M4 |

### Specification (Week 3)

| Agent | Slug | Role | Trace |
| --- | --- | --- | --- |
| Workflow Architect | `specialized-workflow-architect` | Spec body: goal, non-goals, flows, states, edge cases, error taxonomy | G3 |
| Software Architect | `engineering-software-architect` | Data contract, constraints, decisions left open on purpose | G3 |
| Senior Project Manager | `project-manager-senior` | One criterion per requirement, each with observable, unit, threshold, failure condition, and a named test owner | G3, M1 |

### Decision (Week 3)

| Agent | Slug | Role | Trace |
| --- | --- | --- | --- |
| Agents Orchestrator | `agents-orchestrator` | Owns the decision gate: confirms the G1–G3 artifacts exist, calls the gate, records the verdict, its author, and its date | G4, M6 |
| Executive Summary Generator | `support-executive-summary-generator` | One-page decision record per named approver — what is being approved, what it costs, what is still unknown — written so the approver can decide from that page alone | G4, M7 |
| Reality Checker | `testing-reality-checker` | Can QA fail each criterion? Issues the verdict, default NEEDS WORK | G4, M1 |

## Week 1 — Evidence

```text
├── Product Manager → request verbatim, source recorded, requester interrogated once
├── Deal Strategist → what the account needs to close, minus the asked-for feature
├── UX Researcher → 5-8 interviews on the current workflow and its cost
├── Feedback Synthesizer → tickets, churn, reviews clustered by recurring job
├── Analytics Reporter → baseline counts per claimed frequency: source query, date, cohort, n
├── Trend Researcher → baseline, differentiating, or irrelevant, with source
├── Research Synthesist → claim register: evidenced / weak / contradicted / unknown
└── Quality Gate G1: pass requires every register row to carry one of the four labels,
    every `evidenced` row to carry a link a second person opens in under a minute, every
    quantitative claim to carry n, cohort, window and date, and both Thresholds tests
    applied row by row rather than promised: (1) sufficiency — ≥2 independent sources in
    ≥2 different channels, at least one quantitative with n ≥ 30 records or ≥5
    interviews; (2) contradiction — ≥2 independent sources disagreeing with the row.
    Fails on one blank status cell, one dead link, one frequency with no n, or one row
    still labelled `evidenced` that fails either test — the remedy is the relabel, not a
    pass. A row that fails sufficiency is relabelled `weak` and kept: weak evidence is
    usable colour, but a `weak` row can never be the sole basis of an option at G2, and a
    contradicted row kills the option that depended on it.
```

**Customer data handling.** The access named in Required Inputs is a ceiling, not a licence. Usage and churn extracts stay inside the Analytics Reporter's analysis environment and reach the register as counts, cohorts, and windows — never as row-level exports. Interviews are recorded only with explicit consent, the consent is logged against the interview, and a participant may withdraw a quote up to the moment the register is frozen at G1. The claim register carries claim ID, label, source reference, and cohort count only: no names, emails, account IDs, or quotes that identify a person, with identifying detail held in a restricted evidence folder referenced by claim ID. The Product Manager names who outside the Evidence group may open that folder, and everyone with access is listed in the G4 record.

## Week 2 — Framing

The request is compared against the evidence in public, before anyone defends a solution.

| Claimed | What the data shows | Unknown | Resolved before build by |
| --- | --- | --- | --- |
| "Customers keep asking" | Ticket and interview frequency in numbers, or downgraded to `weak` | Share of base asking | Feedback Synthesizer + Analytics Reporter, cohort count |
| "We lose deals without it" | Lost-deal reason separated from the feature name | Whether it repeats | Deal Strategist, win/loss review |
| "It's a two-week build" | No estimate before the spec exists | Surface area, migration cost | Software Architect, t-shirt sizing |
| "Everyone expects it" | Competitor presence, with source | Whether users switch on it | Trend Researcher, teardown |
| "It's safe" | Nobody named the failure mode | Blast radius, reversibility | Reality Checker, pre-mortem |

```text
├── Product Manager → problem statement with no solution nouns
├── Deal Strategist → lost-deal reason separated from the asked-for feature name; which
│   of the options that close evidence actually supports
├── Sprint Prioritizer → three options (S / M / L) with cost of delay and preconditions
├── UI Designer → three concepts of the primary flow for the recommended option; one
│   selected, reason recorded against the evidence, not against taste
├── Research Synthesist → which single open question would flip the decision
├── Software Architect → feasibility triage; new integration surfaces named
├── Reality Checker → challenges the framing before it hardens
└── Quality Gate G2: pass requires 3 options each carrying cost of delay, preconditions,
    and a citation of the Deal Strategist's close evidence (lost-deal reason, win/loss
    review) the option answers to — or an explicit "no deal evidence" — plus 3 distinct
    concepts of the recommended option's primary flow with one selection reason, and a
    written build / buy / decline recommendation with a named author that commits no
    budget. Fails if an option has no cost of delay, if no option cites the Deal
    Strategist's close evidence, if a concept set is two recolours of one layout, if the
    selection reason cites preference instead of a register entry, or if a `weak`
    register row is the sole basis of an option.
```

## Week 3 — Specification

```text
├── Workflow Architect → goal, non-goals, flows, states, edge cases, error taxonomy
├── Software Architect → data contract, constraints, decisions left open on purpose
├── Senior Project Manager → one criterion per requirement, each a runnable assertion
│   with an observable, a unit, a threshold, a failure condition, and a named test owner
├── Product Manager → named out-of-scope exclusions sent to the requester to sign
├── Reality Checker → could QA fail each criterion? default NEEDS WORK
└── Quality Gate G3: pass requires 0 register rows missing any of the six elements
    (requirement, observable, unit, threshold, failure condition, test owner), ≥3 named
    non-goals carrying a requester signature, and the open-decision list from the Software
    Architect still intact — every decision marked open still open, each with an owner and
    a resolution date. Fails on one incomplete row, including a row with no named test
    owner; on one unsigned exclusion; or on one open decision the spec closes on its own
    authority. It is rejected here, not debated in review.
```

### Acceptance Criteria Standard

A criterion is only as good as the test it makes possible. Applied by the Senior Project Manager at authoring and by the Reality Checker at G3.

**Fails a later QA run — acceptable:**

| Criterion | Why it holds |
| --- | --- |
| "Given an account with 10,000 transactions, `POST /exports` returns HTTP 200 with a CSV row count of 10,000 within 5s at p95 over 20 runs on staging; over 5s it returns HTTP 504 with body `{\"error\":\"export_timeout\"}`." | Observable (HTTP status, row count, elapsed), unit (seconds, rows), threshold (5s p95, 20 runs), failure condition (timeout returns 200, or body differs). QA writes the loop, gets 6.1s, and the run goes red without asking anyone. |

**Looks acceptable, cannot be failed:**

| Criterion | Why it is not a criterion |
| --- | --- |
| "The export experience is fast and intuitive for enterprise accounts, with clear error messaging." | Every noun is a judgement. "Fast" has no unit, "intuitive" no observable, "enterprise accounts" no cohort, "clear" no assertion. A later QA run cannot go red on it, so the criterion cannot distinguish a working build from a broken one — and it survives review because it echoes what the requester said. |

The register has one column per element: `requirement | observable | unit | threshold | failure condition | test owner`. A row with an empty element column is the G3 failure, and "test owner" means the person who runs it, not the person who wrote it.

## Week 3 — Decision

The orchestrator owns the gate. The Reality Checker issues the verdict. The Product Manager fills neither role, and the verdict record states who issued it, so a reader can tell authoring from grading. The verdict is a grade of the artifact, not the approval: G4 does not pass on the Reality Checker's signature alone, it passes when every named approver has a dated decision row and a page they read before taking it.

```text
├── Agents Orchestrator → verifies G1, G2, G3 artifacts are on file; schedules the gate
│   inside the committed decision deadline; assembles the approver decision rows;
│   records verdict, author, and timestamp
├── Reality Checker → walks the register asking "what fails here?"; verdict PASS or
│   NEEDS WORK, default NEEDS WORK when any row is unanswerable
├── Executive Summary Generator → one page per named approver: recommendation, options,
│   cost, the open unknowns and what they would change, the non-goals, the verdict
├── Product Manager → decision recorded with the signed out-of-scope list attached
├── Senior Project Manager → collects one dated decision per named approver, and the
│   requester's committed kickoff date
└── Quality Gate G4: pass requires a verdict of PASS issued by the Reality Checker, the
    G1-G3 artifact list checked row by row, a verdict timestamp at or before the decision
    deadline, one one-page decision record per named approver on file and referenced in
    that approver's row, and one recorded approver decision for every named approver —
    decision (approve / veto / pending), authority basis, and date — plus the committed
    kickoff date and, for every Post-runbook row, a named owner and an absolute
    measurement date. Fails on NEEDS WORK, on a missing artifact, on an approver with no
    row or a row still `pending` at the deadline (silence is not approval), on a buy
    recommendation with no dated budget decision, on a kickoff that is not a calendar
    date, or on NO DECISION at 17:00 on week 3 day 5.
```

**Approver decision record.** One row per named approver from Required Inputs. The same table appears in the G4 record and inside each approver's one-page decision record, so the page they read and the decision they took are the same artifact.

| Approver (from Required Inputs) | Decision | Authority basis | Date | Page read |
| --- | --- | --- | --- | --- |
| Name, and the decision they own (scope, budget, or risk) | approve / veto / pending | The delegation, contract clause, or budget line that lets this person decide | YYYY-MM-DD | Link to that approver's one-page decision record |

`pending` is a recorded state, not a pass: one pending row at the deadline turns the gate into NO DECISION. A veto is recorded the same way and is not negotiated away — it ends the run with the verdict and the reason on file.

**Non-negotiable:** the spec is not accepted until every acceptance criterion is phrased so a later QA run could fail it, the out-of-scope list is non-empty and signed by the requester, and every named approver has a dated approve-or-veto row on file. A criterion lacking a threshold, a unit, a failure condition, or a test owner is rejected at G3, not negotiated afterwards; a spec on file is not an approval.

## Key Decisions

| Decision Point | When | Who Decides |
| --- | --- | --- |
| Build vs buy vs decline | Week 2, day 3, before options are sized | Product Manager + Software Architect — a recommendation only; neither can commit money, so the recommendation carries a named author and no budget |
| Buy commitment and budget release | Week 3, day 1, before the spec assumes a purchase | The named budget authority from Required Inputs, dated in the G4 record; a buy recommendation with no dated budget decision fails G4 |
| Scope ceiling: what v1 covers | Week 2, day 5 | Product Manager + requester |
| Which concept goes forward | Week 2, day 4 | UI Designer proposes, Product Manager accepts on register evidence |
| Whether an open unknown blocks build | Week 3, day 1 | Reality Checker |
| Who owns the acceptance criteria | Week 3, day 1 | Senior Project Manager; QA sign-off named |
| Approver list and authority basis recorded | Week 3, day 2 | Senior Project Manager, with each approver |
| Approver decisions taken in writing (approve / veto / pending) | Week 3, day 4 | Each named approver, on their one-page decision record |
| Kickoff date committed | Week 3, day 4, alongside the approver decisions | The requester commits the implementation start date; the Product Manager records it |
| Gate verdict called and recorded | Week 3, day 5, at or before the decision deadline | Agents Orchestrator runs the gate; Reality Checker issues the verdict |

## Success Criteria

Everything here is observable inside the three weeks.

| Metric | Target | Window | Measured by |
| --- | --- | --- | --- |
| M1 — register rows with all six elements (requirement, observable, unit, threshold, failure condition, test owner) | 0 rows missing, including 0 rows with no named test owner; register size recorded | At G3 | Reality Checker |
| M2 — `evidenced` claims with a source a second person can open | 0 without a working link | At G1 | Research Synthesist, audited by Reality Checker |
| M3 — quantitative claims carrying source query, cohort, window, and n | 0 without all four | At G1 | Analytics Reporter |
| M4 — options carrying cost of delay and a Deal Strategist close-evidence citation, and the concept set on file for the recommendation | 3 of 3 options; 3 concepts on the recommended option, 1 selection reason | At G2 | Sprint Prioritizer + UI Designer; close evidence audited by Deal Strategist |
| M5 — out-of-scope items, requester-signed | ≥3 | At G3 | Product Manager |
| M6 — working days from the recorded request date to the G4 verdict timestamp | ≤10 working days, and not past the committed date | At G4 | Agents Orchestrator |
| M7 — named approvers with a recorded decision, authority basis, and date | 1 row per approver; 0 missing, 0 `pending` at PASS | At G4 | Senior Project Manager, checked by Agents Orchestrator |

## Post-runbook

These windows close after the runbook does. They are not scored at G4 and must not be reported as in-run results. **Kickoff** is the implementation start date the requester commits to at G4, recorded as a calendar date; the owner named here measures the metric on the absolute date written into the G4 record, and a row without an owner and a calendar date fails G4 rather than being measured later.

| Metric | Definition | Threshold | Owner | Measurement date |
| --- | --- | --- | --- | --- |
| Spec-to-build rework rate | Reworked requirements ÷ requirements in the kickoff baseline | ≤20% | Senior Project Manager | Absolute date in the G4 record, eight weeks after kickoff |
| Requirements changed after kickoff | Requirements whose goal, threshold, or non-goals changed ÷ baseline count | ≤10%, and 0 without a change-record ID | Product Manager | Absolute date in the G4 record, eight weeks after kickoff |
| Non-goal violations | Non-goals that were built anyway, counted from the build log and the signed list | 0 | Product Manager | Absolute date in the G4 record, eight weeks after kickoff |

## Common Pitfalls

| Pitfall | Mitigation |
| --- | --- |
| Discovery that never ends because research feels safer | Committed decision date in Required Inputs; G1 accepts labelled unknowns, not blank cells |
| A gate nobody calls | The Agents Orchestrator owns G4 and records its timestamp; a verdict timestamp after the deadline is recorded as NO DECISION and fails |
| "Customers keep asking" accepted on volume | Analytics Reporter attaches n, cohort, window and date; a frequency without them fails G1 |
| Options that are one idea in three sizes with no concept behind them | UI Designer must produce a concept set at G2; two recolours of one layout fail |
| A spec written by the loudest stakeholder | Authored by the Workflow Architect; reviewers named in advance |
| Criteria invented by whoever grades them | Authored by the Senior Project Manager, graded by the Reality Checker at G3 |
| Criteria that read well and assert nothing | The "what line goes red?" test at G3; prose is not a criterion |
| No non-goals, so scope is whatever nobody blocked | Out-of-scope list is a G3 item, requester-signed |
| Validating with people who already agreed | Interviews from the target cohort, not internal champions |
| A spec so detailed it decides engineering's work | Software Architect lists every open decision with an owner and a resolution date; G3 fails a spec that closes one on its own authority |
| Approvers named on day 1 and never asked to decide | G4 records one dated decision row per named approver, with the authority basis; a `pending` row at the deadline is NO DECISION, and an agent's PASS is never counted as a human's approval |
| Post-runbook windows measured from a kickoff nobody scheduled | Kickoff is the requester's committed implementation start date, recorded as a calendar date at G4; every Post-runbook row carries an owner and an absolute measurement date |
| Customer data collected because read access was granted | Access is a ceiling, not a licence — counts and cohorts reach the register, identifiers stay in the restricted folder, and interviews are recorded only with logged consent |
| Leftover metrics quoted as if the run proved them | Post-runbook table names the owner and the absolute date instead |
