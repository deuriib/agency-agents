# Runbook: Sales Pipeline Engine

Mode: NEXUS-Sprint | Duration: 4-6 weeks | Agents: 15

## Scenario

The pipeline is a number in a spreadsheet that everyone privately distrusts. Outbound is a list bought from a vendor. Discovery calls are demos with questions attached. Proposals are written the night before. The forecast is optimism with a date on it. Every stage has a name and no definition, so two people reading the same deal report two different stages, and the number that reaches the board is a sum of private guesses dressed as a commitment.

This runbook builds a pipeline engine: a defined ICP, a signal-based outbound motion, a discovery method that disqualifies fast, proposal discipline, and a forecast that reconciles against closed reality. Doctrine: **a pipeline you cannot reconcile against closed outcomes is a mood.** The forecast is measured against what actually closed, and the definition of every stage is a criterion, not a feeling — an observable condition that either holds on a named deal or does not.

Compliance boundary: outbound is regulated, and the rules differ by jurisdiction. A purchased list is a source of contact data, never a source of consent. What may be sent to whom, on what legal basis, into which jurisdiction, and against which suppression list comes from a written lawful-basis determination per jurisdiction, signed and dated by named counsel or the DPO — a human outside this roster — and recording the basis relied on, the balancing or legitimate-interest assessment reference, the jurisdictions in the send set, and the suppression source. The Legal Compliance Checker executes that determination and never issues one. An agent that sends unsolicited messages is a liability, not a growth tactic. Volume is not a defense, "the vendor said it was compliant" is not documentation, and no roster agent's own reading of the law is a legal basis.

Scope is the motion that creates and converts pipeline, and the forecast that reports it. It is not demand generation, not pricing, not product scope, not delivery, and not post-sale service.

## Applicability

| Use this runbook when | Use a different runbook when |
| --- | --- |
| Four quarters of closed-won and closed-lost history exist to reconstruct from | There is no closed-won history to reconstruct from — use `zero-to-one-venture` before this runbook |
| The revenue motion must be built: ICP, signals, sequences, discovery, proposals, forecast | The problem is reach, content, and brand across channels — use `marketing-campaign` |
| Outbound exists but is volume-driven, and inbound leads arrive unqualified | The question is what to charge or how to package it — use `pricing-and-monetization-review` |
| Discovery is a demo, and proposals answer questions nobody asked | The question is what to build next — use `feature-discovery-to-spec` |
| The forecast cannot be reconciled against closed outcomes | A committed delivery program is red and needs recovery — use `delivery-recovery` |
| Two people apply the same stage name differently on the same deal | The customer is already live and needs service — use `customer-support-operations` |

## Required Inputs

Raw sources only. The ICP, the signal taxonomy, the sequences, the stage criteria, the proposal structure, and the forecast model are outputs of the run — listing any of them as a blocking input would make the runbook its own prerequisite.

Two kinds of input appear below and they are not interchangeable: data custody, which a roster agent can legitimately hold and hand over (the CRM as reps use it, the pricing as sold), and a signed human act, which no roster agent may perform for itself (the lawful-basis determination, signed by a named human outside this roster and never issued by the checker that executes it).

| Input | Why it blocks | Owner |
| --- | --- | --- |
| Four quarters of closed-won and closed-lost opportunities, each with the reason recorded at close | The only honest ICP and the only honest stage criteria are derived from what closed and what died | Pipeline Analyst |
| The CRM stage definitions as reps actually use them, including where the same stage is applied inconsistently | A new definition has to land on a known starting state, not a hoped-for one | Pipeline Analyst |
| A written lawful-basis determination per jurisdiction, signed and dated by named counsel or the DPO (a human outside this roster): the basis relied on, the balancing or legitimate-interest assessment reference, the jurisdictions in the send set, and the suppression source | Nothing may be sent until what may be sent to whom is signed. No send may target a jurisdiction without a signed determination, and the send set must be a subset of the signed set | Named counsel or DPO — never a roster agent |
| Pricing and packaging exactly as sold: list price, discounts granted, contract terms | Sequences that promise value the price does not deliver, and forecasts that assume an ACV nobody signs | Deal Strategist |
| A named owner of the number, with written authority to commit a forecast | A forecast with no owner is a rumor with a spreadsheet | Executive sponsor |

