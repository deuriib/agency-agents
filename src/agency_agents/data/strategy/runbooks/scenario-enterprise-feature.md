# Runbook: Enterprise Feature Development

> **Mode**: NEXUS-Sprint | **Duration**: 6-12 weeks | **Agents**: 22

## Scenario

You are adding a major feature to an existing enterprise product: live customers on it, an integration surface that predates the feature, and compliance, security, and quality gates that are not negotiable. Several stakeholders must align, and each holds a different piece of the authority — scope, budget, risk, or regulatory exposure. Weeks 1-11 produce a spec, an architecture, an implementation, and evidence. Week 12 ships it and operates it.

Doctrine, non-negotiable: **the feature is not done when it is deployed but when every acceptance criterion has evidence attached and the rollback path has been exercised.** A deployment is a step inside the run, not its end. The closing condition is an evidence pack a second person can audit without asking a question, plus a rollback rehearsal with a timestamp. Deploying first and assembling evidence afterwards is a failed run with a live endpoint.

Human-authority boundary: **the checker prepares, a named human decides.** The Legal Compliance Checker maps the governing regime onto the feature, drafts the obligations, and assembles the finding set; it never signs off on regulatory exposure. Every compliance determination is signed by the named human approver recorded in Required Inputs, with that person's authority basis written beside the signature. An agent verdict on legal exposure is a draft, not a decision, and G2 and G3 fail when the only signature on a compliance row belongs to an agent.

Stakeholder sign-off is a pre-launch act with a date on it. A sign-off collected after launch is not a gate: it is a record that the decision to ship was taken by nobody.

## Applicability

| Use this runbook when | Use a different runbook when |
| --- | --- |
| A major feature must land inside an existing enterprise product with live customers | Nothing is specified yet — `feature-discovery-to-spec` |
| Compliance, security, and quality gates are contractual, not aspirational | There is no installed base and no integration surface — `startup-mvp` |
| More than one stakeholder can veto, each on a different basis | The deliverable is a public API contract — `api-platform-launch` |
| The integration surface is older than the feature | Production is already broken — `incident-response` |
| The date is committed and the scope is not | The feature is model-backed and output quality is the risk — `ai-feature-integration` |
| Rollback must be proven before rollout, not promised | The deliverable is a decision, not shipped code — `design-sprint` |

## Required Inputs

Only what the roster cannot produce. The architecture, the acceptance-criteria register, the test suite, the evidence pack, and the release are outputs of weeks 1-11; listing them here would make the run circular.

| Input | Why it blocks | Owner |
| --- | --- | --- |
| The approved spec, with the acceptance criteria it was approved against | A feature approved against a paragraph cannot be graded; the criteria are the only thing this run can fail against | Product owner with Senior Project Manager |
| The named stakeholder approvers, each with the decision they own, the authority basis behind it (delegation, contract clause, budget line), and what they can veto | An approver whose authority is unstated cannot approve, and approvals discovered at handoff restart discovery | Project Shepherd |
| The compliance regime that governs the feature, and the named human who answers for it | Regime, obligations, and accountable human are input, not output: the checker maps the regime, the human decides the exposure | Legal Compliance Checker with the named approver |
| Production-like data or access, in the shape of the real integration surface | Counts, migration behaviour, and load cannot be established on fixtures; a staging-only run measures the fixture | Backend Architect with DevOps Automator |
| A delivery date that a named person owns, on the calendar | An unowned date slips silently, and every scope trade in this run is measured from it | Project Shepherd |

## Agent Roster

The roster the registry deploys for this runbook. Roles below are the standing remit; the phase trees name the gate or metric each output is load-bearing for.

### Core Team (Always Active)

