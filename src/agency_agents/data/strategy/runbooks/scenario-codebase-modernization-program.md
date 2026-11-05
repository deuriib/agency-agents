# Runbook: Codebase Modernization Program

Mode: NEXUS-Full | Duration: 3-5 months | Agents: 30-34

## Scenario

You have a live codebase that works but has become expensive to change. Dependencies drift, no one can reproduce the local environment, business logic sits in application code that the database could do natively, there is no caching layer absorbing load, a single oversized entrypoint resists parallel work, and repository clutter hides the code that actually matters.

The system must keep serving users the entire time. This is **modernization in place**: establish a reproducible platform baseline first, then move data-plane responsibilities into the database, then reduce load, then extract services. It is not a big-bang rewrite, and it is not a production cutover onto a different platform.

The ordering is the doctrine. Reproducibility before refactoring, because you cannot prove a migration is safe on an environment you cannot rebuild. Data-plane consolidation before caching, because a cache over unconsolidated queries hides the problem instead of fixing it.

## Applicability

| Use this runbook when | Use a different runbook when |
| --- | --- |
| The codebase is live and must keep serving traffic while its architecture changes | There is a hard cutover to a new platform with dual-run and decommission — use `legacy-platform-migration` |
| The problem set is toolchain reproducibility, data-plane placement, caching, monolith density, and repo hygiene | The problem is org-wide process, stakeholder, and budget change — use `digital-transformation-program` |
| Scope is one repository or a tight group of engineering-owned repositories | You must ship one feature into a healthy product — use `enterprise-feature` |
| Data already exists and is underused; it needs to be used better | No data platform exists at all — use `data-platform-foundation` |
| Repo hygiene matters only as far as it affects engineering speed | The deliverable is a professional public repo surface (LICENSE, SECURITY, Actions, enforcement) — use `repository-hardening-program` |
| You want measurable load reduction without a replatform | You must launch a new public API contract — use `api-platform-launch` |

## Required Inputs

Before Phase 0 starts, confirm all of the following exist. A missing input is a blocker, not a risk to log.

| Input | Why it blocks | Owner |
| --- | --- | --- |
| Write access to add CI checks, tasks, and containers | Phase 0 cannot gate without enforcement | Platform Engineer |
| Access to production-like data or a sanctioned subset | Parity tests are meaningless against empty tables | Database Optimizer |
| Frozen baseline metrics: p50/p95/p99, QPS, error rate, deploy frequency | Without a before-state, "modernized" is unfalsifiable | Analytics Reporter |
| A named owner per bounded context | Extraction without an owner produces orphaned modules | Project Shepherd |
| A decision on managed backend vs self-hosted data plane | Phase 2 cannot begin undecided | Backend Architect |
| Ability to run one non-production environment end to end | Rollback evidence requires somewhere to rehearse | DevOps Automator |

## Agent Roster

### Command (Always Active)

| Agent | Role |
| --- | --- |
| Agents Orchestrator | Dev↔QA loop controller, phase gating |
| Senior Project Manager | Spec-to-task conversion, phase task list |
| Project Shepherd | Bounded-context owners, sequencing, stakeholder alignment |
| Backend Architect | Target architecture, ADR authorship |
| Software Architect | Module boundaries and dependency direction |
| Executive Summary Generator | Steering-committee reporting |

### Platform Baseline (Phase 0)

| Agent | Role |
| --- | --- |
| Platform Engineer | Toolchain pinning and task runner as the single entrypoint |
| DevOps Automator | Containerized local runtime, CI parity, dual-run environment |
| Developer Tooling Engineer | Lint/format/type-check baseline with ratchet, pre-commit |

### Codebase Intelligence (Phase 1)

| Agent | Role |
| --- | --- |
| Codebase Archaeologist | Entrypoint map, dead code, abandoned scripts, duplicate modules |
| Codebase Onboarding Engineer | Factual dependency and data-flow map from source |
| Minimal Change Engineer | Risk-ranked cleanup queue; deletion before refactor |
| Analytics Reporter | Frozen baselines, dependency hygiene and migration KPIs |

### Data Plane (Phase 0+)

