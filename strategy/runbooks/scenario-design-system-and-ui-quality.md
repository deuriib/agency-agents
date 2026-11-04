# Runbook: Design System & UI Quality

> **Mode**: NEXUS-Sprint | **Duration**: 4-6 weeks | **Agents**: 15

## Scenario

The product has screens, not a system. Every component is rebuilt per page: four buttons, six modals, three date pickers. Spacing and type come from whatever the last developer felt — `13px` here, `0.875rem` there, `margin-bottom: 17px` nobody can defend. Accessibility is discovered by users, not caught by the team. The interface reads as a template, not a product; nobody can name the canonical screen.

This runbook builds the system — tokens, components, docs — and installs the **quality gate that keeps new UI from drifting back into one-off screens**. A library without a gate gets bypassed.

Doctrine: **every component in the shipped set ships with a documented token source, an accessibility audit at the stated standard, and a screenshot set taken from the running product.** A component that exists only in Figma is not counted shipped; a component that exists only in code is not counted designed.

## Applicability

| Use this runbook when | Use a different runbook when |
| --- | --- |
| Product exists; the interface must become systematic | Still "what should we build" — use `design-sprint`, which decides but never ships |
| Screens diverge; none is canonical | Retrofit compliance — use `accessibility-remediation-sprint` |
| New UI arrives as one-offs | One feature into a healthy product — use `enterprise-feature` |

## Required Inputs

Only artifacts the roster cannot author. Items the roster produces (UI inventory, accessibility baseline, token set, scope ceiling, parity report) are phase outputs, not inputs.

| Input | Why it blocks | Owner (supplied from outside the roster) |
| --- | --- | --- |
| Brand source pack: approved logo files, licensed web type families, color values, voice notes | Without a source, Brand Guardian converts opinion into tokens and the system becomes a rival brand | Brand owner |
| Access: write on the design-system package, staging URL, design-tool edit seat, CI secret scope for visual-regression baselines | Gates are evaluated against the running product; no access, no observation | Engineering leadership |
| Legal and contractual accessibility obligations: mandated standard, jurisdiction, deadline | A stricter binding standard discovered mid-build voids finished audits | Legal counsel |
| Participant pool, signed consent, incentive budget for at least 5 user sessions | Without real participants, UX research collapses into simulation and the walkthrough role is duplicated | Product owner |
| Named library owner with merge authority over the component directory, plus an executive sponsor who can cut scope | Unowned libraries collect variants; scope ceilings get renegotiated by whoever complains | Product owner + engineering director |
| Up to three business-critical workflows the release will be judged by | Research tasks, copy priorities and research thresholds derive from them | Product owner |

## Scope Ceiling (Week 1 deliverable, gate G1.4)

One frontend developer migrates one frontend in this window; an uncapped "every screen" claim is a fiction.

| Item | Ceiling |
| --- | --- |
| Screens (templates) migrated and gated in this runbook | at most 10, named, with an owner each |
| Components in the shipped set | at most 20, named |
| Critical workflows under user research | at most 3 |

`Scope Ceiling v1.0` is written, dated and signed in Week 1 by Agents Orchestrator, Senior Project Manager and the Product owner. Everything outside it is a **dated follow-on wave** with its own ceiling; those screens stay frozen (no new usage of the old patterns, no new work). A ceiling change is a written amendment with a date and a re-signed signature — not a mid-sprint verbal expansion. Every gate below measures against the ceiling, never against the inventory.

## Gate Standards

Thresholds live here once; phase gates cite them.

### Accessibility standard and severity

Target standard: **WCAG 2.2 Level AA** — success criteria at Level A and Level AA — tested per component state and per template state. Where Required Inputs mandate a stricter regime (contractual AA-plus, EN 301 549, Section 508), the stricter regime applies and is named in the gate log. An automated scan alone does not satisfy a gate: the record must name the assistive technology and version used.

| Level | Mapping | Impact | Gate treatment |
| --- | --- | --- | --- |
| Critical | WCAG 2.2 Level A criterion; task blocked | User cannot complete the task | 0 open at any gate; blocker |
| Serious | WCAG 2.2 Level AA criterion; task completed with significant difficulty or error | Repeated effort, wrong input, abandonment risk | 0 open at any gate |
| Moderate | WCAG 2.2 Level AA criterion; extra effort, recoverable | Slower but completable | At most 3 per screen, each with a dated fix ticket |
| Minor | Level AAA criteria, cosmetic | No functional impact | Backlog with a target date |

