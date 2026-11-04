# Runbook: Paid Media Launch & Spend Governance

Mode: NEXUS-Sprint | Duration: 3-4 weeks | Agents: 17

## Scenario

A budget is approved and the temptation is to spend today. Tracking is half-installed: the tag fires on page view, not on purchase, and nothing stands between the visitor and the pixel but hope. Search terms are guesses copied from a competitor. Creative is one generic asset across every placement. Nobody can price a qualified lead until the invoice arrives.

This runbook designs the account so spend lands on intent, proves consent and measurement before a dollar moves, and holds spend to a finance-signed target. Doctrine: **spend is only an experiment when measurement is already trusted, and consent is what makes the measurement legal.** Impressions are not results; platform conversions are not revenue; an unregistered target is not a target.

## Applicability

| Use this runbook when | Use a different runbook when |
| --- | --- |
| Money is spent on impressions, clicks, installs | Reach and brand — `marketing-campaign` |
| A CAC or ROAS number already has a name and a currency | Earned visibility — `seo-and-ai-search-visibility` |
| Tracking and consent are unproven and spend is imminent | Product experiments with no media spend — `startup-mvp` |
| A new account or platform needs design | One feature, healthy product — `enterprise-feature` |
| Existing spend needs an audit baseline | Whole-portfolio replan — `digital-transformation-program` |

## Required Inputs

Only what the roster cannot produce. Everything else is a gate output, not a precondition.

| Input | Why it blocks | Owner |
| --- | --- | --- |
| Budget envelope, one currency, approved | No agent may approve the money it spends | Budget owner |
| The CAC and ROAS the business commits to inside that envelope | The register records a commitment; it never invents one | Budget owner |
| Platform, tag manager, analytics and CRM access with publish rights | Provisioning is an account-owner act, not an agent act | Platform admin |
| A live landing page and offer for the primary intent | An ad cannot rescue a page that does not convert | Product marketing owner |
| Target markets and the data-processing agreements in force per market | An agent cannot sign a DPA or create a lawful basis | Legal counsel |
| A named accountable human for two signatures | Self-approval is not approval | Executive sponsor |

## Agent Roster

### Command (Always Active)

| Agent | Role |
| --- | --- |
| Agents Orchestrator | Owners, gates, and the sole authority to release spend |
| Finance Tracker | Register of targets, pacing, CAC/ROAS math, stop rules |

### Account Design (Always Active)

| Agent | Role |
| --- | --- |
| PPC Campaign Strategist | Intent-based taxonomy, bid strategy, budget arithmetic |
| Paid Social Strategist | Audiences, placements, frequency caps, exclusions |
| Programmatic & Display Buyer | Inventory, viewability floor, safety blocklist |
| Growth Hacker | Qualification definition, offer and page tests |

### Creative (Phase 2)

| Agent | Role |
| --- | --- |
| Ad Creative Strategist | Hooks, asset matrix, format-per-audience hypotheses |
| Brand Guardian | Brand consistency only: tone, lockup, hierarchy |
| Content Creator | Placement-native assets, landing-page message match |

### Measurement Gate (Phase 2, Blocking)

| Agent | Role |
| --- | --- |
| Tracking & Measurement Specialist | Verified event, deduplication key, attribution windows |
| Analytics Reporter | Dashboard live pre-launch; blended CAC on closed cohorts |
| Evidence Collector | Captured proof: event, consent state, pre-launch traffic |

### Compliance & Consent (Phase 2, Blocking)

| Agent | Role |
| --- | --- |
| Legal Compliance Checker | Claims, disclosures, restricted categories, legal basis — prepares, never signs |
| Privacy Engineer | Consent mode implementation and verification in the tag container |

### Optimization (Phase 3+)

| Agent | Role |
| --- | --- |
| Paid Media Auditor | Placement, geo, device, account structure, waste ledger |
| Search Query Analyst | Terms, negatives, match types, threshold breaches |

### Verdict (Phase 4)

| Agent | Role |
| --- | --- |
| Reality Checker | Closed-cohort verdict on the registered target (default: NEEDS WORK) |

## Phase 1: Account Design and the Register

```text
Days 1-4
├── Agents Orchestrator → assigns an owner per gate, opens the register, holds all
│   spend authority until Phase 3
├── PPC Campaign Strategist → structure by intent, not product catalog; match-type
│   policy, bid strategy, budget split arithmetic
├── Paid Social Strategist → cold, lookalike, retargeting, exclusions, frequency cap
├── Programmatic & Display Buyer → inventory, safety blocklist, viewability floor
├── Growth Hacker → qualification definition: what an outcome must do to count
├── Finance Tracker → register five numbers, each with a named owner and a source:
│   monthly budget, CAC target, ROAS floor, query spend threshold (per query, per
│   reporting period), viewability floor (number plus measurement definition, e.g.
│   share of impressions with 50%+ pixels visible for 1s)
└── Quality Gate: the register holds all five numbers or the runbook stops here.
    No default is substituted for a missing value, and a campaign that maps to no
    named intent, no landing page, or no share of the registered budget is deleted.
```

## Phase 2: Creative, Measurement and Consent

