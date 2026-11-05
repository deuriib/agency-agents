# Runbook: Mobile App Launch

Mode: NEXUS-Sprint | Duration: 6-8 weeks | Agents: 16-18

## Scenario

You are taking a mobile app from validated concept to store-ready release on iOS and Android. There is a real user problem, a controlled backend, and both stores are in scope for the same release. Performance, accessibility, and store optimization are built in rather than bolted on after submission.

## Agent Roster

### Core Build Team

| Agent | Role |
| --- | --- |
| Agents Orchestrator | Pipeline controller |
| Senior Project Manager | Spec-to-task conversion |
| Product Manager | Scope, acceptance criteria, release definition |
| UX Architect | Navigation model, flow architecture, platform conventions |
| UI Designer | Screen design, component library, native patterns |
| Mobile App Builder | Client implementation, native integrations, build pipeline |
| Backend Architect | API contracts, auth, sync, offline behavior |
| DevOps Automator | CI/CD, signing, TestFlight and Play Console tracks |
| Evidence Collector | Visual QA on every build |
| Reality Checker | Final integration and acceptance gate |

### Launch & Growth

| Agent | Role |
| --- | --- |
| App Store Optimizer | Store listing, keywords, screenshots |
| Content Creator | Launch assets, onboarding and permission copy |
| Growth Hacker | Activation funnel and retention instrumentation |
| Brand Guardian | Brand consistency across store and app |

### Post-Launch Support

| Agent | Role |
| --- | --- |
| Support Responder | Review responses, support queue, issue triage |
| Analytics Reporter | Crash, funnel, and retention reporting |
| Performance Benchmarker | Cold start, frame timing, memory, battery profiling |

## Execution Plan

### Phase 1: Validation & Architecture (Weeks 1-2)

```text
Week 1: Release Definition
├── Product Manager → Release definition and v1 scope freeze
├── UX Architect → Navigation model and 8-12 critical flows
├── Backend Architect → API contracts, auth model
├── Reality Checker → Device matrix proposal
└── Quality Gate: Release definition signed off

Week 2: Architecture & Pipeline
├── Mobile App Builder → Client architecture and sync model
├── DevOps Automator → CI/CD, signing, internal distribution track
├── Backend Architect → Offline/sync strategy
├── Evidence Collector → Acceptance-criteria traceability matrix scaffold
└── Quality Gate: Signed build installs on a real device
```

### Phase 2: Core Build (Weeks 2-4)

```text
Sprint 1:
├── UI Designer → Component library and first screens
├── Mobile App Builder → Vertical slice (auth → core action → confirmation)
├── Backend Architect → Sync implementation
├── DevOps Automator → Automated build + test on every merge
├── Evidence Collector → QA every task
└── Quality Gate: Vertical slice works end-to-end on device

Sprint 2:
├── Agents Orchestrator → Dev↔QA loop
├── Mobile App Builder → Remaining critical flows on iOS and Android
├── Reality Checker → Weekly real-device pass on low-RAM device, throttled network
├── Evidence Collector → Traceability matrix coverage
└── Quality Gate: All critical flows functional against staging
```

### Phase 3: Hardening & Store Readiness (Weeks 4-5)

```text
├── Performance Benchmarker → Cold start, scroll, memory, battery against budgets
├── Evidence Collector → Full regression across device matrix
├── App Store Optimizer → Both store listings drafted
├── Brand Guardian → Listing and onboarding consistency review
├── Content Creator → Onboarding, empty, error, and permission copy
├── Reality Checker → First-time-user clean-install pass
└── Quality Gate: Performance budgets met, listings drafted, first-run reviewed
```

### Phase 4: Beta & Submission (Weeks 5-6)

```text
├── DevOps Automator → TestFlight and Play internal testing tracks
├── Support Responder → Beta feedback loop
├── Growth Hacker → Activation and retention instrumentation
├── Product Manager → Beta triage (fix P0/P1, defer rest)
├── App Store Optimizer → Final screenshots and metadata from beta build
├── Legal Compliance Checker (as needed) → Data-handling review for MDM
└── Quality Gate: Both submissions filed, rejection response plan assigned
```