Definitions match `accessibility-remediation-sprint`, Severity Classification. Where the two tables differ, this table governs a gate decision and the difference is recorded in the gate log.

### Figma/code parity (measurable)

"Parity" is two numbers, not a resemblance:

1. **Token identity.** For every state of a component, each rendered spacing, type and color property, read from the computed style of the running product, resolves to the same token ID as the Figma property it corresponds to in the published contract JSON. Pass = 0 mismatches. A property present on one surface and absent on the other counts as a mismatch.
2. **Raster diff.** Full-state screenshot of the built component page versus the design frame exported at 1x, at viewport widths 360, 768, 1280 and 1440 CSS px. Pass = differing pixels ≤ 0.1% of the compared area at a per-channel tolerance ≤ 8/255, and no shifted region larger than 8 CSS px on either axis.

Frontend Developer runs both and attaches the report; UI Designer countersigns the first component of each pattern. Tolerance values are fixed at Week 2 (Key Decisions) and thereafter change only by written decision.

### One-off exceptions (when a literal is allowed)

A raw value or one-off component is allowed only as a **dated exception**, and only when all six conditions hold:

| # | Condition |
| --- | --- |
| E1 | No existing token or component resolves the need; the requester publishes the search (token IDs and components checked) |
| E2 | The case affects at most 1 screen and at most 2 instances |
| E3 | A token/component proposal is filed, and the owning decision-maker records accept, defer or reject with a date |
| E4 | An expiry date is set, at most 60 calendar days from grant |
| E5 | A ledger row exists in `docs/design-system/exceptions.md` |
| E6 | This is not the third exception for the same value — the third converts to a blocking token proposal |

Ledger columns: `id | path:line | value/component | screen | requester | approver | granted | expires | removal plan | follow-on ticket`. An exception records debt; it does not approve the value. Any literal in the ceiling set without a ledger row fails the open gate; any expired row that was neither removed nor re-approved with a written reason fails it too.

## Agent Roster

Every row traces to a gate line or a Success Criteria metric.

### Command (Always Active)

| Agent | Role | Trace |
| --- | --- | --- |
| Agents Orchestrator | Freezes the scope ceiling, sequences gates, resolves split verdicts, owns escalation | G1.4, G4.5 |
| Senior Project Manager | Owns the plan and dates, signs the ceiling, runs the exceptions review, keeps the gate log | G1.4, M12 |

### Foundation (Always Active)

| Agent | Role | Trace |
| --- | --- | --- |
| UX Architect | Inventory, adopt/rebuild/retire taxonomy, primitive → semantic → component tokens, hierarchy contract | G1.1, G1.3 |
| UI Designer | Canonical screen per pattern; specs: anatomy, states, density, rhythm; parity countersign | G2.1, G2.3 |
| Brand Guardian | Brand source into token values; rules on deviation and voice | G1.2, M6 |
| Inclusive Visuals Specialist | Contrast, imagery and representation as spec limits | G2.1, G2.4 |

### Build & Parity (Phase 2)

| Agent | Role | Trace |
| --- | --- | --- |
| Frontend Developer | Implementation from tokens only; runs the parity report; lands required CI | G2.2, G2.3 |
| Technical Writer | Component docs: when to use, when not, states, tokens, code sample | G2.5, M5 |
| Content Creator | Microcopy: labels, button verbs, error copy, empty-state copy | G2.6, M6 |
| Accessibility Auditor | WCAG 2.2 AA audit per component and state, automated plus assistive technology | G2.4, M4 |

### Quality Gate (Phase 3)

| Agent | Role | Trace |
| --- | --- | --- |
| UI Finish-Gate Reviewer | Runs the eight dimensions on the running product; PASS or HOLD per screen | G3.1, M7 |
| Persona Walkthrough Specialist | Simulated fold-by-fold walkthroughs; emits hypotheses, recruits nobody | G3.2 |
| UX Researcher | Recruits and runs task-based sessions with real users; measures task success | G3.3, M10 |
| Evidence Collector | Screenshot sets at four viewports, prior-state pairs, audit artifacts | G3.4, M13 |
| Reality Checker | Terminal verdict, default NEEDS WORK; re-runs a sample of the gate's own passes | G4.1, G4.5 |

## Phase 1 (Week 1): Audit, Tokens & Scope Ceiling