## Agent Roster

Traceability: `G1`-`G5` are the phase gates; `M1`-`M5` are the Success Criteria rows. Every row is justified by the gate or metric that fails when the agent is missing.

### Command (Always Active)

| Agent | Role | Proven by |
| --- | --- | --- |
| Agents Orchestrator | Sequences the phases, holds each gate, releases a sequence segment and a forecast commit and nothing else | G1, G3, G5 |
| Senior Project Manager | Gap list to owned tasks with dates; tracks the disqualification and stage-audit backlog to zero | G2, M1, M2 |
| Sales Coach | Coaches reps against the new stage criteria and call standard; runs forecast review deal by deal | G4, M1 |

### Demand & Signal (Week 1-2)

| Agent | Role | Proven by |
| --- | --- | --- |
| Offer & Lead Gen Strategist | ICP segmentation from closed-won concentration, the offer, and the lead assets that make the first conversation about a problem | G1, M4 |
| Outbound Strategist | Signal taxonomy, channel plan, sequences with volume ceilings, personalization rules, stop rules | G2, G3 |
| Content Creator | Message-market fit copy and proof assets; outbound copy that survives a compliance read | G2, M5 |

### Conversion (Week 3-4)

| Agent | Role | Proven by |
| --- | --- | --- |
| Discovery Coach | Question design, call structure, current-state mapping, gap quantification, and the disqualifying question asked in the first call | G4, M1 |
| Deal Strategist | Qualification scoring, stakeholder map, competitive position, discount position inside authority | G4, M2 |
| Sales Engineer | Technical discovery, a demo built from the discovery record, POC scope with entry and exit criteria | G4 |
| Proposal Strategist | Win themes, executive summary, and a proposal that answers only what the buyer asked | G5 |

### Measurement & Compliance (Week 5-6)

| Agent | Role | Proven by |
| --- | --- | --- |
| Pipeline Analyst | Stage-exit auditing, velocity and conversion analysis, the forecast model, backtest against closed quarters | G5, M1, M3 |
| Analytics Reporter | Dashboard for conversion, cycle time, coverage; forecast-vs-closed reconciliation per category | G5, M1, M3 |
| Legal Compliance Checker | Executes the signed lawful-basis determination: jurisdiction mapping, suppression enforcement, opt-out handling, sequence content review. It never issues the determination | G3, M5 |

### Expansion & Proof (Week 5-6)

| Agent | Role | Proven by |
| --- | --- | --- |
| Account Strategist | Handoff to expansion: land-and-expand plan, stakeholder continuity, net revenue retention baseline | G5, M4 |
| Reality Checker | Final verdict on the packaged forecast and audit evidence; NEEDS WORK is the default | G5, M3 |

## Thresholds

Every number a gate or a stage criterion cites is defined here once. A threshold that is not written down is a feeling with a percentage sign.