| Agent | Role |
| --- | --- |
| Database Optimizer | Extension inventory and pinning, native Postgres capabilities, indexes, consolidation |
| Database Reliability Engineer | Migration reversibility, index health, slow-query budget |
| Data Engineer | Backfill, reconciliation, checksum parity |
| Security Reviewer | Row-level security policy review with denial tests |
| Privacy Engineer | PII placement and retention when data changes hands |

### Service & Load Modernization (Phase 3-4)

| Agent | Role |
| --- | --- |
| Senior Developer | Highest-risk extraction and consolidation work |
| Frontend Developer | Compatibility layer; zero user-visible change |
| API Platform Engineer | Contract definitions and parity harness |
| Reliability Reviewer | Invalidation correctness and graceful degradation |

### Assurance (Phase 0+)

| Agent | Role |
| --- | --- |
| Evidence Collector | QA on every baseline, ported query, and extracted unit |
| Reality Checker | Phase verdicts; default to NEEDS WORK |
| API Tester | Contract parity against the frozen baseline |
| Performance Benchmarker | Latency and throughput parity; N+1 inventory |
| Test Results Analyzer | Defect trends per phase and per extraction |
| Workflow Optimizer | Quarantine policy and migration-factory improvement |

### Risk & Governance (As Needed)

| Agent | Role |
| --- | --- |
| Risk Reviewer | Residual risk register and phase go/no-go |
| Resilience Reviewer | Partial-failure behavior and self-healing of the new topology |
| Observability Reviewer | Signals that make the new paths diagnosable |
| Legal Compliance Checker | Data residency, licensing, third-party terms |
| Infrastructure Maintainer | Production readiness and monitoring handoff |

## Execution Plan

### Phase 0: Toolchain & Reproducibility Baseline (Week 1-2)

```text
Week 1: Pin the toolchain
├── Platform Engineer → mise.toml: every runtime pinned, tasks defined
│   (bootstrap, dev, test, lint, typecheck, db, migrate, seed)
├── Developer Tooling Engineer → pre-commit hooks; formatter/linter/type-check
│   baseline recorded as a ratchet (fail only on NEW violations)
├── DevOps Automator → multi-stage Dockerfile + compose:
│   app + database-with-extensions + cache + object storage + mail
├── Database Optimizer → extension inventory and version pin
│   (PostGIS, pg_trgm, unaccent, pgcrypto, pgvector, h3, uuid-ossp)
└── Quality Gate: from a clean clone on a clean machine, ONE command
    brings the full stack up, seeded, and serving

Week 2: Prove parity
├── DevOps Automator → CI consumes the SAME image and the SAME tasks
├── Infrastructure Maintainer → environment matrix documented
│   (local / CI / staging / prod deltas, explicitly listed)
├── Analytics Reporter → baseline metrics captured and FROZEN
├── Reality Checker → reproducibility verdict (default: NEEDS WORK)
└── Quality Gate: two engineers on two clean machines get identical green
    runs, and the frozen baseline is signed off
```

### Phase 1: Inventory & Repository Hygiene (Week 3-4)

```text
├── Codebase Archaeologist → entrypoint map, dead code, abandoned scripts
├── Codebase Onboarding Engineer → dependency and data-flow map from source only
├── Minimal Change Engineer → risk-ranked cleanup queue (delete before refactor)
├── Workflow Optimizer → quarantine policy: one-off scripts leave the repo;
│   anything kept gets an ADR line saying why
├── Analytics Reporter → dependency report: unused, unpinned, unmaintained, license conflicts
├── Evidence Collector → proof of removal: no references, build green, tests green
└── Quality Gate: zero scratch scripts at repo root, zero unpinned dependencies,
    ratchet baseline recorded, and zero behavior change
```

### Phase 2: Data Plane Consolidation (Week 5-9)

```text
├── Backend Architect → ADR-3 and ADR-4 written and signed off BEFORE any code moves
├── Database Optimizer → push logic into Postgres where it belongs:
│   row-level security, views and materialized views, generated columns,
│   constraints as invariants, functions and triggers, pg_trgm/unaccent search,
│   JSONB expression indexes
├── Database Reliability Engineer → reversible migrations, index health, slow-query budget
├── Data Engineer → backfill and reconciliation; row-count and checksum parity
├── Security Reviewer → RLS review WITH NEGATIVE TESTS: prove a principal
│   cannot read another tenant's rows
├── Privacy Engineer → PII stays where the policy says when data changes hands
├── Evidence Collector → QA each ported query
└── Quality Gate: every ported query has a parity test, every RLS policy has a
    denial test, reconciliation is zero-diff, and the migration reverses cleanly
```

