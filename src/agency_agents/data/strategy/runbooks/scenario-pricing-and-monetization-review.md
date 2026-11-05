# Runbook: Pricing & Monetization Review

> **Mode**: NEXUS-Sprint | **Duration**: 3 weeks | **Agents**: 15

## Scenario

Pricing was set once, by whoever was in the room, and has not been revisited since. The real price is whatever a rep conceded at quarter end. Discounts are negotiated case by case, packaging no longer matches usage, and nobody knows whether the last change helped or hurt.

This runbook turns pricing into a decision with evidence, a migration path, and a billing change proven in test mode before anyone is charged. Three weeks buy the evidence and the proof, not the outcome: anything that needs a billing quarter to observe is measured after the runbook, by the owner named below.

**Non-negotiable gate**: no price change is announced until the Payments & Billing Engineer has shown the new price, proration both directions, mid-cycle change, tax, invoice rendering and the credit-note path working in test mode, until every segment has a written migration path, and until the named human in the written mandate has approved list price, packaging and discount policy. The release is two steps and neither belongs to an agent alone: the Payments & Billing Engineer proves the change in test mode, then the Agents Orchestrator declares it shippable on that evidence — never before the human's approval is recorded by name, authority basis and date. An agent may not declare a price change shippable on its own.

## Applicability

| Use this runbook when | Use a different runbook when |
| --- | --- |
| The question is what to charge and how to package it | Reporting the result — use `monthly-close-and-financial-reporting` |
| Discounts are granted case by case with no ceiling | Testing one offer — use `growth-experiment-loop` |
| Packaging no longer matches observed usage | Shipping the priced product — use `enterprise-feature` |
| A change must reach existing customers without breaking invoicing | The platform cannot meter the metric — fix metering first |

Decision rule for the boundary: if the question changes what is charged, this runbook owns it; if it only reports what was earned, tests one offer, or ships a capability, the row above sends it out — and a dispute about which applies is settled by the named human approver in the mandate, not by the agent that benefits from the wider reading.

## Required Inputs

Raw sources only. Everything this runbook produces — the reconstructed ledger, the margin model, the tier recommendation, the migration path, the test-mode evidence, the verdict — is an output, and an output listed as a blocking input would make the runbook its own prerequisite.

| Input | Why it blocks | Owner |
| --- | --- | --- |
| Invoice and contract export for the last four quarters, at invoice-line level | Realized price is reconstructed from lines; a summary hides the concessions | Financial Analyst |
| Raw metered usage per account: seats, events, storage, API calls, as counted by the platform | Packaging that contradicts usage sells an allowance nobody consumes | Financial Analyst |
| Unit cost inputs: vendor bills, infrastructure spend, support cost per ticket | A margin floor needs an unmeasured cost before it needs a price | FP&A Analyst |
| Unanalyzed win/loss notes and CRM close reasons for four quarters | Coding them is Week 1 work; notes arriving pre-judged import the bias | Pipeline Analyst |
| Renewal calendar: contract end dates, notice windows, auto-renew terms | A notice-window miss is a contract-variation question, not a scheduling detail, and the runbook cannot answer it on its own | Account Strategist |
| Executed agreements and contract templates for accounts renewing within twelve months | The variation mechanism differs per contract family; counsel reads the paper, and a summary of it is the thing being questioned | Account Strategist |
| Billing platform limits as tested facts: what it can meter, prorate, tax, invoice today | An inexpressible model becomes a renewal spreadsheet | Payments & Billing Engineer |
| Written mandate naming who may approve list price, packaging and discount policy, and on what authority | Asking permission at announcement time is a memo, and an approval with no authority basis is an anecdote | Executive Summary Generator |

## Agent Roster

Traceability column: `G1`–`G3` are the weekly Quality Gates, `S1`–`S12` the in-runbook Success Criteria, `P1`–`P5` the post-runbook measures.

### Command (Always Active)

