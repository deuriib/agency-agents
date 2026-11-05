# Runbook: Accessibility Remediation Sprint

> **Mode**: NEXUS-Micro | **Duration**: 1-2 weeks | **Agents**: 9

## Scenario

A compliance deadline or an accessibility complaint has created urgency. The product has known or suspected failures and no current audit. The remediation sprint audits against a pinned standard, prioritizes by a printed severity scale, and fixes what it can prove it fixed.

**Non-negotiable rule:** a violation is fixed when it is verified with the assistive technology a user actually uses, not when an automated scanner stops reporting it. Scanner-clean is not accessible. The scan finds leads; the keyboard and the screen reader decide.

### Severity Scale (cited by every gate as Critical / Serious / Moderate / Minor)

Severity is assigned at triage from the impact observed on a real task, printed once, and used unchanged by every gate and every metric below. A finding with no severity after triage is a triage failure and fails G1.

| Level | WCAG Mapping | Impact | Remediation SLA |
| --- | --- | --- | --- |
| **Critical** | Level A, blocks task | User cannot complete the task | Fix within 48 hours |
| **Serious** | Level AA, causes error or confusion | User completes with significant difficulty | Fix within the sprint |
| **Moderate** | Level AA, inconvenient | Extra effort, but recoverable | Fix within the sprint or schedule with a date |
| **Minor** | Level AAA or cosmetic | No functional impact | Backlog with a target date |

## Applicability

| Use this runbook when | Use a different runbook when |
| --- | --- |
| A deadline or complaint forces accessibility work now, and no current audit exists | The interface must become systematic, with accessibility as one quality dimension — `design-system-and-ui-quality` |
| Failures are known or suspected and unclassified | Production is broken for everyone right now — `incident-response` |
| A standard must be met and the conformance claim defended with evidence | The gap is policy and gates repo-wide — `repository-hardening-program` |
| Existing journeys must keep working for keyboard and screen reader users | The work is a new build with no shipped surface — `feature-discovery-to-spec` |

## Required Inputs

Only artifacts the roster cannot author. The audit report and the fix queue are **outputs** of Week 1, not inputs: a team that waits for a finished inventory waits forever.

| Input | Why it blocks | Owner (from outside the roster) |
| --- | --- | --- |
| The conformance target: WCAG version and level, or Section 508, named by the authority that will judge the work | Without a pinned standard the audit measures nothing, and WCAG 2.2 AA and Section 508 are not interchangeable | Compliance or legal owner |
| Access to an assistive-technology test environment: screen readers with licenses and versions, keyboard-only browser profiles, high-contrast and reduced-motion settings, and permission to drive the real product in it | The close rule is an AT observation; without the environment every fix closes on a scanner, which is not a fix | IT or QA infrastructure owner |
| The current violation inventory, or explicit authority and tooling to build one from scratch | Either the audit corrects an existing list or it creates the list; silence on which produces a fourth partial audit | Product owner |
| A named owner who can authorize a fix that changes design — layout, hierarchy, interaction model, target size | The best structural fixes are design decisions; an unauthorized redesign is reverted in review and the defect returns | Product owner or design director |
| Real users of assistive technology, where available, recruited with consent for at least the critical journeys | Keyboard and screen reader testing by the team finds conformance defects; only users find task failures | Product owner |

## Agent Roster

Every row traces to a Quality Gate line or a Success Criteria metric. Activation marks when the agent joins: the Remediation Core runs from Day 1 to the exit proof; Advisory agents join per finding.

### Remediation Core (Always Active)

| Agent | Role |
| --- | --- |
| Agents Orchestrator | Sprint facilitation, fix sequencing, the gate log, and the call when a gate fails |
| Senior Project Manager | Scope control, deliverable tracking, dated follow-ons for what does not fit the window |
| Section 508 Accessibility Specialist | Pins the standard, maps each finding to its success criterion, prepares the conformance statement |
| Accessibility Auditor | Automated tooling plus keyboard, screen reader, zoom and contrast testing; re-tests every fix with the AT that found it |
| UI Designer | Design-level fixes: contrast, focus visibility, target size, reflow at 200% zoom |
| Frontend Developer | Implementation fixes, semantics before styling; estimates each fix and scopes down anything over one day |
| Evidence Collector | Before and after evidence per finding, indexed by criterion |

### Advisory (As Needed)