```text
├── UX Architect → inventory: every screen, route, variant count, adopt / rebuild / retire
├── UI Designer → archaeology: canonical screen versus accident
├── Brand Guardian → brand source into token values
├── Inclusive Visuals Specialist → contrast, motion, imagery as token limits
├── Accessibility Auditor → WCAG 2.2 AA baseline counted per template, severity per scale
├── UX Architect → taxonomy: primitive → semantic → component; no color-named tokens
├── Frontend Developer → styling layer reads tokens; literals go to the exceptions ledger
├── Agents Orchestrator + Senior Project Manager → Scope Ceiling v1.0 written and signed
└── Quality Gates G1 (blocking):
    G1.1 one token source, imported by the styling layer; ≥ 99% of declared
         color/spacing/type properties resolve to a token ID — audit output attached
    G1.2 zero tokens named after colors or raw values; name list attached
    G1.3 every inventoried screen classified adopt / rebuild / retire with an owner;
         0 unclassified
    G1.4 Scope Ceiling v1.0 dated and signed (≤ 10 templates, ≤ 20 components)
    G1.5 accessibility baseline exists: per-template criterion results with severity,
         plus the standard named in the gate log
    G1.6 exceptions ledger file exists with its header row (its being empty passes)
```

## Phase 2 (Weeks 2-3): Components, Copy & Parity

```text
├── UI Designer → specs for the ceiling set only: anatomy, states, density, rhythm, token IDs
├── Frontend Developer → tokens only; parity report per Gate Standards, countersigned
├── Accessibility Auditor → automated scan plus keyboard, one screen reader, 200% zoom,
│   reduced motion per component state; Critical/Serious closed before done
├── Technical Writer → docs page per component
├── Content Creator → copy sheet: labels, button verbs, error copy, empty states
├── Inclusive Visuals Specialist → imagery and contrast sign-off per spec
├── Frontend Developer → parity and accessibility checks wired as required CI
└── Quality Gates G2 (per component; nothing enters the shipped set until all pass):
    G2.1 spec exists with anatomy, states, density, rhythm and token IDs
    G2.2 static scan of the component directory: 0 raw literals outside the token
         registry, or a ledger row per literal (E1-E6); scan output attached
    G2.3 parity per Gate Standards: 0 token mismatches and diff ≤ 0.1% at four widths
    G2.4 0 Critical and 0 Serious findings against WCAG 2.2 AA; AT name and version in the record
    G2.5 docs page carries all five sections, else fail
    G2.6 100% of strings in the copy sheet; every error string names cause and recovery;
         0 placeholder or code-only text
```

## Phase 3 (Weeks 4-6): Migration, Finish Gate & Proof

```text
Weeks 4-5 — migration and the finish gate
├── Frontend Developer → ceiling set screens migrated onto shipped components
├── Retired components inside the ceiling set deleted from the repo, not deprecated;
│   components outside the ceiling are frozen and dated into wave 2
├── UI Designer + UI Finish-Gate Reviewer → final pass on hierarchy and rhythm per template
├── UI Finish-Gate Reviewer → eight dimensions at 1280 and 360 CSS px on the running product
├── Persona Walkthrough Specialist → two personas, fold by fold; findings filed as
│   numbered hypotheses with a screenshot location, not as verdicts
├── Evidence Collector → screenshot set per screen at four viewports, prior state kept
├── Senior Project Manager → exceptions ledger review against Gate Standards
└── Quality Gates G3 (per screen):
    G3.1 all eight dimensions Pass, or N/A with a written reason and record reference;
         one Fail on one in-scope screen = HOLD
    G3.2 the walkthrough ran and its hypotheses are filed (hypotheses are not pass criteria;
         a hypothesis that shows a demonstrable defect fails G3.1 instead)
    G3.3 adoption ≥ 95% of rendered elements on the screen are shipped component instances
    G3.4 screenshot set complete: 4 viewports × light, dark when in scope, prior state included
    G3.5 0 references to retired components in the ceiling set
    G3.6 0 literals without a ledger row, 0 expired rows

Week 6 — research, proof, verdict
├── UX Researcher → 5+ task-based sessions on the critical workflows from Required Inputs,
│   recruited from the participant pool; recorded tasks, success rate, interventions
├── Evidence Collector → research artifacts and gate evidence indexed in the gate log
├── Reality Checker → re-runs a sample of components the finish gate passed
├── Agents Orchestrator → resolves any split verdict and logs the evidence
└── Quality Gates G4 (system level):
    G4.1 Reality Checker re-runs 3 gate-passed components chosen unannounced; any sample
         that fails revokes that component's PASS and forces a re-run
    G4.2 two recorded red runs: a deliberately broken component (one raw literal, one
         contrast break) turns visual regression red and turns accessibility red
    G4.3 gate log complete: per-screen verdicts, screenshot paths, ledger state, research
         results, with dates and agent names
    G4.4 research: ≥ 5 participants, median task success ≥ 80% per critical workflow,
         0 participant-blocking defects open
    G4.5 every split verdict has a re-run observation and a named resolver in the log;
         0 unresolved splits
```

