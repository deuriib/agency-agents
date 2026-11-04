# Runbook: Legacy Platform Migration

Mode: NEXUS-Full | Duration: 4-6 months | Agents: 24-32

## Scenario

You are moving a production monolith or aging platform onto a modern architecture. Downtime is not acceptable, data integrity is non-negotiable, and the cutover plan must include tested rollback paths. The migration has to proceed incrementally while the existing system keeps serving customers.

## Agent Roster

### Migration Command

| Agent | Role |
| --- | --- |
| Agents Orchestrator | Pipeline controller |
| Senior Project Manager | Spec-to-task conversion |
| Project Shepherd | Stakeholder and vendor coordination |
| Backend Architect | Target architecture and migration strategy |
| Senior Developer | Complex migration implementation |
| Executive Summary Generator | Steering-committee reporting |

### Discovery & Mapping

| Agent | Role |
| --- | --- |
| Database Optimizer | Schema, stored procedures, data lineage |
| SRE | Runtime dependencies, traffic patterns |
| API Tester | Contract inventory and behavior baselines |
| Trend Researcher | Platform and vendor landscape |
| Analytics Reporter | Usage baselines and migration KPIs |

### Build & Cutover

| Agent | Role |
| --- | --- |
| Platform Engineer | Target platform and shared services |
| DevOps Automator | Dual-run infrastructure and cutover automation |
| Frontend Developer | UI migration and compatibility |
| Data Engineer | ETL/ELT and data reconciliation |
| AI Data Remediation Engineer | Anomaly detection and data repair |
| Data Visualization Engineer | Migration dashboards and reconciliation views |

### Assurance

| Agent | Role |
| --- | --- |
| Evidence Collector | Visual and functional QA |
| Reality Checker | Cutover readiness gate |
| Performance Benchmarker | Load and latency parity |
| Test Results Analyzer | Quality and defect trends |
| Workflow Optimizer | Migration-factory process improvement |

### Risk & Communications

| Agent | Role |
| --- | --- |
| Risk Reviewer | Architecture and cutover risk sign-off |
| Legal Compliance Checker | Data-residency and regulatory review |
| Content Creator | Internal and customer communications |
| Support Responder | Customer support during cutover |
| Infrastructure Maintainer | Production readiness and monitoring |

## Execution Plan

### Phase 1: Inventory & Dependency Map (Month 1)

```text
Week 1-2: System Inventory
├── Database Optimizer → Schema and data-lineage map
├── API Tester → Contract and behavior inventory
├── SRE → Runtime dependency and traffic map
├── Analytics Reporter → Usage baseline
└── Quality Gate: Inventory complete and reviewed

Week 3-4: Migration Strategy
├── Backend Architect → Strangler-fig or re-platform decision
├── Risk Reviewer → Risk register and rollback criteria
├── Project Shepherd → Migration sequence and stakeholder plan
├── Legal Compliance Checker → Data-handling constraints
└── Quality Gate: Migration strategy approved
```

### Phase 2: Target Architecture & Migration Factory (Month 2)

```text
├── Platform Engineer → Target platform baseline
├── DevOps Automator → Dual-run environment and cutover tooling
├── Data Engineer → Replication and reconciliation pipeline
├── AI Data Remediation Engineer → Anomaly detection rules
├── Frontend Developer → Compatibility layer
├── Evidence Collector → QA on every migrated component
└── Quality Gate: First component migrated in dual-run mode
```

### Phase 3: Incremental Migration (Month 3-4)

```text
Sprint 1-4:
├── Agents Orchestrator → Dev↔QA loop
├── Senior Developer → High-risk modules
├── Platform Engineer → Service-by-service migration
├── Data Engineer → Continuous reconciliation
├── API Tester → Contract parity every sprint
├── Performance Benchmarker → Latency and throughput parity
├── Test Results Analyzer → Defect trend reporting
└── Quality Gate: Migration coverage ≥ 60% by end of Month 4
```

### Phase 4: Cutover Rehearsal (Month 5)