| Agent | Role |
| --- | --- |
| Legal Compliance Checker | Deadline obligations, disclosure language, review of every statement the team publishes |
| Inclusive Visuals Specialist | Alt-text strategy, non-text content, charts, diagrams and media alternatives |

## Week 1: Audit & Triage

Days 1-4. The audit runs against the pinned standard and nothing is deferred at triage time — deferral is a decision with an owner and a date, made at G1.

```text
├── Section 508 Accessibility Specialist → pin one standard: WCAG 2.2 AA or Section 508,
│   with its level named in writing; "both" is not a pin
├── Accessibility Auditor → automated tooling across every template and state; the scan is a
│   lead generator, and every lead is confirmed by hand before it enters the log
├── Accessibility Auditor → manual keyboard pass of every interactive flow: tab order,
│   visible focus, keyboard traps, skip links, menu and dialog behaviour
├── Accessibility Auditor → screen reader pass on at least two ATs from the test environment,
│   each recorded by name and version
├── Accessibility Auditor → 200% zoom and reflow, high-contrast mode, reduced motion
├── Accessibility Auditor → record each finding: location, success criterion, severity from the
│   Severity Scale, reproduction steps, AT name and version, evidence path
├── Legal Compliance Checker → flag the findings that carry direct compliance exposure
├── Senior Project Manager → name the critical journeys the exit gate will judge, and the fix
│   queue with an owner and an estimate per row
├── Frontend Developer → estimate each row; anything over one day is scoped down or deferred
├── Agents Orchestrator → rank the queue Critical, Serious, Moderate, Minor; every deferred row
│   carries a named owner and a follow-on date
└── Quality Gate (G1): every finding in the log carries a location, a success criterion, a
    severity from the Severity Scale, reproduction steps and the AT name and version that
    produced it — one finding missing one field fails the gate, and so does one Critical
    without a named owner and a 48-hour date
```

## Week 2: Fix & Prove

Days 1-5 fix, days 6-10 prove. Structural fixes land first because they change what the cosmetic fixes must be.

```text
Days 1-5 — fix
├── Frontend Developer → structural fixes first: focus order, landmarks, form labelling,
│   keyboard traps, heading structure, error identification
├── UI Designer → contrast, target size, focus visibility at the design level, reflow at 200%
├── Frontend Developer → implementation from the design decision, semantics before styling
├── Accessibility Auditor → re-test every fix with the same AT that reported it, not a scanner
├── Evidence Collector → before and after evidence per finding, filed against the criterion
├── Agents Orchestrator → any fix that introduces a regression is reverted, not patched over
└── Quality Gate (G2): 0 Critical and 0 Serious remain open in the fix queue, each closure
    carrying a before/after pair observed on the AT that reported it — one open Serious, or one
    closure whose only evidence is a scanner rescan, fails the gate
```

```text
Days 6-10 — prove and report
├── Accessibility Auditor → full re-audit of every template and state, not only the fixed items
├── Accessibility Auditor → keyboard-only run of each critical journey end to end, unaided
├── Accessibility Auditor → screen reader run of each critical journey on the second AT
├── Accessibility Auditor → confirm no new failure was introduced by the remediation
├── Section 508 Accessibility Specialist → prepare the conformance statement: standard, level,
│   scope audited, what conforms, what does not, plan and date for each exception
├── Legal Compliance Checker → review the statement language before it leaves the team
├── Evidence Collector → final evidence pack indexed by criterion, with AT names and versions
├── Senior Project Manager → close the deferred list with dates and owners, or re-open it
└── Quality Gate (G3): the full re-audit records 0 Critical and 0 Serious, every critical journey
    completes keyboard-only and by screen reader, and the conformance statement carries a named
    human signature — one unscheduled Critical or Serious, one journey that needs a mouse, or a
    missing signature fails the exit proof
```

### Status Update Template

```text
[Timestamp] — Accessibility Remediation Update

SCOPE: [Standard, level]
FINDINGS: [Count by severity]
CRITICAL CLOSED: [n / total]
SERIOUS CLOSED: [n / total]
DEFERRED: [Count with scheduled dates and owners]
NEXT MILESTONE: [Date and deliverable]
```

### Escalation Matrix