| Agent | Role | Traceable to |
| --- | --- | --- |
| Agents Orchestrator | Gatekeeper: holds the billing gate, sequences handoffs, releases the price change only after the named human's recorded approval | G3, S9 |
| Finance Tracker | Cash and collected view, countersigns realized revenue, keeps the figure-to-source ledger | G1, S2, S8 |

### Analysis (Week 1)

| Agent | Role | Traceable to |
| --- | --- | --- |
| Pricing Analyst | Value metric, structure modeling, discount economics | G2, S1, S12 |
| FP&A Analyst | Unit cost, margin floor per segment, volume sensitivity | G1, G2, S1, P3 |
| Financial Analyst | Realized-vs-list reconstruction, usage extraction, reconciliation | G1, S2 |
| Trend Researcher | Competitor list price and metering basis, labeled as context | G2 |
### Market & Deal Reality (Week 2)

| Agent | Role | Traceable to |
| --- | --- | --- |
| Deal Strategist | Discount ceiling, concession rules, migration terms, grandfathering | G2, G3, S1, S5, S7 |
| Pipeline Analyst | Win/loss coding, price sensitivity, deal-size effects | G1, P2 |
| Account Strategist | Expansion whitespace and renewals exposure to the new price | G3, S6, P1, P4 |
| Product Manager | Tier boundaries, feature placement, metered vs unlimited | G1, G2 |

### Implementation (Week 3)

| Agent | Role | Traceable to |
| --- | --- | --- |
| Payments & Billing Engineer | Test-mode price, proration, tax, grandfathering, invoice render | G3, S4 |
| Feedback Synthesizer | Buyer-language test of the value metric and the bill estimate | G2, S3 |

### Decision (Week 3)

| Agent | Role | Traceable to |
| --- | --- | --- |
| Executive Summary Generator | Records the decision the named human approves: terms, approver, authority basis, owner, effective date, measurement date; never decides | G3, S8 |
| Profit First Strategist | Credit-note and cash-collection behaviour per segment, plus the model gap on the current price | G3, S11, P5 |
| Reality Checker | Final verdict on the packaged evidence, NEEDS WORK by default | G3, S10 |

## Thresholds

Every number a gate cites is defined here once. An undefined number in a gate is an unfailable criterion.

| Threshold | Definition | Default value | Owner |
| --- | --- | --- | --- |
| Segment taxonomy | The `segment` field carried by every account, invoice line and usage row. Allowed values: `self-serve`, `mid-market`, `enterprise`, derived from contracted seat count and support tier and assigned before Week 1 work starts. An account with an empty value is reported as `unsegmented` and fails G1 | Three values; zero unsegmented accounts | FP&A Analyst |
| Discount ceiling | Largest discount off list a tier may grant without an exception record. The human-approved discount policy governs; this row is the pre-approval default and is superseded the moment the policy states a number. An agent that grants above either value needs a recorded exception carrying account, reason and approver | 15% single-year, 25% multi-year commitment, pending the approved policy; anything above needs FP&A counter-signature and is logged with account, reason, approver | Deal Strategist + FP&A Analyst |
| Margin floor | Realized gross margin below which a deal is declined, not escalated; margin = (realized price − unit cost) / realized price | Self-serve 75%, mid-market 65%, enterprise 55% | FP&A Analyst |
| Tier boundaries | Boundaries on the chosen value metric, at the observed 60th and 90th percentile of paid usage per segment, minimum 3x between boundaries; a boundary falling within 10% of an existing contract size moves to the next gap | Two boundaries, three tiers | Product Manager + Pricing Analyst |
| Volume tolerance | Swing the structures are modeled against | ±20% around current volume | Pricing Analyst |
| Estimate tolerance | How far a buyer's unaided bill estimate may sit from the computed bill | ±15% | Feedback Synthesizer |
| Reconciliation tolerance | Largest unexplained difference accepted in the reconstructed quarter | ≤1% of invoiced revenue | Financial Analyst + Finance Tracker |
| Model gap tolerance | Gap between the modeled margin and the margin produced by re-running the current price through the new model, per segment — the only margin gap observable before a single invoice exists at the new price | ≤2 points per segment | Profit First Strategist |
| Realization tolerance | Post-runbook: gap between modeled margin and cash-received margin after credits, discounts and payment terms, measured on a full quarter billed at the new price (P5) | ≤2 points per segment | Profit First Strategist |