| Agent | Role |
| --- | --- |
| Agents Orchestrator | Pipeline controller; owns the dev↔QA loop and the run's verdict record |
| Project Shepherd | Cross-functional coordination, stakeholder map, veto register, cadence |
| Senior Project Manager | Spec-to-task conversion; every task traced to one acceptance criterion |
| Sprint Prioritizer | Backlog sequencing, RICE scoring, and the ranked scope cut if the date moves |
| UX Architect | UX foundation and component architecture against the existing interface |
| UX Researcher | How the target workflow runs today, plus early user feedback after launch |
| UI Designer | Component design against the existing design system |
| Frontend Developer | UI implementation, task by task |
| Backend Architect | API and system integration, migrations, reversibility |
| Senior Developer | Complex and premium paths, the ones with no prior art |
| DevOps Automator | CI/CD, flags, production-like environments, rollback rehearsal |
| Evidence Collector | Screenshot and flow evidence attached to the criterion it proves |
| API Tester | Endpoint validation per task, plus the full regression suite |
| Reality Checker | Final quality judgment; default verdict NEEDS WORK |
| Performance Benchmarker | Load at 10x traffic, p95 per endpoint against budget |

### Compliance & Governance (As Needed)

| Agent | Role |
| --- | --- |
| Legal Compliance Checker | Regime mapping, obligation rows, audit findings — prepares, never signs |
| Brand Guardian | Brand consistency on every surface the feature touches |
| Finance Tracker | Budget framework and the cost of the date moving |
| Executive Summary Generator | One-page decision records and stakeholder briefings |

### Quality Assurance (As Needed)

| Agent | Role |
| --- | --- |
| Test Results Analyzer | Coverage, defect density, and escape candidates from the evidence pack |
| Workflow Optimizer | Fixes the loop that produced the defects instead of documenting it |
| Experiment Tracker | A/B setup and adoption tracking where a criterion is a behaviour |

## Phase 1-2: Discovery & Foundation

Weeks 1-3. Alignment first, then architecture and the foundation the build will sit on. The compliance mapping and the veto register are produced here because a gate item that appears in week 10 has no route into the spec.

```text
Weeks 1-3: Discovery & Foundation
├── Week 1: Alignment
│   ├── Project Shepherd → stakeholder map, veto register (who can veto what, on which basis), communication plan
│   ├── UX Researcher → the target workflow as it runs today, with counts from production-like data
│   ├── Legal Compliance Checker → regime mapped to feature obligations, one row per obligation, each with a named human approver
│   ├── Senior Project Manager → approved spec decomposed into tasks, each task traced to exactly one acceptance criterion
│   ├── Sprint Prioritizer → RICE-scored backlog, plus the ranked scope that is cut first if the date moves
│   └── Finance Tracker → budget framework and the cost of the date moving by one sprint
├── Week 2-3: Architecture & Foundation
│   ├── UX Architect → UX foundation and component architecture against the existing interface
│   ├── Backend Architect → system architecture, integration plan, migration and backfill path with the down-migration written first
│   ├── UI Designer → component design against the existing design system
│   ├── Brand Guardian → brand impact assessment on every surface the feature touches
│   ├── DevOps Automator → flag plumbing, branch pipeline, production-like environment, rollback runbook draft
│   ├── Frontend Developer → component scaffolding
│   └── Backend Architect → API scaffold and reversible database migrations
└── Quality Gate (G1): open the spec register — one acceptance criterion without a runnable assertion (observable, unit, threshold, failure condition) or without a named test owner fails the gate; open the compliance mapping — one obligation without a named human approver fails it; open the architecture review — one integration point with no owner fails it. The verdict is recorded with author and date, and the next phase does not start on a failed gate.
```

### Stakeholder Cadence

| Audience | Frequency | Agent | Format |
| --- | --- | --- | --- |
| Executive sponsors | Bi-weekly | Executive Summary Generator | SCQA summary (≤500 words) |
| Product team | Weekly | Project Shepherd | Status report |
| Engineering team | Daily | Agents Orchestrator | Pipeline status |
| Compliance team | Monthly, plus at each gate | Legal Compliance Checker | Compliance status with open findings |
| Finance | Monthly | Finance Tracker | Budget report |
| Named approvers | At G1, G2, and before 25% rollout | Project Shepherd | One-page decision record with a signature line and a date |

### Risk Register

Owned and reviewed at every gate. A risk whose owner changes hands at a gate is re-owned in writing, not by recollection.