| Threshold | Definition | Default value | Owner |
| --- | --- | --- | --- |
| Signal | A dated, sourced event at a named account that precedes a buying motion: a funding round, hiring into the function the product serves, a stack or platform change, a leadership change in the buying function, a published compliance deadline. It qualifies only if it carries a source and a date, maps to an ICP segment, and implies the ICP's stated pain. | At least 1 qualifying signal per account per 90 days; an account with no signal is not worked by outbound | Outbound Strategist |
| ICP fit | Three mandatory criteria, all checkable from a public source: segment, size band, and a use case the product serves today. Two optional: technology fit, a contractual or regulatory trigger. | 3 of 3 mandatory; 2 of 3 is a disqualification, not a maybe | Offer & Lead Gen Strategist |
| Minimum deal size | The annual contract value below which direct selling costs more than the deal returns. The figures at right are defaults, not findings: before G1 they are replaced by the ACV at which direct selling stops paying, derived from the four-quarter reconstruction and recorded in this row together with its derivation. | Default, replaced before G1: work directly at $25k ACV and above; route $10k-$25k to a pooled or partner motion; disqualify outbound below $10k | Deal Strategist |
| Stage 2 to 3 exit (qualified) | The deal moves only when the three mandatory ICP criteria match, the buyer states the problem in their own words on a recorded call, and the pain carries a date — a trigger or a deadline. | All three; no partial credit | Discovery Coach |
| Stage 3 to 4 exit (discovery complete) | Current state documented, gap quantified in the buyer's unit (hours, cost, risk), decision authority and signature path named, a timeline stated by the buyer, and every hard disqualifier checked. | All five, each traceable to a call note | Discovery Coach |
| Stage 4 to 5 exit (proposal) | A proposal is issued only after a Stage 3 exit, every section traces to a discovery answer, the economic buyer is engaged and named, and a mutual action plan with dates is agreed. | Zero proposals issued without a Stage 3 exit record | Proposal Strategist |
| Stage 5 to Commit | Written mutual action plan with signature dates, legal or procurement engaged, no open technical validation, discount inside authority. | All four; any deviation demotes the deal to Best Case with a named reason | Deal Strategist |
| Forecast accuracy tolerance | Absolute gap between the committed forecast and closed-won for the same period, measured per category. | At most 10% at commit, at most 25% at best case | Pipeline Analyst |
| Opt-out window | The time allowed between a recipient asking to stop and that request being enforced on every channel. A request counts from receipt, on whatever channel it arrives. | Automated sends: suppressed within 24 hours of receipt; manual sends: suppressed before the next send; the suppression list reflects in the send list within 1 hour | Legal Compliance Checker |
| Disqualification rule | Any hard disqualifier — no ICP fit, below minimum deal size, no identified authority by the end of discovery, no compelling event within 12 months, no signed lawful-basis determination covering the deal's jurisdiction — closes the deal as Closed-Lost with a coded reason. | Closed within 5 business days of the disqualifier appearing; zero disqualified deals left open | Deal Strategist |
| Stage-criteria audit sample | The set G4 scores criterion by criterion: every open deal at Stage 3 or later, up to a cap of 20 deals; above 20, a random 20 drawn by the Pipeline Analyst and named in the audit record. | Every open deal at Stage 3 or later up to 20; a random 20 when the open set is larger | Pipeline Analyst |
| Stage-move authority | Who may move a deal across a stage boundary. | A rep may move 2 to 3; a 3 to 4 or 4 to 5 move needs a co-sign; only the forecast owner commits | Sales Coach |

## Week 1-2: ICP & Signal Design

```text
├── Pipeline Analyst → reconstruct what actually closed: four quarters of won and lost by segment,
│   deal size, source and cycle length; flag every row whose stage history contradicts its close reason
├── Pipeline Analyst → write the stage definitions as they are used today, naming the observed
│   inconsistency per rep so the new definition can be measured against a real starting state
├── Offer & Lead Gen Strategist → ICP from closed-won concentration, not aspiration: segment, size
│   band, use case and urgency trigger; one primary segment, two secondary, the rest declined in writing
├── Outbound Strategist → signal taxonomy from the won-deal history: which events preceded purchase,
│   at what lead time, from which source; channel plan per signal class
├── Content Creator → proof assets and outbound copy built on the language of closed-won calls
├── Legal Compliance Checker → executes the signed determination per jurisdiction: jurisdiction map
│   loaded from it, suppression list loaded, opt-out path and record retention defined, content
│   rules for sequences written down
├── Sales Coach → coaching cadence against the draft stage criteria; rep briefing on the call standard
└── Quality Gate (G1): the ICP is derived from a named closed-won cohort, and every mandatory
    criterion is checkable from a public source in under five minutes (Offer & Lead Gen Strategist);
    each of the four quarters reconciles won plus lost plus open to the CRM count with no unexplained
    row, and every stage carries a numeric exit criterion that replaces one named inconsistency
    (Pipeline Analyst); the minimum deal size is the ACV derived from that reconstruction, recorded with
    its derivation, not the $25k/$10k default (Deal Strategist). A missing quarter, an ICP criterion
    nobody can check, a threshold still running on its default, or a stage whose exit is a feeling
    fails the gate.
```

