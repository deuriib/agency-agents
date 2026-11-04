# Runbook: Compliance Certification Program

Mode: NEXUS-Full | Duration: 3-5 months | Agents: 18-26

## Scenario

You are driving an organization to audit-ready for SOC 2, ISO 27001, or an equivalent certification. Controls must be implemented in code and process, evidence must be collected continuously rather than scrambled at the end, and the control narrative must be defensible on the first audit pass.

## Agent Roster

### Program Core

| Agent | Role |
| --- | --- |
| Agents Orchestrator | Pipeline controller |
| Senior Project Manager | Control implementation plan |
| Project Shepherd | Cross-functional coordination |
| Legal Compliance Checker | Framework mapping and audit liaison |
| Risk Reviewer | Control design and risk sign-off |
| Executive Summary Generator | Audit committee and executive reporting |

### Control Implementation

| Agent | Role |
| --- | --- |
| DevOps Automator | CI/CD controls, change management evidence |
| SRE | Monitoring, incident, and availability controls |
| Backend Architect | Application security and data controls |
| Platform Engineer | Infrastructure baselines and configuration controls |
| Section 508 Accessibility Specialist | Accessibility compliance controls |
| Infrastructure Maintainer | Asset inventory and environment controls |

### Evidence & Testing

| Agent | Role |
| --- | --- |
| Evidence Collector | Continuous evidence capture |
| Reality Checker | Control-effectiveness verdict |
| Test Results Analyzer | Control test results and trends |
| API Tester | Technical control validation |
| Accessibility Auditor | Accessibility evidence and conformance |
| Workflow Optimizer | Evidence workflow and gap remediation |

### Reporting & Communications

| Agent | Role |
| --- | --- |
| Analytics Reporter | Compliance metrics and dashboards |
| Content Creator | Policy, procedure, and control narrative |
| Support Responder | Internal control-owner support |

## Execution Plan

### Phase 1: Scoping & Gap Assessment (Month 1)

```text
Week 1-2: Scoping
├── Legal Compliance Checker → Framework and trust-services scope
├── Risk Reviewer → Risk assessment and materiality
├── Project Shepherd → Control-owner map
├── Senior Project Manager → Program plan
└── Quality Gate: Scope approved by audit committee

Week 3-4: Gap Assessment
├── Backend Architect → Application control gaps
├── DevOps Automator → Change-management and CI/CD gaps
├── SRE → Monitoring and incident-response gaps
├── Section 508 Accessibility Specialist → Accessibility gaps
├── Workflow Optimizer → Evidence-workflow gaps
└── Quality Gate: Gap register approved
```

### Phase 2: Control Design & Implementation (Month 2)

```text
├── DevOps Automator → Automated change and approval evidence
├── Platform Engineer → Infrastructure configuration baselines
├── Backend Architect → Access, encryption, and logging controls
├── SRE → Incident and availability controls
├── Infrastructure Maintainer → Asset inventory controls
├── Content Creator → Policies and procedures
├── Evidence Collector → Evidence capture on every control
└── Quality Gate: Controls implemented and evidence flowing
```

### Phase 3: Evidence Automation (Month 3)

```text
├── Evidence Collector → Continuous evidence pipeline
├── Analytics Reporter → Compliance dashboard
├── Test Results Analyzer → Control test results
├── API Tester → Technical control validation
├── Accessibility Auditor → Accessibility evidence
├── Workflow Optimizer → Evidence gap remediation
└── Quality Gate: Evidence coverage ≥ 90% of controls
```

### Phase 4: Internal Audit & Remediation (Month 4)

```text
Week 1-2: Internal Audit
├── Reality Checker → Control effectiveness testing
├── Legal Compliance Checker → Audit simulation
├── Risk Reviewer → Residual risk review
├── Test Results Analyzer → Findings and severity
└── Quality Gate: Internal audit report issued

Week 3-4: Remediation
├── Senior Project Manager → Remediation plan
├── Engineering control owners → Fix control gaps
├── Evidence Collector → Re-test evidence
├── Reality Checker → Remediation verification
└── Quality Gate: All critical findings closed
```

### Phase 5: Certification Audit (Month 5)

```text
├── Legal Compliance Checker → Auditor liaison and evidence requests
├── Evidence Collector → Evidence package delivery
├── Project Shepherd → Audit logistics and control-owner availability
├── Executive Summary Generator → Audit status to executives
├── Reality Checker → Final readiness verdict
└── Quality Gate: Audit completed with no material exceptions
```

## Key Decisions

| Decision Point | When | Who Decides |
| --- | --- | --- |
| Certification scope | End of Month 1 | Legal Compliance Checker + Executive Sponsor |
| Control design | Month 2 | Risk Reviewer |
| Evidence sufficiency | Month 3 | Reality Checker |
| Remediation priority | Month 4 | Risk Reviewer + Senior Project Manager |
| Audit readiness | Month 5 | Reality Checker |

## Success Criteria

| Metric | Target |
| --- | --- |
| Controls implemented | 100% of in-scope controls |
| Evidence coverage before internal audit | ≥ 90% |
| Critical findings at internal audit | Zero |
| Control tests passed | ≥ 95% |
| Audit completed | No material exceptions |
| Evidence collected continuously | Automated, not manual end-of-program |

## Common Pitfalls

| Pitfall | Mitigation |
| --- | --- |
| Evidence scrambled at audit time from screenshots and inbox archaeology | Evidence Collector automates capture from Month 2, and the Phase 3 gate requires every control to produce its artefact without human assembly |
| Controls documented but not operated, so the audit tests paperwork | Reality Checker tests effectiveness, not existence: each control must be observed doing its job, and the Phase 4 gate fails a control whose sample shows no operation |
| The system boundary excludes the system that actually stores or processes the data | Phase 1 writes the boundary from data flow, not from the org chart, and a named human signs it before any control is designed |
| Compliance treated as a legal-only programme | Engineering control owners are staffed from Phase 2 and each control has a named operational owner, not a legal reviewer |
| The control narrative is written by the team that designed the controls, so the gap audits itself | The narrative is drafted from collected evidence and challenged in Phase 4 by an internal audit pass that was not involved in design |
| Accessibility omitted from scope | Section 508 Accessibility Specialist and Accessibility Auditor are in scope from Month 1, with conformance treated as a control |
| Findings reopened late because closure was recorded without re-test | The remediation gate requires re-test evidence, dated and attributable, before a finding closes |
| Certification treated as the finish line, so controls decay the quarter after the report | A continuing-evidence owner is named before Phase 5, and drift is reviewed on a stated cadence rather than at the next audit |
