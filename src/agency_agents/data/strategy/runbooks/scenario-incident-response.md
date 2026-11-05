# 🚨 Runbook: Incident Response

Mode: NEXUS-Micro | Duration: Minutes to hours | Agents: 10

## Scenario

Something is broken in production. Users are affected. Speed of response matters, but so does doing it right. This runbook covers detection through post-mortem: detect, declare, contain, stabilise, verify, and close on evidence.

Scope is one live production incident — a named service, a named commander, a written severity, and a clock. It is not a scheduled vulnerability fix, not triage of known non-production defects, and not a slipping program whose reported status is the problem.

**Non-negotiable:** an incident is not closed when the symptom disappears. It is closed when the cause is named and evidence is attached. A mitigation without a follow-up owner is an open incident, whatever the dashboard says.

**Legal boundary:** this roster contains no legal agent. Wherever a customer-visible decision appears — disclosure, breach notification, compensation — an agent prepares the material and a named human decides. Legal is pulled in from outside this roster through the escalation path under Severity and Escalation; no agent on this roster renders a legal determination or speaks as counsel in a human's place.

## Applicability

| Use this runbook when | Use a different runbook when |
| --- | --- |
| Production is broken or degraded and users are affected right now | A known vulnerability needs a fix window and coordinated disclosure — use `security-vulnerability-response` |
| A symptom is customer-visible or revenue-affecting and needs a commander, a severity, and a clock | The defects are already known, non-production, and need a fix order — use `bug-triage-and-defect-elimination` |
| A mitigation must land inside minutes to hours, with one person accountable for the call | A delivery program has slipped and reported status is the problem — use `delivery-recovery` |
| A blameless post-mortem with owned action items must exist within 48 hours | The ask is to harden the repository or pipeline against a class of failure — use `repository-hardening-program` |
| An external dependency is failing and the fallback decision cannot wait | The issue is support queue volume, not service availability — use `customer-support-operations` |

## Severity and Escalation

The table below is the only place severity is defined. Every gate cites it, and a severity that is not written here is not a severity: "high" and "bad" are not severities, P0 through P3 are.

| Level | Definition | Examples | Response Time |
|-------|-----------|----------|--------------|
| **P0 — Critical** | Service completely down, data loss, security breach | Database corruption, DDoS attack, auth system failure | Immediate (all hands) |
| **P1 — High** | Major feature broken, significant performance degradation | Payment processing down, 50%+ error rate, 10x latency | < 1 hour |
| **P2 — Medium** | Minor feature broken, workaround available | Search not working, non-critical API errors | < 4 hours |
| **P3 — Low** | Cosmetic issue, minor inconvenience | Styling bug, typo, minor UI glitch | Next sprint |

Escalation path. Escalation is a paging decision taken by the commander, not a discussion opened in the channel.

| Condition | Escalate To | Action |
|-----------|------------|--------|
| P0 not resolved in 30 min | Studio Producer | Additional resources, vendor escalation |
| P1 not resolved in 2 hours | Project Shepherd | Resource reallocation |
| Data breach suspected | Legal Compliance Checker, then named human counsel outside this roster | Regulatory notification assessment is prepared by the agent and decided by the human |
| User data affected | Legal Compliance Checker + Executive Summary Generator, then named human counsel outside this roster | GDPR/CCPA notification package is prepared by this roster, never decided by it |
| Revenue impact > $X | Finance Tracker + Studio Producer | Business impact assessment |
| P3 accepted but left unfixed | Sprint Prioritizer | Backlog row with an owner and a date, or the incident stays open |

## Required Inputs

Only what the roster cannot produce. Everything else this runbook needs, it makes.

| Input | Why it blocks | Owner |
| --- | --- | --- |
| On-call rotation and paging access — who is on call right now, and the ability to page them | A responder who cannot page the next person is a responder working alone; detect-to-declare is a paging path, not a personal network | Engineering Manager |
| A written severity policy, or explicit authority to declare one | The severity table is only usable if someone is empowered to apply it against pressure to call it a P2 | Incident Commander + Engineering Leadership |
| The incident channel — one written channel of record, plus a bridge for P0/P1 | Two channels means two timelines, and the post-mortem is built from the written one | Incident Commander |
| Customer-facing status page access | Remediation without a customer-visible state update is how a P1 becomes a trust incident | Support Responder |
| A named incident commander — a person's name, not a role | Command by committee is why no rollback decision gets made inside the window | Engineering Leadership |

Everything else is an output: the severity record, the timeline, the status updates, the executive brief, the verification evidence, and the post-mortem report.

## Agent Roster

### P0 Critical Response (Always Active)

| Agent | Role |
| --- | --- |
| Infrastructure Maintainer | Incident commander: scope and impact, severity call against the severity table, coordination, and the 30-minute post-fix watch |
| DevOps Automator | Deployment and rollback: recent deploy history, pipeline state, staged rollback candidate, executes the rollback on command |
| Agents Orchestrator | Incident command: assigns cause-class owners, holds the 15-minute update cadence, runs the post-fix loop and escalation |
| Backend Architect | Server-side cause: database health, API error rates, service-to-service calls, isolation of the failing component |
| Support Responder | Customer-visible state: status page and user notifications every 15 minutes while the incident is open |
| Executive Summary Generator | Stakeholder brief on P0: situation, cause, action, impact, next-update timestamp |