```text
├── Outbound Strategist → two sequences per signal class, each with a volume ceiling, a stop rule,
│   and a disqualification branch that ends the sequence instead of chasing
├── Content Creator → message variants keyed to signal and persona; one proof asset per claim made
├── Legal Compliance Checker → line-by-line sequence review against the signed determination: every
│   sequence's target jurisdictions must appear in it, suppression test on a seeded contact, opt-out
│   path inside the opt-out window, unsubscribe and retention handling
├── Pipeline Analyst → baseline pack: stage conversion, cycle time, win rate and pipeline coverage,
│   each on a stated four-quarter denominator
├── Analytics Reporter → dashboard for the baseline pack and the gate record
├── Sales Coach → call standard in writing: discovery before demo, briefed to every rep
└── Quality Gate (G2): every sequence targets only jurisdictions covered by a signed lawful-basis
    determination, carries that determination's reference, a jurisdiction rule, a volume ceiling, and a
    suppression check that removes a seeded suppressed contact (Legal Compliance Checker); every
    baseline metric is computed on a stated denominator over four quarters (Pipeline Analyst); every
    sequence terminates when its disqualification branch fires (Outbound Strategist). A sequence that
    reaches a jurisdiction outside the signed set, or a metric with no denominator, fails the gate.
```

## Week 3-4: Outbound & Discovery

```text
├── Agents Orchestrator → releases one segment at a time, and only on a G2 pass
├── Outbound Strategist → runs the sequences, holds the volume ceiling, retires a step that produces
│   no reply across a full send cycle rather than rewriting it mid-cycle
├── Sales Coach → weekly coaching on recorded discovery calls against the call standard
├── Discovery Coach → question bank per segment, current-state map, gap quantification, and the
│   disqualifying question asked inside the first call, not after the demo
├── Deal Strategist → qualification score per open deal, stakeholder map, risk list
├── Sales Engineer → technical discovery after a Stage 3 exit; demo assembled from the discovery
│   record; POC scoped with written entry and exit criteria
├── Pipeline Analyst → stage audit: the Stage-criteria audit sample scored criterion by criterion,
│   rep-verified
├── Legal Compliance Checker → live sequence audit: every send checked against the signed
│   determination, opt-outs honored inside the opt-out window, suppression re-checked against the
│   current list and reflected in the send list within 1 hour
└── Quality Gate (G3): zero messages sent to a contact in a jurisdiction outside a signed lawful-basis
    determination — the send set is a subset of the signed set, so one send touching an unsigned
    jurisdiction fails the gate and stops that sequence; zero sends to a contact that has not passed a
    suppression check (Legal Compliance Checker with Outbound Strategist); every opt-out honored inside
    the opt-out window — automated sends suppressed within 24 hours of receipt, manual sends suppressed
    before the next send, the send list refreshed from the suppression list within 1 hour; zero outbound
    contacts on an account with no qualifying signal in the trailing 90 days (Signal threshold); zero
    sequences running above their volume ceiling or past a fired stop rule (Agents Orchestrator). Any
    one of those failures stops the sequence, not the audit.
```