## Week 1: Evidence & Segmentation

```text
├── Financial Analyst → list vs invoiced price per account; every exception by reason, tier, approver
├── Financial Analyst → consumed vs paid units per segment, ratio per account
├── FP&A Analyst → unit cost and gross margin per unit, per segment, from vendor bills
├── Finance Tracker → invoiced vs collected vs credited per account, cash view
├── Pipeline Analyst → four quarters of close reasons coded, contract value attached
├── Trend Researcher → competitor list price and metering basis, each labeled as context
├── Product Manager → tier bought vs features used, per segment
└── Quality Gate G1: each segment shows volume, realized price and margin per unit (FP&A Analyst),
    win rate and the top three coded loss reasons (Pipeline Analyst); the reconstructed quarter's
    unexplained difference is ≤1% of invoiced revenue, per Reconciliation tolerance (Financial
    Analyst + Finance Tracker); every discount exception carries a reason and an approver
    (Deal Strategist). Any segment missing a row fails the gate. An account whose `segment` field
    is empty is counted under `unsegmented` per the segment taxonomy, reported separately, and
    fails the gate.
```

## Week 2: Model & Packaging

| Model | Right when | Failure mode |
| --- | --- | --- |
| Per seat | Value scales with headcount; seats countable | Seat hoarding: shared logins cut the bill, not usage |
| Usage-based | Consumption tracks value; customer controls it | Unpredictable revenue; one bad integration bills a customer into churn |
| Tiered | Segments differ visibly; a feature boundary exists | Middle-tier squeeze: everyone buys below, the top tier becomes a demo |
| Hybrid (fee + allowance + overage) | Base value in access, variable cost above it | Allowance copied from a competitor page, so overage arrives as a surprise |

```text
├── Pricing Analyst → value metric that scales with value and is predictable pre-signature
├── Pricing Analyst → three structures modeled against the Week 1 ledger at ±20% volume
├── FP&A Analyst → margin floor per segment applied to the model; below floor is a decline
├── Deal Strategist → discount matrix: ceiling and floor per tier, what buys a concession
├── Product Manager → tier contents and the boundary each tier sits on, cost of moving a feature
├── Trend Researcher → competitor position table, each row marked as context with its metering basis
├── Feedback Synthesizer → unaided buyer estimate of its own bill on ≥10 sampled accounts
└── Quality Gate G2: one recommendation and one rejected alternative with the losing factor named
    (Pricing Analyst); the recommendation clears the 75/65/55 margin floors at the ±20% volume
    swing (FP&A Analyst); every tier carries a numeric ceiling (the approved policy value, or the
    15%/25% default while no policy number exists) and a floor (75/65/55) (Deal Strategist); tier
    boundaries sit at the 60th and 90th percentile with ≥3x separation
    (Product Manager); the unaided bill estimate lands within ±15% on ≥10 accounts
    (Feedback Synthesizer); no competitor figure appears without its context label
    (Trend Researcher).
```

## Week 3: Migration & Billing Proof