| Risk | Probability | Impact | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| Integration complexity | High | High | Integration testing from week 3, API Tester in every sprint | Backend Architect |
| Scope creep | Medium | High | Sprint Prioritizer holds the ranked cut list; Project Shepherd records every change as a register edit, not a conversation | Sprint Prioritizer |
| Compliance issues | Medium | Critical | Legal Compliance Checker in week 1, obligation rows gated at G1 and signed by the named human | Legal Compliance Checker |
| Performance regression | Medium | High | Performance Benchmarker asserts the budget at G2 and again per canary step | Performance Benchmarker |
| Stakeholder misalignment | Low | High | Bi-weekly executive briefing, veto register read back at G1 | Project Shepherd |

## Phase 3-4: Build & Harden

Weeks 4-11. Build runs as a dev↔QA loop where no task closes on a claim; hardening is where the evidence becomes auditable and the rollback path stops being theoretical.

```text
Weeks 4-11: Build & Harden
├── Weeks 4-9: Build
│   ├── Agents Orchestrator → dev↔QA loop, one task at a time, no task closed on a claim
│   ├── Frontend Developer → UI implementation, task by task
│   ├── Backend Architect → API and integration implementation, task by task
│   ├── Senior Developer → complex and premium paths, the ones with no prior art
│   ├── Evidence Collector → evidence per task, attached to the criterion it proves
│   ├── API Tester → endpoint validation per API task, contract and error-body assertions
│   ├── Experiment Tracker → A/B setup where the criterion is a behaviour, with metric and stop rule
│   └── Bi-weekly: Project Shepherd → stakeholder status; Executive Summary Generator → executive briefing; Finance Tracker → budget tracking; Sprint Prioritizer → ranked scope cut if burn puts the date at risk
├── Weeks 10-11: Harden
│   ├── Evidence Collector → full screenshot and flow suite across the in-scope journeys
│   ├── API Tester → complete regression suite, including pre-existing endpoints the feature touches
│   ├── Performance Benchmarker → load at 10x current traffic, p95 per endpoint against budget
│   ├── Legal Compliance Checker → final audit and finding set prepared for the named human approver
│   ├── Test Results Analyzer → coverage, defect density, escape candidates
│   ├── Workflow Optimizer → the loop defect, fixed rather than documented
│   ├── DevOps Automator → production readiness and the rollback rehearsal in production shape
│   ├── Reality Checker → integration judgment, default NEEDS WORK
│   └── Fix cycle → 2-3 days, then re-verification against the same evidence set
└── Quality Gate (G2): open the evidence pack — one acceptance criterion without attached evidence, one regression failure on a touched endpoint, one endpoint over its p95 budget at 10x, or one open compliance finding with no named human decision maker fails the gate. Reality Checker starts at NEEDS WORK and only turns on re-verification of the same evidence set, never on a promise about the next build.
```

## Phase 5: Launch & Operate

Week 12. Rollout is stepped, each step gated on the metric, and the flag's removal is scheduled before the flag is switched on.

```text
Week 12: Launch & Operate
├── DevOps Automator → canary 5% → 25% → 100%, each step gated on the metric, rollback armed throughout
├── Performance Benchmarker → production p95 against the same budget used at G2, per step
├── Evidence Collector → production evidence attached to the criteria it proves
├── Experiment Tracker → adoption against the pre-launch baseline
├── UX Researcher → early user feedback, collected against the criterion it tests
├── Project Shepherd → sign-off rows recorded before the rollout crosses 25%, not after it completes
├── Executive Summary Generator → launch record: what shipped, what is still open, what the numbers say
├── Agents Orchestrator → flag removal tasked, dated, and assigned to a named remover
└── Quality Gate (G3): open the release record — one acceptance criterion without production evidence, no timestamped rollback rehearsal log from the same environment shape, a compliance row whose only signature is an agent's, or a missing pre-launch approver row fails the gate. A deployment with a green dashboard and an empty evidence column is a launched feature that is not done.
```

After G3 the feature is operated, not abandoned: the flag removal date is tracked like a defect, and a day-2 defect enters `bug-triage-and-defect-elimination` with a link to the criterion it broke.

## Key Decisions