| Condition | Escalate To | Action |
| --- | --- | --- |
| Deadline is imminent and Critical findings remain open | Legal Compliance Checker | Written scope reduction and disclosure plan, signed by the named owner |
| A fix introduces a regression | Agents Orchestrator | Revert, re-approach, and log the revert as evidence |
| Standard ambiguity blocks a decision | Section 508 Accessibility Specialist | Written interpretation with rationale, cited by the next gate |
| A required fix conflicts with brand direction | UI Designer + Inclusive Visuals Specialist + brand owner | Criterion wins; the deviation is written and dated |
| Deferred items exceed the window | Senior Project Manager | Follow-on with a date, an owner and a re-audit commitment |

## Key Decisions

| Decision Point | When | Who Decides |
| --- | --- | --- |
| Which conformance target governs, and whether a contractual or jurisdictional regime is stricter than it | Week 1, before the audit starts | Section 508 Accessibility Specialist + Senior Project Manager |
| What blocks the release versus what is scheduled: Critical and Serious block, Moderate is scheduled with a date, Minor goes to backlog | Week 1, at G1 | Agents Orchestrator + Legal Compliance Checker |
| Redesign or patch, per finding: a fix that changes layout, hierarchy, interaction model or target size is a design decision, not an implementation detail | Week 1, per row in the queue | UI Designer + Frontend Developer |
| How a finding that conflicts with brand direction is handled | Any phase, per conflict | UI Designer + Inclusive Visuals Specialist + brand owner |
| Which ATs and versions count as verification for this product | Week 1, before the first AT pass | Accessibility Auditor + Section 508 Accessibility Specialist |
| Who signs the conformance claim, and what the statement may say | Week 2, before G3 | Named human owner, never an agent |

## Success Criteria

Measured inside the 1-2 week window, so every target is countable at the exit proof.

| Metric | Target |
| --- | --- |
| Violations closed by severity — Critical | 100% of the Week 1 Critical log closed and re-verified on the AT that reported it |
| Violations closed by severity — Serious and Moderate | Serious 100% closed and AT-verified; Moderate 100% closed or scheduled with a dated ticket and a named owner |
| Critical and Serious remaining at the exit gate | 0 open; a single open Critical or Serious fails G3 |
| Keyboard-only completion of the critical journeys named in Week 1 | 100% of journeys, 0 keyboard traps, visible focus at every stop, no mouse event required |
| Screen-reader verification coverage | 100% of Critical and Serious fixes re-tested on the AT that reported them; at least 2 ATs per critical journey, name and version recorded |
| Regression introduced by the remediation | 0 new Critical and 0 new Serious in the full re-audit |

### Conformance Claims Are Signed, Not Asserted

A conformance claim, a VPAT entry, and any public accessibility statement are prepared by the team and **signed by a named human** who accepts the liability for the wording. Agents produce the evidence pack, the criterion mapping and a draft; no agent asserts conformance, and no gate passes a statement that carries no human signature. Scanner output is never attached as proof of conformance.

```text
Accessibility Conformance Statement — [Date]

STANDARD: [WCAG 2.2 AA / Section 508]
SCOPE: [Templates and flows audited]
CONFORMANCE: [Conforms / Partially conforms]
KNOWN EXCEPTIONS: [List with remediation dates]
EVIDENCE: [Reference to the evidence pack]
SIGNED: [Named human, role]
CONTACT: [Owner]
```

## Common Pitfalls

| Pitfall | Mitigation |
| --- | --- |
| An automated scan is treated as the audit, and the run closes on a green report | The scan generates leads; every lead is confirmed by keyboard and screen reader pass, and a closure whose only evidence is a rescan fails G2 |
| A contrast ratio or a font size is changed in CSS while the semantic defect underneath stays | Structural fixes land first: focus order, landmarks, labels, headings; the cosmetic pass runs after them |
| ARIA is layered on a broken structure so the tree reads correctly to a developer | Native semantics first; a role or attribute added over a non-semantic element is a rejected fix, not an approved one |
| Testing is done with a mouse and the keyboard path is assumed | Every interactive flow is traversed keyboard-only at G1 and every critical journey is completed keyboard-only at G3 |
| A component is declared fixed and nobody re-verifies it with a screen reader | The re-test uses the same AT that reported the finding, recorded by name and version, and Evidence Collector files the pair |
| The remediation drops scope to hit the date and the statement still claims conformance | Scope reduction is a written decision in the escalation matrix; the statement names exceptions with dates, and an unclaimed exception fails G3 |