### Verdict Precedence

Two verdicts exist and they are not equal in effect:

| Rule | Statement |
| --- | --- |
| Both bind | A screen passes only when the UI Finish-Gate Reviewer returns PASS **and** the Reality Checker does not return NEEDS WORK |
| Failing verdict is default | HOLD and NEEDS WORK stand until the observation that produced them is re-run and recorded passing; neither reviewer clears the other by opinion |
| Terminal | Reality Checker NEEDS WORK is terminal for this runbook's release claim; there is no appeal past it inside the runbook |
| Split resolution | Agents Orchestrator resolves a verdict split using the re-run evidence, within 1 business day; a scope split (is this screen inside the ceiling) goes to Senior Project Manager with the Product owner; the resolver's name and the evidence reference go in the gate log |
| Timeout | No resolution inside 1 business day leaves the failing verdict standing |
| Escalation | Agents Orchestrator reports the split and the standing verdict to the Product owner; the runbook keeps HOLD |

### What the Finish Gate Actually Checks

Every dimension is a failable observation. N/A is legal only with a written reason that names the absent surface plus a record reference; an N/A without a reason is a HOLD.

| Dimension | Pass condition | Measurement method |
| --- | --- | --- |
| Hierarchy | Primary object and primary action are identifiable before body copy is read | 5-second test per template: 5 naive participants, screenshot shown 5 s then hidden; pass = ≥ 4 of 5 name the same primary object and the same primary action |
| Spacing | Every margin and padding resolves to a spacing token | Computed-style audit of the rendered screen: 0 values outside the spacing token set; diff against spec ≤ 0.1% |
| Type | Every font size, weight and line height resolves to a type token | Computed-style audit: 0 non-token values; ≤ 3 distinct sizes per text role |
| Empty states | Every collection surface has a designed empty state and a next action | Enumerated against the screen's collections; 0 without an empty state; screenshot on file |
| Error states | Every field and view has a designed error state naming cause and recovery | Each error forced through a request failure; 0 fields or views without one; screenshot on file |
| Loading | Every async surface has a designed loading state with no layout shift | Throttled load, 3 runs, worst reported: CLS < 0.1 per surface |
| Focus states | Visible focus on every interactive element, keyboard-proven | Tab traversal of the screen: 100% of interactive elements show an indicator, 0 traps, 200% zoom does not clip it |
| Dark mode | Contrast holds and parity holds in the dark token set | Contrast ≥ 4.5:1 body, ≥ 3:1 large text and UI components, measured per text pair; N/A only when the product ships no dark theme, with the record reference |
| Motion | Every transition states a purpose and honours reduced motion | Motion token list with a documented purpose each; with reduced motion emulated, 0 transitions above 0 ms other than opacity changes |

## Key Decisions

| Decision Point | When | Who Decides |
| --- | --- | --- |
| Token taxonomy and semantic vocabulary (primitive → semantic → component) | Week 1 | UX Architect + Brand Guardian |
| WCAG 2.2 AA target, legal overlay, exclusions | Week 1 | Accessibility Auditor + Senior Project Manager |
| Scope Ceiling v1.0: templates, components, workflows | Week 1, before G1.4 | Agents Orchestrator + Senior Project Manager + Product owner |
| Canonical screen per pattern; adopt / rebuild / retire | Week 1 | UI Designer + UX Architect |
| Parity tolerance values (the numbers in Gate Standards) | Week 2, before first PASS | Frontend Developer + UI Designer |
| One-off exception grant, expiry and ledger row | Any phase, per case | UI Designer + Frontend Developer + Senior Project Manager |
| Copy voice for labels, button verbs and error messages | Week 2 | Content Creator + Brand Guardian |
| Research tasks, participant count and success thresholds | Week 4, before sessions | UX Researcher + Senior Project Manager |
| Split verdict resolution | Any phase, per split | Agents Orchestrator (scope splits: Senior Project Manager + Product owner) |
| Release claim | Week 6 | Reality Checker |