### Phase 3: Load Reduction & Caching (Week 8-12)

Phases 3 and 4 overlap by design. Caching lands **before** an extraction starts, never during one.

```text
Week 1: Measure, do not guess
├── Performance Benchmarker → per-endpoint p50/p95/p99, query count per request,
│   N+1 inventory, hot endpoint ranking
├── Database Optimizer → consolidate N+1s into set-based queries FIRST
├── Backend Architect → ADR-5 caching hierarchy with a staleness budget per endpoint
└── Quality Gate: N+1 inventory at zero before a single cache key is added

Week 2-4: Add layers, cheapest first
├── Senior Developer → HTTP validators (ETag/Cache-Control), then app key-value
│   with TTL, then materialized views, then CDN
├── Reliability Reviewer → invalidation correctness; cache down must not mean site down
├── Observability Reviewer → hit ratio, miss reason, and invalidation events are observable
├── Performance Benchmarker → re-measure against the frozen baseline
└── Quality Gate: invalidate-and-reprove tests pass, staleness bound documented and
    tested, P95 within 10% of baseline or better, error rate not worse
```

### Phase 4: Service & Feature Extraction (Week 10-18)

One bounded context per sprint. Never two.

```text
Sprint 1..n (per bounded context):
├── Senior Developer → extract behind a feature flag
├── Backend Architect → module boundary and contract definition
├── API Platform Engineer → contract parity harness
├── API Tester → contract parity against the frozen baseline, every sprint
├── Frontend Developer → compatibility layer, no user-visible change
├── Test Results Analyzer → defect trend per extraction
├── Evidence Collector → QA each extracted unit
└── Quality Gate: behavior parity proven, flag-gated, rollback by flag flip
    (not by redeploy)
```

### Phase 5: Hardening & Decommission (Week 16-20)

```text
├── Security Reviewer, Reliability Reviewer, Resilience Reviewer, Observability Reviewer
│   → parallel sign-off on the new topology
├── Risk Reviewer → residual risk register and go/no-go
├── Performance Benchmarker → peak-load parity against the frozen baseline
├── Workflow Optimizer → migration-factory retrospective; template the next context
├── Reality Checker → final verdict (default: NEEDS WORK)
├── Executive Summary Generator → steering report
└── Quality Gate: no orphaned code path remains, baseline met or beaten,
    onboarding docs updated, and legacy paths removed (not just flagged off)
```

## Architecture Decision Records

These five ADRs are the deterministic core of the program. Phase 2 does not open until ADR-3 and ADR-4 are signed. Phase 3 does not open until ADR-5 is signed.

| ADR | Question it must answer | Decided by | Gate |
| --- | --- | --- | --- |
| ADR-1 Toolchain & task runner | Which runtimes are pinned, and what are the canonical tasks (`bootstrap`, `dev`, `test`, `lint`, `db`, `migrate`)? | Platform Engineer | Phase 0 |
| ADR-2 Local runtime parity | Which services run in containers locally, and how is parity with CI proven? | DevOps Automator | Phase 0 |
| ADR-3 Data-plane placement | Exactly which logic moves into the database (RLS, views, generated columns, functions, full-text/trigram search, JSONB) and which stays in the application? | Backend Architect + Database Optimizer | Phase 2 |
| ADR-4 Managed backend boundary | Which managed capabilities are adopted (database, auth, storage, realtime, edge functions), which are explicitly rejected, and what is the exit path? | Backend Architect | Phase 2 |
| ADR-5 Caching hierarchy | Which layers exist, their TTLs, their invalidation triggers, what must never be cached, and the staleness budget per endpoint? | Backend Architect + Reliability Reviewer | Phase 3 |

## Key Decisions

