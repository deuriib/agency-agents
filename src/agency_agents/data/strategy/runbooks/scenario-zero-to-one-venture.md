# Runbook: Zero-to-One Venture Build

Mode: NEXUS-Full | Duration: 4-6 months | Agents: 26-34

## Scenario

You are standing up a new business line or spin-out from inside an existing company. There is no product yet, demand is unproven, and the venture must reach a real market with real economics. The runbook sequences validation, build, and go-to-market so the venture does not become a prototype that never ships.

## Agent Roster

### Venture Command

| Agent | Role |
| --- | --- |
| Agents Orchestrator | Pipeline controller |
| Senior Project Manager | Spec-to-task conversion |
| Project Shepherd | Stakeholder and dependency coordination |
| Sprint Prioritizer | Backlog and experiment prioritization |
| Finance Tracker | Unit economics and burn tracking |
| Executive Summary Generator | Investor and sponsor reporting |

### Discovery & Validation

| Agent | Role |
| --- | --- |
| Trend Researcher | Market sizing and timing |
| UX Researcher | Customer discovery interviews |
| Growth Hacker | Demand and acquisition experiments |
| Experiment Tracker | Validation experiment design |
| Analytics Reporter | Funnel and cohort measurement |

### Build

| Agent | Role |
| --- | --- |
| Rapid Prototyper | Fast validation builds |
| Backend Architect | API, data model, integrations |
| Frontend Developer | Product UI |
| Mobile App Builder | Mobile client, if applicable |
| AI Engineer | AI-native product capabilities |
| DevOps Automator | CI/CD and environments |
| Database Optimizer | Schema and query performance |

### Brand & Go-to-Market

| Agent | Role |
| --- | --- |
| Brand Guardian | Venture brand identity |
| UI Designer | Product and marketing surfaces |
| UX Architect | End-to-end experience foundation |
| Content Creator | Launch and lifecycle content |
| Social Media Strategist | Social launch and community |
| App Store Optimizer | Store presence, if mobile |
| Developer Community Builder | Developer-facing GTM, if API/product-led |

### Assurance & Operations

| Agent | Role |
| --- | --- |
| Evidence Collector | QA on every task |
| Reality Checker | Final quality gate |
| Performance Benchmarker | Load and cost testing |
| API Tester | Endpoint and integration validation |
| Legal Compliance Checker | Terms, privacy, regulatory fit |
| Support Responder | Early customer support |

## Execution Plan

### Phase 1: Problem Validation (Month 1)

```text
Week 1-2: Discovery
├── Trend Researcher → Market size, timing, competitive scan
├── UX Researcher → 15-20 customer discovery interviews
├── Growth Hacker → Demand-test landing page
├── Analytics Reporter → Funnel baseline
└── Quality Gate: Problem-solution fit evidence reviewed

Week 3-4: Validation Decision
├── Experiment Tracker → Pricing and willingness-to-pay test
├── Sprint Prioritizer → Build/no-build recommendation
├── Finance Tracker → Unit-economics model
├── Project Shepherd → Sponsor decision memo
└── Quality Gate: Go decision documented
```

### Phase 2: Prototype & Demand Test (Month 2)

```text
├── Rapid Prototyper → Clickable or functional prototype
├── UX Architect → Core journey map
├── UI Designer → High-fidelity key screens
├── Growth Hacker → Waitlist and referral test
├── Experiment Tracker → Conversion experiments
├── Analytics Reporter → Prototype engagement data
└── Quality Gate: Demand signal meets pre-agreed threshold
```

### Phase 3: Build the Product (Month 3-4)

```text
Sprint 1-2 (Month 3):
├── Backend Architect → Core API and data model
├── Frontend Developer → Core UI
├── Mobile App Builder → Mobile client if in scope
├── AI Engineer → AI features if in scope
├── DevOps Automator → CI/CD and staging
├── Evidence Collector → QA every task
└── Quality Gate: Core product usable end-to-end

Sprint 3-4 (Month 4):
├── Agents Orchestrator → Dev↔QA loop
├── Senior Developer → Complex integrations
├── Database Optimizer → Performance tuning
├── API Tester → Contract and regression tests
├── Performance Benchmarker → Cost and load test
└── Sprint Review with sponsors
```

### Phase 4: Brand & Go-to-Market (Month 5)

```text
├── Brand Guardian → Brand system and voice
├── UI Designer → Marketing site and product polish
├── Content Creator → Launch narrative, docs, lifecycle emails
├── Social Media Strategist → Launch calendar
├── App Store Optimizer → Store listing and assets
├── Developer Community Builder → Developer onboarding, if applicable
├── Legal Compliance Checker → Terms, privacy, disclosures
└── Quality Gate: GTM readiness review
```

### Phase 5: Launch & Unit Economics (Month 6)

```text
├── DevOps Automator → Production deployment
├── Growth Hacker → Paid and organic acquisition live
├── Support Responder → Customer support active
├── Analytics Reporter → Cohort and retention tracking
├── Finance Tracker → CAC, LTV, payback reporting
├── Reality Checker → Post-launch quality verdict
├── Executive Summary Generator → Launch and economics report
└── Quality Gate: Launch review and next-stage funding decision
```

## Key Decisions

| Decision Point | When | Who Decides |
| --- | --- | --- |
| Problem-solution fit | End of Month 1 | Project Shepherd + Sponsor |
| Build vs. stop | End of Month 1 | Sprint Prioritizer + Finance Tracker |
| Prototype demand threshold | End of Month 2 | Experiment Tracker |
| Launch readiness | Month 5 | Reality Checker |
| Scale investment | End of Month 6 | Sponsor + Finance Tracker |

## Success Criteria

| Metric | Target |
| --- | --- |
| Customer discovery interviews completed | ≥ 15 |
| Prototype demand signal | Meets pre-agreed threshold |
| Core product live | By end of Month 4 |
| Launch | By end of Month 6 |
| Unit economics documented | CAC, LTV, payback in launch report |
| Quality gates passed without waiver | 100% |

## Common Pitfalls

| Pitfall | Mitigation |
| --- | --- |
| Demand evidence is a competitor's fundraising announcement | The Month 1 problem-solution fit gate needs UX Researcher's 15-20 discovery interviews plus Growth Hacker's demand-test landing page with an Analytics Reporter funnel baseline; Trend Researcher's competitive scan is timing input, never demand proof |
| Unit economics modelled before the price was ever tested | Experiment Tracker's pricing and willingness-to-pay test runs in Month 1 Week 3-4 as input to the Finance Tracker model, so CAC, LTV, and payback rest on a tested price instead of an assumed one |
| An internal sponsor who cannot commit budget or sign the Go decision | Project Shepherd owns the sponsor decision memo and the documented Go decision gate; if the sponsor cannot commit, the Sprint Prioritizer plus Finance Tracker build-no-build call closes as stop and no gate is waived |
| Spin-out and org structure decided before the revenue model exists | Structure work sits with Legal Compliance Checker in Phase 4, after the Phase 1 Go decision that carries Finance Tracker's economics, so the entity question waits for the business model it has to fit |
| One friendly pilot customer treated as proof of market | The Month 2 demand threshold is pre-agreed by Experiment Tracker and judged on Growth Hacker's waitlist and referral test plus Analytics Reporter cohort data, so a single pilot cannot satisfy it |
| Venture progress tracked by headcount instead of retained revenue | Phase 5 reports Analytics Reporter retention cohorts and Finance Tracker CAC, LTV, and payback in the Executive Summary Generator launch report, and Sponsor plus Finance Tracker gate scale investment on those numbers |