### Verification & Post-Mortem (Post-Fix)

| Agent | Role |
| --- | --- |
| Evidence Collector | Proof the fix worked: screenshots, the broken metric back at a named baseline, no new issue introduced |
| API Tester | Regression on affected endpoints, response times normalised, error rates at baseline |
| Workflow Optimizer | Post-mortem lead: timeline, root cause with 5 Whys, impact, prevention, action items with owners and deadlines |
| Sprint Prioritizer | Prevention tasks and accepted risks entered in the backlog with an owner and a date |

## Execution Timeline

The clock is the runbook. Three windows, three gates, no phase that passes by elapsed time.

| Phase | Window | Question the phase answers | Gate |
| --- | --- | --- | --- |
| Detect, declare, contain | Minutes 0-30 | What is broken, how bad is it by the severity table, and who is in charge | G1 |
| Stabilise | Minutes 30-120 | Roll back, fix forward, or fail over — and what is the customer told | G2 |
| Verify and post-mortem | Post-fix, report within 48 hours | Is it actually fixed, what caused it, and who owns the follow-up | G3 |

Severity moves in one direction freely and in the other only in writing: raising P2 to P0 needs a channel line, lowering P0 to P2 needs a channel line citing the severity table.

## Minutes 0-30: Detect, Declare, Contain

```text
TRIGGER: monitoring alert / user report / agent detection

├── Infrastructure Maintainer → acknowledge, then declare in writing:
│   ├── Scope: how many users, which services, is data at risk
│   ├── Severity as P0/P1/P2/P3 from the severity table, never as "high" or "bad"
│   ├── Named incident commander stated in the channel
│   ├── Response team activated by severity: P0 all hands, P1 commander + DevOps Automator +
│   │   relevant developer + Support Responder, P2 developer + Evidence Collector,
│   │   P3 Sprint Prioritizer
│   └── Incident channel opened as the single written channel of record, bridge opened for P0/P1
├── Parallel first observations, reported into the channel, never held privately:
│   ├── Infrastructure Maintainer → system metrics (CPU, memory, network, disk), error logs,
│   │   recent deployments, external dependencies
│   ├── Backend Architect (P0/P1) → database health, API error rates, service communication,
│   │   failing component
│   ├── Agents Orchestrator → holds the observation set: every cause class above has an owner,
│   │   and a client-side specialist is pulled in ad hoc when the client surface is implicated
│   └── DevOps Automator → deployment history and pipeline state; rollback candidate identified
│       and staged, not executed
├── Support Responder → first status page update, timestamped, with no cause claim before a
│   cause exists
├── Executive Summary Generator → P0 only: first stakeholder brief carrying the next-update time
└── Quality Gate (G1): the channel holds one written severity from the severity table and one
    named incident commander, and the status page carries a timestamped update — one look at the
    channel and the status page settles it
```

## Minutes 30-120: Stabilise

```text
One branch is chosen, and the choice plus the name of who chose it goes into the channel:

├── Caused by a recent deployment → DevOps Automator rolls back the exact artifact that shipped,
│   Infrastructure Maintainer verifies recovery
├── Caused by infrastructure → Infrastructure Maintainer scales, restarts or fails over,
│   DevOps Automator supports the change
├── Caused by a code bug → developer implements the hotfix, Evidence Collector verifies it,
│   DevOps Automator deploys it, Infrastructure Maintainer monitors recovery
└── Caused by an external dependency → Infrastructure Maintainer activates fallback or cache,
    Support Responder communicates, monitoring waits on the dependency

Throughout the window:
├── Support Responder → status page and user notifications every 15 minutes, including when
│   there is nothing new: "no change, next update at HH:MM"
├── Executive Summary Generator → stakeholder brief at each severity change and each mitigation
│   attempt, P0 only
├── Named human decision owner → any customer-visible commitment beyond "we are working on it":
│   disclosure, breach notification, compensation. The roster prepares the material, legal is
│   pulled in from outside this roster, and no agent speaks as counsel
└── Quality Gate (G2): the chosen branch and the name of who chose it are written in the channel,
    the mitigation either landed or has a stated next attempt with a time, and the newest status
    page update is under 15 minutes old — one look at the channel and the status page settles it
```

### Status Page Update (Support Responder)

```text
[TIMESTAMP] — [SERVICE NAME] Incident

Status: [Investigating / Identified / Monitoring / Resolved]
Impact: [Description of user impact]
Current action: [What we're doing about it]
Next update: [When to expect the next update]
```

### Executive Update (Executive Summary Generator — P0 only)