### Phase 5: Launch & Iterate (Weeks 6-8)

```text
├── DevOps Automator → Staged rollout 10% → 50% → 100%
├── Analytics Reporter → Daily launch dashboard, first two weeks
├── Support Responder → Daily review and support triage
├── Growth Hacker → First activation experiment after baseline stabilizes
├── Reality Checker → Post-launch quality verdict
└── Quality Gate: 100% rollout with crash-free sessions at target
```

## Key Decisions

| Decision Point | When | Who Decides |
| --- | --- | --- |
| v1 scope freeze | Week 1 | Product Manager + Senior Project Manager |
| Sync and offline strategy | Week 2 | Backend Architect + Mobile App Builder |
| Device matrix | Week 2 | Reality Checker |
| Submission readiness | Week 6 | Reality Checker |
| Rollout pace | Week 6 | DevOps Automator + Support Responder |

## Success Criteria

| Metric | Target |
| --- | --- |
| Critical flows functional on both platforms | 100% |
| Traceability to acceptance criteria | 100% |
| Performance budgets | Met or explicitly waived in writing |
| Crash-free sessions at 100% rollout | At or above target |
| Store submissions | Approved without open rejection cycles |
| Support ownership | Handed off with named on-call |

## Common Pitfalls & Mitigations

| Pitfall | Mitigation |
| --- | --- |
| Sync decided late | Backend Architect and Mobile App Builder lock it in Week 2 |
| Device matrix skipped | Reality Checker proposes and validates in Week 1 |
| Performance deferred | Performance Benchmarker runs in Phase 3 with numeric budgets |
| Store rejection at launch | App Store Optimizer finalizes metadata from beta build, not mockups |
| Support gap post-launch | Support Responder owns the queue from hour one |

## Common Pitfalls

| Pitfall | Mitigation |
| --- | --- |
| Store review rejection is discovered at submission, with listing metadata and screenshots written from mockups rather than the shipped build | App Store Optimizer finalizes screenshots and metadata from the beta build in Phase 4, and the Phase 4 gate requires both submissions filed with a rejection response plan assigned; the Legal Compliance Checker data-handling review runs where MDM is in scope |
| Crash-free rate is asserted from a staging run on a modern handset instead of the store build on the device matrix | Reality Checker runs the weekly real-device pass on a low-RAM device over a throttled network in Sprint 2 and gives the post-launch verdict; Analytics Reporter's daily dashboard reads staged-rollout cohorts, and the Phase 5 gate is crash-free sessions at target at 100% rollout |
| Deep links and universal links work in the development scheme but are dead in the store build, where the signing and bundle configuration differ | DevOps Automator's CI/CD and signing pipeline plus the TestFlight and Play internal testing tracks in Phase 4 exercise the installed store build; Evidence Collector regression across the device matrix and the Reality Checker first-time-user clean-install pass cover entry through a deep link |
| Push permission is requested on first launch, before any value is shown, and the denial is unrecoverable | Content Creator writes the onboarding, empty, error, and permission copy in Phase 3 with the Brand Guardian consistency review, and the Reality Checker first-time-user clean-install pass covers the moment the prompt appears |
| An update path bricks offline sessions, because pending local writes meet a changed sync contract on first launch after upgrade | Backend Architect and Mobile App Builder lock the offline/sync strategy in Week 2 and ship sync in Sprint 1; DevOps Automator's staged rollout of 10 percent to 50 percent to 100 percent, read through the Analytics Reporter daily dashboard and Support Responder triage, holds the blast radius while the upgrade path is confirmed |
| Analytics fire only on the build the team installed, so activation and retention read green while the store population is unmeasured | Growth Hacker instruments activation and retention in Phase 4 against the beta build on the TestFlight and Play internal tracks, and the Analytics Reporter daily launch dashboard is validated against store-installed cohorts rather than team devices |