```text
├── Discovery Coach → every open deal at Stage 3 or later carries a record with current state,
│   quantified gap, named authority and buyer-stated timeline
├── Deal Strategist → deals missing authority or a dated compelling event close as Closed-Lost with a
│   coded reason inside 5 business days
├── Sales Engineer → demo review: each demo segment traced to a discovery answer, unasked features cut
├── Proposal Strategist → proposal skeleton and win themes prepared from discovery records only
├── Sales Coach → stage-move co-sign review, with a deviation log and a reason per move
├── Pipeline Analyst → audit result: pass or fail per criterion, pass rate by rep and by stage
└── Quality Gate (G4): the Stage-criteria audit sample scores every exit criterion pass or fail from
    the call record, and the pass rate is stated by rep and by stage (Pipeline Analyst); zero deals
    past the disqualification rule are still open, and every disqualified deal closed inside 5 business
    days with a coded reason (Deal Strategist); zero demos were delivered before a Stage 3 exit (Sales
    Engineer). A stage exit nobody can audit fails the gate, and so does an audit run on any set other
    than the one the Thresholds row defines.
```

## Week 5-6: Proposals, Forecast & Proof

```text
├── Proposal Strategist → one proposal per Stage 4 exit, every section traced to a discovery answer,
│   the executive summary in the buyer's words, no feature list nobody asked for
├── Deal Strategist → discount position inside authority; exception log with reason and approver
├── Pipeline Analyst → forecast model on stage, age and exit evidence, backtested against the four
│   closed quarters with the error reported per quarter before it touches live pipeline
├── Sales Coach → forecast review: each commit defended deal by deal, unsupported commits demoted
│   a category with the reason recorded
├── Analytics Reporter → forecast-vs-closed reconciliation per category, coverage and conversion view
├── Account Strategist → handoff for every closed-won account: stakeholder map, expansion plan,
│   net revenue retention baseline recorded
├── Legal Compliance Checker → sequence records closed out, suppression retained, retention window held
├── Reality Checker → verdict on the packaged evidence: stage audit, backtest, commit traceability
└── Quality Gate (G5): the backtested error on the four closed quarters is inside the forecast accuracy
    tolerance and every commit traces to the Stage 5 to Commit criteria (Pipeline Analyst); every
    proposal in the period traces to a Stage 3 exit and a discovery answer (Proposal Strategist); every
    committed deal carries a written mutual action plan with a signature date (Deal Strategist); the
    Reality Checker's verdict is attached, and NEEDS WORK blocks release. A forecast that cannot be
    reconciled against closed quarters fails the gate, and no number leaves the run.
```

## Key Decisions

| Decision Point | When | Who Decides |
| --- | --- | --- |
| Which segments to serve, and which to decline in writing | Week 2, gate G1 | Offer & Lead Gen Strategist with Pipeline Analyst; the forecast owner signs |
| Which jurisdictions are in the send set, and on what legal basis | Before any send, re-checked at gate G3 | Named counsel or DPO signs the determination; the Legal Compliance Checker executes it, may withdraw a sequence, and may never add a jurisdiction to the send set |
| Whether a POC is offered, and on what terms | Week 4 | Sales Engineer with Deal Strategist: offered only after a Stage 3 exit, with a named success criterion, a written exit date, and a buyer-side owner; never as a substitute for discovery |
| Discount authority, and what buys a concession | Week 4-5 | Deal Strategist inside the threshold; anything above goes to the named owner of the number |
| What gets disqualified, and when | Defined Week 2, applied Week 3-4 | Pipeline Analyst defines the hard disqualifiers; Discovery Coach applies them inside the call |
| Who may move a deal stage | Week 3-4 | Sales Coach: reps move 2 to 3; 3 to 4 and 4 to 5 require a co-sign; only the forecast owner commits |
| How a deal enters the forecast, and what demotes it | Week 5 | Pipeline Analyst model; Sales Coach review; the forecast owner commits |

## Success Criteria

What the run produces and can observe at close-out. A target measured on a quarter that has not happened yet is not a success criterion; the quarterly-scale outcomes live in Post-runbook, where the owner and the read date are fixed.