| Decision | Decided by | Doctrine |
| --- | --- | --- |
| Which scope is at risk when the date moves | Project Shepherd with the named approvers | The cut list is ranked at G1 by the Sprint Prioritizer before the date is at risk; cutting mid-sprint is allowed only against that ranking. Cutting a compliance obligation is not scope, it is unmanaged exposure |
| Which stakeholders can veto | Project Shepherd, recorded at G1 | Veto rights are recorded per approver with their basis (delegation, contract clause, budget line). An approver with no recorded veto can object but does not stop the run; a veto asserted after G2 is an edit to the register, not a stop |
| Build versus configure | Backend Architect and UX Architect, approved by the owner of the integration contract | Configure first when the requirement is expressible in the existing surface; build only for a capability no configuration reaches, and record the maintenance cost the build creates |
| Whether the feature ships behind a flag | DevOps Automator with Project Shepherd | Ship behind a flag when the rollback path is a version switch rather than a data reversal, or when blast radius exceeds the canary cohort. Every flag carries a removal date and a named remover before it is switched on |
| What blocks release | Reality Checker for the verdict; the named compliance approver for exposure | An unmet criterion without evidence, a rollback path not exercised, or an unsigned compliance determination. Nothing else blocks — a blocking list that grows by preference is how a date becomes fiction |
| Who signs the compliance determination | The named human approver from Required Inputs | The Legal Compliance Checker prepares the regime mapping and findings; the signature belongs to the human whose authority basis is recorded. No agent signs off on regulatory exposure |

## Success Criteria

| Metric | Target |
| --- | --- |
| M1 Acceptance criteria with evidence attached | 100% of approved criteria carrying one evidence link each (test name, screenshot, or report), auditable by a second person without asking a question |
| M2 Defect escape rate | ≤ 5% — production defects in the first 30 days ÷ defects found before release; 0 escapes on the criteria graded at G2 |
| M3 p95 against the performance budget | 100% of touched endpoints at or under budget at 10x current traffic; 0 pre-existing endpoint regressions above 5% |
| M4 Accessibility conformance | 100% of in-scope journeys at WCAG 2.1 AA; 0 critical or serious automated findings; 0 unrecorded manual exceptions |
| M5 Change failure rate | ≤ 10% of the feature's releases needing a rollback or hotfix; every canary step decided within 15 minutes of its metric crossing |
| M6 Rollback path exercised | 100% of releases with a timestamped rehearsal log in production shape, decision to previous version serving in ≤ 20 minutes |

### Requirement thresholds asserted at G2

| Requirement | Threshold | Verified by |
| --- | --- | --- |
| Code coverage | > 80% on touched modules | Test Results Analyzer |
| API response time | p95 < 200ms | Performance Benchmarker |
| Accessibility | WCAG 2.1 AA | Evidence Collector |
| Security | Zero critical vulnerabilities | Legal Compliance Checker |
| Brand consistency | 95%+ adherence | Brand Guardian |
| Spec compliance | 100% of criteria evidenced | Reality Checker |
| Load handling | 10x current traffic | Performance Benchmarker |

## Common Pitfalls

| Pitfall | Mitigation |
| --- | --- |
| A spec with criteria nobody can fail | Every criterion carries observable, unit, threshold, failure condition, and a test owner before G1; if no test line goes red on a violation, the criterion is rewritten or deleted, and G2 cannot attach evidence to a phrase |
| Stakeholder sign-off collected by email after launch | Sign-off rows are recorded per named approver with a date before rollout crosses 25%; a signature arriving after launch is history, not a gate, and G3 fails on a missing pre-launch row |
| Compliance treated as a phase rather than a gate | Obligation rows enter the spec register at G1, the finding set at G2, and the signed determination at G3; a compliance review that only happens in week 10 has no route into the build |
| Performance measured in staging only | The budget is asserted at 10x against production-shaped data at G2 and re-asserted per canary step in production; demonstration-environment numbers are labelled as such and never satisfy a metric |
| A flag that never gets removed | The flag carries a removal date and a named remover at G3, both in the release record; an expired flag is a defect with an owner and a date, tracked alongside the day-2 defect intake |
| The team learning the requirements from the demo | Every task is traced to one criterion at G1, the criterion's owner reads it back at sprint review, and a task with no criterion is a scope addition to cut or register |