```text
Week 1-2: Rehearsal
├── DevOps Automator → Full cutover and rollback rehearsal
├── SRE → Failure injection and recovery drill
├── Database Optimizer → Data integrity verification
├── Risk Reviewer → Go/no-go criteria review
├── Reality Checker → Rehearsal verdict (default: NEEDS WORK)
└── Quality Gate: Rehearsal passed with zero data loss

Week 3-4: Final Hardening
├── Performance Benchmarker → Peak-load parity test
├── API Tester → Full regression suite
├── Infrastructure Maintainer → Production readiness
├── Content Creator → Cutover communications
└── Quality Gate: Production readiness review
```

### Phase 5: Production Cutover & Decommission (Month 6)

```text
├── DevOps Automator → Phased traffic cutover (5% → 25% → 100%)
├── SRE → Real-time monitoring and rollback authority
├── Data Engineer → Post-cutover reconciliation
├── Support Responder → Customer support surge
├── Executive Summary Generator → Cutover report
├── Platform Engineer → Legacy decommission plan
└── Quality Gate: Cutover accepted and legacy system retired
```

## Key Decisions

| Decision Point | When | Who Decides |
| --- | --- | --- |
| Migration pattern | End of Month 1 | Backend Architect + Risk Reviewer |
| First component to migrate | Month 2 planning | Project Shepherd + Platform Engineer |
| Cutover go/no-go | Month 5, Week 2 | Reality Checker + Risk Reviewer |
| Rollback trigger | Cutover runbook | SRE |
| Legacy decommission | End of Month 6 | Platform Engineer + Project Shepherd |

## Success Criteria

| Metric | Target |
| --- | --- |
| Inventory coverage | 100% of production components |
| Migration coverage before cutover | ≥ 90% |
| Data loss during cutover | Zero |
| Latency parity | P95 within 10% of baseline |
| Rollback rehearsal | Completed with verified recovery |
| Downtime during cutover | Zero or within approved window |

## Common Pitfalls

| Pitfall | Mitigation |
| --- | --- |
| A cutover plan whose rollback was never rehearsed — the document exists, the timer never ran | The DevOps Automator runs the full cutover and rollback in Phase 4 Week 1-2 under SRE failure injection, rollback criteria are set by the Risk Reviewer in Month 1, and the Month 5 Week 2 go/no-go reads a rehearsal verdict of verified recovery rather than a plan |
| Data integrity asserted from row counts while transformed values diverge | The Data Engineer runs the replication and reconciliation pipeline from Phase 2 and reconciles continuously in Phase 3, the Database Optimizer verifies integrity in the Phase 4 rehearsal, the AI Data Remediation Engineer's anomaly rules and the Data Visualization Engineer's reconciliation views cover what a count cannot, and the Phase 4 gate reads zero data loss |
| Dual-run windows closed before the divergence is explained — equal counts, unexplained deltas | Every divergence is a defect in the Test Results Analyzer trend with an owner, coverage gates at ≥60% in Month 4 and ≥90% before cutover, and the SRE's rollback authority stops the ramp at 5% while a delta is still open |
| Hidden dependencies discovered at cutover — a batch job, a report, or a vendor feed nobody inventoried | Phase 1 is a gate, not a survey: the SRE runtime and traffic map, the API Tester contract inventory, the Database Optimizer lineage map, and the 100% inventory coverage metric are what admit a component to Phase 3, and anything found in Month 6 reopens that map before traffic moves |
| Cutover scheduled in a window that ignores peak traffic | The Phase 4 Week 3-4 peak-load parity test runs against the Analytics Reporter usage baseline, and Phase 5 ramps 5% → 25% → 100% under SRE monitoring with P95 within 10% of baseline, so a peak-hour regression pauses the ramp instead of riding it to 100% |
| The old platform decommissioned while one report still reads it | Retirement is a Key Decision for the Platform Engineer and Project Shepherd at the end of Month 6, backed by the decommission plan and a Phase 1 dependency map with no remaining reader; a live reader keeps that component in the inventory and blocks the Phase 5 gate |