| Metric | Target |
| --- | --- |
| M1 Stage-criteria audit pass rate | 90% or better of the exit criteria in the Stage-criteria audit sample hold from the call record, stated per rep and per stage; every failing criterion carries a named owner and a fix date inside the run |
| M2 Disqualification cycle time | Median 5 business days or less from a hard disqualifier appearing to Closed-Lost with a coded reason; zero disqualified deals left open at close-out |
| M3 Forecast backtest error | The model's error on each of the four closed quarters is inside the forecast accuracy tolerance — at most 10% at commit, at most 25% at best case — reported per quarter, before the model touches live pipeline |
| M4 Win rate | 25% or better of Stage 3-qualified opportunities, on the qualified-only denominator, reported with the opportunity count behind it |
| M5 Outbound legal-basis coverage | 100% of outbound contacts sit inside a signed lawful-basis determination and carry a passed suppression check; 0 sends into an unsigned jurisdiction |

## Common Pitfalls

| Pitfall | Mitigation |
| --- | --- |
| A forecast built from rep optimism, with no evidence behind the commit | Commits require the Stage 5 to Commit criteria, the Sales Coach review, and a model whose backtested error is inside tolerance (M3, G5) |
| Demos delivered before discovery, so the call sells features nobody asked about | Zero demos before a Stage 3 exit, and every demo segment traced to a discovery answer (G4) |
| Proposals that answer questions the buyer never asked, written the night before | Every proposal section traces to a Stage 3 exit and a discovery answer; a proposal without that record is not issued (G5) |
| A purchased list treated as consent | Only a signed lawful-basis determination makes a send lawful, and the Legal Compliance Checker executes it against the suppression list; a vendor's claim of compliance is not documentation, and no roster agent may sign the determination (G3, M5) |
| Stage definitions no two people apply the same way | Numeric exit criteria in Thresholds, the criterion-by-criterion audit on the defined sample, and the pass rate stated by rep and stage (G4, M1) |
| Disqualification treated as failure rather than capacity recovered | Disqualified deals carry a coded reason and close in 5 business days; coaching measures disqualification rate and the time returned to the segment, not only win rate (M2, M4) |

## Post-runbook

Beyond the run, the owner and the measurement point are fixed now, so the engine is judged rather than assumed. The four outcomes a 4-6 week run cannot observe — cohort conversion, cycle time, forecast accuracy across two quarters, and coverage at quarter start — are read here, at the named quarter close, and never asserted at close-out.

| Metric | Owner | Measured on |
| --- | --- | --- |
| Stage conversion, one quarter's cohort: 2 to 3 at 50% or better, 3 to 4 at 60% or better, 4 to closed-won at 25% or better, zero stages outside [baseline ÷ 1.5, baseline × 1.5] where the baseline is the Week 1 four-quarter pack | Pipeline Analyst | Each quarter close, first read at the second quarter close after close-out — a 45-day cycle has to complete first |
| Cycle time: median Stage 2 to closed-won at 45 days or less, no stage dwell above 2x its own median without a written reason | Pipeline Analyst | The first quarter close after close-out, then each quarter close |
| Forecast accuracy: committed forecast within 10% of closed-won for two consecutive quarters, reported per quarter | Pipeline Analyst | Two consecutive quarter closes, starting at the first quarter close after close-out |
| Pipeline coverage: 3.0x to 4.5x the next-quarter target in qualified pipeline at quarter start | Analytics Reporter | Each quarter start after close-out |
| Net revenue retention | Account Strategist | Trailing twelve months, closed at the second full quarter after close-out |
| Expansion revenue from accounts closed during the run | Account Strategist | Quarter after close-out, then rolling per quarter |
| Win rate trend by segment | Pipeline Analyst | Four-quarter rolling, reviewed at each quarter close |
| Forecast accuracy trend, commit and best case separately | Pipeline Analyst | Each quarter close for four quarters |