```text
├── Payments & Billing Engineer → test mode: new price, proration both ways, mid-cycle change,
│   tax against the live tax table, invoice render, credit-note path — each with invoice ID
├── Payments & Billing Engineer → grandfathered accounts by ID, expiry, end-state price
├── Financial Analyst → recompute last quarter's invoices at the new price; explain every delta
│   above 1%
├── Account Strategist → renewals exposure: every account renewing within 6 months carries old
│   price, new price, delta, notice-window check and a renewal owner; expansion whitespace sized
├── Deal Strategist → migration path per segment: who moves, when, at what price, what is held
├── Profit First Strategist → credit-note and cash-collection behaviour per segment: credits raised
│   against the new price in test mode, collection timing against the stated terms, and the model
│   gap when the current price is re-run through the new model
├── Executive Summary Generator → decision record: terms, owner, effective date, measurement date,
│   and the named human's approval with name, authority basis and date — recorded, never decided
├── Reality Checker → verdict on the packaged evidence; NEEDS WORK unless the tests above are
│   attached and traceable
└── Quality Gate G3: zero invoice errors across one complete test-mode cycle, with proration,
    mid-cycle change, tax and the credit-note path each shown by rendered invoice ID
    (Payments & Billing Engineer); every grandfathered ID carries expiry and an end-state price
    and every segment carries a written migration path (Deal Strategist); every account renewing
    within 6 months carries a price and a renewal owner (Account Strategist); credit-note and
    cash-collection behaviour is recorded per segment and the current price, re-run through the new
    model, sits within 2 points of the modeled margin per segment per Model gap tolerance
    (Profit First Strategist); decision record signed with owner, effective date and measurement
    date (Executive Summary Generator); the named human in the written mandate has recorded
    approval of list price, packaging and discount policy, by name, authority basis and date
    (Executive Summary Generator records it; the human owns it); no announcement sent. Release is
    three-step and no step may be skipped: the Payments & Billing Engineer proves the change in
    test mode, the named human approves in writing, and only then may the Agents Orchestrator
    declare the price change shippable, by name and date. An agent may not release on modelling,
    on a test-mode pass, or on its own reading of the mandate. A verdict of NEEDS WORK from the
    Reality Checker blocks the release.
```

## Key Decisions

| Decision Point | When | Who Decides |
| --- | --- | --- |
| Metric of value the price is indexed to | Week 2 | Pricing Analyst + Product Manager |
| Reprice existing customers or hold them | Week 2 | Deal Strategist + FP&A Analyst, submitted inside the G3 approval package to the named human |
| Grandparenting terms and expiry | Week 3 | Deal Strategist + FP&A Analyst |
| Discount ceiling and what buys a concession | Week 2 | Deal Strategist + FP&A Analyst, inside the band the human-approved policy sets |
| Tier boundaries and what becomes metered | Week 2 | Product Manager + Pricing Analyst |
| Variation mechanism per contract family | Week 2, before migration terms are written | Named counsel; the answer is recorded as an input decision that G3 migration paths cite |
| Announcing a price change that touches renewals inside 6 months | Week 3 | Account Strategist + Deal Strategist schedule it; the named human approves the announcement at G3 |
| Approve list price, packaging and discount policy | Week 3, before the G3 release | The named human in the written mandate, with approval recorded by name, authority basis and date |
| Declaring the price change shippable | Week 3, gate G3, only after the human's recorded approval | Agents Orchestrator |
| Final readiness verdict | Week 3, gate G3 | Reality Checker; NEEDS WORK is the default |

## Success Criteria

In-runbook only: observable inside the three weeks. Anything that needs a billing quarter is measured in the post-runbook table below.

