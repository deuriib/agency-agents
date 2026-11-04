# Runbook: Public API Platform Launch

Mode: NEXUS-Sprint | Duration: 6-10 weeks | Agents: 14-16

## Scenario

You are launching a public API with stable contracts, developer documentation, sandbox access, and the operational guardrails that keep it usable and safe. A public API is a product with a versioning promise; breaking a contract after launch costs real customers.

## Agent Roster

### Core API Team

| Agent | Role |
| --- | --- |
| Agents Orchestrator | Pipeline controller |
| Senior Project Manager | Spec-to-task conversion |
| Product Manager | Developer personas, use cases, versioning promise |
| Backend Architect | Resource model, contract design, versioning |
| Platform Engineer | Gateway, quotas, API keys, developer portal |
| DevOps Automator | Environments, deploy pipeline, sandbox |
| Technical Writer | Reference docs, quickstarts, changelog |
| API Tester | Contract tests, error semantics, pagination, idempotency |
| Evidence Collector | Contract stability, doc-code parity |

### Developer Experience

| Agent | Role |
| --- | --- |
| Developer Community Builder | Outreach, feedback channels, examples |
| UX Researcher | First-integration usability testing |
| Support Responder | Developer support queue at launch |

### Security & Operations

| Agent | Role |
| --- | --- |
| Risk Reviewer | Auth model, abuse cases, threat model |
| SRE | SLOs, rate limiting, on-call runbooks |
| Legal Compliance Checker | Terms of service, data handling, deprecation policy |

## Execution Plan

### Phase 1: Contract Design (Weeks 1-2)

```text
Week 1: API Surface
├── Product Manager → Developer personas and top three use cases
├── Backend Architect → Resource model, naming, pagination, filtering, error envelope
├── Backend Architect and Risk Reviewer → Auth model and threat model
├── Platform Engineer and SRE → Rate-limit tiers and breach behavior
└── Quality Gate: Resource model and error semantics documented

Week 2: Versioning
├── Technical Writer → Versioning and deprecation policy (written before endpoints are designed)
├── Legal Compliance Checker → Contractual and regulatory constraints
├── Risk Reviewer → Scoping review
└── Quality Gate: Versioning and deprecation policy written
```

### Phase 2: Implementation (Weeks 2-5)

```text
Sprint 1:
├── Backend Architect and Platform Engineer → Gateway, key issuance, quota enforcement
├── API Tester → Contract tests per endpoint (success, validation, auth, rate limit, pagination)
├── SRE → SLOs and error-budget alerting
├── DevOps Automator → Sandbox with seeded data and self-service keys
└── Quality Gate: Top use case works end-to-end in sandbox with self-issued key

Sprint 2:
├── Agents Orchestrator → Dev↔QA loop
├── Backend Architect → Remaining endpoints in use-case order
├── API Tester → Full contract coverage including failure semantics
├── Evidence Collector → QA on every task
└── Quality Gate: Contract tests cover all endpoints including failure semantics
```

### Phase 3: Documentation & Developer Experience (Weeks 4-6)

```text
├── Technical Writer → Reference docs from spec, quickstart, one guide per use case
├── Evidence Collector → Doc-code parity (execute every documented example)
├── UX Researcher → First-integration testing with 3-5 external developers, no intervention
├── Developer Community Builder → Feedback channel and example repositories
├── Platform Engineer → Developer portal (keys, usage, logs, quota status)
└── Quality Gate: New developer reaches successful call in under 15 minutes unassisted
```

### Phase 4: Hardening & Launch Gate (Weeks 6-8)

```text
├── API Tester → Load test at 3x expected launch traffic
├── Risk Reviewer → Threat model re-test (leaked keys, quota circumvention)
├── SRE → Four on-call runbooks (error spike, latency, quota abuse, upstream failure)
├── Legal Compliance Checker → Terms of service, data handling, deprecation policy
├── Agents Orchestrator → Launch gate review
└── Quality Gate: Load test passed, no blocking findings, gate passed
```

### Phase 5: Launch & Support (Weeks 8-10)

```text
├── DevOps Automator → Limited partner cohort launch
├── Support Responder → Developer support queue with stated response target
├── Technical Writer → Changelog live and maintained
├── Developer Community Builder → First feedback cycle
├── Agents Orchestrator → Week 10 retro and v-next roadmap
└── Quality Gate: Partner cohort integrated, support within target
```

## Key Decisions

| Decision Point | When | Who Decides |
| --- | --- | --- |
| Versioning and deprecation policy | Week 2 | Technical Writer + Legal Compliance Checker |
| Auth and scoping model | Week 1 | Backend Architect + Risk Reviewer |
| Rate-limit tiers | Week 1 | Platform Engineer + SRE |
| Launch gate | Week 8 | Agents Orchestrator |
| First cohort | Week 8 | Product Manager + Developer Community Builder |

## Success Criteria

| Metric | Target |
| --- | --- |
| New developer reaches successful call | Under 15 minutes, unassisted |
| Doc-code parity | 100% of documented examples executed |
| Contract test coverage | 100% of endpoints including failure semantics |
| Load test | Passed at 3x expected launch traffic |
| On-call runbooks | Written and walkthrough-tested |
| Terms of service | Approved before launch gate |

## Common Pitfalls

| Pitfall | Mitigation |
| --- | --- |
| The contract changes after partners have integrated, because versioning was designed around endpoints instead of before them | Technical Writer writes the versioning and deprecation policy in Week 2, before endpoints are designed, and Legal Compliance Checker signs off on the contractual constraints; Backend Architect designs the resource model against that policy rather than retrofitting it |
| Reference docs are generated once and go stale, so the documented example no longer runs | Evidence Collector executes every documented example for doc-code parity in Phase 3, against a target of 100% of documented examples; Technical Writer derives reference docs from the spec and maintains the changelog from launch onward |
| The sandbox does not behave like production, so first integration works on a demo path and fails on real quotas | DevOps Automator ships seeded data and self-service keys in Sprint 1, and the Sprint 1 gate requires the top use case to work end-to-end in the sandbox with a self-issued key before UX Researcher's unassisted third-party integration test in Phase 3 |
| Rate limits are published in docs but not enforced at the gateway, so limits are discovered by customers during an incident | Platform Engineer and SRE agree tiers and breach behavior in Week 1, Platform Engineer enforces quotas at the gateway in Sprint 1, API Tester covers rate-limit responses per endpoint, and Risk Reviewer re-tests quota circumvention at the Phase 4 gate |
| Error responses leak internals or vary per endpoint, so integrators cannot code against failures | Backend Architect fixes the error envelope in the Week 1 gate that requires error semantics documented, and API Tester extends contract coverage to failure semantics on every endpoint by the Sprint 2 gate |
| Keys have no rotation or revocation path, so a leaked key cannot be killed without breaking every integrator | Platform Engineer owns key issuance and the Phase 3 developer portal surface that exposes keys, usage, logs, and quota status; Risk Reviewer's Phase 4 threat-model re-test includes the leaked-key path, and SRE writes the quota-abuse on-call runbook to cover the response |