## Success Criteria

Measured inside the 4-6 week window, so every target is countable before handover.

| Metric | Target | Window | Evidence |
| --- | --- | --- | --- |
| M1 · Token resolution of declared properties | ≥ 99% resolve to a token ID | Week 1 | G1.1 audit output |
| M2 · Shipped-set components with a documented token source | 100% | Week 3 | G2.1 spec |
| M3 · Shipped-set components passing parity | 100% (0 mismatches, ≤ 0.1% diff) | Week 3 | G2.3 report |
| M4 · Shipped-set components with 0 Critical and 0 Serious findings | 100% | Week 3 | G2.4 record |
| M5 · Components with a complete docs page | 100% of the shipped set | Week 3 | G2.5 |
| M6 · Strings covered by the copy sheet; error copy naming recovery | 100% | Week 3 | G2.6 |
| M7 · Ceiling-set screens holding a finish-gate PASS and 0 open HOLD | 100% of the ceiling set | Week 5 | G3.1 |
| M8 · Adoption inside the ceiling set | ≥ 95% of rendered elements are shipped components | Week 5 | G3.3 |
| M9 · Retired components deleted with references removed | 0 references in the ceiling set | Week 5 | G3.5 |
| M10 · User research result | ≥ 5 participants; median task success ≥ 80% per critical workflow | Week 6 | G4.4 |
| M11 · Required CI checks proven able to fail | 2 recorded red runs (visual regression, accessibility) | Week 6 | G4.2 |
| M12 · Exceptions past expiry, open | 0 | Week 6 | Ledger review at G3.6 |
| M13 · Screenshot sets on file per screen | 4 viewports × light (+ dark when in scope) | Week 5 | G3.4 |

## Post-runbook

Metrics whose measurement window exceeds the runbook.

| Metric | Target | Window | Named owner |
| --- | --- | --- | --- |
| Visual-regression or literal escapes reaching production (escape = merged raw literal or unregistered component found in a screen audit) | ≤ 2 per month | Months 2-6 after handover | Senior Project Manager |
| Component coverage of all product screens | ≥ 95%, end of wave 2 | ≤ 6 months | Agents Orchestrator |
| Median time to build a new screen from the library | ≤ 1 business day across the next 5 screens | Next quarter | Senior Project Manager |
| Accessibility conformance drift on shipped screens | 0 Critical, 0 Serious per audit | Quarterly | Accessibility Auditor |
| Open exceptions and same-value recurrence | ≤ 4 per quarter, none repeated 3 times | Quarterly | Senior Project Manager |
| Library adoption by new UI work | ≥ 90% of new UI built from the shipped set | Quarterly review | UI Finish-Gate Reviewer |

## Common Pitfalls

| Pitfall | Mitigation |
| --- | --- |
| Parity approved by eyeball, then drift returns within a sprint | Parity is the token-ID comparison plus the ≤ 0.1% diff number at four widths; an opinion is not an observation |
| The finish gate says PASS and the Reality Checker says NEEDS WORK on the same screen | Precedence is written: the failing verdict stands until its observation is re-run; Agents Orchestrator resolves with evidence inside 1 business day |
| "Every screen" enters the plan in Week 1 and nothing finishes by Week 6 | Scope Ceiling v1.0 is a signed Week 1 output; every gate measures the ceiling set, not the inventory |
| A one-off literal is granted verbally and lives for years | Exceptions need E1-E6, an expiry of ≤ 60 days and a ledger row; the third for one value becomes a blocking token proposal |
| Accessibility severity means whatever the reviewer felt that day | Severity is the printed WCAG 2.2 Level A/AA mapping; Critical and Serious must both be 0 at a gate |
| UX research turns out to be the persona walkthrough with a new label | The walkthrough simulates and recruits nobody, producing hypotheses; the Researcher recruits ≥ 5 participants and reports a task-success rate |
| Dark mode is failed on a product that ships no dark theme, or waved through | Dimensions are Pass, Fail or N/A with a written reason and a record reference; an unexplained N/A is a HOLD |
| Microcopy is left to whoever wrote the component | A copy sheet covers every label, verb and error string; an error string without cause and recovery fails the gate |
| Screenshot proof is a Figma export | The gate reviews the running product; mockups are not evidence |
| A Figma library with no code counterpart; two systems ship | Divergence is a defect under G2.3; parity is checked in the same change that ships the component |