| Metric | Target | Owner |
| --- | --- | --- |
| S1 Discount matrix completeness | 100% of tiers carry a numeric ceiling and floor; zero tiers with an unset value | Deal Strategist + FP&A Analyst |
| S2 Ledger reconciliation | Unexplained difference ≤1% of invoiced revenue on the reconstructed quarter | Financial Analyst + Finance Tracker |
| S3 Bill predictability | Unaided buyer estimate within ±15% of the computed bill on ≥10 sampled accounts | Feedback Synthesizer |
| S4 Test-mode invoice errors | 0 across one complete test-mode cycle at the new price | Payments & Billing Engineer |
| S5 Grandfathered coverage | 100% of grandfathered IDs carry an expiry date and an end-state price | Deal Strategist |
| S6 Renewal exposure schedule | 100% of accounts renewing within 6 months carry old price, new price, delta, notice-window check, renewal owner | Account Strategist |
| S7 Migration coverage | 100% of segments carry a written path; zero segments with an open decision | Deal Strategist |
| S8 Decision traceability | 100% of figures tie to a source row; decision record names owner, effective date, measurement date and approver with authority basis and approval date | Finance Tracker + Executive Summary Generator |
| S9 Release decision | Recorded by the Agents Orchestrator by name and date, after the named human's recorded approval; zero announcements ahead of it | Agents Orchestrator |
| S10 Verdict | Reality Checker verdict issued; NEEDS WORK unless the test-mode and migration evidence is attached | Reality Checker |
| S11 Model gap on the current price | The current price re-run through the new model sits within 2 points of the modeled margin per segment, and credit-note and cash-collection behaviour is recorded per segment | Profit First Strategist |
| S12 Structure decision | Recommendation and rejected alternative both recorded with the losing factor named | Pricing Analyst |

## Post-runbook Measures

The window exceeds the three weeks; the owner and the measurement date are fixed now, so the change is still judged rather than assumed.

| Measure | Target | Window | Owner | Measurement date |
| --- | --- | --- | --- | --- |
| P1 Expansion revenue from existing accounts | ≥8% of base ARR | Two quarters | Account Strategist | Close of the second full quarter after the effective date |
| P2 Churn attributable to the reprice | ≤1 point above the trailing four-quarter baseline | One quarter | Pipeline Analyst | Close of the first full quarter after the effective date |
| P3 Gross margin by segment | At or above the modeled floor, within 3 points of the model | One quarter, then trend | FP&A Analyst | Close of the first full quarter after the effective date; recheck at 90 days |
| P4 Net revenue retention | ≥100% | One quarter | Account Strategist | Close of the first full quarter after the effective date |
| P5 Realization gap | Cash-received margin within 2 points of the modeled margin per segment, after credits, discounts and payment terms | One quarter billed at the new price, then recheck at 90 days | Profit First Strategist | Close of the first full quarter after the effective date; recheck at 90 days |

## Common Pitfalls

| Pitfall | Mitigation |
| --- | --- |
| Repricing from a competitor's public page instead of own usage data | Every price cites the Week 1 ledger; competitor rows carry a context label (G2) |
| A discount ceiling that exists only in a slide | Ceiling is numeric per tier in the matrix and every exception is logged (S1) |
| Grandfathering forever with no expiry, freezing the revenue base | Every grandfathered ID carries an expiry and an end-state price (S5) |
| Announcing because the model looks right | Announcement blocked until the Payments & Billing Engineer's test-mode evidence, the named human's recorded approval and the Agents Orchestrator's release record all exist (S9) |
| An agent treating the mandate as a formality and releasing on its own evidence | G3 fails without the human's approval recorded by name, authority basis and date; the orchestrator's release record is void without it (S9) |
| A ceiling overridden by habit because it shipped with a default value | The human-approved discount policy governs over the default; any grant above it needs a recorded exception row, and G2 fails on a tier without a numeric ceiling (S1) |
| Renewals inside the notice window discovered after the announcement | Renewal exposure schedule built in Week 3 by Account Strategist (S6); the variation mechanism per contract family is answered by named counsel in Week 2, before migration terms are written |
| Revenue up, margin down | Margin floor per segment is primary; a deal below floor is declined, not escalated |
| A usage metric customers cannot predict, producing dispute volume | Buyer estimate tested at ±15% before the structure is approved (S3) |
| Declaring success in week 3 | Expansion, churn, margin trend and the true realization gap are post-runbook measures with a named owner and date (P1–P5) |
