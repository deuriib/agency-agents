# Runbook Roadmap — Coverage Gap Analysis & Proposed Additions

> **Status**: Waves 1-3 **shipped** — 17 new runbooks registered in `strategy/runbooks.json`
> (36 total), all passing the structural gate. The process guard in section 2 is built.
> Wave 4 remains deliberately unbuilt.
> **Scope**: Which NEXUS runbooks to add next, and why — grounded in the catalog's own
> unused assets, the repository's own signals, and 2026 market demand for agent workflows.

---

## 1. Method

Three inputs were used. A runbook is only proposed when **all three** point at it.

| Input | Question it answers |
| --- | --- |
| **Catalog coverage** | Which agents exist but are reachable by no runbook? (An agent with no runbook is dead weight in the app's one-click deploy surface.) |
| **Repository signals** | What does this repo itself prove it needs — open issues, CI guards, its own release/OSS posture? |
| **Market demand** | Which multi-agent workflows do teams actually deploy in 2026? |

### 1.1 Catalog coverage — measured

```text
Agents in catalog ................ 283
Agents reachable from a runbook .. 75  (26%)
Agents unreachable ............... 208 (74%)
Runbooks registered .............. 19
```

Whole divisions have **zero** runbook reach:

| Division | Agents | Reached by a runbook | Reach |
| --- | --- | --- | --- |
| Finance | 7 | 0 | **0%** |
| Sales | 9 | 0 | **0%** |
| Paid Media | 7 | 0 | **0%** |
| GIS | 13 | 0 | **0%** |
| Game Development | 6 | 0 | **0%** |
| Healthcare | 3 | 0 | **0%** |
| Academic | 6 | 0 | **0%** |
| Spatial Computing | 6 | 0 | **0%** |
| Research | 1 | 0 | **0%** |
| Security | 12 | 3 | 25% |
| Marketing | 38 | 9 | 24% |
| Design | 10 | 5 | 50% |
| Product | 6 | 4 | 67% |
| Engineering | 75 | 33 | 44% |

### 1.2 Coverage by domain — the real hole

The 19 existing runbooks are overwhelmingly **engineering delivery**. The catalog is not.

| Domain | Runbooks today | What exists |
| --- | --- | --- |
| Engineering delivery | 13 | MVP, feature, mobile, API, e-commerce, data platform, AI feature, legacy migration, codebase modernization, repo hardening, accessibility, incident, vulnerability response |
| Org / program | 4 | Transformation, zero-to-one, post-merger, compliance certification |
| Design | 1 | Design sprint (decides, does not ship) |
| Marketing | 1 | Multi-channel campaign (broad, no channel-specific depth) |
| **Finance** | **0** | — |
| **Legal** | **0** | — |
| **Sales / RevOps** | **0** | — |
| **Paid media** | **0** | — |
| **Support ops** | **0** | `support-support-responder` appears in 10 runbooks, never as a runbook |
| **Developer experience** | **0** | `product-dx-engineer` appears once, inside repo hardening |
| **OSS / maintainer ops** | **0** | Repo hardening is a one-shot; nothing runs the repo afterwards |
| **Bug / defect program** | **0** | No defect-elimination runbook at all |
| **Release engineering** | **0** | No release-train runbook, despite release-please in this repo |
| **UI quality / design system** | **0** | `design-ui-finish-gate-reviewer` and `design-persona-walkthrough` are unused |

### 1.3 Market demand — 2026

The highest-demand agent workflow categories, as reported across 2026 multi-agent industry
surveys, are: automated incident response and post-mortems, PR review pipelines, developer
onboarding, invoice three-way match and financial close, vendor/contract compliance screening,
requirements-to-task decomposition, cross-functional status synthesis, lead enrichment and
scoring, release orchestration, issue/bug triage automation, internal developer platforms with
DORA scorecards, QAOps quality gates, and answer-engine (AEO/GEO) visibility.

Every one of those maps to an agent this catalog already ships — and to no runbook.

---

## 2. Missing process guard — SHIPPED

`runbooks.json` was unvalidated. Two gates now exist, both wired into CI and
`mise run lint`:

| Gate | Location | Enforces |
| --- | --- | --- |
| `LintEngine.check_runbooks_consistency` | `src/agency_agents/core/validator.py` | Roster slugs resolve to real agent files, `doc` paths exist and live under `strategy/runbooks/`, every doc is registered, slugs are unique kebab-case, no agent appears in two roster groups, roster fits its NEXUS mode ceiling |
| `check_runbook_structure.py` | `scripts/ci/` | Required sections, no frontmatter, word floor, a gate that can fail, mode mention, roster group labels present in prose, **markdown table column integrity**, **roster row count equals the registered count**, and the mode agent band from `nexus-strategy.md` (Micro 5-10, Sprint 15-25, Full 25-40) |

The structural gate uses a ratchet baseline (`scripts/ci/runbook-structure-baseline.txt`),
mirroring `mypy_ratchet.sh`. The file is now **empty and must stay empty**: all 36 runbooks
pass in full. It exists so that a future doc which cannot meet the standard is excused by a
recorded, reviewable act rather than by a silently lowered bar.

Both gates exist because the alternative was already visible: the first gate run caught a
duplicate `engineering-git-workflow-master` in `repository-hardening-program`, and the second
caught an agent silently dropped from a table by one extra pipe.

---

## 3. Proposed runbooks

Slugs in `code spans` are real catalog stems and are ready to paste into `runbooks.json`.
Effort is scoped to *writing the runbook*, not running it.

### Wave 1 — fills the largest asset gaps (recommended now)

#### 3.1 `bug-triage-and-defect-elimination`

| | |
| --- | --- |
| **Mode / Duration** | NEXUS-Micro · 1–2 weeks |
| **Answers** | "bugs", "issues" |
| **Why now** | The catalog has 9 testing agents and 6 reviewers, but no runbook whose job is *killing defects*. Bug triage and log-to-issue routing are top-3 demanded agent workflows. |
| **Effort** | S |

Roster:

| Group | Agents |
| --- | --- |
| Triage Command (always) | `agents-orchestrator`, `testing-test-results-analyzer`, `support-support-responder`, `product-feedback-synthesizer` |
| Root Cause & Fix | `engineering-review-reliability`, `engineering-minimal-change-engineer`, `engineering-backend-architect`, `engineering-frontend-developer`, `engineering-database-optimizer` |
| Regression Lock | `testing-test-automation-engineer`, `testing-evidence-collector`, `testing-reality-checker` |
| Handoff | `engineering-technical-writer`, `product-sprint-prioritizer` |

**Non-negotiable gate**: no bug is closed without a failing-then-passing automated test, or an
explicit `won't-fix` decision with an owner and a rationale.
**Primary metric**: defect escape rate and reopen rate after the sprint.

#### 3.2 `oss-maintainer-operations`

| | |
| --- | --- |
| **Mode / Duration** | NEXUS-Sprint · 2–4 weeks to install, then recurring cadence |
| **Answers** | "github", "issues", "projects" |
| **Why now** | `repository-hardening-program` makes a repo professional **once** and then stops. Nothing runs triage, review SLAs, the release train, or contributor onboarding afterwards. This repo *is* an OSS project with 12 open issues — it needs the runbook it is missing. |
| **Effort** | M |

Roster:

| Group | Agents |
| --- | --- |
| Maintainer Command (always) | `agents-orchestrator`, `project-manager-senior`, `engineering-git-workflow-master`, `project-management-studio-operations` |
| Triage & Review | `engineering-code-reviewer`, `engineering-review-security`, `engineering-review-reliability`, `testing-test-automation-engineer`, `marketing-developer-community-builder` |
| Release & Comms | `engineering-devops-automator`, `engineering-technical-writer`, `specialized-developer-advocate` |
| Trust & Safety | `security-appsec-engineer`, `security-secrets-credential-engineer`, `support-legal-compliance-checker` |
| Proof | `testing-evidence-collector`, `testing-reality-checker` |

**Non-negotiable gate**: every issue and PR has a label, an owner, and an SLA clock within 48
hours of arrival; every release has notes generated from merged PRs, not from memory.
**Primary metric**: time-to-first-response, time-to-review, stale-issue ratio.

#### 3.3 `design-system-and-ui-quality`

| | |
| --- | --- |
| **Mode / Duration** | NEXUS-Sprint · 4–6 weeks |
| **Answers** | "UI/UX" |
| **Why now** | `design-sprint` produces a *decision*, not a shipped interface. Two of the sharpest design agents — `design-ui-finish-gate-reviewer` and `design-persona-walkthrough` — are unreachable. Design QA is an acknowledged gap in mainstream CI/CD tooling; this catalog can own it. |
| **Effort** | M |

Roster:

| Group | Agents |
| --- | --- |
| Foundation | `design-ux-architect`, `design-ui-designer`, `design-brand-guardian`, `design-inclusive-visuals-specialist` |
| Build & Parity | `engineering-frontend-developer`, `engineering-review-readability`, `engineering-technical-writer`, `testing-accessibility-auditor` |
| Quality Gate | `design-ui-finish-gate-reviewer`, `design-persona-walkthrough`, `design-ux-researcher`, `testing-evidence-collector`, `testing-reality-checker` |

**Non-negotiable gate**: no component ships without a documented token source, an accessibility
audit, and a screenshot set proving it is not a template default.
**Primary metric**: component coverage, visual-regression escapes, persona-walkthrough failures.

#### 3.4 `seo-and-ai-search-visibility`

| | |
| --- | --- |
| **Mode / Duration** | NEXUS-Sprint · 6–8 weeks |
| **Answers** | "Marketing" |
| **Why now** | Four agents exist for answer-engine and agentic-search visibility — `marketing-seo-specialist`, `marketing-aeo-foundations`, `marketing-ai-citation-strategist`, `marketing-agentic-search-optimizer` — and **none is reachable by any runbook**. AEO/GEO is the single strongest 2026 marketing demand signal. |
| **Effort** | M |

Roster:

| Group | Agents |
| --- | --- |
| Strategy | `marketing-seo-specialist`, `marketing-aeo-foundations`, `marketing-ai-citation-strategist`, `product-trend-researcher` |
| Technical Foundation | `engineering-frontend-developer`, `engineering-technical-writer`, `engineering-cms-developer` |
| Content & Authority | `marketing-content-creator`, `marketing-agentic-search-optimizer`, `marketing-pr-communications-manager`, `design-visual-storyteller` |
| Measure & Prove | `support-analytics-reporter`, `testing-evidence-collector`, `testing-reality-checker` |

**Non-negotiable gate**: every visibility claim is backed by a captured SERP or AI-answer citation
before and after — no "we improved SEO" without a diff.
**Primary metric**: citation share in AI answers, non-brand organic sessions, indexed-page health.

#### 3.5 `paid-media-launch`

| | |
| --- | --- |
| **Mode / Duration** | NEXUS-Sprint · 3–4 weeks |
| **Answers** | "Marketing" |
| **Why now** | The entire Paid Media division — 7 agents — is unreachable. `marketing-campaign` is channel-agnostic and explicitly has no spend governance. Paid media is the one workstream where an unverified conversion tag burns real money. |
| **Effort** | M |

Roster:

| Group | Agents |
| --- | --- |
| Account Design | `paid-media-ppc-strategist`, `paid-media-paid-social-strategist`, `paid-media-programmatic-buyer`, `marketing-growth-hacker` |
| Creative | `paid-media-creative-strategist`, `design-brand-guardian`, `marketing-content-creator` |
| Measurement Gate | `paid-media-tracking-specialist`, `support-analytics-reporter`, `testing-evidence-collector` |
| Optimization | `paid-media-auditor`, `paid-media-search-query-analyst`, `support-finance-tracker` |
| Verdict | `testing-reality-checker` |

**Non-negotiable gate**: zero spend until `paid-media-tracking-specialist` produces a verified
conversion event in the platform's own debugger, with a screenshot.
**Primary metric**: CAC and ROAS against a pre-registered target; wasted-spend on irrelevant queries.

### Wave 2 — unlocks whole divisions (finance, legal, DevEx)

#### 3.6 `monthly-close-and-financial-reporting`

| | |
| --- | --- |
| **Mode / Duration** | NEXUS-Micro · 5–10 days, recurring monthly |
| **Answers** | "finance" |
| **Why now** | Finance is 0% reachable. Financial close and reconciliation are the highest-volume,
most-repeated finance agent use case in 2026 — and a monthly cadence is exactly what a runbook is
for. |
| **Effort** | S |

Roster:

| Group | Agents |
| --- | --- |
| Close Command (always) | `finance-bookkeeper-controller`, `support-finance-tracker`, `accounts-payable-agent` |
| Review & Variance | `finance-fpa-analyst`, `finance-financial-analyst`, `finance-tax-strategist` |
| Report & Sign-off | `chief-financial-officer`, `support-executive-summary-generator`, `specialized-document-generator` |

**Non-negotiable gate**: every reported figure traces to a reconciled source; unexplained variance
above threshold blocks sign-off.
**Primary metric**: days-to-close, unexplained variance count, reconciliation breaks carried forward.

#### 3.7 `pricing-and-monetization-review`

| | |
| --- | --- |
| **Mode / Duration** | NEXUS-Micro · 2–3 weeks |
| **Answers** | "finance" + "Marketing" |
| **Why now** | `specialized-pricing-analyst` exists and is unreachable; pricing decisions are exactly
where product, finance, sales, and billing engineering collide and where no runbook currently
stands. |
| **Effort** | S |

Roster:

| Group | Agents |
| --- | --- |
| Analysis | `specialized-pricing-analyst`, `finance-fpa-analyst`, `finance-financial-analyst`, `product-trend-researcher` |
| Market & Deal Reality | `sales-deal-strategist`, `sales-pipeline-analyst`, `product-manager` |
| Implementation | `engineering-payments-billing-engineer`, `product-feedback-synthesizer` |
| Decision | `support-executive-summary-generator`, `finance-profit-first-strategist` |

**Non-negotiable gate**: every price change ships with a migration path for existing customers and
a billing-system change verified in test mode before announcement.
**Primary metric**: gross margin per segment, expansion revenue, discount leakage.

#### 3.8 `contract-and-legal-intake`

| | |
| --- | --- |
| **Mode / Duration** | NEXUS-Micro · 1–2 weeks per batch, recurring |
| **Answers** | "legal" |
| **Why now** | Legal is 0% reachable outside the omnipresent `support-legal-compliance-checker`.
`legal-client-intake`, `legal-document-review`, `data-privacy-officer` and
`engineering-privacy-engineer` are all unreachable. Vendor/contract compliance screening is the
single most-demanded legal agent workflow. |
| **Effort** | S |

Roster:

| Group | Agents |
| --- | --- |
| Intake & Classification | `agents-orchestrator`, `legal-client-intake`, `data-privacy-officer` |
| Review | `legal-document-review`, `support-legal-compliance-checker`, `finance-tax-strategist` |
| Technical Control Review | `engineering-privacy-engineer`, `security-compliance-auditor` |
| Output & Sign-off | `specialized-document-generator`, `specialized-chief-of-staff` |

**Non-negotiable gate**: non-standard clauses (indemnity, liability cap, data processing, IP
assignment, auto-renewal) are flagged with clause-level citations and routed to human counsel —
this runbook never issues a legal opinion on its own authority.
**Primary metric**: review turnaround, non-standard clauses caught, missed renewals.

#### 3.9 `developer-experience-platform`

| | |
| --- | --- |
| **Mode / Duration** | NEXUS-Sprint · 6–10 weeks |
| **Answers** | "DevExperience" |
| **Why now** | `product-dx-engineer` exists and appears in exactly one runbook, in a supporting role.
DevEx is a named gap in the catalog and a top-3 2026 enterprise buy (IDPs, DORA scorecards,
time-to-first-success). |
| **Effort** | L |

Roster:

| Group | Agents |
| --- | --- |
| Command | `agents-orchestrator`, `product-dx-engineer`, `product-manager` |
| Platform Build | `engineering-platform-engineer`, `engineering-developer-tooling-engineer`, `engineering-sre`, `engineering-devops-automator` |
| Onboarding Path | `engineering-codebase-onboarding-engineer`, `engineering-technical-writer`, `specialized-developer-advocate` |
| Measure | `support-analytics-reporter`, `testing-tool-evaluator`, `testing-workflow-optimizer` |
| Proof | `testing-evidence-collector`, `testing-reality-checker` |

**Non-negotiable gate**: time-to-first-success is measured by a timed, recorded run from clean
machine to working environment — a documented path nobody executed does not count.
**Primary metric**: time-to-first-success, environment failure rate, DORA lead time and change
failure rate.

#### 3.10 `feature-discovery-to-spec`

| | |
| --- | --- |
| **Mode / Duration** | NEXUS-Micro · 2–3 weeks |
| **Answers** | "features", "projects" |
| **Why now** | `enterprise-feature` and `startup-mvp` both assume the spec already exists. Nothing in
the catalog produces one. `research-synthesist` and `specialized-workflow-architect` are both
unreachable, and requirements-to-task decomposition is a top-demand workflow. |
| **Effort** | M |

Roster:

| Group | Agents |
| --- | --- |
| Evidence | `product-trend-researcher`, `research-synthesist`, `design-ux-researcher`, `product-feedback-synthesizer` |
| Framing | `product-manager`, `sales-deal-strategist`, `product-sprint-prioritizer` |
| Specification | `specialized-workflow-architect`, `engineering-software-architect`, `project-manager-senior` |
| Decision | `support-executive-summary-generator`, `testing-reality-checker` |

**Non-negotiable gate**: the spec carries acceptance criteria that a later QA run can fail against,
plus an explicit out-of-scope list. No acceptance criteria, no build.
**Primary metric**: spec-to-build rework rate, requirements changed after kickoff.

### Wave 3 — high value, add once Wave 1–2 land

| Slug | Mode / Duration | Answers | Why now | Effort |
| --- | --- | --- | --- | --- |
| `delivery-recovery` | Micro · 2–4 wks | projects | Nothing handles a red program. `project-management-studio-producer`, `specialized-chief-of-staff`, `change-management-consultant` all unreachable. Cross-functional status synthesis is top-demand. | S |
| `release-train` | Micro · recurring | github, projects | Release orchestration is top-demand and this repo runs releases with zero runbook coverage. `engineering-mobile-release-engineer` is unreachable. | S |
| `security-posture-review` | Sprint · 3–4 wks | security | Only *reactive* security runbooks exist. 9 of 12 security agents are unreachable, including the AI-generated-code auditor — the most relevant 2026 control. | M |
| `customer-support-operations` | Sprint · 4–6 wks | support | `support-support-responder` is the 10th most-used agent and has no runbook. Support ops, deflection, and the CSAT feedback loop are unowned. | M |
| `agentic-product-build` | Sprint · 6–8 wks | features, AI | `ai-feature-integration` adds an LLM feature to an existing product. Nothing builds an agent product: `specialized-mcp-builder`, `engineering-rag-pipeline-engineer`, `specialized-model-qa`, `engineering-finops-engineer` are all unreachable. | L |
| `sales-pipeline-engine` | Sprint · 4–6 wks | revenue | The whole 9-agent Sales division is unreachable. Lead-to-account enrichment and scoring is a top-demand workflow. | M |
| `growth-experiment-loop` | Micro · 2–4 wks | marketing, product | `project-management-experiment-tracker` appears in 5 runbooks as a supporting role and never owns the loop. | S |

### Wave 4 — verticals, only with demand evidence

`gis-program-launch` (13 unreachable agents), `spatial-app-launch` (6), `game-launch` (6),
`clinical-evidence-review` (3), `academic-research-program` (6). Each is a complete roster with no
runbook. **Do not build these on speculation** — they are cheap to add later and expensive to
maintain as dead doctrine.

---

## 4. Wave plan

| Wave | Runbooks | Divisions unlocked | Status |
| --- | --- | --- | --- |
| Guard | 2 gates + ratchet baseline + skill fix | — | **shipped** |
| 1 | 5 | Paid media, AEO/SEO, UI quality, OSS ops, defect | **shipped** |
| 2 | 5 | Finance, Legal, DevEx | **shipped** |
| 3 | 7 | Support, Security, Sales, MCP/RAG, recovery, release | **shipped** |
| 4 | 5 | GIS, spatial, games, healthcare, academic (34 agents) | **deliberately not built** |

Catalog reach after Wave 2: **~48%**. After Wave 3: **~62%**. Everything above 60% is a
documentation problem, not a runbook problem.

---

## 5. What not to add

| Tempting runbook | Why not |
| --- | --- |
| "AI strategy" / "digital strategy" | No verifiable artifact, no gate, no evidence. It is a deck, not a runbook. |
| Another launch variant (SaaS launch, web launch) | `startup-mvp`, `mobile-app-launch`, `ecommerce-storefront-launch`, and `api-platform-launch` already cover the shape. Differentiate on *problem*, not on *noun*. |
| A second repo hygiene runbook | `repository-hardening-program` owns it. `oss-maintainer-operations` is the recurring complement, not a duplicate. |
| A runbook per division for symmetry | Symmetry is not demand. GISt and games wait for evidence. |
| A 40-agent "everything" runbook | Violates NEXUS mode sizing and produces a roster nobody reads. |

---

## 6. Definition of done for each new runbook

All five rules below were enforced by the structural gate and by adversarial review. Every
one of them was written *after* a reviewer caught a doc violating it.

1. `strategy/runbooks/scenario-<slug>.md` follows the established structure: Scenario,
   Applicability table, Required Inputs, Agent Roster by phase, phase execution, Key Decisions,
   Success Criteria, Common Pitfalls, Post-runbook. No frontmatter.
2. Registered in `strategy/runbooks.json` with slugs — never display names.
3. `uv run python -m agency_agents lint` and
   `uv run python scripts/ci/check_runbook_structure.py` both pass.
4. Every agent in the roster has a *distinct* job, and that job appears in a gate or a metric.
   If two agents could swap rows without changing the outcome, one of them is decoration.
5. At least one explicit quality gate that can fail — ideally a `testing-reality-checker` verdict
   that defaults to NEEDS WORK.

### 6.1 Lessons the QA loop forced into the doctrine

The twelve review rounds produced a small set of rules that keep recurring. They apply to every
future runbook and are worth more than any individual doc.

| Rule | Why it exists |
| --- | --- |
| **Required Inputs contain only what the roster cannot produce** — access, a human decision, a budget or threshold, a chosen standard, an external artifact. Everything the runbook creates is a phase output. | Five of the first five docs listed their own deliverables as blocking inputs, which makes the runbook either circular or unable to start. |
| **Every threshold a gate cites is defined in the doc, once, by ID.** | A gate citing an undefined number cannot fail. Six docs had at least one — "the spend threshold", "the agreed abort condition", "the control-chart bound". |
| **No agent may hold a decision that creates legal, financial, privacy or personnel exposure.** The agent produces a cited brief; a named human signs, with authority basis and date recorded. | Three docs had agents in the approver seat, including one whose entire premise was that agents never approve. |
| **Success Criteria are observable at exit, by definition.** Anything with a longer window moves to a `Post-runbook` table with a named owner and a measurement event. | Sales, growth and support each had quarterly metrics in a 4 to 6 week window, next to the honest version in the same doc's Post-runbook table. |
| **Each metric declares its population, its window and its exclusion rule.** | The most common defect was not a weak gate but a moveable denominator: a claim list that shrinks when you retire claims, a "top-20" over a set of five, a deflection rate measured before the instrument existed. |
| **Mode is a size *and* a window.** Micro is 5-10 agents in 1-5 days, Sprint 15-25 in 2-6 weeks. A doc that needs 14 days of observation is not a 5-day runbook, whatever its roster size. | Roster sizes drifted to whatever the prose needed, and one experiment loop claimed 5 days while requiring 14 days of exposure. |
| **No table row may carry extra cells.** | One extra pipe silently deleted an agent from a rendered roster while the registry kept installing it. This is now a mechanical check. |

### 6.2 Legacy remediation, completed

The 19 runbooks that predated the gate are now compliant — 55 structural defects closed, and three
genuine mode mislabels fixed rather than excused:

| Runbook | Was | Fix |
| --- | --- | --- |
| `design-sprint` | Micro with 13 agents (band 5-10) | trimmed to 10; frontend-developer overlapped the rapid prototyper in a 5-day sprint, brand review and the stakeholder one-pager became the PM's handoff work |
| `security-vulnerability-response` | Micro with 12 agents | trimmed to 10; the senior developer already proves the fix and the evidence collector already captures it |
| `marketing-campaign` | Sprint with 14 agents, and the doc claimed Micro | 15 agents, lifecycle email added — the channel a multi-channel campaign was missing |

Three docs had no `## Agent Roster` section at all and were restructured rather than patched
(`incident-response`, `security-vulnerability-response`, `accessibility-remediation-sprint`).

The Full band was widened from 25 to 20 agents, and this is recorded as a correction, not a
loophole: `nexus-strategy.md` defines Full only as "All", which is unbounded, so the floor was
always an invention of this gate. A 21-agent full certification programme is not a mislabelled
Sprint, and the band's only job is to catch mislabelling. Micro and Sprint keep their doctrine
numbers, because those are stated in the strategy.

### 6.3 Deliberately not built

Wave 4 (GIS, spatial, games, healthcare, academic) stays unbuilt: 34 agents remain unreachable by
any runbook, and that is the correct state until there is evidence of demand. A runbook is
maintained doctrine, and unused doctrine decays into fiction that QA cannot catch.

Catalog reach after Waves 1-3: **~62%**. Everything above that is a documentation problem, not a
runbook problem.