Two blocking gates, in this order. Nothing here is optional and nothing here is self-approved.

```text
Days 4-9
├── Ad Creative Strategist → minimum 3 hooks × 2 formats per audience
├── Content Creator → placement-native sizes, landing-page message match
├── Brand Guardian → brand consistency: tone, lockup, visual hierarchy. Holds no
│   legal authority and approves no claim
├── Legal Compliance Checker → claims, substantiation, disclosures and
│   restricted-category policy per market; assembles the claim file and the legal
│   basis for a human signature — never signs, never publishes
├── Privacy Engineer → consent mode configured in the container, consent state
│   mapped per region, no marketing tag firing ahead of consent
├── Tracking & Measurement Specialist → one real conversion in the platform's own
│   debugger, deduplication key written down, attribution window declared
├── Analytics Reporter → dashboard live, blended CAC defined on closed cohorts
├── Evidence Collector → captures: verified event and payload, consent-declined
│   network log, consent-accepted network log, claim file as approved
├── Agents Orchestrator → reads both gates; spend stays at zero until both PASS
├── Quality Gate — Measurement Gate (blocking): a real purchase or lead produced on
│   the live container appears exactly once in the platform debugger, its payload is
│   captured, the deduplication key is written in the register, and the primary
│   attribution window plus the secondary window are declared per platform
└── Quality Gate — Compliance & Consent Gate (blocking): a consent-declined session
    fires zero marketing tags in the captured network log while a consent-accepted
    session fires exactly the expected set; consent state is mapped per region; each
    region's legal basis is recorded with its named approver; and the production
    container publish carries a named human signature. The Privacy Engineer
    implements, the Legal Compliance Checker prepares — neither signs, and neither
    approves the other's work
```

## Phase 3: Launch and Optimization

```text
Days 10-21
├── Agents Orchestrator → releases the capped launch fraction, then every increase:
│   the only agent permitted to release spend, and the only one who can pause it back
├── PPC Campaign Strategist → days 10-13 are data collection, zero edits
├── Search Query Analyst → owns terms: day-10 term pull, negatives, match types;
│   logs every query above the registered spend threshold as a written decision
├── Paid Media Auditor → owns placement, geo, device and account structure; pauses
│   any placement under the registered viewability floor
├── Paid Social Strategist → rotates creative, pauses sub-floor assets, holds exclusions
├── Ad Creative Strategist → new assets built on the winning hook only
├── Analytics Reporter → weekly read on closed 7-day cohorts, spend to the owner
├── Finance Tracker → pacing against the registered budget and CAC, stop rules
└── Quality Gate: from the same Phase 1 register — zero queries above the registered
    spend threshold without a logged decision, zero placements below the registered
    viewability floor still serving after day 13, waste under 10% of spend, and the
    day-21 account unchanged in bids, budgets and structure
```

### Stop Rules

| Stop rule | Signal | Who flips it | Effect |
| --- | --- | --- | --- |
| No conversions | 500 clicks or 2× target CAC, zero conversions | Finance Tracker → Agents Orchestrator | Pause; re-verify event and consent |
| Cost drift | CAC 25% above target for 3 days | Finance Tracker → Agents Orchestrator | Cut budget to the best ad groups |
| Disapproval | Any policy warning | PPC Campaign Strategist | Fix or pull the asset; legal reviews the claim |
| Tracking breaks | Conversions drop 50%, clicks hold | Tracking & Measurement Specialist → Agents Orchestrator | Pause 4 hours; re-verify event |
| Consent breaks | Any marketing tag in a declined-consent session | Privacy Engineer → Agents Orchestrator | Pause all tags until the gate re-reads PASS |
| Waste drift | 15%+ of spend on irrelevant queries | Search Query Analyst → Agents Orchestrator | Add negatives, cap budget |

## Phase 4: Closed-Cohort Verdict

```text
Days 21-28
├── Agents Orchestrator → freezes bids, budgets and structure: seven days of no change
├── Finance Tracker → closes the cohort ledger: states the cut-off date, includes
│   only cohorts whose registered attribution window has fully elapsed, lists every
│   open cohort separately and excludes it from every ratio
├── Paid Media Auditor → waste ledger per placement, geo and device, re-checking the
│   viewability floor and the query spend threshold against Phase 1
├── Search Query Analyst → negative library, match-type playbook, unresolved queries
├── Analytics Reporter → blended and platform views reconciled on the same cut-off
├── Growth Hacker → next experiment ranked by cost per qualified outcome
├── Reality Checker → verdict on the registered target, closed cohorts only
└── Quality Gate: the verdict states cut-off date, registered target, achieved number
    and difference in one line, computed only on cohorts whose window has elapsed;
    any cohort still inside its window is named as open with its close date
```

Schedule arithmetic: 4 days of design, 5 days of gated build, launch on day 10, 72 hours of collection, optimization to day 21, then a 7-day frozen read to day 28. Every cohort launched by day 21 closes its 7-day window by day 28, so the verdict can compare them. If the registered primary window is 30 days, no cohort has closed by day 28: the verdict then names the cut-off, reports the 7-day cohorts, and labels every 30-day figure as open — never as final CAC.