| Decision Point | When | Who Decides |
| --- | --- | --- |
| Toolchain and task-runner shape | End of Week 1 | Platform Engineer + Developer Tooling Engineer |
| Whether repo cleanup precedes or follows data-plane work | End of Week 2 | Minimal Change Engineer + Project Shepherd |
| Managed backend vs self-hosted data plane | End of Week 3 | Backend Architect + Risk Reviewer |
| What logic is allowed to move into the database | Week 5 | Backend Architect + Database Optimizer |
| Caching layers and staleness budgets | Week 8 | Backend Architect + Reliability Reviewer |
| Order of bounded-context extraction | Week 9 | Project Shepherd + Software Architect |
| Phase go/no-go | Each phase exit | Reality Checker + Risk Reviewer |
| Extraction rollback trigger | Phase 4 runbook | Reliability Reviewer |

## Success Criteria

| Metric | Target |
| --- | --- |
| Clean clone to running stack | One command, under 15 minutes, on macOS, Linux, and CI |
| Local/CI divergence | Same container image and same tasks; zero environment-specific instructions |
| Toolchain pinning | 100% of runtimes pinned; zero floating versions |
| Repository hygiene | Zero scratch scripts at repo root; zero unused dependencies |
| Lint and type ratchet | Baseline recorded; violation count only decreases |
| Logic moved into the data plane | Every item in ADR-3 has a parity test and, where tenant-scoped, a denial test |
| RLS coverage | 100% of tenant-scoped tables with both positive and negative tests |
| Query count on hot endpoints | N+1 inventory at zero; per-request query count reduced |
| Cache behavior | Invalidation tested; staleness bound documented and enforced |
| P95 latency | Within 10% of the frozen baseline, or improved |
| Extraction safety | 100% behind flags; rollback by flag flip |
| Downtime | Zero |

## Deliverables

| Deliverable | Produced by | Phase |
| --- | --- | --- |
| `mise.toml` with pinned runtimes and canonical tasks | Platform Engineer | 0 |
| `Dockerfile` + `compose.yaml` with the full local stack | DevOps Automator | 0 |
| Frozen baseline metrics document | Analytics Reporter | 0 |
| Dependency and data-flow map | Codebase Onboarding Engineer | 1 |
| Cleanup queue with evidence of removal | Minimal Change Engineer + Evidence Collector | 1 |
| ADR-1 through ADR-5 | Backend Architect | 0-3 |
| RLS policy suite with denial tests | Security Reviewer + Database Optimizer | 2 |
| Caching layer with invalidation tests | Senior Developer + Reliability Reviewer | 3 |
| Extraction template and per-context parity reports | API Tester + Workflow Optimizer | 4 |
| Residual risk register and final verdict | Risk Reviewer + Reality Checker | 5 |

## Common Pitfalls

| Pitfall | Mitigation |
| --- | --- |
| A big-bang rewrite in incremental clothing — the context is rebuilt on a branch while "modernization in place" stays on the slide | Phase 4 extracts exactly one bounded context per sprint and never two, each behind a feature flag with rollback by flag flip rather than redeploy, and caching lands before an extraction starts, never during one |
| The frozen baseline quietly refrozen once it stops flattering the program | The baseline is a Phase 0 gate artifact signed off by the Reality Checker, and every Phase 3 and Phase 5 claim is measured against that artifact (P95 within 10% or better, error rate not worse), so moving a target is a change to the Success Criteria table and its owners, not a re-measurement |
| Data-plane consolidation shipped without a rollback path | ADR-3 and ADR-4 are signed before any code moves, the Database Reliability Engineer owns reversible migrations, and the Phase 2 gate does not pass until reconciliation is zero-diff and the migration reverses cleanly |
| Load reduction that relocates cost instead of removing it — cache hit ratio climbs while origin query count and write load climb with it | Phase 3 captures per-endpoint p50/p95/p99 and query count per request before a cache key exists, the Observability Reviewer makes hit ratio, miss reason, and invalidation events observable, and the gate re-measures against the frozen baseline with error rate not worse |
| Service extraction driven by org fashion rather than measured coupling | Extraction order is a Week 9 Key Decision for the Project Shepherd and Software Architect, read off the Phase 1 dependency and data-flow map, and a bounded context with no named owner from Required Inputs never enters the queue |
| A "modernized" module nobody load-tested — behavior parity green, flag on, no peak profile | Phase 5 parallel sign-off includes peak-load parity against the frozen baseline, and a component absent from that report is not modernized however many contract-parity runs passed in Phase 4 |