```text
INCIDENT BRIEF — [TIMESTAMP]

SITUATION: [Service] is [down/degraded] affecting [N users/% of traffic]
CAUSE: [Known/Under investigation] — [Brief description if known]
ACTION: [What's being done] — ETA [time estimate]
IMPACT: [Business impact — revenue, users, reputation]
NEXT UPDATE: [Timestamp]
```

## Post-Fix: Verify & Post-Mortem

```text
├── Evidence Collector → the fix is proven by observation, not by the absence of alerts:
│   ├── screenshots of the working state, kept for the post-mortem record
│   ├── the metric that was broken, back at baseline, with the baseline named
│   └── no new issue introduced by the mitigation itself
├── API Tester (API-related) → regression on affected endpoints, response times normalised,
│   error rates back at baseline
├── Infrastructure Maintainer → all metrics returning to normal, no cascading failure,
│   30-minute post-fix watch completed and logged
├── Support Responder → closing status page update with the cause named at the level a customer
│   can act on; anything about disclosure, breach notification or compensation is prepared by
│   this roster and decided by a named human, with legal pulled in from outside this roster
├── Workflow Optimizer → post-mortem led within 48 hours, blameless:
│   ├── Timeline: introduced, detected, declared, mitigated, resolved, total user impact
│   ├── Root cause: what failed, why it failed, why it was not caught earlier, 5 Whys
│   ├── Impact: users affected, revenue, reputation, data
│   ├── Prevention: which monitoring catches it sooner, which test prevents it, which process
│   │   and infrastructure change is required
│   └── Action items: [Action] → [Owner] → [Deadline], every row filled
├── Sprint Prioritizer → prevention tasks and every accepted risk from the mitigation entered in
│   the backlog with an owner and a date
└── Quality Gate (G3): the cause is named in one sentence and backed by an attached artifact,
    every action item carries a named owner and a deadline, and every mitigation that shipped
    without a permanent fix carries an owner — one look at the post-mortem record settles it
```

## Key Decisions

| Decision Point | When | Who Decides |
| --- | --- | --- |
| Declare severity P0 through P3, and every later change to it | Minutes 0-30, and again whenever measured impact moves | Incident Commander against the severity table; raising is unilateral, lowering needs a written line |
| Page the roster out of hours, or hold it inside the on-call rotation | Minutes 0-30, as soon as severity is written | Incident Commander on P0/P1; Engineering Leadership owns the cost of a false page |
| Roll back or fix forward | Minutes 30-120, once one branch of the decision tree has evidence | Incident Commander, on the DevOps Automator rollback assessment and the Backend Architect cause read |
| Who talks to customers, and what they are told | Minutes 0-120, before the first customer-visible commitment beyond "we are working on it" | Support Responder drafts and publishes routine updates; disclosure, breach notification and compensation are a named human's call, with legal pulled in from outside this roster |
| Stop the deploy pipeline — freeze merges and releases | Minutes 0-120, when two changes or two incidents in the same window are suspected | Incident Commander together with DevOps Automator; unfreezing needs the same two |
| Accept the mitigation and close, or keep the incident open | Post-fix, at G3 | Incident Commander with Workflow Optimizer; a mitigation without a named follow-up owner stays open |

## Success Criteria

| Metric | Target |
| --- | --- |
| Time to detect — first alert or report to a human acknowledging it | 5 minutes or less for P0/P1 |
| Time to declare — acknowledgement to a written severity and a named commander | 10 minutes or less |
| Time to mitigate — declaration to the customer-visible symptom gone | 60 minutes or less for P0, 4 hours or less for P1 |
| Time to restore — declaration to all metrics at baseline with the mitigation still holding | 120 minutes or less for P0 |
| Post-mortem completion — resolved to a published report with owned action items | 48 hours, 100% of P0 and P1 incidents |
| Mitigations closed with a named follow-up owner and a date | 100%, before the incident is closed |

## Common Pitfalls

| Pitfall | Mitigation |
| --- | --- |
| An incident without a named commander — everyone coordinates, nobody decides, and every option waits for consensus | G1 fails until one name and one severity are written in the channel; escalation to Studio Producer at 30 minutes is a paging decision, not a discussion |
| The first responder debugging alone in silence — twenty minutes of investigation that exists only in one person's head | Findings go into the written channel as they are produced; an observation held privately is treated as not made |
| Rollback of an untested artifact — the rollback ships a second unknown into a system already failing | DevOps Automator rolls back the exact artifact that shipped, infra state is verified before and after, and Evidence Collector confirms recovery from the same baseline |
| Closing on the symptom — alerts are green, the cause is unnamed, no artifact is attached | A close needs the cause in one sentence plus attached evidence at G3; otherwise the incident stays open as a mitigation with an owner |
| A post-mortem that blames a person instead of a gap | Findings are written as missing guardrail, missing test, missing alert, or missing review; a report naming an individual fails G3 and is rewritten |
| Severity inflated or deflated to match the response the team wants to give | Severity is applied from the table against measured impact only, every change is a written channel line citing the table, and an inflated P0 is corrected upward or downward in the same place it was declared |