## Key Decisions

| Decision Point | When | Who Decides |
| --- | --- | --- |
| Budget split across platforms | Phase 1 | PPC Campaign Strategist + Finance Tracker |
| Bid strategy and its floor | Phase 1 | PPC Campaign Strategist |
| The five registered numbers, ROAS floor included | Phase 1 | Finance Tracker records, Agents Orchestrator accepts |
| Which claims may run, and their substantiation | Phase 2 | Legal Compliance Checker prepares; named human signs |
| Consent behaviour per region and its legal basis | Phase 2 | Privacy Engineer + Legal Compliance Checker; human signs |
| Publishing the production container | Phase 2 | Privacy Engineer implements; named human approves |
| Whether an asset survives 1,000 impressions | Phase 3 | Ad Creative Strategist + Paid Media Auditor |
| Whether spend moves between platforms | Phase 3 | Paid Social Strategist + Finance Tracker propose; Agents Orchestrator releases |
| How aggressive to get with negatives | Phase 3 | Search Query Analyst |
| Scale, hold or stop on closed cohorts | Phase 4 | Finance Tracker + Reality Checker |

## Success Criteria

| Metric | Target |
| --- | --- |
| Blended CAC | At or below the finance-registered target on closed cohorts only, at the stated cut-off, to the cent; open cohorts listed, never blended in |
| ROAS | At or above the finance-registered floor. No default exists: an unregistered floor stops the runbook in Phase 1 |
| Marketing tags in a consent-declined session | 0, on a captured network log |
| Production container publish | 1 named human approval; 0 agent self-approvals |
| Queries above the registered spend threshold without a logged decision | 0, verified in Phase 3 and again in the waste ledger |
| Live placements below the registered viewability floor | 0 after day 13 |
| Wasted spend on irrelevant queries | Under 10% of spend, per the auditor's ledger |
| Conversion-tracking coverage | 100% of live actions debugger-verified before the first dollar |
| Share of budget on winning ad groups | 70%+ at or below target CAC by day 21 |
| Duplicate or inflated conversions | 0, proven on a deduplicated test event |
| Spend before measurement and consent were verified | 0 days |
| Verdict evidence base | 100% closed cohorts; every open cohort named with its close date |

## Roster Traceability

| Agent | Fails on |
| --- | --- |
| Agents Orchestrator | Phase 1 register gate; Phase 3 gate (day-21 freeze); Success Criteria: spend before verification, 0 days |
| Finance Tracker | Phase 1 five-number register gate; Success Criteria: blended CAC on closed cohorts |
| PPC Campaign Strategist | Phase 1 intent/landing-page/budget gate; Phase 3 day-21 freeze |
| Paid Social Strategist | Phase 1 audience and exclusion gate; Phase 3 sub-floor pause |
| Programmatic & Display Buyer | Phase 1 viewability floor in the register; Phase 3 zero sub-floor placements |
| Growth Hacker | Phase 1 qualification definition that the CAC denominator depends on |
| Ad Creative Strategist | Phase 2 3 hooks × 2 formats gate; Phase 3 sub-floor creative pause |
| Brand Guardian | Phase 2 brand consistency line; holds no claim authority |
| Content Creator | Phase 2 placement-native sizes and message match |
| Tracking & Measurement Specialist | Measurement Gate: exactly one event, deduplication key, window declared |
| Analytics Reporter | Measurement Gate: dashboard live; Phase 4 same-cut-off reconciliation |
| Evidence Collector | Phase 2 captures: event payload and both consent network logs |
| Legal Compliance Checker | Compliance & Consent Gate: legal basis recorded with a named approver |
| Privacy Engineer | Compliance & Consent Gate: zero tags in a declined-consent session |
| Paid Media Auditor | Phase 3 audit gate; Phase 4 waste ledger re-checking both numbers |
| Search Query Analyst | Phase 3 threshold-breaches gate; Success Criteria: 0 undecided queries |
| Reality Checker | Phase 4 closed-cohort verdict gate |

## Common Pitfalls

| Pitfall | Mitigation |
| --- | --- |
| Tags firing before consent because "the banner is a front-end task" | Consent is a Phase 2 blocking gate with a captured declined-consent log |
| A design agent signing off legal claims | Legal prepares and a named human signs; the Brand Guardian owns brand only |
| Last-click launch optimizing the wrong event | Declare the primary window in Phase 2; report blended CAC, platform views as diagnostic |
| Calling CAC final while 30-day conversions are still landing | Verdict on closed cohorts, cut-off stated, open cohorts named |
| Duplicate conversions inflating results | One deduplicated event per action, proven on a test |
| One creative across every placement | Placement-native ratios; stretched squares waste impressions |
| No negative keyword list until week 3 | Pull search terms on day 10, add negatives weekly |
| Spending to hit budget, not the cost target | Pace to targeted CAC; unspent budget is a valid outcome |
| Reporting platform numbers as revenue | Reconcile against the analytics or CRM source first |
| Borrowing a "standard" ROAS floor when finance never gave one | No registered floor, no launch — the register is the contract |
